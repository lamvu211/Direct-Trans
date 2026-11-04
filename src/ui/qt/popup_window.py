"""Translation result popup (Qt, themed)."""

from __future__ import annotations

import ctypes
import logging
import os
import sys
import threading
import time

from PySide6.QtCore import QEvent, Qt, QTimer, QPoint
from PySide6.QtGui import QCursor, QFont, QGuiApplication, QIcon, QColor, QIntValidator, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from font_mapper import FontMapper
from ui.i18n import provider_display_name, theme_label_for
from ui.qt.dispatch import run_on_main
from ui.qt.theme import qss_for, THEME_IDS
from ui.qt.widgets import apply_premium_app, fit_combo_to_contents

STATE_LOADING = "loading"
STATE_READY = "ready"
STATE_ERROR = "error"

POPUP_FONT_SIZE_MIN = 9
POPUP_FONT_SIZE_MAX = 36
POPUP_WINDOW_MIN_WIDTH = 690
POPUP_WINDOW_MIN_HEIGHT = 468
POPUP_WINDOW_DEFAULT_WIDTH = 810
POPUP_WINDOW_DEFAULT_HEIGHT = 546

WM_ENTERSIZEMOVE = 0x0231
WM_EXITSIZEMOVE = 0x0232
HTNOWHERE = 0
EVENT_SYSTEM_FOREGROUND = 0x0003
WINEVENT_OUTOFCONTEXT = 0x0000
WH_MOUSE_LL = 14
WM_LBUTTONDOWN = 0x0201
WM_RBUTTONDOWN = 0x0204
WM_MBUTTONDOWN = 0x0207
_OUTSIDE_CLICK_GRACE_SEC = 0.25

_foreground_watch_timer: QTimer | None = None
_win_event_hook_handle = None
_win_event_proc_ref = None
_mouse_hook_handle = None
_mouse_hook_proc_ref = None
_click_poll_timer: QTimer | None = None
_left_button_was_down = False
_OUR_PROCESS_ID = os.getpid()


class _POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class _MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt", _POINT),
        ("mouseData", ctypes.c_ulong),
        ("flags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.c_size_t),
    ]


def _hwnd_int(hwnd) -> int:
    if not hwnd:
        return 0
    try:
        return int(hwnd)
    except (TypeError, ValueError):
        return 0


def _hwnd_process_id(hwnd: int | None) -> int | None:
    if not hwnd:
        return None
    try:
        import win32gui
        import win32process

        hwnd = _hwnd_int(hwnd)
        if not hwnd or not win32gui.IsWindow(hwnd):
            return None
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return int(pid) if pid else None
    except Exception:
        return None


def _root_hwnd(hwnd: int | None) -> int | None:
    hwnd = _hwnd_int(hwnd)
    if not hwnd:
        return None
    try:
        import win32con
        import win32gui

        if not win32gui.IsWindow(hwnd):
            return None
        root = win32gui.GetAncestor(hwnd, win32con.GA_ROOT)
        return _hwnd_int(root) if root else None
    except Exception:
        return None


def _current_foreground_hwnd() -> int:
    try:
        import ctypes

        return _hwnd_int(ctypes.windll.user32.GetForegroundWindow())
    except Exception:
        return 0


def _any_popup_visible() -> bool:
    return any(p.window is not None and p.window.isVisible() for p in QtPopupWindow.open_popups)


def _any_popup_in_size_move() -> bool:
    return any(getattr(p, "_in_size_move", False) for p in QtPopupWindow.open_popups)


def _screen_lparam(screen_x: int, screen_y: int) -> int:
    x = int(screen_x) & 0xFFFF
    y = int(screen_y) & 0xFFFF
    return x | (y << 16)


def _popup_win32_hit_test(popup: "QtPopupWindow", screen_x: int, screen_y: int) -> int | None:
    win = popup.window
    if win is None or not win.isVisible():
        return None
    try:
        import win32con
        import win32gui

        hwnd = int(win.winId())
        return int(
            win32gui.SendMessage(
                hwnd,
                win32con.WM_NCHITTEST,
                0,
                _screen_lparam(screen_x, screen_y),
            )
        )
    except Exception:
        return None


def _screen_point_hits_popup_ui(screen_x: int, screen_y: int) -> bool:
    """Hit-test in Qt screen coords; includes Win32 resize/caption bands."""
    if _any_popup_in_size_move():
        return True
    pt = QPoint(int(screen_x), int(screen_y))
    for popup in QtPopupWindow.open_popups:
        win = popup.window
        if win is not None and win.isVisible():
            if win.frameGeometry().contains(pt):
                return True
            ht = _popup_win32_hit_test(popup, screen_x, screen_y)
            if ht is not None and ht != HTNOWHERE:
                return True
        picker = getattr(popup, "_color_picker", None)
        if picker is not None and picker.isVisible():
            if picker.frameGeometry().contains(pt):
                return True
    return False


