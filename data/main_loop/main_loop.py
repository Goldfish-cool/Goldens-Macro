import multiprocessing
from time import sleep
import threading
import requests
import os
import keyboard
from pathlib import Path
import asyncio
import logging
from pynput.keyboard import Key
from pynput import keyboard
from tkinter import messagebox
import sys
try:
    from data.lib import config
except:
    ctypes.windll.user32.MessageBoxW(0, "Cant open this folder, also who the fuck told you to?", 0)
    sys.exit(1)
import json
import re
from ahk import AHK
from tkinter.messagebox import showerror
import ctypes
from datetime import datetime
ahk = AHK()
ahk.set_send_mode("Event")
ahk.set_coord_mode("Screen")
import re
config.config_data = config.read_config()
kc = keyboard.Controller()
aura_storgeX = config.config_data['clicks']['AuraStorageX'] 
aura_storgeY = config.config_data['clicks']['AuraStorageY']
regular_tabX = config.config_data['clicks']['RegularAuraTabX'] 
regular_taby = config.config_data['clicks']['RegularAuraTabY']
special_tabX = config.config_data['clicks']['SpecialAuraTabX']
special_tabY = config.config_data['clicks']['SpecialAuraTabY']
aura_searchX = config.config_data['clicks']['AuraSearchBarX'] 
aura_searchY = config.config_data['clicks']['AuraSearchBarY']
slot_1X = config.config_data['clicks']['FirstAuraSlotX']
slot_1Y = config.config_data['clicks']['FirstAuraSlotY']
equip_buttonX = config.config_data['clicks']['EquipButtonX']
equip_buttonY = config.config_data['clicks']['EquipButtonY']
alignX = config.config_data['clicks']['AligmentX']
alignY = config.config_data['clicks']['AligmentY']
exit_buttonX = config.config_data['clicks']['ExitButtonX']
exit_buttonY = config.config_data['clicks']['ExitButtonY']
invo_tabx = config.config_data['clicks']['InvoX']
invo_taby = config.config_data['clicks']['InvoY']
items_tabx = config.config_data['clicks']['ItemsTabX']
items_taby = config.config_data['clicks']['ItemsTabY']
search_itemsx = config.config_data['clicks']['ItemsBarX']
search_itemsy = config.config_data['clicks']['ItemsBarY']
first1x = config.config_data['clicks']['ItemsSlotX']
first1y = config.config_data['clicks']['ItemsSlotY']
items_quanx = config.config_data['clicks']['QuanityBarX']
items_quany = config.config_data['clicks']['QuanityBarY']
usex = config.config_data['clicks']['UseX']
usey = config.config_data['clicks']['UseY']

session_start = None

last_log_position = 0
monitoring_active = False
monitoring_thread = None
lock = threading.Lock()


azerty_replace_dict = {"w":"z", "a":"q"}
logs_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'Roblox', 'logs')
with open("path.txt", "r") as file:
    config_file = f"{file.read()}\\data\\lib\\config.json"

def get_action(file):
    with open("path.txt") as path_file:
        with open(f'{path_file.read()}\\paths\\{file}.py') as file:
            return file.read()
        
def walk_time_conversion(d):
    if config.config_data["settings"]["vip+_mode"] == "1":
        return d
    elif config.config_data["settings"]["vip_mode"] == "1":
        return d * 1.04
    else:
        return d * 1.3

def walk_sleep(d):
    sleep(walk_time_conversion(d))

def walk_send(k, t):
    if config.config_data["settings"]["azerty_mode"] == "1" and azerty_replace_dict[k]:
        k = azerty_replace_dict[k]
    
    if t == True:
        kc.press(k)
    else:
        kc.release(k)

running = False
initialiazed = False
main_process = None

def start():
    global running, main_process

    if running == True:
        ctypes.windll.user32.MessageBoxW(0, "Macro Already Running!", "Warning", 0)
        return
    else:
        running = True
    main_process = multiprocessing.Process(target=macro_start)
    main_process.start()

def stop():
    global running, main_process
    if running == True:
        running = False
    else:
        messagebox.showinfo(title="Info", message="Macro Already Stopped")
        return
    main_process.terminate()

def macro_start():
    tracker = BiomeTracker()
    asyncio.run(tracker.monitor_logs())
    return

def show_error(title, message):
    """Safely show error message using messagebox"""
    try:
        messagebox.showerror(title, message)
    except:
        print(f"Error: {title} - {message}")

