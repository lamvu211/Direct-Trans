"""Low-level keyboard simulation (SendInput + keybd_event fallback)."""

from __future__ import annotations

import ctypes
import time
from ctypes import wintypes

import win32api
import win32con

user32 = ctypes.windll.user32

INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_EXTENDEDKEY = 0x0001

ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class INPUT(ctypes.Structure):
    class _INPUT_UNION(ctypes.Union):
        _fields_ = [
            ("mi", MOUSEINPUT),
            ("ki", KEYBDINPUT),
            ("hi", HARDWAREINPUT),
        ]

    _anonymous_ = ("u",)
    _fields_ = [
        ("type", wintypes.DWORD),
        ("u", _INPUT_UNION),
    ]


_MODIFIER_VKS = (
    (0xA0, 0),
    (0xA1, 0),
    (0xA2, 0),
    (0xA3, KEYEVENTF_EXTENDEDKEY),
    (0xA4, 0),
    (0xA5, KEYEVENTF_EXTENDEDKEY),
    (0x5B, KEYEVENTF_EXTENDEDKEY),
    (0x5C, KEYEVENTF_EXTENDEDKEY),
    (0x10, 0),
    (0x11, 0),
    (0x12, 0),
)


def _send_input_vk(vk: int, flags: int = 0) -> None:
    scan = win32api.MapVirtualKey(vk, 0) & 0xFF
    extra = ULONG_PTR(0)
    inp = INPUT(
        type=INPUT_KEYBOARD,
        ki=KEYBDINPUT(wVk=vk, wScan=scan, dwFlags=flags, time=0, dwExtraInfo=extra),
    )
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))


def release_modifier_keys() -> None:
    """Release common modifier keys (after global hotkeys)."""
    for vk, flags in _MODIFIER_VKS:
        try:
            sc = win32api.MapVirtualKey(vk, 0)
            win32api.keybd_event(vk, sc, win32con.KEYEVENTF_KEYUP | flags, 0)
        except Exception:
            pass


def send_ctrl_chord_keybd(letter_vk: int) -> None:
    """Ctrl+letter via keybd_event (historically reliable for Zalo / Win32 editors)."""
    vk_control = 0x11
    sc_letter = win32api.MapVirtualKey(letter_vk, 0)
    sc_control = win32api.MapVirtualKey(vk_control, 0)
    win32api.keybd_event(vk_control, sc_control, 0, 0)
    win32api.keybd_event(letter_vk, sc_letter, 0, 0)
    win32api.keybd_event(letter_vk, sc_letter, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(vk_control, sc_control, win32con.KEYEVENTF_KEYUP, 0)


def send_ctrl_chord_sendinput(letter_vk: int) -> None:
    vk_control = 0x11
    sc_letter = win32api.MapVirtualKey(letter_vk, 0) & 0xFF
    sc_control = win32api.MapVirtualKey(vk_control, 0) & 0xFF
    extra = ULONG_PTR(0)

    def key(vk: int, scan: int, flags: int) -> INPUT:
        return INPUT(
            type=INPUT_KEYBOARD,
            ki=KEYBDINPUT(wVk=vk, wScan=scan, dwFlags=flags, time=0, dwExtraInfo=extra),
        )

    sequence = (
        key(vk_control, sc_control, 0),
        key(letter_vk, sc_letter, 0),
        key(letter_vk, sc_letter, KEYEVENTF_KEYUP),
        key(vk_control, sc_control, KEYEVENTF_KEYUP),
    )
    arr = (INPUT * len(sequence))(*sequence)
    user32.SendInput(len(sequence), arr, ctypes.sizeof(INPUT))
    time.sleep(0.02)


def send_ctrl_c_keybd() -> None:
    send_ctrl_chord_keybd(0x43)


def send_ctrl_v_keybd() -> None:
    send_ctrl_chord_keybd(0x56)


def send_ctrl_c_sendinput() -> None:
    send_ctrl_chord_sendinput(0x43)


def send_ctrl_v_sendinput() -> None:
    send_ctrl_chord_sendinput(0x56)


def select_backward_characters(count: int, *, max_count: int = 5000) -> None:
    """Select `count` characters left of the caret (WeChat / CEF after copy cleared highlight)."""
    n = min(max(0, count), max_count)
    if n == 0:
        return
    vk_shift = 0x10
    vk_left = 0x25
    sc_shift = win32api.MapVirtualKey(vk_shift, 0)
    sc_left = win32api.MapVirtualKey(vk_left, 0)
    win32api.keybd_event(vk_shift, sc_shift, 0, 0)
    try:
        for _ in range(n):
            win32api.keybd_event(vk_left, sc_left, 0, 0)
            win32api.keybd_event(vk_left, sc_left, win32con.KEYEVENTF_KEYUP, 0)
    finally:
        win32api.keybd_event(vk_shift, sc_shift, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.04)


def select_forward_characters(count: int, *, max_count: int = 5000) -> None:
    """Select `count` characters right of the caret (WeChat / CEF where caret resets to start of selection)."""
    n = min(max(0, count), max_count)
    if n == 0:
        return
    vk_shift = 0x10
    vk_right = 0x27
    sc_shift = win32api.MapVirtualKey(vk_shift, 0)
    sc_right = win32api.MapVirtualKey(vk_right, 0)
    win32api.keybd_event(vk_shift, sc_shift, 0, 0)
    try:
        for _ in range(n):
            win32api.keybd_event(vk_right, sc_right, 0, 0)
            win32api.keybd_event(vk_right, sc_right, win32con.KEYEVENTF_KEYUP, 0)
    finally:
        win32api.keybd_event(vk_shift, sc_shift, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.04)
