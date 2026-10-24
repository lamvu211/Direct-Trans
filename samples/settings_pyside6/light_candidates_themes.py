"""Five light Settings theme candidates — token-driven QSS aligned with production selectors."""

from __future__ import annotations

from dataclasses import dataclass

from premium_themes import _COMMON

_BASE = _COMMON + """
QWidget#tagline { font-size: 7pt; }
QFrame#footBar { border-top: 1px solid rgba(128,128,128,0.25); }
QFrame#topBar { border-bottom: 1px solid rgba(128,128,128,0.2); }
QComboBox#themeCombo { min-width: 148px; }
"""


@dataclass(frozen=True)
class LightThemeTokens:
    """Colors for one light theme — see LIGHT_CANDIDATES.md."""

    id: str
    label: str
    tagline: str
    root_bg: str
    top_bar_bg: str
    top_bar_border: str
    foot_bar_bg: str
    foot_bar_border: str
    card_bg: str
    card_border: str
    brand: str
    text_muted: str
    card_title: str
    text: str
    input_bg: str
    input_border: str
    input_text: str
    input_focus_border: str
    dropdown_bg: str
    dropdown_border: str
    dropdown_selection_bg: str
    dropdown_selection_text: str
    cta_bg: str
    cta_hover_bg: str
    cta_text: str
    cta_focus_border: str
    ghost_bg: str
    ghost_text: str
    ghost_border: str
    ghost_hover_bg: str
    ghost_hover_border: str
    ghost_focus_border: str
    link: str
    link_hover: str
    hk_row_bg: str
    hk_row_border: str
    hk_mode_bg: str
    hk_mode_text: str
    hk_del: str
    hk_del_hover: str
    option_check: str
    radio_border: str
    radio_bg: str
    radio_checked_border: str
    cta_disabled_bg: str
    cta_disabled_text: str
    cta_disabled_border: str


def qss_from_tokens(t: LightThemeTokens) -> str:
    """Build theme QSS matching production light themes (e.g. rose_champagne)."""
    return f"""
QWidget#root {{
    background: {t.root_bg};
}}
QFrame#topBar {{
    background: {t.top_bar_bg};
    border-bottom: 1px solid {t.top_bar_border};
}}
QFrame#footBar {{
    background: {t.foot_bar_bg};
    border-top: 1px solid {t.foot_bar_border};
}}
QLabel#brand {{
    color: {t.brand};
    font-size: 12pt;
    font-weight: 700;
}}
QLabel#brandSub, QLabel#brandVersion {{ color: {t.text_muted}; }}
QLabel#tagline, QLabel#fieldLabel {{ color: {t.text_muted}; }}
QFrame#card {{
    background: {t.card_bg};
    border: 1px solid {t.card_border};
}}
QLabel#cardTitle {{ color: {t.card_title}; }}
QLabel, QCheckBox, QRadioButton {{ color: {t.text}; }}
QComboBox#combo, QComboBox#comboMini, QComboBox#themeCombo, QLineEdit#line, QTextEdit#line {{
    background: {t.input_bg};
    border: 1px solid {t.input_border};
    color: {t.input_text};
}}
QComboBox#combo:focus, QLineEdit#line:focus, QTextEdit#line:focus {{
    border-color: {t.input_focus_border};
}}
QComboBox QAbstractItemView {{
    background-color: {t.dropdown_bg};
    color: {t.input_text};
    selection-background-color: {t.dropdown_selection_bg};
    selection-color: {t.dropdown_selection_text};
    border: 1px solid {t.dropdown_border};
    outline: none;
}}
QPushButton#cta, QPushButton#ctaSmall {{
    color: {t.cta_text};
    border: none;
    background: {t.cta_bg};
}}
QPushButton#cta:hover, QPushButton#ctaSmall:hover {{
    background: {t.cta_hover_bg};
}}
QPushButton#cta:focus, QPushButton#ctaSmall:focus {{
    border: 1px solid {t.cta_focus_border};
}}
QPushButton#cta:disabled, QPushButton#ctaSmall:disabled {{
    opacity: 1.0;
    background: {t.cta_disabled_bg};
    color: {t.cta_disabled_text};
    border: 1px solid {t.cta_disabled_border};
}}
QPushButton#ghost, QToolButton#ghost, QPushButton#showMore {{
    background: {t.ghost_bg};
    color: {t.ghost_text};
    border: 1px solid {t.ghost_border};
}}
QPushButton#ghost:hover, QToolButton#ghost:hover, QPushButton#showMore:hover {{
    background: {t.ghost_hover_bg};
    border-color: {t.ghost_hover_border};
}}
QPushButton#ghost:focus, QToolButton#ghost:focus, QPushButton#showMore:focus {{
    border-color: {t.ghost_focus_border};
}}
QPushButton#textLink {{ color: {t.link}; font-weight: 600; }}
QPushButton#textLink:hover {{ text-decoration: underline; color: {t.link_hover}; }}
QFrame#hkRow {{ background: {t.hk_row_bg}; border: 1px solid {t.hk_row_border}; }}
QLabel#hkMode {{ background: {t.hk_mode_bg}; color: {t.hk_mode_text}; }}
QToolButton#hkDel, QPushButton#hkDel {{
    color: {t.hk_del};
    border: none;
    background: transparent;
    font-size: 9pt;
}}
QToolButton#hkDel:hover, QPushButton#hkDel:hover {{
    color: {t.hk_del_hover};
    background: rgba(0,0,0,0.06);
    border-radius: 4px;
}}
QCheckBox#optionCheck {{ color: {t.option_check}; font-weight: 600; }}
QLabel#statusBy {{ color: {t.card_title}; font-size: 8.5pt; font-weight: 600; }}
QRadioButton::indicator {{
    width: 14px;
    height: 14px;
    border-radius: 8px;
    border: 2px solid {t.radio_border};
    background: {t.radio_bg};
}}
QRadioButton::indicator:checked {{
    border: 2px solid {t.radio_checked_border};
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
        stop:0 {t.radio_checked_border}, stop:0.55 {t.radio_checked_border},
        stop:0.60 {t.radio_bg}, stop:1 {t.radio_bg});
}}
QRadioButton::indicator:hover {{
    border-color: {t.input_focus_border};
}}
""" + _BASE


