from data.lib import config
import multiprocessing
from time import sleep
import ctypes
from pynput import keyboard
from pynput.keyboard import Key
from ahk import AHK
ahk = AHK()  
from data.lib import config
import tkinter as messagebox


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
quest_tabx = config.config_data['clicks']['QuestX']
quest_taby = config.config_data['clicks']['QuestY']
daily_tabx = config.config_data['clicks']['DailyX']
daily_taby = config.config_data['clicks']['DailyY']
slot_1x = config.config_data['clicks']['SlotX']
slot_1y = config.config_data['clicks']['SlotY']
claimx = config.config_data['clicks']['ClaimX']
claimy = config.config_data['clicks']['ClaimY']
invo_tabx = config.config_data['clicks']['QuestX']
invo_taby = config.config_data['clicks']['QuestY']
items_tabx = config.config_data['clicks']['DailyX']
items_taby = config.config_data['clicks']['DailyY']
first1x = config.config_data['clicks']['SlotX']
first1y = config.config_data['clicks']['SlotY']
usex = config.config_data['clicks']['ClaimX']
usey = config.config_data['clicks']['ClaimY']

running = False
initialiazed = False
main_process = None
azerty_replace_dict = {"w":"z", "a":"q"}

with open("path.txt", "r") as file:
    config_file = f"{file.read()}\\data\\lib\\config.json"

def walk_time_conversion(d):
    if config.settings_data["settings"]["vip+_mode"] == "1":
        return d
    elif config.settings_data["settings"]["vip_mode"] == "1":
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
    claim_quests()
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
            sleep(1.3)
            ahk.mouse_move(aura_storgeX, aura_storgeY, speed=10)
            sleep(0.45)
            ahk.click()
            sleep(0.55)
            if config.config_data['auto_equip']['special_aura'] == "0":
                ahk.mouse_move(regular_tabX, regular_taby)
                sleep(0.55)
                ahk.click()
            else:
                ahk.mouse_move(special_tabX, special_tabY, speed=10)
                sleep(0.55)
                ahk.click()
            ahk.mouse_move(aura_searchX, aura_searchY, speed=10)
            sleep(0.55)
            ahk.click()
            sleep(0.55)
            ahk.send_input(config.config_data['auto_equip']['aura'])
            sleep(0.3)
            kc.tap(Key.enter)
            sleep(0.55)
            ahk.mouse_move(slot_1X, slot_1Y, speed=10)
            sleep(0.55)
            ahk.click()
            sleep(0.5)
            ahk.mouse_move(equip_buttonX, equip_buttonY, speed=10)
            sleep(0.2)
            ahk.click()
            sleep(0.2)
            ahk.mouse_move(aura_searchX, aura_searchY, speed=10)
            sleep(0.3)
            ahk.click()
            sleep(0.3)
            kc.tap(Key.enter)
            ahk.mouse_move(aura_storgeX, aura_storgeY, speed=10)
            sleep(0.3)
            ahk.click()
            sleep(0.4)
            align_cam()
        except Exception as e:
            show_error("Auto Equip Error", str(e))

    else:
        return claim_quests()

def do_obby():
    pass

def chalice():
    pass

def claim_quests():
    if config.config_data['claim_daily_quests'] == "1":
        try:
            sleep(2.3)
            ahk.mouse_move(quest_tabx, quest_taby, speed=10)
            sleep(0.45)
            ahk.click()
            sleep(0.55)
            ahk.mouse_move(daily_tabx, daily_taby, speed=10)
            sleep(0.55)
            ahk.click()
            sleep(0.45)
            ahk.mouse_move(slot_1x, slot_1y, speed=10)
            sleep(0.55)
            ahk.click()
            sleep(0.3)
            ahk.mouse_move(claimx, claimy, speed=10)
            sleep(0.4)
            ahk.click()
            sleep(0.5)
            ahk.mouse_move(slot_1x, slot_1y + 80, speed=10)
            sleep(0.55)
            ahk.click()
            sleep(0.3)
            ahk.mouse_move(claimx, claimy)
            sleep(0.3)
            ahk.click()
            sleep(0.3)
            ahk.mouse_move(slot_1x, slot_1y + 140, speed=10)
            sleep(0.55)
            ahk.click()
            sleep(0.3)
            ahk.mouse_move(claimx, claimy, speed=10)
            sleep(0.55)
            ahk.click()
            sleep(0.5)
            ahk.mouse_move(quest_tabx, quest_taby, speed=10)
            sleep(0.45)
            ahk.click()
            sleep(1)
        except Exception as e:
            show_error("Quest Error", str(e))
    else:
        return item_scheduler()
    
def item_collecting():
    pass

def item_scheduler():
    if config.config_data['enable_items'] == "1":
        try:
            ahk.mouse_move(invo_tabx, invo_taby)
            sleep(0.55)
            ahk.click()
            sleep(0.3)
            ahk.mouse_move()
        except Exception as e:
            show_error("Schelduer Error", str(e))
    else:
        return loop()

def align_cam():
    ahk.mouse_move(alignX, alignY, speed=10)
    sleep(0.55)
    ahk.click()
    sleep(0.3)
    ahk.mouse_move(exit_buttonX, exit_buttonY, speed=10)
    sleep(0.3)
    ahk.click()
    sleep(1)
    ahk.mouse_drag(button='r', x=exit_buttonX, y=exit_buttonY, speed=2)

   
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
        "Glitched": {"color": 0xbfff00, "duration": 164}
    }
