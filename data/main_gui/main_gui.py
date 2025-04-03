from customtkinter import *
import ctypes
from pynput.mouse import Button, Controller
import threading
import webbrowser
import keyboard
import json
from tkinter import messagebox
import requests
from data.main_loop.main_loop import MainLoop
try:
    from data.lib import config
except ImportError:
    ctypes.windll.user32.MessageBoxW(0, "Cant Open 'main_gui.py',\nPlease Use the Proper File", "Error", 0)
from time import sleep 
from ahk import AHK 
from PIL import ImageGrab, Image, ImageTk

ahk = AHK()
deactivate_automatic_dpi_awareness()

VERSION = config.get_current_version()
DEFAULT_FONT_BOLD = "Segoe UI Semibold"
class MainWindow(CTk):
    def __init__(self, config_key=None):
        super().__init__()
        self.bind_all("<Button-1>", self.focus_widget)
        self.title(f"Golden's Sol's Macro v{VERSION}")
        self.wm_protocol("WM_DELETE_WINDOW", self.save)
        self.iconpath = ImageTk.PhotoImage(file=f"{config.parent_path()}\\data\\images\\golden_pfp.ico")
        self.wm_iconbitmap()
        self.iconphoto(True, self.iconpath)

        self.geometry("630x315x200x200")
        self.resizable(False, False) # change back to false false when finished bugfixing
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0) # ensures start/stop frame is on bottom of window
        h1 = ("Segoe UI Semibold", 20, "bold")
        self.coord_vars = {}
        self.config_key = config_key
        self.begin_x = None
        self.begin_y = None
        self.end_x = None
        self.end_y = None 
        self.biome = self.get_biomes()
        self.biome_alerts = self.biome.get("biome_alerts", {})
        self.main_loop = MainLoop()
        self.config = config.read_config()

        set_default_color_theme(config.theme_path())
        self.configure(fg_color=config.read_theme("CTk")["fg_color"])

        self.tab_control = CTkTabview(master=self, height=265, fg_color=config.read_theme("CTkTabview")["fg_color"])
        main_tab = self.tab_control.add("Main")
        discord_tab = self.tab_control.add("Discord")
        crafting_tab = self.tab_control.add("Crafting")
        merchant_tab = self.tab_control.add("Merchant")
        settings_tab = self.tab_control.add("Settings")
        extras_tab = self.tab_control.add("Extras")
        credits_tab = self.tab_control.add("Credits")
        self.check_for_updates()
        self.discord_tab_control = CTkTabview(master=discord_tab, height=100, corner_radius=10, border_width=2)
        webhook_subtab = self.discord_tab_control.add("Webhook")
        bot_subtab = self.discord_tab_control.add("Bot")
        self.discord_tab_control.grid(row=0, column=0, sticky="n", padx=10, pady=(5, 10))
        
        self.tab_control.grid(padx=10)
        self.tab_control.set("Credits")
        self.tk_var_list = config.generate_tk_list()

        for button in self.tab_control._segmented_button._buttons_dict.values():
            button.configure(width=1000, height=35, corner_radius=10, border_width=2, font=CTkFont(DEFAULT_FONT_BOLD, size=15, weight="bold"))
        
        buttons_frame = CTkFrame(master=self)
        buttons_frame.grid(row=1, pady=(5, 8), padx=6, sticky="s")

        start_button = CTkButton(master=buttons_frame, text="Start - F1", command=self.start, height=30, width=100, corner_radius=4)#, corner_radius=10, border_width=2)
        start_button.grid(row=0, column=0, padx=4, pady=4)

        stop_button = CTkButton(master=buttons_frame, text="Stop - F2", command=self.stop, height=30, width=100, corner_radius=4)#, corner_radius=10, border_width=2)
        stop_button.grid(row=0, column=1, padx=4, pady=4)

        restart_button = CTkButton(master=buttons_frame, text="Restart - F3", command=self.restart, height=30, width=100, corner_radius=4)#, corner_radius=10, border_width=2)
        restart_button.grid(row=0, column=2, padx=4, pady=4)
        
        # TODO
        keyboard.add_hotkey("F1", self.start)
        keyboard.add_hotkey("F2", self.stop)
        keyboard.add_hotkey("F3", self.restart)
        keyboard.add_hotkey("F4", self.save)

        random_frame = CTkFrame(master=main_tab)
        random_frame.grid(row=0, column=0, sticky="n", padx=(1, 1))
        miscalance_title = CTkLabel(master=random_frame, text="Miscalances", font=("Segoe UI Semibold", 20, "bold")).grid(row=0, column=1)

        obby = CTkCheckBox(state="disabled", master=random_frame, text="Do Obby (30% Luck Boost Every 2 Mins)", variable=self.tk_var_list['obby']['enabled'], onvalue="1", offvalue="0").grid(row=2, column=1, padx=5, pady=5, stick="w")
        chalice = CTkCheckBox(state="disabled", master=random_frame, text="Auto Chalice", variable=self.tk_var_list['chalice']['enabled'], onvalue="1", offvalue="0").grid(row=3, column=1, padx=5, pady=5, stick="w")

        auto_equip = CTkFrame(master=main_tab)
        auto_equip.grid(row=0, column=1, sticky="n", padx=(5, 0))
        auto_equip_title = CTkLabel(master=auto_equip, text="Auto Equip", font=("Segoe UI Semibold", 20, "bold")).grid(row=0, column=1)
        enable_auto_equip = CTkCheckBox(master=auto_equip, text="Enable Auto Equip", variable=self.tk_var_list['auto_equip']['enabled'], onvalue="1", offvalue="0").grid(row=2, column=1, padx=5, pady=5, stick="w")
        auto_equip_gui = CTkButton(master=auto_equip, text="Configure Search", width=330 , command=self.auto_equip_window).grid(column=1, row=3, padx=5, pady=5)

        item_collection_frame = CTkFrame(master=main_tab)
        item_collection_frame.grid(row=1, pady=(6, 0), sticky="we", columnspan=2, column=0, padx=(1, 0))
        item_collection_title = CTkLabel(master=item_collection_frame, text="Collect Items", font=("Segoe UI Semibold", 20, "bold")).grid(row=0, padx=5, columnspan=2)
        assign_frame = CTkFrame(master=main_tab)

        enable_collect_items = CTkCheckBox(master=item_collection_frame, text="Enable Item Collection", variable=self.tk_var_list['item_collecting']['enabled'], onvalue="1", offvalue="0").grid(row=0, sticky="w", padx=5, pady=5)
        
        spot_collection_frame = CTkFrame(master=item_collection_frame)
        #spot_title = CTkLabel(master=spot_collection_frame, text="Collect Spots From:", font=CTkFont(DEFAULT_FONT_BOLD, size=15, weight="bold")).grid(pady=5, padx=5)
        spot_collection_frame.grid(row=1, sticky="w", column=1, padx=(64, 1), pady=(5, 7), ipady=5, ipadx=1)

        CTkCheckBox(master=spot_collection_frame, text="1", width=45, variable=self.tk_var_list['item_collecting']['spot1'], onvalue='1', offvalue='0').grid(row=2, column=0, sticky='e', padx=(5, 0))
        for i in range(1, 8):
            exec(f"CTkCheckBox(master=spot_collection_frame, text='{i + 1}', width=45, variable=self.tk_var_list['item_collecting']['spot{i + 1}'], onvalue='1', offvalue='0').grid(row=2, column={i}, sticky='e')")

        assign_clicks = CTkButton(master=item_collection_frame, text="Assign Clicks", command=self.assign_clicks_gui).grid(row=1, sticky="w", padx=5, pady=5)

        webhook_frame = CTkFrame(master=webhook_subtab)
        webhook_frame.grid(row=0, column=0, sticky="news", padx=5, pady=5)
        
        webhook_title = CTkLabel(master=webhook_frame, text="Webhook", font=("Segoe UI Semibold", 20, "bold"))
        webhook_title.grid(row=0, column=0, padx=5, pady=5)
        
        webhook_enable = CTkCheckBox(master=webhook_frame, text="Enable Webhook", 
            variable=self.tk_var_list['discord']['webhook']['enabled'],
            onvalue="1", offvalue="0")
        webhook_enable.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        webhook_url = CTkEntry(master=webhook_frame, width=250,
            textvariable=self.tk_var_list['discord']['webhook']['url'],
            placeholder_text="Webhook URL",
            show='*')
        webhook_url.grid(row=2, column=1, padx=5, pady=2)
        
        ping_id = CTkEntry(master=webhook_frame, width=250,
            textvariable=self.tk_var_list['discord']['webhook']['ping_id'],
            placeholder_text="User/Role ID to ping",
            show='*')
        ping_id.grid(row=4, column=1, padx=5, pady=2)

        ps_link_entry = CTkEntry(master=webhook_frame, width=250,
            textvariable=self.tk_var_list['discord']['webhook']['ps_link'],
            placeholder_text="Private Server Link",
            show='*')
        ps_link_entry.grid(row=5, column=1, padx=5, pady=2)
        
        # Bot Frame

        bot_frame = CTkFrame(master=bot_subtab)
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

        ps_link = CTkLabel(master=webhook_frame, text="Private Server Link:")
        ps_link.grid(row=5, column=0, padx=5, pady=2, sticky="w")

        bot_token_label = CTkLabel(master=bot_frame, text="Bot Token")
        bot_token_label.grid(row=2, column=0, padx=5, pady=2, sticky="w")

        channel_id_label = CTkLabel(master=bot_frame, text="Channel ID")
        channel_id_label.grid(row=3, column=0, padx=5, pady=2, sticky="w")
        
        bot_token = CTkEntry(master=bot_frame, width=250,
            textvariable=self.tk_var_list['discord']['bot']['token'],
            placeholder_text="Bot Token",
            show='*')
        bot_token.grid(row=2, column=1, padx=5, pady=2)
        
        channel_id = CTkEntry(master=bot_frame, width=250,
            textvariable=self.tk_var_list['discord']['bot']['channel_id'],
            placeholder_text="Channel ID",
            show='*')
        channel_id.grid(row=3, column=1, padx=5, pady=2)

        crafting_frame = CTkFrame(master=crafting_tab)
        crafting_frame.grid(row=0, column=0, sticky="n", padx=(1, 1))
        crafting_title = CTkLabel(master=crafting_frame, text="Crafting", font=h1).grid(row=0, column=1, columnspan=2)
        crafting_enabled = CTkCheckBox(state="disabled", master=crafting_frame, text="Enable Potion Crafting", variable=self.tk_var_list['potion_crafting']['enabled'], onvalue="1", offvalue="0").grid(row=2, column=1, padx=5, pady=5, stick="w")
        list = ['None', 'Fortune I', 'Fortune II', 'Fortune III', 'Speed Potion I', 'Speed Potion II', 'Speed Potion III', 'Lucky Potion I', 'Lucky Potion II', 'Lucky Potion III', 'Heavenly I', 'Heavenly II', 'Warp Potion']
        option1 = CTkOptionMenu(state="disabled", master=crafting_frame, values=list, variable=self.tk_var_list['potion_crafting']['item_1']).grid(row=3, column=1, padx=5, pady=5, stick="w")
        option2 = CTkOptionMenu(state="disabled", master=crafting_frame, values=list, variable=self.tk_var_list['potion_crafting']['item_2']).grid(row=4, column=1, padx=5, pady=5, stick="w")
        option3 = CTkOptionMenu(state="disabled", master=crafting_frame, values=list, variable=self.tk_var_list['potion_crafting']['item_3']).grid(row=5, column=1, padx=5, pady=5, stick="w")
        auto_add = CTkSwitch(state="disabled", master=crafting_frame, text="Auto Add Swicher", variable=self.tk_var_list['potion_crafting']['temporary_auto_add'], onvalue="1", offvalue="0").grid(row=2, column=2, padx=5, pady=5, stick="w")
        crafting_clicks = CTkButton(master=crafting_frame, text="Assign Crafting", command=self.crafting_clicks).grid(row=5, column=2, padx=5, pady=5, stick="w")

        mari_frame = CTkFrame(master=merchant_tab)
        mari_frame.grid(row=0, column=0, sticky="n", padx=(1, 1))

        mari_title = CTkLabel(master=mari_frame, text="Mari Settings", font=h1).grid(row=1, column=1)
        mari_checkbox = CTkCheckBox(state="disabled", master=mari_frame, text="Enable Mari", variable=self.tk_var_list['merchant_items']['enabled'], onvalue="1", offvalue="0").grid(row=2, column=1, padx=5, pady=5, stick="w")
        open_mari_gui = CTkButton(state="disabled", master=mari_frame, text="Open Mari Settings", width=290, command=self.open_mari_settings).grid(row=3, column=1, padx=5, pady=5, stick="w")
        merchant_calibration_button = CTkButton(state="disabled", master=mari_frame, text="Mari Calibration", command=self.merchant_calibrations).grid(row=4, column=1, padx=5, pady=5, stick="w")
        ping_if_mari = CTkCheckBox(state="disabled", master=mari_frame, text="Ping if Mari?", variable=self.tk_var_list['merchant_items']['ping_if_mari'], onvalue="1", offvalue="0").grid(row=5, column=1, padx=5, pady=5, stick="w")
        mari_id = CTkEntry(state="disabled", master=mari_frame, textvariable=self.tk_var_list['merchant_items']['mari_id'], width=60).grid(row=6, column=1, padx=5, pady=5, stick="w")

        jester_frame = CTkFrame(master=merchant_tab)
        jester_frame.grid(row=0, column=1, sticky="n", padx=(5, 0))
        jester_title = CTkLabel(master=jester_frame, text="Jester Settings", font=h1).grid(row=0, column=1)
        jester_checbox = CTkCheckBox(state="disabled", master=jester_frame, text="Enable Jester", variable=self.tk_var_list['jester_items']['enable'], onvalue="1", offvalue="0").grid(row=2, column=1, padx=5, pady=5, stick="w")
        use_mc = CTkCheckBox(state="disabled", master=jester_frame, text="Use Merchant Teleporter", variable=self.tk_var_list['use_mc_teleporter'], onvalue="1", offvalue="0").grid(row=3, column=1, padx=5, pady=5, stick="w")
        open_jester_gui = CTkButton(state="disabled", master=jester_frame, text="Open Jester Settings", width=280, command=self.open_jester_settings).grid(row=4, column=1, padx=5, pady=5, stick="w")
        ping_if_jester = CTkCheckBox(state="disabled", master=jester_frame, text="Ping if Jester", variable=self.tk_var_list['jester_items']['ping_if_jester'], onvalue="1", offvalue="0").grid(row=5, column=1, padx=5, pady=5, stick="w")
        jester_id = CTkEntry(state="disabled", master=jester_frame, textvariable=self.tk_var_list['jester_items']['jester_id'], width=60).grid(row=6, column=1, padx=5, pady=5, stick="w")

        settings_frame = CTkFrame(master=settings_tab)
        settings_frame.grid(row=0, column=0, sticky="n", padx=(1, 1))
        settings_title = CTkLabel(master=settings_frame, text="General", font=h1).grid(row=0, column=1, columnspan=2)

        vip_settings = CTkCheckBox(master=settings_frame, text="VIP Game Pass", variable=self.tk_var_list['settings']['vip_mode'], onvalue="1", offvalue="0").grid(row=2, column=1, padx=5, pady=5, stick="w")
        vip_mode = CTkCheckBox(master=settings_frame, text="VIP+ Mode", variable=self.tk_var_list['settings']['vip+_mode'], onvalue="1", offvalue="0").grid(row=3, column=1, padx=5, pady=5, stick="w")
        azerty_layout = CTkCheckBox(master=settings_frame, text="Azerty Keyboard Layout", variable=self.tk_var_list['settings']['azerty_mode'], onvalue="1", offvalue="0").grid(row=4, column=1, padx=5, pady=5, stick="w")
        claim_quests = CTkCheckBox(master=settings_frame, text="Important webhook only", variable=self.tk_var_list['important_only'], onvalue="1", offvalue="0").grid(row=2, column=2, padx=5, pady=5, stick="w")
        auto_reconnect = CTkCheckBox(state="disabled", master=settings_frame, text="Auto Reconnect (BETA)", variable=self.tk_var_list['reconnect'], onvalue="True", offvalue="False").grid(row=3, column=2, padx=5, pady=5, stick="w")

        aura_settings = CTkFrame(master=settings_tab)
        aura_settings.grid(row=0, column=1, sticky="n", padx=(5, 0))
        aura_title = CTkLabel(master=aura_settings, text="Aura Detection", font=h1).grid(row=0, column=1, columnspan=2)
        enable_dectection = CTkCheckBox(master=aura_settings, text="Enable Aura Dectection", variable=self.tk_var_list['enabled_dectection'], onvalue="1", offvalue="0").grid(row=2, column=1, padx=5, pady=5, stick="w")
        pings_aura = CTkLabel(master=aura_settings, text="Send Min:", justify="left").grid(row=3, column=1, padx=5, pady=5, stick="w")
        min_entry = CTkEntry(master=aura_settings, textvariable=self.tk_var_list['send_min'], width=80).grid(row=3, column=2, padx=5, pady=5, stick="w")
        pings_max = CTkLabel(master=aura_settings, text="Send Max:", justify="left").grid(row=4, column=1, padx=5, pady=5, stick="w")
        max_entry = CTkEntry(master=aura_settings, textvariable=self.tk_var_list['send_max'], width=80).grid(row=4, column=2, padx=5, pady=5, stick="w")

        items_stuff = CTkFrame(master=extras_tab)
        items_stuff.grid(row=0, column=0, stick="n", padx=(5, 0))
        items_title = CTkLabel(master=items_stuff, text="Item Scheduler", font=h1).grid(row=0, padx=5)
        enable_items = CTkCheckBox(master=items_stuff, text="Enable Item Scheduler", variable=self.tk_var_list['enable_items'], onvalue="1", offvalue="0").grid(row=2, column=0, padx=5, pady=5, stick="w")
        scheduler_items = CTkOptionMenu(master=items_stuff, values=['None', 'Merchant Tracker', 'Fortune I', 'Fortune II', 'Fortune III', 'Speed Potion I', 'Speed Potion II', 'Speed Potion III', 'Lucky Potion I', 'Lucky Potion II', 'Lucky Potion III', 'Heavenly I', 'Heavenly II', 'Warp Potion'], width=230, variable=self.tk_var_list['item_scheduler_item']).grid(row=3, column=0, padx=5, pady=5, stick="w")
        quanity_label = CTkLabel(master=items_stuff, text="Quanity:").grid(row=4, column=0, padx=5, pady=2, stick="w")
        quanity = CTkEntry(master=items_stuff, width=80, textvariable=self.tk_var_list['item_scheduler_quantity']).grid(row=4, column=0, padx=5, pady=2)

        biome_config = CTkFrame(master=extras_tab)
        biome_config.grid(row=0, column=2, stick="n", padx=(5, 0))
        biome_title = CTkLabel(master=biome_config, text="Biome Settings", font=h1).grid(row=0, column=0)
        enable_biome = CTkCheckBox(master=biome_config, text="Enable Biome Detection", variable=self.tk_var_list['biome_detection']['enabled'], onvalue="1", offvalue="0").grid(row=2, column=0, padx=5, pady=5, stick="w")
        set_region = CTkButton(master=biome_config, text="Set Biome Region", command=self.set_biome_region).grid(row=3, column=0, padx=5, pady=5, stick="w")

        themes_frame = CTkFrame(master=extras_tab)
        themes_frame.grid(row=0, column=1, sticky="nw", padx=(5, 0))
        themes_ttle = CTkLabel(master=themes_frame, text="Themes", font=h1).grid(row=0, columnspan=2)


        themes = []
        for theme in config.config_data["themes"]:
            themes.append(theme)
        themes.append("Custom Theme")

        change_themes = CTkOptionMenu(master=themes_frame, values=themes, width=140, command=self.change_theme)
        change_themes.grid(row=2, padx=5, pady=5, sticky="w", columnspan=2)

        if not "/" in config.config_data["paths"]["theme"]:
            change_themes.set(config.config_data["paths"]["theme"])
        else:
            change_themes.set("Custom Theme")
        
        credits_frame = CTkScrollableFrame(master=credits_tab, width=570)
        credits_frame.grid(row=0, column=0, padx=(1, 0))    
        credits_title = CTkLabel(master=credits_frame, text="Credits Team", font=h1).grid(row=0, padx=5, columnspan=3)
    
        credits_text = f"""
Founders (Aurium):  
Golden | /x64/dumped

Developers:
vexthecoder

Special Thanks to:
Radiant Team, (Original source code/LPS)
Kat (@Rammstein), (made server logo)
Vex (@vex.rng), for greatly helping me with the detection

Current Macro Version : {VERSION}
"""
        team_logo_image = CTkImage(dark_image=config.round_corners(Image.open(f"{config.parent_path()}/data/images/golden_chill.png"), 35), size=(150, 150))
        credits_label = CTkLabel(master=credits_frame, text=credits_text).grid(row=1, column=1, rowspan=2, padx=56, pady=(17, 30), sticky="n")
        team_image_label = CTkLabel(master=credits_frame, image=team_logo_image, text="").grid(row=1, column=0, padx=6, pady=(0, 6))

    def auto_equip_window(self):
        self.auto_equip_window = CTkToplevel()
        self.auto_equip_window.title("Auto Equip")
        self.auto_equip_window.geometry("250x140")
        self.auto_equip_window.resizable(False, False)
        self.auto_equip_window.attributes("-topmost", True)
        set_default_color_theme(config.theme_path())
        self.configure(fg_color=config.read_theme("CTk")["fg_color"])
        frame = CTkFrame(master=self.auto_equip_window)
        frame.grid(row=0, column=0, sticky="n", padx=(1, 1))
        CTkLabel(master=frame, text="Enter aura name to be used for search.\nThe first result will be equipped so be specific.").grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        aura_entry = CTkEntry(master=frame, textvariable=self.tk_var_list['auto_equip']['aura'])
        aura_entry.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        special_checkbox = CTkCheckBox(master=frame, text="Search in Special Auras", variable=self.tk_var_list['auto_equip']['special_aura'], onvalue="1", offvalue="0")
        special_checkbox.grid()

        # submit 
        submit_button = CTkButton(master=frame, text="Submit", command=lambda: self.save_window_settings(self.auto_equip_window))
        submit_button.grid(pady=5)

    def change_theme(self, choice):
        if choice == "Custom Theme":
            self.iconify()
            filepath = filedialog.askopenfilename(initialdir = "/",
                title = "Choose a theme",
                filetypes = [("Json Theme File", "*.json*")]
            )
            config.config_data["paths"]["theme"] = filepath
            config.save_config(config.config_data)
        else:
            self.tk_var_list["paths"]["theme"] = choice
            config.save_tk_list(self.tk_var_list)

        self.restart()

    def start(self):
        config.save_tk_list(self.tk_var_list)
        config.save_config(config.config_data)
        self.iconify()
        self.main_loop.start()
    
    def stop(self):
        config.save_tk_list(self.tk_var_list)
        config.save_config(config.config_data)
        self.deiconify()
        self.main_loop.stop()
        self.lift()

    def restart(self):
        #self.stop()  # Stop before restart
        os.execv(sys.executable, ['python', f'"{sys.argv[0]}"'])

    def save(self):
        try:
            config.save_tk_list(self.tk_var_list)
            config.save_config(config.config_data)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
            self.destroy()

    def focus_widget(self, event):
        try:
            event.widget.focus_set()
        except:
            pass

    def assign_clicks_gui(self):
        self.assign_clicks_gui = CTkToplevel()
        self.assign_clicks_gui.title("Assign Clicks")
        #self.assign_clicks_gui.geometry("400x540")
        self.assign_clicks_gui.resizable(False, False)
        self.assign_clicks_gui.attributes("-topmost", True)
        
        # Create tabview
        tabview = CTkTabview(master=self.assign_clicks_gui)
        tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Configure grid weights
        self.assign_clicks_gui.grid_rowconfigure(0, weight=1)
        self.assign_clicks_gui.grid_columnconfigure(0, weight=1)

        # Create tabs
        aura_tab = tabview.add("Auras Storage")
        collection_tab = tabview.add("Collection Menu")
        items_tab = tabview.add("Items Menu")

        # Aura settings
        aura_settings = [
            ("Aura Storage:", "aura_storage"),
            ("Regular Aura Tab:", "regular_tab"),
            ("Special Aura Tab:", "special_tab"),
            ("Aura Search Bar:", "search_bar"),
            ("First Aura Slot:", "aura_first_slot"),
            ("Equip Button:", "equip_button")
        ]

        # Collection settings
        collection_settings = [
            ("Collection Menu:", "collection_menu"),
            ("Exit Collection:", "exit_collection")
        ]

        # Items settings
        items_settings = [
            ("Items Storage:", "items_storage"),
            ("Items Tab:", "items_tab"),
            ("Items Search Bar:", "items_bar"),
            ("Items First Slot:", "item_first_slot"),
            ("Quantity Bar:", "item_value"),
            ("Use Button:", "use_button")
        ]

        # Create frames for each tab
        aura_frame = CTkFrame(master=aura_tab)
        aura_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        aura_tab.grid_rowconfigure(0, weight=1)

        collection_frame = CTkFrame(master=collection_tab)
        collection_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        collection_tab.grid_rowconfigure(0, weight=1)

        items_frame = CTkFrame(master=items_tab)
        items_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        items_tab.grid_rowconfigure(0, weight=1)

        # Function to create entry fields and buttons
        def create_click_fields(parent, settings):
            for i, (label_text, config_key) in enumerate(settings):
                # Label
                CTkLabel(parent, text=label_text).grid(row=i, column=0, padx=5, pady=2, sticky="w")
                
                # X Entry
                x_entry = CTkEntry(parent, width=60, 
                    textvariable=self.tk_var_list['clicks'][config_key][0], 
                    placeholder_text="X")
                x_entry.grid(row=i, column=1, padx=5, pady=2)
                
                # Y Entry
                y_entry = CTkEntry(parent, width=60, 
                    textvariable=self.tk_var_list['clicks'][config_key][1], 
                    placeholder_text="Y")
                y_entry.grid(row=i, column=2, padx=5, pady=2)
                
                # Assign Button
                CTkButton(parent, text="Assign Click!", 
                    command=lambda k=config_key, x=x_entry, y=y_entry: 
                    self.start_capture_thread(k, x, y)).grid(row=i, column=3, padx=5, pady=2)

        CTkButton(master=aura_frame, text="Save Calibration", command=lambda: self.save_window_settings(self.assign_clicks_gui)).grid(row=7, column=1, padx=5, pady=2)
        # Create fields for each section
        create_click_fields(aura_frame, aura_settings)
        create_click_fields(collection_frame, collection_settings)
        create_click_fields(items_frame, items_settings)

    def crafting_clicks(self):
        self.crafting_clicks = CTkToplevel()
        self.crafting_clicks.title("Crafting")
        self.crafting_clicks.resizable(False, False)
        
        crafting_frame = CTkFrame(master=self.crafting_clicks)
        crafting_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure grid weights
        self.crafting_clicks.grid_rowconfigure(0, weight=1)
        self.crafting_clicks.grid_columnconfigure(0, weight=1)
        crafting_frame.grid_columnconfigure(1, weight=1)

        crafting_items = [
            ("Search Bar:", "potion_bar"),
            ("First Potion Slot:", "potion_first_slot"),
            ("Auto Add Button:", "auto_button"),
            ("Craft Button:", "craft_button"),
            ("1 Manual Potion:", "1_manual_potion"),
            ("2 Manual Potion:", "2_manual_potion"),
            ("3 Manual Potion:", "3_manual_potion"),
            ("4 Manual Potion:", "4_manual_potion"),
            ("5 Manual Potion:", "5_manual_potion"),
            ("6 Manual Potion (Warp Potion):", "6_manual_potion")
        ]
        
        for i, (text, config_key) in enumerate(crafting_items, start=1):
            # Label
            CTkLabel(crafting_frame, text=text).grid(row=i, column=0, padx=5, pady=2, sticky="w")
            
            # X Entry
            x_entry = CTkEntry(crafting_frame, textvariable=self.tk_var_list['clicks'][config_key][0], width=60)
            x_entry.grid(row=i, column=1, padx=5, pady=2)
            
            # Y Entry
            y_entry = CTkEntry(crafting_frame, textvariable=self.tk_var_list['clicks'][config_key][1], width=60)
            y_entry.grid(row=i, column=2, padx=5, pady=2)
            
            # Assign Button
            CTkButton(crafting_frame, text="Assign Click!", 
                command=lambda k=config_key, x=x_entry, y=y_entry: 
                self.start_capture_thread(k, x, y)).grid(row=i, column=3, padx=5, pady=2)
        
        # Save button at the bottom
        save_button = CTkButton(crafting_frame, text="Save Calibration", 
            command=lambda: self.save_window_settings(self.crafting_clicks))
        save_button.grid(row=len(crafting_items) + 1, column=0, columnspan=4, pady=10)

    def open_mari_settings(self):
        mari_window = CTkToplevel()
        mari_window.title("Mari Selection")
        mari_items = [
            "Void Coin", "Lucky Penny", "Mixed Potion", "Lucky Potion",
            "Lucky Potion L", "Lucky Potion XL", "Speed Potion",
            "Speed Potion L", "Speed Potion XL", "Gear A", "Gear B"
        ]
        frame = CTkFrame(mari_window)
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Configure grid weights
        mari_window.grid_rowconfigure(0, weight=1)
        mari_window.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        
        CTkLabel(frame, text="Item Name").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        CTkLabel(frame, text="Amount").grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Initialize merchant_items in tk_var_list if it doesn't exist
        if 'merchant_items' not in self.tk_var_list:
            self.tk_var_list['merchant_items'] = {}

        for i, item in enumerate(mari_items, start=1):
            # Initialize the StringVar for each item if it doesn't exist
            if item not in self.tk_var_list['merchant_items']:
                self.tk_var_list['merchant_items'][item] = StringVar(value="1")
            CTkCheckBox(master=frame, text=item, onvalue="1", offvalue="0").grid(row=i, column=0, sticky="w", padx=5, pady=2)
            CTkEntry(master=frame, textvariable=self.tk_var_list['merchant_items'][item]).grid(row=i, column=1, padx=5, pady=2, sticky="ew")
        
        save_settings = CTkButton(master=frame, text="Save Settings", command=lambda: self.save_window_settings(mari_window))
        save_settings.grid(row=len(mari_items) + 1, column=0, columnspan=2, pady=10)

    def open_jester_settings(self):
        jester_window = CTkToplevel()
        jester_window.title("Jester Selection")

        jester_items = [
            "Oblivion Potion", "Heavenly Potion", "Rune of Everything", "Rune of Dust",
            "Rune of Nothing", "Rune Of Corruption", "Rune Of Hell", "Rune of Galaxy",
            "Rune of Rainstorm", "Rune of Frost", "Rune of Wind", "Strange Potion", "Lucky Potion",
            "Stella's Candle", "Merchant Tracker", "Random Potion Sack"
        ]
        frame = CTkFrame(master=jester_window)
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Configure grid weights
        jester_window.grid_rowconfigure(0, weight=1)
        jester_window.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        CTkLabel(frame, text="Item Name").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        CTkLabel(frame, text="Amount").grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Initialize jester_items in tk_var_list if it doesn't exist
        if 'jester_items' not in self.tk_var_list:
            self.tk_var_list['jester_items'] = {}

        for i, item in enumerate(jester_items, start=1):
            # Initialize the StringVar for each item if it doesn't exist
            if item not in self.tk_var_list['jester_items']:
                self.tk_var_list['jester_items'][item] = StringVar(value="1")
            CTkCheckBox(master=frame, text=item, onvalue="1", offvalue="0").grid(row=i, column=0, sticky="w", padx=5, pady=2)
            CTkEntry(master=frame, textvariable=self.tk_var_list['jester_items'][item]).grid(row=i, column=1, padx=5, pady=2, sticky="ew")
        
        save_settings = CTkButton(master=frame, text="Save Settings", command=lambda: self.save_window_settings(jester_window))
        save_settings.grid(row=len(jester_items) + 1, column=0, columnspan=2, pady=10)
    
    def merchant_calibrations(self):
        merchant_window = CTkToplevel()
        merchant_window.title("Merchant Calibrations")
        merchant_window.resizable(False, False)
        merchant_window.attributes("-topmost", True)

        positions = [
            ("Merchant Open Button:", "merchant_open_button"),
            ("Merchant Dialoge Box:", "merchant_hold_button"),
            ("Merchant Amount Entry:", "merchant_amount_box"),
            ("Purchase Button:", "merchant_buy_button"),
            ("Merchant First Slot:", "merchant_slot_1"),
            ("Merchant Name OCR:", "merchant_name"),
            ("Merchant Item Name OCR:", "merchant_item_name"),
        ]
        if 'clicks' not in self.tk_var_list:
            self.tk_var_list['clicks'] = {}

        for i, (label_text, pos) in enumerate(positions, start=1):
            if "ocr" in label_text.lower():
                label = CTkLabel(master=merchant_window, text=f"{label_text} (X, Y, W, H)").grid(row=i, column=0, padx=5, pady=5, sticky="w")
                if pos not in self.tk_var_list['clicks']:
                    self.tk_var_list['clicks'][pos] = StringVar(value="1")
                # btw dont d0 'StringVar' it limits you with the variables
                x_entry = CTkEntry(master=merchant_window, textvariable=self.tk_var_list['clicks'][pos][0], width=60)
                x_entry.grid(row=i, column=1, padx=5, pady=5)
                y_entry = CTkEntry(master=merchant_window, textvariable=self.tk_var_list['clicks'][pos][1], width=60)
                y_entry.grid(row=i, column=2, padx=5, pady=5)
                w_entry = CTkEntry(master=merchant_window, textvariable=self.tk_var_list['clicks'][pos][2], width=60)
                w_entry.grid(row=i, column=3, padx=5, pady=5)
                h_entry = CTkEntry(master=merchant_window, textvariable=self.tk_var_list['clicks'][pos][3], width=60)
                h_entry.grid(row=i, column=4, padx=5, pady=5)

                select_button = CTkButton(master=merchant_window, text="Assign (X, Y, W, H)", 
                    command=lambda p=pos, x=x_entry, y=y_entry, w=w_entry, h=h_entry: 
                    self.start_capture_thread(p, x, y, w, h))
                select_button.grid(row=i, column=5, padx=5, pady=5)
            else:
                if pos not in self.tk_var_list['clicks']:
                    self.tk_var_list['clicks'][pos] = StringVar(value="1")
                label = CTkLabel(master=merchant_window, text=f"{label_text} (X, Y)").grid(row=i, column=0, padx=5, pady=5, sticky="w")
                
                x_entry = CTkEntry(master=merchant_window, textvariable=self.tk_var_list['clicks'][pos][0], width=60)
                x_entry.grid(row=i, column=1, padx=5, pady=5)
                y_entry = CTkEntry(master=merchant_window, textvariable=self.tk_var_list['clicks'][pos][1], width=60)
                y_entry.grid(row=i, column=2, padx=5, pady=5)
                
                select_button = CTkButton(master=merchant_window, text="Assign!", 
                    command=lambda p=pos, x=x_entry, y=y_entry: 
                    self.start_capture_thread(p, x, y))
                select_button.grid(row=i, column=5, padx=5, pady=5)
            
        save_button = CTkButton(merchant_window, text="Save Calibration", 
            command=lambda: self.save_window_settings(merchant_window))
        save_button.grid(row=8, column=0, columnspan=6, pady=10)


    def save_window_settings(self, window):
        config.save_tk_list(self.tk_var_list)
        window.destroy()

    def start_capture_thread(self, config_key, x_entry, y_entry, w_entry=None, h_entry=None):
        self.snipping_window = CTkToplevel()
        self.snipping_window.attributes("-fullscreen", True)
        self.snipping_window.attributes("-alpha", 0.3)
        self.snipping_window.config(cursor="cross")
        self.canvas = CTkCanvas(self.snipping_window, bg="lightblue", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Store the entry widgets and config key for later use
        self.x_entry = x_entry
        self.y_entry = y_entry
        self.w_entry = w_entry
        self.h_entry = h_entry
        self.config_key = config_key

        self.snipping_window.bind("<Button-1>", self.on_click)
        self.snipping_window.bind("<B1-Motion>", self.mouse_drag)
        self.snipping_window.bind("<ButtonRelease-1>", self.mouse_release)
        
        # Add window close handler
        self.snipping_window.protocol("WM_DELETE_WINDOW", self.on_window_close)

    def on_window_close(self):
        """Handle window closing"""
        if hasattr(self, 'snipping_window'):
            self.snipping_window.destroy()

    def on_click(self, event):
        try:
            self.begin_x = event.x
            self.begin_y = event.y
            
            if hasattr(self, 'canvas'):
                self.canvas.delete("selection_rect")
        except Exception as e:
            print(f"Error in on_click: {e}")

    def mouse_drag(self, event):
        try:
            self.end_x = event.x
            self.end_y = event.y
            
            # Calculate width and height from coordinates
            width = abs(self.end_x - self.begin_x)
            height = abs(self.end_y - self.begin_y)
            
            # Update the canvas with the current selection rectangle
            if hasattr(self, 'canvas'):
                self.canvas.delete("selection_rect")
                self.canvas.create_rectangle(self.begin_x, self.begin_y, self.end_x, self.end_y,
                                          outline="black", width=2, tag="selection_rect")
            
            # Update the entry widgets with the current coordinates
            if hasattr(self, 'x_entry') and self.x_entry.winfo_exists():
                self.x_entry.delete(0, 'end')
                self.x_entry.insert(0, str(min(self.begin_x, self.end_x)))
            
            if hasattr(self, 'y_entry') and self.y_entry.winfo_exists():
                self.y_entry.delete(0, 'end')
                self.y_entry.insert(0, str(min(self.begin_y, self.end_y)))
            
            if hasattr(self, 'w_entry') and self.w_entry.winfo_exists():
                self.w_entry.delete(0, 'end')
                self.w_entry.insert(0, str(width))
            
            if hasattr(self, 'h_entry') and self.h_entry.winfo_exists():
                self.h_entry.delete(0, 'end')
                self.h_entry.insert(0, str(height))

        except Exception as e:
            print(f"Error in mouse_drag: {e}")

    def mouse_release(self, event):
        try:
            self.end_x = event.x
            self.end_y = event.y
            
            # Calculate width and height from coordinates
            width = abs(self.end_x - self.begin_x)
            height = abs(self.end_y - self.begin_y)
            
            # Update the entry widgets with the final coordinates
            if hasattr(self, 'x_entry') and self.x_entry.winfo_exists():
                self.x_entry.delete(0, 'end')
                self.x_entry.insert(0, str(min(self.begin_x, self.end_x)))
            
            if hasattr(self, 'y_entry') and self.y_entry.winfo_exists():
                self.y_entry.delete(0, 'end')
                self.y_entry.insert(0, str(min(self.begin_y, self.end_y)))
            
            if hasattr(self, 'w_entry') and self.w_entry.winfo_exists():
                self.w_entry.delete(0, 'end')
                self.w_entry.insert(0, str(width))
            
            if hasattr(self, 'h_entry') and self.h_entry.winfo_exists():
                self.h_entry.delete(0, 'end')
                self.h_entry.insert(0, str(height))
            
            # Update the config with new coordinates
            if hasattr(self, 'config_key'):
                config_key = self.config_key.lower().replace('x', '').replace('y', '').replace('w', '').replace('h', '')
                config.config_data['clicks'][config_key] = [min(self.begin_x, self.end_x), min(self.begin_y, self.end_y), width, height]
                config.save_config(config.config_data)
            
            # Close the snipping window
            if hasattr(self, 'snipping_window'):
                self.snipping_window.destroy()
        except Exception as e:
            print(f"Error in on_mouse_release: {e}")
            if hasattr(self, 'snipping_window'):
                self.snipping_window.destroy()
        
    def set_biome_region(self):
        self.biome_window = CTkToplevel()
        self.biome_window.title("Select Biomes")
        self.biome_window.resizable(False, False)
        self.biome_window.attributes("-topmost", True)
    
        biomes = [
            ("Normal", "NORMAL"),
            ("Windy", "WINDY"), ("Rainy", "RAINY") ,
            ("Snowy", "SNOWY"), ("Hell", "HELL"),
            ("Starfall", "STARFALL"), ("Null", "NULL"),
            ("Sandstorm", "SAND STORM"), ("Corruption", "CORRUPTION")
        ]

        # Initialize biome variables if they don't exist
        if not hasattr(self, 'biome_vars'):
            self.biome_vars = {}
            for biome_name, _ in biomes:
                self.biome_vars[biome_name] = StringVar(value="1")

        for i, (biome_name, _) in enumerate(biomes):
            CTkCheckBox(master=self.biome_window, text=biome_name, 
                       variable=self.biome_vars[biome_name],
                       command=self.save_biomes, 
                       onvalue="1", offvalue="0").grid(row=i, column=0, padx=5, pady=5, sticky="w")

        # Add save button
        save_button = CTkButton(master=self.biome_window, text="Save Settings", 
                              command=lambda: self.save_window_settings(self.biome_window))
        save_button.grid(row=len(biomes), column=0, pady=10)

    def save_biomes(self):
        # Update biome_alerts with current checkbox values
        for biome_name, var in self.biome_vars.items():
            self.biome_alerts[biome_name] = var.get() == "1"
        
        # Save to settings.cfg
        try:
            with open("settings.cfg", 'w') as file:
                json.dump({"biome_alerts": self.biome_alerts}, file)
        except Exception as e:
            print(f"Failed to save biome settings: {str(e)}")

    def check_for_updates(self):
        current_version = config.get_current_version()
        try:
            response = requests.get('https://api.github.com/repos/Goldfish-cool/Goldens-Macro/releases')
            response.raise_for_status()
            latest_releases = response.json()
            if latest_releases:
                latest_release = latest_releases[0]
                latest_version = latest_release['tag_name']
                if latest_version != current_version:
                    update_response = messagebox.askyesno("New Update!", f"New Version of the macro v{latest_version}, Would you like to update?")
                    if update_response:
                        webbrowser.open("https://github.com/Goldfish-cool/Goldens-Macro/releases/latest")
                else:
                    pass
                    #messagebox.showinfo("No Update Available", "You are running the latest version of this macro.")
            else:
                pass
                #messagebox.showinfo("No Update Available", "No releases found for this macro.")
        except Exception as e:
            messagebox.showerror("Update Check Error", f"Failed to check for updates: {e}")
            
    def get_biomes(self):
        try:
            with open("settings.cfg", 'r') as file:
                config = json.load(file)
            return {}
        except ValueError as e:
            print(f"Failed to get settings.cfg: {str(e)}")
        
    
