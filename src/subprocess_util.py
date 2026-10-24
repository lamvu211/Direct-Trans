"""Run subprocesses without flashing a console window on Windows."""

import subprocess
import sys


def run_hidden(*args, **kwargs):
    if sys.platform == 'win32':
        flags = kwargs.get('creationflags', 0)
        kwargs['creationflags'] = flags | subprocess.CREATE_NO_WINDOW
    return subprocess.run(*args, **kwargs)
