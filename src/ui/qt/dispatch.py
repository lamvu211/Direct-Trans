"""Schedule callables on the Qt main thread (thread-safe for tray / worker threads)."""

from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import QObject, Qt, QThread, QTimer, Signal, Slot
from PySide6.QtWidgets import QApplication

_app = None
_dispatcher: Optional["_MainDispatcher"] = None


class _MainDispatcher(QObject):
    """Queues Python callables onto the QApplication thread."""

    _invoke = Signal(object, tuple, dict)
    _invoke_delayed = Signal(int, object, tuple, dict)

    def __init__(self) -> None:
        super().__init__()
        self._invoke.connect(self._run, Qt.ConnectionType.QueuedConnection)
        self._invoke_delayed.connect(self._run_delayed, Qt.ConnectionType.QueuedConnection)

    @Slot(object, tuple, dict)
    def _run(self, fn: Callable, args: tuple, kwargs: dict) -> None:
        if fn:
            fn(*args, **kwargs)

    @Slot(int, object, tuple, dict)
    def _run_delayed(self, delay_ms: int, fn: Callable, args: tuple, kwargs: dict) -> None:
        QTimer.singleShot(delay_ms, lambda: fn(*args, **kwargs))


def set_qt_application(app) -> None:
    global _app, _dispatcher
    _app = app
    _dispatcher = _MainDispatcher()
    _dispatcher.moveToThread(app.thread())


def get_qt_application():
    return _app


def _ensure_dispatcher() -> _MainDispatcher:
    global _dispatcher
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication not initialized")
    if _dispatcher is None:
        set_qt_application(app)
    return _dispatcher


def run_on_main(fn: Callable, *args, **kwargs) -> None:
    """Run ``fn`` on the Qt GUI thread (safe from pystray / background threads)."""
    app = QApplication.instance()
    if app is None:
        fn(*args, **kwargs)
        return
    if QThread.currentThread() == app.thread():
        fn(*args, **kwargs)
        return
    _ensure_dispatcher()._invoke.emit(fn, args, kwargs)


def schedule_ms(delay_ms: int, fn: Callable, *args, **kwargs) -> None:
    app = QApplication.instance()
    if app is None:
        QTimer.singleShot(delay_ms, lambda: fn(*args, **kwargs))
        return
    if QThread.currentThread() == app.thread():
        QTimer.singleShot(delay_ms, lambda: fn(*args, **kwargs))
        return
    _ensure_dispatcher()._invoke_delayed.emit(delay_ms, fn, args, kwargs)
