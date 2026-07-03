import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from unittest.mock import patch, MagicMock
import tempfile
import json

from hotkey_manager import parse_hotkey, MOD_CONTROL, MOD_SHIFT, MOD_ALT, MOD_WIN
from font_mapper import FontMapper
from config import Config

class TestComponents(unittest.TestCase):
    def test_parse_hotkey(self):
        # Basic parsing
        mod, vk = parse_hotkey('ctrl+shift+v')
        self.assertEqual(mod, MOD_CONTROL | MOD_SHIFT)
        self.assertEqual(vk, ord('V'))

        # Test empty string (B6 fix)
        mod, vk = parse_hotkey('')
        self.assertEqual(mod, 0)
        self.assertEqual(vk, 0)

        # Test trailing whitespace/empty parts (B6 fix)
        mod, vk = parse_hotkey('ctrl +  + v ')
        self.assertEqual(mod, MOD_CONTROL)
        self.assertEqual(vk, ord('V'))
        
        mod, vk = parse_hotkey(None)
        self.assertEqual(mod, 0)
        self.assertEqual(vk, 0)

    @patch('font_mapper.winreg')
    def test_font_mapper(self, mock_winreg):
        # Reset cache
        FontMapper._lang_cache = {}
        FontMapper._installed_fonts = None
        
        def mock_enum_value(key, i):
            fonts = [('Segoe UI', 0, 1), ('Comic Sans', 0, 1)]
            if i < len(fonts):
                return fonts[i]
            raise OSError()
            
        mock_winreg.EnumValue.side_effect = mock_enum_value
        
        # 'vi' should prefer Segoe UI
        font = FontMapper.get_font('vi')
        self.assertEqual(font, 'Segoe UI')
        
        # Since it's now cached by lang_code, EnumValue shouldn't be called again
        mock_winreg.EnumValue.reset_mock()
        font = FontMapper.get_font('vi')
        self.assertEqual(font, 'Segoe UI')
        self.assertEqual(mock_winreg.EnumValue.call_count, 0)
        
        # Test fallback
        # Reset cache to test fallback when no preferred fonts are installed
        FontMapper._lang_cache = {}
        FontMapper._installed_fonts = None
        def mock_enum_value_empty(key, i):
            raise OSError()
        mock_winreg.EnumValue.side_effect = mock_enum_value_empty
        font = FontMapper.get_font('vi')
        self.assertEqual(font, 'Arial')

    def test_config_encryption(self):
        with tempfile.TemporaryDirectory() as td:
            cfg_path = os.path.join(td, 'test_config.json')
            
            with patch('config.Config._resolve_config_path', return_value=cfg_path):
                cfg = Config()
                # Empty initially
                self.assertEqual(cfg.get_api_key('gemini'), '')
                
                # Set key
                cfg.set_api_key('gemini', 'secret_key_123')
                self.assertEqual(cfg.get_api_key('gemini'), 'secret_key_123')
                
                # Verify encryption on disk
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    encrypted = data.get('api_keys', {}).get('gemini', '')
                    self.assertNotEqual(encrypted, 'secret_key_123')
                    self.assertNotEqual(encrypted, '')
                    
                # Verify reload decrypts properly
                cfg2 = Config()
                self.assertEqual(cfg2.get_api_key('gemini'), 'secret_key_123')

if __name__ == '__main__':
    unittest.main()
