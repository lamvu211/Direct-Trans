"""
config.py - Configuration management for DirectTrans.
Handles load/save of config.json, hotkey management, and Windows auto-start registry.
"""

import json
import os
import sys
import uuid
import copy

from constants import (
    DEFAULT_FALLBACK_ORDER,
    DEFAULT_PROVIDER,
    MODE_POPUP,
    PROVIDER_GEMINI,
    PROVIDER_GROQ,
    PROVIDER_MISTRAL,
    PROVIDER_GOOGLE_FREE,
    PROVIDERS_NEED_API_KEY,
)


class Config:
    DEFAULT_CONFIG = {
        "translation_provider": DEFAULT_PROVIDER,
        "api_keys": {
            PROVIDER_GEMINI: "",
            PROVIDER_GROQ: "",
            PROVIDER_MISTRAL: "",
        },
        "fallback_enabled": True,
        "fallback_order": list(DEFAULT_FALLBACK_ORDER),
        "gemini_model": "gemini-3.1-flash-lite",
        "groq_model": "openai/gpt-oss-120b",
        "mistral_model": "mistral-large-latest",
        "auto_start": False,
        "skipped_versions": [],
        "snooze_update_until": 0,
        "hotkeys": [
            {
                "id": str(uuid.uuid4()),
                "key_combo": "ctrl+shift+v",
                "target_language_code": "vi",
                "target_language_name": "Tiếng Việt",
                "mode": MODE_POPUP
            },
            {
                "id": str(uuid.uuid4()),
                "key_combo": "ctrl+shift+e",
                "target_language_code": "en",
                "target_language_name": "Tiếng Anh",
                "mode": MODE_POPUP
            }
        ]
    }

    def __init__(self):
        self.config_path = self._resolve_config_path()
        self._was_created = False
        self.data = self._load()



    def _resolve_config_path(self) -> str:
        if getattr(sys, 'frozen', False):
            base = os.path.dirname(sys.executable)
        else:
            base = os.path.join(os.environ.get('APPDATA', ''), 'DirectTrans')
            os.makedirs(base, exist_ok=True)
        return os.path.join(base, 'config.json')

    def _load(self) -> dict:
        if not os.path.exists(self.config_path):
            data = copy.deepcopy(self.DEFAULT_CONFIG)
            self._write(data)
            self._was_created = True
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

    def _encrypt_key(self, plain_text: str) -> str:
        if not plain_text:
            return ""
        try:
            import win32crypt
            encrypted_bytes = win32crypt.CryptProtectData(plain_text.encode('utf-8'), None, None, None, None, 0)
            return encrypted_bytes.hex()
        except Exception:
            return plain_text

    def _decrypt_key(self, cipher_hex: str) -> str:
        if not cipher_hex:
            return ""
        try:
            import win32crypt
            cipher_bytes = bytes.fromhex(cipher_hex)
            _, decrypted_bytes = win32crypt.CryptUnprotectData(cipher_bytes, None, None, None, 0)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            import logging
            logging.warning(f"Decrypt API key failed: {e}. Key might be corrupted or from a different user context.")
            return ""

    # --- Provider ---
    def get_provider(self) -> str:
        return self.data.get('translation_provider', DEFAULT_PROVIDER)

    def set_provider(self, provider: str):
        self.data['translation_provider'] = provider
        self.save()

    # --- API Keys ---
    def get_api_key(self, provider: str) -> str:
        val = self.data.get('api_keys', {}).get(provider, '')
        return self._decrypt_key(val)

    def set_api_key(self, provider: str, key: str):
        if 'api_keys' not in self.data:
            self.data['api_keys'] = {}
        self.data['api_keys'][provider] = self._encrypt_key(key)
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

    def is_first_run(self) -> bool:
        """True when config.json was created on this launch."""
        return self._was_created

    def needs_setup(self) -> bool:
        """True when Settings should open on startup (first run or missing API key)."""
        if self.is_first_run():
            return True
        provider = self.get_provider()
        if provider == PROVIDER_GOOGLE_FREE:
            return False
        if provider in PROVIDERS_NEED_API_KEY and not self.get_api_key(provider):
            return True
        return False

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

    def set_auto_start(self, enabled: bool) -> bool:
        try:
            import winreg
            import logging
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            if enabled:
                if getattr(sys, 'frozen', False):
                    exe_path = f'"{sys.executable}"'
                else:
                    main_path = os.path.abspath(os.path.join(
                        os.path.dirname(__file__), 'main.py'
                    ))
                    exe_path = f'"{sys.executable}" "{main_path}"'
                winreg.SetValueEx(key, "DirectTrans", 0, winreg.REG_SZ, exe_path)
            else:
                try:
                    winreg.DeleteValue(key, "DirectTrans")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
            self.data['auto_start'] = enabled
            self.save()
            return True
        except Exception as e:
            import logging
            logging.warning("Failed to update auto-start registry: %s", e)
            return False

    # --- Update preferences ---
    def get_skipped_versions(self) -> list:
        return self.data.get('skipped_versions', [])

    def skip_version(self, version: str):
        skipped = self.data.setdefault('skipped_versions', [])
        if version not in skipped:
            skipped.append(version)
            self.save()

    def get_snooze_until(self) -> float:
        return self.data.get('snooze_update_until', 0)

    def snooze_update(self, days: int = 7):
        import time
        self.data['snooze_update_until'] = time.time() + (days * 86400)
        self.save()