biome_data = {
    "Windy": {"color": 0x9ae5ff, "duration": 120},
    "Rainy": {"color": 0x027cbd, "duration": 120},
    "Snowy": {"color": 0xDceff9, "duration": 120},
    "Sandstorm": {"color": 0x8F7057, "duration": 600},
    "Hell": {"color": 0xff4719, "duration": 660},
    "Starfall": {"color": 0x011ab7, "duration": 600},
    "Corruption": {"color": 0x6d32a8, "duration": 660},
    "Null": {"color": 0x838383, "duration": 90},
    "Glitched": {"color": 0xbfff00, "duration": 164},
    "Dreamspace": {"color": 0xea9dda, "duration": 180}
}
    

def send_discord(title="", description="", thumbnail="", color=None, timestamp=None, footer=""):
    if config.config_data['discord']['webhook']['enabled'] == "1":
        current_time = datetime.now()
        embed = {
            "title": title,
            "description": description,
            "thumbnail": {"url": thumbnail},
            "color": color if color is not None else 0x2F3136,
            "timestamp": timestamp if timestamp is not None else current_time.isoformat(),
            "footer": {"text": footer}
        }
        payload = {
            "embeds": [embed]
        }
        requests.post(config.config_data['discord']["webhook"]["url"], json=payload)
    else:
        return None
    
