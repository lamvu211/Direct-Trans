import unittest
import sys
import os
import tempfile
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from config import Config
from constants import (
    PROVIDER_GEMINI,
    PROVIDER_GROQ,
    PROVIDER_MISTRAL,
    PROVIDER_GOOGLE_FREE,
)
from translator import TranslationManager, TranslationError, TranslationBackend


class StubBackend(TranslationBackend):
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = []

    def translate(self, text: str, target_lang_name: str, target_lang_code: str, **kwargs) -> str:
        self.calls.append({'text': text, 'target_lang_name': target_lang_name, 'target_lang_code': target_lang_code, 'kwargs': kwargs})
        if self.error:
            raise self.error
        return self.result


class MockConfig:
    def __init__(self, provider=PROVIDER_GEMINI, fallback_enabled=True,
                 fallback_order=None, api_keys=None):
        self.data = {
            'translation_provider': provider,
            'fallback_enabled': fallback_enabled,
            'fallback_order': fallback_order or [
                PROVIDER_GEMINI, PROVIDER_GROQ, PROVIDER_MISTRAL, PROVIDER_GOOGLE_FREE,
            ],
        }
        self._api_keys = api_keys or {}

    def get_provider(self):
        return self.data['translation_provider']

    def get_api_key(self, provider):
        return self._api_keys.get(provider, '')

    def get_gemini_model(self):
        return 'gemini-test'

    def get_groq_model(self):
        return 'groq-test'

    def get_mistral_model(self):
        return 'mistral-test'


class TestFallbackChain(unittest.TestCase):
    def _manager_with_stubs(self, config, stubs):
        mgr = TranslationManager(config)
        mgr.backends = stubs
        return mgr

    def test_primary_succeeds_no_fallback(self):
        config = MockConfig(api_keys={PROVIDER_GEMINI: 'key1'})
        gemini = StubBackend(result='Xin chào')
        mgr = self._manager_with_stubs(config, {
            PROVIDER_GEMINI: gemini,
            PROVIDER_GROQ: StubBackend(result='should not run'),
        })
        result = mgr.translate('Hello', 'Vietnamese', 'vi')
        self.assertEqual(result, 'Xin chào')
        self.assertEqual(len(gemini.calls), 1)

    def test_fallback_on_primary_failure(self):
        config = MockConfig(api_keys={
            PROVIDER_GEMINI: 'key1',
            PROVIDER_GROQ: 'key2',
        })
        gemini = StubBackend(error=TranslationError('rate limited'))
        groq = StubBackend(result='Hello from Groq')
        mgr = self._manager_with_stubs(config, {
            PROVIDER_GEMINI: gemini,
            PROVIDER_GROQ: groq,
            PROVIDER_MISTRAL: StubBackend(result='skip'),
            PROVIDER_GOOGLE_FREE: StubBackend(result='skip'),
        })
        result = mgr.translate('Hello', 'Vietnamese', 'vi')
        self.assertEqual(result, 'Hello from Groq')
        self.assertEqual(len(gemini.calls), 1)
        self.assertEqual(len(groq.calls), 1)

    def test_skips_providers_without_api_key(self):
        config = MockConfig(api_keys={PROVIDER_GROQ: 'key2'})
        gemini = StubBackend(result='should skip')
        groq = StubBackend(result='Groq OK')
        mgr = self._manager_with_stubs(config, {
            PROVIDER_GEMINI: gemini,
            PROVIDER_GROQ: groq,
        })
        result = mgr.translate('Hello', 'Vietnamese', 'vi')
        self.assertEqual(result, 'Groq OK')
        self.assertEqual(len(gemini.calls), 0)
        self.assertEqual(len(groq.calls), 1)

    def test_google_free_works_without_api_key(self):
        config = MockConfig(
            provider=PROVIDER_GOOGLE_FREE,
            api_keys={},
        )
        google = StubBackend(result='Free translate')
        mgr = self._manager_with_stubs(config, {
            PROVIDER_GEMINI: StubBackend(result='skip'),
            PROVIDER_GOOGLE_FREE: google,
        })
        result = mgr.translate('Hello', 'Vietnamese', 'vi')
        self.assertEqual(result, 'Free translate')
        self.assertEqual(len(google.calls), 1)

    def test_fallback_disabled_only_tries_primary(self):
        config = MockConfig(
            fallback_enabled=False,
            api_keys={PROVIDER_GEMINI: 'key1'},
        )
        gemini = StubBackend(error=TranslationError('fail'))
        groq = StubBackend(result='should not run')
        mgr = self._manager_with_stubs(config, {
            PROVIDER_GEMINI: gemini,
            PROVIDER_GROQ: groq,
        })
        with self.assertRaises(TranslationError):
            mgr.translate('Hello', 'Vietnamese', 'vi')
        self.assertEqual(len(groq.calls), 0)

    def test_strips_redacted_thinking_tags(self):
        config = MockConfig(api_keys={PROVIDER_GEMINI: 'key1'})
        gemini = StubBackend(result='<think>reasoning</think>Xin chào')
        mgr = self._manager_with_stubs(config, {PROVIDER_GEMINI: gemini})
        result = mgr.translate('Hello', 'Vietnamese', 'vi')
        self.assertEqual(result, 'Xin chào')

    def test_all_providers_fail_raises(self):
        config = MockConfig(api_keys={
            PROVIDER_GEMINI: 'k1',
            PROVIDER_GROQ: 'k2',
        })
        mgr = self._manager_with_stubs(config, {
            PROVIDER_GEMINI: StubBackend(error=TranslationError('a')),
            PROVIDER_GROQ: StubBackend(error=TranslationError('b')),
            PROVIDER_MISTRAL: StubBackend(error=TranslationError('c')),
            PROVIDER_GOOGLE_FREE: StubBackend(error=TranslationError('d')),
        })
        with self.assertRaises(TranslationError) as ctx:
            mgr.translate('Hello', 'Vietnamese', 'vi')
        self.assertIn('All translation providers failed', str(ctx.exception))


class TestConfigSetup(unittest.TestCase):
    def test_is_first_run_when_config_created(self):
        with tempfile.TemporaryDirectory() as td:
            cfg_path = os.path.join(td, 'config.json')
            with patch('config.Config._resolve_config_path', return_value=cfg_path):
                cfg = Config()
                self.assertTrue(cfg.is_first_run())
                self.assertTrue(cfg.needs_setup())

    def test_needs_setup_when_primary_missing_key(self):
        with tempfile.TemporaryDirectory() as td:
            cfg_path = os.path.join(td, 'config.json')
            with patch('config.Config._resolve_config_path', return_value=cfg_path):
                cfg = Config()
                cfg._was_created = False
                cfg.data['translation_provider'] = PROVIDER_GEMINI
                self.assertTrue(cfg.needs_setup())

    def test_no_setup_when_api_key_present(self):
        with tempfile.TemporaryDirectory() as td:
            cfg_path = os.path.join(td, 'config.json')
            with patch('config.Config._resolve_config_path', return_value=cfg_path):
                cfg = Config()
                cfg._was_created = False
                cfg.set_api_key(PROVIDER_GEMINI, 'secret')
                self.assertFalse(cfg.needs_setup())

    def test_no_setup_when_google_free_primary(self):
        with tempfile.TemporaryDirectory() as td:
            cfg_path = os.path.join(td, 'config.json')
            with patch('config.Config._resolve_config_path', return_value=cfg_path):
                cfg = Config()
                cfg._was_created = False
                cfg.data['translation_provider'] = PROVIDER_GOOGLE_FREE
                self.assertFalse(cfg.needs_setup())


if __name__ == '__main__':
    unittest.main()
