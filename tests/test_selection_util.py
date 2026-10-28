import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from clipboard_util import ClipboardUtil
from selection_util import capture_selection, is_em_edit_hwnd, restore_selection


class TestSelectionUtil(unittest.TestCase):
    def test_is_em_edit_hwnd(self):
        with patch("selection_util.win32gui.IsWindow", return_value=True):
            with patch("selection_util.win32gui.GetClassName", return_value="Edit"):
                self.assertTrue(is_em_edit_hwnd(1))
            with patch("selection_util.win32gui.GetClassName", return_value="RichEdit20W"):
                self.assertTrue(is_em_edit_hwnd(1))
            with patch("selection_util.win32gui.GetClassName", return_value="Chrome_RenderWidgetHostHWND"):
                self.assertFalse(is_em_edit_hwnd(1))

    def test_capture_skips_non_edit(self):
        with patch("selection_util._foreground_focus_hwnd", return_value=99):
            with patch("selection_util.is_em_edit_hwnd", return_value=False):
                self.assertIsNone(capture_selection())

    def test_em_edit_excludes_wechat_process(self):
        with patch("selection_util.win32gui.IsWindow", return_value=True):
            with patch("selection_util.win32gui.GetClassName", return_value="Edit"):
                with patch(
                    "selection_util.hwnd_process_basename", return_value="weixin.exe"
                ):
                    self.assertFalse(is_em_edit_hwnd(1))

    def test_restore_requires_em_flag(self):
        state = {"focus_hwnd": 1, "sel_start": 0, "sel_end": 3}
        self.assertFalse(restore_selection(state))
        state["em_selection"] = True
        with patch("selection_util.is_em_edit_hwnd", return_value=True):
            with patch("selection_util.win32api.SendMessage", return_value=0) as send:
                self.assertTrue(restore_selection(state))
                send.assert_called_once()

    def test_suspect_stray_c(self):
        self.assertTrue(ClipboardUtil._is_suspect_stray_c_copy("c"))
        self.assertTrue(ClipboardUtil._is_suspect_stray_c_copy("C"))
        self.assertFalse(ClipboardUtil._is_suspect_stray_c_copy("copy"))
        self.assertFalse(ClipboardUtil._is_suspect_stray_c_copy(""))
    def test_prepare_text_selection_for_paste(self):
        from selection_util import prepare_text_selection_for_paste
        self.assertEqual(prepare_text_selection_for_paste(None, 'hello'), 'none')
        state_zalo = {'focus_hwnd': 1, 'em_selection': False, 'fg_process': 'zalo.exe'}
        self.assertEqual(prepare_text_selection_for_paste(state_zalo, 'hello'), 'none')
        state_wechat = {'focus_hwnd': 1, 'em_selection': False, 'fg_process': 'weixin.exe'}
        self.assertEqual(prepare_text_selection_for_paste(state_wechat, 'hello'), 'none')

    def test_safe_clipboard_formats(self):
        import win32con
        self.assertTrue(ClipboardUtil._is_safe_clipboard_format(win32con.CF_UNICODETEXT, 'text'))
        self.assertTrue(ClipboardUtil._is_safe_clipboard_format(win32con.CF_TEXT, b'text'))
        # Non-str/bytes like handles must be rejected
        self.assertFalse(ClipboardUtil._is_safe_clipboard_format(12345, 99999))
        self.assertFalse(ClipboardUtil._is_safe_clipboard_format(12345, None))
