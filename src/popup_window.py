"""
popup_window.py - Translation result popup window with Claude-inspired Editorial theme.
Supports dynamic multilingual interface translation (VI, EN, KO, ZH, JA) for popup labels.
"""

import tkinter as tk
from font_mapper import FontMapper


class PopupWindow:
    """
    Translation result popup window.
    - Appears at center of current monitor/mouse position
    - Resizable (min 250x120)
    - Copy and Close buttons
    - Dynamic font mapping based on target language
    - Claude theme styling with full localization
    """

    # Class-level list to track all open popup instances (singleton pattern per app session)
    open_popups = []

    # Apple Design Colors
    BASE = '#ffffff'          # Canvas background (Pure White)
    SURFACE0 = '#f5f5f7'      # Surface-soft/parchment (text area background)
    SURFACE1 = '#fafafc'      # Button active background (Pearl)
    TEXT_COLOR = '#1d1d1f'    # Primary headlines and body (Ink)
    SUBTEXT = '#7a7a7a'       # Secondary text (Ink Muted 48)
    BLUE = '#0066cc'          # Primary brand action color (Action Blue)
    GREEN = '#34c759'         # Success state (System Green)
    RED = '#ff453a'           # Error/Close state (System Red)
    PEACH = '#0066cc'         # Primary brand action color (Action Blue)
    BORDER_COLOR = '#d2d2d7'  # Hairline Strong

    # Popup UI translation dictionary
    TRANSLATIONS = {
        'vi': {
            'title_prefix': 'Dịch',
            'replace_btn': '✏ Thay thế',
            'copy_btn': '📋 Copy',
            'copied_feedback': '✓ Đã copy!',
            'loading': '⏳ Đang dịch...',
            'replace_error': 'Lỗi thay thế:',
        },
        'en': {
            'title_prefix': 'Translate',
            'replace_btn': '✏ Replace',
            'copy_btn': '📋 Copy',
            'copied_feedback': '✓ Copied!',
            'loading': '⏳ Translating...',
            'replace_error': 'Replacement error:',
        },
        'ko': {
            'title_prefix': '번역',
            'replace_btn': '✏ 바꾸기',
            'copy_btn': '📋 복사',
            'copied_feedback': '✓ 복사됨!',
            'loading': '⏳ 번역 중...',
            'replace_error': '교체 오류:',
        },
        'zh': {
            'title_prefix': '翻译',
            'replace_btn': '✏ 替换',
            'copy_btn': '📋 复制',
            'copied_feedback': '✓ 已复制!',
            'loading': '⏳ 正在翻译...',
            'replace_error': '替换错误:',
        },
        'ja': {
            'title_prefix': '翻訳',
            'replace_btn': '✏ 置換',
            'copy_btn': '📋 コピー',
            'copied_feedback': '✓ コピー完了!',
            'loading': '⏳ 翻訳中...',
            'replace_error': '置換エラー:',
        }
    }

    def __init__(self, root: tk.Tk, config=None):
        self.root = root
        self.config = config
        self.window = None
        self.text_widget = None
        self.original_rtf = None
        self.target_lang_code = None
        self.translated_text = None

    def show(self, translated_text: str = None, loading: bool = False,
             source_lang: str = "", target_lang: str = "",
             original_rtf: bytes = None, target_lang_code: str = None):
        """Show the popup. If loading=True, shows spinner. Otherwise shows translated text."""
        self.original_rtf = original_rtf
        self.target_lang_code = target_lang_code
        self.translated_text = translated_text

        # Close any existing popups to ensure only 1 window is shown at a time
        for p in list(PopupWindow.open_popups):
            p.close()
        PopupWindow.open_popups.clear()

        self.window = tk.Toplevel(self.root)
        self.window.overrideredirect(False)
        self.window.attributes('-topmost', True)
        self.window.minsize(400, 200)
        self.window.configure(bg=self.BASE)

        # Get interface translations and font based on UI language
        ui_lang = self.config.data.get('ui_language', 'vi') if self.config else 'vi'
        t = self.TRANSLATIONS.get(ui_lang, self.TRANSLATIONS['vi'])
        
        ui_font_family = FontMapper.get_font(ui_lang)
        ui_default_font = (ui_font_family, 9)
        ui_bold_font = (ui_font_family, 9, 'bold')

        # Get content font based on translated target language
        content_font_family = FontMapper.get_font(target_lang_code if target_lang_code else 'en')

        # Position at mouse cursor - center on the screen containing mouse
        try:
            import win32api
            import win32con
            # Get current cursor position
            mx, my = win32api.GetCursorPos()
            # Get monitor containing cursor
            monitor = win32api.MonitorFromPoint((mx, my), win32con.MONITOR_DEFAULTTONEAREST)
            monitor_info = win32api.GetMonitorInfo(monitor)
            # Work area coordinates (excludes taskbar)
            work_area = monitor_info['Work']
            m_left, m_top, m_right, m_bottom = work_area
            
            # Calculate dynamic size: ~45% of width and ~40% of height, with bounds
            popup_w = int((m_right - m_left) * 0.45)
            popup_h = int((m_bottom - m_top) * 0.4)
            popup_w = max(400, min(1200, popup_w))
            popup_h = max(250, min(800, popup_h))
            
            # Center on this monitor
            pos_x = m_left + (m_right - m_left - popup_w) // 2
            pos_y = m_top + (m_bottom - m_top - popup_h) // 2
            self.window.geometry(f'{popup_w}x{popup_h}+{pos_x}+{pos_y}')
        except Exception as e:
            # Fallback if win32 fails
            import logging
            logging.error(f"Failed to center popup using Win32 API: {e}")
            x = self.root.winfo_pointerx()
            y = self.root.winfo_pointery()
            self.window.geometry(f'880x465+{x + 10}+{y + 10}')

        # Localize common target language names based on UI language
        target_lang_display = target_lang
        if target_lang_code:
            common_langs = {
                'vi': {'vi': 'Tiếng Việt', 'en': 'Tiếng Anh', 'ko': 'Tiếng Hàn', 'zh': 'Tiếng Trung', 'ja': 'Tiếng Nhật'},
                'en': {'vi': 'Vietnamese', 'en': 'English', 'ko': 'Korean', 'zh': 'Chinese', 'ja': 'Japanese'},
                'ko': {'vi': '베트남어', 'en': '영어', 'ko': '한국어', 'zh': '중국어', 'ja': '일본어'},
                'zh': {'vi': '越南语', 'en': '英语', 'ko': '韩语', 'zh': '中文', 'ja': '日语'},
                'ja': {'vi': 'ベトナム語', 'en': '英語', 'ko': '韓国語', 'zh': '中国語', 'ja': '日本語'},
            }
            if ui_lang in common_langs and target_lang_code in common_langs[ui_lang]:
                target_lang_display = common_langs[ui_lang][target_lang_code]

        # Title (localized prefix)
        title = f"{t['title_prefix']} → {target_lang_display}" if target_lang_display else "DirectTrans"
        self.window.title(title)

        # Try to set icon if available
        try:
            import os
            icon_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 'assets', 'icon.ico'
            )
            if os.path.exists(icon_path):
                self.window.iconbitmap(icon_path)
        except Exception:
            pass

        # Main frame
        main_frame = tk.Frame(self.window, padx=8, pady=8, bg=self.BASE)
        main_frame.pack(fill='both', expand=True)

        # Header: language label + copy + close buttons
        header = tk.Frame(main_frame, bg=self.BASE)
        header.pack(fill='x')

        lang_label = tk.Label(
            header, text=f"→ {target_lang}",
            fg=self.BLUE, bg=self.BASE, font=ui_default_font
        )
        lang_label.pack(side='left')

        close_btn = tk.Button(
            header, text='✕', command=self.close,
            fg=self.RED, bg=self.BASE, bd=0,
            font=(ui_font_family, 10, 'bold'),
            activebackground=self.SURFACE1, cursor='hand2'
        )
        close_btn.pack(side='right')

        self.copy_btn = tk.Button(
            header, text=t['copy_btn'], command=self._copy,
            fg='#ffffff', bg=self.GREEN, bd=0,
            font=ui_bold_font, padx=8, pady=2,
            activebackground=self.SURFACE1, cursor='hand2'
        )
        self.copy_btn.pack(side='right', padx=(0, 8))

        # Replace button (only show if we have target language code for replacement)
        self.replace_btn = tk.Button(
            header, text=t['replace_btn'], command=self._replace,
            fg='#ffffff', bg=self.PEACH, bd=0,
            font=ui_bold_font, padx=8, pady=2,
            activebackground=self.SURFACE1, cursor='hand2'
        )
        if self.target_lang_code:
            self.replace_btn.pack(side='right', padx=(0, 8))

        # Text area with scrollbar
        text_frame = tk.Frame(
            main_frame, bg=self.SURFACE0,
            highlightbackground=self.BORDER_COLOR,
            highlightcolor=self.BLUE,
            highlightthickness=1
        )
        text_frame.pack(fill='both', expand=True, pady=(8, 0))

        self.text_widget = tk.Text(
            text_frame, wrap='word',
            bg=self.SURFACE0, fg=self.TEXT_COLOR,
            font=(content_font_family, 11),
            relief='flat', padx=8, pady=8,
            insertbackground=self.TEXT_COLOR,
            selectbackground=self.BLUE,
            selectforeground=self.BASE,
            borderwidth=0, highlightthickness=0
        )

        scrollbar = tk.Scrollbar(
            text_frame, command=self.text_widget.yview,
            bg=self.SURFACE1, troughcolor=self.SURFACE0,
            activebackground=self.BLUE
        )
        self.text_widget.config(yscrollcommand=scrollbar.set)

        scrollbar.pack(side='right', fill='y')
        self.text_widget.pack(side='left', fill='both', expand=True)

        if loading:
            self.text_widget.insert('1.0', t['loading'])
            self.text_widget.config(state='disabled')
        elif translated_text:
            self.text_widget.insert('1.0', translated_text)
            self.text_widget.config(state='disabled')

        # Track this popup
        PopupWindow.open_popups.append(self)
        self.window.protocol("WM_DELETE_WINDOW", self.close)

    def update_text(self, translated_text: str):
        """Update text when translation is complete (replaces loading indicator)."""
        self.translated_text = translated_text
        if not self.text_widget or not self.window.winfo_exists():
            return
        self.text_widget.config(state='normal')
        self.text_widget.delete('1.0', 'end')
        self.text_widget.insert('1.0', translated_text)
        self.text_widget.config(state='disabled')

    def show_error(self, error_msg: str):
        """Show error message in popup."""
        self.translated_text = None
        if not self.text_widget or not self.window.winfo_exists():
            return
        self.text_widget.config(state='normal')
        self.text_widget.delete('1.0', 'end')
        self.text_widget.insert('1.0', f'❌ {error_msg}')
        self.text_widget.config(fg=self.RED, state='disabled')

    def _copy(self):
        """Copy translated content to clipboard with dynamic feedback."""
        if not self.text_widget:
            return
        ui_lang = self.config.data.get('ui_language', 'vi') if self.config else 'vi'
        t = self.TRANSLATIONS.get(ui_lang, self.TRANSLATIONS['vi'])

        content = self.text_widget.get('1.0', 'end-1c')
        self.root.clipboard_clear()
        self.root.clipboard_append(content)

        # Visual feedback: briefly change button text
        self.copy_btn.config(text=t['copied_feedback'])
        self.window.after(1500, lambda: self._reset_copy_btn())

    def _reset_copy_btn(self):
        """Reset copy button text after visual feedback."""
        try:
            if self.window.winfo_exists():
                ui_lang = self.config.data.get('ui_language', 'vi') if self.config else 'vi'
                t = self.TRANSLATIONS.get(ui_lang, self.TRANSLATIONS['vi'])
                self.copy_btn.config(text=t['copy_btn'])
        except Exception:
            pass

    def _replace(self):
        """Replace the original selection with the translated text."""
        if not self.translated_text or not self.target_lang_code:
            return
        
        import logging
        import threading
        import time
        from clipboard_util import ClipboardUtil

        # Capture the foreground window before withdrawing popup
        import ctypes
        try:
            target_hwnd = ctypes.windll.user32.GetForegroundWindow()
        except Exception:
            target_hwnd = None

        # Hide window immediately so focus returns to the original active application
        try:
            self.window.withdraw()
        except Exception as e:
            logging.error(f"Error withdrawing window: {e}")

        def perform_paste():
            # Wait for popup to fully hide before simulating paste
            time.sleep(0.25)
            # Restore focus to original target window
            if target_hwnd:
                try:
                    ctypes.windll.user32.SetForegroundWindow(target_hwnd)
                    time.sleep(0.05)
                except Exception:
                    pass
            try:
                ClipboardUtil.replace_selected_text(
                    self.translated_text,
                    self.original_rtf,
                    self.target_lang_code
                )
            except Exception as e:
                logging.error(f"Error replacing text from popup: {e}")
                # Restore window to show the error
                def restore_and_error():
                    try:
                        self.window.deiconify()
                        ui_lang = self.config.data.get('ui_language', 'vi') if self.config else 'vi'
                        t = self.TRANSLATIONS.get(ui_lang, self.TRANSLATIONS['vi'])
                        self.show_error(f"{t['replace_error']} {e}")
                    except Exception:
                        pass
                self.root.after(0, restore_and_error)
                return
            
            # Close the window after successful replace
            self.root.after(0, self.close)

        threading.Thread(target=perform_paste, daemon=True).start()

    def close(self):
        if self in PopupWindow.open_popups:
            PopupWindow.open_popups.remove(self)
        try:
            self.window.destroy()
        except Exception:
            pass
