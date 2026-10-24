"""
Shared DirectTrans Settings layout built with real PySide6 widgets + QSS.
Not a mockup — this is the same stack planned for migration.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
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


class LayoutStyle(Enum):
    CLASSIC = "classic"
    SIDEBAR = "sidebar"
    COMPACT_HEADER = "compact_header"


@dataclass
class SampleMeta:
    id: int
    title: str
    subtitle: str
    layout: LayoutStyle


def _load_logo_label() -> QLabel:
    lbl = QLabel()
    if LOGO_PATH.exists():
        px = QPixmap(str(LOGO_PATH)).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        lbl.setPixmap(px)
    else:
        lbl.setText("DT")
    return lbl


def _make_header_tool_row() -> QHBoxLayout:
    row = QHBoxLayout()
    row.setSpacing(8)
    lang = QComboBox()
    lang.addItems(["English", "Tiếng Việt", "한국어", "中文", "日本語"])
    lang.setCurrentText("English")
    lang.setFixedWidth(140)
    row.addWidget(lang)
    for text in ("User manual", "Update", "Feedback"):
        btn = QPushButton(text)
        btn.setObjectName("headerAction")
        row.addWidget(btn)
    row.addStretch()
    return row


def _provider_group() -> QGroupBox:
    box = QGroupBox("Translation Source")
    lay = QHBoxLayout(box)
    lay.addWidget(QLabel("Provider:"))
    lay.addStretch()
    combo = QComboBox()
    combo.addItems(["Gemini", "Groq", "Mistral", "Google Free"])
    combo.setFixedWidth(160)
    lay.addWidget(combo)
    return box


def _api_keys_group(compact_actions: bool = False) -> QGroupBox:
    box = QGroupBox("API Keys")
    grid = QGridLayout(box)
    grid.setHorizontalSpacing(10)
    grid.setVerticalSpacing(8)

    grid.addWidget(QLabel("API key:"), 0, 0, Qt.AlignmentFlag.AlignTop)
    key_row = QHBoxLayout()
    key_edit = QLineEdit()
    key_edit.setEchoMode(QLineEdit.EchoMode.Password)
    key_edit.setPlaceholderText("••••••••••••")
    key_edit.setText("sk-sample-key-hidden")
    clear_btn = QToolButton()
    clear_btn.setText("✕")
    clear_btn.setObjectName("clearKey")
    key_row.addWidget(key_edit, 1)
    key_row.addWidget(clear_btn)
    grid.addLayout(key_row, 0, 1)

    link = QPushButton("Get API key")
    link.setObjectName("linkButton")
    link.setFlat(True)
    grid.addWidget(link, 1, 1, Qt.AlignmentFlag.AlignLeft)

    grid.addWidget(QLabel("Model:"), 2, 0)
    model = QComboBox()
    model.addItem("gemini-flash-lite-latest")
    model.setFixedWidth(280)
    grid.addWidget(model, 2, 1, Qt.AlignmentFlag.AlignLeft)

    load_btn = QPushButton("↻ Load Models")
    load_btn.setObjectName("secondary")
    test_btn = QPushButton("Test")
    test_btn.setObjectName("secondary")
    save_btn = QPushButton("Save Key")
    save_btn.setObjectName("primary")

    if compact_actions:
        action_bar = QHBoxLayout()
        action_bar.addWidget(load_btn)
        action_bar.addWidget(test_btn)
        action_bar.addStretch()
        action_bar.addWidget(save_btn)
        grid.addLayout(action_bar, 3, 0, 1, 2)
    else:
        btn_row = QHBoxLayout()
        btn_row.addWidget(load_btn)
        btn_row.addWidget(test_btn)
        btn_row.addStretch()
        grid.addLayout(btn_row, 3, 1, Qt.AlignmentFlag.AlignLeft)
        save_lay = QHBoxLayout()
        save_lay.addStretch()
        save_lay.addWidget(save_btn)
        grid.addLayout(save_lay, 4, 0, 1, 2)

    return box


def _options_group() -> QGroupBox:
    box = QGroupBox("Options")
    lay = QVBoxLayout(box)
    cb = QCheckBox("Start with Windows")
    cb.setObjectName("autostart")
    cb.setChecked(True)
    lay.addWidget(cb)
    return box


def _hotkeys_group() -> QGroupBox:
    box = QGroupBox("Hotkeys")
    lay = QVBoxLayout(box)
    table = QTableWidget(len(HOTKEY_ROWS), 4)
    table.setHorizontalHeaderLabels(["Hotkey", "Language", "Mode", ""])
    table.horizontalHeader().setStretchLastSection(True)
    table.verticalHeader().setVisible(False)
    table.setShowGrid(False)
    table.setAlternatingRowColors(True)
    table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setFixedHeight(28 + len(HOTKEY_ROWS) * 30)

    for r, (hk, lang, mode) in enumerate(HOTKEY_ROWS):
        table.setItem(r, 0, QTableWidgetItem(hk))
        table.setItem(r, 1, QTableWidgetItem(lang))
        mode_item = QTableWidgetItem(f"  {mode}")
        table.setItem(r, 2, mode_item)
        del_btn = QPushButton("✕")
        del_btn.setObjectName("dangerIcon")
        del_btn.setFixedSize(28, 24)
        table.setCellWidget(r, 3, del_btn)

    table.setColumnWidth(0, 130)
    table.setColumnWidth(1, 140)
    table.setColumnWidth(2, 80)
    lay.addWidget(table)

    add_btn = QPushButton("+ Add Hotkey")
    add_btn.setObjectName("primary")
    add_btn.setFixedWidth(140)
    lay.addWidget(add_btn, alignment=Qt.AlignmentFlag.AlignLeft)
    return box


def _classic_body(compact_api: bool = False) -> QWidget:
    w = QWidget()
    lay = QVBoxLayout(w)
    lay.setContentsMargins(12, 8, 12, 12)
    lay.setSpacing(10)
    for g in (
        _provider_group(),
        _api_keys_group(compact_actions=compact_api),
        _options_group(),
        _hotkeys_group(),
    ):
        lay.addWidget(g)
    lay.addStretch()
    return w


def build_settings_window(meta: SampleMeta, qss: str) -> QWidget:
    """Top-level QWidget mimicking SettingsWindow (QMainWindow-style content)."""
    win = QWidget()
    win.setWindowTitle(f"Sample {meta.id}: {meta.title} — DirectTrans Settings v2.0.0")
    win.setMinimumSize(640, 560)
    win.resize(680, 620)

    root = QVBoxLayout(win)
    root.setContentsMargins(0, 0, 0, 0)
    root.setSpacing(0)

    header = QFrame()
    header.setObjectName("header")
    header_lay = QVBoxLayout(header)
    header_lay.setContentsMargins(12, 10, 12, 10)
    top = QHBoxLayout()
    top.addWidget(_load_logo_label())
    title = QLabel("DirectTrans")
    title.setObjectName("appTitle")
    top.addWidget(title)
    top.addStretch()
    header_lay.addLayout(top)
    header_lay.addLayout(_make_header_tool_row())
    root.addWidget(header)

    if meta.layout == LayoutStyle.SIDEBAR:
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        nav = QListWidget()
        nav.setObjectName("sideNav")
        nav.setFixedWidth(148)
        for label in ("Translation", "API Keys", "Options", "Hotkeys"):
            nav.addItem(QListWidgetItem(label))
        nav.setCurrentRow(0)
        stack = QStackedWidget()
        stack.addWidget(_wrap_scroll(_provider_group()))
        stack.addWidget(_wrap_scroll(_api_keys_group()))
        stack.addWidget(_wrap_scroll(_options_group()))
        stack.addWidget(_wrap_scroll(_hotkeys_group()))
        nav.currentRowChanged.connect(stack.setCurrentIndex)
        body.addWidget(nav)
        body.addWidget(stack, 1)
        body_w = QWidget()
        body_w.setLayout(body)
        root.addWidget(body_w, 1)
    elif meta.layout == LayoutStyle.COMPACT_HEADER:
        toolbar = QFrame()
        toolbar.setObjectName("subToolbar")
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(12, 6, 12, 6)
        for t in ("Translation Source", "API Keys", "Options", "Hotkeys"):
            b = QPushButton(t)
            b.setObjectName("segment")
            b.setCheckable(True)
            if t == "Translation Source":
                b.setChecked(True)
            tb.addWidget(b)
        tb.addStretch()
        root.addWidget(toolbar)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(_classic_body(compact_api=True))
        root.addWidget(scroll, 1)
    else:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(_classic_body(compact_api=False))
        root.addWidget(scroll, 1)

    win.setStyleSheet(qss)
    return win


def _wrap_scroll(inner: QWidget) -> QWidget:
    w = QWidget()
    lay = QVBoxLayout(w)
    lay.setContentsMargins(12, 12, 12, 12)
    lay.addWidget(inner)
    lay.addStretch()
    return w


def apply_fusion_app_style(app: QApplication) -> None:
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 9))
