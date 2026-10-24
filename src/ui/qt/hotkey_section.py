"""Hotkey list with collapse (3 rows) + add/delete."""

from __future__ import annotations

import copy

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ui.i18n import TRANSLATIONS
from ui.qt.hotkey_dialog import HotkeyDialog
from ui.qt.hotkey_manage_dialog import HotkeyManageDialog
from ui.qt.hotkey_ui import pause_translation_hotkeys
from ui.qt.widgets import CONTROL_HEIGHT

HOTKEYS_COLLAPSED_COUNT = 5


class _HotkeyRow(QFrame):
    def __init__(self, hk: dict, on_edit, on_delete, parent=None):
        super().__init__(parent)
        self._hk = hk
        self._on_edit = on_edit
        self.setObjectName("hkRow")
        self.setFixedHeight(CONTROL_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(TRANSLATIONS["vi"].get("edit_hk_tip", "Double-click to edit"))

    def mouseDoubleClickEvent(self, event):
        self._on_edit(self._hk)
        super().mouseDoubleClickEvent(event)


class HotkeySection(QWidget):
    def __init__(
        self,
        config,
        on_save_callback,
        hotkey_manager,
        get_current_lang,
        external_add_btn: QPushButton | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.config = config
        self.on_save_callback = on_save_callback
        self.hotkey_manager = hotkey_manager
        self.get_current_lang = get_current_lang
        self._rows_host = QVBoxLayout()
        self._rows_host.setContentsMargins(0, 0, 0, 4)
        self._rows_host.setSpacing(3)
        self._more_btn = QPushButton()
        self._more_btn.setObjectName("showMore")
        self._more_btn.setFixedHeight(22)
        self._more_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._more_btn.clicked.connect(self._open_manage_dialog)
        self._add_btn = external_add_btn
        if self._add_btn is None:
            self._add_btn = QPushButton()
            self._add_btn.setObjectName("ctaSmall")
        self._add_btn.clicked.connect(self._on_add)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(4)
        root.addLayout(self._rows_host)
        root.addWidget(self._more_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        self.reload()

    def add_button(self) -> QPushButton:
        return self._add_btn

    def _t(self):
        return TRANSLATIONS.get(self.get_current_lang(), TRANSLATIONS["vi"])

    def reload(self):
        self._render()

    def _hotkeys(self):
        return copy.deepcopy(self.config.get_hotkeys())

    def _exec_dialog(self, dlg: QDialog) -> int:
        with pause_translation_hotkeys(self.hotkey_manager):
            return dlg.exec()

    def _open_manage_dialog(self):
        dlg = HotkeyManageDialog(
            self.config,
            self.on_save_callback,
            self.hotkey_manager,
            self.get_current_lang,
            parent=self.window(),
        )
        dlg._update_size()
        dlg._center_on_parent()
        self._exec_dialog(dlg)
        self._render()

    def _clear_rows(self):
        while self._rows_host.count():
            item = self._rows_host.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

    def _render(self):
        self._clear_rows()
        hotkeys = self._hotkeys()
        count = min(HOTKEYS_COLLAPSED_COUNT, len(hotkeys))
        t = self._t()
        for i in range(count):
            hk = hotkeys[i]
            self._rows_host.addWidget(self._make_row(hk))
        hidden = len(hotkeys) - HOTKEYS_COLLAPSED_COUNT
        if hidden > 0:
            self._more_btn.setVisible(True)
            self._more_btn.setText(t.get("hotkeys_show_more", "Xem thêm ({n})").format(n=hidden))
        else:
            self._more_btn.setVisible(False)
        self._add_btn.setText(t["add_hk_btn"])
        tip = t.get("edit_hk_tip", "Double-click to edit")
        self.setToolTip(tip)

    def _make_row(self, hk: dict) -> QFrame:
        row = _HotkeyRow(hk, self._on_edit, self._delete)
        h = QHBoxLayout(row)
        h.setContentsMargins(8, 0, 4, 0)
        h.setSpacing(6)
        t = self._t()
        mode = hk.get("mode", "popup")
        mode_label = t["popup_mode"] if mode == "popup" else t["replace_mode"]

        key_lbl = QLabel(hk.get("key_combo", ""))
        key_lbl.setObjectName("hkKey")
        key_lbl.setFixedWidth(112)
        key_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        lang_name = hk.get("target_language_name", "")
        lang_lbl = QLabel(lang_name)
        lang_lbl.setObjectName("hkLang")
        lang_lbl.setMinimumWidth(72)
        fm = lang_lbl.fontMetrics()
        lang_lbl.setText(fm.elidedText(lang_name, Qt.TextElideMode.ElideRight, 160))
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
        delb.setToolTip(t.get("del_hk_tip", "Xóa phím tắt này"))
        delb.setAccessibleName(t.get("del_hk_tip", "Xóa phím tắt này"))
        delb.setFixedSize(CONTROL_HEIGHT, CONTROL_HEIGHT)
        delb.clicked.connect(lambda checked=False, i=hid: self._delete(i))

        h.addWidget(delb)
        row.setToolTip(t.get("edit_hk_tip", "Double-click to edit"))
        return row

    def _on_edit(self, hk: dict):
        others = [x for x in self._hotkeys() if x.get("id") != hk.get("id")]
        dlg = HotkeyDialog(self.config, others, parent=self.window(), edit_hotkey=hk)
        if self._exec_dialog(dlg) == QDialog.DialogCode.Accepted:
            if self.on_save_callback:
                self.on_save_callback()
            if self.hotkey_manager:
                self.hotkey_manager.reload()
            self._render()

    def _delete(self, hotkey_id: str):
        self.config.remove_hotkey(hotkey_id)
        self._render()
        if self.on_save_callback:
            self.on_save_callback()
        if self.hotkey_manager:
            self.hotkey_manager.reload()

    def _on_add(self):
        dlg = HotkeyDialog(self.config, self._hotkeys(), parent=self.window())
        if self._exec_dialog(dlg) == QDialog.DialogCode.Accepted:
            if self.on_save_callback:
                self.on_save_callback()
            if self.hotkey_manager:
                self.hotkey_manager.reload()
            self._render()

    def update_ui_language(self, _lang_code: str, _font_family: str | None = None):
        self._render()