def _apply_foreground_to_popups(fg_hwnd: int) -> None:
    if not fg_hwnd or not QtPopupWindow.open_popups or not _any_popup_visible():
        return
    for popup in list(QtPopupWindow.open_popups):
        if popup.window is None or not popup.window.isVisible():
            continue
        if popup._should_keep_visible_for_foreground(fg_hwnd):
            continue
        logging.info(
            "Hiding translation popup: foreground left source window (fg=%#x)",
            fg_hwnd,
        )
        popup.dismiss()


def _check_popup_foreground() -> None:
    if not QtPopupWindow.open_popups:
        _stop_foreground_watch()
        return
    if not _any_popup_visible():
        return
    _apply_foreground_to_popups(_current_foreground_hwnd())


def _handle_outside_click(screen_x: int, screen_y: int) -> None:
    if not _any_popup_visible():
        return
    if _any_popup_in_size_move():
        return
    now = time.monotonic()
    if _screen_point_hits_popup_ui(screen_x, screen_y):
        return
    for popup in list(QtPopupWindow.open_popups):
        if popup.window is None or not popup.window.isVisible():
            continue
        if now < getattr(popup, "_outside_click_grace_until", 0.0):
            continue
        logging.info("Hiding translation popup: click outside")
        popup.dismiss()
        return


def _poll_mouse_for_outside_click() -> None:
    global _left_button_was_down
    if not _any_popup_visible():
        _left_button_was_down = False
        return
    down = bool(ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000)
    if down and not _left_button_was_down:
        pos = QCursor.pos()
        _handle_outside_click(pos.x(), pos.y())
    _left_button_was_down = down


def _mouse_hook_callback(nCode, wParam, lParam):
    try:
        if nCode >= 0 and wParam in (WM_LBUTTONDOWN, WM_RBUTTONDOWN, WM_MBUTTONDOWN):
            info = ctypes.cast(lParam, ctypes.POINTER(_MSLLHOOKSTRUCT)).contents
            x, y = info.pt.x, info.pt.y
            run_on_main(lambda: _handle_outside_click(x, y))
    except Exception:
        logging.exception("Low-level mouse hook failed")
    try:
        import ctypes as _ctypes

        return _ctypes.windll.user32.CallNextHookEx(_mouse_hook_handle, nCode, wParam, lParam)
    except Exception:
        return 0


def _ensure_mouse_hook() -> None:
    global _mouse_hook_handle, _mouse_hook_proc_ref
    if _mouse_hook_handle:
        return
    try:
        from ctypes import wintypes

        LowLevelMouseProc = ctypes.WINFUNCTYPE(
            ctypes.c_long,
            ctypes.c_int,
            wintypes.WPARAM,
            wintypes.LPARAM,
        )
        _mouse_hook_proc_ref = LowLevelMouseProc(_mouse_hook_callback)
        _mouse_hook_handle = ctypes.windll.user32.SetWindowsHookExW(
            WH_MOUSE_LL,
            _mouse_hook_proc_ref,
            None,
            0,
        )
        if not _mouse_hook_handle:
            logging.warning("SetWindowsHookExW(WH_MOUSE_LL) failed")
    except Exception:
        logging.exception("Failed to install outside-click mouse hook")


def _win_event_callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
    try:
        fg = _hwnd_int(hwnd)
        if fg:
            run_on_main(lambda h=fg: _apply_foreground_to_popups(h))
    except Exception:
        logging.exception("WinEvent foreground callback failed")


def _ensure_win_event_hook() -> None:
    global _win_event_hook_handle, _win_event_proc_ref
    if _win_event_hook_handle:
        return
    try:
        import ctypes
        from ctypes import wintypes

        WinEventProc = ctypes.WINFUNCTYPE(
            None,
            wintypes.HANDLE,
            wintypes.DWORD,
            wintypes.HWND,
            wintypes.LONG,
            wintypes.LONG,
            wintypes.DWORD,
            wintypes.DWORD,
        )
        _win_event_proc_ref = WinEventProc(_win_event_callback)
        _win_event_hook_handle = ctypes.windll.user32.SetWinEventHook(
            EVENT_SYSTEM_FOREGROUND,
            EVENT_SYSTEM_FOREGROUND,
            None,
            _win_event_proc_ref,
            0,
            0,
            WINEVENT_OUTOFCONTEXT,
        )
        if not _win_event_hook_handle:
            logging.warning("SetWinEventHook(EVENT_SYSTEM_FOREGROUND) failed; timer fallback only")
    except Exception:
        logging.exception("Failed to install foreground WinEvent hook")


def _start_foreground_watch() -> None:
    global _foreground_watch_timer, _click_poll_timer
    _ensure_win_event_hook()
    _ensure_mouse_hook()
    app = QApplication.instance()
    if app is None:
        return
    if _foreground_watch_timer is None:
        _foreground_watch_timer = QTimer(app)
        _foreground_watch_timer.setInterval(400)
        _foreground_watch_timer.timeout.connect(_check_popup_foreground)
    _foreground_watch_timer.start()
    if _click_poll_timer is None:
        _click_poll_timer = QTimer(app)
        _click_poll_timer.setInterval(50)
        _click_poll_timer.timeout.connect(_poll_mouse_for_outside_click)
    _click_poll_timer.start()


