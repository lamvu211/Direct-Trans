"""Scrollable dialog listing all hotkeys (keeps settings window fixed height)."""

from __future__ import annotations

import copy
import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ui.i18n import TRANSLATIONS
from ui.qt.hotkey_dialog import HotkeyDialog
from ui.qt.theme import apply_theme


class _ManageHotkeyRow(QFrame):
    def __init__(self, hk: dict, on_edit, parent=None):
        super().__init__(parent)
        self._hk = hk
        self._on_edit = on_edit
        self.setObjectName("hkRow")
        self.setFixedHeight(24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mouseDoubleClickEvent(self, event):
        self._on_edit(self._hk)
        super().mouseDoubleClickEvent(event)


class HotkeyManageDialog(QDialog):
    def __init__(self, config, on_save_callback, hotkey_manager, get_current_lang, parent=None):
        super().__init__(parent)
        self.config = config
        self.on_save_callback = on_save_callback
        self.hotkey_manager = hotkey_manager
        self.get_current_lang = get_current_lang
        lang = get_current_lang()
        self._t = TRANSLATIONS.get(lang, TRANSLATIONS["vi"])

        self.setObjectName("root")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        theme_id = self.config.get_ui_theme() if self.config else "midnight_gold"
        apply_theme(self, theme_id)

        self.setWindowTitle(f"🖥️ {self._t.get('hotkey_section', 'Hotkeys').strip()}")
        self.setFixedWidth(480)

        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "icon.ico"
        )
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(8)

        host = QWidget()
        host.setObjectName("scrollViewport")
        self._list = QVBoxLayout(host)
        self._list.setContentsMargins(0, 2, 0, 2)
        self._list.setSpacing(3)
        root.addWidget(host)

        bottom_bar = QHBoxLayout()
        bottom_bar.setContentsMargins(0, 2, 0, 0)
        bottom_bar.setSpacing(8)

        add_btn = QPushButton(self._t["add_hk_btn"])
        add_btn.setObjectName("ctaSmall")
        add_btn.setFixedHeight(24)
        add_btn.clicked.connect(self._on_add)
        bottom_bar.addWidget(add_btn, 0, Qt.AlignmentFlag.AlignLeft)

        bottom_bar.addStretch(1)

        close_btn = QPushButton(self._t.get("close_tip", "Đóng"))
        close_btn.setObjectName("ghost")
        close_btn.setFixedHeight(24)
        close_btn.clicked.connect(self.accept)
        bottom_bar.addWidget(close_btn, 0, Qt.AlignmentFlag.AlignRight)

        root.addLayout(bottom_bar)
        self._reload_rows()

    def _center_on_parent(self):
        p = self.parent()
        if p is not None:
            top_p = p.window() if hasattr(p, "window") else p
            p_geo = top_p.frameGeometry() if top_p.isWindow() else top_p.geometry()
            x = p_geo.x() + (p_geo.width() - self.width()) // 2
            y = p_geo.y() + (p_geo.height() - self.height()) // 2
            self.move(x, y)

    def showEvent(self, event):
        super().showEvent(event)
        self._update_size()
        self._center_on_parent()
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, self._center_on_parent)

    def _update_size(self):
        if self.layout() is not None:
            self.layout().activate()
            hint = self.layout().sizeHint()
            self.setFixedSize(480, hint.height())
        if self.isVisible():
            self._center_on_parent()

    def _reload_rows(self):
        while self._list.count():
            item = self._list.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        for hk in copy.deepcopy(self.config.get_hotkeys()):
            self._list.addWidget(self._row(hk))
        self._update_size()

    def _row(self, hk: dict) -> QFrame:
        row = _ManageHotkeyRow(hk, self._on_edit)
        row.setToolTip(self._t.get("edit_hk_tip", "Double-click to edit"))
        h = QHBoxLayout(row)
        h.setContentsMargins(8, 0, 4, 0)
        h.setSpacing(6)

        mode = hk.get("mode", "popup")
        mode_label = self._t["popup_mode"] if mode == "popup" else self._t["replace_mode"]

        key_lbl = QLabel(hk.get("key_combo", ""))
        key_lbl.setObjectName("hkKey")
        key_lbl.setFixedWidth(112)
        key_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        lang_name = hk.get("target_language_name", "")
        lang_lbl = QLabel(lang_name)
        lang_lbl.setObjectName("hkLang")
        lang_lbl.setMinimumWidth(72)
        fm = lang_lbl.fontMetrics()
        lang_lbl.setText(fm.elidedText(lang_name, Qt.TextElideMode.ElideRight, 200))
        lang_lbl.setToolTip(lang_name)
        mode_lbl = QLabel(mode_label)
        mode_lbl.setObjectName("hkMode")
        mode_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mode_lbl.setMinimumWidth(80)

        h.addWidget(key_lbl)
        h.addWidget(lang_lbl, 1)
        h.addWidget(mode_lbl)

        hid = hk.get("id")
        delb = QToolButton()
        delb.setText("✕")
        delb.setObjectName("hkDel")
        delb.setToolTip(self._t.get("del_hk_tip", "Xóa phím tắt này"))
        delb.setAccessibleName(self._t.get("del_hk_tip", "Xóa phím tắt này"))
        delb.setFixedSize(24, 24)
        delb.clicked.connect(lambda: self._on_delete(hid))

        h.addWidget(delb)
        return row

    def _notify(self):
        if self.on_save_callback:
            self.on_save_callback()
        if self.hotkey_manager:
            self.hotkey_manager.reload()

    def _on_delete(self, hotkey_id: str):
        self.config.remove_hotkey(hotkey_id)
        self._notify()
        self._reload_rows()

    def _on_add(self):
        dlg = HotkeyDialog(self.config, copy.deepcopy(self.config.get_hotkeys()), parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._notify()
            self._reload_rows()

    def _on_edit(self, hk: dict):
        dlg = HotkeyDialog(
            self.config,
            [x for x in copy.deepcopy(self.config.get_hotkeys()) if x.get("id") != hk.get("id")],
            parent=self,
            edit_hotkey=hk,
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._notify()
            self._reload_rows()
