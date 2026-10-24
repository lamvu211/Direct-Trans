"""
Compact, premium DirectTrans Settings — PySide6 + gradient QSS.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

ASSETS = Path(__file__).resolve().parents[2] / "src" / "assets"
LOGO_PATH = ASSETS / "logo-direct-trans.png"

HOTKEY_ROWS = [
    ("ctrl+shift+v", "Tiếng Việt", "popup"),
    ("ctrl+shift+e", "English", "popup"),
    ("ctrl+shift+k", "한국어", "popup"),
    ("ctrl+shift+j", "日本語", "popup"),
]


class PremiumLayout(Enum):
    RAIL = "rail"           # Icon rail + stacked pages
    SPLIT = "split"         # 2-column cards
    STRIP = "strip"         # Top chips + single scroll
    DECK = "deck"           # Ultra-compact command deck
    PANEL = "panel"         # Left gradient panel + right content


@dataclass
class PremiumMeta:
    id: int
    title: str
    tagline: str
    layout: PremiumLayout


def _logo() -> QLabel:
    lb = QLabel()
    lb.setObjectName("logo")
    if LOGO_PATH.exists():
        px = QPixmap(str(LOGO_PATH)).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        lb.setPixmap(px)
    return lb


def _chip_nav(buttons: list[str], object_name: str = "navChip") -> tuple[QHBoxLayout, QButtonGroup, list[QPushButton]]:
    group = QButtonGroup()
    group.setExclusive(True)
    lay = QHBoxLayout()
    lay.setSpacing(4)
    btns: list[QPushButton] = []
    for i, text in enumerate(buttons):
        b = QPushButton(text)
        b.setObjectName(object_name)
        b.setCheckable(True)
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        if i == 0:
            b.setChecked(True)
        group.addButton(b, i)
        lay.addWidget(b)
        btns.append(b)
    lay.addStretch()
    return lay, group, btns


def _card(title: str, object_name: str = "card") -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName(object_name)
    outer = QVBoxLayout(frame)
    outer.setContentsMargins(10, 8, 10, 10)
    outer.setSpacing(6)
    if title:
        t = QLabel(title)
        t.setObjectName("cardTitle")
        outer.addWidget(t)
    body = QVBoxLayout()
    body.setSpacing(6)
    outer.addLayout(body)
    return frame, body


def _api_block(compact: bool = True, show_provider_row: bool = True) -> QWidget:
    w = QWidget()
    g = QGridLayout(w)
    g.setContentsMargins(0, 0, 0, 0)
    g.setHorizontalSpacing(8)
    g.setVerticalSpacing(5)

    row = 0
    if compact and show_provider_row:
        g.addWidget(QLabel("Provider"), 0, 0)
        prov = QComboBox()
        prov.addItems(["Gemini", "Groq", "Mistral", "Google Free"])
        prov.setObjectName("combo")
        g.addWidget(prov, 0, 1)
        g.addWidget(QLabel("Model"), 0, 2)
        model = QComboBox()
        model.addItem("gemini-flash-lite-latest")
        model.setObjectName("combo")
        g.addWidget(model, 0, 3)
        g.setColumnStretch(1, 1)
        g.setColumnStretch(3, 2)
        row = 1
    elif compact:
        g.addWidget(QLabel("Model"), 0, 0)
        model = QComboBox()
        model.addItem("gemini-flash-lite-latest")
        model.setObjectName("combo")
        g.addWidget(model, 0, 1, 1, 3)
        g.setColumnStretch(1, 1)
        row = 1

    key_l = QLabel("API key")
    key_l.setObjectName("fieldLabel")
    g.addWidget(key_l, row, 0, Qt.AlignmentFlag.AlignTop)
    key_row = QHBoxLayout()
    key = QLineEdit()
    key.setEchoMode(QLineEdit.EchoMode.Password)
    key.setText("••••••••••••")
    key.setObjectName("line")
    clr = QToolButton()
    clr.setText("✕")
    clr.setObjectName("ghost")
    key_row.addWidget(key, 1)
    key_row.addWidget(clr)
    g.addLayout(key_row, row, 1, 1, 3)

    link = QPushButton("Get API key →")
    link.setObjectName("textLink")
    link.setFlat(True)
    g.addWidget(link, row + 1, 1, 1, 3, Qt.AlignmentFlag.AlignLeft)

    bar = QHBoxLayout()
    bar.setSpacing(6)
    for label, oid in (("↻ Models", "ghost"), ("Test", "ghost"), ("Save", "cta")):
        b = QPushButton(label)
        b.setObjectName(oid)
        bar.addWidget(b)
    bar.addStretch()
    g.addLayout(bar, row + 2, 0, 1, 4)
    return w


def _hotkey_list(compact: bool) -> QWidget:
    w = QWidget()
    v = QVBoxLayout(w)
    v.setContentsMargins(0, 0, 0, 0)
    v.setSpacing(3)
    for hk, lang, mode in HOTKEY_ROWS:
        row = QFrame()
        row.setObjectName("hkRow")
        h = QHBoxLayout(row)
        h.setContentsMargins(8, 4, 6, 4)
        h.setSpacing(6)
        k = QLabel(hk)
        k.setObjectName("hkKey")
        lg = QLabel(lang)
        lg.setObjectName("hkLang")
        m = QLabel(mode)
        m.setObjectName("hkMode")
        delb = QToolButton()
        delb.setText("✕")
        delb.setObjectName("hkDel")
        h.addWidget(k)
        h.addWidget(lg, 1)
        h.addWidget(m)
        h.addWidget(delb)
        v.addWidget(row)
    add = QPushButton("+ Hotkey")
    add.setObjectName("ctaSmall")
    add.setFixedHeight(26)
    v.addWidget(add, alignment=Qt.AlignmentFlag.AlignLeft)
    return w


def _options_block() -> QWidget:
    w = QWidget()
    h = QHBoxLayout(w)
    h.setContentsMargins(0, 0, 0, 0)
    cb = QCheckBox("Launch with Windows")
    cb.setObjectName("optionCheck")
    cb.setChecked(True)
    h.addWidget(cb)
    h.addStretch()
    manual = QPushButton("Manual")
    manual.setObjectName("ghost")
    feedback = QPushButton("Feedback")
    feedback.setObjectName("ghost")
    h.addWidget(manual)
    h.addWidget(feedback)
    return w


def _transparent_page(host: QWidget) -> None:
    host.setObjectName("pageHost")
    host.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)


def _prep_scroll(scroll: QScrollArea) -> None:
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setObjectName("scroll")
    scroll.setAutoFillBackground(False)
    scroll.viewport().setObjectName("scrollViewport")
    scroll.viewport().setAutoFillBackground(False)
    scroll.viewport().setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)


def _page_api() -> QWidget:
    w = QWidget()
    _transparent_page(w)
    lay = QVBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    card, body = _card("Translation & API")
    body.addWidget(_api_block(True))
    lay.addWidget(card)
    return w


def _page_hotkeys() -> QWidget:
    w = QWidget()
    _transparent_page(w)
    lay = QVBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    card, body = _card("Shortcuts")
    body.addWidget(_hotkey_list(True))
    lay.addWidget(card)
    return w


def _page_general() -> QWidget:
    w = QWidget()
    _transparent_page(w)
    lay = QVBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    card, body = _card("General")
    body.addWidget(_options_block())
    lay.addWidget(card)
    card2, body2 = _card("Language")
    lang = QComboBox()
    lang.addItems(["English", "Tiếng Việt", "한국어", "中文", "日本語"])
    lang.setObjectName("combo")
    body2.addWidget(lang)
    lay.addWidget(card2)
    return w


def _header_compact(show_actions: bool = True) -> QFrame:
    bar = QFrame()
    bar.setObjectName("topBar")
    h = QHBoxLayout(bar)
    h.setContentsMargins(10, 8, 10, 6)
    h.setSpacing(8)
    h.addWidget(_logo())
    title = QLabel("DirectTrans")
    title.setObjectName("brand")
    sub = QLabel("Settings")
    sub.setObjectName("brandSub")
    brand = QVBoxLayout()
    brand.setSpacing(0)
    brand.addWidget(title)
    brand.addWidget(sub)
    h.addLayout(brand)
    h.addStretch()
    if show_actions:
        upd = QPushButton("Update")
        upd.setObjectName("ghost")
        upd.setFixedHeight(24)
        h.addWidget(upd)
    return bar


def build_premium_window(meta: PremiumMeta, qss: str) -> QWidget:
    win = QWidget()
    win.setObjectName("root")
    win.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    win.setWindowTitle(f"Premium {meta.id}: {meta.title}")
    win.resize(500, 460)
    win.setMinimumSize(460, 400)
    win.setMaximumWidth(540)

    root = QVBoxLayout(win)
    root.setContentsMargins(0, 0, 0, 0)
    root.setSpacing(0)

    stack = QStackedWidget()
    stack.setObjectName("stack")
    stack.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    stack.addWidget(_page_api())
    stack.addWidget(_page_hotkeys())
    stack.addWidget(_page_general())
    nav_labels = ["API", "Hotkeys", "General"]

    if meta.layout == PremiumLayout.PANEL:
        shell = QHBoxLayout()
        shell.setSpacing(0)
        panel = QFrame()
        panel.setObjectName("sidePanel")
        pv = QVBoxLayout(panel)
        pv.setContentsMargins(12, 14, 12, 14)
        pv.setSpacing(10)
        pv.addWidget(_logo())
        brand = QLabel("DirectTrans")
        brand.setObjectName("sideBrand")
        pv.addWidget(brand)
        tag = QLabel(meta.tagline)
        tag.setObjectName("sideTag")
        tag.setWordWrap(True)
        pv.addWidget(tag)
        pv.addSpacing(8)
        side_group = QButtonGroup(win)
        for i, lab in enumerate(nav_labels):
            b = QPushButton(lab)
            b.setObjectName("sideNav")
            b.setCheckable(True)
            if i == 0:
                b.setChecked(True)
            side_group.addButton(b, i)
            pv.addWidget(b)
        pv.addStretch()
        lang = QComboBox()
        lang.addItems(["EN", "VI", "KO", "ZH", "JA"])
        lang.setObjectName("comboMini")
        pv.addWidget(lang)
        shell.addWidget(panel)
        content = QVBoxLayout()
        content.setContentsMargins(10, 10, 10, 10)
        content_w = QWidget()
        content_w.setLayout(content)
        content.addWidget(stack, 1)
        shell.addWidget(content_w, 1)
        wrap = QWidget()
        wrap.setLayout(shell)
        root.addWidget(wrap, 1)
        side_group.idClicked.connect(stack.setCurrentIndex)

    elif meta.layout == PremiumLayout.SPLIT:
        root.addWidget(_header_compact())
        body = QHBoxLayout()
        body.setContentsMargins(8, 4, 8, 8)
        body.setSpacing(8)
        left = QVBoxLayout()
        card, cbody = _card("API")
        cbody.addWidget(_api_block(True))
        left.addWidget(card)
        card_o, obody = _card("Options")
        obody.addWidget(_options_block())
        left.addWidget(card_o)
        right = QVBoxLayout()
        card_h, hbody = _card("Hotkeys")
        hbody.addWidget(_hotkey_list(True))
        right.addWidget(card_h, 1)
        lw, rw = QWidget(), QWidget()
        lw.setLayout(left)
        rw.setLayout(right)
        body.addWidget(lw, 3)
        body.addWidget(rw, 2)
        bw = QWidget()
        bw.setLayout(body)
        root.addWidget(bw, 1)

    elif meta.layout == PremiumLayout.DECK:
        root.addWidget(_header_compact(False))
        nav_lay, nav_g, _ = _chip_nav(nav_labels, "deckChip")
        nav_wrap = QFrame()
        nav_wrap.setObjectName("deckNav")
        nav_wrap.setLayout(nav_lay)
        root.addWidget(nav_wrap)
        nav_g.idClicked.connect(stack.setCurrentIndex)
        scroll = QScrollArea()
        _prep_scroll(scroll)
        scroll.setWidget(stack)
        root.addWidget(scroll, 1)
        foot = QFrame()
        foot.setObjectName("footBar")
        fh = QHBoxLayout(foot)
        fh.setContentsMargins(10, 6, 10, 8)
        lang = QComboBox()
        lang.addItems(["English", "Tiếng Việt", "한국어"])
        lang.setObjectName("comboMini")
        fh.addWidget(lang)
        fh.addStretch()
        man = QPushButton("Manual")
        man.setObjectName("ghost")
        fh.addWidget(man)
        root.addWidget(foot)

    elif meta.layout == PremiumLayout.RAIL:
        shell = QHBoxLayout()
        shell.setSpacing(0)
        rail = QFrame()
        rail.setObjectName("rail")
        rv = QVBoxLayout(rail)
        rv.setContentsMargins(6, 10, 6, 10)
        rv.setSpacing(4)
        rail_group = QButtonGroup(win)
        for i, sym in enumerate(("⚡", "⌨", "◆")):
            b = QPushButton(sym)
            b.setObjectName("railBtn")
            b.setFixedSize(36, 36)
            b.setCheckable(True)
            if i == 0:
                b.setChecked(True)
            rail_group.addButton(b, i)
            rv.addWidget(b, alignment=Qt.AlignmentFlag.AlignHCenter)
        rail_group.idClicked.connect(stack.setCurrentIndex)
        rv.addStretch()
        shell.addWidget(rail)
        main = QVBoxLayout()
        main.setContentsMargins(8, 8, 8, 8)
        main.addWidget(_header_compact())
        nav_lay, nav_g, _ = _chip_nav(nav_labels)
        main.addLayout(nav_lay)
        nav_g.idClicked.connect(stack.setCurrentIndex)
        scroll = QScrollArea()
        _prep_scroll(scroll)
        scroll.setWidget(stack)
        main.addWidget(scroll, 1)
        mw = QWidget()
        mw.setLayout(main)
        shell.addWidget(mw, 1)
        wrap = QWidget()
        wrap.setLayout(shell)
        root.addWidget(wrap, 1)

    else:  # STRIP default
        root.addWidget(_header_compact())
        nav_lay, nav_g, _ = _chip_nav(nav_labels)
        nav_frame = QFrame()
        nav_frame.setObjectName("navStrip")
        nav_frame.setLayout(nav_lay)
        root.addWidget(nav_frame)
        nav_g.idClicked.connect(stack.setCurrentIndex)
        scroll = QScrollArea()
        _prep_scroll(scroll)
        inner = QWidget()
        inner.setObjectName("pageHost")
        inner.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        inner_l = QVBoxLayout(inner)
        inner_l.setContentsMargins(8, 4, 8, 8)
        inner_l.addWidget(stack)
        scroll.setWidget(inner)
        root.addWidget(scroll, 1)

    win.setStyleSheet(qss)
    return win


def apply_premium_app(app) -> None:
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 9))
