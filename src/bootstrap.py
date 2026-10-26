"""
PyInstaller entry: show Win32 loading bar before importing the rest of the app.
"""

import os
import sys

if not getattr(sys, "frozen", False):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_win32_splash = None
if getattr(sys, "frozen", False):
    from win32_startup_splash import Win32StartupSplash

    _win32_splash = Win32StartupSplash()
    _win32_splash.start()

from main import run_app

if __name__ == "__main__":
    run_app(_win32_splash)
