"""
updater.py - Check for new versions via GitHub Releases API.
If a newer version is found, prompts the user and opens the browser to download.
"""

import logging
import time
import threading
from datetime import datetime, timedelta

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


def _should_prompt(config, force: bool = False) -> bool:
    """Snooze applies only to automatic checks (startup / 9:00 AM)."""
    if force:
        return True
    snooze_until = config.get_snooze_until()
    if snooze_until > 0 and time.time() < snooze_until:
        logging.info("Update check snoozed until %s", time.ctime(snooze_until))
        return False
    return True


def ms_until_next_local_time(hour: int, minute: int = 0) -> int:
    """Milliseconds until the next occurrence of hour:minute (local time)."""
    now = datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if now >= target:
        target += timedelta(days=1)
    delta = target - now
    return max(0, int(delta.total_seconds() * 1000))


def _show_update_dialog(_root, config, latest_tag: str, release_name: str):
    from ui.qt.updater_dialog import show_update_dialog

    show_update_dialog(config, latest_tag, release_name)


def _run_update_check(_root, config, force: bool = False, on_finish=None):
    if not _should_prompt(config, force=force):
        return

    release = _fetch_latest_version()
    if not release:
        if force and on_finish:
            try:
                from ui.qt.dispatch import run_on_main
                run_on_main(lambda: on_finish("error", "network"))
            except Exception:
                pass
        return

    latest_tag = release['tag']
    if not latest_tag:
        if force and on_finish:
            try:
                from ui.qt.dispatch import run_on_main
                run_on_main(lambda: on_finish("error", "invalid_tag"))
            except Exception:
                pass
        return

    current = _parse_version(APP_VERSION)
    latest = _parse_version(latest_tag)

    if latest <= current:
        logging.info("App is up to date (current=%s, latest=%s)", APP_VERSION, latest_tag)
        if force and on_finish:
            try:
                from ui.qt.dispatch import run_on_main
                run_on_main(lambda: on_finish("up_to_date", APP_VERSION))
            except Exception:
                pass
        return

    if config.is_version_skipped(latest_tag) and not force:
        logging.info("Version %s is skipped until reminder expires", latest_tag)
        return

    logging.info("New version available: %s (current: %s)", latest_tag, APP_VERSION)

    def _show():
        _show_update_dialog(_root, config, latest_tag, release.get('name', ''))

    try:
        from ui.qt.dispatch import run_on_main
        run_on_main(_show)
    except Exception:
        if _root and hasattr(_root, "after"):
            _root.after(0, _show)


def check_for_updates_in_background(_root, config, force: bool = False, on_finish=None):
    """Run update check on a background thread. Shows dialog on main thread if update found."""

    def _check():
        _run_update_check(_root, config, force=force, on_finish=on_finish)

    thread = threading.Thread(target=_check, daemon=True)
    thread.start()


def schedule_daily_update_check(schedule_ms, config, hour: int = 9, minute: int = 0):
    """Schedule the next automatic update check at local hour:minute (default 9:00 AM)."""

    def _tick():
        check_for_updates_in_background(None, config, force=False)
        schedule_daily_update_check(schedule_ms, config, hour=hour, minute=minute)

    delay = ms_until_next_local_time(hour, minute)
    logging.info("Next scheduled update check in %d ms (at %02d:%02d local)", delay, hour, minute)
    schedule_ms(delay, _tick)
