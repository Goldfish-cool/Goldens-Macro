from tkinter.messagebox import showerror
from data.lib import config
import multiprocessing
from time import sleep
import ctypes
from pynput import keyboard
from pynput.keyboard import Key, Controller
from ahk import AHK
ahk = AHK()
import tkinter as messagebox
import mouse
import requests
from datetime import datetime, timedelta
import os
from pynput.mouse import Button, Controller
import threading
import time
import json
import re

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

running = False
initialiazed = False
main_process = None
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

def start():
    send_discord("Starting", "Macro Has Been Started...", None, "0x5865F2", f"{datetime.now()}", "Golden's Sol's Macro v0.0")
    global running
    global main_process
    if running == True:
        ctypes.windll.user32.MessageBoxW(0, "Macro Already Running!", "Warning", 0)
        return
    else:
        running = True

    main_process = multiprocessing.Process(target=macro_start)
    main_process.start()

def stop():
    global running
    if running == True:
        running = False
    else:
        ctypes.windll.user32.MessageBoxW(0, "Macro Already Stopped", "Warning", 0)
        return
    global main_process
    main_process.terminate()

def macro_start():
    auto_equip()
    sleep(1)
    align_cam()
    sleep(1)
    do_crafting()
    sleep(1)
    item_scheduler()
    sleep(1)
    chalice()
    sleep(1)
    do_obby()
    sleep(2)
    item_collecting()
    return

def auto_equip():
    if config.config_data['auto_equip']['enabled'] == "1":
        try:
            send_discord("Equiping", f"Auto Equiping {config.config_data['auto_equip']['aura']}", None, None, "Goldem's Sol's Macro v0.0")
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

def do_obby():
    pass

def do_crafting():
    if config.config_data['potion_crafting']['enabled'] == "1":
        send_discord("Crafting", "Going To Craft Potions", None, None, "Golden's Sol's Macro v0.0")
        try:
            exec(f'{get_action("potion_path")}')
        except Exception as e:
            show_error("Crafting Error", str(e))

def crafting():
    try:
        pass
    except:
        pass

def chalice():
    return None

# Not Working atm
def claim_quests():
    return None
    
def item_collecting():
    if config.config_data['item_collecting']['enabled'] == "1":
        send_discord("Collecting", "**Collecting Spot Around The Map**", None, None, "Golden's Sol's Macro v0.0")
        try:
            exec(f'{get_action("item_collect")}')
        except Exception as e:
            show_error("Item Collecting Error", str(e))
    else:
        return None

# Not Working atm
def item_scheduler():
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
            sleep(0.33)
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

def align_cam():
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

def reset():
    kc.tap(Key.esc)
    sleep(0.33)
    ahk.key_press("r")
    sleep(0.55)
    kc.tap(Key.enter)

def loop():
    auto_equip()
    sleep(1)
    claim_quests()
    sleep(1)
    align_cam()
    sleep(1)
    item_scheduler()
    sleep(1)
    chalice()
    sleep(1)
    do_obby()
    sleep(2)
    item_collecting()
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

def get_latest_log_file():
    files = [os.path.join(logs_dir, f) for f in os.listdir(logs_dir) if f.endswith('.log')]
    latest_file = max(files, key=os.path.getmtime)
    return latest_file

def read_log_file(log_file_path):
    if not os.path.exists(log_file_path):
        print(f"Log file not found: {log_file_path}")
        return []

    with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as file:
        lines = file.readlines()
        return lines
    
def biome_check():
    try:
        log_file_path = get_latest_log_file()
        log_lines = read_log_file(log_file_path)

        for line in log_lines:
            for biome in biome_data:
                if biome in line:
                    return biome
    except Exception as e:
        print(f"Error in biome_check: {e}")
        return None

def send_discord(title="", description="", thumbnail="", color=None, timestamp=None, footer=""):
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

