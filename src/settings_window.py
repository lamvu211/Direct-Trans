"""
settings_window.py - Settings UI for DirectTrans
"""

import tkinter as tk
from tkinter import ttk
import webbrowser
import os
from font_mapper import FontMapper

from ui.constants import *
from ui.i18n import TRANSLATIONS
from ui.api_config_tab import ApiConfigTab
from ui.hotkey_config_tab import HotkeyConfigTab


class SettingsWindow:
    def __init__(self, root, config, on_save_callback, on_close_callback=None, hotkey_manager=None):
        self.root = root
        self.config = config
        self.on_save_callback = on_save_callback
        self.on_close_callback = on_close_callback
        self.hotkey_manager = hotkey_manager
        self.window = None

        self.current_lang = self.config.data.get('ui_language', 'vi')
        self.logo_img = None

    def _on_minimize(self, event):
        import logging
        if event.widget == self.window and self.window.winfo_exists() and self.window.state() == 'iconic':
            logging.info("Settings window minimized. Withdrawing to tray.")
            self.window.withdraw()

    def restore_and_focus(self):
        if self.window and self.window.winfo_exists():
            self.window.deiconify()
            self.window.state('normal')
            self.window.attributes('-topmost', True)
            self.window.focus_force()

    def show(self):
        self.window = tk.Toplevel(self.root)
        self.window.title("DirectTrans Settings v1.0.6")
        self.window.geometry("580x630")
        self.window.resizable(True, True)
        self.window.minsize(580, 500)
        self.window.configure(bg=BASE)
        self.window.attributes('-topmost', True)
        self.window.after(200, lambda: self.window.attributes('-topmost', False))
        self.window.bind("<Unmap>", self._on_minimize)

        try:
            icon_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 'assets', 'icon.ico'
            )
            if os.path.exists(icon_path):
                self.window.iconbitmap(icon_path)
        except Exception:
            pass

        self._create_header()

        canvas = tk.Canvas(self.window, bg=BASE, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.window, orient='vertical', command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=BASE)

        self.scroll_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )

        canvas_window_id = canvas.create_window((0, 0), window=self.scroll_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_window_id, width=event.width)
        canvas.bind('<Configure>', _on_canvas_configure)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)

        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)

        def on_close():
            canvas.unbind("<MouseWheel>")
            try:
                self.window.destroy()
            except Exception:
                pass
            if self.on_close_callback:
                self.on_close_callback()

        self.window.protocol("WM_DELETE_WINDOW", on_close)
        self.close_window = on_close

        # Initialize sub-components
        self.api_tab = ApiConfigTab(
            self.scroll_frame, 
            self.config, 
            self.on_save_callback, 
            lambda: self.current_lang,
            lambda: self.window
        )
        self._create_options_section()
        self.hotkey_tab = HotkeyConfigTab(
            self.scroll_frame, 
            self.config, 
            self.on_save_callback, 
            self.hotkey_manager, 
            lambda: self.current_lang,
            lambda: self.window
        )

        try:
            self.update_ui_language(self.config.data.get('ui_language', 'vi'))
        except Exception as e:
            import logging
            logging.warning(f"Failed to apply UI language font: {e}")

    def _create_header(self):
        header = tk.Frame(self.window, bg=MANTLE, pady=8)
        header.pack(fill='x', padx=0, pady=0)

        top_row = tk.Frame(header, bg=MANTLE)
        top_row.pack(fill='x', padx=10, pady=(0, 6))

        logo_loaded = False
        logo_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'assets', 'logo-direct-trans.png'
        )
        if not os.path.exists(logo_path):
            logo_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logo-direct-trans.png'
            )

        if os.path.exists(logo_path):
            try:
                from PIL import Image, ImageTk
                img = Image.open(logo_path)
                img = img.resize((24, 24), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img)

                logo_lbl = tk.Label(top_row, image=self.logo_img, bg=MANTLE)
                logo_lbl.pack(side='left', padx=(0, 6))
                logo_loaded = True
            except Exception as e:
                import logging
                logging.error(f"Failed to load/resize logo image: {e}")

        if not logo_loaded:
            logo_lbl = tk.Label(
                top_row, text="⚙", fg=PRIMARY, bg=MANTLE,
                font=('Segoe UI', 12, 'bold')
            )
            logo_lbl.pack(side='left', padx=(0, 6))

        self.title_label = tk.Label(
            top_row, text="DirectTrans",
            fg=TEXT_COLOR, bg=MANTLE,
            font=('Georgia', 14, 'bold')
        )
        self.title_label.pack(side='left')

        def open_user_manual(event=None):
            import sys
            if getattr(sys, 'frozen', False):
                base = sys._MEIPASS
                manual_path = os.path.join(base, 'assets', 'user_manual.html')
            else:
                base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                manual_path = os.path.join(base, 'src', 'assets', 'user_manual.html')
            
            if os.path.exists(manual_path):
                import subprocess
                try:
                    os.startfile(manual_path)
                except Exception:
                    webbrowser.open('file:///' + manual_path.replace('\\', '/').replace(' ', '%20'))
            else:
                online_url = 'https://github.com/lamvu211/Direct-Trans'
                webbrowser.open(online_url)
                
        bottom_row = tk.Frame(header, bg=MANTLE)
        bottom_row.pack(fill='x', padx=10)

        ui_languages = [
            ("Tiếng Việt", "vi"), 
            ("English", "en"), 
            ("한국어", "ko"), 
            ("中文", "zh"), 
            ("日本語", "ja")
        ]
        ui_lang_names = [l[0] for l in ui_languages]
        ui_lang_map = {l[0]: l[1] for l in ui_languages}
        reverse_ui_lang_map = {l[1]: l[0] for l in ui_languages}

        self.ui_lang_var = tk.StringVar(value=reverse_ui_lang_map.get(self.current_lang, "Tiếng Việt"))

        self.lang_ui_combo = ttk.Combobox(
            bottom_row, textvariable=self.ui_lang_var,
            values=ui_lang_names, state='readonly', width=14
        )
        self.lang_ui_combo.pack(side='left', padx=(0, 6))

        self.manual_btn = tk.Button(
            bottom_row, text="User manual",
            fg=WHITE, bg=PRIMARY, bd=0, cursor='hand2', font=('Segoe UI', 9, 'bold'),
            padx=16, pady=2,
            command=open_user_manual
        )
        self.manual_btn.pack(side='left', padx=(0, 6))

        def open_update_link():
            import webbrowser
            webbrowser.open("https://github.com/lamvu211/Direct-Trans/releases/latest")

        self.update_btn = tk.Button(
            bottom_row, text="Update",
            fg=WHITE, bg=PRIMARY, bd=0, cursor='hand2', font=('Segoe UI', 9, 'bold'),
            padx=16, pady=2,
            command=open_update_link
        )
        self.update_btn.pack(side='left')

        def on_ui_lang_selected(event):
            selected_name = self.ui_lang_var.get()
            lang_code = ui_lang_map.get(selected_name, 'vi')
            self.update_ui_language(lang_code)
            self.config.save()


        self.lang_ui_combo.bind("<<ComboboxSelected>>", on_ui_lang_selected)

    def _create_options_section(self):
        self.options_lf = tk.LabelFrame(
            self.scroll_frame, text=" Tùy chọn ",
            fg=PRIMARY, bg=BASE,
            font=('Segoe UI', 10, 'bold'),
            labelanchor='nw', padx=10, pady=8
        )
        self.options_lf.pack(fill='x', padx=10, pady=4)

        self.autostart_var = tk.BooleanVar(value=self.config.is_auto_start())

        def on_autostart_change():
            desired = self.autostart_var.get()
            if not self.config.set_auto_start(desired):
                self.autostart_var.set(not desired)
                return
            if self.on_save_callback:
                self.on_save_callback()

        self.autostart_cb = tk.Checkbutton(
            self.options_lf, text="Khởi động cùng Windows", variable=self.autostart_var,
            command=on_autostart_change,
            fg=TEXT_COLOR, bg=BASE,
            selectcolor=SURFACE0,
            activebackground=BASE,
            activeforeground=TEXT_COLOR,
            font=('Segoe UI', 10),
            anchor='w'
        )
        self.autostart_cb.pack(fill='x', pady=2)

    def update_ui_language(self, lang_code):
        self.current_lang = lang_code
        self.config.data['ui_language'] = lang_code

        t = TRANSLATIONS[lang_code]
        font_family = FontMapper.get_font(lang_code)

        default_font = (font_family, 10)
        bold_font = (font_family, 10, 'bold')
        title_font = ('Georgia', 15, 'bold') if lang_code in ('vi', 'en') else (font_family, 15, 'bold')

        self.title_label.config(text=t['title'], font=title_font)
        
        self.options_lf.config(text=t['options_section'], font=bold_font)
        self.autostart_cb.config(text=t['autostart_label'], font=default_font)
        
        self.lang_ui_combo.config(font=default_font)

        # Delegate updates to tabs
        self.api_tab.update_ui_language(lang_code, font_family)
        self.hotkey_tab.update_ui_language(lang_code, font_family)
