"""Shared helpers for hotkey settings UI."""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hotkey_manager import HotkeyManager


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
