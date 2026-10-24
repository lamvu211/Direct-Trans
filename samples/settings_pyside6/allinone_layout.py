"""Single-screen Settings — no scroll, theme dropdown, collapsed hotkeys."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

import allinone_themes as _default_theme_registry
from allinone_themes import DEFAULT_THEME_ID
from premium_layout import (
    HOTKEY_ROWS,
    _api_block,
    _card,
    _logo,
    apply_premium_app,
)

HOTKEYS_COLLAPSED_COUNT = 3


@dataclass
class AllInOneMeta:
    """Used only for PNG export metadata."""
    id: int
    title: str
    tagline: str


def _hotkey_rows_widget() -> tuple[QVBoxLayout, QPushButton]:
    """Build collapsible hotkey list: 3 rows + 'Xem thêm' / 'Thu gọn'."""
    rows_host = QVBoxLayout()
    rows_host.setContentsMargins(0, 0, 0, 0)
    rows_host.setSpacing(2)

    more_btn = QPushButton()
    more_btn.setObjectName("showMore")
    more_btn.setFlat(False)
    more_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    expanded = False

    def _make_row(hk: str, lang: str, mode: str) -> QFrame:
        row = QFrame()
        row.setObjectName("hkRow")
        row.setFixedHeight(26)
        h = QHBoxLayout(row)
        h.setContentsMargins(6, 2, 4, 2)
        h.setSpacing(4)
        k = QLabel(hk)
        k.setObjectName("hkKey")
        lg = QLabel(lang)
        lg.setObjectName("hkLang")
        m = QLabel(mode)
        m.setObjectName("hkMode")
        delb = QToolButton()
        delb.setText("✕")
        delb.setObjectName("hkDel")
        delb.setFixedSize(22, 20)
        h.addWidget(k)
        h.addWidget(lg, 1)
        h.addWidget(m)
        h.addWidget(delb)
        return row

    def _clear_layout(layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

    def _render() -> None:
        _clear_layout(rows_host)
        count = len(HOTKEY_ROWS) if expanded else min(HOTKEYS_COLLAPSED_COUNT, len(HOTKEY_ROWS))
        for i in range(count):
            hk, lang, mode = HOTKEY_ROWS[i]
            rows_host.addWidget(_make_row(hk, lang, mode))
        hidden = len(HOTKEY_ROWS) - HOTKEYS_COLLAPSED_COUNT
        if hidden > 0:
            more_btn.setVisible(True)
            more_btn.setText("Thu gọn" if expanded else f"Xem thêm ({hidden})")
        else:
            more_btn.setVisible(False)

    def _toggle() -> None:
        nonlocal expanded
        expanded = not expanded
        _render()

    more_btn.clicked.connect(_toggle)
    _render()
    return rows_host, more_btn


class AllInOneSettingsWindow(QWidget):
    """Production-shaped settings shell (sample). Theme via dropdown."""

    def __init__(
        self,
        initial_theme_id: str = DEFAULT_THEME_ID,
        parent=None,
        theme_registry=None,
    ):
        super().__init__(parent)
        self._registry = theme_registry or _default_theme_registry
        self.setObjectName("root")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        reg_default = getattr(self._registry, "DEFAULT_THEME_ID", DEFAULT_THEME_ID)
        if initial_theme_id not in self._registry.THEME_IDS:
            initial_theme_id = reg_default
        self._current_theme_id = initial_theme_id
        self._on_theme_changed_callbacks: list = []

        self.setWindowTitle("DirectTrans Settings")
        self.setFixedWidth(520)
        self.setFixedHeight(572)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._tagline = QLabel()
        self._tagline.setObjectName("tagline")

        outer.addWidget(self._build_header())
        outer.addWidget(self._build_body(), 1)
        outer.addWidget(self._build_footer())

        self.set_theme(initial_theme_id)

    def _build_header(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("topBar")
        root = QVBoxLayout(bar)
        root.setContentsMargins(10, 8, 10, 6)
        root.setSpacing(4)

        row1 = QHBoxLayout()
        row1.setSpacing(6)
        row1.addWidget(_logo())
        title = QLabel("DirectTrans")
        title.setObjectName("brand")
        sub = QLabel("Settings")
        sub.setObjectName("brandSub")
        titles = QVBoxLayout()
        titles.setSpacing(0)
        titles.addWidget(title)
        titles.addWidget(sub)
        row1.addLayout(titles)
        row1.addStretch()
        upd = QPushButton("Update")
        upd.setObjectName("ghost")
        upd.setFixedHeight(22)
        row1.addWidget(upd)
        root.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(5)
        lang = QComboBox()
        lang.addItems(["English", "Tiếng Việt", "한국어", "中文", "日本語"])
        lang.setObjectName("comboMini")
        lang.setFixedWidth(118)
        row2.addWidget(lang)

        theme_lbl = QLabel("Theme")
        theme_lbl.setObjectName("fieldLabel")
        row2.addWidget(theme_lbl)
        self._theme_combo = QComboBox()
        self._theme_combo.setObjectName("themeCombo")
        for tid in self._registry.THEME_IDS:
            self._theme_combo.addItem(self._registry.label_for(tid), tid)
        self._theme_combo.currentIndexChanged.connect(self._on_theme_combo_changed)
        row2.addWidget(self._theme_combo)

        for label in ("Manual", "Feedback"):
            b = QPushButton(label)
            b.setObjectName("ghost")
            b.setFixedHeight(22)
            row2.addWidget(b)
        row2.addStretch()
        root.addLayout(row2)
        return bar

    def _build_body(self) -> QWidget:
        host = QWidget()
        host.setObjectName("pageHost")
        host.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        lay = QVBoxLayout(host)
        lay.setContentsMargins(8, 4, 8, 4)
        lay.setSpacing(5)

        lay.addWidget(self._provider_card())
        lay.addWidget(self._api_card())
        lay.addWidget(self._options_card())
        lay.addWidget(self._hotkeys_card())
        return host

    def _provider_card(self) -> QFrame:
        card, body = _card("Translation source")
        row = QHBoxLayout()
        row.addWidget(QLabel("Provider"))
        combo = QComboBox()
        combo.addItems(["Gemini", "Groq", "Mistral", "Google Free"])
        combo.setObjectName("combo")
        row.addWidget(combo, 1)
        body.addLayout(row)
        return card

    def _api_card(self) -> QFrame:
        card, body = _card("API keys")
        body.addWidget(_api_block(compact=True, show_provider_row=False))
        return card

    def _options_card(self) -> QFrame:
        card, body = _card("Options")
        cb = QCheckBox("Start with Windows")
        cb.setObjectName("optionCheck")
        cb.setChecked(True)
        body.addWidget(cb)
        return card

    def _hotkeys_card(self) -> QFrame:
        card, body = _card("Hotkeys")
        rows, more = _hotkey_rows_widget()
        body.addLayout(rows)
        body.addWidget(more, alignment=Qt.AlignmentFlag.AlignLeft)
        add = QPushButton("+ Hotkey")
        add.setObjectName("ctaSmall")
        add.setFixedHeight(24)
        body.addWidget(add, alignment=Qt.AlignmentFlag.AlignLeft)
        return card

    def _build_footer(self) -> QFrame:
        foot = QFrame()
        foot.setObjectName("footBar")
        fh = QHBoxLayout(foot)
        fh.setContentsMargins(10, 4, 10, 6)
        fh.addWidget(self._tagline, 1)
        save = QPushButton("Save all")
        save.setObjectName("cta")
        save.setFixedHeight(26)
        fh.addWidget(save)
        return foot

    def _on_theme_combo_changed(self, index: int) -> None:
        tid = self._theme_combo.itemData(index)
        if tid and tid != self._current_theme_id:
            self.set_theme(tid)

    def set_theme(self, theme_id: str) -> None:
        reg_default = getattr(self._registry, "DEFAULT_THEME_ID", DEFAULT_THEME_ID)
        if theme_id not in self._registry.THEME_IDS:
            theme_id = reg_default
        self._current_theme_id = theme_id
        self.setStyleSheet(self._registry.qss_for(theme_id))
        self._tagline.setText(self._registry.tagline_for(theme_id))
        idx = self._theme_combo.findData(theme_id)
        if idx >= 0 and self._theme_combo.currentIndex() != idx:
            self._theme_combo.blockSignals(True)
            self._theme_combo.setCurrentIndex(idx)
            self._theme_combo.blockSignals(False)
        for cb in self._on_theme_changed_callbacks:
            cb(theme_id)

    def current_theme_id(self) -> str:
        return self._current_theme_id

    def on_theme_changed(self, callback) -> None:
        self._on_theme_changed_callbacks.append(callback)


def build_allinone_window(
    meta: AllInOneMeta | None = None,
    qss: str | None = None,
    initial_theme_id: str = DEFAULT_THEME_ID,
    theme_registry=None,
) -> AllInOneSettingsWindow:
    """Build window. Legacy `meta,qss` applies theme by id from meta.id if provided."""
    if meta is not None:
        theme_map = {1: "midnight_gold", 2: "aurora_glass", 3: "rose_champagne", 4: "nord_snow"}
        initial_theme_id = theme_map.get(meta.id, DEFAULT_THEME_ID)
    win = AllInOneSettingsWindow(
        initial_theme_id=initial_theme_id,
        theme_registry=theme_registry,
    )
    if qss is not None:
        win.setStyleSheet(qss)
    return win


__all__ = [
    "AllInOneMeta",
    "AllInOneSettingsWindow",
    "build_allinone_window",
    "apply_premium_app",
    "HOTKEYS_COLLAPSED_COUNT",
]
