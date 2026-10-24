"""Luxury compact palettes — gradients via Qt Style Sheets."""

from premium_layout import PremiumLayout, PremiumMeta

_COMMON = """
#root { background: transparent; }
QStackedWidget#stack, QWidget#pageHost, QWidget#scrollViewport {
    background: transparent;
}
QScrollArea#scroll { background: transparent; border: none; }
QLabel#fieldLabel { font-size: 8pt; opacity: 0.85; }
QComboBox#combo, QComboBox#comboMini {
    padding: 4px 8px;
    min-height: 22px;
    border-radius: 6px;
}
QLineEdit#line {
    padding: 5px 8px;
    border-radius: 6px;
    min-height: 20px;
}
QFrame#card {
    border-radius: 10px;
}
QLabel#cardTitle {
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
QLabel#brand { font-size: 11pt; font-weight: 700; }
QLabel#brandSub { font-size: 7pt; }
QPushButton#textLink {
    border: none;
    text-align: left;
    padding: 0;
    font-size: 8pt;
}
QToolButton#ghost, QPushButton#ghost {
    border-radius: 6px;
    padding: 4px 10px;
    min-height: 22px;
    font-size: 8pt;
}
QPushButton#cta {
    border-radius: 7px;
    padding: 5px 14px;
    font-weight: 600;
    min-height: 24px;
}
QPushButton#ctaSmall {
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 8pt;
}
QPushButton#navChip, QPushButton#deckChip {
    border-radius: 12px;
    padding: 4px 12px;
    font-size: 8pt;
    font-weight: 600;
    min-height: 22px;
}
QFrame#hkRow { border-radius: 6px; }
QLabel#hkKey { font-family: Consolas; font-size: 8pt; font-weight: 600; }
QLabel#hkLang { font-size: 8pt; }
QLabel#hkMode {
    font-size: 7pt;
    padding: 2px 6px;
    border-radius: 4px;
}
"""


def _midnight_gold() -> tuple[PremiumMeta, str]:
    meta = PremiumMeta(1, "Midnight Gold", "Obsidian canvas · gilded accents", PremiumLayout.PANEL)
    qss = """
    QWidget#root {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
            stop:0 #0c0c12, stop:0.45 #141422, stop:1 #1a1528);
    }
    QFrame#sidePanel {
        background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 #12121c, stop:1 #0a0a10);
        border-right: 1px solid #2a2438;
        min-width: 118px;
        max-width: 118px;
    }
    QLabel#sideBrand { color: #f5e6c8; font-size: 12pt; font-weight: 700; }
    QLabel#sideTag { color: #8a7f6a; font-size: 7pt; }
    QPushButton#sideNav {
        text-align: left;
        padding: 8px 10px;
        border: none;
        border-radius: 8px;
        color: #a89f8c;
        background: transparent;
    }
    QPushButton#sideNav:checked {
        color: #1a1208;
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 #d4af37, stop:1 #f0d78c);
    }
    QFrame#card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(212, 175, 55, 0.22);
    }
    QLabel#cardTitle { color: #c9a227; }
    QLabel, QCheckBox { color: #e8e4dc; }
    QComboBox#combo, QComboBox#comboMini, QLineEdit#line {
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
    QPushButton#cta:hover { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #ffe9a8, stop:1 #d4af37); }
    QPushButton#ghost, QToolButton#ghost {
        background: rgba(255,255,255,0.06);
        color: #c4bdb0;
        border: 1px solid #3d3550;
    }
    QPushButton#textLink { color: #e8c547; }
    QFrame#hkRow { background: rgba(0,0,0,0.25); border: 1px solid #2a2438; }
    QLabel#hkMode { background: #2a2438; color: #d4af37; }
    QToolButton#hkDel { color: #c75c5c; border: none; background: transparent; }
    QCheckBox#optionCheck { color: #f0d78c; }
    """ + _COMMON
    return meta, qss