def _stop_foreground_watch() -> None:
    global _foreground_watch_timer, _win_event_hook_handle, _mouse_hook_handle, _click_poll_timer
    if _foreground_watch_timer is not None:
        _foreground_watch_timer.stop()
        _foreground_watch_timer = None
    if _click_poll_timer is not None:
        _click_poll_timer.stop()
        _click_poll_timer = None
    if _win_event_hook_handle:
        try:
            ctypes.windll.user32.UnhookWinEvent(_win_event_hook_handle)
        except Exception:
            logging.exception("UnhookWinEvent failed")
        _win_event_hook_handle = None
    if _mouse_hook_handle:
        try:
            ctypes.windll.user32.UnhookWindowsHookEx(_mouse_hook_handle)
        except Exception:
            logging.exception("UnhookWindowsHookEx failed")
        _mouse_hook_handle = None


class _ThemedPopupWidget(QWidget):
    """Top-level popup widget with Esc key dismiss (after user clicks into the popup)."""

    def __init__(self, owner, parent=None, flags=Qt.WindowType.Widget):
        super().__init__(parent, flags)
        self.owner = owner

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            focus_target = obj if isinstance(obj, QWidget) else None
            self.owner.engage_popup_focus(focus_target)
        return False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            if self.owner.is_popup_focus_engaged():
                self.owner.close()
            event.accept()
            return
        super().keyPressEvent(event)

    def closeEvent(self, event):
        self.owner.close()
        event.accept()

    def nativeEvent(self, eventType, message):
        if eventType in (b"windows_generic_MSG", "windows_generic_MSG"):
            try:
                import ctypes.wintypes

                msg = ctypes.wintypes.MSG.from_address(int(message))
                if msg.message == WM_ENTERSIZEMOVE:
                    self.owner._in_size_move = True
                elif msg.message == WM_EXITSIZEMOVE:
                    self.owner._in_size_move = False
                    self.owner._save_popup_window_size()
            except Exception:
                logging.debug("nativeEvent size-move handling failed", exc_info=True)
        return super().nativeEvent(eventType, message)


def _install_popup_click_focus(root: QWidget) -> None:
    """Any click on the popup engages keyboard focus without stealing it on initial show."""
    if not isinstance(root, _ThemedPopupWidget):
        return
    root.installEventFilter(root)
    for child in root.findChildren(QWidget):
        child.installEventFilter(root)


def _make_swatch_icon(color_hex: str, size: int = 14) -> QIcon:
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor(color_hex))
    p.setPen(QPen(QColor(255, 255, 255, 90), 1))
    p.drawRoundedRect(0, 0, size - 1, size - 1, 3, 3)
    p.end()
    return QIcon(pm)

