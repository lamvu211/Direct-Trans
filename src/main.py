"""
main.py - Entry point for DirectTrans application.
Orchestrates all components: config, tray, hotkeys, translation, clipboard, popup, settings.
"""

import sys
import os
import win32event
import win32api
import winerror
import threading
import logging

# Define LOG_DIR early for single instance signaling and logging
if getattr(sys, 'frozen', False):
    LOG_DIR = os.path.dirname(sys.executable)
else:
    LOG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _boot_trace(msg: str) -> None:
    """Append startup diagnostics (frozen builds) before logging is configured."""
    if not getattr(sys, "frozen", False):
        return
    try:
        path = os.path.join(LOG_DIR, "boot_trace.txt")
        with open(path, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception:
        pass


_boot_trace("boot: interpreter started")

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
    """Kill other DirectTrans* processes so a newly launched exe can take over."""
    from process_util import kill_other_directtrans_processes

    try:
        kill_other_directtrans_processes(exclude_pid=os.getpid(), wait_seconds=3.0)
    except Exception as e:
        logging.warning("kill_old_processes failed: %s", e)


def _discard_startup_signal_file() -> None:
    """Remove stale single-instance signal without opening Settings."""
    signal_file = os.path.join(LOG_DIR, "directtrans.signal")
    try:
        if os.path.exists(signal_file):
            os.remove(signal_file)
    except OSError as e:
        logging.debug("Could not remove signal file: %s", e)


def _signal_existing_instance_and_exit() -> None:
    """Second instance (dev): ask the running copy to show Settings, then exit."""
    _boot_trace("boot: check_single_instance another instance, exiting")
    signal_file = os.path.join(LOG_DIR, "directtrans.signal")
    try:
        with open(signal_file, "w", encoding="utf-8") as f:
            f.write("SHOW")
    except OSError:
        pass
    try:
        win32api.CloseHandle(sys.app_mutex)
    except Exception:
        pass
    sys.exit(0)


def check_single_instance():
    """Single-instance mutex. Packaged exe kills stale processes instead of signaling them."""
    _boot_trace("boot: check_single_instance enter")
    sys.app_mutex = win32event.CreateMutex(None, 1, "DirectTrans_SingleInstance_Mutex")
    err = win32api.GetLastError()
    _boot_trace(f"boot: check_single_instance GetLastError={err}")
    if err == winerror.ERROR_ALREADY_EXISTS or err == winerror.ERROR_ACCESS_DENIED:
        if getattr(sys, "frozen", False):
            logging.warning("Mutex still held; retrying stale DirectTrans cleanup")
            kill_old_processes()
            try:
                win32api.CloseHandle(sys.app_mutex)
            except Exception:
                pass
            sys.app_mutex = win32event.CreateMutex(None, 1, "DirectTrans_SingleInstance_Mutex")
            err = win32api.GetLastError()
            _boot_trace(f"boot: check_single_instance retry GetLastError={err}")
            if err not in (winerror.ERROR_ALREADY_EXISTS, winerror.ERROR_ACCESS_DENIED):
                _discard_startup_signal_file()
                _boot_trace("boot: check_single_instance acquired mutex after retry")
                return
            logging.error("Cannot start: another DirectTrans instance is still running")
            try:
                win32api.CloseHandle(sys.app_mutex)
            except Exception:
                pass
            sys.exit(1)
        _signal_existing_instance_and_exit()
    _discard_startup_signal_file()
    _boot_trace("boot: check_single_instance acquired mutex")

import logging.handlers

# Setup logging
log_file = os.path.join(LOG_DIR, 'directtrans.log')
handler = logging.handlers.TimedRotatingFileHandler(
    log_file, when="H", interval=1, backupCount=1, encoding="utf-8"
)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - [%(module)s] %(message)s', '%Y-%m-%d %H:%M:%S'))
logging.getLogger().setLevel(logging.INFO)
logging.getLogger().addHandler(handler)
_boot_trace("boot: logging configured")
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
from updater import check_for_updates_in_background, schedule_daily_update_check


class DirectTransApp:
    def __init__(self):
        self.config = Config()
        self._heal_auto_start_path()
        self.translator = TranslationManager(self.config)
        self.enabled = True
        self._gui_ready = False
        self.tray = None
        self.hotkey_manager = None
        self.settings_window = None
        self._startup_splash = None
        self._win32_startup_splash = None
        self.translation_thread = None
        self._processing_lock = threading.Lock()
        self.config._theme_listener = self._on_ui_theme_changed

    def _on_ui_theme_changed(self, theme_id: str):
        """Keep Settings and any open translation popups in sync with config.ui_theme."""

        def apply_theme_ui():
            settings = getattr(self, "settings_window", None)
            if settings is not None and settings.is_open():
                try:
                    settings.set_theme(theme_id)
                except Exception:
                    logging.exception("Failed to sync theme to Settings")

            try:
                from ui.qt.popup_window import QtPopupWindow

                for popup in list(QtPopupWindow.open_popups):
                    try:
                        popup.sync_theme_display(theme_id)
                    except Exception:
                        logging.exception("Failed to sync theme to popup")
            except Exception:
                pass

        run_on_main = getattr(self, "_run_on_main", None)
        if run_on_main:
            run_on_main(apply_theme_ui)
        else:
            apply_theme_ui()

    def run(self):
        """Start the application on the main thread."""
        self._run_qt()

    def _run_qt(self):
        """Qt main loop (settings, popup, updater dialogs)."""
        from PySide6.QtWidgets import QApplication
        from ui.dpi_util import enable_process_dpi_awareness
        from ui.qt.dispatch import run_on_main, schedule_ms, set_qt_application
        from ui.qt.widgets import apply_premium_app

        enable_process_dpi_awareness()
        import ctypes
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("DirectTrans.App.2.0.0")
        except Exception:
            pass
        self.qt_app = QApplication(sys.argv)
        self.qt_app.setQuitOnLastWindowClosed(False)
        apply_premium_app(self.qt_app)
        from PySide6.QtGui import QIcon
        app_icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
        if os.path.exists(app_icon_path):
            self.qt_app.setWindowIcon(QIcon(app_icon_path))
        set_qt_application(self.qt_app)

        if not getattr(self, "_win32_startup_splash", None) and self.config.needs_setup():
            from ui.qt.startup_splash import StartupSplash

            self._startup_splash = StartupSplash()
            self._startup_splash.show_and_pulse()
        self._run_on_main = run_on_main
        self._schedule_ms = schedule_ms
        self._gui_ready = True

        self.tray = TrayIcon(
            on_settings=self._safe_show_settings,
            on_toggle=self._safe_toggle_enabled,
            on_quit=self._safe_quit,
            config=self.config,
            is_enabled=lambda: self.enabled,
        )
        logging.info("Starting tray icon on background thread.")
        threading.Thread(target=self.tray.run, daemon=True).start()

        self.hotkey_manager = HotkeyManager(self.config, self._on_hotkey)
        self.hotkey_manager.register_all()

        # Start single-instance listener using filesystem poll
        self._start_single_instance_listener()

        # Packaged exe: always show Settings on startup so users see the app after install
        if getattr(sys, "frozen", False):
            logging.info("Opening settings window on startup (packaged build).")
            self._schedule_ms(300, self._show_settings)
        elif self.config.needs_setup():
            logging.info("Opening settings window on startup (first run or missing API key).")
            self._schedule_ms(1000, self._show_settings)

        self._schedule_ms(5000, lambda: check_for_updates_in_background(None, self.config))
        schedule_daily_update_check(self._schedule_ms, self.config, hour=9, minute=0)

        print("DirectTrans is running. Use system tray icon to access settings.")
        logging.info("DirectTrans initialized and running.")

        self.qt_app.exec()

    def _start_single_instance_listener(self):
        """Poll the signal file for SHOW command from other instances."""
        signal_file = os.path.join(LOG_DIR, 'directtrans.signal')
        if os.path.exists(signal_file):
            try:
                os.remove(signal_file)
            except Exception as e:
                logging.error("Cannot delete signal file %s: %s", signal_file, e)
            else:
                logging.info("Received SHOW signal from filesystem watch.")
                for handler in logging.root.handlers:
                    try:
                        handler.flush()
                    except Exception:
                        pass
                self._show_settings()
        
        # Schedule the next check in 2000ms (restore window doesn't need sub-second responsiveness)
        if getattr(self, "_schedule_ms", None):
            self._schedule_ms(2000, self._start_single_instance_listener)

    def _safe_show_settings(self):
        if getattr(self, "_run_on_main", None):
            self._run_on_main(self._show_settings)

    def _safe_toggle_enabled(self):
        if getattr(self, "_run_on_main", None):
            self._run_on_main(self._toggle_enabled)

    def _safe_quit(self):
        if getattr(self, "_run_on_main", None):
            self._run_on_main(self._quit)

    def _notify_hotkey_busy(self):
        from ui.i18n import TRANSLATIONS

        ui_lang = self.config.data.get("ui_language", "vi")
        msgs = TRANSLATIONS.get(ui_lang, TRANSLATIONS["en"])
        title = msgs.get("hotkey_busy_title", "DirectTrans")
        message = msgs.get("hotkey_busy_msg", "Please wait.")
        logging.info("Hotkey ignored: translation already in progress.")
        if self.tray:
            self.tray.notify(title, message)

    def _on_hotkey(self, hotkey_config: dict):
        """Callback when user presses a registered hotkey."""
        if not self._processing_lock.acquire(blocking=False):
            self._notify_hotkey_busy()
            return

        if not self.enabled:
            logging.info("Hotkey pressed but app is paused.")
            self._processing_lock.release()
            return
        if not self._gui_ready:
            self._processing_lock.release()
            return

        logging.info(f"Hotkey triggered for language: {hotkey_config.get('target_language_code')} (Mode: {hotkey_config.get('mode')})")

        thread = threading.Thread(
            target=self._process_translation,
            args=(hotkey_config,),
            daemon=True
        )
        thread.start()

    def _show_error_popup(
        self,
        message: str,
        target_lang_name: str,
        target_lang_code: str | None = None,
    ):
        """Helper to display error message in a popup window."""
        if not self._gui_ready:
            return

        def show():
            p = PopupWindow(self.config)
            p.show(
                target_lang=target_lang_name,
                target_lang_code=target_lang_code,
            )
            p.show_error(message)
        self._run_on_main(show)

    def _show_result_popup(
        self,
        translated: str,
        target_lang_name: str,
        target_lang_code: str,
        selected_rtf,
        original_hwnd,
        selected_text: str,
        provider_used: str,
    ):
        def show():
            p = PopupWindow(self.config)
            p.show(
                translated_text=translated,
                target_lang=target_lang_name,
                target_lang_code=target_lang_code,
                original_rtf=selected_rtf,
                original_hwnd=original_hwnd,
                original_text=selected_text,
                provider_key=provider_used,
            )
        self._run_on_main(show)

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
                self._show_error_popup(
                    msgs.get('err_clipboard_msg', 'Không thể lấy văn bản từ clipboard.'),
                    target_lang_name,
                    target_lang_code,
                )
                return

            if not selected_text or not selected_text.strip():
                logging.warning("Selected text is empty or only whitespace.")
                self._show_error_popup(
                    msgs.get(
                        'err_clipboard_empty_msg',
                        'Hãy bôi đen đoạn cần dịch, rồi bấm phím tắt dịch.',
                    ),
                    target_lang_name,
                    target_lang_code,
                )
                return

            # 2. If popup mode, show loading popup first
            popup = None
            popup_event = threading.Event()

            if mode == MODE_POPUP:
                logging.info("Spawning translation popup window.")
                def create_popup():
                    nonlocal popup
                    p = PopupWindow(self.config)
                    p.show(
                        loading=True, 
                        target_lang=target_lang_name,
                        original_rtf=selected_rtf,
                        target_lang_code=target_lang_code,
                        original_hwnd=original_hwnd,
                        original_text=selected_text,
                    )
                    popup = p
                    popup_event.set()

                self._run_on_main(create_popup)
                popup_event.wait(timeout=5.0)
                if popup is None:
                    logging.warning(
                        "Loading popup was not created in time (5s); will show result popup after translate."
                    )

            # 3. Translate
            try:
                logging.info(f"Starting translation process to {target_lang_name} ({target_lang_code})...")
                translation = self.translator.translate(selected_text, target_lang_name, target_lang_code)
                translated = translation.text
                provider_used = translation.provider
                logging.info("Translation process completed successfully.")
            except Exception as e:
                err_msg = str(e)
                logging.error(f"Translation failed: {err_msg}")
                if popup:
                    self._run_on_main(
                        lambda msg=err_msg: popup.show_error(msgs.get('err_trans_title', 'Lỗi dịch: {}').format(msg))
                    )
                else:
                    self._show_error_popup(
                        msgs.get('err_trans_title', 'Lỗi dịch: {}').format(err_msg),
                        target_lang_name,
                        target_lang_code,
                    )
                return

            # 4. Output result
            if mode == MODE_POPUP:
                if popup:
                    def _finish_popup():
                        popup.update_text(translated, provider_key=provider_used)
                    self._run_on_main(_finish_popup)
                else:
                    self._show_result_popup(
                        translated,
                        target_lang_name,
                        target_lang_code,
                        selected_rtf,
                        original_hwnd,
                        selected_text,
                        provider_used,
                    )
            elif mode == MODE_REPLACE:
                try:
                    ClipboardUtil.replace_selected_text(
                        translated,
                        selected_rtf,
                        target_lang_code,
                        original_text=selected_text,
                        target_hwnd=original_hwnd,
                    )
                except Exception:
                    def show_fallback():
                        p = PopupWindow(self.config)
                        p.show(
                            translated_text=translated,
                            target_lang=target_lang_name,
                            original_rtf=selected_rtf,
                            target_lang_code=target_lang_code,
                            original_hwnd=original_hwnd,
                            original_text=selected_text,
                            provider_key=provider_used,
                        )
                    self._run_on_main(show_fallback)
        finally:
            self._processing_lock.release()

    def _dismiss_startup_splash(self) -> None:
        win32_splash = getattr(self, "_win32_startup_splash", None)
        if win32_splash is not None:
            self._win32_startup_splash = None
            try:
                win32_splash.close()
            except Exception:
                logging.exception("Failed to close Win32 startup splash")

        splash = self._startup_splash
        if splash is None:
            return
        self._startup_splash = None
        try:
            splash.finish()
        except Exception:
            logging.exception("Failed to close startup splash")

    def _show_settings(self):
        """Open settings window."""
        if not self._gui_ready:
            return

        try:
            # Reuse existing window (visible, minimized, or hidden to tray)
            if self.settings_window and self.settings_window.is_open():
                logging.info("Settings window already exists. Restoring and focusing.")
                self.settings_window.show()
                return

            def on_settings_closed():
                self.settings_window = None

            self.settings_window = SettingsWindow(
                None, self.config, self._on_settings_saved, on_settings_closed, self.hotkey_manager
            )
            self.settings_window.show()
            logging.info("Settings window opened.")
        except Exception as e:
            logging.exception("Failed to open settings window: %s", e)
        finally:
            self._dismiss_startup_splash()

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
        self._dismiss_startup_splash()
        if self.hotkey_manager:
            self.hotkey_manager.stop()
        if self.tray:
            self.tray.stop()
        if hasattr(sys, 'app_mutex') and sys.app_mutex:
            try:
                win32api.CloseHandle(sys.app_mutex)
            except Exception:
                pass
        if getattr(self, "qt_app", None):
            self.qt_app.quit()
        os._exit(0)


def run_app(win32_startup_splash=None) -> None:
    """Entry from bootstrap.py (exe) or ``python main.py`` (dev)."""
    if getattr(sys, "frozen", False):
        _boot_trace("boot: before kill_old_processes")
        kill_old_processes()
        _boot_trace("boot: after kill_old_processes")
    check_single_instance()
    _boot_trace("boot: after check_single_instance")

    app = DirectTransApp()
    app._win32_startup_splash = win32_startup_splash
    app.run()


if __name__ == "__main__":
    run_app()