def _aurora_glass() -> tuple[PremiumMeta, str]:
    meta = PremiumMeta(2, "Aurora Glass", "Violet dawn · frosted cards", PremiumLayout.STRIP)
    qss = """
    QWidget#root {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
            stop:0 #1b0f2e, stop:0.35 #2d1b4e, stop:0.7 #1a3a4a, stop:1 #0f2847);
    }
    QFrame#topBar { background: transparent; }
    QLabel#brand { color: #f8f4ff; }
    QLabel#brandSub { color: #b8a8d8; }
    QFrame#navStrip { background: transparent; padding: 0 8px; }
    QPushButton#navChip {
        background: rgba(255,255,255,0.08);
        color: #d8cef0;
        border: 1px solid rgba(255,255,255,0.12);
    }
    QPushButton#navChip:checked {
        color: #fff;
        border: 1px solid rgba(255,255,255,0.35);
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 #7c3aed, stop:1 #22d3ee);
    }
    QFrame#card {
        background: rgba(255, 255, 255, 0.09);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    QLabel#cardTitle { color: #c4b5fd; }
    QLabel, QCheckBox { color: #ede9fe; }
    QComboBox#combo, QLineEdit#line {
        background: rgba(0,0,0,0.2);
        color: #fff;
        border: 1px solid rgba(255,255,255,0.15);
    }
    QPushButton#cta {
        border: none;
        color: white;
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #7c3aed, stop:1 #06b6d4);
    }
    QPushButton#ctaSmall { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #6366f1, stop:1 #8b5cf6); color: white; border: none; }
    QPushButton#ghost, QToolButton#ghost {
        background: rgba(255,255,255,0.06);
        color: #e9e0ff;
        border: 1px solid rgba(255,255,255,0.12);
    }
    QPushButton#textLink { color: #67e8f9; }
    QFrame#hkRow { background: rgba(0,0,0,0.15); border: 1px solid rgba(255,255,255,0.1); }
    QLabel#hkMode { background: rgba(124,58,237,0.4); color: #e9d5ff; }
    QCheckBox#optionCheck { color: #a5f3fc; }
    """ + _COMMON
    return meta, qss


def _rose_champagne() -> tuple[PremiumMeta, str]:
    meta = PremiumMeta(3, "Rose Champagne", "Warm blush · editorial compact", PremiumLayout.DECK)
    qss = """
    QWidget#root {
        background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 #fff5f7, stop:0.5 #fce7f3, stop:1 #fdf2f8);
    }
    QLabel#brand { color: #4a1942; font-family: Georgia; font-size: 12pt; }
    QLabel#brandSub { color: #9d6b8a; }
    QFrame#deckNav { background: transparent; padding: 0 10px 4px; }
    QPushButton#deckChip {
        background: rgba(255,255,255,0.7);
        color: #7c3d5e;
        border: 1px solid #f9a8d4;
    }
    QPushButton#deckChip:checked {
        color: #fff;
        border: none;
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 #be185d, stop:1 #f472b6);
    }
    QFrame#card {
        background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 #ffffff, stop:1 #fff1f2);
        border: 1px solid #fbcfe8;
    }
    QLabel#cardTitle { color: #9d174d; }
    QLabel, QCheckBox { color: #4a1942; }
    QComboBox#combo, QComboBox#comboMini, QLineEdit#line {
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
    QPushButton#ghost, QToolButton#ghost {
        background: #fff;
        color: #9d174d;
        border: 1px solid #f9a8d4;
    }
    QPushButton#textLink { color: #db2777; }
    QFrame#footBar {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 rgba(255,255,255,0.9), stop:1 rgba(252,231,243,0.95));
        border-top: 1px solid #fbcfe8;
    }
    QFrame#hkRow { background: #fff; border: 1px solid #fce7f3; }
    QLabel#hkMode { background: #fce7f3; color: #9d174d; }
    QCheckBox#optionCheck { color: #be185d; font-weight: 600; }
    """ + _COMMON
    return meta, qss


