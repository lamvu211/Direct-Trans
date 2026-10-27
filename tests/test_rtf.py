import unittest
import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from clipboard_util import ClipboardUtil, RTFManipulator


SIMPLE_RTF = (
    r'{\rtf1\ansi\deff0'
    r'{\fonttbl{\f0 Arial;}}'
    r'\f0 Hello world'
    r'}'
)

MULTI_PARAGRAPH_RTF = (
    r'{\rtf1\ansi\deff0'
    r'{\fonttbl{\f0 Arial;}}'
    r'\f0 Line one\par Line two'
    r'}'
)

NESTED_BRACE_RTF = (
    r'{\rtf1\ansi\deff0'
    r'{\fonttbl{\f0{\*\panose 02020603050405020304}Times New Roman;}}'
    r'\f0 Nested braces test'
    r'}'
)



class TestUnicodePasteHeuristics(unittest.TestCase):
    def test_multiline_single_column_prefers_unicode(self):
        self.assertTrue(
            ClipboardUtil.should_prefer_unicode_paste(
                {"excel": False},
                "Line one\nLine two\nLine three",
                "Dòng một\nDòng hai",
            )
        )

    def test_tabbed_excel_still_prefers_unicode(self):
        self.assertTrue(
            ClipboardUtil.should_prefer_unicode_paste(
                {"excel": True},
                "A\tB\r\nC\tD",
                "X\tY\r\nZ\tW",
            )
        )

    def test_excel_parse_quoted_multiline_cell(self):
        raw = '"line1\nline2"\r\nsecond'
        grid = ClipboardUtil.parse_excel_clipboard(raw)
        self.assertEqual(grid, [["line1\nline2"], ["second"]])

    def test_excel_serialize_quotes_each_cell(self):
        grid = [["a\nb"], ["c"]]
        out = ClipboardUtil.serialize_excel_clipboard(grid)
        self.assertEqual(out, '"a\nb"\r\n"c"')

    def test_excel_two_by_two_grid_roundtrip(self):
        raw = "A\tB\r\nC\tD"
        grid = ClipboardUtil.parse_excel_clipboard(raw)
        self.assertEqual(grid, [["A", "B"], ["C", "D"]])
        out = ClipboardUtil.serialize_excel_clipboard(grid)
        self.assertEqual(
            ClipboardUtil.parse_excel_clipboard(out),
            grid,
        )

    def test_coerce_excel_paste_keeps_quoted_output(self):
        self.assertEqual(
            ClipboardUtil.coerce_excel_paste_text('"Xin chào"', '"Hello"'),
            '"Xin chào"',
        )

    def test_coerce_excel_paste_rewraps_single_cell_if_quotes_dropped(self):
        original = '"line1\nline2"'
        self.assertEqual(
            ClipboardUtil.coerce_excel_paste_text("v1\nv2", original),
            '"v1\nv2"',
        )

    def test_normalize_preserves_excel_row_breaks(self):
        raw = "a\nb\r\nc"
        self.assertEqual(
            ClipboardUtil._normalize_selected_plain_text(raw, excel=True),
            "a\nb\r\nc",
        )
        self.assertEqual(
            ClipboardUtil._normalize_selected_plain_text(raw, excel=False),
            "a\nb\nc",
        )

    def test_excel_clipboard_hint_prefers_unicode(self):
        self.assertTrue(
            ClipboardUtil.should_prefer_unicode_paste(
                {"excel": True},
                "Single line",
                "Một dòng có dấu",
            )
        )

    def test_rtf_likely_excel_compact(self):
        compact = (
            r'{\rtf1\ansi\deff0{\fonttbl{\f0 Arial;}}\f0 Hi\par there}'
        ).encode("latin-1")
        self.assertTrue(RTFManipulator._rtf_likely_excel(compact))

    def test_rtf_not_excel_when_word_stylesheet(self):
        wordish = (
            r'{\rtf1\ansi{\stylesheet{\s0 Normal;}{\fonttbl{\f0 Arial;}}}'
            r'\f0 Hello'
            r'}'
        ).encode("latin-1")
        self.assertFalse(RTFManipulator._rtf_likely_excel(wordish))


class TestRTFTokenizer(unittest.TestCase):
    def test_tokenize_plain_text(self):
        body = r'\f0 Hello'
        tokens = RTFManipulator._tokenize_rtf(body)
        text_parts = [v for t, v in tokens if t == 'text']
        self.assertIn('Hello', ''.join(text_parts))

    def test_tokenize_control_words(self):
        body = r'\b bold \b0'
        tokens = RTFManipulator._tokenize_rtf(body)
        controls = [v for t, v in tokens if t == 'control']
        self.assertTrue(any('\\b' in c for c in controls))

    def test_tokenize_unicode_escape(self):
        body = r'\u23456?'
        tokens = RTFManipulator._tokenize_rtf(body)
        text_parts = [v for t, v in tokens if t == 'text']
        self.assertEqual(len(text_parts), 1)
        self.assertTrue(text_parts[0])

    def test_tokenize_hex_char(self):
        body = r"\'41"
        tokens = RTFManipulator._tokenize_rtf(body)
        text_parts = [v for t, v in tokens if t == 'text']
        self.assertEqual(text_parts[0], 'A')

    def test_escape_rtf_special_chars(self):
        escaped = RTFManipulator._escape_rtf_text('a\\b{c}d\ne\tf')
        self.assertIn('\\\\', escaped)
        self.assertIn('\\{', escaped)
        self.assertIn('\\}', escaped)
        self.assertIn('\\par ', escaped)
        self.assertIn('\\tab ', escaped)


