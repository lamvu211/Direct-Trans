"""Qt theme registry — ported from samples/settings_pyside6."""

from __future__ import annotations

_COMMON = """
#root { background: transparent; }
QStackedWidget#stack, QWidget#pageHost, QWidget#scrollViewport {
    background: transparent;
}
QScrollArea#scroll { background: transparent; border: none; }
QLabel#fieldLabel { font-size: 8pt; opacity: 0.85; }
QComboBox {
    combobox-popup: 0;
}
QComboBox#combo, QComboBox#comboMini {
    padding: 2px 6px;
    min-height: 24px;
    max-height: 24px;
    min-width: 0;
    border-radius: 6px;
}
QComboBox#themeCombo {
    padding: 2px 6px;
    min-height: 24px;
    max-height: 24px;
    min-width: 120px;
    border-radius: 6px;
}
QComboBox#combo::drop-down, QComboBox#comboMini::drop-down, QComboBox#themeCombo::drop-down {
    width: 0px;
    border: none;
    background: transparent;
}
QComboBox#combo::down-arrow, QComboBox#comboMini::down-arrow, QComboBox#themeCombo::down-arrow {
    width: 0px;
    height: 0px;
    border: none;
    image: none;
}
QLabel#apiStatus {
    font-weight: 700;
    font-size: 8.5pt;
}
QLabel#apiStatus[statusKind="pass"] { color: #22c55e; }
QLabel#apiStatus[statusKind="fail"] { color: #ef4444; }
QLineEdit#line, QTextEdit#line {
    padding: 4px 8px;
    border-radius: 6px;
}
QLineEdit#line {
    min-height: 24px;
    max-height: 24px;
}
QFrame#card {
    border-radius: 10px;
}
QLabel#cardTitle {
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    padding: 0;
    margin: 0;
}
QLabel#statusBy { font-size: 8.5pt; font-weight: 600; }
QTextEdit#popupText {
    border: none;
    background: transparent;
    padding: 4px 8px;
}
QPushButton#colorBtn {
    border-radius: 6px;
    padding: 2px 8px;
    font-family: Consolas, monospace;
    font-size: 8.5pt;
    font-weight: 600;
    min-height: 24px;
    max-height: 24px;
}
QFrame#popupDivider {
    border: none;
    min-height: 1px;
    max-height: 1px;
}
QWidget#popupHeaderContainer, QWidget#popupTextContainer {
    background: transparent;
}
QFrame#fontSizeBox {
    border-radius: 6px;
    min-height: 28px;
    max-height: 28px;
}
QLabel#brandVersion {
    font-style: italic;
    font-size: 8.5pt;
    opacity: 0.8;
}
QPushButton#sizeBtn {
    border: none;
    background: transparent;
    font-weight: 700;
    font-size: 10pt;
    padding: 0 4px;
    min-height: 22px;
    max-height: 22px;
}
QLineEdit#sizeEdit {
    font-weight: 600;
    font-size: 8.5pt;
    padding: 0 2px;
    min-width: 18px;
    border: none;
    background: transparent;
}
QLineEdit#sizeEdit:focus {
    border: 1px solid rgba(128, 128, 128, 0.45);
    border-radius: 3px;
    background: rgba(255, 255, 255, 0.06);
}
QLabel#styleLabel {
    font-size: 8.5pt;
    font-weight: 600;
}
QLabel#brand { font-size: 12pt; font-weight: 700; }
QLabel#brandSub { font-size: 8pt; }
QPushButton#textLink {
    border: none;
    text-align: left;
    padding: 0;
    font-size: 8pt;
}
QToolButton#ghost, QPushButton#ghost {
    border-radius: 6px;
    padding: 2px 10px;
    min-height: 24px;
    max-height: 24px;
    font-size: 8pt;
}
QPushButton#cta {
    border-radius: 7px;
    padding: 2px 14px;
    font-weight: 600;
    min-height: 24px;
    max-height: 24px;
}
QPushButton#ctaSmall {
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 8pt;
    font-weight: 600;
    min-height: 24px;
    max-height: 24px;
}
QPushButton#showMore {
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 8pt;
    min-height: 20px;
    max-height: 22px;
}
QPushButton#navChip, QPushButton#deckChip {
    border-radius: 12px;
    padding: 4px 12px;
    font-size: 8pt;
    font-weight: 600;
    min-height: 22px;
}
QFrame#hkRow {
    border-radius: 6px;
    min-height: 24px;
    max-height: 24px;
}
QLabel#hkKey { font-family: Consolas; font-size: 8pt; font-weight: 600; }
QLabel#hkLang { font-size: 8pt; }
QLabel#hkMode {
    font-size: 7.5pt;
    padding: 2px 8px;
    border-radius: 4px;
}
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 6px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: rgba(128, 128, 128, 0.35);
    min-height: 24px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(128, 128, 128, 0.6);
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
}
QPushButton:disabled, QToolButton:disabled, QComboBox:disabled, QLineEdit:disabled {
    opacity: 0.55;
}
QPushButton#cta:disabled, QPushButton#ctaSmall:disabled {
    opacity: 1.0;
    background: #3a3a48;
    color: #8c8c98;
    border: 1px solid #4a4a58;
}
QRadioButton {
    spacing: 8px;
    font-size: 8.5pt;
}
QRadioButton::indicator {
    width: 14px;
    height: 14px;
    border-radius: 8px;
    border: 2px solid #ffffff;
    background: #ffffff;
}
QRadioButton::indicator:checked {
    border: 2px solid #ffffff;
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
        stop:0 #000000, stop:0.55 #000000, stop:0.60 #ffffff, stop:1 #ffffff);
}
QRadioButton::indicator:hover {
    border-color: #cbd5e1;
}
"""

