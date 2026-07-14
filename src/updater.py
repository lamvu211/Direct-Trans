"""
updater.py - Check for new versions via GitHub Releases API.
If a newer version is found, prompts the user and opens the browser to download.
"""

import logging
import time
import threading
import webbrowser
import requests

from constants import APP_VERSION, GITHUB_REPO, GITHUB_RELEASES_URL

GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


def _parse_version(tag: str) -> tuple:
    """Parse version tag like 'v1.0.9' or '1.0.9' into comparable tuple (1, 0, 9)."""
    tag = tag.lstrip('vV')
    parts = []
    for p in tag.split('.'):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def _fetch_latest_version() -> dict | None:
    """Fetch latest release info from GitHub API. Returns dict with 'tag' and 'name', or None."""
    try:
        resp = requests.get(GITHUB_API_URL, timeout=10, headers={
            'Accept': 'application/vnd.github.v3+json'
        })
        if resp.status_code == 200:
            data = resp.json()
            return {
                'tag': data.get('tag_name', ''),
                'name': data.get('name', ''),
                'body': data.get('body', ''),
            }
        logging.warning("GitHub API returned status %d", resp.status_code)
    except requests.RequestException as e:
        logging.warning("Failed to check for updates: %s", e)
    return None


def _should_check(config) -> bool:
    """Determine if we should check for updates based on snooze settings."""
    snooze_until = config.get_snooze_until()
    if snooze_until > 0 and time.time() < snooze_until:
        logging.info("Update check snoozed until %s", time.ctime(snooze_until))
        return False
    return True


def _show_update_dialog(root, config, latest_tag: str, release_name: str):
    """Show update notification dialog on the main Tkinter thread."""
    import tkinter as tk
    from tkinter import ttk

    ui_lang = config.data.get('ui_language', 'vi')

    strings = {
        'vi': {
            'title': 'Cập nhật mới',
            'message': f'Phiên bản {latest_tag} đã sẵn sàng!\nBạn đang dùng v{APP_VERSION}.',
            'update_btn': '🌐 Tải về từ GitHub',
            'snooze_btn': '⏰ Nhắc lại sau (7 ngày)',
            'skip_btn': '⏭ Bỏ qua phiên bản này',
        },
        'en': {
            'title': 'Update Available',
            'message': f'Version {latest_tag} is available!\nYou are using v{APP_VERSION}.',
            'update_btn': '🌐 Download from GitHub',
            'snooze_btn': '⏰ Remind me later (7 days)',
            'skip_btn': '⏭ Skip this version',
        },
        'ko': {
            'title': '업데이트 가능',
            'message': f'{latest_tag} 버전을 사용할 수 있습니다!\n현재 v{APP_VERSION}을 사용 중입니다.',
            'update_btn': '🌐 GitHub에서 다운로드',
            'snooze_btn': '⏰ 나중에 알림 (7일)',
            'skip_btn': '⏭ 이 버전 건너뛰기',
        },
        'zh': {
            'title': '有新版本',
            'message': f'版本 {latest_tag} 已就绪！\n当前使用 v{APP_VERSION}。',
            'update_btn': '🌐 从 GitHub 下载',
            'snooze_btn': '⏰ 稍后提醒 (7 天)',
            'skip_btn': '⏭ 跳过此版本',
        },
        'ja': {
            'title': 'アップデート可能',
            'message': f'バージョン {latest_tag} が利用可能です！\n現在 v{APP_VERSION} を使用中です。',
            'update_btn': '🌐 GitHub からダウンロード',
            'snooze_btn': '⏰ 後で通知 (7 日後)',
            'skip_btn': '⏭ このバージョンをスキップ',
        },
    }
    s = strings.get(ui_lang, strings['en'])

    dialog = tk.Toplevel(root)
    dialog.title(s['title'])
    dialog.resizable(False, False)
    dialog.grab_set()

    # Center on screen
    dialog.update_idletasks()
    w, h = 380, 180
    x = (dialog.winfo_screenwidth() - w) // 2
    y = (dialog.winfo_screenheight() - h) // 2
    dialog.geometry(f"{w}x{h}+{x}+{y}")

    msg_label = tk.Label(dialog, text=s['message'], font=("Segoe UI", 11), justify='center')
    msg_label.pack(pady=(18, 12))

    btn_frame = tk.Frame(dialog)
    btn_frame.pack(fill='x', padx=20, pady=(0, 12))

    def on_update():
        webbrowser.open(GITHUB_RELEASES_URL)
        dialog.destroy()

    def on_snooze():
        config.snooze_update(days=7)
        dialog.destroy()

    def on_skip():
        config.skip_version(latest_tag)
        dialog.destroy()

    ttk.Button(btn_frame, text=s['update_btn'], command=on_update).pack(fill='x', pady=2)
    ttk.Button(btn_frame, text=s['snooze_btn'], command=on_snooze).pack(fill='x', pady=2)
    ttk.Button(btn_frame, text=s['skip_btn'], command=on_skip).pack(fill='x', pady=2)

    # Handle window close (X button) same as snooze
    dialog.protocol("WM_DELETE_WINDOW", on_snooze)


def check_for_updates_in_background(root, config):
    """Run update check on a background thread. Shows dialog on main thread if update found."""
    def _check():
        if not _should_check(config):
            return

        release = _fetch_latest_version()
        if not release:
            return

        latest_tag = release['tag']
        if not latest_tag:
            return

        current = _parse_version(APP_VERSION)
        latest = _parse_version(latest_tag)

        if latest <= current:
            logging.info("App is up to date (current=%s, latest=%s)", APP_VERSION, latest_tag)
            return

        if latest_tag in config.get_skipped_versions():
            logging.info("Version %s was skipped by user", latest_tag)
            return

        logging.info("New version available: %s (current: %s)", latest_tag, APP_VERSION)
        root.after(0, lambda: _show_update_dialog(root, config, latest_tag, release.get('name', '')))

    thread = threading.Thread(target=_check, daemon=True)
    thread.start()
