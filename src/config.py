"""
config.py - Configuration management for DirectTrans.
Handles load/save of config.json, hotkey management, and Windows auto-start registry.
"""

import json
import os
import sys
import uuid
import copy


class Config:
    DEFAULT_CONFIG = {
        "translation_provider": "gemini",
        "api_keys": {
            "gemini": "",
            "groq": "",
            "mistral": ""
        },
        "fallback_enabled": True,
        "fallback_order": ["gemini", "groq", "mistral", "google_free"],
        "gemini_model": "gemini-3.1-flash-lite",
        "groq_model": "openai/gpt-oss-120b",
        "mistral_model": "mistral-large-latest",
        "auto_start": False,
        "hotkeys": [
            {
                "id": str(uuid.uuid4()),
                "key_combo": "ctrl+shift+v",
                "target_language_code": "vi",
                "target_language_name": "Tiếng Việt",
                "mode": "popup"
            },
            {
                "id": str(uuid.uuid4()),
                "key_combo": "ctrl+shift+e",
                "target_language_code": "en",
                "target_language_name": "Tiếng Anh",
                "mode": "popup"
            }
        ]
    }

    def __init__(self):
        self.config_path = self._resolve_config_path()
        self.data = self._load()

    def _resolve_config_path(self) -> str:
        if getattr(sys, 'frozen', False):
            base = os.path.dirname(sys.executable)
        else:
            base = os.path.dirname(os.path.abspath(__file__))
            base = os.path.dirname(base)  # up one level from src/
        return os.path.join(base, 'config.json')

    def _load(self) -> dict:
        if not os.path.exists(self.config_path):
            data = copy.deepcopy(self.DEFAULT_CONFIG)
            self._write(data)
            return data

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError, OSError):
            # Corrupt config file - reset to defaults
            data = copy.deepcopy(self.DEFAULT_CONFIG)
            self._write(data)
            return data

        # Merge with defaults to fill in any missing keys
        merged = copy.deepcopy(self.DEFAULT_CONFIG)
        self._deep_merge(merged, data)
        return merged

    def _deep_merge(self, base: dict, override: dict):
        """Recursively merge override into base, keeping base defaults for missing keys."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def _write(self, data: dict):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save(self):
        self._write(self.data)

    # --- Provider ---
    def get_provider(self) -> str:
        return self.data.get('translation_provider', 'gemini')

    def set_provider(self, provider: str):
        self.data['translation_provider'] = provider
        self.save()

    # --- API Keys ---
    def get_api_key(self, provider: str) -> str:
        return self.data.get('api_keys', {}).get(provider, '')

    def set_api_key(self, provider: str, key: str):
        if 'api_keys' not in self.data:
            self.data['api_keys'] = {}
        self.data['api_keys'][provider] = key
        self.save()

    def get_gemini_model(self) -> str:
        return self.data.get('gemini_model', 'gemini-3.1-flash-lite')

    def set_gemini_model(self, model: str):
        self.data['gemini_model'] = model
        self.save()

    def get_groq_model(self) -> str:
        return self.data.get('groq_model', 'openai/gpt-oss-120b')

    def set_groq_model(self, model: str):
        self.data['groq_model'] = model
        self.save()

    def get_mistral_model(self) -> str:
        return self.data.get('mistral_model', 'mistral-large-latest')

    def set_mistral_model(self, model: str):
        self.data['mistral_model'] = model
        self.save()

    # --- Hotkeys ---
    def get_hotkeys(self) -> list:
        return self.data.get('hotkeys', [])

    def add_hotkey(self, key_combo: str, lang_code: str, lang_name: str, mode: str) -> str:
        hotkey_id = str(uuid.uuid4())
        entry = {
            "id": hotkey_id,
            "key_combo": key_combo,
            "target_language_code": lang_code,
            "target_language_name": lang_name,
            "mode": mode
        }
        self.data.setdefault('hotkeys', []).append(entry)
        self.save()
        return hotkey_id

    def remove_hotkey(self, hotkey_id: str):
        self.data['hotkeys'] = [
            hk for hk in self.data.get('hotkeys', []) if hk.get('id') != hotkey_id
        ]
        self.save()

    def update_hotkey(self, hotkey_id: str, **kwargs):
        for hk in self.data.get('hotkeys', []):
            if hk.get('id') == hotkey_id:
                hk.update(kwargs)
                break
        self.save()

    # --- Auto-start ---
    def is_auto_start(self) -> bool:
        return self.data.get('auto_start', False)

    def set_auto_start(self, enabled: bool):
        self.data['auto_start'] = enabled
        self.save()
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            if enabled:
                if getattr(sys, 'frozen', False):
                    exe_path = sys.executable
                else:
                    main_path = os.path.abspath(os.path.join(
                        os.path.dirname(__file__), 'main.py'
                    ))
                    exe_path = f'pythonw "{main_path}"'
                winreg.SetValueEx(key, "DirectTrans", 0, winreg.REG_SZ, exe_path)
            else:
                try:
                    winreg.DeleteValue(key, "DirectTrans")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception:
            pass  # Registry access may fail in some environments

    def is_first_run(self) -> bool:
        """Check if this is the first run (no API keys configured)."""
        gemini = self.get_api_key('gemini')
        return not gemini
