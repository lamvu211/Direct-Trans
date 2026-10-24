"""Custom HSV Color Picker Popup (matching Antigravity / modern UI style)."""

from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, QSize, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QLinearGradient,
    QMouseEvent,
    QPainter,
    QPen,
)
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class _SaturationValueBox(QWidget):
    """2D Saturation-Value gradient box with interactive handle."""

    colorChanged = Signal(float, float)  # sat, val (0.0 to 1.0)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 130)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self._hue = 0.6  # default ~blue
        self._sat = 0.5
        self._val = 0.8
        self._tracking = False

    def set_hue(self, hue: float):
        self._hue = max(0.0, min(1.0, hue))
        self.update()

    def set_sat_val(self, sat: float, val: float):
        self._sat = max(0.0, min(1.0, sat))
        self._val = max(0.0, min(1.0, val))
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._tracking = True
            self._update_from_pos(event.position().toPoint())

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._tracking:
            self._update_from_pos(event.position().toPoint())

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._tracking = False

    def _update_from_pos(self, pt: QPoint):
        w = max(1, self.width())
        h = max(1, self.height())
        sat = max(0.0, min(1.0, pt.x() / w))
        val = max(0.0, min(1.0, 1.0 - (pt.y() / h)))
        self._sat = sat
        self._val = val
        self.update()
        self.colorChanged.emit(sat, val)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()

        # Rounded background clip
        p.setPen(Qt.PenStyle.NoPen)
        # 1. Horizontal gradient: white -> pure hue color
        hue_color = QColor.fromHsvF(self._hue, 1.0, 1.0)
        h_grad = QLinearGradient(0, 0, self.width(), 0)
        h_grad.setColorAt(0.0, QColor(255, 255, 255))
        h_grad.setColorAt(1.0, hue_color)
        p.setBrush(h_grad)
        p.drawRoundedRect(rect, 6, 6)

        # 2. Vertical gradient: transparent -> black
        v_grad = QLinearGradient(0, 0, 0, self.height())
        v_grad.setColorAt(0.0, QColor(0, 0, 0, 0))
        v_grad.setColorAt(1.0, QColor(0, 0, 0, 255))
        p.setBrush(v_grad)
        p.drawRoundedRect(rect, 6, 6)

        # Draw handle circle
        hx = int(self._sat * self.width())
        hy = int((1.0 - self._val) * self.height())
        hx = max(5, min(self.width() - 5, hx))
        hy = max(5, min(self.height() - 5, hy))

        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(QColor(0, 0, 0, 180), 3))
        p.drawEllipse(QPoint(hx, hy), 6, 6)
        p.setPen(QPen(QColor(255, 255, 255, 240), 1.8))
        p.drawEllipse(QPoint(hx, hy), 6, 6)
        p.end()


class _HueSlider(QWidget):
    """Horizontal Rainbow Hue Slider with handle."""

    hueChanged = Signal(float)  # hue 0.0 to 1.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 16)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._hue = 0.6
        self._tracking = False

    def set_hue(self, hue: float):
        self._hue = max(0.0, min(1.0, hue))
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._tracking = True
            self._update_from_pos(event.position().toPoint())

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._tracking:
            self._update_from_pos(event.position().toPoint())

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._tracking = False

    def _update_from_pos(self, pt: QPoint):
        w = max(1, self.width())
        hue = max(0.0, min(1.0, pt.x() / w))
        self._hue = hue
        self.update()
        self.hueChanged.emit(hue)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()

        # Rainbow gradient
        grad = QLinearGradient(0, 0, self.width(), 0)
        grad.setColorAt(0.00, QColor(255, 0, 0))
        grad.setColorAt(0.17, QColor(255, 255, 0))
        grad.setColorAt(0.33, QColor(0, 255, 0))
        grad.setColorAt(0.50, QColor(0, 255, 255))
        grad.setColorAt(0.67, QColor(0, 0, 255))
        grad.setColorAt(0.83, QColor(255, 0, 255))
        grad.setColorAt(1.00, QColor(255, 0, 0))

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(grad)
        p.drawRoundedRect(rect, 8, 8)

        # Handle
        hx = int(self._hue * self.width())
        hx = max(6, min(self.width() - 6, hx))
        cy = self.height() // 2

        cur_color = QColor.fromHsvF(self._hue, 1.0, 1.0)
        p.setBrush(cur_color)
        p.setPen(QPen(QColor(255, 255, 255), 2))
        p.drawEllipse(QPoint(hx, cy), 6, 6)
        p.end()


class ColorPickerPopup(QFrame):
    """Floating color picker popup menu (HSV box + Hue slider)."""

    colorSelected = Signal(str)  # HEX string "#RRGGBB"

    def __init__(self, initial_color: str = "#B1B9E5", parent=None, theme_id: str = "midnight_gold"):
        super().__init__(parent, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setObjectName("colorPickerPopup")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._color = QColor(initial_color)
        if not self._color.isValid():
            self._color = QColor("#B1B9E5")

        hue = max(0.0, self._color.hsvHueF())
        if hue < 0:
            hue = 0.0
        sat = self._color.hsvSaturationF()
        val = self._color.valueF()

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        # Container frame for styling
        card = QFrame()
        card.setObjectName("pickerCard")
        if theme_id == "nord_snow":
            card.setStyleSheet("""
                QFrame#pickerCard {
                    background: #ECEFF4;
                    border: 1px solid #D8DEE9;
                    border-radius: 8px;
                }
            """)
        elif theme_id == "rose_champagne":
            card.setStyleSheet("""
                QFrame#pickerCard {
                    background: #ffffff;
                    border: 1px solid #f9a8d4;
                    border-radius: 8px;
                }
            """)
        else:
            card.setStyleSheet("""
                QFrame#pickerCard {
                    background: #181820;
                    border: 1px solid #383848;
                    border-radius: 8px;
                }
            """)
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(8, 8, 8, 8)
        card_lay.setSpacing(8)

        self._sv_box = _SaturationValueBox(self)
        self._sv_box.set_hue(hue)
        self._sv_box.set_sat_val(sat, val)
        self._sv_box.colorChanged.connect(self._on_sv_changed)
        card_lay.addWidget(self._sv_box)

        self._hue_slider = _HueSlider(self)
        self._hue_slider.set_hue(hue)
        self._hue_slider.hueChanged.connect(self._on_hue_changed)
        card_lay.addWidget(self._hue_slider)

        root.addWidget(card)

    def set_color(self, hex_color: str):
        c = QColor(hex_color)
        if c.isValid():
            self._color = c
            hue = max(0.0, c.hsvHueF())
            if hue < 0:
                hue = 0.0
            self._sv_box.set_hue(hue)
            self._sv_box.set_sat_val(c.hsvSaturationF(), c.valueF())
            self._hue_slider.set_hue(hue)

    def _on_sv_changed(self, sat: float, val: float):
        hue = self._hue_slider._hue
        self._color = QColor.fromHsvF(hue, sat, val)
        self.colorSelected.emit(self._color.name().upper())

    def _on_hue_changed(self, hue: float):
        self._sv_box.set_hue(hue)
        sat = self._sv_box._sat
        val = self._sv_box._val
        self._color = QColor.fromHsvF(hue, sat, val)
        self.colorSelected.emit(self._color.name().upper())
