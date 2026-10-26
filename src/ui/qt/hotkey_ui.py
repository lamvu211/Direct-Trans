"""Shared helpers for hotkey settings UI."""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QToolButton, QWidget

if TYPE_CHECKING:
    from hotkey_manager import HotkeyManager


def prepare_hotkey_row_frame(row: QFrame) -> None:
    row.setAttribute(Qt.WidgetAttribute.WA_Hover, True)


def pass_mouse_to_row(labels: list[QLabel]) -> None:
    for lbl in labels:
        lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)


class HotkeyRowClickToEdit(QFrame):
    """Hotkey list row: single-click opens edit (delete button excluded)."""

    def __init__(
        self,
        hk: dict,
        on_edit: Callable[[dict], None],
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._hk = hk
        self._on_edit = on_edit
        prepare_hotkey_row_frame(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            child = self.childAt(event.position().toPoint())
            if isinstance(child, QToolButton) and child.objectName() == "hkDel":
                super().mousePressEvent(event)
                return
            self._on_edit(self._hk)
        super().mousePressEvent(event)


@contextmanager
def pause_translation_hotkeys(hotkey_manager: "HotkeyManager | None"):
    """Unregister global hotkeys while capturing combos in a dialog."""
    if hotkey_manager:
        hotkey_manager.unregister_all()
    try:
        yield
    finally:
        if hotkey_manager:
            hotkey_manager.register_all()
