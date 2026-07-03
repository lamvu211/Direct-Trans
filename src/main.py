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

def kill_old_processes():
    """Kill any existing DirectTrans.exe processes (old versions or stale autostart instances).
    This ensures the new version always takes over cleanly.
    Waits for processes to fully terminate before returning.
    """
    try:
        import subprocess
        current_pid = os.getpid()

        # List ALL processes, then filter for any exe starting with "DirectTrans"
        # This catches versioned names like DirectTrans_v1.0.4.exe
        result = subprocess.run(
            ['tasklist', '/FO', 'CSV', '/NH'],
            capture_output=True, text=True, timeout=5
        )
        killed_any = False
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            parts = line.strip('"').split('","')
            if len(parts) >= 2:
                proc_name = parts[0].strip('"').lower()
                if not proc_name.startswith('directtrans'):
                    continue
                try:
                    pid = int(parts[1].strip('"'))
                    if pid != current_pid:
                        subprocess.run(['taskkill', '/PID', str(pid), '/F'],
                                       capture_output=True, timeout=5)
                        killed_any = True
                except (ValueError, subprocess.SubprocessError):
                    pass

        # Wait for killed processes to fully terminate (up to 3 seconds)
        if killed_any:
            import time
            for _ in range(30):
                time.sleep(0.1)
                check = subprocess.run(
                    ['tasklist', '/FO', 'CSV', '/NH'],
                    capture_output=True, text=True, timeout=5
                )
                still_alive = False
                for line in check.stdout.strip().split('\n'):
                    if not line.strip() or 'INFO' in line.upper():
                        continue
                    parts = line.strip('"').split('","')
                    if len(parts) >= 2:
                        proc_name = parts[0].strip('"').lower()
                        if not proc_name.startswith('directtrans'):
                            continue
                        try:
                            pid = int(parts[1].strip('"'))
                            if pid != current_pid:
                                still_alive = True
                        except ValueError:
                            pass
                if not still_alive:
                    break
    except Exception:
        pass
    
    # Clean up any stale signal files left by killed processes
    signal_file = os.path.join(LOG_DIR, 'directtrans.signal')
    try:
        if os.path.exists(signal_file):
            os.remove(signal_file)
    except Exception:
        pass

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

# Kill old/stale processes first, then check single instance
if getattr(sys, 'frozen', False):
    kill_old_processes()
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
from constants import MODE_POPUP, MODE_REPLACE
from tray import TrayIcon
from hotkey_manager import HotkeyManager
from translator import TranslationManager
from clipboard_util import ClipboardUtil
from popup_window import PopupWindow
from settings_window import SettingsWindow


class DirectTransApp:
    def __init__(self):
        self.config = Config()
        self._heal_auto_start_path()
        self.translator = TranslationManager(self.config)
        self.enabled = True
        self.root = None
        self.tray = None
        self.hotkey_manager = None
        self.settings_window = None
        self.translation_thread = None
        self._processing_lock = threading.Lock()

    def run(self):
        """Start the application on the main thread."""
        self.tray = TrayIcon(
            on_settings=self._safe_show_settings,
            on_toggle=self._safe_toggle_enabled,
            on_quit=self._safe_quit,
            config=self.config,
            is_enabled=lambda: self.enabled
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

        # Open settings on first run or when primary provider has no API key
        if self.config.needs_setup():
            logging.info("Opening settings window on startup (first run or missing API key).")
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
        
        # Schedule the next check in 2000ms (restore window doesn't need sub-second responsiveness)
        if self.root:
            self.root.after(2000, self._start_single_instance_listener)

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
        if not self._processing_lock.acquire(blocking=False):
            return

        if not self.enabled:
            logging.info("Hotkey pressed but app is paused.")
            self._processing_lock.release()
            return
        if not self.root:
            self._processing_lock.release()
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
        try:
            mode = hotkey_config['mode']
            target_lang_code = hotkey_config['target_language_code']
            target_lang_name = hotkey_config['target_language_name']

            from ui.i18n import TRANSLATIONS
            ui_lang = self.config.data.get('ui_language', 'vi')
            msgs = TRANSLATIONS.get(ui_lang, TRANSLATIONS['en'])

            import ctypes
            try:
                original_hwnd = ctypes.windll.user32.GetForegroundWindow()
            except Exception:
                original_hwnd = None

            # 1. Get selected text
            try:
                selected_text, selected_rtf = ClipboardUtil.get_selected_text()
            except Exception as e:
                logging.error(f"Failed to get selected text from clipboard: {e}")
                self._show_error_popup(msgs.get('err_clipboard_msg', 'Không thể lấy văn bản từ clipboard.'), target_lang_name)
                return

            if not selected_text or not selected_text.strip():
                logging.warning("Selected text is empty or only whitespace.")
                self._show_error_popup(msgs.get('err_clipboard_msg', 'Không thể lấy văn bản từ clipboard.'), target_lang_name)
                return

            # 2. If popup mode, show loading popup first
            popup = None
            popup_event = threading.Event()

            if mode == MODE_POPUP:
                logging.info("Spawning translation popup window.")
                def create_popup():
                    nonlocal popup
                    p = PopupWindow(self.root, self.config)
                    p.show(
                        loading=True, 
                        target_lang=target_lang_name,
                        original_rtf=selected_rtf,
                        target_lang_code=target_lang_code,
                        original_hwnd=original_hwnd
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
                    popup.root.after(0, lambda msg=err_msg: popup.show_error(msgs.get('err_trans_title', 'Lỗi dịch: {}').format(msg)))
                else:
                    self._show_error_popup(msgs.get('err_trans_title', 'Lỗi dịch: {}').format(err_msg), target_lang_name)
                return

            # 4. Output result
            if mode == MODE_POPUP and popup:
                self.root.after(0, lambda: popup.update_text(translated))
            elif mode == MODE_REPLACE:
                try:
                    ClipboardUtil.replace_selected_text(translated, selected_rtf, target_lang_code)
                except Exception:
                    def show_fallback():
                        p = PopupWindow(self.root, self.config)
                        p.show(
                            translated_text=translated, 
                            target_lang=target_lang_name,
                            original_rtf=selected_rtf,
                            target_lang_code=target_lang_code,
                            original_hwnd=original_hwnd
                        )
                    self.root.after(0, show_fallback)
        finally:
            self._processing_lock.release()

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

    def _heal_auto_start_path(self):
        """If auto-start is enabled, update registry to point to the current exe.
        Ensures upgrading between versions keeps startup working.
        """
        if not getattr(sys, 'frozen', False):
            return
        if not self.config.is_auto_start():
            return
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_READ
            )
            current_val, _ = winreg.QueryValueEx(key, "DirectTrans")
            winreg.CloseKey(key)

            expected_path = sys.executable
            registered_path = current_val.strip('"')
            if registered_path != expected_path:
                logging.info(f"Auto-start path outdated ({current_val}), updating to current exe.")
                self.config.set_auto_start(True)
        except FileNotFoundError:
            logging.info("Auto-start registry entry missing, re-creating.")
            self.config.set_auto_start(True)
        except Exception as e:
            logging.warning(f"Failed to heal auto-start path: {e}")

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
        """
        Quit the application. 
        Note: os._exit(0) is used to forcefully terminate all threads, 
        including the Windows message loop in HotkeyManager and systray loop,
        preventing the app from hanging in the background.
        """
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
