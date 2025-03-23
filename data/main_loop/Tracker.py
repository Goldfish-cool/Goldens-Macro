import os
import re
import json
import requests
import logging
import asyncio
from pathlib import Path
from datetime import datetime
from data.lib import config
config.config_data = config.read_config()

class BiomeTracker:
    def __init__(self):
        self._create_default_config()
        self.biomes = self._load_biome_data()
        self.auras = self._load_aura_data()
        self.current_biome = None
        self.biome_counts = {b["name"]: 0 for b in self.biomes.values()}
        self.config = self._load_config()
        self.loggingEnabled = self.config.get("logging_enabled", "true")
        self.webhook_url = config.config_data['discord']['webhook']['url']
        self.private_server_link = config.config_data['discord']['webhook']['ps_link']
        self.biome_alerts = self.config.get("biome_alerts", {})
        self.last_aura = None
        self.last_processed_position = 0
        self.last_sent_biome = None
        self.last_sent_aura = None

    def _create_default_config(self):
        config_path = Path("settings.cfg")
        if not config_path.exists():
            try:
                with open(config_path, "w") as f:
                    json.dump(
                        {
                            "_comment": "highly recommended to keep logging_enabled enabled in case you run into an error, so you can report it to the devs",
                            "logging_enabled": True,
                            "webhook_url": "",
                            "private_server_link": "No Private Server Link specified in the config.",
                            "biome_alerts": {
                                "WINDY": True,
                                "RAINY": True,
                                "SNOWY": True,
                                "SAND STORM": True,
                                "HELL": True,
                                "STARFALL": True,
                                "CORRUPTION": True,
                                "NULL": True,
                            },
                        },
                        f,
                        indent=2,
                    )
                logging.info("Created default config file")
            except Exception as e:
                logging.error(f"Failed to create config: {str(e)}")

    def _load_config(self):
        try:
            with open("settings.cfg") as f:
                config = json.load(f)
                for biome in self._load_biome_data():
                    if biome not in config.get("biome_alerts", {}):
                        config["biome_alerts"][biome] = False
                return config
        except Exception as e:
            logging.error(f"Config load error: {str(e)}")
            return {
                "_comment": "highly recommended to keep logging_enabled enabled in case you run into an error, so you can report it to the devs",
                "logging_enabled": True,
                "webhook_url": "",
                "private_server_link": "No Private Server Link specified in the config.",
                "biome_alerts": {
                    "WINDY": True,
                    "RAINY": True,
                    "SNOWY": True,
                    "SAND STORM": True,
                    "HELL": True,
                    "STARFALL": True,
                    "CORRUPTION": True,
                    "NULL": True,
                },
            }

    def _load_biome_data(self):
        try:
            response = requests.get("https://raw.githubusercontent.com/Goldfish-cool/Goldens-Macro/refs/heads/data/biome-data.json")
            response.raise_for_status()
            biome_list = response.json()
            logging.info(f"Loaded biome data from {response.url}")
            return {biome["name"]: biome for biome in biome_list}
        except Exception as e:
            logging.error(f"Failed to load biome data: {str(e)}")
            return {}

    def _load_aura_data(self):
        try:
            response = requests.get("https://raw.githubusercontent.com/Goldfish-cool/Goldens-Macro/refs/heads/data/aura-data.json")
            response.raise_for_status()
            aura_list = response.json()
            logging.info(f"Loaded aura data from {response.url}")
            return {aura["identifier"]: aura for aura in aura_list}
        except Exception as e:
            logging.error(f"Failed to load aura data: {str(e)}")
            return {}

    async def monitor_logs(self):
        log_dir = Path(os.getenv("LOCALAPPDATA")) / "Roblox" / "logs"

        latest_log = max(log_dir.glob("*.log"), key=os.path.getmtime, default=None)
        if latest_log:
            self.last_processed_position = latest_log.stat().st_size
        else:
            self.last_processed_position = 0

        while True:
            try:
                latest_log = max(
                    log_dir.glob("*.log"), key=os.path.getmtime, default=None
                )
                if not latest_log:
                    await asyncio.sleep(5)
                    continue

                with open(latest_log, "r", errors="ignore") as f:
                    if latest_log.stat().st_size < self.last_processed_position:
                        self.last_processed_position = 0

                    f.seek(self.last_processed_position)
                    lines = f.readlines()
                    self.last_processed_position = f.tell()

                    for line in lines:
                        await self._process_log_entry(line)

                await asyncio.sleep(1)

            except Exception as e:
                logging.error(f"Log monitoring error: {str(e)}")
                await asyncio.sleep(5)

    async def _process_log_entry(self, line):
        try:
            self._detect_biome_change(line)
            self._check_aura_equipped(line)
        except Exception as e:
            logging.error(f"Log processing error: {str(e)}")

    def _detect_biome_change(self, line):
        if "[BloxstrapRPC]" not in line:
            return

        try:
            json_str = line.split("[BloxstrapRPC] ")[1]
            data = json.loads(json_str)
            hover_text = data.get("data", {}).get("largeImage", {}).get("hoverText", "")

            if hover_text in self.biomes and self.current_biome != hover_text:
                self._handle_new_biome(hover_text)
        except (IndexError, json.JSONDecodeError):
            pass
        except Exception as e:
            logging.error(f"Biome detection error: {str(e)}")

    def _handle_new_biome(self, biome_name):
        try:
            self.current_biome = biome_name
            self.biome_counts[biome_name] += 1
            logging.info(f"Biome detected: {biome_name}")

            if biome_name != self.last_sent_biome:
                biome_data = self.biomes[biome_name]

                if biome_name in ["GLITCHED", "DREAMSPACE"]:
                    self._send_webhook(
                        title=f"Biome Detected",
                        description=f"# - {biome_name}",
                        color=int(biome_data["visuals"]["primary_hex"], 16),
                        thumbnail=biome_data["visuals"]["preview_image"],
                        urgent=True,
                        is_aura=False,
                    )
                elif self.biome_alerts.get(biome_name, False):
                    self._send_webhook(
                        title=f"Biome Detected",
                        description=f"# - {biome_name}",
                        color=int(biome_data["visuals"]["primary_hex"], 16),
                        thumbnail=biome_data["visuals"]["preview_image"],
                        urgent=False,
                        is_aura=False,
                    )

                self.last_sent_biome = biome_name

        except KeyError:
            logging.warning(f"Received unknown biome: {biome_name}")
        except Exception as e:
            logging.error(f"Biome handling error: {str(e)}")

    def _check_aura_equipped(self, line):
        if "[BloxstrapRPC]" not in line:
            return

        try:
            json_str = line.split("[BloxstrapRPC] ")[1]
            data = json.loads(json_str)
            state = data.get("data", {}).get("state", "")

            match = re.search(r'Equipped "(.*?)"', state)
            if match and (aura_name := match.group(1)) in self.auras:
                self._process_aura(aura_name)
        except (IndexError, json.JSONDecodeError):
            pass
        except Exception as e:
            logging.error(f"Aura check error: {str(e)}")

    def _process_aura(self, aura_name):
        try:
            aura = self.auras[aura_name]
            aura_data = aura["properties"]
            visuals = aura.get("visuals", {})
            thumbnail = visuals.get("preview_image")

            base_chance = aura_data["base_chance"]
            rarity = base_chance
            obtained_biome = None

            biome_amplifier = aura_data.get("biome_amplifier", ["None", 1])
            
            if biome_amplifier[0] != "None" and (
                self.current_biome == biome_amplifier[0] 
                or self.current_biome == "GLITCHED"
            ):
                rarity /= biome_amplifier[1]
                obtained_biome = self.current_biome

            rarity = int(rarity)

            if aura_data.get("rank") == "challenged":
                color = 0x808080      # Grey (challenged)
            else:
                if rarity <= 999:
                    color = 0xFFFFFF  # White (basic)
                elif rarity <= 9999:
                    color = 0xFFC0CB  # Very light pink (epic)
                elif rarity <= 99998:
                    color = 0xFFA500  # Orangeish/brown (unique)
                elif rarity <= 999999:
                    color = 0xFFFF00  # Yellow (legendary)
                elif rarity <= 9999999:
                    color = 0xFF1493  # Pink (mythic)
                elif rarity <= 99999998:
                    color = 0x00008B  # Darkish blue (exalted)
                elif rarity <= 999999999:
                    color = 0x8B0000  # Blood red (glorious)
                else:
                    color = 0x00FFFF  # Cyan (transcendent)

            fields = []
            if base_chance == 0:
                rarity_str = "Unobtainable"
            else:
                rarity_str = f"1 in {rarity:,}"
            fields.append({"name": "Rarity", "value": rarity_str, "inline": True})
            
            if obtained_biome:
                fields.append({"name": "Obtained From", "value": obtained_biome, "inline": True})

            logging.info(f"Aura equipped: {aura_name} (1 in {rarity:,})")

            if aura_name != self.last_sent_aura:
                self._send_webhook(
                    title=f"Aura Detection",
                    description=f"{aura_name} has been equipped.",
                    color=color,
                    thumbnail=thumbnail,
                    is_aura=True,
                    fields=fields
                )
                self.last_sent_aura = aura_name

        except KeyError as e:
            logging.warning(f"Missing aura property: {str(e)}")
        except ZeroDivisionError:
            logging.error("Invalid biome amplifier value (division by zero)")
        except Exception as e:
            logging.error(f"Aura processing error: {str(e)}")

    def _send_webhook(
        self, title, description, color, thumbnail=None, urgent=False, is_aura=False, fields=None
    ):
        if not self.webhook_url:
            logging.error(f"Please specify a Webhook URL in the config")
            return

        try:
            current_time = datetime.now().isoformat()

            embed = {
                "title": title,
                "description": description,
                "color": color,
                "timestamp": current_time,
                "footer": {"text": "Goldens Sol's Macro"},
            }

            if fields is not None:
                embed["fields"] = fields
            else:
                if not is_aura:
                    ps_link = self.private_server_link
                    if not ps_link or ps_link.strip() == "":
                        ps_link = "No Private Server Link specified in the config."
                    embed["fields"] = [{"name": "Private Server Link", "value": ps_link}]

            if thumbnail:
                embed["thumbnail"] = {"url": thumbnail}

            payload = {"content": "@everyone" if urgent else None, "embeds": [embed]}
            logging.info(f"Attempting to send webhook: {payload}")

            async def send():
                try:
                    response = await asyncio.to_thread(
                        requests.post, self.webhook_url, json=payload, timeout=5
                    )
                    if response.status_code == 429:
                        retry_after = response.json().get("retry_after", 5)
                        logging.warning(f"Rate limited - retrying in {retry_after}s")
                        await asyncio.sleep(retry_after)
                        await send()
                    response.raise_for_status()
                except Exception as e:
                    logging.error(f"Webhook failed: {str(e)}")

            asyncio.create_task(send())
        except Exception as e:
            logging.error(f"Webhook creation error: {str(e)}")


