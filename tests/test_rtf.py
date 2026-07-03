import unittest
import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from clipboard_util import RTFManipulator


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
        self.assertIn('Translated', rtf)
        # Styled control words should remain
        self.assertIn('\\b', rtf)

    def test_create_simple_rtf_fallback(self):
        rtf = RTFManipulator._create_simple_rtf('Hello\tworld', 'Arial')
        self.assertIn('\\tab ', rtf)
        self.assertIn('Hello', rtf)
        self.assertIn('Arial', rtf)


if __name__ == '__main__':
    unittest.main()
