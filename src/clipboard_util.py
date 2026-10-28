"""
clipboard_util.py - Clipboard operations with RTF support for DirectTrans.
Handles reading/writing clipboard, simulating Ctrl+C/V, and RTF manipulation.
"""

import time
import re
import win32clipboard
import win32con
import win32api
import logging
import ctypes


CF_RTF = win32clipboard.RegisterClipboardFormat("Rich Text Format")

# Wait after Ctrl+V before restoring the user's clipboard (slow apps need more time).
CLIPBOARD_PASTE_SETTLE_DELAY = 0.65

# Substrings of registered clipboard format names that indicate Excel / spreadsheet copy.
_EXCEL_CLIPBOARD_NAME_FRAGMENTS = (
    "biff",
    "excel",
    "sheet",
    "worksheet",
    "workbook",
)


class ClipboardUtil:

    @staticmethod
    def _is_suspect_stray_c_copy(text: str) -> bool:
        """Lone 'c' often means Ctrl+C degraded to typing 'c' in CEF editors (WeChat)."""
        return len(text) == 1 and text in ("c", "C")

    @staticmethod
    def _copy_selection_to_clipboard() -> None:
        """
        Copy selected text to clipboard.
        1. Try WM_COPY first (preserves selection in RichEdit/Edit controls without keystrokes).
        2. Fallback to synthetic Ctrl+C after ensuring physical hotkey keys are released.
        """
        from selection_util import _foreground_focus_hwnd
        import win32gui
        focus_hwnd = _foreground_focus_hwnd()
        if focus_hwnd and win32gui.IsWindow(focus_hwnd):
            user32 = ctypes.windll.user32
            user32.GetClipboardSequenceNumber.restype = ctypes.c_ulong
            seq_before = user32.GetClipboardSequenceNumber()
            try:
                win32api.SendMessage(focus_hwnd, win32con.WM_COPY, 0, 0)
                time.sleep(0.04)
                if user32.GetClipboardSequenceNumber() != seq_before:
                    # WM_COPY succeeded! Zero keystrokes sent, selection perfectly preserved!
                    return
            except Exception:
                pass

        # Fallback: wait briefly for physical hotkey keys to release so they don't leak as typed chars
        from input_util import (
            release_modifier_keys,
            send_ctrl_c_keybd,
            send_ctrl_c_sendinput,
        )
        from selection_util import is_wechat_foreground

        start = time.time()
        while time.time() - start < 0.2:
            ctrl_down = win32api.GetAsyncKeyState(win32con.VK_CONTROL) & 0x8000
            shift_down = win32api.GetAsyncKeyState(win32con.VK_SHIFT) & 0x8000
            v_down = win32api.GetAsyncKeyState(0x56) & 0x8000
            if not (ctrl_down or shift_down or v_down):
                break
            time.sleep(0.02)

        if is_wechat_foreground():
            release_modifier_keys()
            time.sleep(0.03)
            send_ctrl_c_keybd()
            return

        send_ctrl_c_sendinput()
        time.sleep(0.03)
        release_modifier_keys()
        time.sleep(0.03)
        send_ctrl_c_keybd()

    @staticmethod
    def _poll_clipboard_after_copy(sentinel: str) -> tuple[str, dict | None, bytes | None]:
        selected_text = ""
        selected_rtf = None
        clipboard_hints = {"excel": False}
        for _ in range(12):
            time.sleep(0.05)
            current_dict = ClipboardUtil._read_clipboard()
            txt = current_dict.get(win32con.CF_UNICODETEXT, "")
            if isinstance(txt, str) and txt != sentinel:
                clipboard_hints = ClipboardUtil._extract_clipboard_hints(current_dict)
                selected_text = ClipboardUtil._normalize_selected_plain_text(
                    txt, excel=clipboard_hints.get("excel", False)
                )
                selected_rtf = current_dict.get(CF_RTF)
                break
        return selected_text, clipboard_hints, selected_rtf

    @staticmethod
    def _extract_clipboard_hints(data_dict: dict) -> dict:
        """Detect source app traits from formats present after Ctrl+C."""
        excel = False
        for fmt in data_dict:
            try:
                name = win32clipboard.GetClipboardFormatName(fmt)
            except Exception:
                continue
            if not name:
                continue
            lower = name.lower()
            if any(frag in lower for frag in _EXCEL_CLIPBOARD_NAME_FRAGMENTS):
                excel = True
                break
        return {"excel": excel}

    @staticmethod
    def _split_logical_lines(text: str) -> list[str]:
        return text.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    @staticmethod
    def align_translated_line_structure(
        original_text: str, translated_text: str
    ) -> str:
        """
        Pad or merge translated lines so line count matches the original selection.
        Preserves intentional blank lines from the source for RTF / Word paste.
        """
        if not original_text:
            return translated_text
        orig = ClipboardUtil._split_logical_lines(original_text)
        trans = ClipboardUtil._split_logical_lines(translated_text)
        if len(orig) == len(trans):
            return translated_text

        trans_nonempty = [line for line in trans if line.strip()]
        out: list[str] = []
        ti = 0
        for line in orig:
            if not line.strip():
                out.append("")
                continue
            if ti < len(trans_nonempty):
                out.append(trans_nonempty[ti])
                ti += 1
            else:
                out.append("")
        if ti < len(trans_nonempty):
            for j in range(len(out) - 1, -1, -1):
                if out[j]:
                    out[j] = out[j] + "\n" + "\n".join(trans_nonempty[ti:])
                    break
            else:
                out.append("\n".join(trans_nonempty[ti:]))

        if "\r\n" in original_text:
            return "\r\n".join(out)
        return "\n".join(out)

    @staticmethod
    def should_prefer_unicode_paste(
        clipboard_hints: dict | None,
        original_text: str | None,
        translated_text: str,
        original_rtf: bytes | None = None,
    ) -> bool:
        """
        Excel (and similar) mishandles RTF: each \\par becomes a new row, and \\uN
        escapes often render as '?'. Paste plain Unicode for in-cell / spreadsheet content.
        """
        hints = clipboard_hints or {}
        if hints.get("excel"):
            return True
        text = original_text or ""
        if "\t" in text:
            return False
        normalized = text.replace("\r\n", "\n").replace("\x0b", "\n")
        nonempty = [ln for ln in normalized.split("\n") if ln.strip()]
        if len(nonempty) > 1:
            return True
        if original_rtf and any(ord(c) > 127 for c in translated_text):
            if RTFManipulator._rtf_likely_excel(original_rtf):
                return True
        return False

    @staticmethod
    def _normalize_selected_plain_text(txt: str, excel: bool) -> str:
        """
        Excel uses LF (\\n) inside a cell and CRLF (\\r\\n) between rows.
        Do not collapse CRLF to LF for Excel or row boundaries are lost.
        """
        text = txt.replace("\x0b", "\n")
        if excel:
            return text
        return text.replace("\r\n", "\n")

    @staticmethod
    def parse_excel_clipboard(text: str) -> list[list[str]]:
        """
        Parse Excel CF_UNICODETEXT (tab-separated, CRLF rows, quoted fields).
        """
        if not text:
            return [[""]]
        grid: list[list[str]] = []
        row: list[str] = []
        cell: list[str] = []
        in_quotes = False
        i = 0
        n = len(text)
        while i < n:
            ch = text[i]
            if in_quotes:
                if ch == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        cell.append('"')
                        i += 2
                        continue
                    in_quotes = False
                    i += 1
                    continue
                cell.append(ch)
                i += 1
                continue
            if ch == '"':
                in_quotes = True
                i += 1
                continue
            if ch == "\t":
                row.append("".join(cell))
                cell = []
                i += 1
                continue
            if ch == "\r":
                if i + 1 < n and text[i + 1] == "\n":
                    row.append("".join(cell))
                    cell = []
                    grid.append(row)
                    row = []
                    i += 2
                    continue
                cell.append(ch)
                i += 1
                continue
            if ch == "\n":
                row.append("".join(cell))
                cell = []
                grid.append(row)
                row = []
                i += 1
                continue
            cell.append(ch)
            i += 1
        row.append("".join(cell))
        grid.append(row)
        return grid

    @staticmethod
    def serialize_excel_clipboard(grid: list[list[str]], quote_all_cells: bool = True) -> str:
        """Serialize grid for Excel paste; quote fields so in-cell newlines stay in one cell."""
        lines: list[str] = []
        for row in grid:
            fields = [
                ClipboardUtil._excel_quote_cell(cell, force=quote_all_cells)
                for cell in row
            ]
            lines.append("\t".join(fields))
        return "\r\n".join(lines)

    @staticmethod
    def _excel_quote_cell(cell: str, force: bool = True) -> str:
        normalized = cell.replace("\r\n", "\n").replace("\r", "\n")
        if not force and "\t" not in normalized and "\n" not in normalized and '"' not in normalized:
            return normalized
        escaped = normalized.replace('"', '""')
        return f'"{escaped}"'

    @staticmethod
    def excel_grid_shape(grid: list[list[str]]) -> tuple[int, int]:
        rows = len(grid)
        cols = max((len(r) for r in grid), default=1)
        return rows, cols

    @staticmethod
    def excel_grid_to_display(grid: list[list[str]]) -> str:
        """Human-readable text for popup (CRLF between rows, tab between columns)."""
        row_parts: list[str] = []
        for row in grid:
            cells = [c.replace("\r\n", "\n").replace("\r", "\n") for c in row]
            row_parts.append("\t".join(cells))
        return "\r\n".join(row_parts)

    @staticmethod
    def excel_display_to_grid(display_text: str, shape: tuple[int, int]) -> list[list[str]]:
        """Map edited popup text back to a grid with the same row/column shape."""
        rows, cols = shape
        if "\r\n" in display_text:
            raw_rows = display_text.split("\r\n")
        else:
            text = display_text.replace("\r", "\n")
            raw_rows = text.split("\n")
            if len(raw_rows) > rows:
                merged_tail = "\n".join(raw_rows[rows - 1 :])
                raw_rows = raw_rows[: rows - 1] + [merged_tail]
        if len(raw_rows) < rows:
            raw_rows.extend([""] * (rows - len(raw_rows)))
        elif len(raw_rows) > rows:
            raw_rows = raw_rows[:rows]
        grid: list[list[str]] = []
        for r in range(rows):
            line = raw_rows[r] if r < len(raw_rows) else ""
            parts = line.split("\t") if cols > 1 else [line]
            if len(parts) < cols:
                parts.extend([""] * (cols - len(parts)))
            elif len(parts) > cols:
                parts = parts[: cols - 1] + ["\t".join(parts[cols - 1 :])]
            grid.append(parts)
        return grid

    @staticmethod
    def coerce_excel_paste_text(translated_text: str, original_text: str | None) -> str:
        """
        Excel paste: use model output as-is when quotes are preserved.
        If the model dropped quotes but the source was one quoted cell, re-wrap.
        """
        translated = translated_text
        original = original_text or ""
        if '"' in translated or '"' not in original:
            return translated
        grid = ClipboardUtil.parse_excel_clipboard(original)
        if len(grid) == 1 and len(grid[0]) == 1:
            inner = grid[0][0].replace("\r\n", "\n").replace("\r", "\n")
            body = translated.replace("\r\n", "\n").replace("\r", "\n")
            if body == inner:
                return original
            escaped = body.replace('"', '""')
            return f'"{escaped}"'
        return translated

    @staticmethod
    def _format_clipboard_paste_text(
        translated_text: str,
        original_text: str | None,
        clipboard_hints: dict | None,
        use_unicode_only: bool,
    ) -> str:
        hints = clipboard_hints or {}
        if hints.get("excel"):
            return ClipboardUtil.coerce_excel_paste_text(
                translated_text, original_text
            )
        if use_unicode_only:
            return translated_text.replace("\r\n", "\n")
        return translated_text.replace("\n", "\r\n").replace("\r\r\n", "\r\n")

    @staticmethod
    def get_selected_text() -> tuple:
        """
        Get the currently selected text from the active application.
        Returns: (plain_text, rtf_data_or_None, clipboard_hints, selection_state)
        """
        from selection_util import (
            capture_focus_hint,
            capture_selection,
            foreground_process_basename,
        )

        selection_state = capture_selection() or capture_focus_hint()
        fg_process = foreground_process_basename()

        user32 = ctypes.windll.user32
        user32.GetClipboardSequenceNumber.restype = ctypes.c_ulong
        seq_before = user32.GetClipboardSequenceNumber()

        # Backup current clipboard (safe formats only)
        backup_dict = ClipboardUtil._read_clipboard()

        ClipboardUtil._copy_selection_to_clipboard()

        # Poll clipboard sequence number: if unchanged, nothing was selected
        changed = False
        selected_text = ""
        selected_rtf = None
        clipboard_hints = {"excel": False}

        for _ in range(12):
            time.sleep(0.05)
            if user32.GetClipboardSequenceNumber() != seq_before:
                changed = True
                break

        if changed:
            current_dict = ClipboardUtil._read_clipboard()
            txt = current_dict.get(win32con.CF_UNICODETEXT, "")
            if isinstance(txt, str):
                clipboard_hints = ClipboardUtil._extract_clipboard_hints(current_dict)
                selected_text = ClipboardUtil._normalize_selected_plain_text(
                    txt, excel=clipboard_hints.get("excel", False)
                )
                selected_rtf = current_dict.get(CF_RTF)

            if ClipboardUtil._is_suspect_stray_c_copy(selected_text):
                logging.warning(
                    "Suspect stray 'c' from synthetic copy; retrying copy (fg=%s).",
                    fg_process,
                )
                seq_retry = user32.GetClipboardSequenceNumber()
                time.sleep(0.06)
                ClipboardUtil._copy_selection_to_clipboard()
                for _ in range(12):
                    time.sleep(0.05)
                    if user32.GetClipboardSequenceNumber() != seq_retry:
                        break
                retry_dict = ClipboardUtil._read_clipboard()
                retry_txt = retry_dict.get(win32con.CF_UNICODETEXT, "")
                if isinstance(retry_txt, str) and not ClipboardUtil._is_suspect_stray_c_copy(retry_txt):
                    clipboard_hints = ClipboardUtil._extract_clipboard_hints(retry_dict)
                    selected_text = ClipboardUtil._normalize_selected_plain_text(
                        retry_txt, excel=clipboard_hints.get("excel", False)
                    )
                    selected_rtf = retry_dict.get(CF_RTF)
                else:
                    selected_text = ""
                    selected_rtf = None

            # Restore original clipboard only if a new copy occurred
            ClipboardUtil._write_clipboard(backup_dict)

        if selection_state is not None:
            selection_state = dict(selection_state)
            selection_state["fg_process"] = fg_process
            selection_state["original_char_count"] = len(selected_text)

        logging.info(
            "Clipboard read. Got text length: %s, RTF present: %s, excel_like: %s, "
            "selection_capture: %s, fg_process: %s",
            len(selected_text),
            bool(selected_rtf),
            clipboard_hints.get("excel"),
            bool(selection_state and selection_state.get("em_selection")),
            fg_process,
        )
        return selected_text, selected_rtf, clipboard_hints, selection_state

    @staticmethod
    def replace_selected_text(
        translated_text: str,
        original_rtf: bytes | None,
        target_lang: str,
        original_text: str | None = None,
        target_hwnd: int | None = None,
        clipboard_hints: dict | None = None,
        selection_state: dict | None = None,
    ):
        """
        Replace the selected text with translated text, preserving formatting.
        """
        from input_util import release_modifier_keys, send_ctrl_v_keybd
        from selection_util import (
            focus_window_for_paste,
            hwnd_log,
            prepare_text_selection_for_paste,
        )

        if original_text:
            translated_text = ClipboardUtil.align_translated_line_structure(
                original_text, translated_text
            )

        # Backup current clipboard
        backup_dict = ClipboardUtil._read_clipboard()

        write_dict = {}
        use_unicode_only = ClipboardUtil.should_prefer_unicode_paste(
            clipboard_hints,
            original_text,
            translated_text,
            original_rtf=original_rtf,
        )
        if original_rtf and not use_unicode_only:
            new_rtf = RTFManipulator.replace_text_preserve_format(
                original_rtf, translated_text, target_lang, original_text=original_text
            )
            write_dict[CF_RTF] = new_rtf
        elif use_unicode_only:
            logging.info(
                "Replace paste: using Unicode text only (spreadsheet / in-cell multiline)."
            )

        formatted_text = ClipboardUtil._format_clipboard_paste_text(
            translated_text,
            original_text,
            clipboard_hints,
            use_unicode_only,
        )
        write_dict[win32con.CF_UNICODETEXT] = formatted_text
        ClipboardUtil._write_clipboard(write_dict)

        release_modifier_keys()
        time.sleep(0.05)

        preferred_focus = (
            selection_state.get("focus_hwnd") if selection_state else None
        )
        fg_process = (selection_state or {}).get("fg_process")
        paste_focus = focus_window_for_paste(
            target_hwnd, preferred_focus, fg_process=fg_process
        )
        select_method = prepare_text_selection_for_paste(
            selection_state, original_text
        )
        logging.info(
            "Replace focus hwnd=%s paste_focus=%s select_method=%s",
            hwnd_log(target_hwnd),
            hwnd_log(paste_focus),
            select_method,
        )
        time.sleep(0.08)

        send_ctrl_v_keybd()
        time.sleep(CLIPBOARD_PASTE_SETTLE_DELAY)

        # Restore clipboard after paste
        ClipboardUtil._write_clipboard(backup_dict)
        logging.info(f"Clipboard replaced and restored (target lang: {target_lang}).")

    _SAFE_FORMATS = (win32con.CF_UNICODETEXT, win32con.CF_TEXT, win32con.CF_OEMTEXT)

    @staticmethod
    def _is_safe_clipboard_format(fmt: int, data: any) -> bool:
        """Strict whitelist: only standard plain text and RTF bytes. Reject all OLE, COM handles, or custom formats."""
        if not isinstance(data, (str, bytes)):
            return False
        if fmt in ClipboardUtil._SAFE_FORMATS or fmt == CF_RTF:
            return True
        return False

    @staticmethod
    def _read_clipboard() -> dict:
        """Read safe clipboard formats (text/RTF/bytes) into a dictionary."""
        data_dict = {}
        opened = False
        # Retry up to 5 times (total 50ms) to open clipboard if locked
        for i in range(5):
            try:
                win32clipboard.OpenClipboard()
                opened = True
                break
            except Exception as e:
                if i == 4:
                    logging.warning(f"Clipboard read failed (may be locked by another app): {e}")
                    return {}
                time.sleep(0.01)
        
        try:
            fmt = 0
            while True:
                fmt = win32clipboard.EnumClipboardFormats(fmt)
                if fmt == 0:
                    break
                try:
                    data = win32clipboard.GetClipboardData(fmt)
                    if ClipboardUtil._is_safe_clipboard_format(fmt, data):
                        data_dict[fmt] = data
                except Exception:
                    pass
        except Exception as e:
            logging.warning(f"Error getting clipboard data: {e}")
        finally:
            if opened:
                try:
                    win32clipboard.CloseClipboard()
                except Exception:
                    pass
            
        return data_dict

    @staticmethod
    def _write_clipboard(data_dict: dict):
        """Write safe clipboard formats and data without crashing heap."""
        opened = False
        # Retry up to 5 times (total 50ms) to open clipboard if locked
        for i in range(5):
            try:
                win32clipboard.OpenClipboard()
                opened = True
                break
            except Exception as e:
                if i == 4:
                    logging.warning(f"Clipboard write failed (may be locked by another app): {e}")
                    return
                time.sleep(0.01)
        
        try:
            win32clipboard.EmptyClipboard()
            for fmt, data in data_dict.items():
                if not isinstance(data, (str, bytes)):
                    continue
                try:
                    win32clipboard.SetClipboardData(fmt, data)
                except Exception:
                    pass
        except Exception as e:
            logging.warning(f"Error setting clipboard data: {e}")
        finally:
            if opened:
                try:
                    win32clipboard.CloseClipboard()
                except Exception:
                    pass


