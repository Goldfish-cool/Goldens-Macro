import multiprocessing
import pyautogui
import time
from time import sleep
import threading
import requests
import os
import mss
from collections import defaultdict
import cv2
import numpy as np
from pynput.mouse import Button, Controller
from pynput.keyboard import Key
from pynput import keyboard
from tkinter import messagebox
import sys
try:
    from data.lib import config
except:
    ctypes.windll.user32.MessageBoxW(0, "Cant open this folder, also who the fuck told you to?", 0)
    sys.exit(1)
import threading
import time
import json
from ahk import AHK
from tkinter.messagebox import showerror
import ctypes
from datetime import datetime, timedelta
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

def parse_time(time_str):
    parts = time_str.split(":")
    if len(parts) == 3:
        hours, minutes, seconds = map(int, parts)
        return hours * 3600 + minutes * 60 + seconds
    return 0

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as file:
            return json.load(file)
    return {"session_time": "0:00:00"}

def load_auras():
    auras_path = os.path.join(os.path.dirname(__file__), "auras.json")
    if os.path.exists(auras_path):
        with open(auras_path, "r", encoding='utf-8', errors='ignore') as file:
            return json.load(file)
    return {}

def load_biomes():
    biomes_path = os.path.join(os.path.dirname(__file__), "biomes.json")
    if os.path.exists(biomes_path):
        with open(biomes_path, "r", encoding='utf-8', errors='ignore') as file:
            return json.load(file)
    return {}

def get_log_files():
    logs_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'Roblox', 'logs')
    if os.path.exists(logs_dir):
        return [os.path.join(logs_dir, f) for f in os.listdir(logs_dir) if f.endswith('.log')]
    return []
    
# Load configurations and data after defining the functions
configure = load_config()
auras = load_auras()
biomes = load_biomes()

current_biome = None
last_notification = {biome: datetime.min for biome in biomes}

session_start = None
saved_session_time = parse_time(configure.get("session_time", "0:00:00"))

last_log_position = 0
monitoring_active = False
monitoring_thread = None
lock = threading.Lock()
logs = get_log_files()



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
    start_monitoring()
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
    start_monitoring()
    item_collecting()
    return

def auto_equip():
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

def do_obby():
    pass

def do_crafting():
    if config.config_data['potion_crafting']['enabled'] == "1":
        send_discord("Crafting", "Going To Craft Potions", footer="Golden's Sol's Macro v0.0")
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
        send_discord("Collecting", "**Collecting Spot Around The Map**", footer="Golden's Macro v0.0")
        try:
            exec(f'{get_action("item_collect")}')
        except Exception as e:
            show_error("Item Collecting Error", str(e))
    else:
        return loop()

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
    start_monitoring()
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
    
def biome_check():
    try:
        log_file_path = get_latest_log_file()
        if not log_file_path:
            return None
            
        with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as file:
            lines = file.readlines()
            for line in reversed(lines):
                for biome in biome_data:
                    if biome in line:
                        return biome
    except Exception as e:
        print(f"Error in biome_check: {e}")
        return None

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
def read_full_log_file(log_file_path):
    if not os.path.exists(log_file_path):
        print(f"Log file not found: {log_file_path}")
        return []

    with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as file:
        return file.readlines()
    
def read_log_file(log_file_path):
    global last_log_position
    if not os.path.exists(log_file_path):
        return []
    with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as file:
        file.seek(last_log_position)
        lines = file.readlines()
        last_log_position = file.tell()
        return lines

def get_latest_log_file():
    try:
        log_dir = os.path.expanduser("~/AppData/Local/Roblox/logs")
        if not os.path.exists(log_dir):
            return None
        logs = [os.path.join(log_dir, f) for f in os.listdir(log_dir) if f.endswith('.log')]
        if logs:
            return max(logs, key=os.path.getmtime)
        return None
    except Exception as e:
        print(f"Error getting log file: {e}")
        return None

