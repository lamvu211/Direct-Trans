# Direct-Trans

**Direct-Trans** is a lightweight, high-performance, and non-intrusive AI-powered translation utility built specifically for Windows. Operating quietly in the system tray, it registers global system hotkeys to capture selected text from any active application, translate it via state-of-the-art AI backends, and either display the output in an elegant popup window or directly replace the selected text while preserving the original layout and formatting (RTF).

**Current version:** v2.0.0 (`DirectTrans_v2.0.0.exe`)

---

## Key Features

- **Format-Preserving Direct Replacement (`replace` mode):** Translates selected text and replaces it in-place (simulating paste). Unlike naive text replacers, Direct-Trans tokenizes and manipulates **Rich Text Format (RTF)** bytes, preserving styles like colors, bold, and italic, while dynamically mapping appropriate fonts for CJK, Indic, Arabic, or Cyrillic target languages using the Windows Registry.
- **Advanced API Backend & Fallback Chain:**
  - Integrates with **Gemini API** (default: `gemini-flash-lite-latest`), **Groq API**, and **Mistral API** (default: `codestral-latest`).
  - **Google Translate (Free)** serves as a robust built-in fallback.
  - An **automatic fallback chain** (built-in order; no user configuration) retries other providers if your primary fails (network issues or API limits), without interrupting your workflow.
- **Reasoning/CoT Filtering:** Automatically parses and strips `<think>...</think>` tags from output (typical for models like DeepSeek-R1 or Qwen-Cot), ensuring only clean translations are delivered.
- **PySide6 settings & popup (v2.0):** All-in-one Settings with three QSS themes (**Midnight Gold**, **Aurora Glass**, **Rose Champagne**), scrollable content area, API key toolbar with test/save status, and hotkey list with manage dialog. Translation popup shows loading state, provider used (including fallback), and safe Copy/Replace behavior.
- **Robust Windows System Integration:**
  - **Zero-Dependency Global Hotkeys:** Built on native Windows `RegisterHotKey` APIs via `ctypes` instead of heavy external keyboard hook libraries. It runs a dedicated background message loop to guarantee responsive hotkey triggers without interfering with native applications.
  - **Modifier Recovery:** Programmatically releases stuck modifier keys (Shift, Ctrl, Alt, Win) when triggering hotkeys to prevent application-stuck key states on rapid use.
  - **Single-Instance Enforcement:** Uses a Windows System Mutex coupled with a filesystem signal watch (`directtrans.signal`). Attempting to launch a second instance instantly focus-restores the existing instance's settings window.
  - **Auto-Start Registry Management:** Easily configures the app to run on Windows startup using native registry entries (`HKCU\...\Run`).
- **Multilingual UI:** Tray menu, Settings, dialogs, and popup are localized in **Vietnamese, English, Korean, Chinese, and Japanese**.

---

## Technical Architecture

Direct-Trans is organized into decoupled modules under the `src/` directory:

| Module | Role |
|--------|------|
| `main.py` | Entry point: single-instance mutex, **PySide6** `QApplication` loop, coordinates threads and startup. |
| `constants.py` | Modes, provider IDs, fallback order, `APP_VERSION`. |
| `config.py` | `config.json`, DPAPI-encrypted API keys, hotkeys, theme, update snooze. |
| `tray.py` | System tray (`pystray`) on a background thread. |
| `hotkey_manager.py` | Native Windows hotkeys (`user32` message loop). |
| `clipboard_util.py` | Clipboard backup, RTF-aware replace. |
| `translator.py` | Gemini, Groq, Mistral, Google Free + fallback manager. |
| `font_mapper.py` | Windows font resolution for target languages. |
| `settings_window.py` | Thin facade → `ui/qt/settings_window.py`. |
| `popup_window.py` | Thin facade → `ui/qt/popup_window.py`. |
| `ui/qt/` | Settings, popup, themes (`theme.py`), API/hotkey sections, updater dialog, main-thread `dispatch.py`. |
| `ui/i18n.py` | Translations and provider/language lists. |
| `ui/dpi_util.py` | Scaled window sizes for high-DPI monitors. |

Design choices that look like bugs but are intentional (exe kills older `DirectTrans*` processes, model name reset on exe launch, fixed fallback order) are documented in [`REVIEW_INTENT.md`](REVIEW_INTENT.md). Known open issues are in [`issue.md`](issue.md).

---

## Setup & Local Run

### Prerequisites
- **Windows OS** (win32 / ctypes APIs)
- **Python 3.10+**

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/lamvu211/Direct-Trans.git
   cd Direct-Trans
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Includes `PySide6`, `pystray`, `Pillow`, `keyboard` (hotkey capture in Settings dialogs only), `pywin32`, and `requests`.

3. **Run the application:**
   - Console (debugging):
     ```bash
     python src/main.py
     ```
   - Background (no console):
     ```bash
     pythonw src/main.py
     ```

4. **Configuration:**
   - Packaged **`.exe`**: Settings opens on every launch; Gemini/Groq/Mistral **model names** reset to built-in defaults each run (API keys are kept).
   - Dev mode: Settings opens on first run or when the primary provider (other than Google Free) has no API key.
   - Re-open Settings: double-click the tray icon or **Settings** in the tray menu.
   - **Feedback** in Settings emails a report with `directtrans.log` attached (Outlook preferred; otherwise mailto with the log path).
   - Config path: `%APPDATA%\DirectTrans\config.json` in dev, or next to the executable when frozen.

---

## Default Key Shortcuts

On first run, two hotkeys are created:

| Shortcut | Target | Mode |
|----------|--------|------|
| `Ctrl + Shift + V` | Vietnamese | Popup |
| `Ctrl + Shift + E` | English | Popup |

Add, edit (double-click a row), or delete hotkeys in Settings; use **Show more** when you have more than three. Modes: **popup** or **replace**.

---

## Running Tests

```bash
python -m pytest tests/ -q
```

CI also runs `python -m unittest discover -s tests -v` on Windows (Python 3.10–3.12). Tests cover translators, fallback chain, hotkeys, config, RTF, and Qt UI regressions.

Optional UI screenshots:

```bash
python scripts/capture_ui_screenshots.py
```

Output: `docs/ui-review/screenshots/`.

---

## Building Standalone Executable

PyInstaller spec: `DirectTrans.spec` (icon, assets, versioned output name).

```cmd
.\build.bat
```

Artifact: `dist\DirectTrans_v2.0.0.exe`. Close any running DirectTrans process if the build reports a file lock.

---

## Project Structure

```text
Direct-Trans/
├── src/
│   ├── assets/              # Icons, logo, user_manual.html
│   ├── ui/
│   │   ├── qt/              # PySide6 UI (settings, popup, themes)
│   │   ├── i18n.py
│   │   └── dpi_util.py
│   ├── main.py
│   ├── constants.py
│   ├── config.py
│   ├── tray.py
│   ├── hotkey_manager.py
│   ├── clipboard_util.py
│   ├── translator.py
│   ├── font_mapper.py
│   ├── settings_window.py   # Facade
│   └── popup_window.py      # Facade
├── tests/
├── scripts/                 # e.g. capture_ui_screenshots.py
├── samples/settings_pyside6/  # Early Qt prototypes (optional)
├── .github/workflows/       # CI
├── DirectTrans.spec
├── build.bat
├── requirements.txt
├── CHANGELOG.md
├── issue.md                 # Known open issues
├── REVIEW_INTENT.md         # Intentional product behavior
└── README.md
```

---

## License

This project is open-sourced under the [MIT License](LICENSE).
