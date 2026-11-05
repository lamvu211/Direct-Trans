import unittest
import sys
import os
import requests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from unittest.mock import patch, MagicMock
from translator import (
    BaseHTTPTranslator,
    GeminiTranslator,
    GroqTranslator,
    MistralTranslator,
    GoogleFreeTranslator,
    TranslationError,
    clean_model_output,
)


def _mock_http_session(mock_session_class):
    mock_session = MagicMock()
    mock_session_class.return_value = mock_session
    return mock_session


class TestTranslator(unittest.TestCase):
    @patch('translator.requests.Session')
    def test_gemini_translator(self, mock_session_class):
        mock_session = _mock_http_session(mock_session_class)
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "Xin chào"}]}}]
        }
        mock_session.post.return_value = mock_resp

        t = GeminiTranslator()
        res = t.translate("Hello", "Vietnamese", "vi", api_key="test_key", model="gemini-pro")
        self.assertEqual(res, "Xin chào")

        mock_resp.raise_for_status.side_effect = Exception("Bad Request")
        with self.assertRaises(TranslationError):
            t.translate("Hello", "Vietnamese", "vi", api_key="test_key", model="gemini-pro")

    @patch('translator.requests.Session')
    def test_gemini_blocked_response(self, mock_session_class):
        mock_session = _mock_http_session(mock_session_class)
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "candidates": [],
            "promptFeedback": {"blockReason": "SAFETY"},
        }
        mock_session.post.return_value = mock_resp

        t = GeminiTranslator()
        with self.assertRaises(TranslationError) as ctx:
            t.translate("Hello", "Vietnamese", "vi", api_key="test_key", model="gemini-pro")
        self.assertIn("refused", str(ctx.exception).lower())

    def test_clean_model_output(self):
        self.assertEqual(
            clean_model_output("<think>x</think>Hi"),
            "Hi",
        )
        self.assertEqual(
            clean_model_output("<think>a</think>Hi<thinking>b</thinking>"),
            "Hi",
        )
        redacted = "redacted_thinking"
        self.assertEqual(
            clean_model_output(f"<{redacted}>x</{redacted}>Hello"),
            "Hello",
        )
        self.assertEqual(
            clean_model_output(
                "<text>\nCố định Pemnut vào sản phẩm\nƯu điểm: Giảm tỷ lệ lệch tâm của đai ốc\n</text>"
            ),
            "Cố định Pemnut vào sản phẩm\nƯu điểm: Giảm tỷ lệ lệch tâm của đai ốc",
        )
        self.assertEqual(
            clean_model_output("<text>Hello</text>"),
            "Hello",
        )

    @patch('translator.requests.Session')
    def test_groq_translator(self, mock_session_class):
        mock_session = _mock_http_session(mock_session_class)
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "<think>Thinking...</think>Xin chào"}}]
        }
        mock_session.post.return_value = mock_resp

        t = GroqTranslator()
        res = t.translate("Hello", "Vietnamese", "vi", api_key="test_key", model="llama")
        self.assertEqual(res, "<think>Thinking...</think>Xin chào")

    @patch('translator.requests.Session')
    def test_mistral_translator(self, mock_session_class):
        mock_session = _mock_http_session(mock_session_class)
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "Xin chào"}}]
        }
        mock_session.post.return_value = mock_resp

        t = MistralTranslator()
        res = t.translate("Hello", "Vietnamese", "vi", api_key="test_key", model="mistral")
        self.assertEqual(res, "Xin chào")

    @patch('translator.requests.Session')
    def test_google_free_translator(self, mock_session_class):
        mock_session = _mock_http_session(mock_session_class)
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = [
            [["Xin chào", "Hello", None, None, 1]], None, "en"
        ]
        mock_session.post.return_value = mock_resp

        t = GoogleFreeTranslator()
        res = t.translate("Hello", "Vietnamese", "vi")
        self.assertEqual(res, "Xin chào")
        self.assertTrue(mock_session.post.called)

    @patch('translator.requests.Session')
    def test_session_recreated_after_connection_error(self, mock_session_class):
        mock_session = _mock_http_session(mock_session_class)
        mock_session.post.side_effect = requests.exceptions.ConnectionError("broken pipe")

        t = GeminiTranslator()
        with self.assertRaises(TranslationError):
            t.translate("Hi", "English", "en", api_key="k", model="gemini-pro")
        self.assertEqual(mock_session.post.call_count, 1)
        mock_session.close.assert_called()


if __name__ == '__main__':
    unittest.main()