def start_monitoring():
    global monitoring_active
    if not monitoring_active:
        monitoring_active = True
        global session_start
        session_start = datetime.now()
        global monitoring_thread
        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitoring_thread.start()
        print("Monitoring started.")

def stop_monitoring():
    global monitoring_active, saved_session_time, session_start
    if monitoring_active:
        monitoring_active = False
        elapsed_time = int((datetime.now() - session_start).total_seconds())
        saved_session_time += elapsed_time
        session_start = None
        config.save_config(config.config_data)
        print("Monitoring stopped.")

def monitoring_loop():
    last_log_file = None
    while monitoring_active:
        try:
            current_log_file = get_latest_log_file()
            if current_log_file != last_log_file:
                global last_log_position
                last_log_position = 0
                last_log_file = current_log_file

            detect_biome()
            detect_aura(current_log_file)
            sleep(1.5)
        except Exception as e:
            print(f"Error in monitoring loop: {e}")


def detect_biome():
    try:
        log_file_path = get_latest_log_file()
        log_lines = read_log_file(log_file_path)
        for line in reversed(log_lines):
            for biome in biomes:
                if biome in line:
                    handle_biome_detection(biome)
                    return
    except Exception as e:
        print(f"hella nah golden, get your ass to fixing this {e}")
    

def handle_biome_detection(biome):
    global current_biome, last_notification # that was a struggle to spell that
    try:
        if current_biome != biome:
            biome_info = biomes[biome]
            now = datetime.now()
            print(f"Biome Detected: {biome}")
            if biome == "WINDY":   
                send_discord("**Biome Detected**", f"# - [{biome}]({config.config_data['discord']['webhook']['ps_link']})", thumbnail="https://i.postimg.cc/6qPH4wy6/image.png", color=0x9ae5ff, timestamp=now.isoformat(), footer="Golden Sol's Biome Detecter")
            elif biome == "RAINY":
                send_discord("**Biome Detected**", f"# - [{biome}]({config.config_data['discord']['webhook']['ps_link']})", thumbnail="https://static.wikia.nocookie.net/sol-rng/images/e/ec/Rainy.png", color=0x027cbd, timestamp=now.isoformat(), footer="Golden Sol's Biome Detecter")
            elif biome == "SNOWY":
                send_discord("**Biome Detected**", f"# - [{biome}]({config.config_data['discord']['webhook']['ps_link']})", thumbnail="https://static.wikia.nocookie.net/sol-rng/images/d/d7/Snowy_img.png", color=0xDceff9, timestamp=now.isoformat(), footer="Golden Sol's Biome Detecter")
            elif biome == "SAND STORM":
                send_discord("**Biome Detected**", f"# - [{biome}]({config.config_data['discord']['webhook']['ps_link']})", thumbnail="https://i.postimg.cc/3JyL25Kz/image.png", color=0x8F7057, timestamp=now.isoformat(), footer="Golden Sol's Biome Detecter")
            elif biome == "HELL":
                send_discord("**Biome Detected**", f"# - [{biome}]({config.config_data['discord']['webhook']['ps_link']})", thumbnail="https://i.postimg.cc/hGC5xNyY/image.png", color=0xff4719, timestamp=now.isoformat(), footer="Golden Sol's Biome Detecter")
            elif biome == "STARFALL":
                send_discord("**Biome Detected**", f"# - [{biome}]({config.config_data['discord']['webhook']['ps_link']})", thumbnail="https://i.postimg.cc/1t0dY4J8/image.png", color=0x011ab7, timestamp=now.isoformat(), footer="Golden Sol's Biome Detecter")
            elif biome == "CORRUPTION":
                send_discord("**Biome Detected**", f"# - [{biome}]({config.config_data['discord']['webhook']['ps_link']})", thumbnail="https://i.postimg.cc/ncZQ84Dh/image.png", color=0x6d32a8, timestamp=now.isoformat(), footer="Golden Sol's Biome Detecter")
            elif biome == "NULL":
                send_discord("**Biome Detected**", f"# - [{biome}]({config.config_data['discord']['webhook']['ps_link']})", thumbnail= "https://static.wikia.nocookie.net/sol-rng/images/f/fc/NULLLL.png", color=0x838383, timestamp=now.isoformat(), footer="Golden Sol's Biome Detecter")
            elif biome == "GLITCHED":
                send_message("@everyone")
                send_discord("**Biome Detected**", f"# - [{biome}]({config.config_data['discord']['webhook']['ps_link']})", thumbnail="https://i.postimg.cc/W3Lhtn5g/image.png", color=0xbfff00, timestamp=now.isoformat(), footer="Golden Sol's Biome Detecter")
            elif biome == "DREAMSPACE":
                send_message("@everyone")
                send_discord("**Biome Detected**", f"# - [{biome}]({config.config_data['discord']['webhook']['ps_link']})", thumbnail="https://i.postimg.cc/rFjCcW3w/image.png", color=0xea9dda, timestamp=now.isoformat(), footer="Golden Sol's Biome Detecter")
                
            # Update current biome
            current_biome = biome
            last_notification[biome] = now
    except Exception as e:
        print(f"damn golden, dis failed badly, fix it up {e}")
    

