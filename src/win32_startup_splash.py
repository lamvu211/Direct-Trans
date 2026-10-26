"""Native Win32 loading window on a background thread (no Qt/tk). For packaged exe startup."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
import threading

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

WS_POPUP = 0x80000000
WS_VISIBLE = 0x10000000
WS_EX_TOPMOST = 0x00000008
WS_EX_TOOLWINDOW = 0x00000080

HWND_TOPMOST = wintypes.HWND(-1)
SWP_NOSIZE = 0x0001
SWP_SHOWWINDOW = 0x0040
SPI_GETWORKAREA = 0x0030
ERROR_CLASS_ALREADY_EXISTS = 1410

GRADIENT_FILL_RECT_H = 0x00000000
TRANSPARENT = 1
DT_CENTER = 0x00000001
DT_SINGLELINE = 0x00000020
FW_SEMIBOLD = 600
PS_SOLID = 0

_WIN_W = 400
_WIN_H = 140
_PAD_X = 24
_BAR_TOP = 52
_BAR_H = 24
_BAR_INSET = 3


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
    if msg == WM_CLOSE:
        user32.DestroyWindow(hwnd)
        return 0
    if msg == WM_DESTROY:
        user32.PostQuitMessage(0)
        return 0
    return user32.DefWindowProcW(hwnd, msg, wparam, lparam)


class Win32StartupSplash:
    """LOADING… + monochrome gradient bar + percent; +10% every second."""

    _CLASS_NAME = "DirectTransStartupSplash"

    def __init__(self) -> None:
        self._hwnd: int | None = None
        self._percent = 0
        self._closed = False
        self._ready = threading.Event()
        self._thread: threading.Thread | None = None
        self._font = None

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
        hwnd = self._hwnd
        if hwnd:
            user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)

    def _on_create(self, hwnd: int) -> None:
        self._hwnd = hwnd
        self._font = gdi32.CreateFontW(
            -15,
            0,
            0,
            0,
            FW_SEMIBOLD,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            "Segoe UI",
        )
        user32.SetTimer(hwnd, 1, 1000, None)
        self._center(hwnd)
        self._ready.set()

    def _on_timer(self) -> None:
        if self._closed or not self._hwnd:
            return
        if self._percent < 100:
            self._percent = min(100, self._percent + 10)
            user32.InvalidateRect(self._hwnd, None, False)

    def _draw_centered_text(self, hdc, text: str, top: int, height: int, width: int) -> None:
        gdi32.SetBkMode(hdc, TRANSPARENT)
        gdi32.SetTextColor(hdc, 0x00000000)
        if self._font:
            old_font = gdi32.SelectObject(hdc, self._font)
        rc = RECT(0, top, width, top + height)
        user32.DrawTextW(hdc, text, -1, ctypes.byref(rc), DT_CENTER | DT_SINGLELINE)
        if self._font:
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

            white = gdi32.CreateSolidBrush(0x00FFFFFF)
            user32.FillRect(hdc, ctypes.byref(client), white)
            gdi32.DeleteObject(white)

            self._draw_centered_text(hdc, "LOADING...", 14, 28, w)

            bar_left = _PAD_X
            bar_right = w - _PAD_X
            bar_w = bar_right - bar_left
            outer = RECT(bar_left, _BAR_TOP, bar_right, _BAR_TOP + _BAR_H)
            frame_pen = gdi32.CreatePen(PS_SOLID, 2, 0x00000000)
            old_pen = gdi32.SelectObject(hdc, frame_pen)
            null_brush = gdi32.GetStockObject(5)
            old_brush = gdi32.SelectObject(hdc, null_brush)
            gdi32.Rectangle(hdc, outer.left, outer.top, outer.right, outer.bottom)

            inner_l = bar_left + _BAR_INSET
            inner_t = _BAR_TOP + _BAR_INSET
            inner_r = bar_right - _BAR_INSET
            inner_b = _BAR_TOP + _BAR_H - _BAR_INSET
            inner_w = inner_r - inner_l
            inner_h = inner_b - inner_t
            inner = RECT(inner_l, inner_t, inner_r, inner_b)
            user32.FillRect(hdc, ctypes.byref(inner), gdi32.GetStockObject(0))  # WHITE_BRUSH

            fill_w = max(0, int(inner_w * self._percent / 100))
            if fill_w > 0:
                verts = (TRIVERTEX * 2)(
                    TRIVERTEX(inner_l, inner_t, _c16(0), _c16(0), _c16(0), 0x0000),
                    TRIVERTEX(inner_l + fill_w, inner_b, _c16(120), _c16(120), _c16(120), 0x0000),
                )
                mesh = GRADIENT_RECT(0, 1)
                msimg32.GradientFill(hdc, verts, 2, ctypes.byref(mesh), 1, GRADIENT_FILL_RECT_H)

            gdi32.SelectObject(hdc, old_brush)
            gdi32.SelectObject(hdc, old_pen)
            gdi32.DeleteObject(frame_pen)

            self._draw_centered_text(hdc, f"{self._percent}%", _BAR_TOP + _BAR_H + 12, 26, w)
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

        hwnd = user32.CreateWindowExW(
            WS_EX_TOPMOST | WS_EX_TOOLWINDOW,
            self._CLASS_NAME,
            "DirectTrans",
            WS_POPUP | WS_VISIBLE,
            0,
            0,
            _WIN_W,
            _WIN_H,
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
