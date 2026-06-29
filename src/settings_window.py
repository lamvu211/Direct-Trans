"""
settings_window.py - Settings UI for DirectTrans with Claude-inspired Editorial theme.
Includes API key hyperlinks, hotkey management with auto-detect, and all config options.
Supports dynamic multilingual interface (VI, EN, KO, ZH, JA) with font family mapping.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import threading
import copy
import uuid
import os
from font_mapper import FontMapper


class SettingsWindow:
    """
    Full settings UI with:
    - Translation provider dropdown (aligned to right)
    - API key entries with clickable hyperlinks to get keys (compact 2-row layout)
    - Fallback, cache, auto-start toggles
    - Hotkey table with add/edit/delete
    - Hotkey auto-detection dialog
    - Sticky header with logo and interface language dropdown
    """

    # Supported languages for hotkey target
    LANGUAGES = [
        ("Tiếng Việt", "vi"), ("English", "en"), ("中文 (Chinese)", "zh"),
        ("日本語 (Japanese)", "ja"), ("한국어 (Korean)", "ko"),
        ("Français (French)", "fr"), ("Deutsch (German)", "de"),
        ("Español (Spanish)", "es"), ("Português (Portuguese)", "pt"),
        ("Русский (Russian)", "ru"), ("Italiano (Italian)", "it"),
        ("Nederlands (Dutch)", "nl"), ("Polski (Polish)", "pl"),
        ("Türkçe (Turkish)", "tr"), ("العربية (Arabic)", "ar"),
        ("हिन्दी (Hindi)", "hi"), ("ภาษาไทย (Thai)", "th"),
        ("Bahasa Indonesia", "id"), ("Bahasa Melayu", "ms"),
        ("Tiếng Lào (Lao)", "lo"), ("ភាសាខ្mែរ (Khmer)", "km"),
        ("Burmese", "my"), ("Filipino", "fil"),
        ("Svenska (Swedish)", "sv"), ("Norsk (Norwegian)", "no"),
        ("Dansk (Danish)", "da"), ("Suomi (Finnish)", "fi"),
        ("Čeština (Czech)", "cs"), ("Română (Romanian)", "ro"),
        ("Magyar (Hungarian)", "hu"), ("Ελληνικά (Greek)", "el"),
        ("עברית (Hebrew)", "he"), ("فارسی (Persian)", "fa"),
        ("Українська (Ukrainian)", "uk"), ("Български (Bulgarian)", "bg"),
    ]

    PROVIDERS = [("Gemini", "gemini"), ("GroqCloud", "groq"), ("Mistral", "mistral"), ("Google Free", "google_free")]

    # Apple Design Colors
    BASE = '#ffffff'          # Canvas background (Pure White)
    MANTLE = '#f5f5f7'        # Sticky Header background (Parchment)
    CRUST = '#e0e0e0'         # Border color for elements (Hairline)
    SURFACE0 = '#f5f5f7'      # Surface-soft/parchment (row backgrounds)
    SURFACE1 = '#fafafc'      # Button neutral background (Pearl)
    SURFACE2 = '#e0e0e0'      # Highlight/Hover background (Hairline)
    TEXT_COLOR = '#1d1d1f'    # Primary headlines and body (Ink)
    SUBTEXT = '#7a7a7a'       # Secondary text (Ink Muted 48)
    PRIMARY = '#0066cc'       # Primary action color (Action Blue)
    RED = '#ff453a'           # Error state (System Red)
    YELLOW = '#ff9f0a'        # Accent yellow/orange (System Orange)
    BORDER_COLOR = '#d2d2d7'  # Input border color (Hairline Strong)

    # Interface translation dictionary
    TRANSLATIONS = {
        'vi': {
            'title': 'DirectTrans',
            'provider_section': ' Nguồn dịch ',
            'provider_label': 'Provider:',
            'api_section': ' 🔑 API Keys ',
            'api_label': 'API key:',
            'api_link': '🔗 Lấy API key',
            'model_label': 'Model:',
            'load_models': '↻ Load Models',
            'test_btn': 'Test',
            'save_btn': 'Lưu Key',
            'google_free_note': 'ℹ Google Free không cần API key',
            'options_section': ' Tùy chọn ',
            'autostart_label': 'Khởi động cùng Windows',
            'hotkey_section': ' ⌨ Phím tắt ',
            'table_hk': 'Phím tắt',
            'table_lang': 'Ngôn ngữ',
            'table_mode': 'Chế độ',
            'add_hk_btn': '+ Thêm phím tắt',
            'popup_mode': '📋 popup',
            'replace_mode': '✏ replace',
            'save_success': 'Đã lưu',
            'save_empty': 'Trống',
            'test_running': '⏳...',
            'test_pass': 'Pass',
            'test_fail': 'Fail',
            'net_error': 'Lỗi mạng',
            'dialog_add_title': 'Thêm phím tắt',
            'dialog_edit_title': 'Sửa phím tắt',
            'dialog_press_prompt': 'Nhấn tổ hợp phím (Nhấp chuột vào ô để thu âm phím):',
            'dialog_lang_prompt': 'Ngôn ngữ đích:',
            'dialog_mode_prompt': 'Chế độ:',
            'dialog_mode_popup': '📋 Popup (hiện kết quả)',
            'dialog_mode_replace': '✏ Replace (thay thế text)',
            'dialog_save_btn': 'Lưu',
            'dialog_add_btn': 'Thêm',
            'dialog_cancel_btn': 'Hủy',
            'dialog_missing_info': 'Vui lòng nhập tổ hợp phím.',
            'dialog_dup_title': 'Trùng phím tắt',
            'dialog_dup_msg': 'phím tắt đã được sử dụng',
            'dialog_recording': 'Đang chờ nhập phím...',
            'dialog_missing_title': 'Thiếu thông tin'
        },
        'en': {
            'title': 'DirectTrans',
            'provider_section': ' Translation Source ',
            'provider_label': 'Provider:',
            'api_section': ' 🔑 API Keys ',
            'api_label': 'API key:',
            'api_link': '🔗 Get API key',
            'model_label': 'Model:',
            'load_models': '↻ Load Models',
            'test_btn': 'Test',
            'save_btn': 'Save Key',
            'google_free_note': 'ℹ Google Free does not require an API key',
            'options_section': ' Options ',
            'autostart_label': 'Start with Windows',
            'hotkey_section': ' ⌨ Hotkeys ',
            'table_hk': 'Hotkey',
            'table_lang': 'Language',
            'table_mode': 'Mode',
            'add_hk_btn': '+ Add Hotkey',
            'popup_mode': '📋 popup',
            'replace_mode': '✏ replace',
            'save_success': 'Saved',
            'save_empty': 'Empty',
            'test_running': '⏳...',
            'test_pass': 'Pass',
            'test_fail': 'Fail',
            'net_error': 'Net Error',
            'dialog_add_title': 'Add Hotkey',
            'dialog_edit_title': 'Edit Hotkey',
            'dialog_press_prompt': 'Press hotkey combination (Click the box to record keys):',
            'dialog_lang_prompt': 'Target Language:',
            'dialog_mode_prompt': 'Mode:',
            'dialog_mode_popup': '📋 Popup (show results)',
            'dialog_mode_replace': '✏ Replace (replace text)',
            'dialog_save_btn': 'Save',
            'dialog_add_btn': 'Add',
            'dialog_cancel_btn': 'Cancel',
            'dialog_missing_info': 'Please enter a hotkey combination.',
            'dialog_dup_title': 'Duplicate Hotkey',
            'dialog_dup_msg': 'This hotkey combo is already in use.',
            'dialog_recording': 'Waiting for keys...',
            'dialog_missing_title': 'Missing Info'
        },
        'ko': {
            'title': 'DirectTrans',
            'provider_section': ' 번역 소스 ',
            'provider_label': '제공자:',
            'api_section': ' 🔑 API 키 ',
            'api_label': 'API key:',
            'api_link': '🔗 API 키 받기',
            'model_label': '모델:',
            'load_models': '↻ 모델 로드',
            'test_btn': '테스트',
            'save_btn': '키 저장',
            'google_free_note': 'ℹ Google Free는 API 키가 필요하지 않습니다',
            'options_section': ' 옵션 ',
            'autostart_label': 'Windows와 함께 시작',
            'hotkey_section': ' ⌨ 단축키 ',
            'table_hk': '단축키',
            'table_lang': '언어',
            'table_mode': '모드',
            'add_hk_btn': '+ 단축키 추가',
            'popup_mode': '📋 팝업',
            'replace_mode': '✏ 바꾸기',
            'save_success': '저장됨',
            'save_empty': '비어 있음',
            'test_running': '⏳...',
            'test_pass': '통과',
            'test_fail': '실패',
            'net_error': '네트워크 오류',
            'dialog_add_title': '단축키 추가',
            'dialog_edit_title': '단축키 수정',
            'dialog_press_prompt': '단축키 입력 (텍스트 박스를 클릭하여 단축키 녹음):',
            'dialog_lang_prompt': '대상 언어:',
            'dialog_mode_prompt': '모드:',
            'dialog_mode_popup': '📋 팝업 (결과 표시)',
            'dialog_mode_replace': '✏ 바꾸기 (텍스트 교체)',
            'dialog_save_btn': '저장',
            'dialog_add_btn': '추가',
            'dialog_cancel_btn': '취소',
            'dialog_missing_info': '단축키 조합을 입력해 주세요.',
            'dialog_dup_title': '단축키 중복',
            'dialog_dup_msg': '이 단축키 조합은 이미 사용 중입니다.',
            'dialog_recording': '키 입력 대기 중...',
            'dialog_missing_title': '정보 누락'
        },
        'zh': {
            'title': 'DirectTrans',
            'provider_section': ' 翻译源 ',
            'provider_label': '服务商:',
            'api_section': ' 🔑 API 密钥 ',
            'api_label': 'API key:',
            'api_link': '🔗 获取 API 密钥',
            'model_label': '模型:',
            'load_models': '↻ 加载模型',
            'test_btn': '测试',
            'save_btn': '保存密钥',
            'google_free_note': 'ℹ Google Free 不需要 API 密钥',
            'options_section': ' 选项 ',
            'autostart_label': '开机自启动',
            'hotkey_section': ' ⌨ 快捷键 ',
            'table_hk': '快捷键',
            'table_lang': '语言',
            'table_mode': '模式',
            'add_hk_btn': '+ 添加快捷键',
            'popup_mode': '📋 弹窗',
            'replace_mode': '✏ 替换',
            'save_success': '已保存',
            'save_empty': '为空',
            'test_running': '⏳...',
            'test_pass': '通过',
            'test_fail': '失败',
            'net_error': '网络错误',
            'dialog_add_title': '添加快捷键',
            'dialog_edit_title': '编辑快捷键',
            'dialog_press_prompt': '按下快捷键组合 (点击输入框进行录入):',
            'dialog_lang_prompt': '目标语言:',
            'dialog_mode_prompt': '模式:',
            'dialog_mode_popup': '📋 弹窗 (显示结果)',
            'dialog_mode_replace': '✏ 替换 (替换文本)',
            'dialog_save_btn': '保存',
            'dialog_add_btn': '添加',
            'dialog_cancel_btn': '取消',
            'dialog_missing_info': '请输入快捷键组合。',
            'dialog_dup_title': '快捷键冲突',
            'dialog_dup_msg': '此快捷键组合已被占用。',
            'dialog_recording': '正在等待输入...',
            'dialog_missing_title': '缺少信息'
        },
        'ja': {
            'title': 'DirectTrans',
            'provider_section': ' 翻訳ソース ',
            'provider_label': 'プロバイダー:',
            'api_section': ' 🔑 API キー ',
            'api_label': 'API key:',
            'api_link': '🔗 API キーを取得',
            'model_label': 'モデル:',
            'load_models': '↻ モデル読み込み',
            'test_btn': 'テスト',
            'save_btn': 'キー保存',
            'google_free_note': 'ℹ Google Free は API キー不要です',
            'options_section': ' オプション ',
            'autostart_label': 'Windows 起動時に実行',
            'hotkey_section': ' ⌨ ショートカットキー ',
            'table_hk': 'ショートカット',
            'table_lang': '言語',
            'table_mode': 'モード',
            'add_hk_btn': '+ ショートカットを追加',
            'popup_mode': '📋 ポップアップ',
            'replace_mode': '✏ 置換',
            'save_success': '保存完了',
            'save_empty': '空欄',
            'test_running': '⏳...',
            'test_pass': '合格',
            'test_fail': '不合格',
            'net_error': 'ネットエラー',
            'dialog_add_title': 'ショートカットを追加',
            'dialog_edit_title': 'ショートカットの編集',
            'dialog_press_prompt': 'キーコンビネーションを入力 (クリックしてキーを録音):',
            'dialog_lang_prompt': '対象言語:',
            'dialog_mode_prompt': 'モード:',
            'dialog_mode_popup': '📋 ポップアップ (結果表示)',
            'dialog_mode_replace': '✏ 置換 (テキスト置き換え)',
            'dialog_save_btn': '保存',
            'dialog_add_btn': '追加',
            'dialog_cancel_btn': 'キャンセル',
            'dialog_missing_info': 'キーコンビネーションを入力してください。',
            'dialog_dup_title': '重複するショートカット',
            'dialog_dup_msg': 'このショートカットは既に使用されています。',
            'dialog_recording': 'キーの入力を待っています...',
            'dialog_missing_title': '情報不足'
        }
    }

    def __init__(self, root, config, on_save_callback, on_close_callback=None, hotkey_manager=None):
        self.root = root
        self.config = config
        self.on_save_callback = on_save_callback
        self.on_close_callback = on_close_callback
        self.hotkey_manager = hotkey_manager
        self.window = None

        # UI state variables
        self.provider_var = None
        self.gemini_entry = None
        self.autostart_var = None
        self.hotkey_rows = []  # list of dicts for current hotkeys in UI
        self.temp_hotkeys = copy.deepcopy(self.config.get_hotkeys())
        self.current_lang = self.config.data.get('ui_language', 'vi')

        # Keeps strong reference to PhotoImage to prevent garbage collection
        self.logo_img = None

    def _on_minimize(self, event):
        import logging
        if event.widget == self.window and self.window.state() == 'iconic':
            logging.info("Settings window minimized. Withdrawing to tray.")
            self.window.withdraw()

    def restore_and_focus(self):
        if self.window and self.window.winfo_exists():
            self.window.deiconify()
            self.window.state('normal')
            self.window.attributes('-topmost', True)
            self.window.focus_force()

    def show(self):
        """Build and display the settings window."""
        self.window = tk.Toplevel(self.root)
        self.window.title("DirectTrans Settings v1.0")
        self.window.geometry("580x630")
        self.window.resizable(True, True)
        self.window.minsize(580, 500)
        self.window.configure(bg=self.BASE)
        self.window.attributes('-topmost', True)
        self.window.after(200, lambda: self.window.attributes('-topmost', False))
        self.window.bind("<Unmap>", self._on_minimize)

        # Try to set app taskbar icon
        try:
            icon_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 'assets', 'icon.ico'
            )
            if os.path.exists(icon_path):
                self.window.iconbitmap(icon_path)
        except Exception:
            pass

        # 1. Create Sticky Header (packed directly to self.window to keep it fixed at top)
        self._create_header()

        # 2. Scrollable canvas for content (packed below header)
        canvas = tk.Canvas(self.window, bg=self.BASE, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.window, orient='vertical', command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=self.BASE)

        self.scroll_frame.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )

        canvas_window_id = canvas.create_window((0, 0), window=self.scroll_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        # Keep inner scroll_frame width matched to the canvas width to prevent right gap
        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_window_id, width=event.width)
        canvas.bind('<Configure>', _on_canvas_configure)

        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)

        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)

        # Unbind mousewheel on close
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

        # Build sections inside scroll_frame
        self._create_provider_section()
        self._create_api_section()
        self._create_options_section()
        self._create_hotkey_section()

        # Sync interface language and fonts
        try:
            self.update_ui_language(self.config.data.get('ui_language', 'vi'))
        except Exception as e:
            import logging
            logging.warning(f"Failed to apply UI language font: {e}")

    def _create_header(self):
        """Sticky app header containing Logo, Title, Info link, and Language Selection."""
        header = tk.Frame(self.window, bg=self.MANTLE, pady=8)
        header.pack(fill='x', padx=0, pady=0)  # zero margin, flush to top

        # Top row container for Logo + Title
        top_row = tk.Frame(header, bg=self.MANTLE)
        top_row.pack(fill='x', padx=10, pady=(0, 6))

        # Load logo-direct-trans.png with PIL and fallback to unicode if needed
        logo_loaded = False
        logo_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'assets', 'logo-direct-trans.png'
        )
        # Fallback to parent directory just in case
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

                logo_lbl = tk.Label(top_row, image=self.logo_img, bg=self.MANTLE)
                logo_lbl.pack(side='left', padx=(0, 6))
                logo_loaded = True
            except Exception as e:
                import logging
                logging.error(f"Failed to load/resize logo image: {e}")

        if not logo_loaded:
            # Fallback to standard gear character
            logo_lbl = tk.Label(
                top_row, text="⚙", fg=self.PRIMARY, bg=self.MANTLE,
                font=('Segoe UI', 12, 'bold')
            )
            logo_lbl.pack(side='left', padx=(0, 6))

        # Title Label
        self.title_label = tk.Label(
            top_row, text="DirectTrans",
            fg=self.TEXT_COLOR, bg=self.MANTLE,
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
                online_url = 'https://github.com/nguyenthanh-viet/direct-trans'
                webbrowser.open(online_url)
                
        # Bottom row container for controls
        bottom_row = tk.Frame(header, bg=self.MANTLE)
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
            fg='#ffffff', bg=self.PRIMARY, bd=0, cursor='hand2', font=('Segoe UI', 9, 'bold'),
            padx=16, pady=2,
            command=open_user_manual
        )
        self.manual_btn.pack(side='left', padx=(0, 6))

        self.update_btn = tk.Button(
            bottom_row, text="Update",
            fg='#ffffff', bg=self.PRIMARY, bd=0, cursor='hand2', font=('Segoe UI', 9, 'bold'),
            padx=16, pady=2
        )
        self.update_btn.pack(side='left')

        def on_ui_lang_selected(event):
            selected_name = self.ui_lang_var.get()
            lang_code = ui_lang_map.get(selected_name, 'vi')
            self.update_ui_language(lang_code)
            if self.on_save_callback:
                self.on_save_callback()

        self.lang_ui_combo.bind("<<ComboboxSelected>>", on_ui_lang_selected)

    def _create_provider_section(self):
        """Translation provider dropdown (aligned to right edge)."""
        self.provider_lf = tk.LabelFrame(
            self.scroll_frame, text=" Nguồn dịch ",
            fg=self.PRIMARY, bg=self.BASE,
            font=('Segoe UI', 10, 'bold'),
            labelanchor='nw', padx=10, pady=8
        )
        self.provider_lf.pack(fill='x', padx=10, pady=(0, 4))

        row = tk.Frame(self.provider_lf, bg=self.BASE)
        row.pack(fill='x')

        self.provider_lbl = tk.Label(
            row, text="Provider:", fg=self.TEXT_COLOR, bg=self.BASE,
            font=('Segoe UI', 10)
        )
        self.provider_lbl.pack(side='left')

        self.provider_var = tk.StringVar(value=self.config.get_provider())

        provider_names = [p[0] for p in self.PROVIDERS]
        provider_map_local = {p[0]: p[1] for p in self.PROVIDERS}
        reverse_map = {p[1]: p[0] for p in self.PROVIDERS}

        self.provider_var.set(reverse_map.get(self.config.get_provider(), "Gemini"))

        # Right-aligned dropdown matching language selector width
        self.provider_combo = ttk.Combobox(
            row, textvariable=self.provider_var,
            values=provider_names, state='readonly', width=14
        )
        self.provider_combo.pack(side='right')

        def on_provider_selected(event):
            provider_name = self.provider_var.get()
            provider_key = provider_map_local.get(provider_name, 'gemini')
            self.config.data['translation_provider'] = provider_key
            self.config.save()
            if hasattr(self, 'update_api_frame_visibility'):
                self.update_api_frame_visibility(provider_key)
            if self.on_save_callback:
                self.on_save_callback()
        self.provider_combo.bind("<<ComboboxSelected>>", on_provider_selected)

    def update_api_frame_visibility(self, provider_key):
        # Hide all frames
        for key, frame in self.api_frames.items():
            frame.pack_forget()
        
        # Show the selected frame
        if provider_key in self.api_frames:
            if provider_key == 'google_free':
                self.api_frames[provider_key].pack(anchor='w', pady=(4, 0))
            else:
                self.api_frames[provider_key].pack(fill='x', pady=(2, 4))

    def _create_api_section(self):
        """API keys section with dynamic frames based on selected provider."""
        t = self.TRANSLATIONS.get(self.current_lang, self.TRANSLATIONS['vi'])
        self.api_lf = tk.LabelFrame(
            self.scroll_frame, text=" 🔑 API Keys ",
            fg=self.PRIMARY, bg=self.BASE,
            font=('Segoe UI', 10, 'bold'),
            labelanchor='nw', padx=10, pady=8
        )
        self.api_lf.pack(fill='x', padx=10, pady=4)

        self.api_frames = {}

        def _fetch_provider_models(provider, api_key, combo, btn_fetch, btn_save, btn_test):
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
                if provider == 'mistral':
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
                if not self.window.winfo_exists(): return
                btn_fetch.config(state=btn_state)
                btn_save.config(state=btn_state)
                btn_test.config(state=btn_state)
                combo.config(state=combo_state)

            def fetch():
                self.window.after(0, lambda: set_ui_state('disabled', 'disabled'))
                self.window.after(0, lambda: combo.set("Fetching...") if self.window.winfo_exists() else None)
                
                try:
                    if provider == 'gemini':
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
                    elif provider == 'groq':
                        url = "https://api.groq.com/openai/v1/models"
                        resp = requests.get(url, headers={"Authorization": f"Bearer {api_key}", "User-Agent": "Mozilla/5.0"}, timeout=10)
                        if resp.status_code == 200:
                            models = [m['id'] for m in resp.json().get('data', []) if is_valid_translation_model(m['id'])]
                        else:
                            models = []
                    elif provider == 'mistral':
                        url = "https://api.mistral.ai/v1/models"
                        resp = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
                        if resp.status_code == 200:
                            models = [m['id'] for m in resp.json().get('data', []) if is_valid_translation_model(m['id'])]
                        else:
                            models = []
                    
                    if models:
                        def update_success():
                            if not self.window.winfo_exists(): return
                            combo['values'] = models
                            current = getattr(self.config, f"get_{provider}_model")()
                            if current in models:
                                combo.set(current)
                            else:
                                combo.set(models[0])
                                getattr(self.config, f"set_{provider}_model")(models[0])
                            set_ui_state('normal', 'readonly')
                        self.window.after(0, update_success)
                    else:
                        def update_fail():
                            if not self.window.winfo_exists(): return
                            combo.set("Load Failed")
                            set_ui_state('normal', 'readonly')
                        self.window.after(0, update_fail)
                except Exception:
                    def update_exc():
                        if not self.window.winfo_exists(): return
                        combo.set("Load Failed")
                        set_ui_state('normal', 'readonly')
                    self.window.after(0, update_exc)

            threading.Thread(target=fetch, daemon=True).start()

        # Gemini Frame
        gemini_frame = tk.Frame(self.api_lf, bg=self.BASE)
        gemini_frame.columnconfigure(1, weight=1)
        
        # Row 0: API Key
        self.gemini_lbl = tk.Label(gemini_frame, text="API key:", fg=self.TEXT_COLOR, bg=self.BASE, font=('Segoe UI', 10, 'bold'))
        self.gemini_lbl.grid(row=0, column=0, sticky='w', pady=2)
        
        gemini_entry_frame = tk.Frame(gemini_frame, bg='#ffffff', highlightthickness=1, highlightbackground=self.BORDER_COLOR, highlightcolor=self.PRIMARY)
        gemini_entry_frame.grid(row=0, column=1, sticky='ew', padx=(8, 4), pady=2)
        
        self.gemini_entry = tk.Entry(gemini_entry_frame, show='•', bg='#ffffff', fg=self.TEXT_COLOR, insertbackground=self.TEXT_COLOR, font=('Segoe UI', 10), relief='flat', bd=0)
        gemini_btn_clear = tk.Label(gemini_entry_frame, text="✕", fg=self.SUBTEXT, bg='#ffffff', font=('Segoe UI', 9), cursor='hand2')
        gemini_btn_clear.pack(side='right', padx=(4, 4))
        
        self.gemini_entry.pack(side='left', fill='x', expand=True, padx=(4, 0), pady=2)
        self.gemini_entry.insert(0, self.config.get_api_key('gemini'))
        gemini_btn_clear.bind("<Button-1>", lambda e, e_w=self.gemini_entry: (e_w.delete(0, tk.END), self.on_save_callback() if self.on_save_callback else None))

        gemini_btn_fetch = tk.Button(gemini_frame, text="↻ Load Models", fg=self.PRIMARY, bg=self.BASE, bd=0, font=('Segoe UI', 8), cursor='hand2')
        gemini_btn_fetch.grid(row=0, column=2, sticky='w', padx=(4, 4), pady=2)

        self.gemini_link = tk.Label(gemini_frame, text="🔗 Lấy API key", fg=self.PRIMARY, bg=self.BASE, cursor='hand2', font=('Segoe UI', 9, 'underline'))
        self.gemini_link.grid(row=0, column=3, columnspan=2, sticky='e', padx=(4, 0), pady=2)
        self.gemini_link.bind('<Button-1>', lambda e: webbrowser.open('https://aistudio.google.com/app/apikey'))

        # Row 1: Model
        tk.Label(gemini_frame, text="Model:", fg=self.TEXT_COLOR, bg=self.BASE, font=('Segoe UI', 9)).grid(row=1, column=0, sticky='w', pady=2)
        
        current_gemini_model = self.config.get_gemini_model()
        self.gemini_model_combo = ttk.Combobox(gemini_frame, values=[current_gemini_model], state='readonly', width=32, font=('Segoe UI', 9))
        self.gemini_model_combo.set(current_gemini_model)
        self.gemini_model_combo.grid(row=1, column=1, sticky='ew', padx=(8, 4), pady=2)
        self.gemini_model_combo.bind("<<ComboboxSelected>>", lambda e: (self.config.set_gemini_model(self.gemini_model_combo.get()), self.on_save_callback() if self.on_save_callback else None))

        gemini_btn_test = tk.Button(gemini_frame, text="Test", fg=self.TEXT_COLOR, bg=self.SURFACE1, bd=0, font=('Segoe UI', 9), padx=8, pady=2, cursor='hand2')
        gemini_btn_test.grid(row=1, column=2, sticky='w', padx=(4, 4), pady=2)

        self.gemini_status_lbl = tk.Label(gemini_frame, text="", fg=self.TEXT_COLOR, bg=self.BASE, font=('Segoe UI', 9, 'bold'), anchor='e', width=10)
        self.gemini_status_lbl.grid(row=1, column=3, sticky='e', padx=(4, 4), pady=2)

        self.gemini_btn_save = tk.Button(gemini_frame, text=t['save_btn'], fg='#ffffff', bg=self.PRIMARY, bd=0, font=('Segoe UI', 9, 'bold'), padx=8, pady=2, cursor='hand2')
        self.gemini_btn_save.grid(row=1, column=4, sticky='e', padx=(4, 0), pady=2)

        self.gemini_btn_save.config(command=lambda: self._quick_save_key('gemini', self.gemini_entry.get().strip(), self.gemini_status_lbl))
        gemini_btn_test.config(command=lambda: self._test_key('gemini', self.gemini_entry.get().strip(), self.gemini_status_lbl, self.gemini_model_combo, gemini_btn_fetch, self.gemini_btn_save, gemini_btn_test))
        gemini_btn_fetch.config(command=lambda bf=gemini_btn_fetch, bs=self.gemini_btn_save, bt=gemini_btn_test: _fetch_provider_models('gemini', self.gemini_entry.get().strip(), self.gemini_model_combo, bf, bs, bt))

        self.api_frames['gemini'] = gemini_frame

        # GroqCloud Frame
        groq_frame = tk.Frame(self.api_lf, bg=self.BASE)
        groq_frame.columnconfigure(1, weight=1)
        
        # Row 0: API Key
        self.groq_lbl = tk.Label(groq_frame, text="API key:", fg=self.TEXT_COLOR, bg=self.BASE, font=('Segoe UI', 10, 'bold'))
        self.groq_lbl.grid(row=0, column=0, sticky='w', pady=2)
        
        groq_entry_frame = tk.Frame(groq_frame, bg='#ffffff', highlightthickness=1, highlightbackground=self.BORDER_COLOR, highlightcolor=self.PRIMARY)
        groq_entry_frame.grid(row=0, column=1, sticky='ew', padx=(8, 4), pady=2)
        
        self.groq_entry = tk.Entry(groq_entry_frame, show='•', bg='#ffffff', fg=self.TEXT_COLOR, insertbackground=self.TEXT_COLOR, font=('Segoe UI', 10), relief='flat', bd=0)
        groq_btn_clear = tk.Label(groq_entry_frame, text="✕", fg=self.SUBTEXT, bg='#ffffff', font=('Segoe UI', 9), cursor='hand2')
        groq_btn_clear.pack(side='right', padx=(4, 4))
        
        self.groq_entry.pack(side='left', fill='x', expand=True, padx=(4, 0), pady=2)
        self.groq_entry.insert(0, self.config.get_api_key('groq'))
        groq_btn_clear.bind("<Button-1>", lambda e, e_w=self.groq_entry: (e_w.delete(0, tk.END), self.on_save_callback() if self.on_save_callback else None))

        groq_btn_fetch = tk.Button(groq_frame, text="↻ Load Models", fg=self.PRIMARY, bg=self.BASE, bd=0, font=('Segoe UI', 8), cursor='hand2')
        groq_btn_fetch.grid(row=0, column=2, sticky='w', padx=(4, 4), pady=2)

        groq_link = tk.Label(groq_frame, text="🔗 Lấy API key", fg=self.PRIMARY, bg=self.BASE, cursor='hand2', font=('Segoe UI', 9, 'underline'))
        groq_link.grid(row=0, column=3, columnspan=2, sticky='e', padx=(4, 0), pady=2)
        groq_link.bind('<Button-1>', lambda e: webbrowser.open('https://console.groq.com/keys'))

        # Row 1: Model
        tk.Label(groq_frame, text="Model:", fg=self.TEXT_COLOR, bg=self.BASE, font=('Segoe UI', 9)).grid(row=1, column=0, sticky='w', pady=2)
        
        current_groq_model = self.config.get_groq_model()
        self.groq_model_combo = ttk.Combobox(groq_frame, values=[current_groq_model], state='readonly', width=32, font=('Segoe UI', 9))
        self.groq_model_combo.set(current_groq_model)
        self.groq_model_combo.grid(row=1, column=1, sticky='ew', padx=(8, 4), pady=2)
        self.groq_model_combo.bind("<<ComboboxSelected>>", lambda e: (self.config.set_groq_model(self.groq_model_combo.get()), self.on_save_callback() if self.on_save_callback else None))

        groq_btn_test = tk.Button(groq_frame, text="Test", fg=self.TEXT_COLOR, bg=self.SURFACE1, bd=0, font=('Segoe UI', 9), padx=8, pady=2, cursor='hand2')
        groq_btn_test.grid(row=1, column=2, sticky='w', padx=(4, 4), pady=2)

        self.groq_status_lbl = tk.Label(groq_frame, text="", fg=self.TEXT_COLOR, bg=self.BASE, font=('Segoe UI', 9, 'bold'), anchor='e', width=10)
        self.groq_status_lbl.grid(row=1, column=3, sticky='e', padx=(4, 4), pady=2)

        self.groq_btn_save = tk.Button(groq_frame, text=t['save_btn'], fg='#ffffff', bg=self.PRIMARY, bd=0, font=('Segoe UI', 9, 'bold'), padx=8, pady=2, cursor='hand2')
        self.groq_btn_save.grid(row=1, column=4, sticky='e', padx=(4, 0), pady=2)

        self.groq_btn_save.config(command=lambda: self._quick_save_key('groq', self.groq_entry.get().strip(), self.groq_status_lbl))
        groq_btn_test.config(command=lambda: self._test_key('groq', self.groq_entry.get().strip(), self.groq_status_lbl, self.groq_model_combo, groq_btn_fetch, self.groq_btn_save, groq_btn_test))
        groq_btn_fetch.config(command=lambda bf=groq_btn_fetch, bs=self.groq_btn_save, bt=groq_btn_test: _fetch_provider_models('groq', self.groq_entry.get().strip(), self.groq_model_combo, bf, bs, bt))

        self.api_frames['groq'] = groq_frame

        # Mistral Frame
        mistral_frame = tk.Frame(self.api_lf, bg=self.BASE)
        mistral_frame.columnconfigure(1, weight=1)
        
        # Row 0: API Key
        self.mistral_lbl = tk.Label(mistral_frame, text="API key:", fg=self.TEXT_COLOR, bg=self.BASE, font=('Segoe UI', 10, 'bold'))
        self.mistral_lbl.grid(row=0, column=0, sticky='w', pady=2)
        
        mistral_entry_frame = tk.Frame(mistral_frame, bg='#ffffff', highlightthickness=1, highlightbackground=self.BORDER_COLOR, highlightcolor=self.PRIMARY)
        mistral_entry_frame.grid(row=0, column=1, sticky='ew', padx=(8, 4), pady=2)
        
        self.mistral_entry = tk.Entry(mistral_entry_frame, show='•', bg='#ffffff', fg=self.TEXT_COLOR, insertbackground=self.TEXT_COLOR, font=('Segoe UI', 10), relief='flat', bd=0)
        mistral_btn_clear = tk.Label(mistral_entry_frame, text="✕", fg=self.SUBTEXT, bg='#ffffff', font=('Segoe UI', 9), cursor='hand2')
        mistral_btn_clear.pack(side='right', padx=(4, 4))
        
        self.mistral_entry.pack(side='left', fill='x', expand=True, padx=(4, 0), pady=2)
        self.mistral_entry.insert(0, self.config.get_api_key('mistral'))
        mistral_btn_clear.bind("<Button-1>", lambda e, e_w=self.mistral_entry: (e_w.delete(0, tk.END), self.on_save_callback() if self.on_save_callback else None))

        mistral_btn_fetch = tk.Button(mistral_frame, text="↻ Load Models", fg=self.PRIMARY, bg=self.BASE, bd=0, font=('Segoe UI', 8), cursor='hand2')
        mistral_btn_fetch.grid(row=0, column=2, sticky='w', padx=(4, 4), pady=2)

        mistral_link = tk.Label(mistral_frame, text="🔗 Lấy API key", fg=self.PRIMARY, bg=self.BASE, cursor='hand2', font=('Segoe UI', 9, 'underline'))
        mistral_link.grid(row=0, column=3, columnspan=2, sticky='e', padx=(4, 0), pady=2)
        mistral_link.bind('<Button-1>', lambda e: webbrowser.open('https://console.mistral.ai/api-keys'))

        # Row 1: Model
        tk.Label(mistral_frame, text="Model:", fg=self.TEXT_COLOR, bg=self.BASE, font=('Segoe UI', 9)).grid(row=1, column=0, sticky='w', pady=2)
        
        current_mistral_model = self.config.get_mistral_model()
        self.mistral_model_combo = ttk.Combobox(mistral_frame, values=[current_mistral_model], state='readonly', width=32, font=('Segoe UI', 9))
        self.mistral_model_combo.set(current_mistral_model)
        self.mistral_model_combo.grid(row=1, column=1, sticky='ew', padx=(8, 4), pady=2)
        self.mistral_model_combo.bind("<<ComboboxSelected>>", lambda e: (self.config.set_mistral_model(self.mistral_model_combo.get()), self.on_save_callback() if self.on_save_callback else None))

        mistral_btn_test = tk.Button(mistral_frame, text="Test", fg=self.TEXT_COLOR, bg=self.SURFACE1, bd=0, font=('Segoe UI', 9), padx=8, pady=2, cursor='hand2')
        mistral_btn_test.grid(row=1, column=2, sticky='w', padx=(4, 4), pady=2)

        self.mistral_status_lbl = tk.Label(mistral_frame, text="", fg=self.TEXT_COLOR, bg=self.BASE, font=('Segoe UI', 9, 'bold'), anchor='e', width=10)
        self.mistral_status_lbl.grid(row=1, column=3, sticky='e', padx=(4, 4), pady=2)

        mistral_btn_save = tk.Button(mistral_frame, text="Lưu Key", fg='#ffffff', bg=self.PRIMARY, bd=0, font=('Segoe UI', 9, 'bold'), padx=8, pady=2, cursor='hand2')
        mistral_btn_save.grid(row=1, column=4, sticky='e', padx=(4, 0), pady=2)

        mistral_btn_save.config(command=lambda: self._quick_save_key('mistral', self.mistral_entry.get().strip(), self.mistral_status_lbl))
        mistral_btn_test.config(command=lambda: self._test_key('mistral', self.mistral_entry.get().strip(), self.mistral_status_lbl, self.mistral_model_combo, mistral_btn_fetch, mistral_btn_save, mistral_btn_test))
        mistral_btn_fetch.config(command=lambda bf=mistral_btn_fetch, bs=mistral_btn_save, bt=mistral_btn_test: _fetch_provider_models('mistral', self.mistral_entry.get().strip(), self.mistral_model_combo, bf, bs, bt))

        self.api_frames['mistral'] = mistral_frame


        # 4. Google Free Note
        self.google_free_lbl = tk.Label(
            self.api_lf,
            text="ℹ Google Free không cần API key",
            fg=self.SUBTEXT, bg=self.BASE,
            font=('Segoe UI', 9, 'italic')
        )
        self.api_frames['google_free'] = self.google_free_lbl

        # Init visibility
        self.update_api_frame_visibility(self.config.get_provider())

    def _quick_save_key(self, provider: str, key: str, status_lbl: tk.Label):


        """Save API Key quickly without closing settings."""
        self.config.set_api_key(provider, key)
        t = self.TRANSLATIONS[self.current_lang]
        status_lbl.config(text=t['save_success'], fg='#5db872')
        self.window.after(1500, lambda: status_lbl.config(text=""))
        if self.on_save_callback:
            self.on_save_callback()

    def _test_key(self, provider: str, key: str, status_lbl: tk.Label, combo: ttk.Combobox = None, btn_fetch: tk.Button = None, btn_save: tk.Button = None, btn_test: tk.Button = None):
        """Test API key asynchronously on a separate thread."""
        t_dict = self.TRANSLATIONS[self.current_lang]
        if not key:
            status_lbl.config(text=t_dict['save_empty'], fg=self.RED)
            return

        status_lbl.config(text=t_dict['test_running'], fg=self.PRIMARY)
        
        if combo: combo.config(state='disabled')
        if btn_fetch: btn_fetch.config(state='disabled')
        if btn_save: btn_save.config(state='disabled')
        if btn_test: btn_test.config(state='disabled')

        def run_test():
            from translator import GeminiTranslator, GroqTranslator, MistralTranslator
            
            models_to_test = list(combo['values']) if combo and combo.get() and combo.get() not in ["Load Failed", "Fetching..."] else [getattr(self.config, f"get_{provider}_model")()]
            
            valid_models = []
            err_msg_to_show = None
            
            for m in models_to_test:
                def _update_status(curr_m=m):
                    if not self.window.winfo_exists(): return
                    status_lbl.config(text="Testing...", fg=self.PRIMARY)
                self.window.after(0, _update_status)
                
                try:
                    res = None
                    if provider == 'gemini':
                        t = GeminiTranslator()
                        t.api_key = key
                        t.model = m
                        res = t.translate("Hi", "vi")
                    elif provider == 'groq':
                        t = GroqTranslator()
                        t.api_key = key
                        t.model = m
                        res = t.translate("Hi", "vi")
                    elif provider == 'mistral':
                        t = MistralTranslator()
                        t.api_key = key
                        t.model = m
                        res = t.translate("Hi", "vi")

                    if res:
                        valid_models.append(m)
                except Exception as e:
                    import logging
                    logging.error(f"Test API key failed for {m}: {e}")
                    if not err_msg_to_show:
                        err_msg_to_show = str(e)

            if valid_models:
                self.config.set_api_key(provider, key)
                def _set_pass():
                    if not self.window.winfo_exists():
                        return
                    if combo and len(models_to_test) > 1:
                        combo['values'] = valid_models
                        if combo.get() not in valid_models:
                            combo.set(valid_models[0])
                            getattr(self.config, f"set_{provider}_model")(valid_models[0])
                    status_lbl.config(text=t_dict['test_pass'], fg='#5db872')
                    if combo: combo.config(state='readonly')
                    if btn_fetch: btn_fetch.config(state='normal')
                    if btn_save: btn_save.config(state='normal')
                    if btn_test: btn_test.config(state='normal')
                self.window.after(0, _set_pass)
            else:
                short_err = t_dict['test_fail']
                if err_msg_to_show:
                    if "429" in err_msg_to_show:
                        short_err = "Fail (429)"
                    elif "403" in err_msg_to_show:
                        short_err = "Fail (403)"
                    elif "400" in err_msg_to_show:
                        short_err = "Fail (400)"
                    elif "connection" in err_msg_to_show.lower() or "timeout" in err_msg_to_show.lower():
                        short_err = t_dict['net_error']
                
                def _set_fail(msg=short_err):
                    if not self.window.winfo_exists():
                        return
                    status_lbl.config(text=msg, fg=self.RED)
                    if combo and len(models_to_test) > 1:
                        combo['values'] = []
                        combo.set("No valid models")
                    if combo: combo.config(state='readonly')
                    if btn_fetch: btn_fetch.config(state='normal')
                    if btn_save: btn_save.config(state='normal')
                    if btn_test: btn_test.config(state='normal')
                self.window.after(0, _set_fail)

        threading.Thread(target=run_test, daemon=True).start()

    def _create_options_section(self):
        """Checkboxes section."""
        self.options_lf = tk.LabelFrame(
            self.scroll_frame, text=" Tùy chọn ",
            fg=self.PRIMARY, bg=self.BASE,
            font=('Segoe UI', 10, 'bold'),
            labelanchor='nw', padx=10, pady=8
        )
        self.options_lf.pack(fill='x', padx=10, pady=4)

        self.autostart_var = tk.BooleanVar(value=self.config.is_auto_start())

        def on_autostart_change():
            self.config.set_auto_start(self.autostart_var.get())
            if self.on_save_callback:
                self.on_save_callback()

        self.autostart_cb = tk.Checkbutton(
            self.options_lf, text="Khởi động cùng Windows", variable=self.autostart_var,
            command=on_autostart_change,
            fg=self.TEXT_COLOR, bg=self.BASE,
            selectcolor=self.SURFACE0,
            activebackground=self.BASE,
            activeforeground=self.TEXT_COLOR,
            font=('Segoe UI', 10),
            anchor='w'
        )
        self.autostart_cb.pack(fill='x', pady=2)

    def _create_hotkey_section(self):
        """Hotkey table and action buttons."""
        self.hotkey_lf = tk.LabelFrame(
            self.scroll_frame, text=" ⌨ Phím tắt ",
            fg=self.PRIMARY, bg=self.BASE,
            font=('Segoe UI', 10, 'bold'),
            labelanchor='nw', padx=10, pady=8
        )
        self.hotkey_lf.pack(fill='x', padx=10, pady=4)

        # Table header frame
        header_frame = tk.Frame(self.hotkey_lf, bg=self.SURFACE1)
        header_frame.pack(fill='x', pady=(0, 2))

        # Dynamic table header labels (stored as attributes to easily update text and fonts)
        self.th_hk = tk.Label(header_frame, text="Phím tắt", width=14, fg=self.TEXT_COLOR, bg=self.SURFACE1, font=('Segoe UI', 9, 'bold'), anchor='w')
        self.th_hk.pack(side='left', padx=2, pady=4)

        self.th_lang = tk.Label(header_frame, text="Ngôn ngữ", width=16, fg=self.TEXT_COLOR, bg=self.SURFACE1, font=('Segoe UI', 9, 'bold'), anchor='w')
        self.th_lang.pack(side='left', padx=2, pady=4)

        self.th_mode = tk.Label(header_frame, text="Chế độ", fg=self.TEXT_COLOR, bg=self.SURFACE1, font=('Segoe UI', 9, 'bold'), anchor='w')
        self.th_mode.pack(side='left', padx=2, pady=4)

        th_empty = tk.Label(header_frame, text="", width=4, fg=self.TEXT_COLOR, bg=self.SURFACE1, font=('Segoe UI', 9, 'bold'), anchor='w')
        th_empty.pack(side='left', padx=2, pady=4)

        # Hotkeys list rows container
        self.hotkey_list_frame = tk.Frame(self.hotkey_lf, bg=self.BASE)
        self.hotkey_list_frame.pack(fill='x')

        # Load current active hotkeys
        self.hotkey_rows = []
        for hk in self.temp_hotkeys:
            self._add_hotkey_row(hk)

        # Add button
        self.add_btn = tk.Button(
            self.hotkey_lf, text="+ Thêm phím tắt",
            fg=self.PRIMARY, bg=self.SURFACE0,
            font=('Segoe UI', 10), bd=0,
            activebackground=self.SURFACE1,
            activeforeground=self.PRIMARY,
            cursor='hand2', padx=12, pady=4,
            command=self._show_hotkey_dialog
        )
        self.add_btn.pack(anchor='w', pady=(8, 4))

    def _add_hotkey_row(self, hk: dict):
        """Insert a single row representing a hotkey combo config."""
        font_family = FontMapper.get_font(self.current_lang)
        default_font = (font_family, 10)
        bold_font = (font_family, 10, 'bold')

        row_frame = tk.Frame(self.hotkey_list_frame, bg=self.SURFACE0)
        row_frame.pack(fill='x', pady=1)

        # Setup mouse hover visual states
        def on_enter(e, rf=row_frame):
            rf.config(bg=self.SURFACE2)
            for w in rf.winfo_children():
                if w.cget('text') != '✕':
                    w.config(bg=self.SURFACE2)

        def on_leave(e, rf=row_frame):
            rf.config(bg=self.SURFACE0)
            for w in rf.winfo_children():
                if w.cget('text') != '✕':
                    w.config(bg=self.SURFACE0)

        row_frame.bind('<Enter>', on_enter)
        row_frame.bind('<Leave>', on_leave)

        lbl_combo = tk.Label(
            row_frame, text=hk.get('key_combo', ''),
            width=14, fg=self.PRIMARY, bg=self.SURFACE0,
            font=bold_font, anchor='w'
        )
        lbl_combo.pack(side='left', padx=2, pady=3)
        lbl_combo.bind('<Enter>', on_enter)
        lbl_combo.bind('<Leave>', on_leave)

        lbl_lang = tk.Label(
            row_frame, text=hk.get('target_language_name', ''),
            width=16, fg=self.TEXT_COLOR, bg=self.SURFACE0,
            font=default_font, anchor='w'
        )
        lbl_lang.pack(side='left', fill='x', expand=True, padx=2, pady=3)
        lbl_lang.bind('<Enter>', on_enter)
        lbl_lang.bind('<Leave>', on_leave)

        del_btn = tk.Button(
            row_frame, text='✕',
            fg=self.RED, bg=self.SURFACE0, bd=0,
            font=bold_font,
            activebackground=self.SURFACE1,
            cursor='hand2',
            command=lambda hid=hk.get('id'), frame=row_frame: self._delete_hotkey(hid, frame)
        )
        del_btn.pack(side='right', padx=4, pady=3)

        t = self.TRANSLATIONS[self.current_lang]
        mode_text = t['popup_mode'] if hk.get('mode') == 'popup' else t['replace_mode']
        lbl_mode = tk.Label(
            row_frame, text=mode_text,
            fg=self.SUBTEXT, bg=self.SURFACE0,
            font=default_font, anchor='w'
        )
        lbl_mode.pack(side='right', padx=2, pady=3)
        lbl_mode.bind('<Enter>', on_enter)
        lbl_mode.bind('<Leave>', on_leave)

        # Bind edit action on double click
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
        """Remove hotkey row config instantly."""
        frame.destroy()
        self.hotkey_rows = [r for r in self.hotkey_rows if r['id'] != hotkey_id]
        self.temp_hotkeys = [hk for hk in self.temp_hotkeys if hk.get('id') != hotkey_id]
        
        self.config.data['hotkeys'] = self.temp_hotkeys
        self.config.save()
        if self.on_save_callback:
            self.on_save_callback()

    def _show_hotkey_dialog(self, edit_hotkey_data=None):
        """Spawn the Hotkey Dialog with keyboard recording hooks, styled with the active UI language."""
        if self.hotkey_manager:
            self.hotkey_manager.unregister_all()

        dialog = tk.Toplevel(self.window)
        is_edit = edit_hotkey_data is not None
        
        t_dict = self.TRANSLATIONS[self.current_lang]
        font_family = FontMapper.get_font(self.current_lang)
        default_font = (font_family, 10)
        bold_font = (font_family, 10, 'bold')
        small_font = (font_family, 9)

        dialog.title(t_dict['dialog_edit_title'] if is_edit else t_dict['dialog_add_title'])
        dialog.minsize(400, 320)
        dialog.configure(bg=self.BASE)
        dialog.attributes('-topmost', True)
        dialog.grab_set()

        # Keyboard combo display input box
        tk.Label(
            dialog, text=t_dict['dialog_press_prompt'], fg=self.TEXT_COLOR, bg=self.BASE,
            font=small_font
        ).pack(anchor='w', padx=16, pady=(16, 4))

        initial_val = edit_hotkey_data.get('key_combo', '') if is_edit else ""
        hotkey_var = tk.StringVar(value=initial_val)
        hotkey_entry = tk.Entry(
            dialog, textvariable=hotkey_var,
            bg='#ffffff', fg=self.PRIMARY,
            insertbackground=self.PRIMARY,
            font=(font_family, 12, 'bold'),
            relief='flat',
            justify='center',
            highlightthickness=1,
            highlightbackground=self.BORDER_COLOR,
            highlightcolor=self.PRIMARY
        )
        hotkey_entry.pack(fill='x', padx=16)

        # Global hook detection states
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
                
                # Modifiers normalization
                if name in ('left ctrl', 'right ctrl', 'ctrl'):
                    name = 'ctrl'
                elif name in ('left shift', 'right shift', 'shift'):
                    name = 'shift'
                elif name in ('left alt', 'right alt', 'alt', 'alt gr'):
                    name = 'alt'
                elif name in ('left windows', 'right windows', 'win', 'windows'):
                    name = 'win'
                
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

        # Language dropdown selector
        tk.Label(
            dialog, text=t_dict['dialog_lang_prompt'], fg=self.TEXT_COLOR, bg=self.BASE,
            font=default_font
        ).pack(anchor='w', padx=16, pady=(16, 4))

        lang_names = [lang[0] for lang in self.LANGUAGES]
        default_lang_name = lang_names[0]
        if is_edit:
            old_code = edit_hotkey_data.get('target_language_code')
            for name, code in self.LANGUAGES:
                if code == old_code:
                    default_lang_name = name
                    break
                    
        lang_var = tk.StringVar(value=default_lang_name)
        lang_combo = ttk.Combobox(
            dialog, textvariable=lang_var,
            values=lang_names, state='readonly'
        )
        lang_combo.pack(fill='x', padx=16)

        # Mode selection option radio buttons
        tk.Label(
            dialog, text=t_dict['dialog_mode_prompt'], fg=self.TEXT_COLOR, bg=self.BASE,
            font=default_font
        ).pack(anchor='w', padx=16, pady=(16, 4))

        initial_mode = edit_hotkey_data.get('mode', 'popup') if is_edit else "popup"
        mode_var = tk.StringVar(value=initial_mode)
        mode_frame = tk.Frame(dialog, bg=self.BASE)
        mode_frame.pack(anchor='w', padx=16)

        r1 = tk.Radiobutton(
            mode_frame, text=t_dict['dialog_mode_popup'], variable=mode_var, value="popup",
            fg=self.TEXT_COLOR, bg=self.BASE, selectcolor=self.SURFACE0,
            activebackground=self.BASE, activeforeground=self.TEXT_COLOR,
            font=default_font
        )
        r1.pack(side='left', padx=(0, 16))

        r2 = tk.Radiobutton(
            mode_frame, text=t_dict['dialog_mode_replace'], variable=mode_var, value="replace",
            fg=self.TEXT_COLOR, bg=self.BASE, selectcolor=self.SURFACE0,
            activebackground=self.BASE, activeforeground=self.TEXT_COLOR,
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
            dialog.destroy()
            if self.hotkey_manager:
                self.hotkey_manager.register_all()
            
        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)

        btn_frame = tk.Frame(dialog, bg=self.BASE)
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
            for name, code in self.LANGUAGES:
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
            fg='#ffffff', bg=self.PRIMARY,
            font=bold_font,
            relief='flat', padx=16, pady=4,
            cursor='hand2'
        ).pack(side='left', padx=(0, 8))

        tk.Button(
            btn_frame, text=t_dict['dialog_cancel_btn'], command=on_dialog_close,
            fg=self.TEXT_COLOR, bg=self.SURFACE1,
            font=default_font,
            relief='flat', padx=16, pady=4,
            cursor='hand2'
        ).pack(side='left')

    def update_ui_language(self, lang_code):
        """Update interface strings and typography font weights/families dynamically."""
        self.current_lang = lang_code
        self.config.data['ui_language'] = lang_code
        self.config.save()

        t = self.TRANSLATIONS[lang_code]
        font_family = FontMapper.get_font(lang_code)

        # Initialize fonts based on mapping
        default_font = (font_family, 10)
        bold_font = (font_family, 10, 'bold')
        title_font = ('Georgia', 15, 'bold') if lang_code in ('vi', 'en') else (font_family, 15, 'bold')
        italic_font = (font_family, 9, 'italic')
        small_font = (font_family, 9)

        # Update labels, headers, and tooltips
        self.title_label.config(text=t['title'], font=title_font)

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

        # self.model_lbl.config(text=t['model_label'], font=small_font)
        # self.reload_btn.config(text=t['load_models'], font=small_font)
        if hasattr(self, 'gemini_btn_save'):
            self.gemini_btn_save.config(text=t['save_btn'])
        if hasattr(self, 'groq_btn_save'):
            self.groq_btn_save.config(text=t['save_btn'])
        if hasattr(self, 'mistral_btn_save'):
            self.mistral_btn_save.config(text=t['save_btn'])
        # self.gemini_test_btn.config(text=t['test_btn'], font=small_font)
        self.google_free_lbl.config(text=t['google_free_note'], font=italic_font)

        self.options_lf.config(text=t['options_section'], font=bold_font)
        self.autostart_cb.config(text=t['autostart_label'], font=default_font)

        self.hotkey_lf.config(text=t['hotkey_section'], font=bold_font)

        self.th_hk.config(text=t['table_hk'], font=bold_font)
        self.th_lang.config(text=t['table_lang'], font=bold_font)
        self.th_mode.config(text=t['table_mode'], font=bold_font)

        self.add_btn.config(text=t['add_hk_btn'], font=default_font)

        # Configure widget generic fonts
        self.gemini_entry.config(font=default_font)
        self.gemini_model_combo.config(font=small_font)
        self.provider_combo.config(font=default_font)
        self.lang_ui_combo.config(font=default_font)

        # Re-render active hotkey rows with new translations
        self.redraw_hotkey_rows()

    def redraw_hotkey_rows(self):
        """Clean and rebuild current hotkeys rows inside container frame."""
        for widget in self.hotkey_list_frame.winfo_children():
            widget.destroy()
        
        self.hotkey_rows.clear()
        for hk in self.temp_hotkeys:
            self._add_hotkey_row(hk)
