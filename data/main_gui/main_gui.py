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
    def __init__(self):
        super().__init__()
        self.title(f"Golden's Sol's Macro v{VERSION}")
        self.geometry("630x315x200x200")
        self.resizable(False, False) # change back to false false when finished bugfixing
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0) # ensures start/stop frame is on bottom of window

        self.tab_control = CTkTabview(master=self, fg_color=["gray86", "gray17"], height=265, corner_radius=10, border_width=2)
        main_tab = self.tab_control.add("Main")
        discord_tab = self.tab_control.add("Discord")
        crafting_tab = self.tab_control.add("Crafting")
        settings_tab = self.tab_control.add("Settings")
        credits_tab = self.tab_control.add("Credits")

        self.discord_tab_control = CTkTabview(master=discord_tab, fg_color=["gray86", "gray17"], height=100, corner_radius=10, border_width=2)
        webhook_subtab = self.discord_tab_control.add("Webhook")
        bot_subtab = self.discord_tab_control.add("Bot")
        self.discord_tab_control.grid(row=0, column=0, sticky="n", padx=10, pady=(5, 10))

        self.tab_control.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        #self.tab_control.set("Credits")
        self.tk_var_list = config.generate_tk_list()

        for button in self.tab_control._segmented_button._buttons_dict.values():
            button.configure(width=1000, height=35, corner_radius=10, border_width=2, font=("Segoe UI", 15, "bold"))
        
        buttons_frame = CTkFrame(master=self)
        buttons_frame.grid(row=1, pady=(5, 8), padx=6, sticky="sew")
        buttons_frame.grid_columnconfigure(0, weight=1)

        start_button = CTkButton(master=buttons_frame, text="Start - F1", command=self.start, height=30, width=100)#, corner_radius=10, border_width=2)
        start_button.grid(row=0, column=0, padx=4, pady=4, sticky="e")

        stop_button = CTkButton(master=buttons_frame, text="Stop - F2", command=self.stop, height=30, width=100)#, corner_radius=10, border_width=2)
        stop_button.grid(row=0, column=1, padx=4, pady=4, sticky="w")
        
        # TODO
        keyboard.add_hotkey("F1", self.start)
        keyboard.add_hotkey("F2", self.stop)
        keyboard.add_hotkey("F3", self.restart)



        # Main Tab

        random_frame = CTkFrame(master=main_tab, fg_color=["gray81", "gray23"])
        random_frame.grid(row=0, column=0, sticky="n", padx=(1, 1))
        miscellaneous_title = CTkLabel(master=random_frame, text="Miscellaneous", font=("Segoe UI Semibold", 20, "bold")).grid(row=0, column=1)

        obby = CTkCheckBox(master=random_frame, text="Obby (30% Luck Boost Every loop or 4 Mins)", variable=self.tk_var_list['obby']['enabled'], onvalue="1", offvalue="0").grid(row=2, column=1, padx=5, pady=5, stick="w")
        chalice = CTkCheckBox(master=random_frame, text="Auto Chalice (Collected Biomes Items 30% Luck)", variable=self.tk_var_list['chalice']['enabled'], onvalue="1", offvalue="0").grid(row=3, column=1, padx=5, pady=5, stick="w")

        auto_equip = CTkFrame(master=main_tab, fg_color=["gray81", "gray23"])
        auto_equip.grid(row=0, column=1, sticky="n", padx=(5, 0))
        auto_equip_title = CTkLabel(master=auto_equip, text="Auto Equip", font=("Segoe UI Semibold", 20, "bold")).grid(row=0, column=1)
        enable_auto_equip = CTkCheckBox(master=auto_equip, text="Enable Auto Equip", variable=self.tk_var_list['auto_equip']['enabled'], onvalue="1", offvalue="0").grid(row=2, column=1, padx=5, pady=5, stick="w")
        auto_equip_gui = CTkButton(master=auto_equip, text="Configure Search", width=255 , command=self.auto_equip_window).grid(column=1, row=3, padx=5, pady=5)

        item_collection_frame = CTkFrame(master=main_tab, fg_color=["gray81", "gray23"])
        item_collection_frame.grid(row=1, pady=(6, 0), sticky="we", columnspan=2, column=0, padx=(1, 0))
        item_collection_title = CTkLabel(master=item_collection_frame, text="Collect Items", font=("Segoe UI Semibold", 20, "bold")).grid(row=0, padx=5, pady=5, columnspan=2)
        enable_collect_items = CTkCheckBox(master=item_collection_frame, text="Enable Item Collection", variable=self.tk_var_list['item_collecting']['enabled'], onvalue="1", offvalue="0").grid(row=0, sticky="w", padx=5, pady=5)
        
        spot_collection_frame = CTkFrame(master=item_collection_frame, fg_color=["gray65", "gray28"])
        spot_collection_frame.grid(row=1, sticky="w", column=1, padx=(64, 1), pady=(5, 7), ipady=5, ipadx=1)

        CTkCheckBox(master=spot_collection_frame, text="1", width=45, variable=self.tk_var_list['item_collecting']['spot1'], onvalue='1', offvalue='0').grid(row=1, column=0, sticky='e', padx=(5, 0))
        for i in range(1, 8):
            exec(f"CTkCheckBox(master=spot_collection_frame, text='{i + 1}', width=45, variable=self.tk_var_list['item_collecting']['spot{i + 1}'], onvalue='1', offvalue='0').grid(row=1, column={i}, sticky='e')")

        assign_clicks = CTkButton(master=item_collection_frame, text="Assign Clicks", command=self.assign_clicks_gui).grid(row=1, sticky="w", padx=5, pady=5)



        # Discord Tab

        # Webhook Frame

        webhook_frame = CTkFrame(master=webhook_subtab, fg_color=["gray81", "gray23"])
        webhook_frame.grid(row=0, column=0, sticky="news", padx=5, pady=5)
        
        webhook_title = CTkLabel(master=webhook_frame, text="Webhook", font=("Segoe UI Semibold", 20, "bold"))
        webhook_title.grid(row=0, column=0, padx=5, pady=5)
        
        webhook_enable = CTkCheckBox(master=webhook_frame, text="Enable Webhook", 
            variable=self.tk_var_list['discord']['webhook']['enabled'],
            onvalue="1", offvalue="0")
        webhook_enable.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        webhook_url = CTkEntry(master=webhook_frame, width=250,
            textvariable=self.tk_var_list['discord']['webhook']['url'],
            placeholder_text="Webhook URL")
        webhook_url.grid(row=2, column=1, padx=5, pady=2)
        
        ping_id = CTkEntry(master=webhook_frame, width=250,
            textvariable=self.tk_var_list['discord']['webhook']['ping_id'],
            placeholder_text="User/Role ID to ping")
        ping_id.grid(row=4, column=1, padx=5, pady=2)
        
        # Bot Frame

        bot_frame = CTkFrame(master=bot_subtab, fg_color=["gray81", "gray23"])
        bot_frame.grid(row=0, column=0, sticky="news", padx=5, pady=5)
        
        bot_title = CTkLabel(master=bot_frame, text="Bot", font=("Segoe UI Semibold", 20, "bold"))
        bot_title.grid(row=0, column=0, padx=5, pady=5)
        
        bot_enable = CTkCheckBox(master=bot_frame, text="Enable Bot",
            variable=self.tk_var_list['discord']['bot']['enabled'],
            onvalue="1", offvalue="0")
        bot_enable.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        webhook_url_label = CTkLabel(master=webhook_frame, text="Webhook URL")
        webhook_url_label.grid(row=2, column=0, padx=5, pady=2, sticky="w")

        ping_id_label = CTkLabel(master=webhook_frame, text="User/Role ID to ping")
        ping_id_label.grid(row=4, column=0, padx=5, pady=2, sticky="w")

        bot_token_label = CTkLabel(master=bot_frame, text="Bot Token")
        bot_token_label.grid(row=2, column=0, padx=5, pady=2, sticky="w")

        channel_id_label = CTkLabel(master=bot_frame, text="Channel ID")
        channel_id_label.grid(row=3, column=0, padx=5, pady=2, sticky="w")
        
        bot_token = CTkEntry(master=bot_frame, width=250,
            textvariable=self.tk_var_list['discord']['bot']['token'],
            placeholder_text="Bot Token")
        bot_token.grid(row=2, column=1, padx=5, pady=2)
        
        channel_id = CTkEntry(master=bot_frame, width=250,
            textvariable=self.tk_var_list['discord']['bot']['channel_id'],
            placeholder_text="Channel ID")
        channel_id.grid(row=3, column=1, padx=5, pady=2)

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
        self.auto_equip_window.destroy()

    def assign_clicks_gui(self):
        self.click_window = CTkToplevel()
        self.click_window.title("Assign Menu")
        self.click_window.geometry("400x300")
        label = CTkLabel(master=self.click_window, text="Assign Your Clicks!").grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        button_pos = CTkButton(master=self.click_window, text="pOS", command=self.start_snip).grid()
    
    def start(self):
        config.save_tk_list(self.tk_var_list)
        config.save_config(config.config_data)
    
    def stop(self):
        pass

    def restart(self):
        os.execv(sys.executable, ['python', f'"{sys.argv[0]}"'])
