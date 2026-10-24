"""All-in-one Settings themes — registry for runtime theme switch."""

from __future__ import annotations

from premium_themes import _COMMON

_BASE = _COMMON + """
QWidget#tagline { font-size: 7pt; }
QFrame#footBar { border-top: 1px solid rgba(128,128,128,0.25); }
QFrame#topBar { border-bottom: 1px solid rgba(128,128,128,0.2); }
QComboBox#themeCombo { min-width: 128px; }
"""

MIDNIGHT_GOLD_QSS = """
QWidget#root {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #0c0c12, stop:0.45 #141422, stop:1 #1a1528);
}
QFrame#topBar {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #161622, stop:1 #0e0e16);
    border-bottom: 1px solid #2a2438;
}
QFrame#footBar {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #12121c, stop:1 #0a0a10);
    border-top: 1px solid #2a2438;
}
QLabel#brand { color: #f5e6c8; font-size: 12pt; font-weight: 700; }
QLabel#brandSub { color: #8a7f6a; }
QLabel#tagline { color: #8a7f6a; }
QFrame#card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(212, 175, 55, 0.22);
}
QLabel#cardTitle { color: #c9a227; }
QLabel, QCheckBox { color: #e8e4dc; }
QComboBox#combo, QComboBox#comboMini, QComboBox#themeCombo, QLineEdit#line {
    background: #1c1c28;
    color: #f0ebe3;
    border: 1px solid #3d3550;
}
QComboBox#combo:focus, QLineEdit#line:focus { border-color: #d4af37; }
QPushButton#cta, QPushButton#ctaSmall {
    color: #1a1208;
    border: none;
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #f0d78c, stop:1 #c9a227);
}
QPushButton#cta:hover {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #ffe9a8, stop:1 #d4af37);
}
QPushButton#ghost, QToolButton#ghost, QPushButton#showMore {
    background: rgba(255,255,255,0.06);
    color: #c4bdb0;
    border: 1px solid #3d3550;
}
QPushButton#textLink { color: #e8c547; }
QFrame#hkRow { background: rgba(0,0,0,0.25); border: 1px solid #2a2438; }
QLabel#hkMode { background: #2a2438; color: #d4af37; }
QToolButton#hkDel { color: #c75c5c; border: none; background: transparent; }
QCheckBox#optionCheck { color: #f0d78c; font-weight: 600; }
""" + _BASE

AURORA_GLASS_QSS = """
QWidget#root {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #1b0f2e, stop:0.35 #2d1b4e, stop:0.7 #1a3a4a, stop:1 #0f2847);
}
QFrame#topBar {
    background: rgba(0, 0, 0, 0.2);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
QFrame#footBar {
    background: rgba(0, 0, 0, 0.25);
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}
QLabel#brand { color: #f8f4ff; font-size: 12pt; font-weight: 700; }
QLabel#brandSub { color: #b8a8d8; }
QLabel#tagline { color: #a78bfa; }
QFrame#card {
    background: rgba(255, 255, 255, 0.09);
    border: 1px solid rgba(255, 255, 255, 0.18);
}
QLabel#cardTitle { color: #c4b5fd; }
QLabel, QCheckBox { color: #ede9fe; }
QComboBox#combo, QComboBox#comboMini, QComboBox#themeCombo, QLineEdit#line {
    background: rgba(0,0,0,0.25);
    color: #fff;
    border: 1px solid rgba(255,255,255,0.15);
}
QPushButton#cta, QPushButton#ctaSmall {
    border: none;
    color: white;
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #7c3aed, stop:1 #06b6d4);
}
QPushButton#ghost, QToolButton#ghost, QPushButton#showMore {
    background: rgba(255,255,255,0.06);
    color: #e9e0ff;
    border: 1px solid rgba(255,255,255,0.12);
}
QPushButton#textLink { color: #67e8f9; }
QFrame#hkRow { background: rgba(0,0,0,0.15); border: 1px solid rgba(255,255,255,0.1); }
QLabel#hkMode { background: rgba(124,58,237,0.4); color: #e9d5ff; }
QCheckBox#optionCheck { color: #a5f3fc; font-weight: 600; }
""" + _BASE

ROSE_CHAMPAGNE_QSS = """
QWidget#root {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #fff5f7, stop:0.5 #fce7f3, stop:1 #fdf2f8);
}
QFrame#topBar {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #ffffff, stop:1 #fce7f3);
    border-bottom: 1px solid #fbcfe8;
}
QFrame#footBar {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 rgba(255,255,255,0.95), stop:1 #fce7f3);
    border-top: 1px solid #fbcfe8;
}
QLabel#brand {
    color: #4a1942;
    font-family: Georgia;
    font-size: 12pt;
    font-weight: 700;
}
QLabel#brandSub { color: #9d6b8a; }
QLabel#tagline { color: #9d6b8a; }
QFrame#card {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #ffffff, stop:1 #fff1f2);
    border: 1px solid #fbcfe8;
}
QLabel#cardTitle { color: #9d174d; }
QLabel, QCheckBox { color: #4a1942; }
QComboBox#combo, QComboBox#comboMini, QComboBox#themeCombo, QLineEdit#line {
    background: #fff;
    border: 1px solid #f9a8d4;
    color: #4a1942;
}
QPushButton#cta, QPushButton#ctaSmall {
    color: #fff;
    border: none;
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #f472b6, stop:1 #be185d);
}
QPushButton#ghost, QToolButton#ghost, QPushButton#showMore {
    background: #fff;
    color: #9d174d;
    border: 1px solid #f9a8d4;
}
QPushButton#textLink { color: #db2777; }
QFrame#hkRow { background: #fff; border: 1px solid #fce7f3; }
QLabel#hkMode { background: #fce7f3; color: #9d174d; }
QCheckBox#optionCheck { color: #be185d; font-weight: 600; }
""" + _BASE

THEME_IDS = ("midnight_gold", "aurora_glass", "rose_champagne")

THEMES: dict[str, dict[str, str]] = {
    "midnight_gold": {
        "label": "Midnight Gold",
        "tagline": "Obsidian canvas · gilded accents",
        "qss": MIDNIGHT_GOLD_QSS,
    },
    "aurora_glass": {
        "label": "Aurora Glass",
        "tagline": "Violet dawn · frosted cards",
        "qss": AURORA_GLASS_QSS,
    },
    "rose_champagne": {
        "label": "Rose Champagne",
        "tagline": "Warm blush · editorial compact",
        "qss": ROSE_CHAMPAGNE_QSS,
    },
}

DEFAULT_THEME_ID = "midnight_gold"


def qss_for(theme_id: str) -> str:
    return THEMES[theme_id]["qss"]


def label_for(theme_id: str) -> str:
    return THEMES[theme_id]["label"]


def tagline_for(theme_id: str) -> str:
    return THEMES[theme_id]["tagline"]


# Legacy factories for export loop
def midnight_gold():
    from allinone_layout import AllInOneMeta
    return AllInOneMeta(1, label_for("midnight_gold"), tagline_for("midnight_gold")), qss_for("midnight_gold")


def aurora_glass():
    from allinone_layout import AllInOneMeta
    return AllInOneMeta(2, label_for("aurora_glass"), tagline_for("aurora_glass")), qss_for("aurora_glass")


def rose_champagne():
    from allinone_layout import AllInOneMeta
    return AllInOneMeta(3, label_for("rose_champagne"), tagline_for("rose_champagne")), qss_for("rose_champagne")


ALLINONE_THEMES = [midnight_gold, aurora_glass, rose_champagne]
