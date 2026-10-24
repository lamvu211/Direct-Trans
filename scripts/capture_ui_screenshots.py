"""Capture Qt UI screenshots for visual review (Settings, popup, dialogs)."""

from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)

# Use native Windows compositor when available for real pixels.
if "QT_QPA_PLATFORM" not in os.environ:
    pass  # default platform (windows)

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from config import Config
from ui.qt.hotkey_dialog import HotkeyDialog
from ui.qt.hotkey_manage_dialog import HotkeyManageDialog
from ui.qt.popup_window import QtPopupWindow
from ui.qt.settings_window import QtSettingsWindow
from ui.qt.theme import THEME_IDS
from ui.qt.widgets import apply_premium_app


OUT_DIR = os.path.join(ROOT, "docs", "ui-review", "screenshots")


def _save(widget, name: str) -> str:
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, name)
    widget.grab().save(path)
    return path


def main() -> int:
    app = QApplication.instance() or QApplication([])
    apply_premium_app(app)
    from ui.qt.dispatch import set_qt_application

    set_qt_application(app)

    config = Config()
    saved: list[str] = []

    for tid in THEME_IDS:
        config.set_ui_theme(tid)
        win = QtSettingsWindow(config, None, None, None)
        win.show()
        app.processEvents()
        saved.append(_save(win, f"settings_{tid}.png"))
        win.close()

        popup = QtPopupWindow(config=config)
        popup.show(
            translated_text="Sample translation for screenshot review.",
            target_lang="English",
            target_lang_code="en",
            provider_key="gemini",
        )
        app.processEvents()
        saved.append(_save(popup.window, f"popup_result_{tid}.png"))
        popup.close()

        popup_load = QtPopupWindow(config=config)
        popup_load.show(loading=True, target_lang="English", target_lang_code="en")
        app.processEvents()
        saved.append(_save(popup_load.window, f"popup_loading_{tid}.png"))
        popup_load.close()

    config.set_ui_theme("midnight_gold")
    hk = HotkeyDialog(config, config.get_hotkeys())
    hk.show()
    app.processEvents()
    saved.append(_save(hk, "hotkey_dialog_midnight_gold.png"))
    hk.close()

    hk_m = HotkeyManageDialog(config, None, None, lambda: "vi")
    hk_m.show()
    app.processEvents()
    saved.append(_save(hk_m, "hotkey_manage_midnight_gold.png"))
    hk_m.close()

    print("Saved screenshots:")
    for p in saved:
        print(" ", p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
