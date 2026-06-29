# Direct-Trans

**Direct-Trans** is a lightweight, high-performance, and non-intrusive AI-powered translation utility built specifically for Windows. Operating quietly in the system tray, it registers global system hotkeys to capture selected text from any active application, translate it via state-of-the-art AI backends, and either display the output in a elegant popup window or directly replace the selected text while preserving the original layout and formatting (RTF).

---

## Key Features

- **Format-Preserving Direct Replacement (`replace` mode):** Translates selected text and replaces it in-place (simulating paste). Unlike naive text replacers, Direct-Trans tokenizes and manipulates **Rich Text Format (RTF)** bytes, preserving styles like colors, bold, and italic, while dynamically mapping appropriate fonts for CJK, Indic, Arabic, or Cyrillic target languages using the Windows Registry.
- **Advanced API Backend & Fallback Chain:**
  - Integrates with **Gemini API** (default: `gemini-3.1-flash-lite`), **Groq API**, and **Mistral API**.
  - **Google Translate (Free)** serves as a robust built-in fallback.
  - A customizable **fallback chain** ensures that if your primary AI provider fails (due to network issues or API limits), the system automatically retries down the line without interrupting your workflow.
- **Reasoning/CoT Filtering:** Automatically parses and strips `<think>...</think>` tags from output (typical for models like DeepSeek-R1 or Qwen-Cot), ensuring only clean translations are delivered.
- **Robust Windows System Integration:**
  - **Zero-Dependency Global Hotkeys:** Built on native Windows `RegisterHotKey` APIs via `ctypes` instead of heavy external keyboard hook libraries. It runs a dedicated background message loop to guarantee responsive hotkey triggers without interfering with native applications.
  - **Modifier Recovery:** Programmatically releases stuck modifier keys (Shift, Ctrl, Alt, Win) when triggering hotkeys to prevent application-stuck key states on rapid use.
  - **Single-Instance Enforcement:** Uses a Windows System Mutex coupled with a filesystem signal watch (`directtrans.signal`). Attempting to launch a second instance instantly focus-restores the existing instance's settings window.
  - **Auto-Start Registry Management:** Easily configures the app to run on Windows startup using native registry entries (`HKCU\...\Run`).
- **Multilingual Support:** The entire interface (Tray Menu, Settings, and Popup Window) is fully localized in **Vietnamese, English, Korean, Chinese, and Japanese**.

---

## Technical Architecture

Direct-Trans is organized into decoupled modules under the `src/` directory:

- `main.py`: Entry point. Enforces the single-instance mutex, initializes the Tkinter main loop, coordinates background threads, and handles startup configurations.
- `tray.py`: Manages the system tray icon and menu using `pystray`. Runs on a background thread to prevent GUI lockups.
- `hotkey_manager.py`: Implements native Windows hotkey binding using ctypes to hook into `user32.dll` message loops.
- `clipboard_util.py`: Handles clipboard backup, sentinel-based clipboard verification, and safe RTF-preserved pasting.
- `translator.py`: Abstracted translation backends with custom HTTP API wrappers for Gemini, Groq, Mistral, and Google Translate, complete with exponential backoff retries and CoT tag filters.
- `font_mapper.py`: Resolves and validates installed Windows fonts (via registry checking) matching the target language requirements.
- `popup_window.py`: Custom Tkinter dialog styling the translation popup in Claude's signature aesthetic.
- `settings_window.py`: Multi-tab interface for managing API credentials, custom hotkeys, auto-start, and interface languages.

---

## Setup & Local Run

### Prerequisites
- **Windows OS** (due to win32/ctypes APIs dependency)
- **Python 3.10+**

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/lamvu211/Direct-Trans.git
   cd Direct-Trans
   ```

2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *Dependencies include: `pystray`, `Pillow`, `keyboard` (fallback utilities), `pywin32`, and `requests`.*

3. **Run the application:**
   - To run with console (for debugging):
     ```bash
     python src/main.py
     ```
   - To run in background (no console):
     ```bash
     pythonw src/main.py
     ```

4. **Configuration:**
   On first run, the Settings Window will automatically open. Paste your API keys (e.g., Gemini API key) to get started. You can re-open the Settings Window anytime by double-clicking the system tray icon or right-clicking and selecting **Cài đặt / Settings**.

---

## Default Key Shortcuts

On initial run, Direct-Trans configures two default hotkeys:
- `Ctrl + Shift + V`: Translates selected text to **Vietnamese** and displays it in a popup.
- `Ctrl + Shift + E`: Translates selected text to **English** and displays it in a popup.

You can modify these, add new target languages (e.g., Japanese, Korean, Chinese), or change their mode to `replace` inside the Settings Window.

---

## Building Standalone Executable

Direct-Trans uses PyInstaller to bundle the Python scripts and assets into a single, standalone Windows `.exe` file.

The build process is managed by `DirectTrans.spec` (the single source of truth for build configurations, icon binding, and dependency exclusion).

To build the executable:
1. Run the provided batch file:
   ```cmd
   .\build.bat
   ```
2. The compiled binary will be generated under the `dist/` directory as `dist\DirectTrans_v1.0.3.exe` (or the version specified in the spec file).

---

## Project Structure

```text
Direct-Trans/
├── src/
│   ├── assets/            # Graphical resources and icons
│   ├── main.py            # App orchestrator & single-instance logic
│   ├── tray.py            # System tray integration
│   ├── hotkey_manager.py  # Windows API global hotkeys via ctypes
│   ├── clipboard_util.py  # Clipboard helper & RTF parser
│   ├── translator.py      # AI translation endpoints & fallback manager
│   ├── font_mapper.py     # System font lookup helper
│   ├── popup_window.py    # Claude-inspired popup window UI
│   └── settings_window.py # Tkinter settings window UI
├── DirectTrans.spec       # PyInstaller build spec
├── build.bat              # Autocompile script
├── requirements.txt       # Python dependency list
├── CHANGELOG.md           # Release history log
└── README.md              # Project documentation
```

---

## License

This project is open-sourced under the [MIT License](LICENSE).
