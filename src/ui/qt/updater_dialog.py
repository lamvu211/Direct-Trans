"""Qt update notification dialog."""

from __future__ import annotations

import os
import webbrowser

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

from constants import APP_VERSION, GITHUB_RELEASES_URL
from ui.qt.theme import apply_theme
from ui.qt.widgets import apply_control_height


def show_update_dialog(config, latest_tag: str, _release_name: str = "") -> None:
    ui_lang = config.data.get("ui_language", "vi")
    strings = {
        "vi": {
            "title": "Cập nhật mới",
            "message": f"Phiên bản {latest_tag} đã sẵn sàng!\nBạn đang dùng v{APP_VERSION}.",
            "update_btn": "🌐 Tải về từ GitHub",
            "snooze_btn": "⏰ Nhắc lại sau (1 ngày)",
            "skip_btn": "⏭ Bỏ qua (nhắc sau 1 tuần)",
        },
        "en": {
            "title": "Update Available",
            "message": f"Version {latest_tag} is available!\nYou are using v{APP_VERSION}.",
            "update_btn": "🌐 Download from GitHub",
            "snooze_btn": "⏰ Remind me later (1 day)",
            "skip_btn": "⏭ Skip (remind in 1 week)",
        },
        "ko": {
            "title": "업데이트 가능",
            "message": f"{latest_tag} 버전을 사용할 수 있습니다!\n현재 v{APP_VERSION}을 사용 중입니다.",
            "update_btn": "🌐 GitHub에서 다운로드",
            "snooze_btn": "⏰ 나중에 알림 (1일)",
            "skip_btn": "⏭ 건너뛰기 (1주 후)",
        },
        "zh": {
            "title": "有新版本",
            "message": f"版本 {latest_tag} 已就绪！\n当前使用 v{APP_VERSION}。",
            "update_btn": "🌐 从 GitHub 下载",
            "snooze_btn": "⏰ 稍后提醒 (1 天)",
            "skip_btn": "⏭ 跳过 (一周后提醒)",
        },
        "ja": {
            "title": "アップデート可能",
            "message": f"バージョン {latest_tag} が利用可能です！\n現在 v{APP_VERSION} を使用中です。",
            "update_btn": "🌐 GitHub からダウンロード",
            "snooze_btn": "⏰ 後で通知 (1 日後)",
            "skip_btn": "⏭ スキップ (1 週間後)",
        },
    }
    s = strings.get(ui_lang, strings["en"])

    dialog = QDialog()
    dialog.setObjectName("root")
    dialog.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    theme_id = config.get_ui_theme()
    apply_theme(dialog, theme_id)
    dialog.setWindowTitle(s["title"])
    dialog.setModal(True)
    dialog.setMinimumWidth(360)

    icon_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "icon.ico"
    )
    if os.path.exists(icon_path):
        dialog.setWindowIcon(QIcon(icon_path))

    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(10)

    msg_lbl = QLabel(s["message"])
    msg_lbl.setObjectName("tagline")
    msg_lbl.setWordWrap(True)
    layout.addWidget(msg_lbl)

    def on_update():
        webbrowser.open(GITHUB_RELEASES_URL)
        dialog.accept()

    def on_snooze():
        config.snooze_update(days=1)
        dialog.accept()

    def on_skip():
        config.skip_version(latest_tag, days=7)
        dialog.accept()

    for idx, (text, slot) in enumerate(((s["update_btn"], on_update), (s["snooze_btn"], on_snooze), (s["skip_btn"], on_skip))):
        btn = QPushButton(text)
        btn.setObjectName("cta" if idx == 0 else "ghost")
        apply_control_height(btn, 28)
        btn.clicked.connect(slot)
        layout.addWidget(btn)

    dialog.exec()