class BiomeAuraMonitor:
    def __init__(self):
        self.config = self.load_config()
        self.auras = self.load_auras()
        self.biomes = self.load_biomes()
        
        self.current_biome = None
        self.last_notification = {biome: datetime.min for biome in self.biomes}
        
        self.session_start = None
        self.saved_session_time = self.parse_time(self.config.get("session_time", "0:00:00"))
        
        self.last_log_position = 0
        self.monitoring_active = False
        self.monitoring_thread = None
        self.lock = threading.Lock()
        self.logs = self.get_log_files()
        
        self.start_monitoring()

    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as file:
                return json.load(file)
        return {"session_time": "0:00:00"}

    def load_auras(self):
        auras_path = os.path.join(os.path.dirname(__file__), "auras.json")
        if os.path.exists(auras_path):
            with open(auras_path, "r") as file:
                return json.load(file)
        return {}

    def load_biomes(self):
        biomes_path = os.path.join(os.path.dirname(__file__), "biomes.json")
        if os.path.exists(biomes_path):
            with open(biomes_path, "r") as file:
                return json.load(file)
        return {}

    def get_log_files(self):
        logs_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'Roblox', 'logs')
        if os.path.exists(logs_dir):
            return [os.path.join(logs_dir, f) for f in os.listdir(logs_dir) if f.endswith('.log')]
        return []

    def parse_time(self, time_str):
        parts = time_str.split(":")
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        return 0

    def get_latest_log_file(self):
        if self.logs:
            return max(self.logs, key=os.path.getmtime)
        return None

    def read_log_file(self, log_file_path):
        if not os.path.exists(log_file_path):
            return []
        with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as file:
            file.seek(self.last_log_position)
            lines = file.readlines()
            self.last_log_position = file.tell()
            return lines

    def start_monitoring(self):
        if not self.monitoring_active:
            self.monitoring_active = True
            self.session_start = datetime.now()
            self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            print("Monitoring started.")

    def stop_monitoring(self):
        if self.monitoring_active:
            self.monitoring_active = False
            elapsed_time = int((datetime.now() - self.session_start).total_seconds())
            self.saved_session_time += elapsed_time
            self.session_start = None
            self.save_config()
            print("Monitoring stopped.")

    def monitoring_loop(self):
        last_log_file = None
        while self.monitoring_active:
            try:
                current_log_file = self.get_latest_log_file()
                if current_log_file != last_log_file:
                    self.last_log_position = 0
                    last_log_file = current_log_file
                
                self.detect_biome()
                self.detect_aura(current_log_file)
                time.sleep(1.5)
            except Exception as e:
                print(f"Error in monitoring loop: {e}")

    def detect_biome(self):
        try:
            log_file_path = self.get_latest_log_file()
            log_lines = self.read_log_file(log_file_path)
            for line in reversed(log_lines):
                for biome in self.biomes:
                    if biome in line:
                        self.handle_biome_detection(biome)
                        return
        except Exception as e:
            print(f"Error in detect_biome: {e}")

    def handle_biome_detection(self, biome):
        try:
            if self.current_biome != biome:
                biome_info = self.biomes[biome]
                now = datetime.now()
                print(f"Biome detected: {biome}, Color: {biome_info['color']}, Duration: {biome_info['duration']}")
                self.current_biome = biome
                self.last_notification[biome] = now
                self.send_notification(f"Biome detected: {biome}")
                send_discord(
                    title="Biome Detected",
                    description=f"Biome detected: {biome}",
                    color=biome_info['color'],
                    timestamp=now.isoformat(),
                    footer="Biome Detection"
                )
        except Exception as e:
            print(f"Error in handle_biome_detection: {e}")

    def detect_aura(self, log_file_path):
        try:
            log_lines = self.read_log_file(log_file_path)
            for line in reversed(log_lines):
                match = re.search(r'"state":"Equipped \\"(.*?)\\"', line)
                if match:
                    aura = match.group(1)
                    if aura in self.auras:
                        aura_info = self.auras[aura]
                        rarity = aura_info["rarity"]
                        exclusive_biome, multiplier = aura_info["exclusive_biome"]
                        if self.current_biome == "GLITCHED":
                            rarity /= multiplier
                        elif self.current_biome == exclusive_biome:
                            rarity /= multiplier
                        formatted_rarity = f"{int(rarity):,}"
                        self.send_notification(f"Aura equipped: {aura} (Rarity: 1/{formatted_rarity})")
                        send_discord(
                            title="Aura Equipped",
                            description=f"Aura equipped: {aura} (Rarity: 1/{formatted_rarity})",
                            color=0x5865F2,
                            timestamp=datetime.now().isoformat(),
                            footer="Aura Detection"
                        )
                        return
        except Exception as e:
            print(f"Error in detect_aura: {e}")

    def detect_aura(self, log_file_path):
        try:
            log_lines = self.read_log_file(log_file_path)
            for line in reversed(log_lines):
                match = re.search(r'"state":"Equipped \\"(.*?)\\"', line)
                if match:
                    aura = match.group(1)
                    if aura in self.auras:
                        aura_info = self.auras[aura]
                        rarity = aura_info["rarity"]
                        exclusive_biome, multiplier = aura_info["exclusive_biome"]
                        if self.current_biome == "GLITCHED":
                            rarity /= multiplier
                        elif self.current_biome == exclusive_biome:
                            rarity /= multiplier
                        formatted_rarity = f"{int(rarity):,}"
                        self.send_notification(f"Aura equipped: {aura} (Rarity: 1/{formatted_rarity})")
                        return
        except Exception as e:
            print(f"Error in detect_aura: {e}")

    def send_notification(self, message):
        webhook_url = self.config.get("discord", {}).get("webhook", {}).get("url")
        if not webhook_url:
            print("Webhook URL is missing in the config.")
            return
        payload = {"content": message}
        try:
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            print(f"Notification sent: {message}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send notification: {e}")

    def save_config(self):
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        config = {
            "session_time": self.get_total_session_time(),
            "discord": self.config.get("discord", {})
        }
        with open(config_path, "w") as file:
            json.dump(config, file, indent=4)

    def get_total_session_time(self):
        if self.session_start:
            elapsed_time = datetime.now() - self.session_start
            total_seconds = int(elapsed_time.total_seconds()) + self.saved_session_time
        else:
            total_seconds = self.saved_session_time
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

if __name__ == "__main__":
    monitor = BiomeAuraMonitor()
    monitor.start_monitoring()
