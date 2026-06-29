"""
font_mapper.py - Maps target language to the best available font on Windows.
"""

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

    # Cache for font existence checks to avoid repeated registry lookups
    _font_cache = {}

    @staticmethod
    def get_font(lang_code: str) -> str:
        """Return the best available font for the given language code."""
        candidates = FontMapper.FONT_MAP.get(lang_code, FontMapper.DEFAULT_FONTS)

        for font in candidates:
            if FontMapper._font_exists(font):
                return font

        return 'Arial'  # Ultimate fallback, always available on Windows

    @staticmethod
    def _font_exists(font_name: str) -> bool:
        """Check if a font is installed on Windows via registry."""
        if font_name in FontMapper._font_cache:
            return FontMapper._font_cache[font_name]

        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
            )
            try:
                i = 0
                while True:
                    try:
                        name, _, _ = winreg.EnumValue(key, i)
                        if font_name.lower() in name.lower():
                            FontMapper._font_cache[font_name] = True
                            return True
                        i += 1
                    except OSError:
                        break
            finally:
                winreg.CloseKey(key)
        except Exception:
            pass

        FontMapper._font_cache[font_name] = False
        return False
