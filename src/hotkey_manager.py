"""
hotkey_manager.py - Global hotkey registration/management using Windows RegisterHotKey via ctypes.
"""

import threading
import logging
import ctypes
from ctypes import wintypes
import time

user32 = ctypes.windll.user32

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008

WM_HOTKEY = 0x0312
WM_QUIT = 0x0012
WM_USER = 0x0400
UPDATE_HOTKEYS_MSG = WM_USER + 1

# Virtual-key codes for keys VkKeyScan does not accept as a one-char string.
_VK_BY_NAME = {f"f{i}": 0x70 + (i - 1) for i in range(1, 13)}

_DISALLOWED_MAIN_KEYS = frozenset(
    {
        "space",
        "enter",
        "return",
        "tab",
        "escape",
        "esc",
        "backspace",
        "delete",
        "insert",
        "home",
        "end",
        "pageup",
        "pagedown",
        "up",
        "down",
        "left",
        "right",
        "printscreen",
        "pause",
        "capslock",
        "numlock",
        "scrolllock",
    }
    | {f"f{i}" for i in range(1, 13)}
)


def parse_hotkey(combo_str):
    """
    Parses a hotkey string like 'ctrl+shift+v' into (modifiers, vk_code).
    """
    if not combo_str or not isinstance(combo_str, str):
        return 0, 0
        
    parts = [p.strip().lower() for p in combo_str.split('+') if p.strip()]
    modifiers = 0
    vk = 0
    for part in parts:
        if part in ('ctrl', 'control'):
            modifiers |= MOD_CONTROL
        elif part in ('shift',):
            modifiers |= MOD_SHIFT
        elif part in ('alt',):
            modifiers |= MOD_ALT
        elif part in ('win', 'windows'):
            modifiers |= MOD_WIN
        else:
            if part in _VK_BY_NAME:
                vk = _VK_BY_NAME[part]
                continue
            if len(part) == 1:
                res = user32.VkKeyScanW(ord(part))
                if res != -1:
                    vk = res & 0xFF
                else:
                    vk = ord(part.upper())
            else:
                logging.warning("Unknown hotkey segment: %s", part)
    return modifiers, vk


def _main_key_part(combo_str: str) -> str | None:
    if not combo_str:
        return None
    parts = [p.strip().lower() for p in combo_str.split("+") if p.strip()]
    for part in parts:
        if part not in ("ctrl", "control", "shift", "alt", "win", "windows"):
            return part
    return None


def validate_hotkey_combo(combo_str: str) -> tuple[bool, str]:
    """
    Validate a combo string for RegisterHotKey.
    Returns (ok, error_code) where error_code is one of:
    empty, no_main_key, no_modifier, disallowed_key, unregistered_key.
    """
    if not combo_str or not str(combo_str).strip():
        return False, "empty"
    modifiers, vk = parse_hotkey(combo_str)
    main = _main_key_part(combo_str)
    if not main:
        return False, "no_main_key"
    if main in _DISALLOWED_MAIN_KEYS:
        return False, "disallowed_key"
    if modifiers == 0:
        return False, "no_modifier"
    if vk == 0:
        return False, "unregistered_key"
    return True, ""


class HotkeyManager:
    def __init__(self, config, on_hotkey_triggered):
        """
        config: Config instance
        on_hotkey_triggered: callback(hotkey_config_dict)
            Called when user presses a registered hotkey, receives the hotkey config dict:
            {id, key_combo, target_language_code, target_language_name, mode}
        """
        self.config = config
        self.on_hotkey_triggered = on_hotkey_triggered
        self._thread = None
        self._thread_id = None
        
        # Start the hotkey message loop thread
        self._start_thread()

    def _start_thread(self):
        started_event = threading.Event()
        self._thread = threading.Thread(target=self._message_loop, args=(started_event,), daemon=True)
        self._thread.start()
        started_event.wait()

    def _message_loop(self, started_event):
        self._thread_id = ctypes.windll.kernel32.GetCurrentThreadId()
        
        # Force the OS to create a message queue for this thread
        msg = wintypes.MSG()
        user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 0)
        
        started_event.set()
        
        registered_hotkeys = {}  # hk_id -> hotkey_config_dict
        
        # Register initial
        self._do_register_all(registered_hotkeys)

        while True:
            bRet = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if bRet == 0 or bRet == -1:
                break
            
            if msg.message == WM_HOTKEY:
                hk_id = msg.wParam
                if hk_id in registered_hotkeys:
                    hk_config = registered_hotkeys[hk_id]
                    # Callback spawns its own worker; keep message loop responsive.
                    try:
                        self.on_hotkey_triggered(hk_config)
                    except Exception as e:
                        logging.error("Hotkey callback failed: %s", e)
            
            elif msg.message == UPDATE_HOTKEYS_MSG:
                # wparam 1 means register_all, wparam 0 means unregister_all
                if msg.wParam == 1:
                    self._do_register_all(registered_hotkeys)
                else:
                    self._do_unregister_all(registered_hotkeys)
            
            elif msg.message == WM_QUIT:
                self._do_unregister_all(registered_hotkeys)
                break
            
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

    def _do_register_all(self, registered_hotkeys):
        self._do_unregister_all(registered_hotkeys)
        hotkeys = self.config.get_hotkeys()
        for idx, hk in enumerate(hotkeys, start=1):
            modifiers, vk = parse_hotkey(hk['key_combo'])
            if vk == 0:
                logging.error(f"Could not parse hotkey {hk['key_combo']}")
                continue
            
            # RegisterHotKey(hWnd, id, fsModifiers, vk)
            # MOD_NOREPEAT (0x4000) is useful to prevent spam holding
            if user32.RegisterHotKey(None, idx, modifiers | 0x4000, vk):
                registered_hotkeys[idx] = hk
                logging.info(f"Registered hotkey via ctypes: {hk['key_combo']} -> {hk['target_language_code']} ({hk['mode']})")
            else:
                logging.error(f"Failed to register hotkey {hk['key_combo']} via ctypes. Code: {ctypes.GetLastError()}")

    def _do_unregister_all(self, registered_hotkeys):
        for hk_id in list(registered_hotkeys.keys()):
            user32.UnregisterHotKey(None, hk_id)
        registered_hotkeys.clear()
        logging.info("Unregistered all hotkeys.")

    def register_all(self):
        """Signal thread to register hotkeys."""
        if self._thread_id:
            user32.PostThreadMessageW(self._thread_id, UPDATE_HOTKEYS_MSG, 1, 0)

    def unregister_all(self):
        """Signal thread to unregister hotkeys."""
        if self._thread_id:
            user32.PostThreadMessageW(self._thread_id, UPDATE_HOTKEYS_MSG, 0, 0)

    def reload(self):
        """Reload hotkeys (call after settings change)."""
        self.register_all()
        
    def stop(self):
        """Clean shutdown of the hotkey thread."""
        if self._thread_id:
            user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)
            if self._thread:
                self._thread.join(timeout=1.0)