def _emerald_split() -> tuple[PremiumMeta, str]:
    meta = PremiumMeta(4, "Emerald Noir", "Split deck · jewel green", PremiumLayout.SPLIT)
    qss = """
    QWidget#root {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
            stop:0 #021a14, stop:0.5 #042f23, stop:1 #010a08);
    }
    QFrame#topBar { background: transparent; border-bottom: 1px solid #0d3d32; }
    QLabel#brand { color: #ecfdf5; }
    QLabel#brandSub { color: #6ee7b7; }
    QFrame#card {
        background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 rgba(16, 185, 129, 0.08), stop:1 rgba(0,0,0,0.35));
        border: 1px solid #065f46;
    }
    QLabel#cardTitle { color: #34d399; }
    QLabel, QCheckBox { color: #d1fae5; }
    QComboBox#combo, QLineEdit#line {
        background: #022c22;
        color: #ecfdf5;
        border: 1px solid #047857;
    }
    QPushButton#cta, QPushButton#ctaSmall {
        color: #022c22;
        font-weight: 700;
        border: none;
        background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 #6ee7b7, stop:1 #059669);
    }
    QPushButton#ghost, QToolButton#ghost {
        background: #022c22;
        color: #6ee7b7;
        border: 1px solid #047857;
    }
    QPushButton#textLink { color: #2dd4bf; }
    QFrame#hkRow { background: #011a14; border: 1px solid #065f46; }
    QLabel#hkMode { background: #064e3b; color: #6ee7b7; }
    QCheckBox#optionCheck { color: #34d399; }
    """ + _COMMON
    return meta, qss


def _sapphire_rail() -> tuple[PremiumMeta, str]:
    meta = PremiumMeta(5, "Sapphire Rail", "Ocean rail · platinum UI", PremiumLayout.RAIL)
    qss = """
    QWidget#root {
        background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 #0f172a, stop:0.4 #1e3a5f, stop:1 #0c1929);
    }
    QFrame#rail {
        background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 #1e293b, stop:1 #0f172a);
        border-right: 1px solid #334155;
        max-width: 48px;
    }
    QPushButton#railBtn {
        border-radius: 10px;
        border: 1px solid transparent;
        background: transparent;
        color: #94a3b8;
        font-size: 14px;
    }
    QPushButton#railBtn:checked {
        color: #fff;
        border: 1px solid #38bdf8;
        background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 #0ea5e9, stop:1 #0369a1);
    }
    QLabel#brand { color: #f1f5f9; }
    QLabel#brandSub { color: #7dd3fc; }
    QPushButton#navChip {
        background: #1e293b;
        color: #94a3b8;
        border: 1px solid #334155;
    }
    QPushButton#navChip:checked {
        color: #f0f9ff;
        border: 1px solid #38bdf8;
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #0284c7, stop:1 #38bdf8);
    }
    QFrame#card {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid #334155;
    }
    QLabel#cardTitle { color: #7dd3fc; }
    QLabel, QCheckBox { color: #e2e8f0; }
    QComboBox#combo, QLineEdit#line {
        background: #0f172a;
        color: #f1f5f9;
        border: 1px solid #475569;
    }
    QPushButton#cta, QPushButton#ctaSmall {
        color: #fff;
        border: none;
        background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 #38bdf8, stop:1 #0284c7);
    }
    QPushButton#ghost, QToolButton#ghost {
        background: #1e293b;
        color: #bae6fd;
        border: 1px solid #475569;
    }
    QPushButton#textLink { color: #38bdf8; }
    QFrame#hkRow { background: #0f172a; border: 1px solid #334155; }
    QLabel#hkMode { background: #1e3a5f; color: #7dd3fc; }
    QCheckBox#optionCheck { color: #38bdf8; }
    """ + _COMMON
    return meta, qss


PREMIUM_THEMES = [
    _midnight_gold,
    _aurora_glass,
    _rose_champagne,
    _emerald_split,
    _sapphire_rail,
]
