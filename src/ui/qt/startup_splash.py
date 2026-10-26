"""Minimal startup splash (packaged exe / first-run Settings)."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget


class _LoadingPanel(QWidget):
    """Monochrome LOADING… + bordered bar + percent (matches packaged Win32 splash)."""

    def __init__(self) -> None:
        super().__init__()
        self._percent = 0
        self.setFixedHeight(118)

    def percent(self) -> int:
        return self._percent

    def set_percent(self, value: int) -> None:
        self._percent = max(0, min(100, value))
        self.update()

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        w = self.width()
        title_font = QFont("Segoe UI", 11)
        title_font.setWeight(QFont.Weight.DemiBold)
        title_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2.0)
        p.setFont(title_font)
        p.setPen(QColor(0, 0, 0))
        p.drawText(0, 8, w, 28, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, "LOADING...")

        margin = 8
        bar_left = margin
        bar_top = 44
        bar_w = w - 2 * margin
        bar_h = 24
        inset = 3

        p.setPen(QPen(QColor(0, 0, 0), 2))
        p.setBrush(QColor(255, 255, 255))
        p.drawRect(bar_left, bar_top, bar_w, bar_h)

        inner_x = bar_left + inset
        inner_y = bar_top + inset
        inner_w = bar_w - 2 * inset
        inner_h = bar_h - 2 * inset
        p.fillRect(inner_x, inner_y, inner_w, inner_h, QColor(255, 255, 255))

        fill_w = int(inner_w * self._percent / 100)
        if fill_w > 0:
            grad = QLinearGradient(inner_x, inner_y, inner_x + fill_w, inner_y)
            grad.setColorAt(0.0, QColor(0, 0, 0))
            grad.setColorAt(1.0, QColor(120, 120, 120))
            p.fillRect(inner_x, inner_y, fill_w, inner_h, grad)

        pct_font = QFont("Segoe UI", 11)
        pct_font.setWeight(QFont.Weight.DemiBold)
        p.setFont(pct_font)
        p.drawText(
            0,
            bar_top + bar_h + 10,
            w,
            24,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
            f"{self._percent}%",
        )


class StartupSplash(QWidget):
    """Loading bar: +10% every second, caps at 100%. Closed when Settings opens."""

    def __init__(self) -> None:
        super().__init__(
            None,
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool,
        )
        self.setObjectName("StartupSplash")
        self.setFixedSize(400, 140)
        self.setStyleSheet("QWidget#StartupSplash { background: #ffffff; }")

        self._panel = _LoadingPanel()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.addWidget(self._panel)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    def _center(self) -> None:
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        self.move(
            geo.x() + (geo.width() - self.width()) // 2,
            geo.y() + (geo.height() - self.height()) // 2,
        )

    def show_and_pulse(self) -> None:
        self._center()
        self.show()
        self.raise_()
        self._timer.start(1000)
        app = QApplication.instance()
        if app is not None:
            app.processEvents()

    def _tick(self) -> None:
        p = self._panel.percent()
        if p < 100:
            self._panel.set_percent(p + 10)

    def finish(self) -> None:
        self._timer.stop()
        self.close()
