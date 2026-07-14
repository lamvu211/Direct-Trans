# Changelog

## v1.0.9
- **Added automatic update notification**: On startup, the app checks GitHub Releases for new versions in the background. If a newer version is found, a dialog offers three options: open the download page, snooze for 7 days, or skip that version. User preferences are persisted in `config.json`.
- **Added `APP_VERSION` constant**: Centralized version tracking in `constants.py` for update comparison and future use.
- **Fixed prompt injection in translation**: Wrapped text inside `<text>` tags and strictly instructed the LLM to ignore hidden inline instructions to prevent the model from translating into an unexpected language.
- **Improved LLM target language recognition**: Passed the full language name instead of the short language code to LLM providers (Gemini, Groq, Mistral) to improve accuracy, while keeping the language code format for the Google Translate API.

## v1.0.8
- **Fixed RTF bullet point translation**: Added `\pntext` and `\listtext` to the ignored groups list in RTF processing. This prevents the parser from accidentally overwriting hidden bullet point characters with translated text, fixing the "lost text" and font corruption issues when translating bulleted or numbered lists in Word and PowerPoint.

## v1.0.7
- **Fixed RTF parsing for Microsoft Office**: Replaced regex with a brace-counting algorithm for `\fonttbl` extraction in RTF processing. This resolves an issue where pasting translated text back into Word or PowerPoint would cause fonts to unexpectedly increase in size or fail to paste entirely due to nested brace structures in Office's RTF format.

## v1.0.6
- **Fixed Replace button not pasting text**: The `Replace` button in the popup window previously failed because it captured the popup's own window handle when clicked, rather than the target application. It now correctly captures and restores focus to the original active window before simulating `Ctrl+V`.
- **Disabled popup always-on-top**: The translation popup no longer forces itself to stay on top (`-topmost`) of other windows, improving UX when switching to other applications.
- **Fixed version upgrade not replacing old process**: `kill_old_processes()` used exact name `DirectTrans.exe` which didn't match versioned executables like `DirectTrans_v1.0.4.exe`. Now matches any process starting with "DirectTrans".
- **Fixed auto-start registry not updating on upgrade**: When upgrading from v1.0.4 to v1.0.5+, the Windows startup registry entry still pointed to the old exe. Added `_heal_auto_start_path()` that automatically detects and updates the registry path on startup.
- **Added fallback chain tests**: Comprehensive unit tests for `TranslationManager` with mock backends, verifying provider order, skip-on-missing-key behavior, fallback-disabled mode, and `<think>` tag stripping.
- **Added RTF manipulation tests**: Fixed test cases for `_tokenize_rtf` (plain text, control words, unicode escape, hex chars) and `replace_text_preserve_format` (structure preservation, multi-paragraph, styled content).
- **Added first-run detection**: `Config.is_first_run()` and `Config.needs_setup()` methods control whether Settings opens on startup. Settings only opens when config is freshly created or primary provider has no API key. Google Free users skip the prompt.
- **Added shared constants module**: Centralized `TranslationMode` and `Provider` enums in `constants.py`, eliminating hardcoded string literals across the codebase.
- **Added GitHub Actions CI**: Runs unittest suite on push/PR to main/master across Python 3.10-3.12 on Windows.
- **Updated README**: Documented `src/ui/` module structure, startup behavior, CI badge reference, and test coverage.
- **Fixed docstring in `translator.py`**: Removed stale references to "LRU cache" and "DeepL".

