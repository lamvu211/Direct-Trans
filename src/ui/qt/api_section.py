"""API keys / models section (Qt port of ApiConfigTab)."""

from __future__ import annotations

import re
import threading
import webbrowser

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from constants import (
    PROVIDER_GEMINI,
    PROVIDER_GROQ,
    PROVIDER_MISTRAL,
    PROVIDER_GOOGLE_FREE,
)
from ui.i18n import TRANSLATIONS
from ui.qt.dispatch import run_on_main, schedule_ms
from ui.qt.widgets import (
    SETTINGS_FIELD_H_SPACING,
    SETTINGS_FIELD_INDENT,
    SETTINGS_FIELD_LABEL_WIDTH,
    apply_control_height,
)

MISTRAL_MODEL_ALLOWLIST = ("codestral-latest", "ministral-8b-latest")
_LABEL_COL = 0
_FIELD_COL = 1
_FIELD_SPAN = 1


def _make_clear_icon(size: int = 16) -> QIcon:
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(QColor("#a1a1aa"), 1.8)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    pad = 4
    p.drawLine(pad, pad, size - pad, size - pad)
    p.drawLine(size - pad, pad, pad, size - pad)
    p.end()
    return QIcon(pm)


class ApiSection(QWidget):
    def __init__(self, config, on_save_callback, get_current_lang, parent=None):
        super().__init__(parent)
        self.config = config
        self.on_save_callback = on_save_callback
        self.get_current_lang = get_current_lang
        self._panels: dict[str, QWidget] = {}
        self._model_combos: dict[str, QComboBox] = {}
        self._status_labels: dict[str, QLabel] = {}
        self._key_entries: dict[str, QLineEdit] = {}
        self._model_labels: dict[str, QLabel] = {}
        self._key_labels: dict[str, QLabel] = {}
        self._link_btns: dict[str, QPushButton] = {}
        self._fetch_btns: dict[str, QPushButton] = {}
        self._test_btns: dict[str, QPushButton] = {}
        self._save_btns: dict[str, QPushButton] = {}

        self._google_note = QLabel()
        self._google_note.setObjectName("fieldLabel")
        self.setMinimumHeight(68)
        self._stack = QStackedWidget()
        from PySide6.QtWidgets import QSizePolicy
        self._stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._toolbar = self._build_toolbar()

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._stack)

        self._stack.addWidget(self._google_note)
        for provider, link in (
            (PROVIDER_GEMINI, "https://aistudio.google.com/app/apikey"),
            (PROVIDER_GROQ, "https://console.groq.com/keys"),
            (PROVIDER_MISTRAL, "https://admin.mistral.ai/organization/api-keys"),
        ):
            self._panels[provider] = self._build_provider_panel(provider, link)
            self._stack.addWidget(self._panels[provider])
        self.set_provider(self.config.get_provider())
        self.update_ui_language(self.get_current_lang())

    def toolbar(self) -> QWidget:
        return self._toolbar

    def sync_form_layout(self, provider_label: QLabel | None = None) -> int:
        """Align label column with provider + model fields."""
        col_w = SETTINGS_FIELD_LABEL_WIDTH
        if provider_label is not None:
            col_w = max(col_w, provider_label.sizeHint().width())
        for provider in self._panels:
            col_w = max(col_w, self._model_labels[provider].sizeHint().width())
            col_w = max(col_w, self._key_labels[provider].sizeHint().width())
        for panel in self._panels.values():
            grid = panel.layout()
            if isinstance(grid, QGridLayout):
                grid.setColumnMinimumWidth(_LABEL_COL, col_w)
        if provider_label is not None:
            provider_label.setFixedWidth(col_w)
        return col_w + SETTINGS_FIELD_H_SPACING

    def _t(self):
        return TRANSLATIONS.get(self.get_current_lang(), TRANSLATIONS["vi"])

    def set_provider(self, provider_key: str):
        if provider_key == PROVIDER_GOOGLE_FREE:
            self.setMinimumHeight(32)
            self._stack.setCurrentWidget(self._google_note)
        elif provider_key in self._panels:
            self.setMinimumHeight(68)
            self._stack.setCurrentWidget(self._panels[provider_key])
        self._toolbar.setVisible(provider_key != PROVIDER_GOOGLE_FREE)
        if provider_key in self._panels:
            self._sync_toolbar_status_from(self._status_labels[provider_key])

    def _build_toolbar(self) -> QWidget:
        host = QWidget()
        lay = QHBoxLayout(host)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        t = self._t()
        btn_fetch = QPushButton(t["load_models"])
        btn_fetch.setObjectName("ghost")
        btn_test = QPushButton(t["test_btn"])
        btn_test.setObjectName("ghost")
        btn_save = QPushButton(t["save_btn"])
        btn_save.setObjectName("cta")
        for b in (btn_fetch, btn_test, btn_save):
            apply_control_height(b)
        status = QLabel("")
        status.setObjectName("apiStatus")
        lay.addWidget(status)
        lay.addWidget(btn_fetch)
        lay.addWidget(btn_test)
        lay.addWidget(btn_save)
        self._toolbar_fetch = btn_fetch
        self._toolbar_test = btn_test
        self._toolbar_save = btn_save
        self._toolbar_status = status
        btn_fetch.clicked.connect(self._toolbar_fetch_clicked)
        btn_test.clicked.connect(self._toolbar_test_clicked)
        btn_save.clicked.connect(self._toolbar_save_clicked)
        return host

    def _toolbar_fetch_clicked(self):
        p = self._active_provider()
        if not p:
            return
        entry = self._key_entries[p]
        self._fetch_models(
            p,
            entry.text().strip(),
            self._model_combos[p],
            self._toolbar_fetch,
            self._toolbar_save,
            self._toolbar_test,
            self._status_labels[p],
        )

    def _toolbar_test_clicked(self):
        p = self._active_provider()
        if not p:
            return
        entry = self._key_entries[p]
        self._test_key(
            p,
            entry.text().strip(),
            self._status_labels[p],
            self._model_combos[p],
            self._toolbar_fetch,
            self._toolbar_save,
            self._toolbar_test,
        )

    def _toolbar_save_clicked(self):
        p = self._active_provider()
        if not p:
            return
        entry = self._key_entries[p]
        self._quick_save(p, entry.text().strip(), self._status_labels[p])

    def _active_provider(self) -> str | None:
        w = self._stack.currentWidget()
        for key, panel in self._panels.items():
            if panel is w:
                return key
        return None

    def _sync_toolbar_status_from(self, panel_status: QLabel):
        self._toolbar_status.setText(panel_status.text())
        kind = panel_status.property("statusKind")
        self._toolbar_status.setProperty("statusKind", kind or "")
        self._restyle_status(self._toolbar_status)

    def _set_status(self, label: QLabel, text: str, kind: str | None = None):
        label.setText(text)
        label.setProperty("statusKind", kind or "")
        self._restyle_status(label)
        if label in self._status_labels.values():
            self._sync_toolbar_status_from(label)

    def _restyle_status(self, label: QLabel):
        label.style().unpolish(label)
        label.style().polish(label)
        label.update()

    def _placeholder_combo_texts(self) -> set[str]:
        t = self._t()
        return {
            "",
            t.get("fetching_models", "Fetching..."),
            t.get("load_models_failed", "Load Failed"),
            "Fetching...",
            "Load Failed",
            "Tải thất bại",
            "Đang tải...",
        }

    def _build_provider_panel(self, provider: str, api_link: str) -> QWidget:
        w = QWidget()
        from PySide6.QtWidgets import QSizePolicy
        w.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        w.setMinimumHeight(68)
        g = QGridLayout(w)
        g.setContentsMargins(0, 0, 0, 0)
        g.setHorizontalSpacing(SETTINGS_FIELD_H_SPACING)
        g.setVerticalSpacing(4)
        g.setColumnMinimumWidth(_LABEL_COL, SETTINGS_FIELD_LABEL_WIDTH)
        g.setColumnStretch(_LABEL_COL, 0)
        g.setColumnStretch(_FIELD_COL, 1)

        t = self._t()
        lbl_model = QLabel(t["model_label"])
        lbl_model.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        g.addWidget(lbl_model, 0, _LABEL_COL)
        self._model_labels[provider] = lbl_model

        model_combo = QComboBox()
        model_combo.setObjectName("combo")
        from PySide6.QtWidgets import QSizePolicy
        model_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        apply_control_height(model_combo)
        current = getattr(self.config, f"get_{provider}_model")()
        model_combo.addItem(current)
        model_combo.setEditable(False)
        g.addWidget(model_combo, 0, _FIELD_COL, 1, _FIELD_SPAN)
        self._model_combos[provider] = model_combo

        key_lbl = QLabel(t["api_label"])
        key_lbl.setObjectName("fieldLabel")
        key_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        g.addWidget(key_lbl, 1, _LABEL_COL)
        self._key_labels[provider] = key_lbl

        entry = QLineEdit()
        entry.setEchoMode(QLineEdit.EchoMode.Password)
        entry.setObjectName("line")
        from PySide6.QtWidgets import QSizePolicy
        entry.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        apply_control_height(entry)
        entry.setText(self.config.get_api_key(provider))
        entry.setAccessibleName(f"{provider} API key input")
        clr = QAction(_make_clear_icon(), "✕", entry)
        clr.setToolTip(t.get("clear_key_tip", "Xóa nội dung ô nhập"))
        clr.triggered.connect(entry.clear)
        entry.addAction(clr, QLineEdit.ActionPosition.TrailingPosition)
        clr.setVisible(bool(entry.text()))
        entry.textChanged.connect(lambda txt, a=clr: a.setVisible(bool(txt)))

        link = QPushButton(t["api_link"])
        link.setObjectName("ghost")
        apply_control_height(link)
        link.clicked.connect(lambda: webbrowser.open(api_link))
        self._link_btns[provider] = link

        key_row = QHBoxLayout()
        key_row.setSpacing(6)
        key_row.addWidget(entry, 1)
        key_row.addWidget(link)
        g.addLayout(key_row, 1, _FIELD_COL, 1, _FIELD_SPAN)
        self._key_entries[provider] = entry

        status = QLabel("")
        status.setObjectName("apiStatus")
        status.hide()
        self._status_labels[provider] = status

        btn_fetch = QPushButton()
        btn_fetch.hide()
        btn_test = QPushButton()
        btn_test.hide()
        btn_save = QPushButton()
        btn_save.hide()
        self._fetch_btns[provider] = btn_fetch
        self._test_btns[provider] = btn_test
        self._save_btns[provider] = btn_save

        model_combo.currentTextChanged.connect(
            lambda text, p=provider: getattr(self.config, f"set_{p}_model")(text)
            if text and text not in self._placeholder_combo_texts()
            else None
        )

        return w

    def _quick_save(self, provider: str, key: str, status: QLabel):
        self.config.set_api_key(provider, key)
        t = self._t()
        self._set_status(status, t["save_success"], None)
        schedule_ms(1500, lambda: self._set_status(status, "", None))
        if self.on_save_callback:
            self.on_save_callback()

    def _is_alive(self) -> bool:
        return self.window() is not None

    def _fetch_models(
        self, provider, api_key, combo, btn_fetch, btn_save, btn_test, status
    ):
        t = self._t()
        if not api_key:
            return
        self.config.set_api_key(provider, api_key)

        preserve = combo.currentText()
        if preserve in self._placeholder_combo_texts():
            preserve = getattr(self.config, f"get_{provider}_model")()

        def set_ui(enabled: bool):
            for b in (btn_fetch, btn_save, btn_test):
                b.setEnabled(enabled)
            combo.setEnabled(enabled)

        failed_text = t.get("load_models_failed", "Load Failed")
        self._set_status(status, t.get("fetching_models", "Fetching..."), None)
        run_on_main(lambda: set_ui(False))

        def fetch():
            import requests

            models = []
            try:
                if provider == PROVIDER_GEMINI:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
                    resp = requests.get(url, timeout=10)
                    if resp.status_code == 200:
                        models = [
                            m["name"].replace("models/", "")
                            for m in resp.json().get("models", [])
                            if "generateContent" in m.get("supportedGenerationMethods", [])
                            and self._valid_model(provider, m["name"])
                        ]
                elif provider == PROVIDER_GROQ:
                    url = "https://api.groq.com/openai/v1/models"
                    resp = requests.get(
                        url,
                        headers={"Authorization": f"Bearer {api_key}", "User-Agent": "Mozilla/5.0"},
                        timeout=10,
                    )
                    if resp.status_code == 200:
                        models = [m["id"] for m in resp.json().get("data", []) if self._valid_model(provider, m["id"])]
                elif provider == PROVIDER_MISTRAL:
                    url = "https://api.mistral.ai/v1/models"
                    resp = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
                    if resp.status_code == 200:
                        available = {m["id"] for m in resp.json().get("data", [])}
                        models = [mid for mid in MISTRAL_MODEL_ALLOWLIST if mid in available]

                def done():
                    if not self._is_alive():
                        return
                    if models:
                        combo.blockSignals(True)
                        combo.clear()
                        combo.addItems(models)
                        pick = preserve if preserve in models else getattr(
                            self.config, f"get_{provider}_model")()
                        if pick not in models:
                            pick = models[0]
                        combo.setCurrentText(pick)
                        getattr(self.config, f"set_{provider}_model")(pick)
                        combo.blockSignals(False)
                        self._set_status(status, "", None)
                    else:
                        self._set_status(status, failed_text, "fail")
                    set_ui(True)

                run_on_main(done)
            except Exception:
                run_on_main(lambda: (self._set_status(status, failed_text, "fail"), set_ui(True)))

        threading.Thread(target=fetch, daemon=True).start()

    def _valid_model(self, provider: str, model_name: str) -> bool:
        name_lower = model_name.lower()
        blacklist = [
            "embed", "vision", "audio", "tts", "whisper", "moderation",
            "coder", "math", "bison", "learnlm", "code", "ocr", "devstral",
            "voxtral", "magistral", "ministral", "pixtral", "robotics",
            "research", "antigravity", "lyria", "banana", "guard", "image",
            "vibe", "tiny", "small",
        ]
        if provider == PROVIDER_MISTRAL:
            blacklist.append("open")
        whitelist = ["gemini", "gemma", "llama", "mistral", "mixtral", "qwen", "deepseek", "gpt"]
        clutter = ["preview", "experimental", "001", "002", "customtools"]
        if not any(wl in name_lower for wl in whitelist):
            return False
        for kw in blacklist:
            if kw in name_lower:
                return False
        if re.search(r"-\d{4}$", name_lower) and "mistral" in name_lower:
            return False
        for kw in clutter:
            if kw in name_lower:
                return False
        return True

    def _test_key(self, provider, key, status, combo, btn_fetch, btn_save, btn_test):
        t_dict = self._t()
        if not key:
            self._set_status(status, t_dict["save_empty"], "fail")
            return
        self._set_status(status, t_dict["test_running"], None)
        for b in (btn_fetch, btn_save, btn_test):
            b.setEnabled(False)
        combo.setEnabled(False)

        def _finish_ui(message: str, kind: str | None) -> None:
            if not self._is_alive():
                return
            self._set_status(status, message, kind)
            combo.setEnabled(True)
            for b in (btn_fetch, btn_save, btn_test):
                b.setEnabled(True)

        def run_test():
            from translator import GeminiTranslator, GroqTranslator, MistralTranslator

            model = combo.currentText()
            if model in self._placeholder_combo_texts():
                model = getattr(self.config, f"get_{provider}_model")()
            try:
                res = None
                if provider == PROVIDER_GEMINI:
                    res = GeminiTranslator().translate("Hi", "Vietnamese", "vi", api_key=key, model=model)
                elif provider == PROVIDER_GROQ:
                    res = GroqTranslator().translate("Hi", "Vietnamese", "vi", api_key=key, model=model)
                elif provider == PROVIDER_MISTRAL:
                    res = MistralTranslator().translate("Hi", "Vietnamese", "vi", api_key=key, model=model)
                if res:
                    self.config.set_api_key(provider, key)
                    run_on_main(lambda: _finish_ui(t_dict["test_pass"], "pass"))
                else:
                    raise RuntimeError("empty")
            except Exception as e:
                err_msg = str(e)
                short_err = t_dict["test_fail"]
                if "429" in err_msg:
                    short_err = f"{t_dict['test_fail']} (429)"
                elif "403" in err_msg:
                    short_err = f"{t_dict['test_fail']} (403)"
                elif "400" in err_msg:
                    short_err = f"{t_dict['test_fail']} (400)"
                elif "connection" in err_msg.lower() or "timeout" in err_msg.lower():
                    short_err = t_dict["net_error"]
                run_on_main(lambda: _finish_ui(short_err, "fail"))

        threading.Thread(target=run_test, daemon=True).start()

    def update_ui_language(self, _lang_code: str, _font_family: str | None = None):
        t = self._t()
        self._google_note.setText(t["google_free_note"])
        self._toolbar_fetch.setText(t["load_models"])
        self._toolbar_test.setText(t["test_btn"])
        self._toolbar_save.setText(t["save_btn"])

        for p in self._panels:
            if p in self._model_labels:
                self._model_labels[p].setText(t["model_label"])
            if p in self._key_labels:
                self._key_labels[p].setText(t["api_label"])
            if p in self._link_btns:
                self._link_btns[p].setText(t["api_link"])

        prov = self._active_provider()
        if prov:
            self._sync_toolbar_status_from(self._status_labels[prov])
