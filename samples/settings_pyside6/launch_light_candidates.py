#!/usr/bin/env python3
"""Launch Settings samples for the five light theme candidates."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from allinone_layout import AllInOneSettingsWindow, apply_premium_app
import light_candidates_themes as light_registry

OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def main() -> int:
    parser = argparse.ArgumentParser(description="Light theme candidate Settings samples")
    parser.add_argument("--all", action="store_true", help="Open 5 windows (one per theme)")
    parser.add_argument("--export", action="store_true", help="Save PNG screenshots to output/")
    parser.add_argument("--one", type=int, help="Show only candidate N (1–5)")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    apply_premium_app(app)

    theme_ids = list(light_registry.THEME_IDS)
    if args.one is not None:
        if args.one < 1 or args.one > len(theme_ids):
            print("--one must be 1..5", file=sys.stderr)
            return 2
        theme_ids = [theme_ids[args.one - 1]]

    windows: list[AllInOneSettingsWindow] = []

    if args.all and not args.export:
        for i, tid in enumerate(light_registry.THEME_IDS):
            w = AllInOneSettingsWindow(
                initial_theme_id=tid,
                theme_registry=light_registry,
            )
            w.move(40 + (i % 3) * 40, 40 + i * 28)
            w.show()
            windows.append(w)
    else:
        initial = theme_ids[0]
        w = AllInOneSettingsWindow(
            initial_theme_id=initial,
            theme_registry=light_registry,
        )
        w.show()
        windows.append(w)

        if args.export:
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            for tid in theme_ids:
                w.set_theme(tid)
                app.processEvents()
                safe = re.sub(r"[^\w\-]+", "_", light_registry.label_for(tid)).strip("_")
                path = OUTPUT_DIR / f"light_candidate_{safe}.png"
                w.grab().save(str(path))
                print(path)
            QTimer.singleShot(0, app.quit)
            return app.exec()

    if not args.export:
        print("Light candidates: use Theme dropdown to compare all 5 palettes.")
        print(f"Docs: {Path(__file__).with_name('LIGHT_CANDIDATES.md')}")
        print(f"Export: python {Path(__file__).name} --export")

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
