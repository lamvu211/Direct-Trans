"""Modal dialog to add a hotkey (keyboard capture via keyboard package)."""

from __future__ import annotations

import os

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QRadioButton,
    QVBoxLayout,
)

from constants import MODE_POPUP, MODE_REPLACE
from hotkey_manager import validate_hotkey_combo
from ui.i18n import LANGUAGES, TRANSLATIONS
from ui.qt.dispatch import run_on_main
from ui.qt.theme import apply_theme


class HotkeyDialog(QDialog):
    def __init__(self, config, existing_hotkeys, parent=None, edit_hotkey: dict | None = None):
        super().__init__(parent)
        self.config = config
        self.existing = existing_hotkeys
        self._edit = edit_hotkey
        self._t = TRANSLATIONS.get(config.data.get("ui_language", "vi"), TRANSLATIONS["vi"])

        self.setObjectName("root")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        theme_id = self.config.get_ui_theme() if self.config else "midnight_gold"
        apply_theme(self, theme_id)

        title = self._t["dialog_edit_title"] if edit_hotkey else self._t["dialog_add_title"]
        self.setWindowTitle(title)

        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "icon.ico"
        )
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._detect = {"hook_id": None, "active": False}
        self._pressed: set[str] = set()
        self._accumulated: set[str] = set()
        self._recorded: list[str | None] = [None]
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        layout.addWidget(QLabel(self._t["dialog_press_prompt"]))
        self._original_combo = edit_hotkey.get("key_combo", "") if edit_hotkey else ""
        initial_combo = self._original_combo if edit_hotkey else self._t["dialog_recording"]
        self._combo_edit = QLineEdit(initial_combo)
        self._combo_edit.setObjectName("line")
        self._combo_edit.setReadOnly(True)
        layout.addWidget(self._combo_edit)
        self._combo_edit.installEventFilter(self)

        layout.addWidget(QLabel(self._t["dialog_lang_prompt"]))
        self._lang_combo = QComboBox()
        self._lang_combo.setObjectName("combo")
        default_lang_name = LANGUAGES[0][0]
        if edit_hotkey:
            for name, code in LANGUAGES:
                if code == edit_hotkey.get("target_language_code"):
                    default_lang_name = name
                    break
        for name, _code in LANGUAGES:
            self._lang_combo.addItem(name)
        idx = self._lang_combo.findText(default_lang_name)
        if idx >= 0:
            self._lang_combo.setCurrentIndex(idx)
        layout.addWidget(self._lang_combo)

        layout.addWidget(QLabel(self._t["dialog_mode_prompt"]))
        mode_row = QHBoxLayout()
        self._popup_rb = QRadioButton(self._t["dialog_mode_popup"])
        self._replace_rb = QRadioButton(self._t["dialog_mode_replace"])
        if edit_hotkey and edit_hotkey.get("mode") == MODE_REPLACE:
            self._replace_rb.setChecked(True)
        else:
            self._popup_rb.setChecked(True)
        mode_row.addWidget(self._popup_rb)
        mode_row.addWidget(self._replace_rb)
        layout.addLayout(mode_row)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        save_btn = buttons.button(QDialogButtonBox.StandardButton.Save)
        if save_btn:
            save_btn.setObjectName("cta")
            save_btn.setText(self._t.get("dialog_save_btn", "Lưu"))
        cancel_btn = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        if cancel_btn:
            cancel_btn.setObjectName("ghost")
            cancel_btn.setText(self._t.get("dialog_cancel_btn", "Hủy"))

        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)

    def eventFilter(self, obj, event):
        if obj == self._combo_edit and event.type() == QEvent.Type.FocusIn:
            self._start_detect()
        elif obj == self._combo_edit and event.type() == QEvent.Type.FocusOut:
            self._stop_detect()
        return super().eventFilter(obj, event)

    def _start_detect(self):
        if not self._edit:
            self._combo_edit.setText(self._t["dialog_recording"])
        self._detect["active"] = True
        self._pressed.clear()
        self._accumulated.clear()
        self._recorded[0] = None
        if self._detect["hook_id"]:
            try:
                import keyboard
                keyboard.unhook(self._detect["hook_id"])
            except Exception:
                pass

        def hook_callback(e):
            if not self._detect["active"]:
                return
            name = (e.name or "").lower()
            if name in ("left ctrl", "right ctrl", "ctrl"):
                name = "ctrl"
            elif name in ("left shift", "right shift", "shift"):
                name = "shift"
            elif name in ("left alt", "right alt", "alt", "alt gr"):
                name = "alt"
            elif name in ("left windows", "right windows", "win", "windows"):
                name = "win"
            if len(name) == 1:
                ascii_val = ord(name)
                if 1 <= ascii_val <= 26:
                    name = chr(ascii_val + 96)
            if e.event_type == "down":
                self._pressed.add(name)
                self._accumulated.add(name)
            elif e.event_type == "up":
                self._pressed.discard(name)
            if self._accumulated:
                modifiers = []
                main_key = None
                if "ctrl" in self._accumulated:
                    modifiers.append("ctrl")
                if "shift" in self._accumulated:
                    modifiers.append("shift")
                if "alt" in self._accumulated:
                    modifiers.append("alt")
                if "win" in self._accumulated:
                    modifiers.append("win")
                for k in self._accumulated:
                    if k not in ("ctrl", "shift", "alt", "win"):
                        main_key = "space" if k == "space" else k
                        break
                combo_parts = modifiers.copy()
                if main_key:
                    combo_parts.append(main_key)
                if combo_parts:
                    current_combo = "+".join(combo_parts)
                    self._recorded[0] = current_combo
                    run_on_main(lambda c=current_combo: self._combo_edit.setText(c))
            if e.event_type == "up" and not self._pressed:
                final_combo = self._recorded[0]
                if final_combo:
                    parts = final_combo.split("+")
                    has_main = any(p not in ("ctrl", "shift", "alt", "win") for p in parts)
                    if has_main:
                        combo_lower = final_combo.lower()
                        if any(hk.get("key_combo", "").lower() == combo_lower for hk in self.existing):
                            run_on_main(
                                lambda: QMessageBox.warning(
                                    self, self._t["dialog_dup_title"], self._t["dialog_dup_msg"]
                                )
                            )
                            self._accumulated.clear()
                            self._recorded[0] = None
                        else:
                            self._stop_detect()

        import keyboard
        self._detect["hook_id"] = keyboard.hook(hook_callback)

    def _stop_detect(self):
        self._detect["active"] = False
        if self._detect["hook_id"]:
            try:
                import keyboard
                keyboard.unhook(self._detect["hook_id"])
            except Exception:
                pass
            self._detect["hook_id"] = None
        if self._combo_edit.text() == self._t["dialog_recording"]:
            if self._edit:
                self._combo_edit.setText(self._original_combo)
            else:
                self._combo_edit.clear()

    def _save(self):
        combo = self._combo_edit.text().strip()
        if not combo or combo == self._t["dialog_recording"]:
            QMessageBox.warning(self, self._t["dialog_missing_title"], self._t["dialog_missing_info"])
            return
        ok, err = validate_hotkey_combo(combo)
        if not ok:
            msg_key = {
                "empty": "dialog_missing_info",
                "no_main_key": "dialog_hotkey_no_main",
                "no_modifier": "dialog_hotkey_no_modifier",
                "disallowed_key": "dialog_hotkey_special_keys_hint",
                "unregistered_key": "dialog_hotkey_unregistered",
            }.get(err, "dialog_hotkey_unregistered")
            QMessageBox.warning(self, self._t["dialog_missing_title"], self._t.get(msg_key, self._t["dialog_missing_info"]))
            return
        combo_lower = combo.lower()
        if any(hk.get("key_combo", "").lower() == combo_lower for hk in self.existing):
            QMessageBox.warning(self, self._t["dialog_dup_title"], self._t["dialog_dup_msg"])
            return
        lang_name = self._lang_combo.currentText()
        lang_code = "vi"
        for name, code in LANGUAGES:
            if name == lang_name:
                lang_code = code
                break
        mode = MODE_REPLACE if self._replace_rb.isChecked() else MODE_POPUP
        if self._edit:
            self.config.update_hotkey(
                self._edit["id"],
                key_combo=combo,
                target_language_code=lang_code,
                target_language_name=lang_name,
                mode=mode,
            )
        else:
            self.config.add_hotkey(combo, lang_code, lang_name, mode)
        self._stop_detect()
        self.accept()

    def closeEvent(self, event):
        self._stop_detect()
        super().closeEvent(event)
