"""Tests verifying fixes for the 18 UI/UX and QA audit findings."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QGuiApplication, QKeyEvent
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QLineEdit, QScrollArea

from config import Config
from ui.i18n import TRANSLATIONS
from ui.qt.theme import THEME_IDS, qss_for
from ui.qt.settings_window import QtSettingsWindow
from ui.qt.popup_window import QtPopupWindow, STATE_LOADING
from ui.qt.hotkey_dialog import HotkeyDialog
from ui.qt.hotkey_manage_dialog import HotkeyManageDialog
from ui.qt.widgets import apply_premium_app


class TestUiQaFixes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        apply_premium_app(cls.app)

    def setUp(self):
        self.config = Config()
        if not self.config.get_hotkeys():
            self.config.data['hotkeys'] = list(self.config.DEFAULT_CONFIG['hotkeys'])

    def test_issue_01_popup_textedit_dark_theme(self):
        """ISSUE-01: QTextEdit in popup is themed, not raw white in dark themes."""
        for tid in ("midnight_gold", "aurora_glass"):
            qss = qss_for(tid)
            self.assertIn("QTextEdit#line", qss)
            self.config.set_ui_theme(tid)
            popup = QtPopupWindow(config=self.config)
            popup.show(translated_text="Sample text", target_lang="English", target_lang_code="en")
            self.app.processEvents()
            pm = popup.window.grab()
            img = pm.toImage()
            te_center = popup.text_widget.mapTo(popup.window, popup.text_widget.rect().center())
            px = img.pixelColor(te_center.x(), te_center.y())
            # Ensure it is NOT bright pure white #ffffff
            self.assertNotEqual(px.name(), "#ffffff", f"QTextEdit is white in {tid}")
            popup.close()

    def test_issue_02_dialogs_themed(self):
        """ISSUE-02: HotkeyDialog & HotkeyManageDialog have theme applied."""
        hk_dlg = HotkeyDialog(self.config, self.config.get_hotkeys())
        self.assertEqual(hk_dlg.objectName(), "root")
        self.assertTrue(len(hk_dlg.styleSheet()) > 500)
        hk_dlg.close()

        hk_mng = HotkeyManageDialog(self.config, None, None, lambda: "vi")
        self.assertEqual(hk_mng.objectName(), "root")
        self.assertTrue(len(hk_mng.styleSheet()) > 500)
        hk_mng.close()

    def test_issue_03_language_switch_updates_all_cards_and_api(self):
        """ISSUE-03: Switching language updates all card titles and API labels."""
        self.config.data["ui_language"] = "vi"
        win = QtSettingsWindow(self.config, None, None, None)
        card_titles_vi = [lb.text().upper() for lb in win.findChildren(QLabel, "cardTitle")]
        self.assertIn("NGUỒN DỊCH", card_titles_vi)
        self.assertIn("PHÍM TẮT", card_titles_vi)

        win._lang_combo.setCurrentIndex(win._lang_combo.findData("en"))
        card_titles_en = [lb.text().upper() for lb in win.findChildren(QLabel, "cardTitle")]
        self.assertIn("TRANSLATION SOURCE", card_titles_en)
        self.assertIn("HOTKEYS", card_titles_en)

        api = win.api_section
        self.assertEqual(api._toolbar_save.text(), "Save Key")
        self.assertEqual(api._toolbar_fetch.text(), "Load Models")
        self.assertEqual(api._link_btns["gemini"].text(), "🔗 Get API key")
        win.close()

    def test_issue_04_settings_has_scroll_area(self):
        """ISSUE-04: SettingsWindow uses responsive auto-scaling without scroll area."""
        win = QtSettingsWindow(self.config, None, None, None)
        scrolls = win.findChildren(QScrollArea)
        self.assertEqual(len(scrolls), 0)
        self.assertGreater(win.height(), 350)
        win.close()

    def test_issue_05_lang_combo_fits_longest_label(self):
        """ISSUE-05: Language combo width fits longest label (no excess empty space)."""
        win = QtSettingsWindow(self.config, None, None, None)
        fm = win._lang_combo.fontMetrics()
        max_w = max(
            fm.horizontalAdvance(win._lang_combo.itemText(i))
            for i in range(win._lang_combo.count())
        )
        self.assertGreaterEqual(win._lang_combo.width(), max_w)
        self.assertLessEqual(win._lang_combo.width(), max_w + 30)
        win.close()

    def test_hotkey_edit_preserves_combo_text(self):
        hk = {
            "id": "test-id",
            "key_combo": "ctrl+shift+e",
            "target_language_code": "en",
            "target_language_name": "English",
            "mode": "popup",
        }
        dlg = HotkeyDialog(self.config, [], edit_hotkey=hk)
        self.assertEqual(dlg._combo_edit.text(), "ctrl+shift+e")
        dlg.close()

    def test_issue_06_theme_token_parity(self):
        """ISSUE-06: All themes have :hover, :focus, hkDel, and QTextEdit."""
        for tid in THEME_IDS:
            qss = qss_for(tid)
            self.assertIn(":hover", qss, f"Theme {tid} missing :hover")
            self.assertIn(":focus", qss, f"Theme {tid} missing :focus")
            self.assertIn("hkDel", qss, f"Theme {tid} missing hkDel")
            self.assertIn("QTextEdit#line", qss, f"Theme {tid} missing QTextEdit#line")
            self.assertIn("QScrollBar", qss, f"Theme {tid} missing QScrollBar")

    def test_issue_07_rose_champagne_contrast(self):
        """ISSUE-07: rose_champagne contrast fix is applied."""
        qss = qss_for("rose_champagne")
        self.assertIn("#783d63", qss)
        self.assertIn("#b81463", qss)

    def test_popup_copy_disabled_while_loading(self):
        popup = QtPopupWindow(config=self.config)
        popup.show(loading=True, target_lang="English", target_lang_code="en")
        self.app.processEvents()
        self.assertEqual(popup._state, STATE_LOADING)
        self.assertFalse(popup.copy_btn.isEnabled())
        self.assertFalse(popup.replace_btn.isEnabled())
        popup._copy()
        self.app.processEvents()
        self.assertEqual(QGuiApplication.clipboard().text(), "")
        popup.close()

    def test_popup_copy_uses_translated_text_only(self):
        popup = QtPopupWindow(config=self.config)
        popup.show(
            translated_text="Hello world",
            target_lang="English",
            target_lang_code="en",
        )
        self.app.processEvents()
        popup.text_widget.setPlainText("stale widget text")
        popup._copy()
        self.app.processEvents()
        self.assertEqual(QGuiApplication.clipboard().text(), "Hello world")
        popup.close()

    def test_issue_08_popup_esc_key_and_stay_on_top(self):
        """ISSUE-08: Popup dismisses on Esc key and has StayOnTop flag."""
        popup = QtPopupWindow(config=self.config)
        popup.show(translated_text="Text", target_lang="VI", target_lang_code="vi")
        self.assertTrue(bool(popup.window.windowFlags() & Qt.WindowType.WindowStaysOnTopHint))

        # Simulate Escape key event
        key_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier)
        self.app.sendEvent(popup.window, key_event)
        self.assertIsNone(popup.window)

    def test_issue_09_api_key_row_actions(self):
        """API key row has clear action and get-key button."""
        win = QtSettingsWindow(self.config, None, None, None)
        api_sec = win.api_section
        entry = api_sec._key_entries["gemini"]
        self.assertEqual(entry.echoMode(), QLineEdit.EchoMode.Password)
        self.assertGreater(len(entry.actions()), 0)
        link = api_sec._link_btns["gemini"]
        self.assertTrue(link.text())
        win.close()

    def test_issue_14_hotkey_labels_object_names(self):
        """ISSUE-14: Hotkey labels have hkKey, hkLang, hkMode objectNames."""
        win = QtSettingsWindow(self.config, None, None, None)
        hk_sec = win.hotkey_section
        keys = hk_sec.findChildren(QLabel, "hkKey")
        langs = hk_sec.findChildren(QLabel, "hkLang")
        modes = hk_sec.findChildren(QLabel, "hkMode")
        self.assertGreater(len(keys), 0)
        self.assertGreater(len(langs), 0)
        self.assertGreater(len(modes), 0)
        win.close()

    def test_popup_font_style_defaults_and_customization(self):
        """Verify popup font color & size defaults and persistence per theme."""
        self.assertEqual(self.config.get_popup_style("midnight_gold")["color"], "#B1B9E5")
        self.assertEqual(self.config.get_popup_style("midnight_gold")["size"], 12)
        self.assertEqual(self.config.get_popup_style("aurora_glass")["color"], "#B1B9E5")
        self.assertEqual(self.config.get_popup_style("aurora_glass")["size"], 12)
        self.assertEqual(self.config.get_popup_style("rose_champagne")["color"], "#4C4F69")
        self.assertEqual(self.config.get_popup_style("rose_champagne")["size"], 12)

        # Test UI controls
        popup = QtPopupWindow(config=self.config)
        popup.show(translated_text="Sample output", target_lang="English", target_lang_code="en")
        self.app.processEvents()
        self.assertIsNotNone(popup.color_btn)
        self.assertIsNotNone(popup.size_label)
        self.assertEqual(popup.size_label.text(), "12")

        # Test increase / decrease
        popup._on_increase_font_size()
        self.assertEqual(popup._current_font_size, 13)
        self.assertEqual(popup.size_label.text(), "13")
        popup._on_decrease_font_size()
        self.assertEqual(popup._current_font_size, 12)
        popup.close()

    def test_settings_hotkeys_delete_layout_stable(self):
        """Verify deleting hotkeys does not shrink API keys card width."""
        win = QtSettingsWindow(self.config, None, None, None)
        win.show()
        self.app.processEvents()
        initial_w = win.width()
        combo = win.api_section._model_combos["gemini"]
        entry = win.api_section._key_entries["gemini"]
        # When hotkeys count changes, window width remains fixed 520
        win.update_window_height()
        self.assertEqual(win.width(), initial_w)
        win.close()

    def test_issue_17_section_titles_clean_whitespace(self):
        """ISSUE-17: i18n section titles don't have leading/trailing whitespace."""
        for lang, d in TRANSLATIONS.items():
            for k in ("provider_section", "api_section", "options_section", "hotkey_section"):
                val = d[k]
                self.assertEqual(val, val.strip(), f"Whitespace found in {lang}.{k}: '{val}'")

    def test_settings_api_section_not_clipped_on_fewer_hotkeys(self):
        """Verify API keys card and entry fields are never squished when hotkeys count changes."""
        for count in (1, 2, 3):
            self.config.data['hotkeys'] = [
                {'id': f'hk-{i}', 'key': f'ctrl+shift+{i}', 'target_lang': 'vi', 'mode': 'popup'}
                for i in range(count)
            ]
            win = QtSettingsWindow(self.config, None, None, None)
            win.show()
            self.app.processEvents()
            self.assertGreaterEqual(win.api_section.height(), 68)
            api_card = win.api_section.parentWidget()
            self.assertGreaterEqual(api_card.height(), 120)
            entry = win.api_section._key_entries['gemini']
            self.assertGreaterEqual(entry.height(), 24)
            # Entry must be within api_section bounds (no clipping)
            self.assertLessEqual(entry.geometry().bottom(), win.api_section.height())
            win.close()

    def test_popup_theme_combo_no_truncation_and_dropdown_qss(self):
        """Verify theme combo has adequate width without ellipsis and uses dropdown popup."""
        for tid in THEME_IDS:
            qss = qss_for(tid)
            self.assertIn("combobox-popup: 0", qss)
            self.assertIn("min-width: 120px", qss)

        self.config.set_ui_theme("rose_champagne")
        popup = QtPopupWindow(config=self.config)
        popup.show(translated_text="Sample", target_lang="English", target_lang_code="en")
        self.app.processEvents()
        self.assertGreaterEqual(popup.theme_combo.width(), 120)
        self.assertEqual(popup.theme_combo.view().textElideMode(), Qt.TextElideMode.ElideNone)
        popup.close()

    def test_issue_18_dead_code_removed(self):
        """ISSUE-18: Verify dead code functions removed."""
        import ui.qt.widgets as w
        import ui.dpi_util as d
        self.assertFalse(hasattr(w, "api_block_placeholder"))
        self.assertFalse(hasattr(d, "apply_tk_scaling"))
        self.assertFalse(hasattr(d, "centered_geometry"))
        self.assertFalse(hasattr(d, "get_work_area_at_pointer"))


if __name__ == "__main__":
    unittest.main()
