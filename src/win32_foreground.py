"""Best-effort Win32 foreground for our own top-level Qt windows."""

from __future__ import annotations

import ctypes
import sys

SW_RESTORE = 9


def bring_hwnd_to_foreground(hwnd: int) -> None:
    if sys.platform != "win32" or not hwnd:
        return
    user32 = ctypes.windll.user32
    try:
        user32.AllowSetForegroundWindow(ctypes.c_uint(-1).value)
    except Exception:
        pass
    try:
        if user32.IsIconic(hwnd):
            user32.ShowWindow(hwnd, SW_RESTORE)
    except Exception:
        pass
    try:
        user32.SetForegroundWindow(hwnd)
    except Exception:
        pass
    try:
        user32.BringWindowToTop(hwnd)
    except Exception:
        pass


def bring_qt_widget_to_foreground(widget) -> None:
    if widget is None:
        return
    try:
        hwnd = int(widget.winId())
    except Exception:
        return
    bring_hwnd_to_foreground(hwnd)