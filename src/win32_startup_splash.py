"""Native Win32 loading window on a background thread (no Qt/tk). For packaged exe startup."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
import threading
import time

from ui.dpi_util import scale_logical_px, win32_scale_factor, win32_system_dpi

user32 = ctypes.WinDLL("user32", use_last_error=True)
gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
msimg32 = ctypes.WinDLL("msimg32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

LRESULT = ctypes.c_ssize_t
WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.DefWindowProcW.restype = LRESULT
gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
gdi32.SelectObject.restype = wintypes.HGDIOBJ
gdi32.CreateFontW.restype = wintypes.HFONT
gdi32.CreateSolidBrush.restype = wintypes.HBRUSH
gdi32.CreatePen.restype = wintypes.HPEN
gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
gdi32.GetStockObject.restype = wintypes.HGDIOBJ

WM_CREATE = 0x0001
WM_CLOSE = 0x0010
WM_DESTROY = 0x0002
WM_TIMER = 0x0113
WM_PAINT = 0x000F
WM_ERASEBKGND = 0x0014
WM_DPICHANGED = 0x02E0

WS_POPUP = 0x80000000
WS_VISIBLE = 0x10000000
WS_EX_TOPMOST = 0x00000008
WS_EX_TOOLWINDOW = 0x00000080

HWND_TOPMOST = wintypes.HWND(-1)
SWP_NOSIZE = 0x0001
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040
SPI_GETWORKAREA = 0x0030
ERROR_CLASS_ALREADY_EXISTS = 1410

GRADIENT_FILL_RECT_H = 0x00000000
TRANSPARENT = 1
DT_CENTER = 0x00000001
DT_SINGLELINE = 0x00000020
FW_SEMIBOLD = 600
FW_BOLD = 700
PS_SOLID = 0

_PROGRESS_STEP = 20
_PROGRESS_INTERVAL_MS = 1000

_WIN_W = 380
_WIN_H = 200
_BAR_W = 300
_BAR_TOP = 58
_BAR_H = 14
_BAR_INSET = 2

_CLR_BG = 0x00ECECEC
_CLR_TRACK = 0x00E2E2E2
_CLR_FILL_TOP = 0x00B0DDA8  # BGR: #A8DDB0
_CLR_FILL_BOTTOM = 0x008AC1A5  # BGR: #A5C18A
_CLR_TITLE = 0x003A3A3A
_CLR_SUB = 0x009A9A9A
_CLR_TOOLTIP_BG = 0x00F7F7F7
_CLR_TOOLTIP_BORDER = 0x00D8D8D8
_CLR_TOOLTIP_TEXT = 0x006E6E6E


class WNDCLASSEXW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.UINT),
        ("style", wintypes.UINT),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", wintypes.HINSTANCE),
        ("hIcon", wintypes.HICON),
        ("hCursor", wintypes.HCURSOR),
        ("hbrBackground", wintypes.HBRUSH),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
        ("hIconSm", wintypes.HICON),
    ]


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


user32.FillRect.argtypes = [wintypes.HDC, ctypes.POINTER(RECT), wintypes.HBRUSH]
user32.FillRect.restype = ctypes.c_int


class PAINTSTRUCT(ctypes.Structure):
    _fields_ = [
        ("hdc", wintypes.HDC),
        ("fErase", wintypes.BOOL),
        ("rcPaint", RECT),
        ("fRestore", wintypes.BOOL),
        ("fIncUpdate", wintypes.BOOL),
        ("rgbReserved", ctypes.c_byte * 32),
    ]


class TRIVERTEX(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_long),
        ("y", ctypes.c_long),
        ("Red", ctypes.c_ushort),
        ("Green", ctypes.c_ushort),
        ("Blue", ctypes.c_ushort),
        ("Alpha", ctypes.c_ushort),
    ]


class GRADIENT_RECT(ctypes.Structure):
    _fields_ = [
        ("UpperLeft", ctypes.c_ulong),
        ("LowerRight", ctypes.c_ulong),
    ]


_active: Win32StartupSplash | None = None
_class_registered = False


def _c16(channel: int) -> int:
    return max(0, min(255, channel)) * 256


@WNDPROC
def _window_proc(hwnd, msg, wparam, lparam):
    inst = _active
    if msg == WM_CREATE and inst is not None:
        inst._on_create(hwnd)
        return 0
    if msg == WM_ERASEBKGND:
        return 1
    if msg == WM_PAINT and inst is not None:
        inst._on_paint(hwnd)
        return 0
    if msg == WM_TIMER and inst is not None and wparam == 1:
        inst._on_timer()
        return 0
    if msg == WM_DPICHANGED and inst is not None:
        inst._on_dpichanged(hwnd, wparam, lparam)
        return 0
    if msg == WM_CLOSE:
        user32.DestroyWindow(hwnd)
        return 0
    if msg == WM_DESTROY:
        user32.PostQuitMessage(0)
        return 0
    return user32.DefWindowProcW(hwnd, msg, wparam, lparam)


class Win32StartupSplash:
    """Soft UI loading bar; starts at 20%, +20% every second."""

    _CLASS_NAME = "DirectTransStartupSplash"

    def __init__(self) -> None:
        self._hwnd: int | None = None
        self._percent = _PROGRESS_STEP
        self._closed = False
        self._ready = threading.Event()
        self._thread: threading.Thread | None = None
        self._font_title = None
        self._font_sub = None
        self._font_tip = None
        dpi = win32_system_dpi()
        self._dpi = dpi
        self._scale = win32_scale_factor(dpi)

    def _sx(self, logical: int) -> int:
        return max(1, int(logical * self._scale))

    def _sync_dpi(self, hwnd: int) -> None:
        try:
            self._dpi = int(user32.GetDpiForWindow(hwnd))
        except Exception:
            self._dpi = win32_system_dpi()
        self._scale = win32_scale_factor(self._dpi)

    def _destroy_fonts(self) -> None:
        for font in (self._font_title, self._font_sub, self._font_tip):
            if font:
                gdi32.DeleteObject(font)
        self._font_title = None
        self._font_sub = None
        self._font_tip = None

    def _create_fonts(self) -> None:
        self._destroy_fonts()
        self._font_title = gdi32.CreateFontW(
            -self._sx(16), 0, 0, 0, FW_BOLD, 0, 0, 0, 0, 0, 0, 0, 0, "Segoe UI"
        )
        self._font_sub = gdi32.CreateFontW(
            -self._sx(12), 0, 0, 0, FW_SEMIBOLD, 0, 0, 0, 0, 0, 0, 0, 0, "Segoe UI"
        )
        self._font_tip = gdi32.CreateFontW(
            -self._sx(12), 0, 0, 0, FW_SEMIBOLD, 0, 0, 0, 0, 0, 0, 0, 0, "Segoe UI"
        )

    def start(self) -> None:
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._thread_main, name="Win32StartupSplash", daemon=True)
        self._thread.start()
        self._ready.wait(timeout=10.0)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        import win32gui
        hwnd = self._hwnd
        if hwnd:
            try:
                win32gui.PostMessage(hwnd, WM_CLOSE, 0, 0)
            except Exception:
                pass
            return
        for _ in range(100):
            if self._hwnd:
                try:
                    win32gui.PostMessage(self._hwnd, WM_CLOSE, 0, 0)
                except Exception:
                    pass
                return
            time.sleep(0.02)

    def _on_create(self, hwnd: int) -> None:
        self._hwnd = hwnd
        if self._closed:
            user32.DestroyWindow(hwnd)
            self._hwnd = None
            self._ready.set()
            return
        self._sync_dpi(hwnd)
        self._create_fonts()
        user32.SetTimer(hwnd, 1, _PROGRESS_INTERVAL_MS, None)
        self._center(hwnd)
        user32.ShowWindow(hwnd, 5)  # SW_SHOW — window created hidden to avoid (0,0) hit-test flash
        self._ready.set()

    def _on_dpichanged(self, hwnd: int, wparam: int, lparam: int) -> None:
        dpi_x = wparam & 0xFFFF
        if dpi_x:
            self._dpi = dpi_x
            self._scale = win32_scale_factor(self._dpi)
        suggested = ctypes.cast(lparam, ctypes.POINTER(RECT)).contents
        user32.SetWindowPos(
            hwnd,
            None,
            suggested.left,
            suggested.top,
            suggested.right - suggested.left,
            suggested.bottom - suggested.top,
            SWP_NOZORDER | SWP_NOACTIVATE,
        )
        self._create_fonts()
        user32.InvalidateRect(hwnd, None, True)

    def _on_timer(self) -> None:
        if self._closed or not self._hwnd:
            return
        if self._percent < 100:
            self._percent = min(100, self._percent + _PROGRESS_STEP)
            user32.InvalidateRect(self._hwnd, None, False)

    def _draw_centered_text(
        self,
        hdc,
        text: str,
        top: int,
        height: int,
        width: int,
        color: int,
        font,
    ) -> None:
        gdi32.SetBkMode(hdc, TRANSPARENT)
        gdi32.SetTextColor(hdc, color)
        old_font = None
        if font:
            old_font = gdi32.SelectObject(hdc, font)
        rc = RECT(0, top, width, top + height)
        user32.DrawTextW(hdc, text, -1, ctypes.byref(rc), DT_CENTER | DT_SINGLELINE)
        if old_font:
            gdi32.SelectObject(hdc, old_font)

    def _fill_round_rect(self, hdc, left: int, top: int, right: int, bottom: int, color: int) -> None:
        corner = self._sx(_BAR_H)
        brush = gdi32.CreateSolidBrush(color)
        pen = gdi32.CreatePen(PS_SOLID, 1, color)
        old_brush = gdi32.SelectObject(hdc, brush)
        old_pen = gdi32.SelectObject(hdc, pen)
        gdi32.RoundRect(hdc, left, top, right, bottom, corner, corner)
        gdi32.SelectObject(hdc, old_brush)
        gdi32.SelectObject(hdc, old_pen)
        gdi32.DeleteObject(brush)
        gdi32.DeleteObject(pen)

    def _gradient_fill_round(
        self,
        hdc,
        left: int,
        top: int,
        right: int,
        bottom: int,
        top_color: int,
        bottom_color: int,
    ) -> None:
        if right <= left:
            return
        corner = self._sx(_BAR_H)
        rgn = gdi32.CreateRoundRectRgn(left, top, right, bottom, corner, corner)
        gdi32.SelectClipRgn(hdc, rgn)
        verts = (TRIVERTEX * 2)(
            TRIVERTEX(
                left,
                top,
                _c16((top_color >> 16) & 0xFF),
                _c16((top_color >> 8) & 0xFF),
                _c16(top_color & 0xFF),
                0x0000,
            ),
            TRIVERTEX(
                right,
                bottom,
                _c16((bottom_color >> 16) & 0xFF),
                _c16((bottom_color >> 8) & 0xFF),
                _c16(bottom_color & 0xFF),
                0x0000,
            ),
        )
        mesh = GRADIENT_RECT(0, 1)
        msimg32.GradientFill(hdc, verts, 2, ctypes.byref(mesh), 1, GRADIENT_FILL_RECT_H)
        gdi32.SelectClipRgn(hdc, None)
        gdi32.DeleteObject(rgn)

    def _draw_tooltip(self, hdc, anchor_x: int, bar_top: int, text: str, client_w: int) -> None:
        tip_w = self._sx(44)
        tip_h = self._sx(22)
        tip_y = bar_top - tip_h - self._sx(10)
        tip_x = max(self._sx(4), min(client_w - tip_w - self._sx(4), anchor_x - tip_w // 2))
        bubble = RECT(tip_x, tip_y, tip_x + tip_w, tip_y + tip_h)
        self._fill_round_rect(hdc, bubble.left, bubble.top, bubble.right, bubble.bottom, _CLR_TOOLTIP_BG)
        frame = gdi32.CreatePen(PS_SOLID, 1, _CLR_TOOLTIP_BORDER)
        old_pen = gdi32.SelectObject(hdc, frame)
        null_brush = gdi32.GetStockObject(5)
        old_brush = gdi32.SelectObject(hdc, null_brush)
        bubble_r = self._sx(12)
        gdi32.RoundRect(hdc, bubble.left, bubble.top, bubble.right, bubble.bottom, bubble_r, bubble_r)
        px = anchor_x
        py = bubble.bottom
        pts = (wintypes.POINT * 3)(
            wintypes.POINT(px - self._sx(5), py - 1),
            wintypes.POINT(px, py + self._sx(5)),
            wintypes.POINT(px + self._sx(5), py - 1),
        )
        tip_brush = gdi32.CreateSolidBrush(_CLR_TOOLTIP_BG)
        gdi32.SelectObject(hdc, tip_brush)
        gdi32.Polygon(hdc, pts, 3)
        gdi32.SelectObject(hdc, old_brush)
        gdi32.SelectObject(hdc, old_pen)
        gdi32.DeleteObject(frame)
        gdi32.DeleteObject(tip_brush)
        gdi32.SetBkMode(hdc, TRANSPARENT)
        gdi32.SetTextColor(hdc, _CLR_TOOLTIP_TEXT)
        if self._font_tip:
            old_font = gdi32.SelectObject(hdc, self._font_tip)
        tip_rc = RECT(tip_x, tip_y, tip_x + tip_w, tip_y + tip_h)
        user32.DrawTextW(hdc, text, -1, ctypes.byref(tip_rc), DT_CENTER | DT_SINGLELINE)
        if self._font_tip:
            gdi32.SelectObject(hdc, old_font)

    def _on_paint(self, hwnd: int) -> None:
        ps = PAINTSTRUCT()
        hdc = user32.BeginPaint(hwnd, ctypes.byref(ps))
        if not hdc:
            return
        try:
            client = RECT()
            user32.GetClientRect(hwnd, ctypes.byref(client))
            w = client.right - client.left

            bg = gdi32.CreateSolidBrush(_CLR_BG)
            user32.FillRect(hdc, ctypes.byref(client), bg)
            gdi32.DeleteObject(bg)

            bar_w = self._sx(_BAR_W)
            bar_top = self._sx(_BAR_TOP)
            bar_h = self._sx(_BAR_H)
            inset = self._sx(_BAR_INSET)
            bar_left = (w - bar_w) // 2
            bar_right = bar_left + bar_w
            track = RECT(bar_left, bar_top, bar_right, bar_top + bar_h)
            self._fill_round_rect(hdc, track.left, track.top, track.right, track.bottom, _CLR_TRACK)

            inner_l = bar_left + inset
            inner_t = bar_top + inset
            inner_r = bar_right - inset
            inner_b = bar_top + bar_h - inset
            inner_w = inner_r - inner_l
            fill_w = max(0, int(inner_w * self._percent / 100))
            if fill_w > 0:
                fill_r = inner_l + fill_w
                shadow = RECT(inner_l, inner_t + self._sx(2), fill_r, inner_b + self._sx(2))
                self._fill_round_rect(hdc, shadow.left, shadow.top, shadow.right, shadow.bottom, 0x00C8C8C8)
                self._gradient_fill_round(hdc, inner_l, inner_t, fill_r, inner_b, _CLR_FILL_TOP, _CLR_FILL_BOTTOM)
                self._draw_tooltip(hdc, fill_r, bar_top, f"{self._percent}%", w)

            self._draw_centered_text(
                hdc, "Loading", bar_top + bar_h + self._sx(28), self._sx(26), w, _CLR_TITLE, self._font_title
            )
            self._draw_centered_text(
                hdc,
                "Please Wait...",
                bar_top + bar_h + self._sx(52),
                self._sx(22),
                w,
                _CLR_SUB,
                self._font_sub,
            )
        finally:
            user32.EndPaint(hwnd, ctypes.byref(ps))

    def _center(self, hwnd: int) -> None:
        rect = RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        ww = rect.right - rect.left
        wh = rect.bottom - rect.top
        area = RECT()
        user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(area), 0)
        x = area.left + (area.right - area.left - ww) // 2
        y = area.top + (area.bottom - area.top - wh) // 2
        user32.SetWindowPos(hwnd, HWND_TOPMOST, x, y, 0, 0, SWP_NOSIZE | SWP_SHOWWINDOW)

    def _thread_main(self) -> None:
        global _active, _class_registered
        _active = self
        hinst = kernel32.GetModuleHandleW(None)

        if not _class_registered:
            wc = WNDCLASSEXW()
            wc.cbSize = ctypes.sizeof(WNDCLASSEXW)
            wc.lpfnWndProc = _window_proc
            wc.hInstance = hinst
            wc.hbrBackground = 0x00000005
            wc.lpszClassName = self._CLASS_NAME
            atom = user32.RegisterClassExW(ctypes.byref(wc))
            if atom == 0 and kernel32.GetLastError() != ERROR_CLASS_ALREADY_EXISTS:
                self._ready.set()
                return
            _class_registered = True

        win_w = scale_logical_px(_WIN_W, self._dpi)
        win_h = scale_logical_px(_WIN_H, self._dpi)
        hwnd = user32.CreateWindowExW(
            WS_EX_TOPMOST | WS_EX_TOOLWINDOW,
            self._CLASS_NAME,
            "DirectTrans",
            WS_POPUP,
            0,
            0,
            win_w,
            win_h,
            None,
            None,
            hinst,
            None,
        )
        if not hwnd:
            self._ready.set()
            return

        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        self._hwnd = None
        _active = None
