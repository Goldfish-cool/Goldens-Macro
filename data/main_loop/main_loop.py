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
        ahk.set_send_mode("Event")
        ahk.set_coord_mode("Screen", "Mouse")
       
    async def start_macro(self):
        while True:
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
                ahk.mouse_move(aura_storgeX, aura_storgeY)
                await asyncio.sleep(0.45)
                ahk.click()
                await asyncio.sleep(0.55)
                if config.config_data['auto_equip']['special_aura'] == "0":
                    ahk.mouse_move(regular_tabX, regular_taby)
                    await asyncio.sleep(0.55)
                    ahk.click()
                else:
                    ahk.mouse_move(special_tabX, special_tabY)
                    await asyncio.sleep(0.55)
                    ahk.click()
                ahk.mouse_move(aura_searchX, aura_searchY)
                await asyncio.sleep(0.55)
                ahk.click()
                await asyncio.sleep(0.55)
                ahk.send_input(config.config_data['auto_equip']['aura'])
                await asyncio.sleep(0.3)
                kc.tap(Key.enter)
                await asyncio.sleep(0.55)
                ahk.mouse_move(slot_1X, slot_1Y)
                await asyncio.sleep(0.55)
                ahk.click()
                await asyncio.sleep(0.5)
                ahk.mouse_move(equip_buttonX, equip_buttonY)
                await asyncio.sleep(0.2)
                ahk.click()
                await asyncio.sleep(0.2)
                ahk.mouse_move(aura_searchX, aura_searchY)
                await asyncio.sleep(0.3)
                ahk.click()
                await asyncio.sleep(0.3)
                kc.tap(Key.enter)
                ahk.mouse_move(aura_storgeX, aura_storgeY)
                await asyncio.sleep(0.3)
                ahk.click()
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
                ahk.mouse_move(invo_tabx, invo_taby)
                await asyncio.sleep(0.55)
                ahk.click()
                await asyncio.sleep(0.3)
                ahk.mouse_move(items_tabx, items_taby)
                await asyncio.sleep(0.33)
                ahk.click()
                await asyncio.sleep(0.55)
                ahk.mouse_move(search_itemsx, search_itemsy)
                await asyncio.sleep(0.33)
                ahk.click()
                await asyncio.sleep(0.11)
                ahk.send_input(config.config_data['item_scheduler_item'])
                await asyncio.sleep(0.55)
                ahk.send('{ENTER}')
                await asyncio.sleep(0.43)
                ahk.mouse_move(first1x, first1y)
                await asyncio.sleep(0.4)
                ahk.click()
                await asyncio.sleep(0.33)
                ahk.mouse_move(items_quanx, items_quany)
                await asyncio.sleep(0.55)
                ahk.click()
                await asyncio.sleep(0.1)
                ahk.click()
                await asyncio.sleep(0.33)
                ahk.send_input(config.config_data['item_scheduler_quantity'])
                await asyncio.sleep(0.55)
                ahk.send('{ENTER}')
                await asyncio.sleep(0.43)
                ahk.mouse_move(usex, usey)
                await asyncio.sleep(0.78)
                ahk.click()
                await asyncio.sleep(0.33)
                ahk.mouse_move(invo_tabx, invo_taby)
                await asyncio.sleep(0.55)
                ahk.click()
            except Exception as e:
                show_error("Schelduer Error", str(e))
        else:
            return None

    async def align_cam(self):
        send_discord("Aligning", "Aligning Camera...")
        ahk.mouse_move(alignX, alignY)
        await asyncio.sleep(0.55)
        ahk.click()
        await asyncio.sleep(0.3)
        ahk.mouse_move(exit_buttonX, exit_buttonY)
        await asyncio.sleep(0.3)
        ahk.click()
        await asyncio.sleep(0.75)
        ahk.mouse_drag(exit_buttonX, exit_buttonX, from_position=(exit_buttonX, exit_buttonY), button='right', send_mode="Input")
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
