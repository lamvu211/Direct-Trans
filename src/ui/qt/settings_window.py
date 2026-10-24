"""All-in-one Settings window (PySide6)."""

from __future__ import annotations

import logging
import os
import sys
import webbrowser

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from constants import APP_VERSION, DEFAULT_PROVIDER
from font_mapper import FontMapper
from ui.i18n import TRANSLATIONS, PROVIDERS, theme_label_for
from ui.qt.api_section import ApiSection
from ui.qt.hotkey_section import HotkeySection
from ui.qt.theme import DEFAULT_THEME_ID, THEME_IDS, label_for, qss_for
from ui.qt.widgets import (
    SETTINGS_FIELD_H_SPACING,
    SETTINGS_FIELD_LABEL_WIDTH,
    apply_control_height,
    apply_premium_app,
    card,
    fit_combo_to_contents,
    logo_label,
)


class QtSettingsWindow(QWidget):
    """Production settings UI — responsive scrollable layout, theme dropdown."""

    def __init__(self, config, on_save_callback, on_close_callback=None, hotkey_manager=None):
        super().__init__()
        self.config = config
        self.on_save_callback = on_save_callback
        self.on_close_callback = on_close_callback
        self.hotkey_manager = hotkey_manager
        self.current_lang = self.config.data.get("ui_language", "vi")

        self.setObjectName("root")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._prov_card_lbl: QLabel | None = None
        self._api_card_lbl: QLabel | None = None
        self._opt_card_lbl: QLabel | None = None
        self._hk_card_lbl: QLabel | None = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(self._build_header())
        outer.addWidget(self._build_body(), 1)
        self.update_window_height()

        theme_id = self.config.get_ui_theme()
        self.set_theme(theme_id)
        self.update_ui_language(self.current_lang)

        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "icon.ico"
        )
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def update_window_height(self) -> None:
        from ui.dpi_util import scaled_size
        w, _ = scaled_size(520, 100)
        count = len(self.config.get_hotkeys()) if self.config else 0
        visible_count = max(0, min(count, 5))
        has_more = count > 5
        base_h = 420
        row_h = 29
        more_h = 30 if has_more else 0
        total_h = base_h + (visible_count * row_h) + more_h
        _, h = scaled_size(520, total_h)
        self.setFixedSize(w, h)

    def _on_hotkeys_changed(self):
        self.update_window_height()
        if self.on_save_callback:
            self.on_save_callback()

    def _t(self):
        return TRANSLATIONS.get(self.current_lang, TRANSLATIONS["vi"])

    def _build_header(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("topBar")
        root = QVBoxLayout(bar)
        root.setContentsMargins(12, 8, 12, 6)
        root.setSpacing(4)

        row1 = QHBoxLayout()
        row1.addWidget(logo_label())
        title = QLabel("DirectTrans")
        title.setObjectName("brand")
        row1.addWidget(title)
        row1.addStretch()

        self._version_lbl = QLabel(f"v{APP_VERSION}")
        self._version_lbl.setObjectName("brandVersion")
        vfont = self._version_lbl.font()
        vfont.setItalic(True)
        self._version_lbl.setFont(vfont)
        self._version_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        row1.addWidget(self._version_lbl)
        row1.addSpacing(6)

        self._update_btn = QPushButton(self._t().get("update_btn_header", "Update"))
        self._update_btn.setObjectName("ghost")
        apply_control_height(self._update_btn)
        self._update_btn.clicked.connect(self._check_updates_now)
        row1.addWidget(self._update_btn)
        root.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(6)
        self._lang_combo = QComboBox()
        self._lang_combo.setObjectName("comboMini")
        apply_control_height(self._lang_combo)
        for label, code in (
            ("English", "en"),
            ("Tiếng Việt", "vi"),
            ("한국어", "ko"),
            ("中文", "zh"),
            ("日本語", "ja"),
        ):
            self._lang_combo.addItem(label, code)
        idx = self._lang_combo.findData(self.current_lang)
        if idx >= 0:
            self._lang_combo.setCurrentIndex(idx)
        self._lang_combo.currentIndexChanged.connect(self._on_ui_lang_changed)
        self._lang_combo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        row2.addWidget(self._lang_combo)

        self._theme_lbl = QLabel()
        self._theme_lbl.setObjectName("fieldLabel")
        row2.addWidget(self._theme_lbl)
        self._theme_combo = QComboBox()
        self._theme_combo.setObjectName("themeCombo")
        for tid in THEME_IDS:
            self._theme_combo.addItem(label_for(tid), tid)
        self._theme_combo.currentIndexChanged.connect(self._on_theme_combo_changed)
        apply_control_height(self._theme_combo)
        self._theme_combo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        row2.addWidget(self._theme_combo)
        row2.addStretch(1)

        self._manual_btn = QPushButton()
        self._manual_btn.setObjectName("ghost")
        apply_control_height(self._manual_btn)
        self._manual_btn.clicked.connect(self._open_manual)
        row2.addWidget(self._manual_btn)

        self._feedback_btn = QPushButton()
        self._feedback_btn.setObjectName("ghost")
        apply_control_height(self._feedback_btn)
        self._feedback_btn.clicked.connect(self._open_feedback)
        row2.addWidget(self._feedback_btn)

        root.addLayout(row2)
        self._fit_header_combos()
        self._sync_header_button_widths()
        self.update_window_height()
        return bar

    def _fit_header_combos(self) -> None:
        fit_combo_to_contents(self._lang_combo)
        fit_combo_to_contents(self._theme_combo)

    def _build_body(self) -> QWidget:
        host = QWidget()
        host.setObjectName("pageHost")
        host.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        lay = QVBoxLayout(host)
        lay.setContentsMargins(8, 4, 8, 8)
        lay.setSpacing(6)

        t0 = self._t()
        prov_card, prov_body = card(t0["provider_section"].upper())
        self._prov_card_lbl = prov_card.findChild(QLabel, "cardTitle")

        prov_grid = QGridLayout()
        prov_grid.setContentsMargins(0, 0, 0, 0)
        prov_grid.setHorizontalSpacing(SETTINGS_FIELD_H_SPACING)
        prov_grid.setVerticalSpacing(4)
        prov_grid.setColumnMinimumWidth(0, SETTINGS_FIELD_LABEL_WIDTH)
        prov_grid.setColumnStretch(0, 0)
        prov_grid.setColumnStretch(1, 1)
        self._provider_lbl = QLabel()
        self._provider_lbl.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self._provider_combo = QComboBox()
        self._provider_combo.setObjectName("combo")
        names = [p[0] for p in PROVIDERS]
        self._provider_map = {p[0]: p[1] for p in PROVIDERS}
        self._provider_rev = {p[1]: p[0] for p in PROVIDERS}
        self._provider_combo.addItems(names)
        cur = self.config.get_provider()
        self._provider_combo.setCurrentText(self._provider_rev.get(cur, names[0]))
        self._provider_combo.currentTextChanged.connect(self._on_provider_changed)
        apply_control_height(self._provider_combo)
        prov_grid.addWidget(self._provider_lbl, 0, 0)
        prov_grid.addWidget(self._provider_combo, 0, 1, 1, 1)
        self._provider_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        prov_body.addLayout(prov_grid)
        lay.addWidget(prov_card)

        self.api_section = ApiSection(
            self.config, self.on_save_callback, lambda: self.current_lang
        )
        api_card, api_body = card(
            t0["api_section"].upper(),
            icon="🔑",
            header_right=self.api_section.toolbar(),
        )
        self._api_card_lbl = api_card.findChild(QLabel, "cardTitle")
        api_body.addWidget(self.api_section)
        lay.addWidget(api_card)

        self._hk_add_btn = QPushButton()
        self._hk_add_btn.setObjectName("ctaSmall")
        apply_control_height(self._hk_add_btn)
        self.hotkey_section = HotkeySection(
            self.config,
            self._on_hotkeys_changed,
            self.hotkey_manager,
            lambda: self.current_lang,
            external_add_btn=self._hk_add_btn,
        )
        hk_card, hk_body = card(
            t0["hotkey_section"].upper(),
            icon="🖥️",
            header_right=self._hk_add_btn,
        )
        self._hk_card_lbl = hk_card.findChild(QLabel, "cardTitle")
        hk_body.addWidget(self.hotkey_section)
        lay.addWidget(hk_card)

        opt_card, opt_body = card(t0["options_section"].upper())
        self._opt_card_lbl = opt_card.findChild(QLabel, "cardTitle")
        self._autostart_cb = QCheckBox()
        self._autostart_cb.setObjectName("optionCheck")
        self._autostart_cb.setChecked(self.config.is_auto_start())
        self._autostart_cb.toggled.connect(self._on_autostart)
        opt_body.addWidget(self._autostart_cb)
        lay.addWidget(opt_card)
        lay.addStretch(1)

        self._sync_form_layout()
        return host

    def _sync_form_layout(self) -> None:
        self.api_section.sync_form_layout(self._provider_lbl)

    def _sync_header_button_widths(self) -> None:
        if not hasattr(self, "_feedback_btn") or not hasattr(self, "_update_btn"):
            return
        w = max(self._feedback_btn.sizeHint().width(), 92)
        self._feedback_btn.setMinimumWidth(w)
        self._update_btn.setMinimumWidth(w)

    def _check_updates_now(self):
        from updater import check_for_updates_in_background

        def on_finish(status, val):
            t = self._t()
            if status == "up_to_date":
                msg = t.get("status_up_to_date", "Bạn đang dùng bản mới nhất v{}").format(val)
                self._update_btn.setText("✓ " + t.get("update_btn_header", "Cập nhật"))
                self._update_btn.setToolTip(msg)
                from ui.qt.dispatch import schedule_ms
                schedule_ms(2500, lambda: (
                    self._update_btn.setText(self._t().get("update_btn_header", "Cập nhật")),
                    self._update_btn.setToolTip(self._t().get("update_tip", "Kiểm tra cập nhật")),
                ))

        check_for_updates_in_background(None, self.config, force=True, on_finish=on_finish)

    def _on_provider_changed(self, name: str):
        key = self._provider_map.get(name, DEFAULT_PROVIDER)
        self.config.data["translation_provider"] = key
        self.config.save()
        self.api_section.set_provider(key)
        if self.on_save_callback:
            self.on_save_callback()

    def _on_autostart(self, checked: bool):
        if not self.config.set_auto_start(checked):
            self._autostart_cb.blockSignals(True)
            self._autostart_cb.setChecked(not checked)
            self._autostart_cb.blockSignals(False)
            return
        if self.on_save_callback:
            self.on_save_callback()

    def _on_ui_lang_changed(self, index: int):
        code = self._lang_combo.itemData(index)
        if code:
            self.update_ui_language(code)
            self.config.data["ui_language"] = code
            self.config.save()

    def _on_theme_combo_changed(self, index: int):
        tid = self._theme_combo.itemData(index)
        if tid and tid != self.config.get_ui_theme():
            self.set_theme(tid)
            self.config.set_ui_theme(tid)

    def set_theme(self, theme_id: str) -> None:
        if theme_id not in THEME_IDS:
            theme_id = DEFAULT_THEME_ID
        self.setStyleSheet(qss_for(theme_id))
        self._fit_header_combos()
        idx = self._theme_combo.findData(theme_id)
        if idx >= 0 and self._theme_combo.currentIndex() != idx:
            self._theme_combo.blockSignals(True)
            self._theme_combo.setCurrentIndex(idx)
            self._theme_combo.blockSignals(False)

    def _open_manual(self):
        if getattr(sys, "frozen", False):
            base = sys._MEIPASS
            manual_path = os.path.join(base, "assets", "user_manual.html")
        else:
            base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            manual_path = os.path.join(base, "assets", "user_manual.html")
        if os.path.exists(manual_path):
            try:
                os.startfile(manual_path)
            except Exception:
                webbrowser.open("file:///" + manual_path.replace("\\", "/"))
        else:
            webbrowser.open("https://github.com/lamvu211/Direct-Trans")

    def _open_feedback(self):
        from feedback_util import open_feedback_mail
        open_feedback_mail()

    def update_ui_language(self, lang_code: str):
        self.current_lang = lang_code
        t = TRANSLATIONS.get(lang_code, TRANSLATIONS["vi"])
        font_family = FontMapper.get_font(lang_code)
        font = QApplication.font()
        font.setFamily(font_family)
        self.setFont(font)

        self.setWindowTitle(t.get("app_settings_title", "Settings"))
        self._theme_lbl.setText(t.get("theme_label", "Theme"))

        self._manual_btn.setText(t.get("manual_btn", "Manual"))
        self._manual_btn.setToolTip(t.get("manual_tip", "Mở hướng dẫn sử dụng"))
        self._manual_btn.setAccessibleName(t.get("manual_tip", "Mở hướng dẫn sử dụng"))

        self._feedback_btn.setText(t.get("feedback_btn", "Feedback"))
        self._feedback_btn.setToolTip(t.get("feedback_tip", "Gửi phản hồi / báo lỗi"))
        self._feedback_btn.setAccessibleName(t.get("feedback_tip", "Gửi phản hồi / báo lỗi"))

        self._update_btn.setText(t.get("update_btn_header", "Update"))
        self._update_btn.setToolTip(t.get("update_tip", "Kiểm tra cập nhật mới"))
        self._update_btn.setAccessibleName(t.get("update_tip", "Kiểm tra cập nhật mới"))

        self._autostart_cb.setText(t.get("autostart_label", "Start with Windows"))
        self._provider_lbl.setText(t.get("provider_label", "Provider"))

        if self._prov_card_lbl:
            self._prov_card_lbl.setText(t["provider_section"].upper())
        if self._api_card_lbl:
            self._api_card_lbl.setText(t["api_section"].upper())
        if self._opt_card_lbl:
            self._opt_card_lbl.setText(t["options_section"].upper())
        if self._hk_card_lbl:
            self._hk_card_lbl.setText(t["hotkey_section"].upper())

        for i, tid in enumerate(THEME_IDS):
            self._theme_combo.setItemText(i, theme_label_for(lang_code, tid))
        self._fit_header_combos()

        self.api_section.update_ui_language(lang_code, font_family)
        self.hotkey_section.update_ui_language(lang_code, font_family)
        self._sync_form_layout()
        self._sync_header_button_widths()

    def showEvent(self, event):
        super().showEvent(event)
        self._fit_header_combos()
        self._sync_form_layout()

    def restore_and_focus(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def changeEvent(self, event):
        if event.type() == event.Type.WindowStateChange and self.isMinimized():
            logging.info("Settings minimized — hide to tray.")
            self.hide()
        super().changeEvent(event)

    def closeEvent(self, event: QCloseEvent):
        event.ignore()
        self.hide()
        logging.info("Settings closed — hide to tray.")


def ensure_qt_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
        apply_premium_app(app)
        from ui.qt.dispatch import set_qt_application
        set_qt_application(app)
    return app
