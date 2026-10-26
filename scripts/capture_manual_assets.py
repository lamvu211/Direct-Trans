"""Capture screenshots into src/assets for README and user_manual.html.

Uses your real Config() — do not commit PNGs if they show personal provider/model/hotkeys.
See docs/PUBLIC_REPO.md.
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, SRC)

from PySide6.QtWidgets import QApplication

from screenshot_config import POPUP_README_SAMPLE_TEXT, make_public_screenshot_config
from ui.qt.hotkey_dialog import HotkeyDialog
from ui.qt.hotkey_manage_dialog import HotkeyManageDialog
from ui.qt.popup_window import QtPopupWindow
from ui.qt.settings_window import QtSettingsWindow
from ui.qt.widgets import apply_premium_app


ASSETS = os.path.join(SRC, "assets")


def _save(widget, filename: str) -> str:
    os.makedirs(ASSETS, exist_ok=True)
    path = os.path.join(ASSETS, filename)
    widget.grab().save(path)
    return path


def main() -> int:
    app = QApplication.instance() or QApplication([])
    apply_premium_app(app)
    from ui.qt.dispatch import set_qt_application

    set_qt_application(app)

    config = make_public_screenshot_config()
    config.set_ui_theme("aurora_glass")

    win = QtSettingsWindow(config, None, None, None)
    win.show()
    app.processEvents()
    paths = [_save(win, "screenshot_settings.png")]

    popup = QtPopupWindow(config=config)
    popup.show(
        translated_text=POPUP_README_SAMPLE_TEXT,
        target_lang="English",
        target_lang_code="en",
        provider_key="gemini",
    )
    app.processEvents()
    paths.append(_save(popup.window, "screenshot_popup.png"))
    popup.close()

    hk = HotkeyDialog(config, config.get_hotkeys())
    hk.show()
    app.processEvents()
    paths.append(_save(hk, "screenshot_hotkey_dialog.png"))
    hk.close()

    hk_m = HotkeyManageDialog(config, None, None, lambda: config.data.get("ui_language", "en"))
    hk_m.show()
    app.processEvents()
    paths.append(_save(hk_m, "screenshot_hotkey_manage.png"))
    hk_m.close()

    win.close()

    # Optional: copy tray is not capturable easily; settings is enough for README.
    print("Saved manual assets:")
    for p in paths:
        print(" ", p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