if __name__ == "__main__":
    try:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%m-%d-%Y %H-%M-%S")
        log_filename = log_dir / f"{timestamp} biome_tracker.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_filename), logging.StreamHandler()],
            force=True,
        )

        tracker = BiomeTracker()

        logging.info(f"SolsBot Biome and Aura Tracker has started. Close this console or press CTRL + C to stop the tracker.")
        if tracker.webhook_url:
            try:
                current_time = datetime.now().isoformat()
                embed = {
                    "title": "Tracker Started",
                    "description": "Biome/Aura Detection has started.",
                    "color": 0x00FF00,
                    "timestamp": current_time,
                    "footer": {"text": "Goldens Sol's Macro"},
                    "fields": [{"name": "Private Server Link", "value": tracker.private_server_link}],
                }
                payload = {"content": None, "embeds": [embed]}
                response = requests.post(tracker.webhook_url, json=payload, timeout=5)
                response.raise_for_status()
                logging.info("Startup webhook sent successfully.")
            except Exception as e:
                logging.error(f"Failed to send startup webhook: {str(e)}")

        if tracker.loggingEnabled:
            asyncio.run(tracker.monitor_logs())
    except KeyboardInterrupt:
        logging.info("Tracker stopped by user")
        if tracker.webhook_url:
            try:
                current_time = datetime.now().isoformat()
                embed = {
                    "title": "Tracker Stopped",
                    "description": "Biome/Aura Detection has stopped.",
                    "color": 0xFF0000,
                    "timestamp": current_time,
                    "footer": {"text": "Goldens Sol's Macro"},
                    "fields": [{"name": "Private Server Link", "value": tracker.private_server_link}],
                }
                payload = {"content": None, "embeds": [embed]}
                response = requests.post(tracker.webhook_url, json=payload, timeout=5)
                response.raise_for_status()
                logging.info("Shutdown webhook sent successfully.")
            except Exception as e:
                logging.error(f"Failed to send shutdown webhook: {str(e)}")
    except Exception as e:
        logging.critical(f"Critical failure: {str(e)}")
        if tracker.webhook_url:
            try:
                current_time = datetime.now().isoformat()
                embed = {
                    "title": "Tacker Crashed",
                    "description": f"Biome/Aura Detection has crashed due to: {str(e)}",
                    "color": 0xFF0000,
                    "timestamp": current_time,
                    "footer": {"text": "Goldens Sol's Macro"},
                    "fields": [{"name": "Private Server Link", "value": tracker.private_server_link}],
                }
                payload = {"content": "@everyone", "embeds": [embed]}
                response = requests.post(tracker.webhook_url, json=payload, timeout=5)
                response.raise_for_status()
                logging.info("Crash webhook sent successfully.")
            except Exception as e:
                logging.error(f"Failed to send crash webhook: {str(e)}")
