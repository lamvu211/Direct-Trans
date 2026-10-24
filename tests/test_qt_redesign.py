"""Automated checks for Qt settings/theme redesign (v2.0)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from config import Config
from ui.qt.hotkey_section import HOTKEYS_COLLAPSED_COUNT
from ui.qt.theme import DEFAULT_THEME_ID, THEME_IDS, qss_for, tagline_for


class TestQtRedesign(unittest.TestCase):
    def test_theme_registry(self):
        self.assertEqual(len(THEME_IDS), 3)
        self.assertEqual(DEFAULT_THEME_ID, "midnight_gold")
        for tid in THEME_IDS:
            self.assertIn(tid, ("midnight_gold", "aurora_glass", "rose_champagne"))
            self.assertGreater(len(qss_for(tid)), 500)
            self.assertTrue(tagline_for(tid))

    def test_hotkeys_collapsed_count(self):
        self.assertEqual(HOTKEYS_COLLAPSED_COUNT, 5)

    def test_no_tkinter_in_src(self):
        src = os.path.join(os.path.dirname(__file__), "../src")
        for root, _dirs, files in os.walk(src):
            for name in files:
                if not name.endswith(".py"):
                    continue
                path = os.path.join(root, name)
                with open(path, encoding="utf-8") as f:
                    text = f.read()
                self.assertNotIn("import tkinter", text, msg=path)
                self.assertNotIn("from tkinter", text, msg=path)

    def test_settings_window_smoke_offscreen(self):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance() or QApplication([])
        from unittest.mock import patch
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            cfg_path = os.path.join(td, "cfg.json")
            with patch("config.Config._resolve_config_path", return_value=cfg_path):
                cfg = Config()
                cfg.set_ui_theme("rose_champagne")
                from ui.qt.settings_window import QtSettingsWindow

                win = QtSettingsWindow(cfg, None, None, None)
                self.assertEqual(win.width(), win.minimumWidth())
                self.assertEqual(win.height(), win.minimumHeight())
                self.assertIn("rose_champagne", cfg.get_ui_theme())
                win.close()

    def test_popup_facade_import(self):
        from popup_window import PopupWindow

        self.assertIs(PopupWindow.__name__, "QtPopupWindow")

    def test_run_on_main_from_background_thread(self):
        import threading
        import time

        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PySide6.QtWidgets import QApplication

        from ui.qt.dispatch import run_on_main, set_qt_application

        app = QApplication.instance() or QApplication([])
        set_qt_application(app)
        seen = []

        def worker():
            run_on_main(lambda: seen.append(True))

        threading.Thread(target=worker, daemon=True).start()
        for _ in range(100):
            app.processEvents()
            if seen:
                break
            time.sleep(0.01)
        self.assertEqual(seen, [True])


if __name__ == "__main__":
    unittest.main()