class RTFManipulator:
    """RTF manipulation: replace text while preserving formatting, change font per target language."""

    @staticmethod
    def _rtf_likely_excel(rtf: bytes) -> bool:
        """Heuristic: compact RTF without Word stylesheet (typical Excel cell copy)."""
        try:
            sample = rtf[:4000].decode("latin-1", errors="ignore").lower()
        except Exception:
            return False
        if "\\stylesheet" in sample:
            return False
        if "msftedit word" in sample or "microsoft word" in sample:
            return False
        if "\\fonttbl" not in sample:
            return False
        return len(rtf) < 12000

    @staticmethod
    def _align_translation_lines(translated_lines: list, num_text_paragraphs: int) -> list:
        """Map translation lines to text paragraphs; merge overflow into the last paragraph."""
        if num_text_paragraphs <= 0:
            return []
        if len(translated_lines) == num_text_paragraphs:
            return list(translated_lines)
        if len(translated_lines) > num_text_paragraphs:
            merged = translated_lines[: num_text_paragraphs - 1]
            merged.append('\n'.join(translated_lines[num_text_paragraphs - 1 :]))
            return merged
        # Fewer lines than paragraphs: map early lines 1:1, last line on the last paragraph
        result = [''] * num_text_paragraphs
        for i in range(len(translated_lines) - 1):
            result[i] = translated_lines[i]
        if translated_lines:
            result[num_text_paragraphs - 1] = translated_lines[-1]
        return result

    @staticmethod
    def _nonempty_lines(text: str) -> list:
        return [
            line.strip()
            for line in text.replace('\r\n', '\n').split('\n')
            if line.strip()
        ]

    @staticmethod
    def _normalize_for_match(s: str) -> str:
        return re.sub(r'\s+', ' ', s.strip())

    @staticmethod
    def _map_via_original_lines(text_paragraphs, original_lines, translated_lines):
        """
        Group consecutive RTF text paragraphs to match plain-text lines, then assign translations.
        """
        result = {}
        rtf_i = 0
        for oi, orig_line in enumerate(original_lines):
            if rtf_i >= len(text_paragraphs):
                return None
            target = RTFManipulator._normalize_for_match(orig_line)
            acc = ''
            first_idx = None
            start_rtf_i = rtf_i
            matched = False
            while rtf_i < len(text_paragraphs):
                idx, p_text = text_paragraphs[rtf_i]
                if first_idx is None:
                    first_idx = idx
                acc += p_text
                acc_norm = RTFManipulator._normalize_for_match(acc)
                if acc_norm == target or (
                    target in acc_norm and len(acc_norm) <= len(target) + 40
                ):
                    result[first_idx] = translated_lines[oi]
                    for merge_j in range(start_rtf_i + 1, rtf_i + 1):
                        result[text_paragraphs[merge_j][0]] = ''
                    rtf_i += 1
                    matched = True
                    break
                if len(acc_norm) > len(target) + 80:
                    return None
                rtf_i += 1
            if not matched:
                return None
        if rtf_i < len(text_paragraphs):
            return None
        return result

    @staticmethod
    def _build_paragraph_translation_map(text_paragraphs, translated_lines, original_text=None):
        n_para = len(text_paragraphs)
        if n_para == 0:
            return {}
        if n_para == len(translated_lines):
            return {text_paragraphs[i][0]: translated_lines[i] for i in range(n_para)}

        if original_text:
            original_lines = RTFManipulator._nonempty_lines(original_text)
            if len(original_lines) == len(translated_lines):
                mapped = RTFManipulator._map_via_original_lines(
                    text_paragraphs, original_lines, translated_lines
                )
                if mapped is not None:
                    return mapped

        aligned = RTFManipulator._align_translation_lines(translated_lines, n_para)
        # Fewer translation lines than RTF paragraphs: middle slots become '' and erase content.
        if len(translated_lines) < n_para and any(
            not aligned[i] for i in range(n_para - 1)
        ):
            return None
        return {text_paragraphs[i][0]: aligned[i] for i in range(n_para)}

    @staticmethod
    def replace_text_preserve_format(original_rtf: bytes, new_text: str,
                                     target_lang: str,
                                     original_text: str | None = None) -> bytes:
        """
        Replace text in RTF while preserving formatting.
        Falls back to simple RTF if parsing fails.
        """
        rtf_str = original_rtf.decode('latin-1', errors='replace')

        from font_mapper import FontMapper
        new_font = FontMapper.get_font(target_lang)

        if original_text:
            new_text = ClipboardUtil.align_translated_line_structure(
                original_text, new_text
            )

        try:
            result = RTFManipulator._do_rtf_replace(
                rtf_str, new_text, new_font, original_text=original_text
            )
            return result.encode('latin-1', errors='replace')
        except ValueError:
            return RTFManipulator._create_simple_rtf(new_text, new_font).encode('latin-1', errors='replace')
        except Exception:
            # Fallback: create simple RTF with the new font
            return RTFManipulator._create_simple_rtf(new_text, new_font).encode('latin-1', errors='replace')

    @staticmethod
    def _do_rtf_replace(rtf_str: str, new_text: str, new_font: str,
                         original_text: str | None = None) -> str:
        """
        Replace text content in RTF while preserving control words and paragraph structure.
        """
        # Find the start of the font table
        fonttbl_start = rtf_str.find(r'{\fonttbl')
        if fonttbl_start == -1:
            raise ValueError("No font table found in RTF")

        # Use brace counting to find the end of the font table
        brace_count = 0
        fonttbl_end = -1
        for i in range(fonttbl_start, len(rtf_str)):
            if rtf_str[i] == '{':
                brace_count += 1
            elif rtf_str[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    fonttbl_end = i + 1
                    break

        if fonttbl_end == -1:
            raise ValueError("Malformed font table in RTF")

        fonttbl_content = rtf_str[fonttbl_start:fonttbl_end]

        # Find the highest font index
        font_indices = re.findall(r'\\f(\d+)', fonttbl_content)
        max_font_idx = max(int(idx) for idx in font_indices) if font_indices else 0
        new_font_idx = max_font_idx + 1

        # Create new font entry and insert before closing brace of fonttbl
        new_font_entry = '{\\f' + str(new_font_idx) + ' \\fnil\\fcharset0 ' + new_font + ';}'
        new_fonttbl = fonttbl_content[:-1] + new_font_entry + '}'

        # Replace font table safely without breaking body_start
        body_start = fonttbl_end
        body = rtf_str[body_start:]
        prefix = rtf_str[:fonttbl_start] + new_fonttbl

        # Tokenize the body
        tokens = RTFManipulator._tokenize_rtf(body)

        # 1. Group tokens into paragraphs by control words containing 'par' or 'line'
        paragraphs = []
        current_paragraph = []
        
        group_depth = 0
        skip_depth = -1
        
        for token_type, token_value in tokens:
            if token_type == 'control':
                if token_value == '{':
                    group_depth += 1
                elif token_value == '}':
                    if skip_depth != -1 and group_depth <= skip_depth:
                        skip_depth = -1
                    group_depth -= 1
                else:
                    val = token_value.strip().lower()
                    if val.startswith('\\colortbl') or val.startswith('\\stylesheet') or val.startswith('\\info') or val.startswith('\\*') or val.startswith('\\pntext') or val.startswith('\\listtext'):
                        if skip_depth == -1:
                            skip_depth = group_depth
            
            # Convert text to control if inside a skipped group so it's not translated
            if token_type == 'text' and skip_depth != -1:
                token_type = 'control'

            is_break = False
            if token_type == 'control':
                val = token_value.strip().lower()
                if val.startswith('\\par') or val.startswith('\\line'):
                    is_break = True
            
            if is_break:
                paragraphs.append((current_paragraph, token_value))
                current_paragraph = []
            else:
                current_paragraph.append((token_type, token_value))
                
        paragraphs.append((current_paragraph, None)) # Last paragraph (no trailing break)

        # 2. Extract original text lines that contain non-whitespace text
        text_paragraphs = []
        for idx, (p_tokens, _) in enumerate(paragraphs):
            p_text_parts = []
            for t_type, t_val in p_tokens:
                if t_type == 'text':
                    p_text_parts.append(t_val)
            p_text = ''.join(p_text_parts)
            if p_text.strip():
                text_paragraphs.append((idx, p_text))

        # 3. Split translated text into lines (ignore empty lines to match text_paragraphs)
        translated_lines = RTFManipulator._nonempty_lines(new_text)

        trans_by_text_para = RTFManipulator._build_paragraph_translation_map(
            text_paragraphs, translated_lines, original_text
        )
        if trans_by_text_para is None:
            raise ValueError("Cannot align translation lines to RTF paragraphs safely")

        # 4. Map translated lines to original text-containing paragraphs
        new_paragraphs = []
        applied_font = False

        for idx, (p_tokens, p_break) in enumerate(paragraphs):
            # Check if this paragraph contains text in original
            has_text = idx in trans_by_text_para
            
            if has_text:
                trans_line = trans_by_text_para[idx]
                
                # Calculate total original text length in this paragraph
                orig_text_parts = []
                for t_type, t_val in p_tokens:
                    if t_type == 'text':
                        orig_text_parts.append(t_val)
                orig_text_full = ''.join(orig_text_parts)
                
                # Replace plain text tokens in this paragraph
                new_p_tokens = []
                text_spans = [
                    (idx, t_val)
                    for idx, (t, t_val) in enumerate(p_tokens)
                    if t == 'text' and t_val.strip()
                ]
                orig_lens = [len(v) for _, v in text_spans]
                total_orig = sum(orig_lens) or 1
                trans_chunks = []
                consumed = 0
                for i, length in enumerate(orig_lens):
                    if i == len(orig_lens) - 1:
                        trans_chunks.append(trans_line[consumed:])
                    else:
                        take = max(1, round(len(trans_line) * length / total_orig))
                        take = min(take, len(trans_line) - consumed)
                        trans_chunks.append(trans_line[consumed:consumed + take])
                        consumed += take
                span_to_chunk = {idx: chunk for (idx, _), chunk in zip(text_spans, trans_chunks)}

                for t_idx, (t_type, t_val) in enumerate(p_tokens):
                    if t_type == 'text' and t_val.strip():
                        if not applied_font:
                            new_p_tokens.append(('control', f'\\f{new_font_idx} '))
                            applied_font = True
                        chunk = span_to_chunk.get(t_idx, '')
                        new_p_tokens.append(('text', RTFManipulator._escape_rtf_text(chunk)))
                    elif t_type == 'text':
                        # Whitespace-only token, preserve as is
                        new_p_tokens.append((t_type, t_val))
                    else:
                        new_p_tokens.append((t_type, t_val))
                
                new_paragraphs.append((new_p_tokens, p_break))
            else:
                # Preserve empty or non-text paragraph as is
                new_paragraphs.append((p_tokens, p_break))

        # Reconstruct body
        reconstructed = []
        for p_tokens, p_break in new_paragraphs:
            for t_type, t_val in p_tokens:
                reconstructed.append(t_val)
            if p_break:
                reconstructed.append(p_break)
                
        return prefix + ''.join(reconstructed)

    @staticmethod
    def _tokenize_rtf(rtf_body: str) -> list:
        """
        Tokenize RTF body into (type, value) tuples.
        Types: 'control' (control words/symbols), 'group_open', 'group_close', 'text'
        Special character control words like \\uN and \\'XX are converted to plain 'text' tokens.
        """
        tokens = []
        i = 0
        length = len(rtf_body)
        uc_value = 1  # Default number of fallback chars for \uN

        while i < length:
            ch = rtf_body[i]

            if ch == '{':
                tokens.append(('control', '{'))
                i += 1
            elif ch == '}':
                tokens.append(('control', '}'))
                i += 1
            elif ch == '\\':
                if i + 1 < length:
                    next_ch = rtf_body[i + 1]
                    if next_ch.isalpha():
                        # Control word: \word[optional_number][optional_space]
                        match = re.match(r'\\([a-zA-Z]+)(-?\d+)?\s?', rtf_body[i:])
                        if match:
                            word = match.group(1).lower()
                            full_match = match.group(0)
                            
                            # Handle Unicode escapes
                            if word == 'u' and match.group(2):
                                val = int(match.group(2))
                                # Decode code point
                                char = chr(val) if val >= 0 else chr(val + 65536)
                                i += len(full_match)
                                # Skip the fallback characters (defined by uc_value)
                                i += uc_value
                                tokens.append(('text', char))
                            elif word == 'uc' and match.group(2):
                                uc_value = int(match.group(2))
                                tokens.append(('control', full_match))
                                i += len(full_match)
                            else:
                                tokens.append(('control', full_match))
                                i += len(full_match)
                        else:
                            tokens.append(('control', rtf_body[i:i+2]))
                            i += 2
                    elif next_ch in '\\{}':
                        # Escaped special char
                        tokens.append(('text', next_ch))
                        i += 2
                    elif next_ch == "'":
                        # Hex-encoded character \'XX. Treat as text!
                        hex_val = rtf_body[i+2:i+4]
                        try:
                            char = bytes.fromhex(hex_val).decode('cp1252', errors='replace')
                        except Exception:
                            char = '?'
                        tokens.append(('text', char))
                        i += 4
                    elif next_ch == '\n' or next_ch == '\r':
                        # \<newline> is a paragraph break alias
                        tokens.append(('control', rtf_body[i:i+2]))
                        i += 2
                    else:
                        tokens.append(('control', rtf_body[i:i+2]))
                        i += 2
                else:
                    tokens.append(('control', '\\'))
                    i += 1
            elif ch in '\r\n':
                i += 1  # Skip bare newlines in RTF
            else:
                # Plain text - collect until next control character
                text_start = i
                while i < length and rtf_body[i] not in '\\{}' and rtf_body[i] not in '\r\n':
                    i += 1
                tokens.append(('text', rtf_body[text_start:i]))

        return tokens

    @staticmethod
    def _escape_rtf_text(text: str) -> str:
        """Escape special RTF characters and encode non-ASCII as Unicode escapes."""
        result = []
        for ch in text:
            if ch == '\\':
                result.append('\\\\')
            elif ch == '{':
                result.append('\\{')
            elif ch == '}':
                result.append('\\}')
            elif ch == '\n':
                result.append('\\par ')
            elif ch == '\r':
                continue
            elif ch == '\t':
                result.append('\\tab ')
            elif ord(ch) > 127:
                code = ord(ch)
                if code > 0xFFFF:
                    code -= 0x10000
                signed = code if code <= 32767 else code - 65536
                result.append(f'\\u{signed}?')
            else:
                result.append(ch)
        return ''.join(result)

    @staticmethod
    def _create_simple_rtf(text: str, font_name: str) -> str:
        """Create simple RTF when original parsing fails."""
        escaped = RTFManipulator._escape_rtf_text(text)
        return (
            r'{\rtf1\ansi\deff0'
            r'{\fonttbl{\f0 ' + font_name + r';}}'
            r' ' + escaped +
            r'}'
        )
