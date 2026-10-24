"""Windows DPI helpers for Qt."""

import ctypes


def enable_process_dpi_awareness() -> None:
    """Prefer per-monitor DPI awareness so geometry and fonts scale consistently."""
    try:
        # PROCESS_PER_MONITOR_DPI_AWARE = 2
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        return
    except Exception:
        pass
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


def qt_scale_factor() -> float:
    """Logical DPI scale relative to 96 DPI (1.0 at 100% Windows scaling)."""
    try:
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        if app is None:
            return 1.0
        screen = app.primaryScreen()
        if screen is None:
            return 1.0
        return max(1.0, screen.logicalDotsPerInch() / 96.0)
    except Exception:
        return 1.0


def scaled_size(base_w: int, base_h: int) -> tuple[int, int]:
    factor = qt_scale_factor()
    return int(base_w * factor), int(base_h * factor)
