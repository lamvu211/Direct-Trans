"""One-off: build src/ui/qt/theme.py from samples."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
premium = (ROOT / "samples/settings_pyside6/premium_themes.py").read_text(encoding="utf-8")
common_start = premium.index('_COMMON = """')
common_end = premium.index('"""', common_start + 12) + 3
common = premium[common_start:common_end]

allinone = (ROOT / "samples/settings_pyside6/allinone_themes.py").read_text(encoding="utf-8")
qss_start = allinone.index("_BASE = _COMMON")
qss_end = allinone.index("THEME_IDS")
qss_block = allinone[qss_start:qss_end]
qss_block = qss_block.replace("from premium_themes import _COMMON\n", "")
qss_block = qss_block.replace("_BASE = _COMMON +", "_BASE = _COMMON +")
rest = allinone[qss_end : allinone.index("# Legacy")]

out = (
    '"""Qt theme registry — ported from samples/settings_pyside6."""\n\n'
    "from __future__ import annotations\n\n"
    + common
    + "\n\n"
    + qss_block
    + rest
)

dest = ROOT / "src/ui/qt"
dest.mkdir(parents=True, exist_ok=True)
(dest / "theme.py").write_text(out, encoding="utf-8")
print("Wrote", dest / "theme.py", len(out), "chars")
