"""Shared Qt widgets for settings layout."""

from __future__ import annotations

import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

# Label column width in API / hotkey grids (aligns with "Model:" / "API key:").
SETTINGS_FIELD_LABEL_WIDTH = 52
SETTINGS_FIELD_H_SPACING = 8
SETTINGS_FIELD_INDENT = SETTINGS_FIELD_LABEL_WIDTH + SETTINGS_FIELD_H_SPACING


def _assets_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "assets")
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets")


LOGO_PATH = os.path.join(_assets_dir(), "logo-direct-trans.png")


# Standard control height for settings (combos, line edits, buttons).
CONTROL_HEIGHT = 24


def apply_control_height(widget, height: int = CONTROL_HEIGHT) -> None:
    if hasattr(widget, "setFixedHeight"):
        widget.setFixedHeight(height)


def fit_combo_to_contents(combo: QComboBox, padding: int = 22) -> None:
    """Fixed width from longest item text (no extra empty space)."""
    combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
    combo.setMinimumContentsLength(0)
    fm = combo.fontMetrics()
    max_w = 0
    for i in range(combo.count()):
        max_w = max(max_w, fm.horizontalAdvance(combo.itemText(i)))
    combo.setFixedWidth(max(max_w + padding, 48))


def apply_premium_app(app) -> None:
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 9))


def logo_label() -> QLabel:
    lb = QLabel()
    lb.setObjectName("logo")
    if os.path.exists(LOGO_PATH):
        px = QPixmap(LOGO_PATH).scaled(
            20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        lb.setPixmap(px)
    return lb


def card(
    title: str = "",
    icon: str = "",
    header_right: QWidget | None = None,
) -> tuple[QFrame, QVBoxLayout]:
    from PySide6.QtWidgets import QSizePolicy
    frame = QFrame()
    frame.setObjectName("card")
    frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
    outer = QVBoxLayout(frame)
    outer.setContentsMargins(12, 8, 12, 12)
    outer.setSpacing(4)
    if title or icon or header_right:
        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(6)
        if icon:
            icon_lbl = QLabel(icon)
            icon_lbl.setObjectName("cardIcon")
            icon_lbl.setStyleSheet("font-size: 9.5pt; background: transparent; border: none;")
            header_row.addWidget(icon_lbl, 0, Qt.AlignmentFlag.AlignVCenter)
        if title:
            t = QLabel(title)
            t.setObjectName("cardTitle")
            header_row.addWidget(t, 0, Qt.AlignmentFlag.AlignVCenter)
        header_row.addStretch(1)
        if header_right is not None:
            header_row.addWidget(header_right, 0, Qt.AlignmentFlag.AlignVCenter)
        outer.addLayout(header_row)
    body = QVBoxLayout()
    body.setSpacing(4)
    outer.addLayout(body)
    return frame, body
