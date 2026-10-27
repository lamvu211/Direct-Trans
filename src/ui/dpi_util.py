"""Windows DPI helpers for Qt and native Win32 UI."""

import ctypes


_dpi_awareness_set = False


def enable_process_dpi_awareness() -> None:
    """Prefer per-monitor DPI awareness so geometry and fonts scale consistently."""
    global _dpi_awareness_set
    if _dpi_awareness_set:
        return
    try:
        # PROCESS_PER_MONITOR_DPI_AWARE = 2
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        _dpi_awareness_set = True
        return
    except Exception:
        pass
    try:
        ctypes.windll.user32.SetProcessDPIAware()
        _dpi_awareness_set = True
    except Exception:
        pass


def win32_system_dpi() -> int:
    """Primary display DPI (96 at 100% Windows scaling). Works without Qt."""
    try:
        return max(96, int(ctypes.windll.user32.GetDpiForSystem()))
    except Exception:
        return 96


def win32_scale_factor(dpi: int | None = None) -> float:
    dpi = dpi if dpi is not None else win32_system_dpi()
    return max(1.0, dpi / 96.0)


def scale_logical_px(logical: int, dpi: int | None = None) -> int:
    """Convert 96-DPI design units to physical pixels for the given DPI."""
    dpi = dpi if dpi is not None else win32_system_dpi()
    return max(1, int(logical * dpi / 96))


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