class BiomeTracker:
    def __init__(self):
        self._create_default_config()
        self.biomes = self._load_biome_data()
        self.auras = self._load_aura_data()
        self.current_biome = None
        self.biome_counts = {b["name"]: 0 for b in self.biomes.values()}
        self.config = self._load_config()
        self.loggingEnabled = self.config.get("logging_enabled", "true")
        self.webhook_url = self.config.get("webhook_url", "")
        self.private_server_link = self.config.get("private_server_link", "No Private Server Link specified in the config.")
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
            self.auto_equip()
            sleep(1)
            self.align_cam()
            sleep(1)
            self.claim_quests()
            sleep(1)
            self.item_scheduler()
            sleep(1)
            self.item_collecting()
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
                        title=f"Biome Started",
                        description=f"# - {biome_name}",
                        color=int(biome_data["visuals"]["primary_hex"], 16),
                        thumbnail=biome_data["visuals"]["preview_image"],
                        urgent=True,
                        is_aura=False,
                    )
                elif self.biome_alerts.get(biome_name, False):
                    self._send_webhook(
                        title=f"Biome Started",
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
                    title=f"AURA EQUIPPED: {aura_name}",
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
                "footer": {"text": "SolsBot v1.1.0 Pre2"},
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
    
    def auto_equip(self):
        if config.config_data['auto_equip']['enabled'] == "1":
            try:
                send_discord("Equiping", f"Auto Equiping: {config.config_data['auto_equip']['aura']}", footer="Golden's Sol's Macro v0.0")
                sleep(1.3)
                ahk.mouse_move(aura_storgeX, aura_storgeY)
                sleep(0.45)
                ahk.click()
                sleep(0.55)
                if config.config_data['auto_equip']['special_aura'] == "0":
                    ahk.mouse_move(regular_tabX, regular_taby)
                    sleep(0.55)
                    ahk.click()
                else:
                    ahk.mouse_move(special_tabX, special_tabY)
                    sleep(0.55)
                    ahk.click()
                ahk.mouse_move(aura_searchX, aura_searchY)
                sleep(0.55)
                ahk.click()
                sleep(0.55)
                ahk.send_input(config.config_data['auto_equip']['aura'])
                sleep(0.3)
                kc.tap(Key.enter)
                sleep(0.55)
                ahk.mouse_move(slot_1X, slot_1Y)
                sleep(0.55)
                ahk.click()
                sleep(0.5)
                ahk.mouse_move(equip_buttonX, equip_buttonY)
                sleep(0.2)
                ahk.click()
                sleep(0.2)
                ahk.mouse_move(aura_searchX, aura_searchY)
                sleep(0.3)
                ahk.click()
                sleep(0.3)
                kc.tap(Key.enter)
                ahk.mouse_move(aura_storgeX, aura_storgeY)
                sleep(0.3)
                ahk.click()
                sleep(0.4)
            except Exception as e:
                showerror("Auto Equip Error", str(e))

        else:
            return None

    def do_obby(self):
        pass

    def do_crafting(self):
        if config.config_data['potion_crafting']['enabled'] == "1":
            send_discord("Crafting", "Going To Craft Potions", footer="Golden's Sol's Macro v0.0")
            try:
                exec(f'{get_action("potion_path")}')
            except Exception as e:
                show_error("Crafting Error", str(e))

    def crafting(self):
        try:
            pass
        except:
            pass

    def chalice(self):
        return None

    # Not Working atm
    def claim_quests(self):
        return None
    
    def item_collecting(self):
        if config.config_data['item_collecting']['enabled'] == "1":
            send_discord("Collecting", "**Collecting Spot Around The Map**", footer="Golden's Macro v0.0")
            try:
                exec(f'{get_action("item_collect")}')
            except Exception as e:
                show_error("Item Collecting Error", str(e))
        else:
            return asyncio.run(self.monitor_logs())

    # Not Working atm
    def item_scheduler(self):
        if config.config_data['enable_items'] == "1":
            try:
                ahk.mouse_move(invo_tabx, invo_taby)
                sleep(0.55)
                ahk.click()
                sleep(0.3)
                ahk.mouse_move(items_tabx, items_taby)
                sleep(0.33)
                ahk.click()
                sleep(0.55)
                ahk.mouse_move(search_itemsx, search_itemsy)
                sleep(0.33)
                ahk.click()
                sleep(0.11)
                ahk.send_input(config.config_data['item_scheduler_item'])
                sleep(0.55)
                ahk.send('{ENTER}')
                sleep(0.43)
                ahk.mouse_move(first1x, first1y)
                sleep(0.4)
                ahk.click()
                sleep(0.33)
                ahk.mouse_move(items_quanx, items_quany)
                sleep(0.55)
                ahk.click()
                sleep(0.1)
                ahk.click()
                sleep(0.33)
                ahk.send_input(config.config_data['item_scheduler_quantity'])
                sleep(0.55)
                ahk.send('{ENTER}')
                sleep(0.43)
                ahk.mouse_move(usex, usey)
                sleep(0.78)
                ahk.click()
                sleep(0.33)
                ahk.mouse_move(invo_tabx, invo_taby)
                sleep(0.55)
                ahk.click()
            except Exception as e:
                show_error("Schelduer Error", str(e))
        else:
            return None

    def align_cam(self):
        send_discord("Aligning", "Aligning Camera...")
        ahk.mouse_move(alignX, alignY)
        sleep(0.55)
        ahk.click()
        sleep(0.3)
        ahk.mouse_move(exit_buttonX, exit_buttonY)
        sleep(0.3)
        ahk.click()
        sleep(0.75)
        ahk.mouse_drag(exit_buttonX, exit_buttonX, from_position=(exit_buttonX, exit_buttonY), button='right', send_mode="Input")
        sleep(0.33)
        for i in range(50):
            ahk.click(button="WU")
            sleep(0.01)
        for i in range(15):
            ahk.click(button="WD")
            sleep(0.01)
        sleep(0.77)
        kc.tap(Key.esc)
        sleep(0.33)
        ahk.key_press("r")
        sleep(0.55)
        kc.tap(Key.enter)

    def reset(self):
        kc.tap(Key.esc)
        sleep(0.33)
        ahk.key_press("r")
        sleep(0.55)
        kc.tap(Key.enter)

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
                    "title": "SolsBot Started",
                    "description": "SolsBot Biome/Aura Detection has started.",
                    "color": 0x00FF00,
                    "timestamp": current_time,
                    "footer": {"text": "SolsBot v1.1.0 Pre2"},
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
                    "title": "SolsBot Stopped",
                    "description": "SolsBot Biome/Aura Detection has stopped.",
                    "color": 0xFF0000,
                    "timestamp": current_time,
                    "footer": {"text": "SolsBot v1.1.0 Pre2"},
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
                    "title": "SolsBot Crashed",
                    "description": f"SolsBot Biome/Aura Detection has crashed due to: {str(e)}",
                    "color": 0xFF0000,
                    "timestamp": current_time,
                    "footer": {"text": "SolsBot v1.1.0 Pre2"},
                    "fields": [{"name": "Private Server Link", "value": tracker.private_server_link}],
                }
                payload = {"content": "@everyone", "embeds": [embed]}
                response = requests.post(tracker.webhook_url, json=payload, timeout=5)
                response.raise_for_status()
                logging.info("Crash webhook sent successfully.")
            except Exception as e:
                logging.error(f"Failed to send crash webhook: {str(e)}")
