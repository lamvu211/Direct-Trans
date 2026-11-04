# Changelog

## v2.0.12
- **Popup UX**: Remove redundant toolbar close (✕) button; title-bar close unchanged. Popup no longer steals focus on show (preserves v2.0.10 copy/replace behavior). After the user clicks anywhere on the popup, keyboard focus moves to the popup so font size can be typed (9–36) and **Esc** closes the window.
- **Update dialog**: Window title bar shows **DirectTrans Update** (localized message and buttons unchanged).
- **Build**: `APP_VERSION` **2.0.12**; artifact **`DirectTrans_v2.0.12.exe`**.

## v2.0.11
- **Replace / Excel (regression fix)**: Detect Excel/BIFF clipboard formats by **registered format name** while enumerating the clipboard, without loading unsafe OLE handles into memory. Restores `excel_like` detection with the v2.0.10 safe clipboard whitelist so quoted TSV, `EXCEL_LAYOUT_ADDON`, and `coerce_excel_paste_text` run again on Excel copy/replace.
- **Build**: `APP_VERSION` **2.0.11**; artifact **`DirectTrans_v2.0.11.exe`**.

## v2.0.10
- **Copy**: Try `WM_COPY` on the focused control first (keeps selection in Edit/RichEdit without keystrokes); wait for hotkey modifiers to release before synthetic Ctrl+C; clipboard sequence number instead of a sentinel string; reject stray lone `c` from CEF copy and retry once.
- **WeChat / CEF**: Do not treat WeChat as EM Edit (`EM_GETSEL`/`EM_SETSEL`); skip `AttachThreadInput` when focusing WeChat for paste; WeChat uses `keybd_event` Ctrl+C after releasing modifiers (SendInput path for other apps).
- **Selection / Replace**: `selection_util` captures EM selection on real Edit/RichEdit only; otherwise stores focus hwnd (`capture_focus_hint`); re-select before paste via `EM_SETSEL` when supported — CEF apps keep selection without keyboard nudges.
- **Clipboard safety**: Read/write only whitelisted plain text and RTF bytes (avoids heap crashes from foreign OLE/COM clipboard payloads, e.g. WeChat).
- **Stability**: Safer `AttachThreadInput` detach; hotkey debounce; normalized HWND logging mask.
- **Build**: `APP_VERSION` **2.0.10**; artifact **`DirectTrans_v2.0.10.exe`**.

## v2.0.9
- **Copy (regression fix)**: Restore modifier release before `keybd_event` Ctrl+C; add SendInput attempt first for CEF. Removed incorrect WeChat “reuse old clipboard” fallback (translated stale clipboard text).
- **Replace**: `keybd_event` Ctrl+V; focus target window with `AttachThreadInput` + `SetFocus` on saved focus hwnd; longer delay before popup Replace paste.

## v2.0.8
- **WeChat / CEF**: Copy via `SendInput` before releasing hotkey modifiers; retry and reject stray lone `c`; reuse pre-hotkey clipboard when synthetic copy fails in WeChat.
- **Replace**: Drop `AttachThreadInput` focus path (crash-prone); `EM_SETSEL` only on real Edit/RichEdit; log foreground process and paste focus.
- **Startup splash**: Create hidden, show after center; destroy if closed before `WM_CREATE`; wait for hwnd on close (fixes top-left invisible blocker).

## v2.0.7
- **Replace**: Capture selection anchors (Edit/RichEdit) at copy time and restore before paste; stronger foreground focus (AttachThreadInput / AllowSetForegroundWindow). Popup Replace uses the same path.
- **Replace / RTF**: Align translated line count to the original selection (keeps blank lines) before paste and RTF merge.
- **Build**: `APP_VERSION` **2.0.7**; artifact **`DirectTrans_v2.0.7.exe`**.

