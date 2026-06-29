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

def parse_hotkey(combo_str):
    """
    Parses a hotkey string like 'ctrl+shift+v' into (modifiers, vk_code).
    """
    parts = [p.strip().lower() for p in combo_str.split('+')]
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
            # Try to get VK code from user32.VkKeyScanW
            # VkKeyScanW returns the virtual-key code in the low-order byte
            res = user32.VkKeyScanW(ord(part))
            if res != -1:
                vk = res & 0xFF
            else:
                # Fallback for some keys if needed, but VkKeyScanW usually handles a-z, 0-9
                vk = ord(part.upper())
    return modifiers, vk


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
                    # Invoke callback in a new thread so we don't block the message loop
                    threading.Thread(target=self.on_hotkey_triggered, args=(hk_config,), daemon=True).start()
            
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
