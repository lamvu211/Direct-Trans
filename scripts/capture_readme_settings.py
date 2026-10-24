"""Capture Settings window per theme into src/assets/readme/ (gitignored).

Uses your real Config() — do not commit output to public GitHub. See docs/PUBLIC_REPO.md.
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)

from PySide6.QtWidgets import QApplication

from config import Config
from ui.qt.settings_window import QtSettingsWindow
from ui.qt.theme import THEME_IDS, label_for
from ui.qt.widgets import apply_premium_app

OUT = os.path.join(SRC, "assets", "readme")


def main() -> int:
    app = QApplication.instance() or QApplication([])
    apply_premium_app(app)
    from ui.qt.dispatch import set_qt_application

    set_qt_application(app)

    config = Config()
    config.data["ui_language"] = "vi"
    os.makedirs(OUT, exist_ok=True)

    for tid in THEME_IDS:
        config.set_ui_theme(tid)
        win = QtSettingsWindow(config, None, None, None)
        win.show()
        app.processEvents()
        path = os.path.join(OUT, f"settings_{tid}.png")
        win.grab().save(path)
        print(path, "—", label_for(tid))
        win.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
