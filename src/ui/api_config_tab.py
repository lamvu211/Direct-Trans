import tkinter as tk
from tkinter import ttk
import threading
import webbrowser
from .i18n import TRANSLATIONS, PROVIDERS
from .constants import *
from constants import (
    DEFAULT_PROVIDER,
    PROVIDER_GEMINI,
    PROVIDER_GROQ,
    PROVIDER_MISTRAL,
    PROVIDER_GOOGLE_FREE,
)

class ApiConfigTab:
    def __init__(self, parent_frame, config, on_save_callback, get_current_lang, get_window):
        self.parent_frame = parent_frame
        self.config = config
        self.on_save_callback = on_save_callback
        self.get_current_lang = get_current_lang
        self.get_window = get_window
        
        self.api_frames = {}
        self.gemini_entry = None
        self.groq_entry = None
        self.mistral_entry = None

        self._create_provider_section()
        self._create_api_section()
        self.update_api_frame_visibility(self.config.get_provider())

    def _create_provider_section(self):
        self.provider_lf = tk.LabelFrame(
            self.parent_frame, text=" Nguồn dịch ",
            fg=PRIMARY, bg=BASE,
            font=('Segoe UI', 10, 'bold'),
            labelanchor='nw', padx=10, pady=8
        )
        self.provider_lf.pack(fill='x', padx=10, pady=(0, 4))

        row = tk.Frame(self.provider_lf, bg=BASE)
        row.pack(fill='x')

        self.provider_lbl = tk.Label(
            row, text="Provider:", fg=TEXT_COLOR, bg=BASE,
            font=('Segoe UI', 10)
        )
        self.provider_lbl.pack(side='left')

        self.provider_var = tk.StringVar(value=self.config.get_provider())

        provider_names = [p[0] for p in PROVIDERS]
        self.provider_map_local = {p[0]: p[1] for p in PROVIDERS}
        reverse_map = {p[1]: p[0] for p in PROVIDERS}

        self.provider_var.set(reverse_map.get(self.config.get_provider(), "Gemini"))

        self.provider_combo = ttk.Combobox(
            row, textvariable=self.provider_var,
            values=provider_names, state='readonly', width=14
        )
        self.provider_combo.pack(side='right')
        self.provider_combo.bind("<<ComboboxSelected>>", self.on_provider_selected)

    def on_provider_selected(self, event):
        provider_name = self.provider_var.get()
        provider_key = self.provider_map_local.get(provider_name, DEFAULT_PROVIDER)
        self.config.data['translation_provider'] = provider_key
        self.config.save()
        self.update_api_frame_visibility(provider_key)
        if self.on_save_callback:
            self.on_save_callback()

    def update_api_frame_visibility(self, provider_key):
        for key, frame in self.api_frames.items():
            frame.pack_forget()
        
        if provider_key in self.api_frames:
            if provider_key == PROVIDER_GOOGLE_FREE:
                self.api_frames[provider_key].pack(anchor='w', pady=(4, 0))
            else:
                self.api_frames[provider_key].pack(fill='x', pady=(2, 4))

    def _create_api_section(self):
        t = TRANSLATIONS.get(self.get_current_lang(), TRANSLATIONS['vi'])
        self.api_lf = tk.LabelFrame(
            self.parent_frame, text=" 🔑 API Keys ",
            fg=PRIMARY, bg=BASE,
            font=('Segoe UI', 10, 'bold'),
            labelanchor='nw', padx=10, pady=8
        )
        self.api_lf.pack(fill='x', padx=10, pady=4)

        self._build_provider_frame(PROVIDER_GEMINI, 'https://aistudio.google.com/app/apikey')
        self._build_provider_frame(PROVIDER_GROQ, 'https://console.groq.com/keys')
        self._build_provider_frame(PROVIDER_MISTRAL, 'https://console.mistral.ai/api-keys')
        
        self.google_free_lbl = tk.Label(
            self.api_lf,
            text="ℹ Google Free không cần API key",
            fg=SUBTEXT, bg=BASE,
            font=('Segoe UI', 9, 'italic')
        )
        self.api_frames[PROVIDER_GOOGLE_FREE] = self.google_free_lbl

    def _fetch_provider_models(self, provider, api_key, combo, btn_fetch, btn_save, btn_test):
        if not api_key: return
        self.config.set_api_key(provider, api_key)
        import requests
        import re

        def is_valid_translation_model(model_name: str) -> bool:
            name_lower = model_name.lower()
            blacklist = [
                'embed', 'vision', 'audio', 'tts', 'whisper', 'moderation', 
                'coder', 'math', 'bison', 'learnlm', 'code', 'ocr', 'devstral', 
                'voxtral', 'magistral', 'ministral', 'pixtral', 'robotics', 
                'research', 'antigravity', 'lyria', 'banana', 'guard', 'image',
                'vibe', 'tiny', 'small'
            ]
            if provider == PROVIDER_MISTRAL:
                blacklist.append('open')
            whitelist = ['gemini', 'gemma', 'llama', 'mistral', 'mixtral', 'qwen', 'deepseek', 'gpt']
            clutter = ['preview', 'experimental', '001', '002', 'customtools']
            
            if not any(wl in name_lower for wl in whitelist):
                return False
            for kw in blacklist:
                if kw in name_lower:
                    return False
            if re.search(r'-\d{4}$', name_lower) and 'mistral' in name_lower:
                return False
            for kw in clutter:
                if kw in name_lower:
                    return False
            return True

        def set_ui_state(btn_state, combo_state):
            window = self.get_window()
            if not window or not window.winfo_exists(): return
            btn_fetch.config(state=btn_state)
            btn_save.config(state=btn_state)
            btn_test.config(state=btn_state)
            combo.config(state=combo_state)

        def fetch():
            window = self.get_window()
            if not window: return
            window.after(0, lambda: set_ui_state('disabled', 'disabled'))
            window.after(0, lambda: combo.set("Fetching...") if window.winfo_exists() else None)
            
            try:
                if provider == PROVIDER_GEMINI:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
                    resp = requests.get(url, timeout=10)
                    if resp.status_code == 200:
                        models = [
                            m['name'].replace('models/', '') 
                            for m in resp.json().get('models', []) 
                            if 'generateContent' in m.get('supportedGenerationMethods', []) 
                            and is_valid_translation_model(m['name'])
                        ]
                    else:
                        models = []
                elif provider == PROVIDER_GROQ:
                    url = "https://api.groq.com/openai/v1/models"
                    resp = requests.get(url, headers={"Authorization": f"Bearer {api_key}", "User-Agent": "Mozilla/5.0"}, timeout=10)
                    if resp.status_code == 200:
                        models = [m['id'] for m in resp.json().get('data', []) if is_valid_translation_model(m['id'])]
                    else:
                        models = []
                elif provider == PROVIDER_MISTRAL:
                    url = "https://api.mistral.ai/v1/models"
                    resp = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
                    if resp.status_code == 200:
                        models = [m['id'] for m in resp.json().get('data', []) if is_valid_translation_model(m['id'])]
                    else:
                        models = []
                
                if models:
                    def update_success():
                        if not window.winfo_exists(): return
                        combo['values'] = models
                        current = getattr(self.config, f"get_{provider}_model")()
                        if current in models:
                            combo.set(current)
                        else:
                            combo.set(models[0])
                            getattr(self.config, f"set_{provider}_model")(models[0])
                        set_ui_state('normal', 'readonly')
                    window.after(0, update_success)
                else:
                    def update_fail():
                        if not window.winfo_exists(): return
                        combo.set("Load Failed")
                        set_ui_state('normal', 'readonly')
                    window.after(0, update_fail)
            except Exception:
                def update_exc():
                    if not window.winfo_exists(): return
                    combo.set("Load Failed")
                    set_ui_state('normal', 'readonly')
                window.after(0, update_exc)

        threading.Thread(target=fetch, daemon=True).start()

    def _build_provider_frame(self, provider: str, api_link: str):
        frame = tk.Frame(self.api_lf, bg=BASE)
        frame.columnconfigure(1, weight=1)
        
        lbl = tk.Label(frame, text="API key:", fg=TEXT_COLOR, bg=BASE, font=('Segoe UI', 10, 'bold'))
        lbl.grid(row=0, column=0, sticky='w', pady=2)
        setattr(self, f"{provider}_lbl", lbl)
        
        entry_frame = tk.Frame(frame, bg=BASE, highlightthickness=1, highlightbackground=BORDER_COLOR, highlightcolor=PRIMARY)
        entry_frame.grid(row=0, column=1, sticky='ew', padx=(8, 4), pady=2)
        
        entry = tk.Entry(entry_frame, show='•', bg=BASE, fg=TEXT_COLOR, insertbackground=TEXT_COLOR, font=('Segoe UI', 10), relief='flat', bd=0)
        btn_clear = tk.Label(entry_frame, text="✕", fg=SUBTEXT, bg=BASE, font=('Segoe UI', 9), cursor='hand2')
        btn_clear.pack(side='right', padx=(4, 4))
        entry.pack(side='left', fill='x', expand=True, padx=(4, 0), pady=2)
        entry.insert(0, self.config.get_api_key(provider))
        btn_clear.bind("<Button-1>", lambda e: (entry.delete(0, tk.END), self.on_save_callback() if self.on_save_callback else None))
        setattr(self, f"{provider}_entry", entry)

        btn_fetch = tk.Button(frame, text="↻ Load Models", fg=PRIMARY, bg=BASE, bd=0, font=('Segoe UI', 8), cursor='hand2')
        btn_fetch.grid(row=0, column=2, sticky='w', padx=(4, 4), pady=2)

        link_lbl = tk.Label(frame, text="🔗 Lấy API key", fg=PRIMARY, bg=BASE, cursor='hand2', font=('Segoe UI', 9, 'underline'))
        link_lbl.grid(row=0, column=3, columnspan=2, sticky='e', padx=(4, 0), pady=2)
        link_lbl.bind('<Button-1>', lambda e, l=api_link: webbrowser.open(l))
        setattr(self, f"{provider}_link", link_lbl)

        tk.Label(frame, text="Model:", fg=TEXT_COLOR, bg=BASE, font=('Segoe UI', 9)).grid(row=1, column=0, sticky='w', pady=2)
        
        current_model = getattr(self.config, f"get_{provider}_model")()
        model_combo = ttk.Combobox(frame, values=[current_model], state='readonly', width=32, font=('Segoe UI', 9))
        model_combo.set(current_model)
        model_combo.grid(row=1, column=1, sticky='ew', padx=(8, 4), pady=2)
        model_combo.bind("<<ComboboxSelected>>", lambda e: (getattr(self.config, f"set_{provider}_model")(model_combo.get()), self.on_save_callback() if self.on_save_callback else None))
        setattr(self, f"{provider}_model_combo", model_combo)

        btn_test = tk.Button(frame, text="Test", fg=TEXT_COLOR, bg=SURFACE1, bd=0, font=('Segoe UI', 9), padx=8, pady=2, cursor='hand2')
        btn_test.grid(row=1, column=2, sticky='w', padx=(4, 4), pady=2)

        status_lbl = tk.Label(frame, text="", fg=TEXT_COLOR, bg=BASE, font=('Segoe UI', 9, 'bold'), anchor='e', width=10)
        status_lbl.grid(row=1, column=3, sticky='e', padx=(4, 4), pady=2)
        setattr(self, f"{provider}_status_lbl", status_lbl)

        t = TRANSLATIONS.get(self.get_current_lang(), TRANSLATIONS['vi'])
        btn_save = tk.Button(frame, text=t['save_btn'], fg=WHITE, bg=PRIMARY, bd=0, font=('Segoe UI', 9, 'bold'), padx=8, pady=2, cursor='hand2')
        btn_save.grid(row=1, column=4, sticky='e', padx=(4, 0), pady=2)
        setattr(self, f"{provider}_btn_save", btn_save)

        btn_save.config(command=lambda: self._quick_save_key(provider, entry.get().strip(), status_lbl))
        btn_test.config(command=lambda: self._test_key(provider, entry.get().strip(), status_lbl, model_combo, btn_fetch, btn_save, btn_test))
        btn_fetch.config(command=lambda bf=btn_fetch, bs=btn_save, bt=btn_test: self._fetch_provider_models(provider, entry.get().strip(), model_combo, bf, bs, bt))

        self.api_frames[provider] = frame

    def _quick_save_key(self, provider: str, key: str, status_lbl: tk.Label):
        self.config.set_api_key(provider, key)
        t = TRANSLATIONS.get(self.get_current_lang(), TRANSLATIONS['vi'])
        status_lbl.config(text=t['save_success'], fg=SUCCESS)
        window = self.get_window()
        if window:
            window.after(1500, lambda: status_lbl.config(text=""))
            try:
                clip_content = window.clipboard_get()
                if clip_content == key:
                    window.clipboard_clear()
            except Exception:
                pass
        if self.on_save_callback:
            self.on_save_callback()

    def _test_key(self, provider: str, key: str, status_lbl: tk.Label, combo: ttk.Combobox = None, btn_fetch: tk.Button = None, btn_save: tk.Button = None, btn_test: tk.Button = None):
        t_dict = TRANSLATIONS.get(self.get_current_lang(), TRANSLATIONS['vi'])
        if not key:
            status_lbl.config(text=t_dict['save_empty'], fg=RED)
            return

        status_lbl.config(text=t_dict['test_running'], fg=PRIMARY)
        
        if combo: combo.config(state='disabled')
        if btn_fetch: btn_fetch.config(state='disabled')
        if btn_save: btn_save.config(state='disabled')
        if btn_test: btn_test.config(state='disabled')

        def run_test():
            from translator import GeminiTranslator, GroqTranslator, MistralTranslator
            
            model = combo.get() if combo and combo.get() and combo.get() not in ["Load Failed", "Fetching..."] else getattr(self.config, f"get_{provider}_model")()
            window = self.get_window()
            
            try:
                res = None
                if provider == PROVIDER_GEMINI:
                    t = GeminiTranslator()
                    res = t.translate("Hi", "vi", api_key=key, model=model)
                elif provider == PROVIDER_GROQ:
                    t = GroqTranslator()
                    res = t.translate("Hi", "vi", api_key=key, model=model)
                elif provider == PROVIDER_MISTRAL:
                    t = MistralTranslator()
                    res = t.translate("Hi", "vi", api_key=key, model=model)

                if res:
                    self.config.set_api_key(provider, key)
                    def _set_pass():
                        if not window or not window.winfo_exists(): return
                        status_lbl.config(text=t_dict['test_pass'], fg=SUCCESS)
                        if combo: combo.config(state='readonly')
                        if btn_fetch: btn_fetch.config(state='normal')
                        if btn_save: btn_save.config(state='normal')
                        if btn_test: btn_test.config(state='normal')
                    if window: window.after(0, _set_pass)
                else:
                    raise Exception("Empty response")
            except Exception as e:
                import logging
                logging.error(f"Test API key failed for {model}: {e}")
                err_msg = str(e)
                short_err = t_dict['test_fail']
                if "429" in err_msg: short_err = "Fail (429)"
                elif "403" in err_msg: short_err = "Fail (403)"
                elif "400" in err_msg: short_err = "Fail (400)"
                elif "connection" in err_msg.lower() or "timeout" in err_msg.lower(): short_err = t_dict['net_error']
                
                def _set_fail(msg=short_err):
                    if not window or not window.winfo_exists(): return
                    status_lbl.config(text=msg, fg=RED)
                    if combo: combo.config(state='readonly')
                    if btn_fetch: btn_fetch.config(state='normal')
                    if btn_save: btn_save.config(state='normal')
                    if btn_test: btn_test.config(state='normal')
                if window: window.after(0, _set_fail)

        threading.Thread(target=run_test, daemon=True).start()

    def update_ui_language(self, lang_code, font_family):
        t = TRANSLATIONS.get(lang_code, TRANSLATIONS['vi'])
        default_font = (font_family, 10)
        bold_font = (font_family, 10, 'bold')
        small_font = (font_family, 9)
        italic_font = (font_family, 9, 'italic')

        self.provider_lf.config(text=t['provider_section'], font=bold_font)
        self.provider_lbl.config(text=t['provider_label'], font=default_font)

        self.api_lf.config(text=t['api_section'], font=bold_font)
        if hasattr(self, 'gemini_lbl'):
            self.gemini_lbl.config(text=t['api_label'], font=bold_font)
        if hasattr(self, 'groq_lbl'):
            self.groq_lbl.config(text=t['api_label'], font=bold_font)
        if hasattr(self, 'mistral_lbl'):
            self.mistral_lbl.config(text=t['api_label'], font=bold_font)
        
        if hasattr(self, 'gemini_link'):
            self.gemini_link.config(text=t['api_link'], font=small_font)
        if hasattr(self, 'groq_link'):
            self.groq_link.config(text=t['api_link'], font=small_font)
        if hasattr(self, 'mistral_link'):
            self.mistral_link.config(text=t['api_link'], font=small_font)

        if hasattr(self, 'gemini_btn_save'):
            self.gemini_btn_save.config(text=t['save_btn'])
        if hasattr(self, 'groq_btn_save'):
            self.groq_btn_save.config(text=t['save_btn'])
        if hasattr(self, 'mistral_btn_save'):
            self.mistral_btn_save.config(text=t['save_btn'])
        
        self.google_free_lbl.config(text=t['google_free_note'], font=italic_font)

        self.gemini_entry.config(font=default_font)
        self.gemini_model_combo.config(font=small_font)
        self.provider_combo.config(font=default_font)
