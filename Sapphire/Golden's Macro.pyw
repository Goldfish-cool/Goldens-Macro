import os
import subprocess
import sys
import json
import ctypes
import pathlib
import threading
import time
from PyQt6.QtGui import QGuiApplication, QIcon

def create_main_gui(gui):
    gui.mainloop()

def main():
    from data.main_gui import main_gui
    gui = main_gui.MainWindow()
    create_main_gui(gui)
    
if __name__ == "__main__":
    main()