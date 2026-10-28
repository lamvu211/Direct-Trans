"""
Capture and restore text selection in the focused control (standard Edit/RichEdit).
"""

import ctypes
import logging
import time
from ctypes import wintypes

import win32api
import win32con
import win32gui
import win32process

_EM_EDIT_CLASS_PREFIXES = ("Edit", "RichEdit", "RICHEDIT")

_WECHAT_PROCESS_NAMES = frozenset({"wechat.exe", "weixin.exe"})


class GUITHREADINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("hwndActive", wintypes.HWND),
        ("hwndFocus", wintypes.HWND),
        ("hwndCapture", wintypes.HWND),
        ("hwndMenuOwner", wintypes.HWND),
        ("hwndMoveSize", wintypes.HWND),
        ("hwndCaret", wintypes.HWND),
        ("rcCaret", wintypes.RECT),
    ]


def hwnd_process_basename(hwnd: int | None) -> str | None:
    if not hwnd or not win32gui.IsWindow(hwnd):
        return None
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if not pid:
            return None
        handle = win32api.OpenProcess(win32con.PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        try:
            path = win32process.GetModuleFileNameEx(handle, 0)
        finally:
            win32api.CloseHandle(handle)
        return path.rsplit("\\", 1)[-1].lower()
    except Exception:
        return None


def is_wechat_process(name: str | None) -> bool:
    return name in _WECHAT_PROCESS_NAMES if name else False


def is_em_edit_hwnd(hwnd: int | None) -> bool:
    """True only for classic Edit/RichEdit controls that honor EM_GETSEL/EM_SETSEL."""
    if not hwnd or not win32gui.IsWindow(hwnd):
        return False
    if is_wechat_process(hwnd_process_basename(hwnd)):
        return False
    try:
        cls = win32gui.GetClassName(hwnd) or ""
    except Exception:
        return False
    if cls in _EM_EDIT_CLASS_PREFIXES:
        return True
    return any(cls.startswith(prefix) for prefix in _EM_EDIT_CLASS_PREFIXES)


def foreground_process_basename() -> str | None:
    """Lowercase exe name of the foreground window's process (e.g. wechat.exe)."""
    try:
        fg = ctypes.windll.user32.GetForegroundWindow()
        if not fg:
            return None
        _, pid = win32process.GetWindowThreadProcessId(fg)
        if not pid:
            return None
        handle = win32api.OpenProcess(win32con.PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        try:
            path = win32process.GetModuleFileNameEx(handle, 0)
        finally:
            win32api.CloseHandle(handle)
        return path.rsplit("\\", 1)[-1].lower()
    except Exception:
        return None


def is_wechat_foreground() -> bool:
    return is_wechat_process(foreground_process_basename())


def _foreground_focus_hwnd() -> int | None:
    user32 = ctypes.windll.user32
    fg = user32.GetForegroundWindow()
    if not fg:
        return None
    tid = user32.GetWindowThreadProcessId(fg, None)
    gti = GUITHREADINFO()
    gti.cbSize = ctypes.sizeof(GUITHREADINFO)
    if not user32.GetGUIThreadInfo(tid, ctypes.byref(gti)):
        return None
    focus = gti.hwndFocus
    return int(focus) if focus else None


def _parse_em_getsel(result) -> tuple[int, int]:
    if isinstance(result, tuple) and len(result) >= 2:
        return int(result[0]), int(result[1])
    value = int(result)
    return value & 0xFFFF, (value >> 16) & 0xFFFF


def hwnd_log(hwnd: int | None) -> str:
    if not hwnd:
        return "None"
    try:
        return hex(int(hwnd) & 0xFFFFFFFFFFFFFFFF)
    except Exception:
        return str(hwnd)


def capture_focus_hint() -> dict | None:
    """Remember the focused control for paste (WeChat/Zalo), without EM selection."""
    hwnd = _foreground_focus_hwnd()
    if not hwnd or not win32gui.IsWindow(hwnd):
        return None
    return {
        "focus_hwnd": hwnd,
        "em_selection": False,
        "fg_process": foreground_process_basename(),
    }


def capture_selection(focus_hwnd: int | None = None) -> dict | None:
    """Return selection anchors for restore before paste, or None if unsupported."""
    hwnd = focus_hwnd or _foreground_focus_hwnd()
    if not is_em_edit_hwnd(hwnd):
        return None
    try:
        result = win32api.SendMessage(hwnd, win32con.EM_GETSEL, 0, 0)
        start, end = _parse_em_getsel(result)
        if end <= start:
            return None
        return {
            "focus_hwnd": hwnd,
            "sel_start": start,
            "sel_end": end,
            "em_selection": True,
            "fg_process": foreground_process_basename(),
        }
    except Exception as e:
        logging.debug("capture_selection failed: %s", e)
        return None


def restore_selection(state: dict | None) -> bool:
    if not state or not state.get("em_selection"):
        return False
    hwnd = state.get("focus_hwnd")
    if not is_em_edit_hwnd(hwnd):
        return False
    try:
        start = int(state["sel_start"])
        end = int(state["sel_end"])
        if end <= start:
            return False
        win32api.SendMessage(hwnd, win32con.EM_SETSEL, start, end)
        return True
    except Exception as e:
        logging.debug("restore_selection failed: %s", e)
        return False


def prepare_text_selection_for_paste(
    state: dict | None,
    original_text: str | None,
) -> str:
    """
    Re-select source text before paste when EM_SETSEL is supported (classic Edit/RichEdit).
    Modern UI apps (WeChat, Zalo, browsers) retain their active selection naturally.
    Returns method used: em | none.
    """
    if restore_selection(state):
        return "em"

    return "none"


def focus_window_for_paste(
    target_hwnd: int | None,
    preferred_focus: int | None = None,
    fg_process: str | None = None,
) -> int | None:
    if target_hwnd:
        target_hwnd = int(target_hwnd) & 0xFFFFFFFF
    if preferred_focus:
        preferred_focus = int(preferred_focus) & 0xFFFFFFFF
    """
    Best-effort foreground focus before paste; returns focus control hwnd for logging.
    Skips AttachThreadInput for WeChat (crash-prone with CEF).
    """
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    focus = preferred_focus if preferred_focus and win32gui.IsWindow(preferred_focus) else None

    proc = fg_process
    if not proc and target_hwnd:
        proc = hwnd_process_basename(target_hwnd)
    use_attach = not is_wechat_process(proc)

    if target_hwnd and win32gui.IsWindow(target_hwnd):
        try:
            user32.AllowSetForegroundWindow(ctypes.c_uint(-1).value)
        except Exception:
            pass
        try:
            if win32gui.IsIconic(target_hwnd):
                win32gui.ShowWindow(target_hwnd, 9)  # SW_RESTORE
        except Exception:
            pass

        cur_tid = kernel32.GetCurrentThreadId()
        target_tid = user32.GetWindowThreadProcessId(target_hwnd, None)
        attached = False
        try:
            if use_attach and focus and is_em_edit_hwnd(focus):
                if target_tid and target_tid != cur_tid:
                    attached = bool(user32.AttachThreadInput(cur_tid, target_tid, True))
                user32.SetForegroundWindow(target_hwnd)
                user32.SetFocus(focus)
            else:
                user32.SetForegroundWindow(target_hwnd)
        except Exception:
            try:
                user32.SetForegroundWindow(target_hwnd)
            except Exception:
                pass
        finally:
            if attached:
                try:
                    user32.AttachThreadInput(cur_tid, target_tid, False)
                except Exception:
                    pass
        time.sleep(0.12)

    if not focus:
        focus = _foreground_focus_hwnd()
    return focus