_BASE = _COMMON + """
QWidget#tagline { font-size: 7.5pt; }
QFrame#footBar { border-top: 1px solid rgba(128,128,128,0.25); }
QFrame#topBar { border-bottom: 1px solid rgba(128,128,128,0.2); }
"""

MIDNIGHT_GOLD_QSS = """
QWidget#root, QDialog#root {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #0c0c12, stop:0.45 #141422, stop:1 #1a1528);
    border: none;
}
QWidget#popupRoot {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #0c0c12, stop:0.45 #141422, stop:1 #1a1528);
    border: 1px solid #d4af37;
}
QFrame#popupDivider { background-color: #d4af37; }
QComboBox#combo::down-arrow, QComboBox#comboMini::down-arrow, QComboBox#themeCombo::down-arrow {
    border-top-color: #d4af37;
}
QComboBox QAbstractItemView {
    background-color: #1c1c28;
    color: #f0ebe3;
    selection-background-color: #3d3550;
    selection-color: #ffe9a8;
    border: 1px solid #d4af37;
    outline: none;
}
QFrame#topBar {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #161622, stop:1 #0e0e16);
    border-bottom: 1px solid #2a2438;
}
QFrame#footBar {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #12121c, stop:1 #0a0a10);
    border-top: 1px solid #2a2438;
}
QLabel#statusBy { color: #f5e6c8; font-size: 8.5pt; font-weight: 600; }
QLabel#brand { color: #f5e6c8; font-size: 12pt; font-weight: 700; }
QLabel#brandVersion { color: #c4bdb0; font-style: italic; font-size: 8.5pt; }
QLabel#brandSub { color: #9c917b; }
QLabel#tagline { color: #9c917b; }
QFrame#card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(212, 175, 55, 0.22);
}
QLabel#cardTitle { color: #c9a227; }
QLabel, QCheckBox, QRadioButton { color: #e8e4dc; }
QComboBox#combo, QComboBox#comboMini, QComboBox#themeCombo, QLineEdit#line, QTextEdit#line {
    background: #1c1c28;
    color: #f0ebe3;
    border: 1px solid #3d3550;
}
QComboBox#combo:focus, QComboBox#comboMini:focus, QComboBox#themeCombo:focus,
QLineEdit#line:focus, QTextEdit#line:focus { border-color: #d4af37; }
QComboBox#combo:hover, QComboBox#comboMini:hover, QComboBox#themeCombo:hover {
    background: #252536;
    border-color: #55496d;
}
QPushButton#cta, QPushButton#ctaSmall {
    color: #1a1208;
    border: none;
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #f0d78c, stop:1 #c9a227);
}
QPushButton#cta:hover, QPushButton#ctaSmall:hover {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #ffe9a8, stop:1 #d4af37);
}
QPushButton#cta:focus, QPushButton#ctaSmall:focus {
    border: 1px solid #ffe9a8;
}
QPushButton#ghost, QToolButton#ghost, QPushButton#showMore {
    background: rgba(255,255,255,0.06);
    color: #c4bdb0;
    border: 1px solid #3d3550;
}
QPushButton#ghost:hover, QToolButton#ghost:hover, QPushButton#showMore:hover {
    background: rgba(255,255,255,0.12);
    border-color: #55496d;
}
QPushButton#ghost:focus, QToolButton#ghost:focus, QPushButton#showMore:focus {
    border-color: #d4af37;
}
QPushButton#textLink { color: #e8c547; }
QPushButton#textLink:hover { text-decoration: underline; color: #ffe9a8; }
QFrame#hkRow { background: rgba(0,0,0,0.25); border: 1px solid #2a2438; }
QFrame#hkRow:hover {
    background: rgba(255,255,255,0.08);
    border-color: #55496d;
}
QLabel#hkMode { background: #2a2438; color: #d4af37; }
QToolButton#hkDel, QPushButton#hkDel { color: #e57373; border: none; background: transparent; font-size: 9pt; }
QToolButton#hkDel:hover, QPushButton#hkDel:hover { color: #ff5252; background: rgba(229,115,115,0.15); border-radius: 4px; }
QPushButton#colorBtn {
    background: #1c1c28;
    border: 1px solid #3d3550;
    color: #f0ebe3;
}
QPushButton#colorBtn:hover {
    border-color: #d4af37;
    background: #252536;
}
QFrame#fontSizeBox {
    background: #1c1c28;
    border: 1px solid #3d3550;
}
QPushButton#sizeBtn { color: #f0ebe3; }
QPushButton#sizeBtn:hover { color: #d4af37; background: rgba(212, 175, 55, 0.15); border-radius: 4px; }
QLineEdit#sizeEdit { color: #f0ebe3; }
QLineEdit#sizeEdit:focus { border-color: #d4af37; background: rgba(212, 175, 55, 0.12); }
QCheckBox#optionCheck { color: #f0d78c; font-weight: 600; }
QTextEdit#popupText { color: #f0ebe3; }
""" + _BASE

