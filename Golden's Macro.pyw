import os
import subprocess
import sys
import json
import ctypes
import pathlib
import threading

sys.dont_write_bytecode = True
sys.path.append(pathlib.Path(__file__).parent.resolve())

def create_main_gui(gui):
    gui.mainloop()

def set_path():
    # This approach works for both regular Python scripts and compiled executables
    if getattr(sys, 'frozen', False):
        # If the application is frozen (compiled)
        path = os.path.dirname(sys.executable)
    else:
        # If running as a normal Python script
        path = str(pathlib.Path(__file__).parent.resolve())
    
    with open("path.txt", "w") as file:
        file.write(path)
    
    print(f"Directory path written to path.txt: {path}")
def main():
    
    set_path()
    from data.main_gui import main_gui
    gui = main_gui.MainWindow()
    create_main_gui(gui)
    
if __name__ == "__main__":
    main()
