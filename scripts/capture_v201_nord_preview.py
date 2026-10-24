"""Capture baseline (Midnight Gold) vs Nord Snow UI (Settings, popup, hotkey dialogs)."""

from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)

from PySide6.QtWidgets import QApplication

from config import Config
from ui.qt.hotkey_dialog import HotkeyDialog
from ui.qt.hotkey_manage_dialog import HotkeyManageDialog
from ui.qt.popup_window import QtPopupWindow
from ui.qt.settings_window import QtSettingsWindow
from ui.qt.widgets import apply_premium_app

OUT_DIR = os.path.join(ROOT, "docs", "ui-review", "v2.0.1-nord-preview")
BASELINE_THEME = "midnight_gold"
PREVIEW_THEME = "nord_snow"
POPUP_SAMPLE_VI = (
    "Dự thảo sửa đổi quy định về mô hình quản lý, khai thác dữ liệu tập trung, thống nhất…"
)


def _save(widget, name: str) -> str:
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, name)
    widget.grab().save(path)
    return path


def _capture_suite(config: Config, app: QApplication, prefix: str) -> list[str]:
    paths: list[str] = []

    win = QtSettingsWindow(config, None, None, None)
    win.show()
    app.processEvents()
    paths.append(_save(win, f"{prefix}_settings.png"))
    win.close()

    popup = QtPopupWindow(config=config)
    popup.show(
        translated_text=POPUP_SAMPLE_VI,
        target_lang="English",
        target_lang_code="en",
        provider_key="gemini",
    )
    app.processEvents()
    paths.append(_save(popup.window, f"{prefix}_popup.png"))
    popup.close()

    hk = HotkeyDialog(config, config.get_hotkeys())
    hk.show()
    app.processEvents()
    paths.append(_save(hk, f"{prefix}_hotkey_add.png"))
    hk.close()

    hk_m = HotkeyManageDialog(config, None, None, lambda: config.data.get("ui_language", "vi"))
    hk_m.show()
    app.processEvents()
    paths.append(_save(hk_m, f"{prefix}_hotkey_manage.png"))
    hk_m.close()

    return paths


def main() -> int:
    app = QApplication.instance() or QApplication([])
    apply_premium_app(app)
    from ui.qt.dispatch import set_qt_application

    set_qt_application(app)

    config = Config()
    config.data["ui_language"] = "vi"

    saved: list[str] = []

    config.set_ui_theme(BASELINE_THEME)
    saved.extend(_capture_suite(config, app, "current_v201"))

    config.set_ui_theme(PREVIEW_THEME)
    saved.extend(_capture_suite(config, app, "nord_snow"))

    print("Saved preview screenshots:")
    for p in saved:
        print(" ", p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
