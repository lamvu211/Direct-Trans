# Settings UI samples (PySide6)

Real Qt 6 widgets + **QSS gradients** (not HTML mockups).

## Run

```bash
cd samples/settings_pyside6
pip install PySide6
python launch_samples.py --allinone   # **single screen**, 4 palettes (no tabs)
python launch_samples.py              # premium tabbed samples
python launch_samples.py --classic    # first-generation flat samples
python launch_samples.py --export
python launch_samples.py --one 3
```

## All-in-one (`--allinone`) — **chốt cho migration**

- **Một màn hình**, không tab, **không scroll** (520×572).
- Hotkeys: **3 dòng** + **「Xem thêm (N)」** / **「Thu gọn」**.
- **Dropdown Theme** trên header: Midnight Gold · Aurora Glass · Rose Champagne · **Nord Snow** (khớp production v2.0.2).
- **Light candidates (5 samples):** `python launch_light_candidates.py` — xem `LIGHT_CANDIDATES.md` (Nord Snow đã ship trong app; bốn palette kia là draft).

```bash
python launch_samples.py --allinone
python launch_samples.py --allinone --export
```

PNG: `output/allinone_1_*.png` … `allinone_4_*.png` (cùng layout, đổi theme).

Production UI lives in **`src/ui/qt/`** (see root **`README.md`** and **`CHANGELOG.md`** v2.0.2).

## Premium samples — compact · gradient · layout variants

| # | Name | Layout | Palette |
|---|------|--------|---------|
| 1 | Midnight Gold | Left gradient panel | Obsidian + gold CTA gradients |
| 2 | Aurora Glass | Top chip nav + cards | Violet → cyan aurora background |
| 3 | Rose Champagne | Command deck + footer | Blush editorial, pink gradient buttons |
| 4 | Emerald Noir | **Split** 2-column | API/options left, hotkeys right |
| 5 | Sapphire Rail | Icon rail + chips | Ocean navy, sapphire gradients |

Window width ~500px; API provider+model on one row; hotkeys as dense rows (not wide table).

PNG: `output/premium_*.png`

## Classic samples (`--classic`)

See git history / `themes.py` — first exploration, less compact.
