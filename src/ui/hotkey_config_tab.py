import tkinter as tk
from tkinter import ttk, messagebox
import copy
import uuid
import os
from .i18n import TRANSLATIONS, LANGUAGES
from .constants import *
from constants import (
    DEFAULT_PROVIDER,
    MODE_POPUP,
    MODE_REPLACE,
    PROVIDER_GEMINI,
    PROVIDER_GROQ,
    PROVIDER_MISTRAL,
    PROVIDER_GOOGLE_FREE,
)
from font_mapper import FontMapper

class HotkeyConfigTab:
    def __init__(self, parent_frame, config, on_save_callback, hotkey_manager, get_current_lang, get_window):
        self.parent_frame = parent_frame
        self.config = config
        self.on_save_callback = on_save_callback
        self.hotkey_manager = hotkey_manager
        self.get_current_lang = get_current_lang
        self.get_window = get_window

        self.hotkey_rows = []
        self.temp_hotkeys = copy.deepcopy(self.config.get_hotkeys())

        self._create_hotkey_section()

    def _create_hotkey_section(self):
        self.hotkey_lf = tk.LabelFrame(
            self.parent_frame, text=" ⌨ Phím tắt ",
            fg=PRIMARY, bg=BASE,
            font=('Segoe UI', 10, 'bold'),
            labelanchor='nw', padx=10, pady=8
        )
        self.hotkey_lf.pack(fill='x', padx=10, pady=4)

        header_frame = tk.Frame(self.hotkey_lf, bg=SURFACE1)
        header_frame.pack(fill='x', pady=(0, 2))

        self.th_hk = tk.Label(header_frame, text="Phím tắt", width=14, fg=TEXT_COLOR, bg=SURFACE1, font=('Segoe UI', 9, 'bold'), anchor='w')
        self.th_hk.pack(side='left', padx=2, pady=4)

        self.th_lang = tk.Label(header_frame, text="Ngôn ngữ", width=16, fg=TEXT_COLOR, bg=SURFACE1, font=('Segoe UI', 9, 'bold'), anchor='w')
        self.th_lang.pack(side='left', padx=2, pady=4)

        self.th_mode = tk.Label(header_frame, text="Chế độ", fg=TEXT_COLOR, bg=SURFACE1, font=('Segoe UI', 9, 'bold'), anchor='w')
        self.th_mode.pack(side='left', padx=2, pady=4)

        th_empty = tk.Label(header_frame, text="", width=4, fg=TEXT_COLOR, bg=SURFACE1, font=('Segoe UI', 9, 'bold'), anchor='w')
        th_empty.pack(side='left', padx=2, pady=4)

        self.hotkey_list_frame = tk.Frame(self.hotkey_lf, bg=BASE)
        self.hotkey_list_frame.pack(fill='x')

        self.hotkey_rows = []
        for hk in self.temp_hotkeys:
            self._add_hotkey_row(hk)

        self.add_btn = tk.Button(
            self.hotkey_lf, text="+ Thêm phím tắt",
            fg=PRIMARY, bg=SURFACE0,
            font=('Segoe UI', 10), bd=0,
            activebackground=SURFACE1,
            activeforeground=PRIMARY,
            cursor='hand2', padx=12, pady=4,
            command=self._show_hotkey_dialog
        )
        self.add_btn.pack(anchor='w', pady=(8, 4))

    def _add_hotkey_row(self, hk: dict):
        font_family = FontMapper.get_font(self.get_current_lang())
        default_font = (font_family, 10)
        bold_font = (font_family, 10, 'bold')

        row_frame = tk.Frame(self.hotkey_list_frame, bg=SURFACE0)
        row_frame.pack(fill='x', pady=1)

        def on_enter(e, rf=row_frame):
            rf.config(bg=SURFACE2)
            for w in rf.winfo_children():
                if w.cget('text') != '✕':
                    w.config(bg=SURFACE2)

        def on_leave(e, rf=row_frame):
            rf.config(bg=SURFACE0)
            for w in rf.winfo_children():
                if w.cget('text') != '✕':
                    w.config(bg=SURFACE0)

        row_frame.bind('<Enter>', on_enter)
        row_frame.bind('<Leave>', on_leave)

        lbl_combo = tk.Label(
            row_frame, text=hk.get('key_combo', ''),
            width=14, fg=PRIMARY, bg=SURFACE0,
            font=bold_font, anchor='w'
        )
        lbl_combo.pack(side='left', padx=2, pady=3)
        lbl_combo.bind('<Enter>', on_enter)
        lbl_combo.bind('<Leave>', on_leave)

        lbl_lang = tk.Label(
            row_frame, text=hk.get('target_language_name', ''),
            width=16, fg=TEXT_COLOR, bg=SURFACE0,
            font=default_font, anchor='w'
        )
        lbl_lang.pack(side='left', fill='x', expand=True, padx=2, pady=3)
        lbl_lang.bind('<Enter>', on_enter)
        lbl_lang.bind('<Leave>', on_leave)

        del_btn = tk.Button(
            row_frame, text='✕',
            fg=RED, bg=SURFACE0, bd=0,
            font=bold_font,
            activebackground=SURFACE1,
            cursor='hand2',
            command=lambda hid=hk.get('id'), frame=row_frame: self._delete_hotkey(hid, frame)
        )
        del_btn.pack(side='right', padx=4, pady=3)

        t = TRANSLATIONS.get(self.get_current_lang(), TRANSLATIONS['vi'])
        mode_text = t['popup_mode'] if hk.get('mode') == MODE_POPUP else t['replace_mode']
        lbl_mode = tk.Label(
            row_frame, text=mode_text,
            fg=SUBTEXT, bg=SURFACE0,
            font=default_font, anchor='w'
        )
        lbl_mode.pack(side='right', padx=2, pady=3)
        lbl_mode.bind('<Enter>', on_enter)
        lbl_mode.bind('<Leave>', on_leave)

        def on_double_click(event, hotkey_data=hk):
            self._show_hotkey_dialog(edit_hotkey_data=hotkey_data)

        row_frame.bind('<Double-Button-1>', on_double_click)
        lbl_combo.bind('<Double-Button-1>', on_double_click)
        lbl_lang.bind('<Double-Button-1>', on_double_click)
        lbl_mode.bind('<Double-Button-1>', on_double_click)

        self.hotkey_rows.append({
            'id': hk.get('id'),
            'frame': row_frame,
            'data': hk
        })

    def _delete_hotkey(self, hotkey_id: str, frame: tk.Frame):
        frame.destroy()
        self.hotkey_rows = [r for r in self.hotkey_rows if r['id'] != hotkey_id]
        self.temp_hotkeys = [hk for hk in self.temp_hotkeys if hk.get('id') != hotkey_id]
        
        self.config.data['hotkeys'] = self.temp_hotkeys
        self.config.save()
        if self.on_save_callback:
            self.on_save_callback()

    def _show_hotkey_dialog(self, edit_hotkey_data=None):
        if self.hotkey_manager:
            self.hotkey_manager.unregister_all()

        window = self.get_window()
        if not window: return
        dialog = tk.Toplevel(window)
        is_edit = edit_hotkey_data is not None
        
        lang_code = self.get_current_lang()
        t_dict = TRANSLATIONS.get(lang_code, TRANSLATIONS['vi'])
        font_family = FontMapper.get_font(lang_code)
        default_font = (font_family, 10)
        bold_font = (font_family, 10, 'bold')
        small_font = (font_family, 9)

        dialog.title(t_dict['dialog_edit_title'] if is_edit else t_dict['dialog_add_title'])
        dialog.minsize(400, 320)
        dialog.configure(bg=BASE)
        dialog.attributes('-topmost', True)
        dialog.grab_set()

        tk.Label(
            dialog, text=t_dict['dialog_press_prompt'], fg=TEXT_COLOR, bg=BASE,
            font=small_font
        ).pack(anchor='w', padx=16, pady=(16, 4))

        initial_val = edit_hotkey_data.get('key_combo', '') if is_edit else ""
        hotkey_var = tk.StringVar(value=initial_val)
        hotkey_entry = tk.Entry(
            dialog, textvariable=hotkey_var,
            bg=BASE, fg=PRIMARY,
            insertbackground=PRIMARY,
            font=(font_family, 12, 'bold'),
            relief='flat',
            justify='center',
            highlightthickness=1,
            highlightbackground=BORDER_COLOR,
            highlightcolor=PRIMARY
        )
        hotkey_entry.pack(fill='x', padx=16)

        detect_state = {'hook_id': None, 'active': False}
        pressed_keys = set()
        accumulated_keys = set()
        recorded_combo = [None]

        def start_detecting(event):
            hotkey_var.set(t_dict['dialog_recording'])
            detect_state['active'] = True
            pressed_keys.clear()
            accumulated_keys.clear()
            recorded_combo[0] = None
            
            if detect_state['hook_id']:
                try:
                    import keyboard
                    keyboard.unhook(detect_state['hook_id'])
                except Exception:
                    pass
            
            def hook_callback(e):
                if not detect_state['active']:
                    return
                name = e.name
                if not name:
                    return
                name = name.lower()
                
                if name in ('left ctrl', 'right ctrl', 'ctrl'): name = 'ctrl'
                elif name in ('left shift', 'right shift', 'shift'): name = 'shift'
                elif name in ('left alt', 'right alt', 'alt', 'alt gr'): name = 'alt'
                elif name in ('left windows', 'right windows', 'win', 'windows'): name = 'win'
                
                if len(name) == 1:
                    ascii_val = ord(name)
                    if 1 <= ascii_val <= 26:
                        name = chr(ascii_val + 96)
                
                if e.event_type == 'down':
                    pressed_keys.add(name)
                    accumulated_keys.add(name)
                elif e.event_type == 'up':
                    pressed_keys.discard(name)
                
                if accumulated_keys:
                    modifiers = []
                    main_key = None
                    
                    if 'ctrl' in accumulated_keys: modifiers.append('ctrl')
                    if 'shift' in accumulated_keys: modifiers.append('shift')
                    if 'alt' in accumulated_keys: modifiers.append('alt')
                    if 'win' in accumulated_keys: modifiers.append('win')
                    
                    for k in accumulated_keys:
                        if k not in ('ctrl', 'shift', 'alt', 'win'):
                            main_key = 'space' if k == 'space' else k
                            break
                    
                    combo_parts = modifiers.copy()
                    if main_key:
                        combo_parts.append(main_key)
                    
                    if combo_parts:
                        current_combo = "+".join(combo_parts)
                        dialog.after(0, lambda c=current_combo: hotkey_var.set(c))
                        recorded_combo[0] = current_combo
                
                if e.event_type == 'up' and not pressed_keys:
                    final_combo = recorded_combo[0]
                    if final_combo:
                        parts = final_combo.split('+')
                        has_main_key = any(p not in ('ctrl', 'shift', 'alt', 'win') for p in parts)
                        if has_main_key:
                            combo_lower = final_combo.lower()
                            is_dup = False
                            for hk in self.temp_hotkeys:
                                if (not is_edit or hk['id'] != edit_hotkey_data['id']) and hk['key_combo'].lower() == combo_lower:
                                    is_dup = True
                                    break
                            
                            if is_dup:
                                dialog.after(0, lambda: messagebox.showwarning(t_dict['dialog_dup_title'], t_dict['dialog_dup_msg'], parent=dialog))
                                dialog.after(0, lambda: hotkey_var.set(t_dict['dialog_recording']))
                                accumulated_keys.clear()
                                recorded_combo[0] = None
                            else:
                                stop_detecting()
                                dialog.after(50, lambda: lang_combo.focus_set())
                        else:
                            accumulated_keys.clear()
            
            import keyboard
            detect_state['hook_id'] = keyboard.hook(hook_callback)

        def stop_detecting(event=None):
            detect_state['active'] = False
            if detect_state['hook_id']:
                try:
                    import keyboard
                    keyboard.unhook(detect_state['hook_id'])
                except Exception:
                    pass
                detect_state['hook_id'] = None
            
            val = hotkey_var.get()
            if val == t_dict['dialog_recording']:
                hotkey_var.set(initial_val)

        hotkey_entry.bind('<FocusIn>', start_detecting)
        hotkey_entry.bind('<FocusOut>', stop_detecting)
        hotkey_entry.bind('<KeyPress>', lambda e: "break")

        tk.Label(
            dialog, text=t_dict['dialog_lang_prompt'], fg=TEXT_COLOR, bg=BASE,
            font=default_font
        ).pack(anchor='w', padx=16, pady=(16, 4))

        lang_names = [lang[0] for lang in LANGUAGES]
        default_lang_name = lang_names[0]
        if is_edit:
            old_code = edit_hotkey_data.get('target_language_code')
            for name, code in LANGUAGES:
                if code == old_code:
                    default_lang_name = name
                    break
                    
        lang_var = tk.StringVar(value=default_lang_name)
        lang_combo = ttk.Combobox(
            dialog, textvariable=lang_var,
            values=lang_names, state='readonly'
        )
        lang_combo.pack(fill='x', padx=16)

        tk.Label(
            dialog, text=t_dict['dialog_mode_prompt'], fg=TEXT_COLOR, bg=BASE,
            font=default_font
        ).pack(anchor='w', padx=16, pady=(16, 4))

        initial_mode = edit_hotkey_data.get('mode', MODE_POPUP) if is_edit else MODE_POPUP
        mode_var = tk.StringVar(value=initial_mode)
        mode_frame = tk.Frame(dialog, bg=BASE)
        mode_frame.pack(anchor='w', padx=16)

        r1 = tk.Radiobutton(
            mode_frame, text=t_dict['dialog_mode_popup'], variable=mode_var, value=MODE_POPUP,
            fg=TEXT_COLOR, bg=BASE, selectcolor=SURFACE0,
            activebackground=BASE, activeforeground=TEXT_COLOR,
            font=default_font
        )
        r1.pack(side='left', padx=(0, 16))

        r2 = tk.Radiobutton(
            mode_frame, text=t_dict['dialog_mode_replace'], variable=mode_var, value=MODE_REPLACE,
            fg=TEXT_COLOR, bg=BASE, selectcolor=SURFACE0,
            activebackground=BASE, activeforeground=TEXT_COLOR,
            font=default_font
        )
        r2.pack(side='left')

        def on_dialog_close():
            if detect_state['hook_id']:
                try:
                    import keyboard
                    keyboard.unhook(detect_state['hook_id'])
                except Exception:
                    pass
                detect_state['hook_id'] = None
            dialog.destroy()
            if self.hotkey_manager:
                self.hotkey_manager.register_all()

        def on_dialog_destroy(event):
            if event.widget == dialog and detect_state['hook_id']:
                try:
                    import keyboard
                    keyboard.unhook(detect_state['hook_id'])
                except Exception:
                    pass
                detect_state['hook_id'] = None
            
        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)
        dialog.bind("<Destroy>", on_dialog_destroy)

        btn_frame = tk.Frame(dialog, bg=BASE)
        btn_frame.pack(fill='x', padx=16, pady=(20, 16))

        def do_save():
            combo = hotkey_var.get().strip()
            if not combo or combo == t_dict['dialog_recording']:
                messagebox.showwarning(t_dict['dialog_missing_title'], t_dict['dialog_missing_info'], parent=dialog)
                return

            combo_lower = combo.lower()
            for hk in self.temp_hotkeys:
                if (not is_edit or hk['id'] != edit_hotkey_data['id']) and hk['key_combo'].lower() == combo_lower:
                    messagebox.showwarning(t_dict['dialog_dup_title'], t_dict['dialog_dup_msg'], parent=dialog)
                    return

            selected_name = lang_var.get()
            lang_code = "vi"
            lang_name = selected_name
            for name, code in LANGUAGES:
                if name == selected_name:
                    lang_code = code
                    lang_name = name
                    break

            mode = mode_var.get()

            if is_edit:
                hk_id = edit_hotkey_data['id']
                for hk in self.temp_hotkeys:
                    if hk['id'] == hk_id:
                        hk.update({
                            'key_combo': combo,
                            'target_language_code': lang_code,
                            'target_language_name': lang_name,
                            'mode': mode
                        })
                        break
                
                for r in self.hotkey_rows:
                    if r['id'] == hk_id:
                        r['frame'].destroy()
                        self.hotkey_rows.remove(r)
                        break
                
                self._add_hotkey_row({
                    'id': hk_id,
                    'key_combo': combo,
                    'target_language_code': lang_code,
                    'target_language_name': lang_name,
                    'mode': mode
                })
            else:
                hk_id = str(uuid.uuid4())
                hk_data = {
                    'id': hk_id,
                    'key_combo': combo,
                    'target_language_code': lang_code,
                    'target_language_name': lang_name,
                    'mode': mode
                }
                self.temp_hotkeys.append(hk_data)
                self._add_hotkey_row(hk_data)

            self.config.data['hotkeys'] = self.temp_hotkeys
            self.config.save()
            if self.on_save_callback:
                self.on_save_callback()

            on_dialog_close()

        save_btn_text = t_dict['dialog_save_btn'] if is_edit else t_dict['dialog_add_btn']
        tk.Button(
            btn_frame, text=save_btn_text, command=do_save,
            fg=WHITE, bg=PRIMARY,
            font=bold_font,
            relief='flat', padx=16, pady=4,
            cursor='hand2'
        ).pack(side='left', padx=(0, 8))

        tk.Button(
            btn_frame, text=t_dict['dialog_cancel_btn'], command=on_dialog_close,
            fg=TEXT_COLOR, bg=SURFACE1,
            font=default_font,
            relief='flat', padx=16, pady=4,
            cursor='hand2'
        ).pack(side='left')

    def redraw_hotkey_rows(self):
        for widget in self.hotkey_list_frame.winfo_children():
            widget.destroy()
        
        self.hotkey_rows.clear()
        for hk in self.temp_hotkeys:
            self._add_hotkey_row(hk)

    def update_ui_language(self, lang_code, font_family):
        t = TRANSLATIONS.get(lang_code, TRANSLATIONS['vi'])
        default_font = (font_family, 10)
        bold_font = (font_family, 10, 'bold')

        self.hotkey_lf.config(text=t['hotkey_section'], font=bold_font)
        self.th_hk.config(text=t['table_hk'], font=bold_font)
        self.th_lang.config(text=t['table_lang'], font=bold_font)
        self.th_mode.config(text=t['table_mode'], font=bold_font)
        self.add_btn.config(text=t['add_hk_btn'], font=default_font)

        self.redraw_hotkey_rows()