## v2.0.6
- **Replace / Excel**: Unicode-only paste (no RTF) when copying from Excel; preserve raw quoted TSV from clipboard through translation (`EXCEL_LAYOUT_ADDON`); coerce quotes for single-cell paste if the model drops them. Fixes split rows, lost diacritics (`?`), and multi-cell structure when quotes are kept.
- **Translation**: Expanded system prompt documented in `SYSTEM_PROMPT.md`; Excel layout addon in `src/translator.py`.
- **Build**: `APP_VERSION` **2.0.6**; artifact **`DirectTrans_v2.0.6.exe`**.

## v2.0.5
- **Win11 / high-DPI**: DPI awareness before Win32 splash; splash scales with monitor DPI and handles `WM_DPICHANGED`. Tray starts after Qt is ready; deferred menu refresh; plain-text tray labels (no emoji).
- **Translation**: Restored expanded system prompt from `SYSTEM_PROMPT.original.md` (reordered OUTPUT/INPUT/CONTEXT/TERMINOLOGY; no `<text>` echo in output; `{target_lang}` romanization; personal titles rule). See `SYSTEM_PROMPT.md`. Post-process strips leaked `<text>` wrappers.
- **Replace**: Before Ctrl+V, focus returns to the window where you selected text (hotkey Replace and popup Replace); reduces pasting into the wrong app after a slow translation.
- **Clipboard**: Wait **650ms** after paste before restoring the previous clipboard (was 400ms) to reduce wrong-content paste on slow hosts.
- **Translation**: Clearer errors when Gemini / Groq / Mistral block, return empty, or malformed responses; strip multiple model “reasoning” blocks (`think`, `redacted_thinking`, `thinking`) from output.
- **UI**: Dedicated empty-selection message (highlight text, then press the hotkey) in vi / en / ko / zh / ja.
- **Build**: `APP_VERSION` **2.0.5**; artifact **`DirectTrans_v2.0.5.exe`**.

## v2.0.4
- **UI**: Hover feedback on Language / Theme / Model combos and hotkey rows (aligned with ghost header buttons); all four themes.
- **Hotkeys**: Single-click a row to edit (Settings and manage dialog); delete button unchanged.
- **Popup**: Click the font size number to type a value directly (9–36); +/- buttons unchanged.
- **Build**: `APP_VERSION` **2.0.4**; artifact **`DirectTrans_v2.0.4.exe`**.

## v2.0.3
- **Startup (exe)**: **Loading** screen with soft UI progress bar (starts at 20%, +20% per second, cap 100%) as soon as Python starts — `bootstrap.py` entry, Win32 splash on a background thread; closes when Settings appears.
- **UI**: Rose Champagne brand title uses Segoe UI like other themes; popup font/color labels and tooltips follow UI language; hotkey row tooltip respects locale.
- **Repo**: Expanded `.gitignore` (logs, local exe, internal notes); updated `docs/PUBLIC_REPO.md`.
- **Build**: `APP_VERSION` **2.0.3**; artifact **`DirectTrans_v2.0.3.exe`** (`DirectTrans.spec` → `src/bootstrap.py`).

## v2.0.2
- **Theme**: **Nord Snow** (`nord_snow`) — light frost palette (fourth option in Settings / popup theme dropdown); per-theme popup font defaults; light color picker styling.
- **Docs & samples**: README, user manual, PySide6 all-in-one samples; `docs/PUBLIC_REPO.md` (do not commit personal screenshots/config to the public repo).
- **Build**: `APP_VERSION` **2.0.2**; artifact **`DirectTrans_v2.0.2.exe`**.

## v2.0.1
- **Security**: Gemini API key via `x-goog-api-key`; sanitize API error messages before logs/UI.
- **Single instance**: Packaged exe kills stale `DirectTrans*` processes **before** acquiring the mutex (avoids waking the old exe via `directtrans.signal`).
- **Google Free**: HTTP POST form body (avoids HTTP 414); smaller chunks.
- **RTF / clipboard**: Latin-1 RTF I/O, signed `\u` escapes, proportional inline token replacement; 400ms delay before clipboard restore after replace.
- **Theme**: `Config._theme_listener` syncs popup theme changes to open Settings (`set_theme`).

## v2.0.0

