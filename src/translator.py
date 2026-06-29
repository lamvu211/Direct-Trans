"""
translator.py - Translation backends (Gemini, DeepL, Google Free) with fallback chain and LRU cache.
"""

import requests
import logging
from abc import ABC, abstractmethod


class TranslationError(Exception):
    pass


class TranslationBackend(ABC):
    @abstractmethod
    def translate(self, text: str, target_lang: str) -> str:
        """Translate text to target_lang. Raise TranslationError on failure."""
        pass


class GeminiTranslator(TranslationBackend):
    def __init__(self):
        self.api_key = ""
        self.model = "gemini-3.1-flash-lite"

    @property
    def api_url(self):
        return f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def translate(self, text: str, target_lang: str) -> str:
        if not self.api_key:
            raise TranslationError("Gemini API key not configured")

        payload = {
            "systemInstruction": {
                "parts": [{"text": f"You are a professional translator. Translate the given text to {target_lang}. Return ONLY the translated text, no explanations, no extra formatting. Preserve all line breaks, punctuation, and paragraph structure exactly."}]
            },
            "contents": [{
                "parts": [{"text": text}]
            }],
            "generationConfig": {
                "temperature": 0.3
            }
        }

        import time
        max_retries = 3
        retry_delay = 1.0  # 1 second

        for attempt in range(max_retries):
            try:
                resp = requests.post(
                    self.api_url,
                    params={"key": self.api_key},
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=30
                )
                resp.raise_for_status()
                data = resp.json()
                return data['candidates'][0]['content']['parts'][0]['text'].strip()
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if e.response is not None else 0
                if status_code in (429, 503) and attempt < max_retries - 1:
                    logging.warning(f"Gemini API returned {status_code}. Retrying in {retry_delay}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                raise TranslationError(f"Gemini API error: {e}")
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                if attempt < max_retries - 1:
                    logging.warning(f"Gemini network error ({e}). Retrying in {retry_delay}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                raise TranslationError(f"Gemini network error: {e}")
            except (KeyError, IndexError) as e:
                raise TranslationError(f"Unexpected Gemini response format: {e}")
            except Exception as e:
                raise TranslationError(f"Gemini translation failed: {e}")


class GroqTranslator(TranslationBackend):
    def __init__(self):
        self.api_key = ""
        self.model = "groq-beta"

    def translate(self, text: str, target_lang: str) -> str:
        if not self.api_key:
            raise TranslationError("Groq API key not configured")

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": f"You are a professional translator. Translate the given text to {target_lang}. Return ONLY the translated text, no explanations, no extra formatting. Preserve all line breaks, punctuation, and paragraph structure exactly."},
                {"role": "user", "content": text}
            ],
            "temperature": 0.3
        }

        import time
        max_retries = 3
        retry_delay = 1.0

        for attempt in range(max_retries):
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                return data['choices'][0]['message']['content'].strip()
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if e.response is not None else 0
                if status_code in (429, 503) and attempt < max_retries - 1:
                    logging.warning(f"Groq API returned {status_code}. Retrying in {retry_delay}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                raise TranslationError(f"Groq API error: {e}")
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                if attempt < max_retries - 1:
                    logging.warning(f"Groq network error ({e}). Retrying in {retry_delay}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                raise TranslationError(f"Groq network error: {e}")
            except (KeyError, IndexError) as e:
                raise TranslationError(f"Unexpected Groq response format: {e}")
            except Exception as e:
                raise TranslationError(f"Groq translation failed: {e}")


class MistralTranslator(TranslationBackend):
    def __init__(self):
        self.api_key = ""
        self.model = "mistral-large-latest"

    def translate(self, text: str, target_lang: str) -> str:
        if not self.api_key:
            raise TranslationError("Mistral API key not configured")

        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": f"You are a professional translator. Translate the given text to {target_lang}. Return ONLY the translated text, no explanations, no extra formatting. Preserve all line breaks, punctuation, and paragraph structure exactly."},
                {"role": "user", "content": text}
            ],
            "temperature": 0.3
        }

        import time
        max_retries = 3
        retry_delay = 1.0

        for attempt in range(max_retries):
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                return data['choices'][0]['message']['content'].strip()
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if e.response is not None else 0
                if status_code in (429, 503) and attempt < max_retries - 1:
                    logging.warning(f"Mistral API returned {status_code}. Retrying in {retry_delay}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                raise TranslationError(f"Mistral API error: {e}")
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                if attempt < max_retries - 1:
                    logging.warning(f"Mistral network error ({e}). Retrying in {retry_delay}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                raise TranslationError(f"Mistral network error: {e}")
            except (KeyError, IndexError) as e:
                raise TranslationError(f"Unexpected Mistral response format: {e}")
            except Exception as e:
                raise TranslationError(f"Mistral translation failed: {e}")


class GoogleFreeTranslator(TranslationBackend):
    URL = "https://translate.googleapis.com/translate_a/single"
    CHUNK_SIZE = 5000

    def translate(self, text: str, target_lang: str) -> str:
        # Split into chunks if text is too long
        if len(text) > self.CHUNK_SIZE:
            chunks = self._split_text(text, self.CHUNK_SIZE)
            translated_parts = []
            for chunk in chunks:
                translated_parts.append(self._translate_chunk(chunk, target_lang))
            return ''.join(translated_parts)
        return self._translate_chunk(text, target_lang)

    def _translate_chunk(self, text: str, target_lang: str) -> str:
        params = {
            "client": "gtx",
            "sl": "auto",
            "tl": target_lang,
            "dt": "t",
            "q": text
        }
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

        import time
        max_retries = 3
        retry_delay = 1.0

        for attempt in range(max_retries):
            try:
                resp = requests.get(self.URL, params=params, headers=headers, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                # Response is a nested array: [[["translated", "original", ...], ...], ...]
                if data and data[0]:
                    return ''.join(part[0] for part in data[0] if part and part[0])
                raise TranslationError("Empty Google Translate response")
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if e.response is not None else 0
                if status_code in (429, 503) and attempt < max_retries - 1:
                    logging.warning(f"Google Free Translate returned {status_code}. Retrying in {retry_delay}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                raise TranslationError(f"Google Translate HTTP error: {e}")
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                if attempt < max_retries - 1:
                    logging.warning(f"Google Free Translate network error ({e}). Retrying in {retry_delay}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                raise TranslationError(f"Google Translate network error: {e}")
            except (ValueError, TypeError, IndexError) as e:
                raise TranslationError(f"Google Translate parse error: {e}")

    @staticmethod
    def _split_text(text: str, max_len: int) -> list:
        """Split text into chunks, preferring to break at sentence/paragraph boundaries."""
        chunks = []
        while text:
            if len(text) <= max_len:
                chunks.append(text)
                break
            # Try to find a good break point
            break_at = max_len
            for sep in ('\n\n', '\n', '. ', '! ', '? ', ', ', ' '):
                pos = text.rfind(sep, 0, max_len)
                if pos > max_len // 2:
                    break_at = pos + len(sep)
                    break
            chunks.append(text[:break_at])
            text = text[break_at:]
        return chunks


class TranslationManager:
    """Orchestrates translation with fallback chain and LRU cache."""

    def __init__(self, config):
        self.config = config
        self.backends = {
            'gemini': GeminiTranslator(),
            'groq': GroqTranslator(),
            'mistral': MistralTranslator(),
            'google_free': GoogleFreeTranslator()
        }

    def translate(self, text: str, target_lang: str) -> str:
        """Translate with fallback chain."""
        # 1. Determine provider order
        if self.config.data.get('fallback_enabled', True):
            order = self.config.data.get('fallback_order', ['gemini', 'google_free'])
        else:
            order = [self.config.data.get('translation_provider', 'gemini')]

        # 3. Try each provider
        last_error = None
        for provider in order:
            backend = self.backends.get(provider)
            if not backend:
                continue

            # Skip providers that need API keys but don't have them
            if provider in ('gemini', 'groq', 'mistral') and not self.config.get_api_key(provider):
                continue

            try:
                logging.info(f"Trying provider: {provider}")
                # Pass API key and model to backend
                if provider == 'gemini':
                    backend.api_key = self.config.get_api_key('gemini')
                    backend.model = self.config.get_gemini_model()
                elif provider == 'groq':
                    backend.api_key = self.config.get_api_key('groq')
                    backend.model = self.config.get_groq_model()
                elif provider == 'mistral':
                    backend.api_key = self.config.get_api_key('mistral')
                    backend.model = self.config.get_mistral_model()

                result = backend.translate(text, target_lang)
                logging.info(f"Provider '{provider}' succeeded.")

                import re as _re
                if '<think>' in result:
                    result = _re.sub(r'<think>.*?</think>\s*', '', result, flags=_re.DOTALL).strip()
                return result
            except Exception as e:
                logging.warning(f"Provider '{provider}' failed: {e}")
                last_error = e
                continue

        raise TranslationError(f"All translation providers failed. Last error: {last_error}")
