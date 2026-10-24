#!/usr/bin/env python3
"""
Launch PySide6 Settings samples.

  python launch_samples.py --allinone   # 4 single-screen themes (recommended)
  python launch_samples.py              # 5 premium tabbed samples
  python launch_samples.py --classic    # original flat themes
  python launch_samples.py --export
  python launch_samples.py --one 2
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--export", action="store_true", help="Save PNG screenshots and exit")
    parser.add_argument("--one", type=int, help="Show only sample N (1-3 with --allinone, else 1-5)")
    parser.add_argument("--classic", action="store_true", help="Use original non-premium themes")
    parser.add_argument("--allinone", action="store_true", help="Single-screen layout, 4 color themes")
    args = parser.parse_args()

    if args.allinone:
        from allinone_layout import apply_premium_app, build_allinone_window
        from allinone_themes import THEME_IDS, label_for

        apply_style = apply_premium_app
        prefix = "allinone"
        max_one = 4
    elif args.classic:
        max_one = 5
        from shared_layout import apply_fusion_app_style, build_settings_window
        from themes import ALL_THEMES

        factories = ALL_THEMES
        apply_style = apply_fusion_app_style
        prefix = "sample"
        build = lambda meta, qss: build_settings_window(meta, qss)
    else:
        max_one = 5
        from premium_layout import apply_premium_app, build_premium_window
        from premium_themes import PREMIUM_THEMES

        factories = PREMIUM_THEMES
        apply_style = apply_premium_app
        prefix = "premium"
        build = lambda meta, qss: build_premium_window(meta, qss)

    app = QApplication(sys.argv)
    apply_style(app)

    windows: list[tuple] = []

    if args.allinone:
        if args.one is not None:
            if args.one < 1 or args.one > 4:
                print("--one must be 1..4 with --allinone", file=sys.stderr)
                return 2
            theme_ids = [THEME_IDS[args.one - 1]]
        else:
            theme_ids = list(THEME_IDS)

        if args.export:
            w = build_allinone_window()
            w.show()
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            for i, tid in enumerate(theme_ids, start=1):
                w.set_theme(tid)
                app.processEvents()
                safe = re.sub(r"[^\w\-]+", "_", label_for(tid)).strip("_")
                path = OUTPUT_DIR / f"{prefix}_{i}_{safe}.png"
                w.grab().save(str(path))
                print(path)
            windows.append((tid, w))
            QTimer.singleShot(0, app.quit)
        else:
            w = build_allinone_window()
            if args.one:
                w.set_theme(THEME_IDS[args.one - 1])
            w.move(80, 80)
            w.show()
            windows.append(("allinone", w))
    else:
        themes = factories
        if args.one:
            n = args.one
            limit = 5
            if n < 1 or n > limit:
                print(f"--one must be 1..{limit} for this mode", file=sys.stderr)
                return 2
            themes = [factories[n - 1]]

        for i, factory in enumerate(themes):
            meta, qss = factory()
            w = build(meta, qss)
            if not args.export:
                w.move(60 + (i % 3) * 48, 60 + (i % 5) * 36)
            w.show()
            windows.append((meta, w))

        if args.export:
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            for meta, w in windows:
                app.processEvents()
                safe = re.sub(r"[^\w\-]+", "_", meta.title).strip("_")
                path = OUTPUT_DIR / f"{prefix}_{meta.id}_{safe}.png"
                w.grab().save(str(path))
                print(path)
            QTimer.singleShot(0, app.quit)

    if not args.export:
        label = "allinone" if args.allinone else ("premium" if not args.classic else "classic")
        print(f"Opened {len(windows)} {label} PySide6 sample(s). Close window(s) to exit.")
        print(f"Export: python {Path(__file__).name} --export")

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
