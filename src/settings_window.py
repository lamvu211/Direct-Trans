"""
settings_window.py - Facade for Settings UI (PySide6 all-in-one).
"""

from __future__ import annotations

import sys

from ui.qt.settings_window import QtSettingsWindow, ensure_qt_app


class SettingsWindow:
    """API-compatible wrapper used by main.py (formerly Tk Toplevel)."""

    def __init__(
        self,
        root,
        config,
        on_save_callback,
        on_close_callback=None,
        hotkey_manager=None,
        on_before_api_test=None,
    ):
        self.root = root  # kept for popup / legacy references
        self.config = config
        self.on_save_callback = on_save_callback
        self.on_close_callback = on_close_callback
        self.hotkey_manager = hotkey_manager
        self.on_before_api_test = on_before_api_test
        self.window = None
        self._qt: QtSettingsWindow | None = None

    def is_open(self) -> bool:
        """True while the settings UI exists (including hidden-to-tray, not yet closed)."""
        return self._qt is not None

    def restore_and_focus(self):
        if self._qt:
            self._qt.restore_and_focus()

    def set_theme(self, theme_id: str) -> None:
        """Apply theme to the live Settings window (combo + QSS)."""
        if self._qt is not None:
            self._qt.set_theme(theme_id)

    def sync_provider(self, provider_key: str) -> None:
        if self._qt is not None:
            self._qt.sync_provider_from_config(provider_key)

    def show(self):
        ensure_qt_app()
        if self._qt is None:
            self._qt = QtSettingsWindow(
                self.config,
                self.on_save_callback,
                self._handle_close,
                self.hotkey_manager,
                on_before_api_test=self.on_before_api_test,
            )
            self.window = self._qt
            if getattr(sys, "frozen", False):
                self._qt._deferred_win32_focus = True
        self._qt.restore_and_focus()

    def _handle_close(self):
        self._qt = None
        self.window = None
        if self.on_close_callback:
            self.on_close_callback()
