import multiprocessing
from time import sleep
import json
import re
import threading
import requests
import os
import keyboard
from pathlib import Path
import time
import asyncio
from pynput.keyboard import Key
from pynput import keyboard
from tkinter import messagebox
import sys
try:
    from data.lib import config
except:
    ctypes.windll.user32.MessageBoxW(0, "Cant open this folder, also who the fuck told you to?", 0)
    sys.exit(1)

from ahk import AHK
import ctypes
from datetime import datetime, timedelta
ahk = AHK()

config.config_data = config.read_config()
kc = keyboard.Controller()
# AURA STORAGE
aura_storage = config.config_data['clicks']['aura_storage']
regular_tab = config.config_data['clicks']['regular_tab']
special_tab = config.config_data['clicks']['special_tab']
search_bar = config.config_data['clicks']['search_bar']
aura_first_slot = config.config_data['clicks']['aura_first_slot']
equip_button = config.config_data['clicks']['equip_button']
# ALIGNMENT MENU
collection_menu = config.config_data['clicks']['collection_menu']
exit_collection = config.config_data['clicks']['exit_collection']
# ITEM SCHELDUAR
items_storage = config.config_data['clicks']['items_storage']
items_tab = config.config_data['clicks']['items_tab']
items_bar = config.config_data['clicks']['items_bar']
item_value = config.config_data['clicks']['item_first_slot']
quanity_bar = config.config_data['clicks']['item_value']
use_button = config.config_data['clicks']['use_button']
# MERCHANT
merchant_name = config.config_data['clicks']['merchant_name']
merchant_hold_button = config.config_data['clicks']['merchant_hold_button']
merchant_open_button = config.config_data['clicks']['merchant_open_button']
merchant_item_name = config.config_data['clicks']['merchant_item_name']
merchant_first_slot = config.config_data['clicks']['merchant_slot_1']
merchant_amount_box = config.config_data['clicks']['merchant_amount_box']
merchant_purchase_button = config.config_data['clicks']['merchant_buy_button']

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
        with open(f'{path_file.read()}\\data\\lib\\{file}.py') as file:
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
    main_loop = MainLoop()
    asyncio.run(main_loop.start())

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
        if config.config_data['important_only'] =="0":
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
    else:
        return None
    
