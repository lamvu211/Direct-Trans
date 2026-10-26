import unittest
import sys
import os
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

class TestTranslator(unittest.TestCase):
    @patch('translator.requests.post')
    def test_gemini_translator(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": "Xin chào"}]}}]
        }
        mock_post.return_value = mock_resp
        
        t = GeminiTranslator()
        res = t.translate("Hello", "Vietnamese", "vi", api_key="test_key", model="gemini-pro")
        self.assertEqual(res, "Xin chào")
        
        # Test error handling
        mock_resp.raise_for_status.side_effect = Exception("Bad Request")
        with self.assertRaises(TranslationError):
            t.translate("Hello", "Vietnamese", "vi", api_key="test_key", model="gemini-pro")

    @patch('translator.requests.post')
    def test_gemini_blocked_response(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "candidates": [],
            "promptFeedback": {"blockReason": "SAFETY"},
        }
        mock_post.return_value = mock_resp

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

    @patch('translator.requests.post')
    def test_groq_translator(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "<think>Thinking...</think>Xin chào"}}]
        }
        mock_post.return_value = mock_resp
        
        t = GroqTranslator()
        res = t.translate("Hello", "Vietnamese", "vi", api_key="test_key", model="llama")
        self.assertEqual(res, "<think>Thinking...</think>Xin chào")
        
    @patch('translator.requests.post')
    def test_mistral_translator(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "Xin chào"}}]
        }
        mock_post.return_value = mock_resp
        
        t = MistralTranslator()
        res = t.translate("Hello", "Vietnamese", "vi", api_key="test_key", model="mistral")
        self.assertEqual(res, "Xin chào")
        
    @patch('translator.requests.post')
    def test_google_free_translator(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = [
            [["Xin chào", "Hello", None, None, 1]], None, "en"
        ]
        mock_post.return_value = mock_resp
        
        t = GoogleFreeTranslator()
        res = t.translate("Hello", "Vietnamese", "vi")
        self.assertEqual(res, "Xin chào")
        self.assertTrue(mock_post.called)

if __name__ == '__main__':
    unittest.main()
