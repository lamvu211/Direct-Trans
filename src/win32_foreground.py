"""Best-effort Win32 foreground for our own top-level Qt windows."""

from __future__ import annotations

import ctypes
import sys

SW_RESTORE = 9


def bring_hwnd_to_foreground(hwnd: int) -> None:
    if sys.platform != "win32" or not hwnd:
        return
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    try:
        user32.AllowSetForegroundWindow(ctypes.c_uint(-1).value)
    except Exception:
        pass
    try:
        if user32.IsIconic(hwnd):
            user32.ShowWindow(hwnd, SW_RESTORE)
    except Exception:
        pass

    fg = user32.GetForegroundWindow()
    if fg and int(fg) == int(hwnd):
        return

    fg_thread = 0
    if fg:
        try:
            fg_thread = user32.GetWindowThreadProcessId(fg, None)
        except Exception:
            fg_thread = 0
    cur_thread = kernel32.GetCurrentThreadId()
    attached = False
    if fg_thread and fg_thread != cur_thread:
        try:
            attached = bool(user32.AttachThreadInput(cur_thread, fg_thread, True))
        except Exception:
            attached = False
    try:
        user32.SetForegroundWindow(hwnd)
    except Exception:
        pass
    try:
        user32.BringWindowToTop(hwnd)
    except Exception:
        pass
    finally:
        if attached:
            try:
                user32.AttachThreadInput(cur_thread, fg_thread, False)
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