AURORA_GLASS_QSS = """
QWidget#root, QDialog#root {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #1b0f2e, stop:0.35 #2d1b4e, stop:0.7 #1a3a4a, stop:1 #0f2847);
    border: none;
}
QWidget#popupRoot {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #1b0f2e, stop:0.35 #2d1b4e, stop:0.7 #1a3a4a, stop:1 #0f2847);
    border: 1px solid #c4b5fd;
}
QFrame#popupDivider { background-color: #c4b5fd; }
QComboBox#combo::down-arrow, QComboBox#comboMini::down-arrow, QComboBox#themeCombo::down-arrow {
    border-top-color: #c4b5fd;
}
QComboBox QAbstractItemView {
    background-color: #1a1030;
    color: #ede9fe;
    selection-background-color: #5b21b6;
    selection-color: #ffffff;
    border: 1px solid #a78bfa;
    outline: none;
}
QFrame#topBar {
    background: rgba(0, 0, 0, 0.2);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
QFrame#footBar {
    background: rgba(0, 0, 0, 0.25);
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}
QLabel#statusBy { color: #f8f4ff; font-size: 8.5pt; font-weight: 600; }
QLabel#brand { color: #f8f4ff; font-size: 12pt; font-weight: 700; }
QLabel#brandVersion { color: #b8a8d8; font-style: italic; font-size: 8.5pt; }
QLabel#brandSub { color: #b8a8d8; }
QLabel#tagline { color: #a78bfa; }
QFrame#card {
    background: rgba(255, 255, 255, 0.09);
    border: 1px solid rgba(255, 255, 255, 0.18);
}
QLabel#cardTitle { color: #c4b5fd; }
QLabel, QCheckBox, QRadioButton { color: #ede9fe; }
QComboBox#combo, QComboBox#comboMini, QComboBox#themeCombo, QLineEdit#line, QTextEdit#line {
    background: rgba(0,0,0,0.25);
    color: #fff;
    border: 1px solid rgba(255,255,255,0.15);
}
QComboBox#combo:focus, QComboBox#comboMini:focus, QComboBox#themeCombo:focus,
QLineEdit#line:focus, QTextEdit#line:focus { border-color: #a78bfa; }
QComboBox#combo:hover, QComboBox#comboMini:hover, QComboBox#themeCombo:hover {
    background: rgba(255,255,255,0.12);
    border-color: rgba(255,255,255,0.25);
}
QPushButton#cta, QPushButton#ctaSmall {
    border: none;
    color: white;
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #7c3aed, stop:1 #06b6d4);
}
QPushButton#cta:hover, QPushButton#ctaSmall:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #8b5cf6, stop:1 #22d3ee);
}
QPushButton#cta:focus, QPushButton#ctaSmall:focus {
    border: 1px solid #67e8f9;
}
QPushButton#ghost, QToolButton#ghost, QPushButton#showMore {
    background: rgba(255,255,255,0.06);
    color: #e9e0ff;
    border: 1px solid rgba(255,255,255,0.12);
}
QPushButton#ghost:hover, QToolButton#ghost:hover, QPushButton#showMore:hover {
    background: rgba(255,255,255,0.15);
    border-color: rgba(255,255,255,0.25);
}
QPushButton#ghost:focus, QToolButton#ghost:focus, QPushButton#showMore:focus {
    border-color: #a78bfa;
}
QPushButton#textLink { color: #67e8f9; }
QPushButton#textLink:hover { text-decoration: underline; color: #a5f3fc; }
QFrame#hkRow { background: rgba(0,0,0,0.15); border: 1px solid rgba(255,255,255,0.1); }
QFrame#hkRow:hover {
    background: rgba(255,255,255,0.12);
    border-color: rgba(255,255,255,0.25);
}
QLabel#hkMode { background: rgba(124,58,237,0.4); color: #e9d5ff; }
QToolButton#hkDel, QPushButton#hkDel { color: #f43f5e; border: none; background: transparent; font-size: 9pt; }
QToolButton#hkDel:hover, QPushButton#hkDel:hover { color: #fb7185; background: rgba(244,63,94,0.18); border-radius: 4px; }
QPushButton#colorBtn {
    background: rgba(0, 0, 0, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.18);
    color: #ede9fe;
}
QPushButton#colorBtn:hover {
    border-color: #a78bfa;
    background: rgba(0, 0, 0, 0.5);
}
QFrame#fontSizeBox {
    background: rgba(0, 0, 0, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.18);
}
QPushButton#sizeBtn { color: #ede9fe; }
QPushButton#sizeBtn:hover { color: #a78bfa; background: rgba(167, 139, 250, 0.2); border-radius: 4px; }
QLineEdit#sizeEdit { color: #ede9fe; }
QLineEdit#sizeEdit:focus { border-color: #a78bfa; background: rgba(167, 139, 250, 0.2); }
QCheckBox#optionCheck { color: #a5f3fc; font-weight: 600; }
QTextEdit#popupText { color: #ffffff; }
""" + _BASE

