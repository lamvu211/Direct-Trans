"""Sample standalone preview for high-fidelity neumorphic loading bar.
Can be executed directly to view live Qt window or render comparison image.
"""

from __future__ import annotations

import sys
import os

from PySide6.QtCore import Qt, QRectF, QTimer
from PySide6.QtGui import (
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QRadialGradient,
)
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QSlider


class NeumorphicLoadingBar(QWidget):
    """High-fidelity 3D soft-UI loading bar matching the design reference."""

    def __init__(self, percent: int = 50, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._percent = percent
        self.setFixedSize(400, 300)

    def percent(self) -> int:
        return self._percent

    def set_percent(self, value: int) -> None:
        self._percent = max(0, min(100, value))
        self.update()

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        w = self.width()
        h = self.height()

        # 1. Background with subtle vignette
        self._draw_background(p, w, h)

        # Bar layout parameters
        bar_w = 300.0
        bar_h = 20.0
        bar_left = (w - bar_w) / 2.0
        bar_top = 138.0
        radius = bar_h / 2.0

        # 2. Draw recessed track (Groove with inner shadow & bottom highlight)
        self._draw_track(p, bar_left, bar_top, bar_w, bar_h, radius)

        # 3. Draw green 3D fill capsule & tooltip
        inner_pad = 1.5
        inner_x = bar_left + inner_pad
        inner_y = bar_top + inner_pad
        inner_w = bar_w - 2 * inner_pad
        inner_h = bar_h - 2 * inner_pad
        inner_r = inner_h / 2.0

        fill_w = inner_w * (self._percent / 100.0)

        if fill_w >= inner_h:
            self._draw_fill(p, inner_x, inner_y, fill_w, inner_h, inner_r)
            tip_x = inner_x + fill_w
            self._draw_tooltip(p, tip_x, bar_top, f"{self._percent}%")
        elif fill_w > 0:
            # When fill width is smaller than end cap diameter
            self._draw_fill_small(p, inner_x, inner_y, fill_w, inner_h, inner_r)
            tip_x = inner_x + fill_w
            self._draw_tooltip(p, tip_x, bar_top, f"{self._percent}%")

        # 4. Typography
        self._draw_typography(p, w, bar_top, bar_h)

    def _draw_background(self, p: QPainter, w: int, h: int) -> None:
        rad = QRadialGradient(w / 2.0, h / 2.0, max(w, h) * 0.75)
        rad.setColorAt(0.0, QColor(252, 252, 252))
        rad.setColorAt(0.65, QColor(242, 241, 239))
        rad.setColorAt(1.0, QColor(218, 215, 210))
        p.fillRect(0, 0, w, h, rad)

    def _draw_track(
        self, p: QPainter, x: float, y: float, w: float, h: float, r: float
    ) -> None:
        # Bottom specular rim highlight (creates carved trench illusion)
        rim_path = QPainterPath()
        rim_path.addRoundedRect(QRectF(x, y + 1.2, w, h), r, r)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(255, 255, 255, 230))
        p.drawPath(rim_path)

        track_path = QPainterPath()
        track_path.addRoundedRect(QRectF(x, y, w, h), r, r)

        # Track base color
        p.setBrush(QColor(224, 222, 219))
        p.drawPath(track_path)

        # Inner shadow - multi-layer gradient
        # Top sunken shadow
        p.save()
        p.setClipPath(track_path)

        top_shadow = QLinearGradient(x, y, x, y + h)
        top_shadow.setColorAt(0.0, QColor(0, 0, 0, 75))
        top_shadow.setColorAt(0.18, QColor(0, 0, 0, 38))
        top_shadow.setColorAt(0.45, QColor(0, 0, 0, 10))
        top_shadow.setColorAt(0.75, QColor(0, 0, 0, 0))
        p.setBrush(top_shadow)
        p.drawRect(QRectF(x - 2, y, w + 4, h))

        # Bottom inner floor reflection
        bottom_refl = QLinearGradient(x, y, x, y + h)
        bottom_refl.setColorAt(0.0, QColor(255, 255, 255, 0))
        bottom_refl.setColorAt(0.7, QColor(255, 255, 255, 0))
        bottom_refl.setColorAt(1.0, QColor(255, 255, 255, 95))
        p.setBrush(bottom_refl)
        p.drawRect(QRectF(x - 2, y, w + 4, h))

        # Left end-cap radial shadow
        left_rad = QRadialGradient(x + r, y + r, r)
        left_rad.setColorAt(0.0, QColor(0, 0, 0, 0))
        left_rad.setColorAt(0.6, QColor(0, 0, 0, 18))
        left_rad.setColorAt(1.0, QColor(0, 0, 0, 60))
        p.setBrush(left_rad)
        p.drawEllipse(QRectF(x, y, 2 * r, h))

        # Right end-cap radial shadow
        right_rad = QRadialGradient(x + w - r, y + r, r)
        right_rad.setColorAt(0.0, QColor(0, 0, 0, 0))
        right_rad.setColorAt(0.6, QColor(0, 0, 0, 18))
        right_rad.setColorAt(1.0, QColor(0, 0, 0, 60))
        p.setBrush(right_rad)
        p.drawEllipse(QRectF(x + w - 2 * r, y, 2 * r, h))

        p.restore()

    def _draw_fill(
        self, p: QPainter, x: float, y: float, w: float, h: float, r: float
    ) -> None:
        # Pill path
        fill_path = QPainterPath()
        fill_path.addRoundedRect(QRectF(x, y, w, h), r, r)

        # Soft drop shadow underneath the capsule
        p.setPen(Qt.PenStyle.NoPen)
        for offset_y, alpha in [(2.5, 30), (1.5, 45), (0.8, 60)]:
            sh_path = QPainterPath()
            sh_path.addRoundedRect(QRectF(x, y + offset_y, w, h), r, r)
            p.setBrush(QColor(0, 0, 0, int(alpha)))
            p.drawPath(sh_path)

        # Main green body 3D gradient
        body_grad = QLinearGradient(x, y, x, y + h)
        body_grad.setColorAt(0.0, QColor("#D4EABE"))
        body_grad.setColorAt(0.2, QColor("#C4DFAB"))
        body_grad.setColorAt(0.55, QColor("#A7C78E"))
        body_grad.setColorAt(0.85, QColor("#91B376"))
        body_grad.setColorAt(1.0, QColor("#7E9F63"))
        p.setBrush(body_grad)
        p.drawPath(fill_path)

        # Specular highlight (cylindrical gloss along top edge)
        gloss_path = QPainterPath()
        gloss_h = h * 0.45
        gloss_path.addRoundedRect(QRectF(x + 1.0, y + 0.8, w - 2.0, gloss_h), r * 0.7, r * 0.7)

        gloss_grad = QLinearGradient(x, y, x, y + gloss_h)
        gloss_grad.setColorAt(0.0, QColor(255, 255, 255, 180))
        gloss_grad.setColorAt(0.4, QColor(255, 255, 255, 100))
        gloss_grad.setColorAt(1.0, QColor(255, 255, 255, 0))

        p.setBrush(gloss_grad)
        p.drawPath(gloss_path)

        # Right edge dome highlight (subtle 3D rounding at the cap)
        cap_x = x + w - r * 1.5
        if cap_x > x:
            p.save()
            p.setClipPath(fill_path)
            cap_rad = QRadialGradient(x + w - r, y + r * 0.7, r)
            cap_rad.setColorAt(0.0, QColor(255, 255, 255, 80))
            cap_rad.setColorAt(0.5, QColor(255, 255, 255, 20))
            cap_rad.setColorAt(1.0, QColor(0, 0, 0, 30))
            p.setBrush(cap_rad)
            p.drawEllipse(QRectF(x + w - 2 * r, y, 2 * r, h))
            p.restore()

    def _draw_fill_small(
        self, p: QPainter, x: float, y: float, w: float, h: float, r: float
    ) -> None:
        p.save()
        clip = QPainterPath()
        clip.addRoundedRect(QRectF(x, y, 2 * r, h), r, r)
        p.setClipPath(clip)
        self._draw_fill(p, x, y, 2 * r, h, r)
        p.restore()

    def _draw_tooltip(self, p: QPainter, anchor_x: float, bar_top: float, text: str) -> None:
        tip_w = 40.0
        tip_h = 23.0
        tip_y = bar_top - tip_h - 10.0
        tip_x = anchor_x - tip_w / 2.0
        tip_x = max(6.0, min(self.width() - tip_w - 6.0, tip_x))

        # Smooth speech bubble with downward pointer
        bubble = QPainterPath()
        bubble.addRoundedRect(QRectF(tip_x, tip_y, tip_w, tip_h), 5.0, 5.0)

        pointer = QPainterPath()
        px = max(tip_x + 6.0, min(tip_x + tip_w - 6.0, anchor_x))
        py = tip_y + tip_h
        pointer.moveTo(px - 4.5, py - 0.5)
        pointer.lineTo(px, py + 4.5)
        pointer.lineTo(px + 4.5, py - 0.5)
        pointer.closeSubpath()

        shape = bubble.united(pointer)

        # Soft drop shadow
        p.setPen(Qt.PenStyle.NoPen)
        for offset_y, alpha in [(2.0, 25), (1.0, 45)]:
            p.setBrush(QColor(0, 0, 0, int(alpha)))
            p.drawPath(shape.translated(0, offset_y))

        # Face gradient (clean white-gray soft bevel)
        face_grad = QLinearGradient(tip_x, tip_y, tip_x, tip_y + tip_h)
        face_grad.setColorAt(0.0, QColor(255, 255, 255))
        face_grad.setColorAt(1.0, QColor(238, 238, 238))
        p.setBrush(face_grad)
        p.setPen(QPen(QColor(214, 214, 214), 1.0))
        p.drawPath(shape)

        # Tooltip text
        font = QFont("Segoe UI", 9)
        font.setWeight(QFont.Weight.DemiBold)
        p.setFont(font)
        p.setPen(QColor(105, 110, 115))
        text_rect = QRectF(tip_x, tip_y + 1, tip_w, tip_h - 2)
        p.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

    def _draw_typography(
        self, p: QPainter, w: int, bar_top: float, bar_h: float
    ) -> None:
        title_top = bar_top + bar_h + 26.0

        title_font = QFont("Segoe UI", 16)
        title_font.setWeight(QFont.Weight.Bold)
        p.setFont(title_font)
        p.setPen(QColor(100, 100, 100))
        p.drawText(QRectF(0, title_top, w, 28), Qt.AlignmentFlag.AlignHCenter, "Loading")

        sub_font = QFont("Segoe UI", 10)
        sub_font.setWeight(QFont.Weight.Normal)
        p.setFont(sub_font)
        p.setPen(QColor(145, 145, 145))
        p.drawText(QRectF(0, title_top + 28, w, 22), Qt.AlignmentFlag.AlignHCenter, "Please Wait...")


def render_to_file(percent: int = 50, output_path: str = "sample_preview.png") -> None:
    app = QApplication.instance() or QApplication(["--platform", "offscreen"])
    widget = NeumorphicLoadingBar(percent=percent)
    pixmap = QPixmap(400, 300)
    pixmap.fill(Qt.GlobalColor.transparent)
    widget.render(pixmap)
    pixmap.save(output_path, "PNG")
    print(f"Rendered sample preview at {percent}% to {output_path}")


def main_gui() -> None:
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Sample Loading Bar Preview (Interactive)")
    layout = QVBoxLayout(window)

    bar = NeumorphicLoadingBar(percent=50)
    layout.addWidget(bar, alignment=Qt.AlignmentFlag.AlignCenter)

    controls = QHBoxLayout()
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setRange(0, 100)
    slider.setValue(50)
    slider.valueChanged.connect(bar.set_percent)
    controls.addWidget(slider)

    layout.addLayout(controls)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    if "--gui" in sys.argv:
        main_gui()
    else:
        render_to_file(percent=50, output_path="samples/sample_loading_preview.png")