## v1.0.5
- **Kill old processes on startup**: When launching the EXE, any existing DirectTrans.exe processes (including stale autostart instances from older versions) are automatically terminated before the new instance starts. This ensures the new version always takes over cleanly.
- **Fixed race condition in hotkey processing**: Replaced bare `bool` flag `_processing` with `threading.Lock` to prevent duplicate translations when hotkeys are pressed rapidly.
- **Fixed clipboard data loss on Save Key**: `clipboard_clear()` was called unconditionally when saving an API key, wiping any unrelated clipboard content. Now only clears if clipboard contains the saved key.
- **Fixed tray/app enabled state desync**: Removed independent `enabled` state from `TrayIcon`; tray menu now reads the canonical state from the app via callback, preventing future desync.
- **Fixed popup Replace pasting into wrong app**: Captures the foreground window handle before hiding the popup and restores focus to it before simulating Ctrl+V.
- **Fixed RTF skip_depth edge case**: Corrected group depth comparison (`<=` instead of `==`) when exiting skipped RTF destinations, preventing text loss in complex RTF documents.
- **Fixed Google Translate error messages**: Added explicit `ValueError` (JSON decode) handling so blocked/non-JSON responses show "Invalid response" instead of generic "Request failed".
- **Fixed keyboard hook leak in hotkey dialog**: Added `<Destroy>` event binding to ensure the `keyboard` hook is always released, even if the dialog is destroyed abnormally.
- **Fixed TclError on Settings window close**: Added `winfo_exists()` guard before `state()` call in `<Unmap>` handler to prevent crash when window is being destroyed.
- **Fixed missing user-installed fonts on Windows 10+**: `FontMapper` now reads both `HKLM` and `HKCU` registry keys, detecting per-user fonts installed since Windows 10 1803.
- **Fixed RTF tab character handling**: Tab characters (`\t`) are now correctly escaped as `\tab` in RTF output.
- **Reduced single-instance polling frequency** from 500ms to 2000ms for lower idle resource usage.
- **Simplified API key test flow**: Test button now only tests the currently selected model instead of iterating all models in the combobox.

## v1.0.4
- Fixed critical bug where the `_processing` flag was never reset on successful translation, locking hotkeys.
- Fixed side-effect in `settings_window.py` where changing UI language would write the entire configuration (including unsaved API keys).
- Added thread-safety to `FontMapper._installed_fonts` using a lock to prevent race conditions.
- Made system tray menu fully dynamic, updating its language instantly when the UI language changes.
- Added missing translation keys for Korean, Chinese, and Japanese locales in `i18n.py` to prevent potential runtime errors.
- Removed lazy `import re` inside `translator.py` and redundant `import time` from `clipboard_util.py` to clean up code imports.
- Fixed duplicate encryption key definition in `config.py` (Base64 vs Hex).
- Fixed a concurrency issue where holding hotkeys could spam multiple translation threads.
- Refactored `translator.py` to be stateless, removing state from instances to prevent cross-request contamination.
- Added localized error handling (`i18n.py`) and standard localized error popups for API Key missing, Clipboard errors, and generic translation failures.
- Fixed an issue where the clipboard `RTF` logic was incorrectly chunking the original styling.
- Refactored UI modules to remove magic hex strings and use standard constants (`SUCCESS`, `WHITE`, `BASE`, etc.).
- Refactored `api_config_tab.py` to remove duplicate logic for building provider frames.
- Re-added lazy imports to `clipboard_util.py` to prevent PyInstaller bundling issues.
- Optimized font caching in `font_mapper.py` to prevent repeated slow Windows registry reads.
- Added comprehensive unit tests for translation providers (`tests/test_translator.py`).
- Added robust validation for parsing empty hotkey strings in `hotkey_manager.py`.
- Fixed `_quit()` in `main.py` using `os._exit(0)` to ensure background threads are terminated.
- Fixed "Start with Windows" mechanism: quoted executable paths to support spaces, used `sys.executable` for dev mode startup path, handled registry exceptions safely, and reverted the checkbox status in Settings UI if the registry write fails.

## v1.0.3
- Refactored `settings_window.py` into modular UI components (`i18n.py`, `constants.py`, `api_config_tab.py`, `hotkey_config_tab.py`).
- Enhanced clipboard backup mechanism in `clipboard_util.py` to preserve all OS clipboard formats.
- Implemented Windows DPAPI encryption for API keys in `config.py` using `win32crypt`.
- Created `BaseHTTPTranslator` to DRY up translation requests and standardise retry/backoff logic.
- Fixed fallback chain bug in `TranslationManager` to strictly prioritize the user-selected primary provider.
- Added Update button and restyled User manual button to match Save Key.
- Redesigned header layout to place language combobox, User manual, and Update buttons horizontally under the app title.

## v1.0.2
- Improved system prompt for translation quality: added grammar rules, terminology constraints, abbreviation handling, and phonetic transcription for Asian proper names.
- Added .agent directory to .gitignore.

## v1.0.1
- Added GitHub Release link to "Update" button in Settings window.
- Rewrote project README.md with detailed instructions.
- Uploaded project to GitHub repository.

## v1.0
- Fixed white gap when scrolling up in Settings window.
- Added version number to Settings window title.
- Replaced info icon with "User manual" button below language dropdown.
- Fixed "Lưu Key" button to respect UI language translations.