class MainLoop:
    def __init__(self):
        self.config = self._load_config()
        self.biomes = self._load_biome_data()
        self.auras = self._load_aura_data()
        self.current_biome = None
        self.biome_counts = {b["name"]: 0 for b in self.biomes.values()}
        self.last_aura = None
        self.last_processed_position = 0
        self.last_sent_biome = None
        self.last_sent_aura = None
        self.biome_alerts = self.config.get("biome_alerts", {})
        self.webhook_url = config.config_data['discord']["webhook"]["url"]
        self.private_server_link = config.config_data['discord']["webhook"]["ps_link"]
        self.lock = threading.Lock()
        self.last_quest = datetime.min
        self.last_item = datetime.min
        self.check_roblox_status = None
        self.running = threading.Event()
        self.thread = None
        self.biome_detection_running = threading.Event()
        self.biome_detection_thread = None
        self.biome_detection = None
        self.merchant_items = None 
        self.merchant_webhook = None

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
                            "current_version": "1.0",
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
                print("Created default config file")
            except Exception as e:
                print(f"Failed to create config: {str(e)}")

    def _load_config(self):
        try:
            with open("settings.cfg") as f:
                config = json.load(f)
                for biome in self._load_biome_data():
                    if biome not in config.get("biome_alerts", {}):
                        config["biome_alerts"][biome] = False
                return config
        except Exception as e:
            print(f"Config load error: {str(e)}")
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
            print(f"Loaded biome data from {response.url}")
            return {biome["name"]: biome for biome in biome_list}
        except Exception as e:
            print(f"Failed to load biome data: {str(e)}")
            return {}

    def _load_aura_data(self):
        try:
            response = requests.get("https://raw.githubusercontent.com/Goldfish-cool/Goldens-Macro/refs/heads/data/aura-data.json")
            response.raise_for_status()
            aura_list = response.json()
            print(f"Loaded aura data from {response.url}")
            return {aura["identifier"]: aura for aura in aura_list}
        except Exception as e:
            print(f"Failed to load aura data: {str(e)}")
            return {}

    def start(self):
        if not self.running.is_set():
            self._send_webhook(
                title=f"{time.strftime('[%H:%M:%S]')} Starting",
                description="",
                color=0x64ff5e,
                thumbnail=None,
                urgent=False,
                is_aura=False
            )
            print("Starting Macro!")
            self.running.set()
            self.thread = threading.Thread(target=lambda: asyncio.run(self.loop_process()))
            self.thread.start()

        if config.config_data['biome_detection']['enabled'] == "1":
            if not self.biome_detection_running.is_set():
                self.biome_detection_running.set()
                self.biome_detection_thread = threading.Thread(target=lambda: asyncio.run(self.monitor_logs()))
                self.biome_detection_thread.start()

    def stop(self):
        self._send_webhook(
            title=f"{time.strftime('[%H:%M:%S]')} Stopped",
            description="",
            color=0xff0000,
            thumbnail=None,
            urgent=False,
            is_aura=False
        )
        print("Stopping the whole process...")
        # Clear both running flags
        self.running.clear()
        self.biome_detection_running.clear()
        
        # Stop the main loop thread
        if self.thread is not None:
            try:
                self.thread.join(timeout=2)
            except Exception as e:
                print(f"Error stopping main thread: {e}")
            finally:
                self.thread = None

        # Stop the biome detection thread
        if self.biome_detection_thread is not None:
            try:
                self.biome_detection_thread.join(timeout=2)
            except Exception as e:
                print(f"Error stopping biome detection thread: {e}")
            finally:
                self.biome_detection_thread = None
        
        print("All processes stopped successfully")

    async def loop_process(self):
        print("Starting main loop process...")
        while self.running.is_set():
            try:
                if not self.running.is_set():
                    break
                self.activate_window(titles="Roblox")
                await asyncio.sleep(1)
                await self.auto_equip()
                await asyncio.sleep(1)
                await self.align_cam()
                await asyncio.sleep(1)
                await self.claim_quests()
                await asyncio.sleep(1)
                await self.item_collecting()
                await asyncio.sleep(1)
            except Exception as e:
                print(f"Error in main loop: {e}")
                if not self.running.is_set():
                    break
                await asyncio.sleep(5)
        print("Main loop process stopped")
    
    async def auto_equip(self):
        if config.config_data['auto_equip']['enabled'] == "1":
            try:

                send_discord("Equiping", f"Auto Equiping: {config.config_data['auto_equip']['aura']}", footer="Golden's Sol's Macro v0.0")
                await asyncio.sleep(1.3)
                ahk.click(aura_storage[0], aura_storage[1], coord_mode="Screen")
                await asyncio.sleep(0.55)
                if config.config_data['auto_equip']['special_aura'] == "0":
                    ahk.click(regular_tab[0], regular_tab[1], coord_mode="Screen")
                    await asyncio.sleep(0.55)
                else:
                    ahk.click(special_tab[0], special_tab[1], coord_mode="Screen")
                    await asyncio.sleep(0.55)
                ahk.click(search_bar[0], search_bar[1], coord_mode="Screen")
                await asyncio.sleep(0.55)
                ahk.send_input(config.config_data['auto_equip']['aura'])
                await asyncio.sleep(0.3)
                kc.tap(Key.enter)
                await asyncio.sleep(0.55)
                ahk.click(aura_first_slot[0], aura_first_slot[1], coord_mode="Screen")
                await asyncio.sleep(0.55)
                ahk.click(equip_button[0], equip_button[1], coord_mode="Screen")
                await asyncio.sleep(0.2)
                ahk.click(search_bar[0], search_bar[1], coord_mode="Screen")
                await asyncio.sleep(0.3)
                kc.tap(Key.enter)
                ahk.click(aura_storage[0], aura_storage[1], coord_mode="Screen")
                await asyncio.sleep(0.4)
            except Exception as e:
                messagebox.showerror("Auto Equip Error", str(e))
        else:
            return None

    async def do_obby(self):
        pass

    async def do_crafting(self):
        if config.config_data['potion_crafting']['enabled'] == "1":
            send_discord("Crafting", "Going To Craft Potions", footer="Golden's Sol's Macro v0.0")
            try:
                exec(f'{get_action("potion_path")}')
            except Exception as e:
                messagebox.showerror(title="Crafting Error", message=f"{str(e)}")

    async def crafting(self):
        try:
            pass
        except:
            pass

    async def chalice(self):
        return None

    async def claim_quests(self):
        return None
    
    async def item_collecting(self):
        if config.config_data['item_collecting']['enabled'] == "1":
            send_discord("Collecting", "**Collecting Spot Around The Map**", footer="Golden's Macro v0.0")
            try:
                exec(f'{get_action("item_collect")}')
            except Exception as e:
                messagebox.showerror(title="Item Collecting Error", message=f"{str(e)}")
        else:
            return None

    async def align_cam(self):
        send_discord("Aligning", "Aligning Camera...")
        ahk.click(collection_menu[0], collection_menu[1], coord_mode="Screen")
        await asyncio.sleep(0.55)
        ahk.click(exit_collection[0], exit_collection[1], coord_mode="Screen")
        await asyncio.sleep(0.75)
        ahk.mouse_drag(exit_collection[0], exit_collection[0], from_position=(exit_collection[0], exit_collection[1]), button='right', coord_mode="Screen", send_mode="Input")
        await asyncio.sleep(0.33)
        for i in range(50):
            ahk.click(button="WU")
            await asyncio.sleep(0.01)
        for i in range(15):
            ahk.click(button="WD")
            await asyncio.sleep(0.01)
        await asyncio.sleep(0.77)
        kc.tap(Key.esc)
        await asyncio.sleep(0.33)
        ahk.key_press("r")
        await asyncio.sleep(0.55)
        kc.tap(Key.enter)

    def reset(self):
        kc.tap(Key.esc)
        sleep(0.33)
        ahk.key_press("r")
        sleep(0.55)
        kc.tap(Key.enter)

    def activate_window(self, titles=""):
        try:
            import pywinctl as pwc
        except ImportError:
            messagebox.showerror(title="Import Error", message=f"Failed to activate: {titles}")
            return

        windows = pwc.getAllTitles()
        the_window = titles
        if the_window not in windows:
            messagebox.showerror(title="Error", message=f"No window found with title: {titles}")
        else:
            for window in windows:
                if titles in window:
                    pwc.getWindowsWithTitle(window)[0].activate()
                    break
            else:
                messagebox.showerror(title="Error", message=f"No window found with title containing 'Roblox'")
    
    def auto_loop_stuff(self):
        get_quest = config.config_data['settings']['claim_quest'] == "1"
        try:
            claim_quest = timedelta(minutes=30)
        except ValueError:
            claim_quest = timedelta(minutes=30)
        
        if get_quest and datetime.now() - self.last_quest_time >= claim_quest:
            self.claim_quests()
            self.last_quest_time = datetime.now()
            
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
                print(f"Log monitoring error: {str(e)}")
                await asyncio.sleep(5)

    async def _process_log_entry(self, line):
        try:
            self._detect_biome_change(line)
            self._check_aura_equipped(line)
        except Exception as e:
            print(f"Log processing error: {str(e)}")

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
            print(f"Biome detection error: {str(e)}")

    def _handle_new_biome(self, biome_name):
        try:
            self.current_biome = biome_name
            self.biome_counts[biome_name] += 1
            print(f"Biome detected: {biome_name}")

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
                else:
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
            print(f"Received unknown biome: {biome_name}")
        except Exception as e:
            print(f"Biome handling error: {str(e)}")

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
            print(f"Aura check error: {str(e)}")

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
                or self.current_biome == "DREAMSPACE"
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

            print(f"Aura equipped: {aura_name} (1 in {rarity:,})")

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
            print(f"Missing aura property: {str(e)}")
        except ZeroDivisionError:
            print("Invalid biome amplifier value (division by zero)")
        except Exception as e:
            print(f"Aura processing error: {str(e)}")

    def _send_webhook(
        self, title, description, color, thumbnail=None, urgent=False, is_aura=False, fields=None
    ):
        if not self.webhook_url:
            print(f"Please specify a Webhook URL in the config")
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
                        ps_link = "No Private Server Link (nice on buddy :skull:)."
                    embed["fields"] = [{"name": "Private Server Link", "value": ps_link}]

            if thumbnail:
                embed["thumbnail"] = {"url": thumbnail}

            payload = {"content": "@everyone" if urgent else None, "embeds": [embed]}
            print(f"Attempting to send webhook: {payload}")

            # Use requests directly instead of asyncio
            try:
                response = requests.post(self.webhook_url, json=payload, timeout=5)
                if response.status_code == 429:
                    retry_after = response.json().get("retry_after", 5)
                    print(f"Rate limited - retrying in {retry_after}s")
                    time.sleep(retry_after)
                    response = requests.post(self.webhook_url, json=payload, timeout=5)
                response.raise_for_status()
            except Exception as e:
                print(f"Webhook failed: {str(e)}")

        except Exception as e:
            print(f"Webhook creation error: {str(e)}")