### UI (PySide6)
- **All-in-one Settings** on Qt 6 (`Fusion` + QSS): translation provider, API keys, options, and hotkeys on one scrollable screen (fixed window size; body scrolls inside `QScrollArea`).
- **Three themes** (header dropdown): Midnight Gold, Aurora Glass, Rose Champagne — persisted as `ui_theme` in `config.json`.
- **Header**: UI language + theme selectors (compact width, no combo arrow chrome); User manual, Feedback, and in-app **Update** check.
- **API keys**: Toolbar (Load models, Test, Save key) with bold **Pass** / **Fail** status; model list preserves selection after reload; clear control inside the API key field; **Get API key** opens the provider link.
- **Hotkeys**: Up to three rows on Settings + **Show more** opens a scrollable manage dialog; double-click a row to edit; global hotkeys pause while add/edit dialogs are open; compact row spacing.
- **Translation popup (Qt)**: Loading / ready / error states; Copy and Replace disabled while loading; provider status line (including fallback); Esc closes (no redundant close control).
- **Update dialog**: Closing the window no longer snoozes updates.
- **High-DPI**: Settings and popup sizes scale via `ui/dpi_util.py`.

### Core (unchanged behavior, same config schema)
- Tray (`pystray`), native `RegisterHotKey` hotkeys, clipboard RTF replace, translator fallback chain, DPAPI API keys, auto-update from GitHub Releases, single-instance mutex + signal file.
- Packaged **`.exe`**: opens Settings on launch; resets Gemini/Groq/Mistral **model names** to defaults each run (API keys kept).

### Build & version
- `APP_VERSION` **2.0.0**; artifact **`DirectTrans_v2.0.0.exe`** (`DirectTrans.spec`, `build.bat`).

### Known limitations
- RTF replace, special keys in hotkeys, and complex clipboard cases still have edge cases (track internally or report via **Feedback**).
- Intentional behavior: a new exe **stops** other `DirectTrans*` processes; provider fallback order is fixed; **frozen** builds reset default model names on each launch (API keys are kept).

## v1.0.12
- **Settings on exe startup**: Packaged `.exe` always opens the Settings window when launched (reduces confusion after install).
- **Feedback button**: Opens email to report issues with `directtrans.log` attached (Outlook COM, or mailto fallback with log path).
- **Default models on each exe launch**: Gemini/Groq/Mistral model fields reset to defaults when starting the frozen build.
- **Mistral API key URL**: Link points to `admin.mistral.ai/organization/api-keys`.
- **User manual (Vietnamese)**: Trimmed sections; documents auto-open Settings and Feedback.
- **Hotkey dialog warning**: Added localized hint to avoid Space, F1–F12, Enter, Tab, etc. as the main key (mitigation until VK mapping is implemented).
- **Single-instance signal file**: Open Settings only when `directtrans.signal` is deleted successfully; prevents repeated Settings focus every 2s if delete fails.
- **RTF replace line alignment**: When translation line count differs from source paragraphs, merge extra lines into the last paragraph; partial fix for AI line-count mismatch.
- **Default models**: Gemini `gemini-flash-lite-latest`; Mistral `codestral-latest`. Mistral “Load Models” lists only `codestral-latest` and `ministral-8b-latest`.
- **Google Free**: Try clients `dict-chrome-ex`, `at`, then `gtx` on `translate_a/single` when `gtx` returns 429.

## v1.0.11
- **Enhanced translation system prompt**: Added automatic context detection (academic research, technical standards/guides, business emails, executive reports), native fluency polishing when source and target languages match, respectful honorifics for superiors/clients vs neutral tone for general descriptions, and holistic document purpose alignment.

## v1.0.10
- **Fixed API key test failure**: The "Test" button in the Settings window incorrectly reported a failure due to a missing `target_lang_code` argument introduced in v1.0.9. This bug only affected the test functionality and did not impact actual translation.

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
- **Fixed Replace button not pasting text**: The `Replace` button in the popup window previously failed because it captured the popup's own window handle when clicked, rather than the target application. It now correctly captures and restores focus to the original application before simulating `Ctrl+V`.
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
