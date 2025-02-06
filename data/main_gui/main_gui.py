from customtkinter import *
import ctypes
from pynput.mouse import Button, Controller
import keyboard
import tkinter as ttk
try:
    from data.lib import config
except ImportError:
    ctypes.windll.user32.MessageBoxW(0, "Cant Open 'main_gui.py',\nPlease Use the Proper File", "Error", 0)
from time import sleep 
from ahk import AHK 

deactivate_automatic_dpi_awareness()

VERSION = config.get_current_version()

class MainWindow(CTk):
    def __init__(self, config_key=None, callback=None):
        super().__init__()
        self.title(f"Golden's Sol's Macro v{VERSION}")
        self.geometry("630x315x200x200")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.snipping_window = None
        self.begin_x = None
        self.begin_y = None
        self.end_x = None
        self.end_y = None
        self.config_key = config_key
        self.callback = callback
        # Set Tabs
        self.tab_control = CTkTabview(master=self, fg_color=["gray86", "gray17"], height=265, corner_radius=10, border_width=2)
        main_tab = self.tab_control.add("Main")
        discord_tab = self.tab_control.add("Discord")
        crafting_tab = self.tab_control.add("Crafting")
        settings_tab = self.tab_control.add("Settings")
        credits_tab = self.tab_control.add("Credits")

        self.tab_control.grid(padx=10)
        #self.tab_control.set("Credits")
        self.tk_var_list = config.generate_tk_list()

        for button in self.tab_control._segmented_button._buttons_dict.values():
            button.configure(width=1000, height=35, corner_radius=10, border_width=2, font=("Segoe UI", 15, "bold"))
        
        buttons_frame = CTkFrame(master=self)
        buttons_frame.grid(row=1, pady=(5, 8), padx=6, sticky="s")

        start_button = CTkButton(master=buttons_frame, text="Start - F1", command=self.start, height=30, width=100)#, corner_radius=10, border_width=2)
        start_button.grid(row=0, column=0, padx=4, pady=4)

        stop_button = CTkButton(master=buttons_frame, text="Stop - F2", command=self.stop, height=30, width=100)#, corner_radius=10, border_width=2)
        stop_button.grid(row=0, column=1, padx=4, pady=4)
        
        # TODO
        keyboard.add_hotkey("F1", self.start)
        keyboard.add_hotkey("F2", self.stop)
        keyboard.add_hotkey("F3", self.restart)

        random_frame = CTkFrame(master=main_tab, fg_color=["gray81", "gray23"])
        random_frame.grid(row=0, column=0, sticky="n", padx=(1, 1))
        miscalance_title = CTkLabel(master=random_frame, text="Miscalances", font=("Segoe UI Semibold", 20, "bold")).grid(row=0, column=1)

        obby = CTkCheckBox(master=random_frame, text="Obby (30% Luck Boost Every loop or 4 Mins)", variable=self.tk_var_list['obby']['enabled'], onvalue="1", offvalue="0").grid(row=2, column=1, padx=5, pady=5, stick="w")
        chalice = CTkCheckBox(master=random_frame, text="Auto Chalice (Collected Biomes Items 30% Luck)", variable=self.tk_var_list['chalice']['enabled'], onvalue="1", offvalue="0").grid(row=3, column=1, padx=5, pady=5, stick="w")

        auto_equip = CTkFrame(master=main_tab, fg_color=["gray81", "gray23"])
        auto_equip.grid(row=0, column=1, sticky="n", padx=(5, 0))
        auto_equip_title = CTkLabel(master=auto_equip, text="Auto Equip", font=("Segoe UI Semibold", 20, "bold")).grid(row=0, column=1)
        enable_auto_equip = CTkCheckBox(master=auto_equip, text="Enable Auto Equip", variable=self.tk_var_list['auto_equip']['enabled'], onvalue="1", offvalue="0").grid(row=2, column=1, padx=5, pady=5, stick="w")
        auto_equip_gui = CTkButton(master=auto_equip, text="Configure Search", width=255 , command=self.auto_equip_window).grid(column=1, row=3, padx=5, pady=5)

        item_collection_frame = CTkFrame(master=main_tab, fg_color=["gray81", "gray23"])
        item_collection_frame.grid(row=1, pady=(6, 0), sticky="we", columnspan=2, column=0, padx=(1, 0))
        item_collection_title = CTkLabel(master=item_collection_frame, text="Collect Items", font=("Segoe UI Semibold", 20, "bold")).grid(row=0, padx=5, columnspan=2)
        enable_collect_items = CTkCheckBox(master=item_collection_frame, text="Enable Item Collection", variable=self.tk_var_list['item_collecting']['enabled'], onvalue="1", offvalue="0").grid(row=0, sticky="w", padx=5, pady=5)
        
        spot_collection_frame = CTkFrame(master=item_collection_frame, fg_color=["gray65", "gray28"])
        spot_collection_frame.grid(row=1, sticky="w", column=1, padx=(64, 1), pady=(5, 7), ipady=5, ipadx=1)

        CTkCheckBox(master=spot_collection_frame, text="1", width=45, variable=self.tk_var_list['item_collecting']['spot1'], onvalue='1', offvalue='0').grid(row=1, column=0, sticky='e', padx=(5, 0))
        for i in range(1, 8):
            exec(f"CTkCheckBox(master=spot_collection_frame, text='{i + 1}', width=45, variable=self.tk_var_list['item_collecting']['spot{i + 1}'], onvalue='1', offvalue='0').grid(row=1, column={i}, sticky='e')")

        assign_clicks = CTkButton(master=item_collection_frame, text="Assign Clicks", command=self.assign_clicks_gui).grid(row=1, sticky="w", padx=5, pady=5)

    def auto_equip_window(self):
        self.auto_equip_window = CTkToplevel()
        self.auto_equip_window.title("Auto Equip")
        self.auto_equip_window.geometry("300x170")
        CTkLabel(master=self.auto_equip_window, text="Enter aura name to be used for search.\nThe first result will be equipped so be specific.").grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        aura_entry = CTkEntry(master=self.auto_equip_window, textvariable=self.tk_var_list['auto_equip']['aura'])
        aura_entry.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        special_checkbox = CTkCheckBox(master=self.auto_equip_window, text="Search in Special Auras", variable=self.tk_var_list['auto_equip']['special_aura'], onvalue="1", offvalue="0")
        special_checkbox.grid()

        # submit 
        submit_button = CTkButton(master=self.auto_equip_window, text="Submit", command=lambda: self.submit())
        submit_button.grid(pady=5)

    def submit(self):
        config.save_tk_list(self.tk_var_list)
        config.save_config(config.config_data)

    def assign_clicks_gui(self):
        self.click_window = CTkToplevel()
        self.click_window.title("Assign Menu")
        self.click_window.geometry("400x300")
        label = CTkLabel(master=self.click_window, text="Assign Your Clicks!").grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        
    def check_for_updates(self):
        # Took from my fisch macro (sapphire)
        pass

    def start(self):
        config.save_tk_list(self.tk_var_list)
        config.save_config(config.config_data)
    
    def stop(self):
        pass

    def restart(self):
        os.execv(sys.executable, ['python', f'"{sys.argv[0]}"'])

    # Took From Noteab Biome Macro 1.5.4 patch2.3 or sm like that

    def start_snip(self):
        self.snipping_window = ttk.Toplevel(self.root)
        self.snipping_window.attributes('-fullscreen', True)
        self.snipping_window.attributes('-alpha', 0.3)
        self.snipping_window.configure(bg="lightblue")
        
        self.snipping_window.bind("<Button-1>", self.on_mouse_press)
        self.snipping_window.bind("<B1-Motion>", self.on_mouse_drag)
        self.snipping_window.bind("<ButtonRelease-1>", self.on_mouse_release)

        self.canvas = ttk.Canvas(self.snipping_window, bg="lightblue", highlightthickness=0)
        self.canvas.pack(fill=ttk.BOTH, expand=True)

    def on_mouse_press(self, event):
        self.begin_x = event.x
        self.begin_y = event.y
        self.canvas.delete("selection_rect")

    def on_mouse_drag(self, event):
        self.end_x, self.end_y = event.x, event.y
        self.canvas.delete("selection_rect")
        self.canvas.create_rectangle(self.begin_x, self.begin_y, self.end_x, self.end_y,
                                      outline="white", width=2, tag="selection_rect")

    def on_mouse_release(self, event):
        self.end_x = event.x
        self.end_y = event.y

        x1, y1 = min(self.begin_x, self.end_x), min(self.begin_y, self.end_y)
        x2, y2 = max(self.begin_x, self.end_x), max(self.begin_y, self.end_y)

        self.capture_region(x1, y1, x2, y2)
        self.snipping_window.destroy()

    def capture_region(self, x1, y1, x2, y2):
        if self.config_key:
            region = [x1, y1, x2 - x1, y2 - y1]
            print(f"Region for '{self.config_key}' set to {region}")
            
            if self.callback:
                self.callback(region)