def _t(**kwargs) -> LightThemeTokens:
    defaults = {
        "cta_focus_border": kwargs.get("input_focus_border", "#000"),
        "ghost_focus_border": kwargs.get("input_focus_border", "#000"),
        "ghost_hover_border": kwargs.get("ghost_border", "#ccc"),
        "dropdown_border": kwargs.get("input_border", "#ccc"),
        "dropdown_selection_text": kwargs.get("link", "#000"),
        "radio_border": kwargs.get("input_border", "#ccc"),
        "radio_bg": kwargs.get("input_bg", "#fff"),
        "radio_checked_border": kwargs.get("input_focus_border", "#000"),
        "cta_disabled_bg": "#E5E5E5",
        "cta_disabled_text": "#9CA3AF",
        "cta_disabled_border": "#D4D4D4",
        "hk_del_hover": kwargs.get("hk_del", "#000"),
    }
    merged = {**defaults, **kwargs}
    return LightThemeTokens(**merged)


LIGHT_TOKEN_LIST: tuple[LightThemeTokens, ...] = (
    _t(
        id="cursor_paper",
        label="Cursor Paper",
        tagline="Neutral gray · blue focus · Cursor-like",
        root_bg="#F3F3F3",
        top_bar_bg="#FAFAFA",
        top_bar_border="#E4E4E4",
        foot_bar_bg="#FAFAFA",
        foot_bar_border="#E4E4E4",
        card_bg="#FFFFFF",
        card_border="#E8E8E8",
        brand="#1F1F1F",
        text_muted="#6B6B6B",
        card_title="#525252",
        text="#1F1F1F",
        input_bg="#FFFFFF",
        input_border="#D4D4D4",
        input_text="#1F1F1F",
        input_focus_border="#0969DA",
        dropdown_bg="#FFFFFF",
        dropdown_selection_bg="#EEF4FF",
        dropdown_selection_text="#0550AE",
        cta_bg="#0969DA",
        cta_hover_bg="#0550AE",
        cta_text="#FFFFFF",
        ghost_bg="#FFFFFF",
        ghost_text="#1F1F1F",
        ghost_border="#D4D4D4",
        ghost_hover_bg="#F5F5F5",
        link="#0969DA",
        link_hover="#0550AE",
        hk_row_bg="#FAFAFA",
        hk_row_border="#EBEBEB",
        hk_mode_bg="#EEF4FF",
        hk_mode_text="#0969DA",
        hk_del="#C62828",
        option_check="#0969DA",
    ),
    _t(
        id="antigravity_mist",
        label="Antigravity Mist",
        tagline="Cool white · hairline borders · teal accent",
        root_bg="#F8F9FA",
        top_bar_bg="#FFFFFF",
        top_bar_border="#E5E7EB",
        foot_bar_bg="#FFFFFF",
        foot_bar_border="#E5E7EB",
        card_bg="#FFFFFF",
        card_border="#E5E7EB",
        brand="#111827",
        text_muted="#6B7280",
        card_title="#374151",
        text="#111827",
        input_bg="#FFFFFF",
        input_border="#D1D5DB",
        input_text="#111827",
        input_focus_border="#0D9488",
        dropdown_bg="#FFFFFF",
        dropdown_selection_bg="#CCFBF1",
        dropdown_selection_text="#0F766E",
        cta_bg="#0D9488",
        cta_hover_bg="#0F766E",
        cta_text="#FFFFFF",
        ghost_bg="#FFFFFF",
        ghost_text="#374151",
        ghost_border="#D1D5DB",
        ghost_hover_bg="#F9FAFB",
        link="#0D9488",
        link_hover="#0F766E",
        hk_row_bg="#FFFFFF",
        hk_row_border="#F3F4F6",
        hk_mode_bg="#CCFBF1",
        hk_mode_text="#0F766E",
        hk_del="#DC2626",
        option_check="#0D9488",
    ),
    _t(
        id="paper_ink",
        label="Paper Ink",
        tagline="Warm paper · ink text · indigo accent",
        root_bg="#F4F1EA",
        top_bar_bg="#FFFCF7",
        top_bar_border="#E7E2D8",
        foot_bar_bg="#FFFCF7",
        foot_bar_border="#E7E2D8",
        card_bg="#FFFFFF",
        card_border="#E0DBD0",
        brand="#1A1A1A",
        text_muted="#5C5C5C",
        card_title="#404040",
        text="#1A1A1A",
        input_bg="#FFFFFF",
        input_border="#C9C4B8",
        input_text="#1A1A1A",
        input_focus_border="#4338CA",
        dropdown_bg="#FFFFFF",
        dropdown_selection_bg="#EEF2FF",
        dropdown_selection_text="#3730A3",
        cta_bg="#4338CA",
        cta_hover_bg="#3730A3",
        cta_text="#FFFFFF",
        ghost_bg="#FFFCF7",
        ghost_text="#1A1A1A",
        ghost_border="#C9C4B8",
        ghost_hover_bg="#F4F1EA",
        link="#4338CA",
        link_hover="#3730A3",
        hk_row_bg="#FFFFFF",
        hk_row_border="#EDE8DF",
        hk_mode_bg="#EEF2FF",
        hk_mode_text="#4338CA",
        hk_del="#B91C1C",
        option_check="#4338CA",
    ),
    _t(
        id="nord_snow",
        label="Nord Snow",
        tagline="Frost gray · Nord-inspired · blue accent",
        root_bg="#ECEFF4",
        top_bar_bg="#E5E9F0",
        top_bar_border="#D8DEE9",
        foot_bar_bg="#E5E9F0",
        foot_bar_border="#D8DEE9",
        card_bg="#ECEFF4",
        card_border="#D8DEE9",
        brand="#2E3440",
        text_muted="#4C566A",
        card_title="#3B4252",
        text="#2E3440",
        input_bg="#ECEFF4",
        input_border="#D8DEE9",
        input_text="#2E3440",
        input_focus_border="#5E81AC",
        dropdown_bg="#ECEFF4",
        dropdown_selection_bg="#D8DEE9",
        dropdown_selection_text="#4C6F94",
        cta_bg="#5E81AC",
        cta_hover_bg="#4C6F94",
        cta_text="#ECEFF4",
        ghost_bg="#ECEFF4",
        ghost_text="#2E3440",
        ghost_border="#D8DEE9",
        ghost_hover_bg="#E5E9F0",
        link="#5E81AC",
        link_hover="#4C6F94",
        hk_row_bg="#E5E9F0",
        hk_row_border="#D8DEE9",
        hk_mode_bg="#D8DEE9",
        hk_mode_text="#5E81AC",
        hk_del="#BF616A",
        option_check="#5E81AC",
        cta_disabled_bg="#D8DEE9",
        cta_disabled_text="#4C566A",
        cta_disabled_border="#C0C8D4",
    ),
    _t(
        id="sage_linen",
        label="Sage Linen",
        tagline="Linen warmth · sage green · calm light",
        root_bg="#F5F2EB",
        top_bar_bg="#FAF8F4",
        top_bar_border="#E8E4DC",
        foot_bar_bg="#FAF8F4",
        foot_bar_border="#E8E4DC",
        card_bg="#FFFFFF",
        card_border="#E3DDD2",
        brand="#2C2925",
        text_muted="#6F6A62",
        card_title="#4A7C59",
        text="#2C2925",
        input_bg="#FFFFFF",
        input_border="#D5CFC4",
        input_text="#2C2925",
        input_focus_border="#4A7C59",
        dropdown_bg="#FFFFFF",
        dropdown_selection_bg="#E8F0EA",
        dropdown_selection_text="#3D6649",
        cta_bg="#4A7C59",
        cta_hover_bg="#3D6649",
        cta_text="#FFFFFF",
        ghost_bg="#FFFFFF",
        ghost_text="#2C2925",
        ghost_border="#D5CFC4",
        ghost_hover_bg="#F5F2EB",
        link="#4A7C59",
        link_hover="#3D6649",
        hk_row_bg="#FFFFFF",
        hk_row_border="#EDE9E1",
        hk_mode_bg="#E8F0EA",
        hk_mode_text="#3D6649",
        hk_del="#C2410C",
        option_check="#4A7C59",
    ),
)

THEME_IDS: tuple[str, ...] = tuple(t.id for t in LIGHT_TOKEN_LIST)
DEFAULT_THEME_ID = THEME_IDS[0]

THEMES: dict[str, dict[str, str]] = {
    t.id: {
        "label": t.label,
        "tagline": t.tagline,
        "qss": qss_from_tokens(t),
        "tokens": t,
    }
    for t in LIGHT_TOKEN_LIST
}


def qss_for(theme_id: str) -> str:
    return THEMES[theme_id]["qss"]


def label_for(theme_id: str) -> str:
    return THEMES[theme_id]["label"]


def tagline_for(theme_id: str) -> str:
    return THEMES[theme_id]["tagline"]


def tokens_for(theme_id: str) -> LightThemeTokens:
    return THEMES[theme_id]["tokens"]