ROSE_CHAMPAGNE_QSS = """
QWidget#root, QDialog#root {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #fff5f7, stop:0.5 #fce7f3, stop:1 #fdf2f8);
    border: none;
}
QWidget#popupRoot {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #fff5f7, stop:0.5 #fce7f3, stop:1 #fdf2f8);
    border: 1px solid #e11d48;
}
QFrame#popupDivider { background-color: #e11d48; }
QComboBox#combo::down-arrow, QComboBox#comboMini::down-arrow, QComboBox#themeCombo::down-arrow {
    border-top-color: #be185d;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #4a1942;
    selection-background-color: #fce7f3;
    selection-color: #9d174d;
    border: 1px solid #f472b6;
    outline: none;
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
    font-size: 12pt;
    font-weight: 700;
}
QLabel#brandSub { color: #783d63; font-weight: 500; }
QLabel#brandVersion { color: #783d63; font-style: italic; font-size: 8.5pt; }
QLabel#tagline { color: #783d63; font-weight: 500; }
QFrame#card {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #ffffff, stop:1 #fff1f2);
    border: 1px solid #fbcfe8;
}
QLabel#cardTitle { color: #9d174d; }
QLabel, QCheckBox, QRadioButton { color: #4a1942; }
QComboBox#combo, QComboBox#comboMini, QComboBox#themeCombo, QLineEdit#line, QTextEdit#line {
    background: #fff;
    border: 1px solid #f9a8d4;
    color: #4a1942;
}
QComboBox#combo:focus, QComboBox#comboMini:focus, QComboBox#themeCombo:focus,
QLineEdit#line:focus, QTextEdit#line:focus { border-color: #be185d; }
QComboBox#combo:hover, QComboBox#comboMini:hover, QComboBox#themeCombo:hover {
    background: #fff1f2;
    border-color: #f472b6;
}
QPushButton#cta, QPushButton#ctaSmall {
    color: #fff;
    border: none;
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #f472b6, stop:1 #be185d);
}
QPushButton#cta:hover, QPushButton#ctaSmall:hover {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #f472b6, stop:1 #9d174d);
}
QPushButton#cta:focus, QPushButton#ctaSmall:focus {
    border: 1px solid #9d174d;
}
QPushButton#ghost, QToolButton#ghost, QPushButton#showMore {
    background: #fff;
    color: #9d174d;
    border: 1px solid #f9a8d4;
}
QPushButton#ghost:hover, QToolButton#ghost:hover, QPushButton#showMore:hover {
    background: #fff1f2;
    border-color: #f472b6;
}
QPushButton#ghost:focus, QToolButton#ghost:focus, QPushButton#showMore:focus {
    border-color: #be185d;
}
QPushButton#textLink { color: #b81463; font-weight: 600; }
QPushButton#textLink:hover { text-decoration: underline; color: #9d174d; }
QFrame#hkRow { background: #fff; border: 1px solid #fce7f3; }
QFrame#hkRow:hover {
    background: #fff1f2;
    border-color: #f472b6;
}
QLabel#hkMode { background: #fce7f3; color: #9d174d; }
QToolButton#hkDel, QPushButton#hkDel { color: #be185d; border: none; background: transparent; font-size: 9pt; }
QToolButton#hkDel:hover, QPushButton#hkDel:hover { color: #9d174d; background: rgba(190,24,93,0.12); border-radius: 4px; }
QCheckBox#optionCheck { color: #be185d; font-weight: 600; }
QLabel#statusBy { color: #9d174d; font-size: 8.5pt; font-weight: 600; }
QTextEdit#popupText { color: #4C4F69; }
QPushButton#colorBtn {
    background: #ffffff;
    border: 1px solid #f9a8d4;
    color: #4C4F69;
}
QPushButton#colorBtn:hover {
    border-color: #be185d;
    background: #fff1f2;
}
QFrame#fontSizeBox {
    background: #ffffff;
    border: 1px solid #f9a8d4;
}
QPushButton#sizeBtn {
    color: #4C4F69;
}
QPushButton#sizeBtn:hover {
    color: #be185d;
    background: #fff1f2;
}
QLineEdit#sizeEdit {
    color: #4C4F69;
}
QLineEdit#sizeEdit:focus {
    border-color: #be185d;
    background: #fff1f2;
}
""" + _BASE

