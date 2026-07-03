"""
font_mapper.py - Maps target language to the best available font on Windows.
"""

import threading
import winreg


class FontMapper:
    """Map target language code to the best matching font installed on the system."""

    FONT_MAP = {
        # CJK
        'zh': ['Microsoft YaHei', 'SimSun', 'Arial Unicode MS'],
        'ja': ['Yu Gothic', 'MS Gothic', 'Meiryo', 'Arial Unicode MS'],
        'ko': ['Malgun Gothic', 'Gulim', 'Arial Unicode MS'],

        # South/Southeast Asian
        'th': ['Leelawadee UI', 'Tahoma', 'Arial Unicode MS'],
        'hi': ['Nirmala UI', 'Mangal', 'Arial Unicode MS'],
        'ta': ['Nirmala UI', 'Latha', 'Arial Unicode MS'],
        'my': ['Myanmar Text', 'Padauk', 'Arial Unicode MS'],
        'km': ['Leelawadee UI', 'Khmer UI', 'Arial Unicode MS'],

        # Arabic/Hebrew (RTL)
        'ar': ['Arabic Typesetting', 'Tahoma', 'Arial'],
        'he': ['David', 'Tahoma', 'Arial'],
        'fa': ['Arabic Typesetting', 'Tahoma', 'Arial'],

        # Cyrillic
        'ru': ['Segoe UI', 'Arial', 'Times New Roman'],
        'uk': ['Segoe UI', 'Arial', 'Times New Roman'],
        'bg': ['Segoe UI', 'Arial', 'Times New Roman'],

        # Latin-based (Vietnamese, European, etc.)
        'vi': ['Segoe UI', 'Arial', 'Times New Roman'],
        'en': ['Segoe UI', 'Arial', 'Times New Roman'],
        'fr': ['Segoe UI', 'Arial', 'Times New Roman'],
        'de': ['Segoe UI', 'Arial', 'Times New Roman'],
        'es': ['Segoe UI', 'Arial', 'Times New Roman'],
        'pt': ['Segoe UI', 'Arial', 'Times New Roman'],
        'it': ['Segoe UI', 'Arial', 'Times New Roman'],
        'nl': ['Segoe UI', 'Arial', 'Times New Roman'],
        'pl': ['Segoe UI', 'Arial', 'Times New Roman'],
        'tr': ['Segoe UI', 'Arial', 'Times New Roman'],
        'ro': ['Segoe UI', 'Arial', 'Times New Roman'],
        'cs': ['Segoe UI', 'Arial', 'Times New Roman'],
        'sv': ['Segoe UI', 'Arial', 'Times New Roman'],
    }

    DEFAULT_FONTS = ['Segoe UI', 'Arial', 'Times New Roman']

    _lang_cache = {}
    _installed_fonts = None
    _lock = threading.Lock()

    @staticmethod
    def get_font(lang_code: str) -> str:
        """Return the best available font for the given language code."""
        if lang_code in FontMapper._lang_cache:
            return FontMapper._lang_cache[lang_code]

        candidates = FontMapper.FONT_MAP.get(lang_code, FontMapper.DEFAULT_FONTS)

        for font in candidates:
            if FontMapper._font_exists(font):
                FontMapper._lang_cache[lang_code] = font
                return font

        FontMapper._lang_cache[lang_code] = 'Arial'
        return 'Arial'  # Ultimate fallback, always available on Windows

    @staticmethod
    def _font_exists(font_name: str) -> bool:
        """Check if a font is installed on Windows via registry."""
        if FontMapper._installed_fonts is None:
            with FontMapper._lock:
                # Double-check after acquiring lock
                if FontMapper._installed_fonts is None:
                    fonts = []
                    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
                        try:
                            key = winreg.OpenKey(
                                hive,
                                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
                            )
                            try:
                                i = 0
                                while True:
                                    try:
                                        name, _, _ = winreg.EnumValue(key, i)
                                        fonts.append(name.lower())
                                        i += 1
                                    except OSError:
                                        break
                            finally:
                                winreg.CloseKey(key)
                        except Exception:
                            pass
                    FontMapper._installed_fonts = fonts

        font_name_lower = font_name.lower()
        for installed_font in FontMapper._installed_fonts:
            if font_name_lower in installed_font:
                return True
                
        return False

