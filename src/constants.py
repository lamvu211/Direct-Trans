"""
constants.py - Shared business constants for DirectTrans.
"""

from enum import Enum


class TranslationMode(str, Enum):
    POPUP = "popup"
    REPLACE = "replace"


class Provider(str, Enum):
    GEMINI = "gemini"
    GROQ = "groq"
    MISTRAL = "mistral"
    GOOGLE_FREE = "google_free"


MODE_POPUP = TranslationMode.POPUP.value
MODE_REPLACE = TranslationMode.REPLACE.value
VALID_MODES = (MODE_POPUP, MODE_REPLACE)

PROVIDER_GEMINI = Provider.GEMINI.value
PROVIDER_GROQ = Provider.GROQ.value
PROVIDER_MISTRAL = Provider.MISTRAL.value
PROVIDER_GOOGLE_FREE = Provider.GOOGLE_FREE.value

PROVIDERS_NEED_API_KEY = (PROVIDER_GEMINI, PROVIDER_GROQ, PROVIDER_MISTRAL)
DEFAULT_FALLBACK_ORDER = (
    PROVIDER_GEMINI, PROVIDER_GROQ, PROVIDER_MISTRAL, PROVIDER_GOOGLE_FREE,
)
DEFAULT_PROVIDER = PROVIDER_GEMINI
ALL_PROVIDERS = tuple(p.value for p in Provider)

APP_VERSION = "1.0.9"
GITHUB_REPO = "lamvu211/Direct-Trans"
GITHUB_RELEASES_URL = f"https://github.com/{GITHUB_REPO}/releases/latest"
