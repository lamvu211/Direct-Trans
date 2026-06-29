"""
main.py - Entry point for DirectTrans application.
Orchestrates all components: config, tray, hotkeys, translation, clipboard, popup, settings.
"""

import sys
import os
import win32event
import win32api
import winerror
import tkinter as tk
import threading
import logging

# Define LOG_DIR early for single instance signaling and logging
if getattr(sys, 'frozen', False):
    LOG_DIR = os.path.dirname(sys.executable)
else:
    LOG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Redirect stdout and stderr to prevent crash in --noconsole mode
if getattr(sys, 'frozen', False):
    class DummyWriter:
        def write(self, x): pass
        def flush(self): pass
    if sys.stdout is None:
        sys.stdout = DummyWriter()
    if sys.stderr is None:
        sys.stderr = DummyWriter()

def check_single_instance():
    """Checks if another instance is running using a Windows Mutex.
    If yes, writes a signal file to restore the existing instance and exits.
    """
    sys.app_mutex = win32event.CreateMutex(None, 1, "DirectTrans_SingleInstance_Mutex")
    err = win32api.GetLastError()
    if err == winerror.ERROR_ALREADY_EXISTS or err == winerror.ERROR_ACCESS_DENIED:
        # First instance is already running! Write a signal file
        signal_file = os.path.join(LOG_DIR, 'directtrans.signal')
        try:
            with open(signal_file, 'w', encoding='utf-8') as f:
                f.write('SHOW')
        except Exception:
            pass
        # Close mutex handle and exit
        win32api.CloseHandle(sys.app_mutex)
        sys.exit(0)

# Check single instance before starting anything else
check_single_instance()

import logging.handlers

# Setup logging
log_file = os.path.join(LOG_DIR, 'directtrans.log')
handler = logging.handlers.TimedRotatingFileHandler(
    log_file, when="H", interval=1, backupCount=1, encoding="utf-8"
)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - [%(module)s] %(message)s', '%Y-%m-%d %H:%M:%S'))
logging.getLogger().setLevel(logging.INFO)
logging.getLogger().addHandler(handler)
logging.info("=== DirectTrans Starting ===")

# Add src directory to path for imports
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from config import Config
from tray import TrayIcon
from hotkey_manager import HotkeyManager
from translator import TranslationManager
from clipboard_util import ClipboardUtil
from popup_window import PopupWindow
from settings_window import SettingsWindow


