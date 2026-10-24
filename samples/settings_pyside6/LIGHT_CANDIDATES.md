# Light theme candidates (Settings sample)

Five minimal **light** palettes aimed at Cursor Light / Antigravity-style UIs. Tokens map 1:1 to QSS in `light_candidates_themes.py` (same object names as production `src/ui/qt/theme.py`).

## Token → UI mapping

| Token | Qt widgets / object names |
|-------|---------------------------|
| `root_bg` | `QWidget#root` window background |
| `top_bar_*` | `QFrame#topBar` |
| `foot_bar_*` | `QFrame#footBar` |
| `brand`, `text_muted` | `QLabel#brand`, `#brandSub`, `#tagline`, `#fieldLabel` (muted) |
| `card_*`, `card_title` | `QFrame#card`, `QLabel#cardTitle` |
| `text` | `QLabel`, `QCheckBox`, `QRadioButton`, `QLabel#hkKey`, `#hkLang` |
| `input_*` | `QComboBox#combo`, `#comboMini`, `#themeCombo`, `QLineEdit#line` |
| `dropdown_*` | `QComboBox QAbstractItemView` |
| `cta_*` | `QPushButton#cta`, `#ctaSmall` |
| `ghost_*` | `QPushButton#ghost`, `QToolButton#ghost`, `#showMore` |
| `text_link_*` | `QPushButton#textLink` |
| `hk_*` | `QFrame#hkRow`, `QLabel#hkMode`, `#hkDel` |
| `option_check` | `QCheckBox#optionCheck` |
| `radio_*` | `QRadioButton::indicator` |
| `cta_disabled_*` | `QPushButton#cta:disabled` |

---

## 1. Cursor Paper (`cursor_paper`)

Neutral warm gray canvas, near-black text, **blue** focus and primary actions (Cursor-like).

| Role | Hex |
|------|-----|
| Root | `#F3F3F3` |
| Top bar | `#FAFAFA` / border `#E4E4E4` |
| Footer | `#FAFAFA` / border `#E4E4E4` |
| Card | `#FFFFFF` / border `#E8E8E8` |
| Text | `#1F1F1F` |
| Muted | `#6B6B6B` |
| Card title | `#525252` |
| Input | bg `#FFFFFF`, border `#D4D4D4`, focus `#0969DA` |
| CTA | bg `#0969DA`, text `#FFFFFF`, hover `#0550AE` |
| Ghost | bg `#FFFFFF`, text `#1F1F1F`, border `#D4D4D4` |
| Link | `#0969DA` / hover `#0550AE` |
| Hotkey row | `#FAFAFA` / border `#EBEBEB` |
| Mode chip | bg `#EEF4FF`, text `#0969DA` |

---

## 2. Antigravity Mist (`antigravity_mist`)

Cool white, hairline borders, **teal** accent (clean IDE / Antigravity feel).

| Role | Hex |
|------|-----|
| Root | `#F8F9FA` |
| Top bar | `#FFFFFF` / border `#E5E7EB` |
| Footer | `#FFFFFF` / border `#E5E7EB` |
| Card | `#FFFFFF` / border `#E5E7EB` |
| Text | `#111827` |
| Muted | `#6B7280` |
| Card title | `#374151` |
| Input | bg `#FFFFFF`, border `#D1D5DB`, focus `#0D9488` |
| CTA | bg `#0D9488`, text `#FFFFFF`, hover `#0F766E` |
| Ghost | bg `#FFFFFF`, text `#374151`, border `#D1D5DB` |
| Link | `#0D9488` / hover `#0F766E` |
| Hotkey row | `#FFFFFF` / border `#F3F4F6` |
| Mode chip | bg `#CCFBF1`, text `#0F766E` |

---

## 3. Paper Ink (`paper_ink`)

High-contrast **editorial**: warm paper root, ink text, **indigo** accent (minimal, no pink).

| Role | Hex |
|------|-----|
| Root | `#F4F1EA` |
| Top bar | `#FFFCF7` / border `#E7E2D8` |
| Footer | `#FFFCF7` / border `#E7E2D8` |
| Card | `#FFFFFF` / border `#E0DBD0` |
| Text | `#1A1A1A` |
| Muted | `#5C5C5C` |
| Card title | `#404040` |
| Input | bg `#FFFFFF`, border `#C9C4B8`, focus `#4338CA` |
| CTA | bg `#4338CA`, text `#FFFFFF`, hover `#3730A3` |
| Ghost | bg `#FFFCF7`, text `#1A1A1A`, border `#C9C4B8` |
| Link | `#4338CA` / hover `#3730A3` |
| Hotkey row | `#FFFFFF` / border `#EDE8DF` |
| Mode chip | bg `#EEF2FF`, text `#4338CA` |

---

## 4. Nord Snow (`nord_snow`) — **shipped in DirectTrans v2.0.2**

Cool **frost** palette (Nord-inspired light), blue-gray text, **frost blue** accent. Production QSS: `src/ui/qt/theme.py`.

| Role | Hex |
|------|-----|
| Root | `#ECEFF4` |
| Top bar | `#E5E9F0` / border `#D8DEE9` |
| Footer | `#E5E9F0` / border `#D8DEE9` |
| Card | `#ECEFF4` / border `#D8DEE9` |
| Text | `#2E3440` |
| Muted | `#4C566A` |
| Card title | `#3B4252` |
| Input | bg `#ECEFF4`, border `#D8DEE9`, focus `#5E81AC` |
| CTA | bg `#5E81AC`, text `#ECEFF4`, hover `#4C6F94` |
| Ghost | bg `#ECEFF4`, text `#2E3440`, border `#D8DEE9` |
| Link | `#5E81AC` / hover `#4C6F94` |
| Hotkey row | `#E5E9F0` / border `#D8DEE9` |
| Mode chip | bg `#D8DEE9`, text `#5E81AC` |

---

## 5. Sage Linen (`sage_linen`)

Warm **linen** background, soft green accent (calm, non-pink alternative to Rose Champagne).

| Role | Hex |
|------|-----|
| Root | `#F5F2EB` |
| Top bar | `#FAF8F4` / border `#E8E4DC` |
| Footer | `#FAF8F4` / border `#E8E4DC` |
| Card | `#FFFFFF` / border `#E3DDD2` |
| Text | `#2C2925` |
| Muted | `#6F6A62` |
| Card title | `#4A7C59` |
| Input | bg `#FFFFFF`, border `#D5CFC4`, focus `#4A7C59` |
| CTA | bg `#4A7C59`, text `#FFFFFF`, hover `#3D6649` |
| Ghost | bg `#FFFFFF`, text `#2C2925`, border `#D5CFC4` |
| Link | `#4A7C59` / hover `#3D6649` |
| Hotkey row | `#FFFFFF` / border `#EDE9E1` |
| Mode chip | bg `#E8F0EA`, text `#3D6649` |

---

## Run samples

```bash
cd samples/settings_pyside6
python launch_light_candidates.py              # one window, theme dropdown (5 options)
python launch_light_candidates.py --all        # 5 windows tiled
python launch_light_candidates.py --export     # PNGs → output/light_candidate_*.png
python launch_light_candidates.py --one 1      # single theme by index 1–5
```
