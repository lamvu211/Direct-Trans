"""
tray.py - System tray icon with menu using pystray.
Runs on a background thread alongside Tkinter without thread conflicts or blocking.
"""

import os
import sys
import logging
import pystray
from PIL import Image, ImageDraw, ImageFont

TRAY_STRINGS = {
    'vi': {'settings': '⚙ Cài đặt', 'quit': '❌ Thoát', 'enable': 'Bật', 'disable': 'Tắt'},
    'en': {'settings': '⚙ Settings', 'quit': '❌ Quit', 'enable': 'Enable', 'disable': 'Disable'},
    'ko': {'settings': '⚙ 설정', 'quit': '❌ 종료', 'enable': '활성화', 'disable': '비활성화'},
    'zh': {'settings': '⚙ 设置', 'quit': '❌ 退出', 'enable': '启用', 'disable': '禁用'},
    'ja': {'settings': '⚙ 設定', 'quit': '❌ 終了', 'enable': '有効', 'disable': '無効'},
}

class TrayIcon:
    def __init__(self, on_settings, on_toggle, on_quit, config=None, is_enabled=None):
        """
        on_settings: callback to open Settings window (will be run on main thread via root.after)
        on_toggle: callback to toggle translation on/off
        on_quit: callback to quit the app
        is_enabled: callable that returns current enabled state
        """
        self.on_settings = on_settings
        self.on_toggle = on_toggle
        self.on_quit = on_quit
        self.is_enabled = is_enabled or (lambda: True)
        self.icon = None
        self.config = config

        # Load or create image
        image = self._load_icon_image()

        # Build icon
        self.icon = pystray.Icon(
            "DirectTrans",
            image,
            "DirectTrans",
            menu=self._build_menu()
        )

    def _get_strings(self) -> dict:
        """Get tray menu strings based on current UI language from config."""
        lang = self.config.data.get('ui_language', 'vi') if self.config else 'vi'
        return TRAY_STRINGS.get(lang, TRAY_STRINGS['vi'])

    def _get_icon_path(self) -> str:
        """Get the path to the icon file."""
        if getattr(sys, 'frozen', False):
            base = sys._MEIPASS
            png_path = os.path.join(base, 'assets', 'logo-direct-trans.png')
            if os.path.exists(png_path):
                return png_path
            return os.path.join(base, 'assets', 'icon.ico')
        else:
            base = os.path.dirname(os.path.abspath(__file__))
            png_path = os.path.join(base, 'assets', 'logo-direct-trans.png')
            if os.path.exists(png_path):
                return png_path
            return os.path.join(base, 'assets', 'icon.ico')

    def _load_icon_image(self) -> Image.Image:
        icon_path = self._get_icon_path()
        if os.path.exists(icon_path):
            try:
                logging.info(f"Loading system tray icon from: {icon_path}")
                return Image.open(icon_path)
            except Exception as e:
                logging.error(f"Failed to load icon from path: {e}")
        
        # Fallback to default self-drawn icon if path does not exist or fails to load
        return self._create_default_icon()

    def _create_default_icon(self) -> Image.Image:
        """Create a default icon (letters 'DT' on a blue background)."""
        logging.info("Creating default self-drawn system tray icon.")
        img = Image.new('RGBA', (64, 64), '#cc785c')
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("segoeui.ttf", 28)
        except Exception:
            try:
                font = ImageFont.truetype("arial.ttf", 28)
            except Exception:
                font = ImageFont.load_default()

        text = "DT"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (64 - text_w) // 2
        y = (64 - text_h) // 2 - 2
        draw.text((x, y), text, fill='white', font=font)
        return img

    def _build_menu(self):
        return pystray.Menu(
            pystray.MenuItem(
                lambda item: self._get_strings()['settings'],
                lambda icon, item: self.on_settings(),
                default=True
            ),
            pystray.MenuItem(
                lambda item: self._get_strings()['disable'] if self.is_enabled() else self._get_strings()['enable'],
                lambda icon, item: self._toggle()
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                lambda item: self._get_strings()['quit'],
                lambda icon, item: self.on_quit()
            )
        )

    def _toggle(self):
        """Toggle enabled state and update menu."""
        self.on_toggle()
        if self.icon:
            self.icon.update_menu()

    def run(self):
        """Run the tray icon. This blocks, so it should be run in a separate thread."""
        logging.info("pystray tray icon thread starting...")
        try:
            self.icon.run()
        except Exception as e:
            logging.error(f"Error in pystray run: {e}")

    def stop(self):
        """Stop the tray icon."""
        if self.icon:
            try:
                self.icon.stop()
                logging.info("pystray tray icon stopped.")
            except Exception as e:
                logging.error(f"Error stopping pystray icon: {e}")