class TestRTFReplace(unittest.TestCase):
    @patch('font_mapper.FontMapper.get_font', return_value='Segoe UI')
    def test_replace_preserves_structure(self, _mock_font):
        result = RTFManipulator.replace_text_preserve_format(
            SIMPLE_RTF.encode('utf-8'), 'Xin chào', 'vi'
        )
        rtf = result.decode('utf-8')
        self.assertIn('Xin ch', rtf)
        self.assertIn('fonttbl', rtf)
        self.assertIn('Segoe UI', rtf)

    @patch('font_mapper.FontMapper.get_font', return_value='Segoe UI')
    def test_replace_multi_paragraph(self, _mock_font):
        result = RTFManipulator.replace_text_preserve_format(
            MULTI_PARAGRAPH_RTF.encode('utf-8'), 'Dòng một\nDòng hai', 'vi'
        )
        rtf = result.decode('utf-8')
        self.assertIn('D', rtf)
        self.assertIn('\\par', rtf)

    @patch('font_mapper.FontMapper.get_font', return_value='Arial')
    def test_replace_puts_text_in_first_token(self, _mock_font):
        styled_rtf = (
            r'{\rtf1\ansi\deff0{\fonttbl{\f0 Arial;}}'
            r'\f0\b bold\b0 normal'
            r'}'
        )
        result = RTFManipulator.replace_text_preserve_format(
            styled_rtf.encode('utf-8'), 'Translated', 'en'
        )
        rtf = result.decode('utf-8')
        plain = rtf.replace('\\', '')
        self.assertIn('Tran', plain)
        self.assertIn('slated', plain)
        # Styled control words should remain
        self.assertIn('\\b', rtf)

    @patch('font_mapper.FontMapper.get_font', return_value='Arial')
    def test_align_extra_translation_lines_merged_into_last(self, _mock_font):
        three_para_rtf = (
            r'{\rtf1\ansi\deff0{\fonttbl{\f0 Arial;}}'
            r'\f0 One\par Two\par Three'
            r'}'
        )
        result = RTFManipulator.replace_text_preserve_format(
            three_para_rtf.encode('utf-8'),
            'A\nB\nC\nD',
            'en',
        )
        rtf = result.decode('utf-8')
        self.assertIn('A', rtf)
        self.assertIn('B', rtf)
        self.assertIn('C', rtf)
        self.assertIn('D', rtf)
        self.assertNotIn('One', rtf)

    def test_align_translation_lines_helper(self):
        self.assertEqual(
            RTFManipulator._align_translation_lines(['a', 'b', 'c'], 2),
            ['a', 'b\nc'],
        )
        self.assertEqual(
            RTFManipulator._align_translation_lines(['only'], 3),
            ['', '', 'only'],
        )

    @patch('font_mapper.FontMapper.get_font', return_value='Arial')
    def test_fewer_translation_lines_uses_simple_rtf_fallback(self, _mock_font):
        """Avoid clearing middle RTF paragraphs when line counts diverge."""
        three_para_rtf = (
            r'{\rtf1\ansi\deff0{\fonttbl{\f0 Arial;}}'
            r'\f0 One\par Two\par Three'
            r'}'
        )
        result = RTFManipulator.replace_text_preserve_format(
            three_para_rtf.encode('utf-8'),
            'Alpha\nBeta',
            'en',
            original_text='One\nTwo\nThree',
        )
        rtf = result.decode('utf-8')
        self.assertIn('Alpha', rtf)
        self.assertIn('Beta', rtf)
        self.assertNotIn('One', rtf)
        self.assertNotIn('Two', rtf)

    def test_map_via_original_lines_merges_split_rtf_paragraphs(self):
        text_paragraphs = [(0, 'Hello'), (1, ' world'), (2, 'Second')]
        original_lines = ['Hello world', 'Second']
        translated_lines = ['Xin chào', 'Hai']
        mapped = RTFManipulator._map_via_original_lines(
            text_paragraphs, original_lines, translated_lines
        )
        self.assertEqual(mapped[0], 'Xin chào')
        self.assertEqual(mapped[1], '')
        self.assertEqual(mapped[2], 'Hai')

    @patch('font_mapper.FontMapper.get_font', return_value='Arial')
    def test_replace_with_nested_fonttbl(self, _mock_font):
        result = RTFManipulator.replace_text_preserve_format(
            NESTED_BRACE_RTF.encode('utf-8'), 'Success', 'en'
        )
        rtf = result.decode('utf-8')
        self.assertIn('Success', rtf)
        # Verify that the nested panose group is preserved
        self.assertIn('\\*\\panose', rtf)
        self.assertIn('Arial', rtf)

    def test_create_simple_rtf_fallback(self):
        rtf = RTFManipulator._create_simple_rtf('Hello\tworld', 'Arial')
        self.assertIn('\\tab ', rtf)
        self.assertIn('Hello', rtf)
        self.assertIn('Arial', rtf)


if __name__ == '__main__':
    unittest.main()