NORD_SNOW_QSS = """
QWidget#root, QDialog#root {
    background: #ECEFF4;
    border: none;
}
QWidget#popupRoot {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #ECEFF4, stop:1 #E5E9F0);
    border: 1px solid #5E81AC;
}
QFrame#popupDivider { background-color: #5E81AC; }
QComboBox#combo::down-arrow, QComboBox#comboMini::down-arrow, QComboBox#themeCombo::down-arrow {
    border-top-color: #5E81AC;
}
QComboBox QAbstractItemView {
    background-color: #ECEFF4;
    color: #2E3440;
    selection-background-color: #D8DEE9;
    selection-color: #4C6F94;
    border: 1px solid #D8DEE9;
    outline: none;
}
QFrame#topBar {
    background: #E5E9F0;
    border-bottom: 1px solid #D8DEE9;
}
QFrame#footBar {
    background: #E5E9F0;
    border-top: 1px solid #D8DEE9;
}
QLabel#brand {
    color: #2E3440;
    font-size: 12pt;
    font-weight: 700;
}
QLabel#brandSub { color: #4C566A; font-weight: 500; }
QLabel#brandVersion { color: #4C566A; font-style: italic; font-size: 8.5pt; }
QLabel#tagline { color: #4C566A; font-weight: 500; }
QFrame#card {
    background: #ECEFF4;
    border: 1px solid #D8DEE9;
}
QLabel#cardTitle { color: #3B4252; }
QLabel, QCheckBox, QRadioButton { color: #2E3440; }
QComboBox#combo, QComboBox#comboMini, QComboBox#themeCombo, QLineEdit#line, QTextEdit#line {
    background: #ECEFF4;
    border: 1px solid #D8DEE9;
    color: #2E3440;
}
QComboBox#combo:focus, QComboBox#comboMini:focus, QComboBox#themeCombo:focus,
QLineEdit#line:focus, QTextEdit#line:focus { border-color: #5E81AC; }
QComboBox#combo:hover, QComboBox#comboMini:hover, QComboBox#themeCombo:hover {
    background: #E5E9F0;
    border-color: #C0C8D4;
}
QPushButton#cta, QPushButton#ctaSmall {
    color: #ECEFF4;
    border: none;
    background: #5E81AC;
}
QPushButton#cta:hover, QPushButton#ctaSmall:hover {
    background: #4C6F94;
}
QPushButton#cta:focus, QPushButton#ctaSmall:focus {
    border: 1px solid #4C6F94;
}
QPushButton#cta:disabled, QPushButton#ctaSmall:disabled {
    opacity: 1.0;
    background: #D8DEE9;
    color: #4C566A;
    border: 1px solid #C0C8D4;
}
QPushButton#ghost, QToolButton#ghost, QPushButton#showMore {
    background: #ECEFF4;
    color: #2E3440;
    border: 1px solid #D8DEE9;
}
QPushButton#ghost:hover, QToolButton#ghost:hover, QPushButton#showMore:hover {
    background: #E5E9F0;
    border-color: #C0C8D4;
}
QPushButton#ghost:focus, QToolButton#ghost:focus, QPushButton#showMore:focus {
    border-color: #5E81AC;
}
QPushButton#textLink { color: #5E81AC; font-weight: 600; }
QPushButton#textLink:hover { text-decoration: underline; color: #4C6F94; }
QFrame#hkRow { background: #E5E9F0; border: 1px solid #D8DEE9; }
QFrame#hkRow:hover {
    background: #ECEFF4;
    border-color: #C0C8D4;
}
QLabel#hkMode { background: #D8DEE9; color: #5E81AC; }
QToolButton#hkDel, QPushButton#hkDel { color: #BF616A; border: none; background: transparent; font-size: 9pt; }
QToolButton#hkDel:hover, QPushButton#hkDel:hover { color: #A54E56; background: rgba(191,97,106,0.12); border-radius: 4px; }
QCheckBox#optionCheck { color: #5E81AC; font-weight: 600; }
QLabel#statusBy { color: #3B4252; font-size: 8.5pt; font-weight: 600; }
QTextEdit#popupText { color: #2E3440; }
QPushButton#colorBtn {
    background: #ECEFF4;
    border: 1px solid #D8DEE9;
    color: #2E3440;
}
QPushButton#colorBtn:hover {
    border-color: #5E81AC;
    background: #E5E9F0;
}
QFrame#fontSizeBox {
    background: #ECEFF4;
    border: 1px solid #D8DEE9;
}
QPushButton#sizeBtn {
    color: #2E3440;
}
QPushButton#sizeBtn:hover {
    color: #5E81AC;
    background: #D8DEE9;
}
QLineEdit#sizeEdit {
    color: #2E3440;
}
QLineEdit#sizeEdit:focus {
    border-color: #5E81AC;
    background: #ECEFF4;
}
QRadioButton::indicator {
    width: 14px;
    height: 14px;
    border-radius: 8px;
    border: 2px solid #D8DEE9;
    background: #ECEFF4;
}
QRadioButton::indicator:checked {
    border: 2px solid #5E81AC;
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
        stop:0 #5E81AC, stop:0.55 #5E81AC, stop:0.60 #ECEFF4, stop:1 #ECEFF4);
}
QRadioButton::indicator:hover {
    border-color: #5E81AC;
}
""" + _BASE

THEME_IDS = ("midnight_gold", "aurora_glass", "rose_champagne", "nord_snow")

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
    "nord_snow": {
        "label": "Nord Snow",
        "tagline": "Frost gray · Nord-inspired · blue accent",
        "qss": NORD_SNOW_QSS,
    },
}

DEFAULT_THEME_ID = "midnight_gold"


def qss_for(theme_id: str) -> str:
    return THEMES[theme_id]["qss"]


def label_for(theme_id: str) -> str:
    return THEMES[theme_id]["label"]


def tagline_for(theme_id: str) -> str:
    return THEMES[theme_id]["tagline"]


def apply_theme(widget, theme_id: str) -> None:
    if theme_id not in THEME_IDS:
        theme_id = DEFAULT_THEME_ID
    widget.setStyleSheet(qss_for(theme_id))
