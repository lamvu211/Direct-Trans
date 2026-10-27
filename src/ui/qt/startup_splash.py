"""Minimal startup splash (packaged exe / first-run Settings)."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

_BG = QColor("#ECECEC")
_TRACK_FACE = QColor("#E2E2E2")
_TRACK_SHADOW = QColor(0, 0, 0, 28)
_FILL_LIGHT = QColor("#C8DDB0")
_FILL_DARK = QColor("#A5C18A")
_FILL_SHADOW = QColor(0, 0, 0, 45)
_TEXT_TITLE = QColor("#3A3A3A")
_TEXT_SUB = QColor("#9A9A9A")
_TOOLTIP_BG = QColor("#F7F7F7")
_TOOLTIP_BORDER = QColor("#D8D8D8")
_TOOLTIP_TEXT = QColor("#6E6E6E")

_PROGRESS_STEP = 20
_PROGRESS_INTERVAL_MS = 1000


class _LoadingPanel(QWidget):
    """Soft UI loading bar with tooltip (matches startup mockup)."""

    def __init__(self) -> None:
        super().__init__()
        self._percent = _PROGRESS_STEP
        self.setFixedHeight(168)

    def percent(self) -> int:
        return self._percent

    def set_percent(self, value: int) -> None:
        self._percent = max(0, min(100, value))
        self.update()

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w = self.width()
        bar_w = min(300, w - 48)
        bar_h = 14
        bar_left = (w - bar_w) // 2
        bar_top = 58
        radius = bar_h / 2.0

        self._draw_track(p, bar_left, bar_top, bar_w, bar_h, radius)

        inner_pad = 2.0
        inner_x = bar_left + inner_pad
        inner_y = bar_top + inner_pad
        inner_w = bar_w - 2 * inner_pad
        inner_h = bar_h - 2 * inner_pad
        inner_r = max(1.0, inner_h / 2.0)
        fill_w = inner_w * self._percent / 100.0

        if fill_w > 0.5:
            self._draw_fill(p, inner_x, inner_y, fill_w, inner_h, inner_r)
            tip_x = inner_x + fill_w
            self._draw_tooltip(p, tip_x, bar_top, f"{self._percent}%")

        title_font = QFont("Segoe UI", 13)
        title_font.setWeight(QFont.Weight.Bold)
        p.setFont(title_font)
        p.setPen(_TEXT_TITLE)
        p.drawText(0, bar_top + bar_h + 28, w, 26, Qt.AlignmentFlag.AlignHCenter, "Loading")

        sub_font = QFont("Segoe UI", 10)
        p.setFont(sub_font)
        p.setPen(_TEXT_SUB)
        p.drawText(0, bar_top + bar_h + 52, w, 22, Qt.AlignmentFlag.AlignHCenter, "Please Wait...")

    def _round_path(self, x: float, y: float, width: float, height: float, radius: float) -> QPainterPath:
        path = QPainterPath()
        path.addRoundedRect(QRectF(x, y, width, height), radius, radius)
        return path

    def _draw_track(self, p: QPainter, x: int, y: int, width: int, height: int, radius: float) -> None:
        groove = self._round_path(x, y, width, height, radius)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(_TRACK_SHADOW)
        p.drawPath(self._round_path(x, y + 1.2, width, height, radius))
        p.setBrush(_TRACK_FACE)
        p.drawPath(groove)
        highlight = QLinearGradient(x, y, x, y + height)
        highlight.setColorAt(0.0, QColor(255, 255, 255, 90))
        highlight.setColorAt(0.45, QColor(255, 255, 255, 0))
        highlight.setColorAt(1.0, QColor(0, 0, 0, 22))
        p.setBrush(highlight)
        p.drawPath(groove)

    def _draw_fill(
        self,
        p: QPainter,
        x: float,
        y: float,
        width: float,
        height: float,
        radius: float,
    ) -> None:
        fill_path = self._round_path(x, y, width, height, radius)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(_FILL_SHADOW)
        p.drawPath(self._round_path(x, y + 2.0, width, height, radius))
        grad = QLinearGradient(x, y, x, y + height)
        grad.setColorAt(0.0, _FILL_LIGHT)
        grad.setColorAt(1.0, _FILL_DARK)
        p.setBrush(grad)
        p.drawPath(fill_path)
        gloss = QLinearGradient(x, y, x, y + height)
        gloss.setColorAt(0.0, QColor(255, 255, 255, 70))
        gloss.setColorAt(0.5, QColor(255, 255, 255, 0))
        p.setBrush(gloss)
        p.drawPath(fill_path)

    def _draw_tooltip(self, p: QPainter, anchor_x: float, bar_top: int, text: str) -> None:
        tip_w = 44.0
        tip_h = 22.0
        tip_y = bar_top - tip_h - 10.0
        tip_x = anchor_x - tip_w / 2.0
        tip_x = max(4.0, min(self.width() - tip_w - 4.0, tip_x))

        bubble = QPainterPath()
        bubble.addRoundedRect(QRectF(tip_x, tip_y, tip_w, tip_h), 6, 6)
        pointer = QPainterPath()
        px = anchor_x
        py = tip_y + tip_h
        pointer.moveTo(px - 5, py - 0.5)
        pointer.lineTo(px, py + 5)
        pointer.lineTo(px + 5, py - 0.5)
        pointer.closeSubpath()
        shape = bubble.united(pointer)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(0, 0, 0, 35))
        p.drawPath(shape.translated(0, 1.5))
        p.setBrush(_TOOLTIP_BG)
        p.setPen(QPen(_TOOLTIP_BORDER, 1))
        p.drawPath(shape)

        font = QFont("Segoe UI", 9)
        p.setFont(font)
        p.setPen(_TOOLTIP_TEXT)
        p.drawText(int(tip_x), int(tip_y), int(tip_w), int(tip_h), Qt.AlignmentFlag.AlignCenter, text)


class StartupSplash(QWidget):
    """Loading bar: starts at 20%, +20% every second, caps at 100%. Closed when Settings opens."""

    def __init__(self) -> None:
        super().__init__(
            None,
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool,
        )
        self.setObjectName("StartupSplash")
        self.setFixedSize(380, 200)
        self.setStyleSheet(f"QWidget#StartupSplash {{ background: {_BG.name()}; }}")

        self._panel = _LoadingPanel()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
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
        self._panel.set_percent(_PROGRESS_STEP)
        self._center()
        self.show()
        self.raise_()
        self._timer.start(_PROGRESS_INTERVAL_MS)
        app = QApplication.instance()
        if app is not None:
            app.processEvents()

    def _tick(self) -> None:
        p = self._panel.percent()
        if p < 100:
            self._panel.set_percent(min(100, p + _PROGRESS_STEP))

    def finish(self) -> None:
        self._timer.stop()
        self.close()
