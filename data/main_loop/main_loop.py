from data.lib import config
import multiprocessing
from time import sleep
import ctypes
from pynput import keyboard
from pynput.keyboard import Key
from pynput.mouse import Button, Controller 

mouse = Controller()
kc = keyboard.Controller()

running = False
initialiazed = False
main_process = None

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
    item_scheduler()
    sleep(1)
    chalice()
    sleep(1)
    do_obby()
    sleep(2)
    item_collecting()
    return

def auto_equip():
    pass

def do_obby():
    pass

def chalice():
    pass

def item_collecting():
    pass

def item_scheduler():
    pass

def loop():
    auto_equip()
    sleep(1)
    item_scheduler()
    sleep(1)
    chalice()
    sleep(1)
    do_obby()
    sleep(2)
    item_collecting()
    return