def detect_aura(log_file_path):
    global auras
    try:
        log_lines = read_full_log_file(log_file_path)
        for line in reversed(log_lines):
            match = re.search(r'"state":"Equipped \\"(.*?)\\"', line)
            if match:
                aura = match.group(1)
                if aura in auras:
                    aura_info = auras[aura]
                    rarity = aura_info["rarity"]
                    exclusive_biome, multiplier = aura_info["exclusive_biome"]
                    
                    # Apply rarity modifiers based on biome
                    if current_biome == "GLITCHED":
                        rarity /= multiplier
                        biome_message = "[From GLITCHED!]"
                    elif current_biome == exclusive_biome:
                        rarity /= multiplier
                        biome_message = f"[From {exclusive_biome}!]"
                    else:
                        biome_message = ""
                        
                    formatted_rarity = f"{int(rarity):,}"
                    print(f"Aura Detected: {aura}")
                    
                    # Track last aura found to detect changes
                    if not hasattr(detect_aura, 'last_aura_name'):
                        detect_aura.last_aura_name = None
                    
                    # Only send webhook if aura name has changed
                    if aura != detect_aura.last_aura_name:
                        send_message(f"<@{config.config_data['discord']['webhook']['ping_id']}>")
                        send_discord(
                            "Aura Detection",
                            f"**Aura Equipped/Found: {aura} {biome_message} (rarity: 1/{formatted_rarity})**",
                            color=aura_info['color'],
                            footer="Golden's Aura Detection"
                        )
                        detect_aura.last_aura_name = aura
                    else:
                        print(f"Same aura detected again: {aura}")
                    return
    except Exception as e:
        print(f"aura dection is broken: {e}")

def send_message(message):
    webhook_url = config.config_data['discord']['webhook']['url']
    if not webhook_url:
        print("Webhook is missing")
        return
    payload = {"content": message}
    try:
        response = requests.post(webhook_url, json=payload)
        print(f"Notification sent: {message}")
    except requests.exception.RequestException as e:
        print(f"Failed to send a notification: {e}")

def save_config():
    try:
        config_pather = f"{config.parent_path()}\\data\\lib\\config.json"
        configer = {
            "session_time": get_total_session_time(),
            "discord": config.config_data.get("discord", {})
        }
        with open(config_pather, "w") as file:
            json.dump(config, file, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

def get_total_session_time():
    if session_start:
        elapsed_time = datetime.now() - session_start
        total_seconds = int(elapsed_time.total_seconds()) + saved_session_time
    else:
        total_seconds = saved_session_time
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"
