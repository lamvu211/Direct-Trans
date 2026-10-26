"""Demo config for public UI screenshots (no personal keys, English UI)."""

from __future__ import annotations

import copy

from config import Config
from constants import MODE_POPUP, PROVIDER_GEMINI, PROVIDER_GROQ, PROVIDER_MISTRAL


def make_public_screenshot_config() -> Config:
    """Fresh DEFAULT_CONFIG overlay — safe to commit resulting PNGs after visual review."""
    config = Config()
    config.data = copy.deepcopy(Config.DEFAULT_CONFIG)
    config.data["ui_language"] = "en"
    config.data["translation_provider"] = PROVIDER_GEMINI
    config.data["api_keys"] = {
        PROVIDER_GEMINI: "",
        PROVIDER_GROQ: "",
        PROVIDER_MISTRAL: "",
    }
    config.data["hotkeys"] = [
        {
            "id": "00000000-0000-4000-8000-000000000001",
            "key_combo": "ctrl+shift+v",
            "target_language_code": "vi",
            "target_language_name": "Vietnamese",
            "mode": MODE_POPUP,
        },
        {
            "id": "00000000-0000-4000-8000-000000000002",
            "key_combo": "ctrl+shift+e",
            "target_language_code": "en",
            "target_language_name": "English",
            "mode": MODE_POPUP,
        },
    ]
    return config


POPUP_README_SAMPLE_TEXT = (
    "Draft amendments to regulations on centralized, unified data management "
    "and exploitation models…"
)
