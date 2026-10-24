"""Regression tests for updater NameError fix and settings hide/reopen."""

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from config import Config


class TestUpdaterRegression(unittest.TestCase):
    def test_newer_version_schedules_dialog_without_name_error(self):
        cfg_path_holder = []

        def run_thread_inline(target=None, daemon=None):
            mock = MagicMock()
            mock.start = lambda: target()
            return mock

        with tempfile.TemporaryDirectory() as td:
            cfg_path = os.path.join(td, "cfg.json")
            with patch("config.Config._resolve_config_path", return_value=cfg_path):
                config = Config()

            release = {"tag": "v99.0.0", "name": "Future", "body": ""}
            scheduled = []

            def capture_run_on_main(fn, *args, **kwargs):
                scheduled.append(fn)
                fn()

            with patch("updater._fetch_latest_version", return_value=release), patch(
                "updater._should_prompt", return_value=True
            ), patch("updater.threading.Thread", side_effect=run_thread_inline), patch(
                "ui.qt.dispatch.run_on_main", side_effect=capture_run_on_main
            ) as mock_run_on_main, patch(
                "updater._show_update_dialog"
            ) as mock_show_dialog:
                from updater import check_for_updates_in_background

                check_for_updates_in_background(None, config)

            self.assertEqual(len(scheduled), 1)
            mock_run_on_main.assert_called()
            mock_show_dialog.assert_called_once_with(
                None, config, "v99.0.0", "Future"
            )


class TestVersionSkip(unittest.TestCase):
    def test_skip_version_expires(self):
        import time

        with tempfile.TemporaryDirectory() as td:
            cfg_path = os.path.join(td, "cfg.json")
            with patch("config.Config._resolve_config_path", return_value=cfg_path):
                config = Config()
            config.skip_version("v9.9.9", days=7)
            self.assertTrue(config.is_version_skipped("v9.9.9"))
            config.data["version_skip_until"]["v9.9.9"] = time.time() - 1
            self.assertFalse(config.is_version_skipped("v9.9.9"))


class TestSettingsHideReopenRegression(unittest.TestCase):
    def test_reopen_after_hide_reuses_same_qt_window(self):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PySide6.QtWidgets import QApplication

        QApplication.instance() or QApplication([])

        with tempfile.TemporaryDirectory() as td:
            cfg_path = os.path.join(td, "cfg.json")
            with patch("config.Config._resolve_config_path", return_value=cfg_path):
                cfg = Config()
                from settings_window import SettingsWindow

                sw = SettingsWindow(None, cfg, None, None, None)
                sw.show()
                first = sw._qt
                self.assertIsNotNone(first)
                self.assertTrue(first.isVisible())

                first.hide()
                self.assertFalse(first.isVisible())
                self.assertTrue(sw.is_open())

                sw.show()
                self.assertIs(sw._qt, first)
                self.assertTrue(first.isVisible())

                sw._handle_close()
                self.assertFalse(sw.is_open())


if __name__ == "__main__":
    unittest.main()
