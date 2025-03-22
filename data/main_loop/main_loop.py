import multiprocessing
from time import sleep
import webbrowser
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
from datetime import datetime, timedelta
ahk = AHK()

config.config_data = config.read_config()
kc = keyboard.Controller()
aura_storage = config.config_data['clicks']['aura_storage']
regular_tab = config.config_data['clicks']['regular_tab']
special_tab = config.config_data['clicks']['special_tab']
search_bar = config.config_data['clicks']['search_bar']
aura_first_slot = config.config_data['clicks']['aura_first_slot']
equip_button = config.config_data['clicks']['equip_button']
collection_menu = config.config_data['clicks']['collection_menu']
exit_collection = config.config_data['clicks']['exit_collection']
items_storage = config.config_data['clicks']['items_storage']
items_tab = config.config_data['clicks']['items_tab']
items_bar = config.config_data['clicks']['items_bar']
item_value = config.config_data['clicks']['item_value']
quanity_bar = config.config_data['clicks']['item_value']
use_button = config.config_data['clicks']['use_button']

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
    if __name__ == '__main__':
        multiprocessing.freeze_support()
        main_process = multiprocessing.Process(target=macro_start)
        main_process.start()

def stop():
    global running, main_process
    if running == True:
        running = False
    else:
        messagebox.showinfo(title="Info", message="Macro Already Stopped")
        return
    if __name__ == '__main__':
        multiprocessing.freeze_support()
        main_process.terminate()

def macro_start():
    main_loop = MainLoop()
    asyncio.run(main_loop.start_macro())

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
        self.webhook_url = config.config_data['discord']["webhook"]["url"]
        self.private_server_link = config.config_data['discord']["webhook"]["ps_link"]
        self.lock = threading.Lock()
        self.last_quest = datetime.min
        self.last_item = datetime.min
        self.check_roblox_status = None

       
    async def start_macro(self):
        while True:
            self.activate_window(titles="Roblox")
            await self.auto_equip()
            await asyncio.sleep(1)
            await self.align_cam()
            await asyncio.sleep(1)
            await self.claim_quests()
            await asyncio.sleep(1)
            await self.item_scheduler()
            await asyncio.sleep(1)
            await self.item_collecting()
            await asyncio.sleep(1)  # Sleep for a bit before starting the loop again
    
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

    async def claim_quests(self):
        return None
    
    async def item_collecting(self):
        if config.config_data['item_collecting']['enabled'] == "1":
            send_discord("Collecting", "**Collecting Spot Around The Map**", footer="Golden's Macro v0.0")
            try:
                exec(f'{get_action("item_collect")}')
            except Exception as e:
                show_error("Item Collecting Error", str(e))
        else:
            return None

    async def item_scheduler(self):
        if config.config_data['enable_items'] == "1":
            try:
                ahk.click(items_storage[0], items_storage[1], coord_mode="Screen")
                await asyncio.sleep(0.55)
                ahk.click(items_tab[0], items_tab[1], coord_mode="Screen")
                await asyncio.sleep(0.33)
                ahk.click(items_bar[0], items_bar[1], coord_mode="Screen")
                await asyncio.sleep(0.33)
                ahk.send_input(config.config_data['item_scheduler_item'])
                await asyncio.sleep(0.55)
                ahk.send('{ENTER}')
                await asyncio.sleep(0.43)
                ahk.click(item_value[0], item_value[1], coord_mode="Screen")
                await asyncio.sleep(0.33)
                ahk.click(quanity_bar[0], quanity_bar[1], coord_mode="Screen")
                await asyncio.sleep(0.1)
                ahk.click()
                await asyncio.sleep(0.33)
                ahk.send_input(config.config_data['item_scheduler_quantity'])
                await asyncio.sleep(0.55)
                ahk.send('{ENTER}')
                await asyncio.sleep(0.43)
                ahk.click(use_button[0], use_button[1], coord_mode="Screen")
                await asyncio.sleep(0.78)
                ahk.click(items_storage[0], items_storage[1], coord_mode="Screen")
            except Exception as e:
                show_error("Schelduer Error", str(e))
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

    def auto_loop_stuff(self):
        get_quest = config.config_data['claim_daily_quests'] == "1"
        try:
            claim_quest = timedelta(minutes=30)
        except ValueError:
            claim_quest = timedelta(minutes=30)
        
        if get_quest and datetime.now() - self.last_quest >= claim_quest:
            self.claim_quests()
            self.last_quest = datetime.now()
    
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
