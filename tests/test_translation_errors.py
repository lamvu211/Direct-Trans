import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from translator import TranslationError
from translation_errors import user_message_for_translation_error, infer_error_code


class TestTranslationErrors(unittest.TestCase):
    def test_timeout_code(self):
        exc = TranslationError("Timeout: x", code="TIMEOUT")
        self.assertEqual(infer_error_code(exc), "TIMEOUT")
        msg = user_message_for_translation_error(exc, "vi")
        self.assertIn("12 giây", msg)

    def test_http_429_vi(self):
        exc = TranslationError("API error (429)", code="HTTP_429")
        msg = user_message_for_translation_error(exc, "vi")
        self.assertIn("429", msg)

    def test_fallback_en_for_unknown_lang(self):
        exc = TranslationError("Timeout", code="TIMEOUT")
        msg = user_message_for_translation_error(exc, "fr")
        self.assertIn("12s", msg)


if __name__ == "__main__":
    unittest.main()