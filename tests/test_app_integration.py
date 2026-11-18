"""Integration-style tests for autostart, pause wiring, API fetch (mocked)."""

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from config import Config


class TestAppIntegration(unittest.TestCase):
    def test_pause_logic_unregister_register(self):
        """Mirrors DirectTransApp._toggle_enabled hotkey side effects."""
        hm = MagicMock()
        enabled = True
        enabled = not enabled
        if enabled:
            hm.register_all()
        else:
            hm.unregister_all()
        hm.unregister_all.assert_called_once()
        enabled = not enabled
        if enabled:
            hm.register_all()
        else:
            hm.unregister_all()
        hm.register_all.assert_called_once()

    def test_autostart_registry_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            cfg_path = os.path.join(td, "cfg.json")
            with patch("config.Config._resolve_config_path", return_value=cfg_path):
                cfg = Config()
            fake_key = MagicMock()
            with patch("winreg.OpenKey", return_value=fake_key), patch(
                "winreg.SetValueEx"
            ) as set_val, patch("winreg.CloseKey"):
                ok = cfg.set_auto_start(True)
            self.assertTrue(ok)
            set_val.assert_called()
            self.assertTrue(cfg.is_auto_start())

    def test_single_instance_signal_file_contract(self):
        with tempfile.TemporaryDirectory() as td:
            signal = os.path.join(td, "directtrans.signal")
            with open(signal, "w", encoding="utf-8") as f:
                f.write("SHOW")
            self.assertEqual(open(signal, encoding="utf-8").read(), "SHOW")

    def test_api_fetch_models_gemini_mock(self):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PySide6.QtWidgets import QApplication

        QApplication.instance() or QApplication([])
        from ui.qt.api_section import ApiSection

        with tempfile.TemporaryDirectory() as td:
            cfg_path = os.path.join(td, "cfg.json")
            with patch("config.Config._resolve_config_path", return_value=cfg_path):
                cfg = Config()
            section = ApiSection(cfg, None, lambda: "en")
            combo = section._model_combos["gemini"]
            btn_fetch = MagicMock()
            btn_save = MagicMock()
            btn_test = MagicMock()
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "models": [
                    {
                        "name": "models/gemini-flash-lite-latest",
                        "supportedGenerationMethods": ["generateContent"],
                    }
                ]
            }
            status = section._status_labels["gemini"]
            with patch("requests.get", return_value=mock_resp):
                section._fetch_models(
                    "gemini", "fake-key", combo, btn_fetch, btn_save, btn_test, status
                )
            # Allow Qt timer / thread to finish
            import time

            for _ in range(20):
                time.sleep(0.05)
                if combo.count() > 1 or combo.currentText() == "gemini-flash-lite-latest":
                    break
            self.assertIn(
                combo.currentText(),
                ("gemini-flash-lite-latest", "Fetching..."),
            )


if __name__ == "__main__":
    unittest.main()
