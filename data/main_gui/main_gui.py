from customtkinter import *
import ctypes
from pynput.mouse import Button, Controller
import threading
import webbrowser
import keyboard
import subprocess
from tkinter import messagebox
import requests
from data.main_loop import main_loop
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

        self.iconpath = ImageTk.PhotoImage(file=f"{config.parent_path()}/data/images/golden_pfp.ico")
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

        set_default_color_theme(config.theme_path())
        self.configure(fg_color=config.read_theme("CTk")["fg_color"])

        self.tab_control = CTkTabview(master=self, height=265, fg_color=config.read_theme("CTkTabview")["fg_color"])
        main_tab = self.tab_control.add("Main")
        discord_tab = self.tab_control.add("Discord")
        crafting_tab = self.tab_control.add("Crafting")
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
        crafting_clicks = CTkButton(state="disabled", master=crafting_frame, text="Assign Crafting", command=self.crafting_clicks).grid(row=5, column=2, padx=5, pady=5, stick="w")
    
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
        quanity = CTkEntry(master=items_stuff, width=80, textvariable=self.tk_var_list['item_scheduler_quantity']).grid(row=4, column=0, padx=5, pady=5, stick="w")

        biome_config = CTkFrame(master=extras_tab)
        biome_config.grid(row=0, column=2, stick="n", padx=(5, 0))
        biome_title = CTkLabel(master=biome_config, text="Biome Settings", font=h1).grid(row=0, column=0)
        enable_biome = CTkCheckBox(master=biome_config, text="Enable Biome Detection", command=self.start_detection, variable=self.tk_var_list['biome_detection']['enabled'], onvalue="1", offvalue="0").grid(row=2, column=0, padx=5, pady=5, stick="w")
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
    
        credits_text = """
Founders (Aurium):   |   Developers:
Golden | /x64/dumped  |  vexthecoder

Special Thanks to:
Radiant Team, (letting us use their saving/LPS)
Kat (@Rammstein), (made server logo)
Vex (@vex.rng), for greatly helping me with the detection

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
        submit_button = CTkButton(master=frame, text="Submit", command=lambda: self.submit())
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

    def submit(self):
        config.save_tk_list(self.tk_var_list)
        config.save_config(config.config_data)
        self.auto_equip_window.destroy()

    def start(self):
        config.save_tk_list(self.tk_var_list)
        config.save_config(config.config_data)
        if main_loop.running == False:
            self.iconify()
        main_loop.start()
    
    def stop(self):
        config.save_tk_list(self.tk_var_list)
        config.save_config(config.config_data)
        if main_loop.running == False:
            self.deiconify()
        main_loop.stop()

    def restart(self):
        os.execv(sys.executable, ['python', f'"{sys.argv[0]}"'])

    def focus_widget(self, event):
        try:
            event.widget.focus_set()
        except:
            pass
    
    def start_detection(self):
        response = messagebox.askyesno(title="Detection", message="Do you wish to start the detection?\nTo Close the detection press ctrl + c.")
        if response:
            if getattr(sys, 'frozen', False):
                # If the application is frozen (compiled)
                subprocess.Popen([sys.executable, 'Tracker.py'])
            else:
                os.system('python Tracker.py')
        else:
            return False

    def assign_clicks_gui(self):
        self.assign_clicks_gui = CTkToplevel()
        self.assign_clicks_gui.title("Assign Clicks")
        self.assign_clicks_gui.geometry("400x540")
        self.assign_clicks_gui.resizable(False, False)
        self.assign_clicks_gui.attributes("-topmost", True)
        aura_equip_frame = CTkFrame(master=self.assign_clicks_gui)
        aura_equip_frame.grid(row=0, column=0, sticky="n", padx=(1, 1))

        aura_storage_label = CTkLabel(master=aura_equip_frame, text="Aura Storage:")
        aura_storage_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")

        aura_storage_x_entry = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['aura_storage'][0], placeholder_text="X")
        aura_storage_x_entry.grid(row=1, column=1, padx=5, pady=2)

        aura_storage_y_entry = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['aura_storage'][1], placeholder_text="Y")
        aura_storage_y_entry.grid(row=1, column=2, padx=5, pady=2)

        assign_button1 = CTkButton(master=aura_equip_frame, text="Assign Click!", command=lambda: self.start_capture_thread('aura_storage', aura_storage_x_entry, aura_storage_y_entry))
        assign_button1.grid(row=1, column=3, padx=5, pady=2)

        regular_aura_tab_label = CTkLabel(master=aura_equip_frame, text="Regular Aura Tab:")
        regular_aura_tab_label.grid(row=2, column=0, padx=5, pady=2, sticky="w")

        regular_aura_tab_x_entry = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['regular_tab'][0], placeholder_text="X")
        regular_aura_tab_x_entry.grid(row=2, column=1, padx=5, pady=2)

        regular_aura_tab_y_entry = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['regular_tab'][1], placeholder_text="Y")
        regular_aura_tab_y_entry.grid(row=2, column=2, padx=5, pady=2)

        assign_button2 = CTkButton(master=aura_equip_frame, text="Assign Click!", command=lambda: self.start_capture_thread('regular_tab', regular_aura_tab_x_entry, regular_aura_tab_y_entry))
        assign_button2.grid(row=2, column=3, padx=5, pady=2)

        special_aura_tab_label = CTkLabel(master=aura_equip_frame, text="Special Aura Tab:")
        special_aura_tab_label.grid(row=3, column=0, padx=5, pady=2, sticky="w")

        special_aura_tab_x_entry = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['special_tab'][0], placeholder_text="X")
        special_aura_tab_x_entry.grid(row=3, column=1, padx=5, pady=2)

        special_aura_tab_y_entry = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['special_tab'][1], placeholder_text="Y")
        special_aura_tab_y_entry.grid(row=3, column=2, padx=5, pady=2)

        assign_button3 = CTkButton(master=aura_equip_frame, text="Assign Click!", command=lambda: self.start_capture_thread('special_tab', special_aura_tab_x_entry, special_aura_tab_y_entry))
        assign_button3.grid(row=3, column=3, padx=5, pady=2)

        aura_search_bar_label = CTkLabel(master=aura_equip_frame, text="Aura Search Bar:")
        aura_search_bar_label.grid(row=4, column=0, padx=5, pady=2, sticky="w")

        aura_search_bar_x_entry = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['search_bar'][0], placeholder_text="X")
        aura_search_bar_x_entry.grid(row=4, column=1, padx=5, pady=2)

        aura_search_bar_y_entry = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['search_bar'][1], placeholder_text="Y")
        aura_search_bar_y_entry.grid(row=4, column=2, padx=5, pady=2)

        assign_button4 = CTkButton(master=aura_equip_frame, text="Assign Click!", command=lambda: self.start_capture_thread('search_bar', aura_search_bar_x_entry, aura_search_bar_y_entry))
        assign_button4.grid(row=4, column=3, padx=5, pady=2)

        first_aura_slot_label = CTkLabel(master=aura_equip_frame, text="First Aura Slot:")
        first_aura_slot_label.grid(row=5, column=0, padx=5, pady=2, sticky="w")

        first_aura_slot_x_entry = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['aura_first_slot'][0], placeholder_text="X")
        first_aura_slot_x_entry.grid(row=5, column=1, padx=5, pady=2)

        first_aura_slot_y_entry = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['aura_first_slot'][1], placeholder_text="Y")
        first_aura_slot_y_entry.grid(row=5, column=2, padx=5, pady=2)

        assign_button5 = CTkButton(master=aura_equip_frame, text="Assign Click!", command=lambda: self.start_capture_thread('aura_first_slot', first_aura_slot_x_entry, first_aura_slot_y_entry))
        assign_button5.grid(row=5, column=3, padx=5, pady=2)

        equip_button_label = CTkLabel(master=aura_equip_frame, text="Equip Button:")
        equip_button_label.grid(row=6, column=0, padx=5, pady=2, sticky="w")

        equip_button_x_entry = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['equip_button'][0], placeholder_text="X")
        equip_button_x_entry.grid(row=6, column=1, padx=5, pady=2)

        equip_button_y_entry = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['equip_button'][1], placeholder_text="Y")
        equip_button_y_entry.grid(row=6, column=2, padx=5, pady=2)

        assign_button6 = CTkButton(master=aura_equip_frame, text="Assign Click!", command=lambda: self.start_capture_thread('equip_button', equip_button_x_entry, equip_button_y_entry))
        assign_button6.grid(row=6, column=3, padx=5, pady=2)

        alignment = CTkLabel(master=aura_equip_frame, text="Collection Menu:")
        alignment.grid(row=7, column=0, padx=5, pady=2, sticky="w")

        alignment_x_entry = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['collection_menu'][0], placeholder_text="X")
        alignment_x_entry.grid(row=7, column=1, padx=5, pady=2)

        alignmet_y_entry = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['collection_menu'][1], placeholder_text="Y")
        alignmet_y_entry.grid(row=7, column=2, padx=5, pady=2)

        assign_button7 = CTkButton(master=aura_equip_frame, text="Assign Click!", command=lambda: self.start_capture_thread('collection_menu', alignment_x_entry, alignmet_y_entry))
        assign_button7.grid(row=7, column=3, padx=5, pady=2)

        exit_alignment = CTkLabel(master=aura_equip_frame, text="Exit Collection:")
        exit_alignment.grid(row=8, column=0, padx=5, pady=2, sticky="w")

        exit_alignment_x_entry = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['exit_collection'][0], placeholder_text="X")
        exit_alignment_x_entry.grid(row=8, column=1, padx=5, pady=2)

        exit_alignmet_y_entry = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['exit_collection'][1], placeholder_text="Y")
        exit_alignmet_y_entry.grid(row=8, column=2, padx=5, pady=2)

        assign_button8 = CTkButton(master=aura_equip_frame, text="Assign Click!", command=lambda: self.start_capture_thread('exit_collection', exit_alignment_x_entry, exit_alignmet_y_entry))
        assign_button8.grid(row=8, column=3, padx=5, pady=2)

        invo_tab = CTkLabel(master=aura_equip_frame, text="Items Storage:")
        invo_tab.grid(row=9, column=0, padx=5, pady=2, sticky="w")

        items_tabx = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['items_storage'][0], placeholder_text="X")
        items_tabx.grid(row=9, column=1, padx=5, pady=2, sticky="w")

        items_taby = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['items_storage'][1], placeholder_text="Y")
        items_taby.grid(row=9, column=2, padx=5, pady=2, sticky="w")

        assign_button9 = CTkButton(master=aura_equip_frame, text="Assign Click!", command=lambda: self.start_capture_thread('items_storage', items_tabx, items_taby))
        assign_button9.grid(row=9, column=3, padx=5, pady=2)

        invo_storge = CTkLabel(master=aura_equip_frame, text="Items Tab:")
        invo_storge.grid(row=10, column=0, padx=5, pady=2, sticky="w")

        items_barx = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['items_tab'][0], placeholder_text="X")
        items_barx.grid(row=10, column=1, padx=5, pady=2, sticky="w")

        items_bary = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['items_tab'][1], placeholder_text="Y")
        items_bary.grid(row=10, column=2, padx=5, pady=2, sticky="w")

        assign_button10 = CTkButton(master=aura_equip_frame, text="Assign Click!", command=lambda: self.start_capture_thread('items_tab', items_barx, items_bary))
        assign_button10.grid(row=10, column=3, padx=5, pady=2)

        invo_bar = CTkLabel(master=aura_equip_frame, text="Items Search Bar:")
        invo_bar.grid(row=11, column=0, padx=5, pady=2, sticky="w")

        items_searchx = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['items_bar'][0], placeholder_text="X")
        items_searchx.grid(row=11, column=1, padx=5, pady=2, sticky="w")

        items_searchy = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['items_bar'][1], placeholder_text="Y")
        items_searchy.grid(row=11, column=2, padx=5, pady=2, sticky="w")

        assign_button11 = CTkButton(master=aura_equip_frame, text="Assign Click!", command=lambda: self.start_capture_thread('items_bar', items_searchx, items_searchy))
        assign_button11.grid(row=11, column=3, padx=5, pady=2)

        invo_bar = CTkLabel(master=aura_equip_frame, text="Items First Slot:")
        invo_bar.grid(row=12, column=0, padx=5, pady=2, sticky="w")

        items_slotx = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['item_first_slot'][0], placeholder_text="X")
        items_slotx.grid(row=12, column=1, padx=5, pady=2, sticky="w")

        items_sloty = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['item_first_slot'][1], placeholder_text="Y")
        items_sloty.grid(row=12, column=2, padx=5, pady=2, sticky="w")

        assign_button12 = CTkButton(master=aura_equip_frame, text="Assign Click!", command=lambda: self.start_capture_thread('item_first_slot', items_slotx, items_sloty))
        assign_button12.grid(row=12, column=3, padx=5, pady=2)
        
        invo_bar = CTkLabel(master=aura_equip_frame, text="Quanity Bar:")
        invo_bar.grid(row=13, column=0, padx=5, pady=2, sticky="w")

        quanityx = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['item_value'][0], placeholder_text="X")
        quanityx.grid(row=13, column=1, padx=5, pady=2, sticky="w")

        quanityy = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['item_value'][1], placeholder_text="Y")
        quanityy.grid(row=13, column=2, padx=5, pady=2, sticky="w")

        assign_button13 = CTkButton(master=aura_equip_frame, text="Assign Click!", command=lambda: self.start_capture_thread('item_value', quanityx, quanityy))
        assign_button13.grid(row=13, column=3, padx=5, pady=2)

        invo_button = CTkLabel(master=aura_equip_frame, text="Use Button:")
        invo_button.grid(row=14, column=0, padx=5, pady=2, sticky="w")

        usex = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['use_button'][0], placeholder_text="X")
        usex.grid(row=14, column=1, padx=5, pady=2, sticky="w")

        usey = CTkEntry(master=aura_equip_frame, width=60, textvariable=self.tk_var_list['clicks']['use_button'][1], placeholder_text="Y")
        usey.grid(row=14, column=2, padx=5, pady=2, sticky="w")

        assign_button14 = CTkButton(master=aura_equip_frame, text="Assign Click!", command=lambda: self.start_capture_thread('use_button', usex, usey))
        assign_button14.grid(row=14, column=3, padx=5, pady=2)
    
    def crafting_clicks(self):
        self.crafting_clicks = CTkToplevel()
        self.crafting_clicks.title("Crafting")
        self.crafting_clicks.geometry("400x540")
        self.crafting_clicks.resizable(False, False)
        
        crafting_frame = CTkFrame(master=self.crafting_clicks)
        crafting_frame.pack(fill="both", expand=True)

        for i in range(1, 6):
            potion_search_bar_label = CTkLabel(master=crafting_frame, text=f"#{i} manual potion add box:")
            potion_search_bar_label.grid(row=i, column=0, padx=5, pady=2, sticky="w")

            potion_search_bar_x_entry = CTkEntry(master=crafting_frame, width=60, textvariable=self.tk_var_list[f'clicks'][f"{i}_potion_manual_x"], placeholder_text="X")
            potion_search_bar_x_entry.grid(row=i, column=1, padx=5, pady=2)

            potion_search_bar_y_entry = CTkEntry(master=crafting_frame, width=60, textvariable=self.tk_var_list[f'clicks'][f"{i}_potion_manual_y"], placeholder_text="Y")
            potion_search_bar_y_entry.grid(row=i, column=2, padx=5, pady=2)

            assign_potion_search_bar_click = CTkButton(master=crafting_frame, text="Assign Click!", command=lambda key=self.config_key, x_entry=potion_search_bar_x_entry, y_entry=potion_search_bar_y_entry: self.start_capture_thread(key, x_entry, y_entry))
            assign_potion_search_bar_click.grid(row=i, column=3, padx=5, pady=2)

        potion_search_bar_label = CTkLabel(master=crafting_frame, text="Potion Search Bar:")
        potion_search_bar_label.grid(row=7, column=0, padx=5, pady=2, sticky="w")

        potion_search_bar_x_entry = CTkEntry(master=crafting_frame, width=60, textvariable=self.tk_var_list['clicks']['PotionBarX'])
        potion_search_bar_x_entry.grid(row=7, column=1, padx=5, pady=2)

        potion_search_bar_y_entry = CTkEntry(master=crafting_frame, width=60, textvariable=self.tk_var_list['clicks']['PotionBarY'])
        potion_search_bar_y_entry.grid(row=7, column=2, padx=5, pady=2)

        assign_potion_search_bar_click = CTkButton(master=crafting_frame, text="Assign Click!", command=lambda key=self.config_key: self.start_capture_thread(key, potion_search_bar_x_entry, potion_search_bar_y_entry))
        assign_potion_search_bar_click.grid(row=7, column=3, padx=5, pady=2)

        first_potion_slot_label = CTkLabel(master=crafting_frame, text="First Potion Slot:")
        first_potion_slot_label.grid(row=8, column=0, padx=5, pady=2, sticky="w")

        first_potion_slot_x_entry = CTkEntry(master=crafting_frame, width=60, textvariable=self.tk_var_list['clicks']['FirstSlotPotionX'])
        first_potion_slot_x_entry.grid(row=8, column=1, padx=5, pady=2)

        first_potion_slot_y_entry = CTkEntry(master=crafting_frame, width=60, textvariable=self.tk_var_list['clicks']['FirstSlotPotionY'])
        first_potion_slot_y_entry.grid(row=8, column=2, padx=5, pady=2)

        assign_first_potion_slot_click = CTkButton(master=crafting_frame, text="Assign Click!", command=lambda key=self.config_key: self.start_capture_thread(key, first_potion_slot_x_entry, first_potion_slot_y_entry))
        assign_first_potion_slot_click.grid(row=8, column=3, padx=5, pady=2)

        craft_button_label = CTkLabel(master=crafting_frame, text="Craft Button:")
        craft_button_label.grid(row=9, column=0, padx=5, pady=2, sticky="w")

        craft_button_x_entry = CTkEntry(master=crafting_frame, width=60, textvariable=self.tk_var_list['clicks']['CraftButtonX'])
        craft_button_x_entry.grid(row=9, column=1, padx=5, pady=2)

        craft_button_y_entry = CTkEntry(master=crafting_frame, width=60, textvariable=self.tk_var_list['clicks']['CraftButtonY'])
        craft_button_y_entry.grid(row=9, column=2, padx=5, pady=2)

        assign_craft_button_click = CTkButton(master=crafting_frame, text="Assign Click!", command=lambda key=self.config_key: self.start_capture_thread(key, craft_button_x_entry, craft_button_y_entry))
        assign_craft_button_click.grid(row=9, column=3, padx=5, pady=2)

        auto_button_label = CTkLabel(master=crafting_frame, text="Auto Button:")
        auto_button_label.grid(row=10, column=0, padx=5, pady=2, sticky="w")

        auto_button_x_entry = CTkEntry(master=crafting_frame, width=60, textvariable=self.tk_var_list['clicks']['AutoButtonX'])
        auto_button_x_entry.grid(row=10, column=1, padx=5, pady=2)

        auto_button_y_entry = CTkEntry(master=crafting_frame, width=60, textvariable=self.tk_var_list['clicks']['AutoButtonY'])
        auto_button_y_entry.grid(row=10, column=2, padx=5, pady=2)

        assign_auto_button_click = CTkButton(master=crafting_frame, text="Assign Click!", command=lambda key=self.config_key: self.start_capture_thread(key, auto_button_x_entry, auto_button_y_entry))
        assign_auto_button_click.grid(row=10, column=3, padx=5, pady=2)

    def start_capture_thread(self, config_key, x_entry, y_entry):
        self.snipping_window = CTkToplevel()
        self.snipping_window.attributes("-fullscreen", True)
        self.snipping_window.attributes("-alpha", 0.3)
        self.snipping_window.config(cursor="cross")
        self.canvas = CTkCanvas(self.snipping_window, bg="lightblue", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Store the entry widgets and config key for later use
        self.x_entry = x_entry
        self.y_entry = y_entry
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
            self.end_x, self.end_y = event.x, event.y
            
            # Update the canvas with the current selection rectangle
            if hasattr(self, 'canvas'):
                self.canvas.delete("selection_rect")
                self.canvas.create_rectangle(self.begin_x, self.begin_y, self.end_x, self.end_y,
                                          outline="white", width=2, tag="selection_rect")
            
            # Update the entry widgets with the current coordinates
            if hasattr(self, 'x_entry') and self.x_entry.winfo_exists():
                self.x_entry.delete(0, 'end')
                self.x_entry.insert(0, str(self.end_x))
            
            if hasattr(self, 'y_entry') and self.y_entry.winfo_exists():
                self.y_entry.delete(0, 'end')
                self.y_entry.insert(0, str(self.end_y))
        except Exception as e:
            print(f"Error in on_mouse_drag: {e}")

    def mouse_release(self, event):
        try:
            self.end_x = event.x
            self.end_y = event.y
            
            # Update the entry widgets with the final coordinates
            if hasattr(self, 'x_entry') and self.x_entry.winfo_exists():
                self.x_entry.delete(0, 'end')
                self.x_entry.insert(0, str(self.end_x))
            
            if hasattr(self, 'y_entry') and self.y_entry.winfo_exists():
                self.y_entry.delete(0, 'end')
                self.y_entry.insert(0, str(self.end_y))
            
            # Update the config with new coordinates
            if hasattr(self, 'config_key'):
                config_key = self.config_key.lower().replace('x', '').replace('y', '')
                config.config_data['clicks'][config_key] = [self.end_x, self.end_y]
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
        self.biome_window.geometry("300x400")
        self.biome_window.resizable(False, False)
        self.biome_window.attributes("-topmost", True)
    
        biomes = ["Windy", "Rainy", "Snowy", "Sandstorm", "Hell", "Starfall", "Corruption", "Null", "Glitched", "Dreamspace"]
        for i, biome in enumerate(biomes):
            state = "disabled" if biome in ["Glitched", "Dreamspace"] else "normal"
            CTkCheckBox(master=self.biome_window, text=biome, state=state, variable=self.tk_var_list['biomes'][biome], onvalue="1", offvalue="0").grid(row=i, column=0, padx=5, pady=5, sticky="w")

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
                    update_response = messagebox.askyesno("New Update!", f"New Version of the macro {latest_version}, Would you like to update?")
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
            