class DirectTransApp:
    def __init__(self):
        self.config = Config()
        self.translator = TranslationManager(self.config)
        self.enabled = True
        self.root = None
        self.tray = None
        self.hotkey_manager = None
        self.settings_window = None

    def run(self):
        """Start the application on the main thread."""
        self.tray = TrayIcon(
            on_settings=self._safe_show_settings,
            on_toggle=self._safe_toggle_enabled,
            on_quit=self._safe_quit,
            config=self.config
        )
        # Start pystray tray icon on a background thread
        logging.info("Starting tray icon on background thread.")
        threading.Thread(target=self.tray.run, daemon=True).start()

        self._run_tkinter()

    def _run_tkinter(self):
        """Run tkinter event loop on the main thread."""
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("DirectTrans")

        # Try to set icon
        try:
            icon_path = os.path.join(BASE_DIR, 'assets', 'icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass

        # Initialize hotkey manager (needs root for after() calls)
        self.hotkey_manager = HotkeyManager(self.config, self._on_hotkey)
        self.hotkey_manager.register_all()

        # Start single-instance listener using filesystem poll
        self._start_single_instance_listener()

        # Always open settings on startup so user sees the interface
        logging.info("Opening settings window on startup.")
        self.root.after(1000, self._show_settings)

        print("DirectTrans is running. Use system tray icon to access settings.")
        logging.info("DirectTrans initialized and running.")

        # Tkinter event loop
        self.root.mainloop()

    def _start_single_instance_listener(self):
        """Poll the signal file for SHOW command from other instances."""
        signal_file = os.path.join(LOG_DIR, 'directtrans.signal')
        if os.path.exists(signal_file):
            try:
                os.remove(signal_file)
            except Exception:
                pass
            logging.info("Received SHOW signal from filesystem watch.")
            # Force flush logging handlers to ensure it is written to disk immediately
            for handler in logging.root.handlers:
                try:
                    handler.flush()
                except Exception:
                    pass
            self._show_settings()
        
        # Schedule the next check in 500ms
        if self.root:
            self.root.after(500, self._start_single_instance_listener)

    def _safe_show_settings(self):
        if self.root:
            self.root.after(0, self._show_settings)

    def _safe_toggle_enabled(self):
        if self.root:
            self.root.after(0, self._toggle_enabled)

    def _safe_quit(self):
        if self.root:
            self.root.after(0, self._quit)

    def _on_hotkey(self, hotkey_config: dict):
        """Callback when user presses a registered hotkey."""
        import time
        now = time.time()
        if now - getattr(self, '_last_hotkey_time', 0) < 1.0:
            logging.info("Debounced rapid hotkey trigger.")
            return
        self._last_hotkey_time = now

        if not self.enabled:
            logging.info("Hotkey pressed but app is paused.")
            return
        if not self.root:
            return

        logging.info(f"Hotkey triggered for language: {hotkey_config.get('target_language_code')} (Mode: {hotkey_config.get('mode')})")

        thread = threading.Thread(
            target=self._process_translation,
            args=(hotkey_config,),
            daemon=True
        )
        thread.start()

    def _show_error_popup(self, message: str, target_lang_name: str):
        """Helper to display error message in a popup window."""
        if not self.root:
            return
        def show():
            p = PopupWindow(self.root, self.config)
            p.show(target_lang=target_lang_name)
            p.show_error(message)
        self.root.after(0, show)

    def _process_translation(self, hotkey_config: dict):
        """Main translation processing logic."""
        mode = hotkey_config['mode']
        target_lang_code = hotkey_config['target_language_code']
        target_lang_name = hotkey_config['target_language_name']

        # 1. Get selected text
        try:
            selected_text, selected_rtf = ClipboardUtil.get_selected_text()
        except Exception as e:
            logging.error(f"Failed to get selected text from clipboard: {e}")
            self._show_error_popup("Không thể truy cập clipboard.", target_lang_name)
            return

        if not selected_text or not selected_text.strip():
            logging.warning("Selected text is empty or only whitespace.")
            self._show_error_popup("Không tìm thấy văn bản đang chọn. Vui lòng bôi đen văn bản trước.", target_lang_name)
            return

        # 2. If popup mode, show loading popup first
        popup = None
        popup_event = threading.Event()

        if mode == 'popup':
            logging.info("Spawning translation popup window.")
            def create_popup():
                nonlocal popup
                p = PopupWindow(self.root, self.config)
                p.show(
                    loading=True, 
                    target_lang=target_lang_name,
                    original_rtf=selected_rtf,
                    target_lang_code=target_lang_code
                )
                popup = p
                popup_event.set()

            self.root.after(0, create_popup)
            popup_event.wait(timeout=2.0)
            if popup is None:
                logging.warning("Popup was not created in time (2s timeout). Translation result dropped.")
                return

        # 3. Translate
        try:
            logging.info(f"Starting translation process to {target_lang_code}...")
            translated = self.translator.translate(selected_text, target_lang_code)
            logging.info("Translation process completed successfully.")
        except Exception as e:
            err_msg = str(e)
            logging.error(f"Translation failed: {err_msg}")
            if popup:
                self.root.after(0, lambda msg=err_msg: popup.show_error(msg))
            else:
                self._show_error_popup(f"Dịch thất bại: {err_msg}", target_lang_name)
            return

        # 4. Output result
        if mode == 'popup' and popup:
            self.root.after(0, lambda: popup.update_text(translated))
        elif mode == 'replace':
            try:
                ClipboardUtil.replace_selected_text(translated, selected_rtf, target_lang_code)
            except Exception:
                def show_fallback():
                    p = PopupWindow(self.root, self.config)
                    p.show(
                        translated_text=translated, 
                        target_lang=target_lang_name,
                        original_rtf=selected_rtf,
                        target_lang_code=target_lang_code
                    )
                self.root.after(0, show_fallback)

    def _show_settings(self):
        """Open settings window."""
        if not self.root:
            return

        # If settings window already exists, restore and focus it
        if self.settings_window and self.settings_window.window and self.settings_window.window.winfo_exists():
            logging.info("Settings window already exists. Restoring and focusing.")
            self.root.after(0, self.settings_window.restore_and_focus)
            return

        def on_settings_closed():
            self.settings_window = None

        self.settings_window = SettingsWindow(
            self.root, self.config, self._on_settings_saved, on_settings_closed, self.hotkey_manager
        )
        self.root.after(0, self.settings_window.show)

    def _on_settings_saved(self):
        """Callback after settings are saved."""
        if self.hotkey_manager:
            self.hotkey_manager.reload()

    def _toggle_enabled(self):
        """Toggle translation on/off."""
        self.enabled = not self.enabled
        if self.hotkey_manager:
            if self.enabled:
                self.hotkey_manager.register_all()
            else:
                self.hotkey_manager.unregister_all()

    def _quit(self):
        """Clean shutdown."""
        logging.info("=== DirectTrans Shutting Down ===")
        if self.hotkey_manager:
            self.hotkey_manager.stop()
        if self.tray:
            self.tray.stop()
        if hasattr(sys, 'app_mutex') and sys.app_mutex:
            try:
                win32api.CloseHandle(sys.app_mutex)
            except Exception:
                pass
        if self.root:
            self.root.quit()
        os._exit(0)


if __name__ == '__main__':
    # Enable DPI awareness for crisp rendering on high-DPI displays
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    app = DirectTransApp()
    app.run()