class QtPopupWindow:
    open_popups: list[QtPopupWindow] = []

    TRANSLATIONS = {
        "vi": {
            "title_prefix": "Dịch",
            "replace_btn": "✏ Thay thế",
            "copy_btn": "📋 Copy",
            "copied_feedback": "✓ Đã copy!",
            "loading": "⏳ Đang dịch...",
            "replace_error": "Lỗi thay thế:",
            "status_by": "Dịch bởi {provider}",
            "font_style_label": "Màu & cỡ chữ",
            "color_picker_tip": "Chọn màu chữ kết quả dịch",
            "font_decrease_tip": "Giảm cỡ chữ",
            "font_increase_tip": "Tăng cỡ chữ",
            "font_size_edit_tip": "Nhấp để gõ cỡ chữ (9–36)",
        },
        "en": {
            "title_prefix": "Translate",
            "replace_btn": "✏ Replace",
            "copy_btn": "📋 Copy",
            "copied_feedback": "✓ Copied!",
            "loading": "⏳ Translating...",
            "replace_error": "Replacement error:",
            "status_by": "Translated by {provider}",
            "font_style_label": "Font color & size",
            "color_picker_tip": "Choose result text color",
            "font_decrease_tip": "Decrease font size",
            "font_increase_tip": "Increase font size",
            "font_size_edit_tip": "Click to type font size (9–36)",
        },
        "ko": {
            "title_prefix": "번역",
            "replace_btn": "✏ 바꾸기",
            "copy_btn": "📋 복사",
            "copied_feedback": "✓ 복사됨!",
            "loading": "⏳ 번역 중...",
            "replace_error": "교체 오류:",
            "status_by": "{provider}로 번역됨",
            "font_style_label": "글자 색·크기",
            "color_picker_tip": "번역 결과 글자 색 선택",
            "font_decrease_tip": "글자 크기 줄이기",
            "font_increase_tip": "글자 크기 늘리기",
            "font_size_edit_tip": "클릭하여 글자 크기 입력 (9–36)",
        },
        "zh": {
            "title_prefix": "翻译",
            "replace_btn": "✏ 替换",
            "copy_btn": "📋 复制",
            "copied_feedback": "✓ 已复制!",
            "loading": "⏳ 正在翻译...",
            "replace_error": "替换错误:",
            "status_by": "由 {provider} 翻译",
            "font_style_label": "字体颜色与大小",
            "color_picker_tip": "选择译文文字颜色",
            "font_decrease_tip": "减小字号",
            "font_increase_tip": "增大字号",
            "font_size_edit_tip": "点击输入字号 (9–36)",
        },
        "ja": {
            "title_prefix": "翻訳",
            "replace_btn": "✏ 置換",
            "copy_btn": "📋 コピー",
            "copied_feedback": "✓ コピー完了!",
            "loading": "⏳ 翻訳中...",
            "replace_error": "置換エラー:",
            "status_by": "{provider} で翻訳",
            "font_style_label": "文字色とサイズ",
            "color_picker_tip": "翻訳結果の文字色を選択",
            "font_decrease_tip": "文字サイズを小さく",
            "font_increase_tip": "文字サイズを大きく",
            "font_size_edit_tip": "クリックしてサイズ入力 (9–36)",
        },
    }

    def __init__(self, root=None, config=None):
        if config is None and root is not None and hasattr(root, "data"):
            config = root
            root = None
        self.config = config
        self.window: QWidget | None = None
        self.text_widget: QTextEdit | None = None
        self.original_rtf = None
        self.original_text = None
        self.target_lang_code = None
        self.translated_text = None
        self.provider_key = None
        self.status_label: QLabel | None = None
        self.copy_btn: QPushButton | None = None
        self.replace_btn: QPushButton | None = None
        self.color_btn: QPushButton | None = None
        self.size_input: QLineEdit | None = None
        self._color_picker = None
        self._current_font_color = "#B1B9E5"
        self._current_font_size = 12
        self.original_hwnd = None
        self.clipboard_hints = None
        self.selection_state = None
        self._copy_reset_timer: QTimer | None = None
        self._state = STATE_READY
        self._popup_focus_engaged = False
        self._source_root_hwnd: int | None = None
        self._outside_click_grace_until = 0.0
        self._in_size_move = False

    def _ui_lang(self) -> str:
        return self.config.data.get("ui_language", "vi") if self.config else "vi"

    def _t(self):
        return self.TRANSLATIONS.get(self._ui_lang(), self.TRANSLATIONS["en"])

    def _ensure_app(self):
        if QApplication.instance() is None:
            app = QApplication([])
            apply_premium_app(app)

    def show(
        self,
        translated_text: str = None,
        loading: bool = False,
        source_lang: str = "",
        target_lang: str = "",
        original_rtf: bytes = None,
        target_lang_code: str = None,
        original_hwnd: int = None,
        original_text: str = None,
        provider_key: str = None,
        clipboard_hints: dict | None = None,
        selection_state: dict | None = None,
    ):
        self._ensure_app()
        self._popup_focus_engaged = False
        self._outside_click_grace_until = time.monotonic() + _OUTSIDE_CLICK_GRACE_SEC
        self.original_rtf = original_rtf
        self.original_text = original_text
        self.clipboard_hints = clipboard_hints
        self.selection_state = selection_state
        self.target_lang_code = target_lang_code
        self.translated_text = translated_text
        self.provider_key = provider_key
        self.original_hwnd = original_hwnd
        self._source_root_hwnd = _root_hwnd(original_hwnd) if original_hwnd else None

        for p in list(QtPopupWindow.open_popups):
            p.close()
        QtPopupWindow.open_popups.clear()

        t = self._t()
        ui_lang = self._ui_lang()
        ui_font_family = FontMapper.get_font(ui_lang)
        content_font_family = FontMapper.get_font(target_lang_code if target_lang_code else "en")

        win = _ThemedPopupWidget(
            self,
            None,
            Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint,
        )
        win.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        win.setObjectName("popupRoot")
        win.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        theme_id = self.config.get_ui_theme() if self.config else "midnight_gold"
        win.setStyleSheet(qss_for(theme_id))

        target_lang_display = self._localized_target_name(ui_lang, target_lang, target_lang_code)
        title = f"{t['title_prefix']} → {target_lang_display}" if target_lang_display else "DirectTrans"
        win.setWindowTitle(title)
        win.setMinimumSize(POPUP_WINDOW_MIN_WIDTH, POPUP_WINDOW_MIN_HEIGHT)

        self._apply_popup_window_size(win)

        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "icon.ico"
        )
        if os.path.exists(icon_path):
            win.setWindowIcon(QIcon(icon_path))

        main = QVBoxLayout(win)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        popup_style = self.config.get_popup_style(theme_id) if self.config else {"color": "#B1B9E5", "size": 12}
        self._current_font_color = popup_style.get("color", "#B1B9E5")
        self._current_font_size = popup_style.get("size", 12)

        header_container = QWidget()
        header_container.setObjectName("popupHeaderContainer")
        header = QHBoxLayout(header_container)
        header.setContentsMargins(12, 10, 12, 10)
        header.setSpacing(6)
        self.status_label = QLabel("")
        self.status_label.setObjectName("statusBy")
        self.status_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        header.addWidget(self.status_label, 1)
        header.addStretch(1)

        # 1. ComboBox chọn Theme (nằm bên trái "Font color & size", độ cao 24px)
        from PySide6.QtWidgets import QSizePolicy
        self.theme_combo = QComboBox()
        self.theme_combo.setObjectName("themeCombo")
        self.theme_combo.setFixedHeight(24)
        self.theme_combo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        for tid in THEME_IDS:
            self.theme_combo.addItem(theme_label_for(ui_lang, tid), tid)
        cur_t_idx = self.theme_combo.findData(theme_id)
        if cur_t_idx >= 0:
            self.theme_combo.setCurrentIndex(cur_t_idx)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        if hasattr(self.theme_combo, "view") and self.theme_combo.view():
            self.theme_combo.view().setTextElideMode(Qt.TextElideMode.ElideNone)
        fit_combo_to_contents(self.theme_combo, padding=28)
        header.addWidget(self.theme_combo, 0, Qt.AlignmentFlag.AlignVCenter)
        header.addSpacing(6)

        # 2. Cụm Font color & size: text có màu giống Translated by... (statusBy)
        style_lbl = QLabel(t.get("font_style_label", "Font color & size"))
        style_lbl.setObjectName("statusBy")
        header.addWidget(style_lbl, 0, Qt.AlignmentFlag.AlignVCenter)
        header.addSpacing(4)

        # Box chọn màu (90x24px)
        clean_hex = self._current_font_color.lstrip("#")
        self.color_btn = QPushButton(f"# {clean_hex}")
        self.color_btn.setObjectName("colorBtn")
        self.color_btn.setFixedSize(90, 30)
        self.color_btn.setIcon(_make_swatch_icon(self._current_font_color))
        self.color_btn.setToolTip(t.get("color_picker_tip", "Choose result text color"))
        self.color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.color_btn.clicked.connect(self._open_color_picker)
        header.addWidget(self.color_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        header.addSpacing(4)

        # Box font size (90x24px - bằng kích thước với box chọn màu)
        size_box = QFrame()
        size_box.setObjectName("fontSizeBox")
        size_box.setFixedSize(90, 30)
        size_lay = QHBoxLayout(size_box)
        size_lay.setContentsMargins(4, 0, 4, 0)
        size_lay.setSpacing(2)

        minus_btn = QPushButton("−")
        minus_btn.setObjectName("sizeBtn")
        minus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        minus_btn.setToolTip(t.get("font_decrease_tip", "Decrease font size"))
        minus_btn.clicked.connect(self._on_decrease_font_size)
        size_lay.addWidget(minus_btn, 0, Qt.AlignmentFlag.AlignVCenter)

        self.size_input = QLineEdit(str(self._current_font_size))
        self.size_input.setObjectName("sizeEdit")
        self.size_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.size_input.setFixedHeight(22)
        self.size_input.setValidator(
            QIntValidator(POPUP_FONT_SIZE_MIN, POPUP_FONT_SIZE_MAX, self.size_input)
        )
        self.size_input.setToolTip(t.get("font_size_edit_tip", "Click to type font size (9–36)"))
        self.size_input.setCursor(Qt.CursorShape.IBeamCursor)
        self.size_input.editingFinished.connect(self._on_font_size_edited)
        self.size_input.returnPressed.connect(self._on_font_size_edited)
        size_lay.addWidget(self.size_input, 1, Qt.AlignmentFlag.AlignVCenter)

        plus_btn = QPushButton("+")
        plus_btn.setObjectName("sizeBtn")
        plus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        plus_btn.setToolTip(t.get("font_increase_tip", "Increase font size"))
        plus_btn.clicked.connect(self._on_increase_font_size)
        size_lay.addWidget(plus_btn, 0, Qt.AlignmentFlag.AlignVCenter)

        header.addWidget(size_box, 0, Qt.AlignmentFlag.AlignVCenter)
        header.addSpacing(8)

        # 3. Actions: Replace & Copy (độ cao 24px)
        actions = QHBoxLayout()
        actions.setSpacing(6)
        if self.target_lang_code:
            self.replace_btn = QPushButton(t["replace_btn"])
            self.replace_btn.setObjectName("ctaSmall")
            self.replace_btn.setFixedHeight(24)
            self.replace_btn.setToolTip(t["replace_btn"])
            self.replace_btn.setAccessibleName(t["replace_btn"])
            self.replace_btn.clicked.connect(self._replace)
            actions.addWidget(self.replace_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        else:
            self.replace_btn = None

        self.copy_btn = QPushButton(t["copy_btn"])
        self.copy_btn.setObjectName("cta")
        self.copy_btn.setFixedHeight(24)
        self.copy_btn.setToolTip(t["copy_btn"])
        self.copy_btn.setAccessibleName(t["copy_btn"])
        self.copy_btn.clicked.connect(self._copy)
        actions.addWidget(self.copy_btn, 0, Qt.AlignmentFlag.AlignVCenter)

        header.addLayout(actions)
        main.addWidget(header_container)

        self.divider = QFrame()
        self.divider.setObjectName("popupDivider")
        self.divider.setFixedHeight(1)
        self.divider.setFrameShape(QFrame.Shape.HLine)
        self.divider.setFrameShadow(QFrame.Shadow.Plain)
        main.addWidget(self.divider)

        text_container = QWidget()
        text_container.setObjectName("popupTextContainer")
        text_lay = QVBoxLayout(text_container)
        text_lay.setContentsMargins(12, 10, 12, 10)
        text_lay.setSpacing(0)

        self.text_widget = QTextEdit()
        self.text_widget.setObjectName("popupText")
        self.text_widget.setFont(QFont(content_font_family, self._current_font_size))
        self.text_widget.setReadOnly(True)
        self.text_widget.setAccessibleName("Translation result")
        self.text_widget.setFrameShape(QFrame.Shape.NoFrame)
        self._apply_output_style(self._current_font_color, self._current_font_size, save=False)
        text_lay.addWidget(self.text_widget, 1)
        main.addWidget(text_container, 1)

        win.setFont(QFont(ui_font_family, 9))
        if loading:
            self._state = STATE_LOADING
            self.text_widget.setPlainText(t["loading"])
        elif translated_text:
            self._state = STATE_READY
            self.text_widget.setPlainText(translated_text)
        else:
            self._state = STATE_READY

        self._refresh_status_label(t)
        self._sync_action_buttons()
        self.window = win
        _install_popup_click_focus(win)
        QtPopupWindow.open_popups.append(self)
        win.show()
        self._center_on_work_area(win)
        QTimer.singleShot(0, lambda w=win: self._center_on_work_area(w))
        win.raise_()
        _start_foreground_watch()

    def is_popup_focus_engaged(self) -> bool:
        return self._popup_focus_engaged

    def engage_popup_focus(self, focus_widget: QWidget | None = None) -> None:
        """
        After the user clicks the popup, accept keyboard focus (font size, Esc).
        Initial show uses WA_ShowWithoutActivating so the source app keeps selection.
        """
        win = self.window
        if not win:
            return
        if not self._popup_focus_engaged:
            self._popup_focus_engaged = True
            win.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
            win.activateWindow()
        win.raise_()
        if (
            focus_widget is not None
            and focus_widget.focusPolicy() != Qt.FocusPolicy.NoFocus
            and not focus_widget.hasFocus()
        ):
            focus_widget.setFocus(Qt.FocusReason.MouseFocusReason)

    @staticmethod
    def _clamp_font_size(size: int) -> int:
        return max(POPUP_FONT_SIZE_MIN, min(POPUP_FONT_SIZE_MAX, size))

    def _apply_output_style(self, color_hex: str, font_size: int, save: bool = True):
        self._current_font_color = color_hex.upper()
        self._current_font_size = self._clamp_font_size(font_size)
        if self.text_widget:
            self.text_widget.setFont(QFont(self.text_widget.font().family(), self._current_font_size))
            self.text_widget.setStyleSheet(
                f"QTextEdit#popupText {{ color: {self._current_font_color}; font-size: {self._current_font_size}pt; border: none; background: transparent; padding: 4px 8px; }}"
            )
        if self.color_btn:
            clean = self._current_font_color.lstrip("#")
            self.color_btn.setIcon(_make_swatch_icon(self._current_font_color))
            self.color_btn.setText(f"# {clean}")
        if self.size_input:
            self.size_input.blockSignals(True)
            self.size_input.setText(str(self._current_font_size))
            self.size_input.blockSignals(False)

        if save and self.config:
            theme_id = self.config.get_ui_theme()
            self.config.set_popup_style(theme_id, color=self._current_font_color, size=self._current_font_size)

    def _on_decrease_font_size(self):
        new_size = self._clamp_font_size(self._current_font_size - 1)
        self._apply_output_style(self._current_font_color, new_size)

    def _on_increase_font_size(self):
        new_size = self._clamp_font_size(self._current_font_size + 1)
        self._apply_output_style(self._current_font_color, new_size)

    def _on_font_size_edited(self):
        if not self.size_input:
            return
        raw = self.size_input.text().strip()
        if not raw:
            self.size_input.setText(str(self._current_font_size))
            return
        try:
            value = int(raw)
        except ValueError:
            self.size_input.setText(str(self._current_font_size))
            return
        self._apply_output_style(self._current_font_color, value)

    def sync_theme_display(self, theme_id: str) -> None:
        """Refresh popup QSS, theme combo, and font defaults without writing config."""
        if not theme_id or not self.window:
            return
        self.window.setStyleSheet(qss_for(theme_id))
        if hasattr(self, "theme_combo") and self.theme_combo:
            idx = self.theme_combo.findData(theme_id)
            if idx >= 0 and self.theme_combo.currentIndex() != idx:
                self.theme_combo.blockSignals(True)
                self.theme_combo.setCurrentIndex(idx)
                self.theme_combo.blockSignals(False)
        popup_style = self.config.get_popup_style(theme_id) if self.config else {"color": "#B1B9E5", "size": 12}
        self._current_font_color = popup_style.get("color", "#B1B9E5")
        self._current_font_size = popup_style.get("size", 12)
        self._apply_output_style(self._current_font_color, self._current_font_size, save=False)
        if hasattr(self, "_color_picker") and self._color_picker:
            self._color_picker.close()
            self._color_picker = None

    def _on_theme_changed(self, index: int):
        if not hasattr(self, "theme_combo") or not self.theme_combo or not self.window:
            return
        theme_id = self.theme_combo.itemData(index)
        if not theme_id:
            return
        if self.config:
            self.config.set_ui_theme(theme_id)
        else:
            self.sync_theme_display(theme_id)

    def _open_color_picker(self):
        if not self.color_btn or not self.window:
            return
        theme_id = self.config.get_ui_theme() if self.config else "midnight_gold"
        if not hasattr(self, "_color_picker") or self._color_picker is None:
            from ui.qt.color_picker import ColorPickerPopup
            self._color_picker = ColorPickerPopup(self._current_font_color, parent=self.window, theme_id=theme_id)
            self._color_picker.colorSelected.connect(
                lambda hex_c: self._apply_output_style(hex_c, self._current_font_size)
            )
        self._color_picker.set_color(self._current_font_color)
        pos = self.color_btn.mapToGlobal(QPoint(0, self.color_btn.height() + 4))
        self._color_picker.move(pos)
        self._color_picker.show()

    def _localized_target_name(self, ui_lang: str, target_lang: str, target_lang_code: str | None) -> str:
        if not target_lang_code:
            return target_lang
        common_langs = {
            "vi": {"vi": "Tiếng Việt", "en": "Tiếng Anh", "ko": "Tiếng Hàn", "zh": "Tiếng Trung", "ja": "Tiếng Nhật"},
            "en": {"vi": "Vietnamese", "en": "English", "ko": "Korean", "zh": "Chinese", "ja": "Japanese"},
            "ko": {"vi": "베트남어", "en": "영어", "ko": "한국어", "zh": "중국어", "ja": "일본어"},
            "zh": {"vi": "越南语", "en": "英语", "ko": "韩语", "zh": "中文", "ja": "日语"},
            "ja": {"vi": "ベトナム語", "en": "英語", "ko": "韓国語", "zh": "中国語", "ja": "日本語"},
        }
        if ui_lang in common_langs and target_lang_code in common_langs[ui_lang]:
            return common_langs[ui_lang][target_lang_code]
        return target_lang

    def _screen_at_cursor(self):
        pos = QCursor.pos()
        return QGuiApplication.screenAt(pos) or QGuiApplication.primaryScreen()

    def _popup_dimensions(self, avail_w: int, avail_h: int) -> tuple[int, int]:
        popup_w = min(1020, max(720, int(avail_w * 0.45)))
        popup_h = min(740, max(507, int(avail_h * 0.50)))
        return popup_w, popup_h

    def _apply_popup_window_size(self, win: QWidget) -> None:
        """Use saved config size or default for this monitor."""
        saved = self.config.get_popup_window_size() if self.config else None
        if saved:
            win.resize(int(saved["width"]), int(saved["height"]))
            return
        screen = self._screen_at_cursor()
        if screen is None:
            win.resize(POPUP_WINDOW_DEFAULT_WIDTH, POPUP_WINDOW_DEFAULT_HEIGHT)
            return
        avail = screen.availableGeometry()
        popup_w, popup_h = self._popup_dimensions(avail.width(), avail.height())
        win.resize(popup_w, popup_h)

    def _save_popup_window_size(self) -> None:
        if not self.config or not self.window:
            return
        fg = self.window.frameGeometry()
        w, h = fg.width(), fg.height()
        if w < POPUP_WINDOW_MIN_WIDTH or h < POPUP_WINDOW_MIN_HEIGHT:
            w, h = self.window.width(), self.window.height()
        self.config.set_popup_window_size(w, h)

    def _place_on_monitor(self, win: QWidget):
        """Legacy hook; sizing handled in _apply_popup_window_size."""
        self._apply_popup_window_size(win)

    def _center_on_work_area(self, win: QWidget):
        """Center after show() so frameGeometry includes decorations and layout is applied."""
        screen = QGuiApplication.screenAt(win.frameGeometry().center()) or self._screen_at_cursor()
        if screen is None:
            return
        avail = screen.availableGeometry()
        fg = win.frameGeometry()
        fg.moveCenter(avail.center())
        x = max(avail.left(), min(fg.x(), avail.right() - fg.width() + 1))
        y = max(avail.top(), min(fg.y(), avail.bottom() - fg.height() + 1))
        win.move(x, y)

    def _is_alive(self) -> bool:
        return self.window is not None and self.window.isVisible()

    def _popup_ui_hwnds(self) -> list[int]:
        hwnds: list[int] = []
        if self.window is not None and self.window.isVisible():
            try:
                hwnds.append(_hwnd_int(self.window.winId()))
            except Exception:
                pass
        picker = getattr(self, "_color_picker", None)
        if picker is not None and picker.isVisible():
            try:
                hwnds.append(_hwnd_int(picker.winId()))
            except Exception:
                pass
        return hwnds

    def _should_keep_visible_for_foreground(self, fg_hwnd: int) -> bool:
        """Keep popup while user stays in DirectTrans or the same top-level source window."""
        fg_hwnd = _hwnd_int(fg_hwnd)
        if not fg_hwnd:
            return False
        fg_pid = _hwnd_process_id(fg_hwnd)
        if fg_pid is None:
            return False
        if fg_pid == _OUR_PROCESS_ID:
            return True

        source_root = self._source_root_hwnd
        if not source_root and self.original_hwnd:
            source_root = _root_hwnd(int(self.original_hwnd))
            self._source_root_hwnd = source_root
        if not source_root:
            return True

        orig = _hwnd_int(self.original_hwnd)
        if fg_hwnd == orig or fg_hwnd == source_root:
            return True
        fg_root = _root_hwnd(fg_hwnd)
        return bool(fg_root and fg_root == source_root)

    def _refresh_status_label(self, t=None):
        if not self.status_label:
            return
        t = t or self._t()
        if self.provider_key:
            name = provider_display_name(self.provider_key)
            self.status_label.setText(t["status_by"].format(provider=name))
        else:
            self.status_label.setText("")

    def _sync_action_buttons(self) -> None:
        can_copy = self._state == STATE_READY and bool(self.translated_text)
        can_replace = can_copy and bool(self.target_lang_code)
        if self.copy_btn:
            self.copy_btn.setEnabled(can_copy)
        if self.replace_btn:
            self.replace_btn.setEnabled(can_replace)

    def update_text(self, translated_text: str, provider_key: str = None):
        self.translated_text = translated_text
        self._state = STATE_READY
        if provider_key:
            self.provider_key = provider_key
        if not self.text_widget or not self.window:
            return
        self.text_widget.setPlainText(translated_text)
        self._refresh_status_label()
        self._sync_action_buttons()

    def show_error(self, error_msg: str):
        self.translated_text = None
        self._state = STATE_ERROR
        if not self.text_widget or not self.window:
            return
        self.text_widget.setPlainText(f"❌ {error_msg}")
        if self.status_label:
            self.status_label.setText("")
        self._sync_action_buttons()

    def _copy(self):
        if self._state != STATE_READY or not self.translated_text or not self.copy_btn:
            return
        t = self._t()
        QGuiApplication.clipboard().setText(self.translated_text)
        self.copy_btn.setText(t["copied_feedback"])
        if self._copy_reset_timer:
            self._copy_reset_timer.stop()
        parent = self.window or self.text_widget
        self._copy_reset_timer = QTimer(parent)
        self._copy_reset_timer.setSingleShot(True)
        self._copy_reset_timer.timeout.connect(lambda: self.copy_btn.setText(t["copy_btn"]))
        self._copy_reset_timer.start(1500)

    def _replace(self):
        if not self.translated_text or not self.target_lang_code:
            return
        from clipboard_util import ClipboardUtil

        import ctypes

        if self.original_hwnd:
            target_hwnd = self.original_hwnd
        else:
            try:
                target_hwnd = ctypes.windll.user32.GetForegroundWindow()
            except Exception:
                target_hwnd = None

        if self.window:
            self.window.hide()

        def perform_paste():
            time.sleep(0.08)
            try:
                paste_text = self.translated_text or ""
                ClipboardUtil.replace_selected_text(
                    paste_text,
                    self.original_rtf,
                    self.target_lang_code,
                    original_text=self.original_text,
                    target_hwnd=target_hwnd,
                    clipboard_hints=self.clipboard_hints,
                    selection_state=self.selection_state,
                )
            except Exception as e:
                logging.error("Error replacing text from popup: %s", e)
                t = self._t()

                def restore_and_error():
                    if self.window:
                        self.restore_visible()
                    self.show_error(f"{t['replace_error']} {e}")

                run_on_main(restore_and_error)
                return
            run_on_main(self.close)

        threading.Thread(target=perform_paste, daemon=True).start()

    def dismiss(self) -> None:
        """Hide popup when user clicks away or switches apps; next hotkey creates a new popup."""
        if getattr(self, "_color_picker", None):
            try:
                self._color_picker.close()
            except Exception:
                pass
            self._color_picker = None
        if self.window is not None:
            try:
                self.window.hide()
            except Exception:
                pass
        if not _any_popup_visible():
            _stop_foreground_watch()

    def close(self):
        if self in QtPopupWindow.open_popups:
            QtPopupWindow.open_popups.remove(self)
        if self.window:
            try:
                self.window.close()
                self.window.deleteLater()
            except Exception:
                pass
            self.window = None
        if not QtPopupWindow.open_popups:
            _stop_foreground_watch()

    def restore_visible(self) -> None:
        """Show hidden popup again (e.g. after failed Replace)."""
        if self.window is not None:
            self.window.show()
            self.window.raise_()
            _start_foreground_watch()
