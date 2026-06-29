"""
clipboard_util.py - Clipboard operations with RTF support for DirectTrans.
Handles reading/writing clipboard, simulating Ctrl+C/V, and RTF manipulation.
"""

import time
import re
import win32clipboard
import win32con
import win32api
import keyboard
import logging


CF_RTF = win32clipboard.RegisterClipboardFormat("Rich Text Format")


class ClipboardUtil:

    @staticmethod
    def get_selected_text() -> tuple:
        """
        Get the currently selected text from the active application.
        Returns: (plain_text, rtf_data_or_None)
        """
        # Backup current clipboard
        backup_text, backup_rtf = ClipboardUtil._read_clipboard()

        # Đặt một giá trị token đặc biệt để kiểm tra xem clipboard có được cập nhật bởi ctrl+c không
        sentinel = f"__DIRECT_TRANS_SENTINEL_{time.time()}__"
        ClipboardUtil._write_clipboard(sentinel, None)

        import win32api
        import win32con
        modifiers = [
            (0xA0, 0), # VK_LSHIFT
            (0xA1, 0), # VK_RSHIFT
            (0xA2, 0), # VK_LCONTROL
            (0xA3, win32con.KEYEVENTF_EXTENDEDKEY), # VK_RCONTROL
            (0xA4, 0), # VK_LMENU (Alt)
            (0xA5, win32con.KEYEVENTF_EXTENDEDKEY), # VK_RMENU (RAlt)
            (0x5B, win32con.KEYEVENTF_EXTENDEDKEY), # VK_LWIN
            (0x5C, win32con.KEYEVENTF_EXTENDEDKEY)  # VK_RWIN
        ]

        # Unconditionally force release all modifiers (both specific and generic)
        # This guarantees Chrome/Edge will not see leftover modifier states like Shift
        # even if the user presses the hotkey extremely fast.
        for vk, flags in modifiers + [(0x10, 0), (0x11, 0), (0x12, 0)]:
            try:
                sc = win32api.MapVirtualKey(vk, 0)
                win32api.keybd_event(vk, sc, win32con.KEYEVENTF_KEYUP | flags, 0)
            except Exception:
                pass

        # Small delay to let OS register modifier key releases
        time.sleep(0.08)

        # Simulate Ctrl+C using Win32 API with proper scan codes
        VK_C = 0x43
        VK_CONTROL = 0x11
        SC_C = win32api.MapVirtualKey(VK_C, 0)
        SC_CONTROL = win32api.MapVirtualKey(VK_CONTROL, 0)

        win32api.keybd_event(VK_CONTROL, SC_CONTROL, 0, 0)  # Ctrl down
        win32api.keybd_event(VK_C, SC_C, 0, 0)  # C down
        win32api.keybd_event(VK_C, SC_C, win32con.KEYEVENTF_KEYUP, 0)  # C up
        win32api.keybd_event(VK_CONTROL, SC_CONTROL, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl up
        
        # We intentionally do NOT restore modifiers here via software KEYDOWN.
        # Restoring them was causing keys (like Ctrl) to get stuck down permanently 
        # if the user physically released them right before our software restored them.

        # Đợi clipboard cập nhật (tối đa 500ms, kiểm tra mỗi 50ms)
        selected_text = ""
        selected_rtf = None
        for _ in range(10):
            time.sleep(0.05)
            txt, rtf = ClipboardUtil._read_clipboard()
            if txt != sentinel:
                selected_text = txt
                selected_rtf = rtf
                break

        # Khôi phục lại clipboard gốc
        ClipboardUtil._write_clipboard(backup_text, backup_rtf)

        # Chuẩn hóa nếu không copy được gì (vẫn là sentinel)
        if selected_text == sentinel:
            selected_text = ""
            selected_rtf = None

        logging.info(f"Clipboard read. Got text length: {len(selected_text)}, RTF present: {bool(selected_rtf)}")
        return selected_text, selected_rtf

    @staticmethod
    def replace_selected_text(translated_text: str, original_rtf: bytes | None,
                              target_lang: str):
        """
        Replace the selected text with translated text, preserving formatting.
        """
        # Backup current clipboard
        backup_text, backup_rtf = ClipboardUtil._read_clipboard()

        if original_rtf:
            new_rtf = RTFManipulator.replace_text_preserve_format(
                original_rtf, translated_text, target_lang
            )
            ClipboardUtil._write_clipboard(translated_text, new_rtf)
        else:
            ClipboardUtil._write_clipboard(translated_text, None)

        # We only need the modifiers list to force-release them below.
        import win32api
        import win32con
        modifiers = [
            (0xA0, 0), # VK_LSHIFT
            (0xA1, 0), # VK_RSHIFT
            (0xA2, 0), # VK_LCONTROL
            (0xA3, win32con.KEYEVENTF_EXTENDEDKEY), # VK_RCONTROL
            (0xA4, 0), # VK_LMENU (Alt)
            (0xA5, win32con.KEYEVENTF_EXTENDEDKEY), # VK_RMENU (RAlt)
            (0x5B, win32con.KEYEVENTF_EXTENDEDKEY), # VK_LWIN
            (0x5C, win32con.KEYEVENTF_EXTENDEDKEY)  # VK_RWIN
        ]

        # Unconditionally force release all modifiers (both specific and generic)
        for vk, flags in modifiers + [(0x10, 0), (0x11, 0), (0x12, 0)]:
            try:
                sc = win32api.MapVirtualKey(vk, 0)
                win32api.keybd_event(vk, sc, win32con.KEYEVENTF_KEYUP | flags, 0)
            except Exception:
                pass

        time.sleep(0.08)

        # Simulate Ctrl+V using Win32 API with proper scan codes
        VK_V = 0x56
        VK_CONTROL = 0x11
        SC_V = win32api.MapVirtualKey(VK_V, 0)
        SC_CONTROL = win32api.MapVirtualKey(VK_CONTROL, 0)

        win32api.keybd_event(VK_CONTROL, SC_CONTROL, 0, 0)  # Ctrl down
        win32api.keybd_event(VK_V, SC_V, 0, 0)  # V down
        win32api.keybd_event(VK_V, SC_V, win32con.KEYEVENTF_KEYUP, 0)  # V up
        win32api.keybd_event(VK_CONTROL, SC_CONTROL, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl up
        
        # We intentionally do NOT restore modifiers here via software KEYDOWN.
        time.sleep(0.2)

        # Restore clipboard after paste
        ClipboardUtil._write_clipboard(backup_text, backup_rtf)
        logging.info(f"Clipboard replaced and restored (target lang: {target_lang}).")

    @staticmethod
    def _read_clipboard() -> tuple:
        """Read clipboard, return (plain_text, rtf_bytes_or_None)."""
        text = ""
        rtf = None
        opened = False
        import time
        # Retry up to 5 times (total 50ms) to open clipboard if locked
        for i in range(5):
            try:
                win32clipboard.OpenClipboard()
                opened = True
                break
            except Exception as e:
                if i == 4:
                    logging.warning(f"Clipboard read failed (may be locked by another app): {e}")
                    return "", None
                time.sleep(0.01)
        
        try:
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            if win32clipboard.IsClipboardFormatAvailable(CF_RTF):
                rtf = win32clipboard.GetClipboardData(CF_RTF)
        except Exception as e:
            logging.warning(f"Error getting clipboard data: {e}")
        finally:
            if opened:
                try:
                    win32clipboard.CloseClipboard()
                except Exception:
                    pass
            
        if text:
            # Normalize various line break characters to \n for consistent translation
            text = text.replace('\r\n', '\n').replace('\x0b', '\n')
            
        return text, rtf

    @staticmethod
    def _write_clipboard(text: str, rtf: bytes | None):
        """Write both plain text and RTF (if available) to clipboard."""
        opened = False
        import time
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
            if text:
                # Ensure standard Windows newlines for plain text
                text = text.replace('\n', '\r\n').replace('\r\r\n', '\r\n')
                win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
            if rtf:
                win32clipboard.SetClipboardData(CF_RTF, rtf)
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
    def replace_text_preserve_format(original_rtf: bytes, new_text: str,
                                     target_lang: str) -> bytes:
        """
        Replace text in RTF while preserving formatting.
        Falls back to simple RTF if parsing fails.
        """
        rtf_str = original_rtf.decode('utf-8', errors='replace')

        from font_mapper import FontMapper
        new_font = FontMapper.get_font(target_lang)

        try:
            result = RTFManipulator._do_rtf_replace(rtf_str, new_text, new_font)
            return result.encode('utf-8')
        except Exception:
            # Fallback: create simple RTF with the new font
            return RTFManipulator._create_simple_rtf(new_text, new_font).encode('utf-8')

    @staticmethod
    def _do_rtf_replace(rtf_str: str, new_text: str, new_font: str) -> str:
        """
        Replace text content in RTF while preserving control words and paragraph structure.
        """
        # Find the font table
        fonttbl_match = re.search(r'\{\\fonttbl\s*((?:\{[^}]*\}[\s]*)*)\}', rtf_str)
        if not fonttbl_match:
            raise ValueError("No font table found in RTF")

        fonttbl_content = fonttbl_match.group(0)

        # Find the highest font index
        font_indices = re.findall(r'\\f(\d+)', fonttbl_content)
        max_font_idx = max(int(idx) for idx in font_indices) if font_indices else 0
        new_font_idx = max_font_idx + 1

        # Create new font entry and insert before closing brace of fonttbl
        new_font_entry = '{\\f' + str(new_font_idx) + ' \\fnil\\fcharset0 ' + new_font + ';}'
        new_fonttbl = fonttbl_content[:-1] + new_font_entry + '}'

        # Replace font table safely without breaking body_start
        body_start = fonttbl_match.end()
        body = rtf_str[body_start:]
        prefix = rtf_str[:fonttbl_match.start()] + new_fonttbl

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
                    if skip_depth != -1 and group_depth == skip_depth:
                        skip_depth = -1
                    group_depth -= 1
                else:
                    val = token_value.strip().lower()
                    if val.startswith('\\colortbl') or val.startswith('\\stylesheet') or val.startswith('\\info') or val.startswith('\\*'):
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
        translated_lines = [line.strip() for line in new_text.replace('\r\n', '\n').split('\n') if line.strip()]

        # 4. Map translated lines to original text-containing paragraphs
        new_paragraphs = []
        translated_idx = 0
        applied_font = False

        for idx, (p_tokens, p_break) in enumerate(paragraphs):
            # Check if this paragraph contains text in original
            has_text = any(idx == orig_idx for orig_idx, _ in text_paragraphs)
            
            if has_text:
                if translated_idx < len(translated_lines):
                    trans_line = translated_lines[translated_idx]
                    translated_idx += 1
                else:
                    trans_line = '' # Clear the remaining text to avoid mixing languages
                
                # Calculate total original text length in this paragraph
                orig_text_parts = []
                for t_type, t_val in p_tokens:
                    if t_type == 'text':
                        orig_text_parts.append(t_val)
                orig_text_full = ''.join(orig_text_parts)
                
                # Replace plain text tokens in this paragraph
                new_p_tokens = []
                text_tokens_in_p = sum(1 for t, v in p_tokens if t == 'text' and v.strip())
                text_token_idx = 0
                trans_remaining = trans_line
                
                for t_type, t_val in p_tokens:
                    if t_type == 'text' and t_val.strip():
                        text_token_idx += 1
                        if not applied_font:
                            # Insert font change control word
                            new_p_tokens.append(('control', f'\\f{new_font_idx} '))
                            applied_font = True
                        
                        if text_token_idx == text_tokens_in_p:
                            new_p_tokens.append(('text', RTFManipulator._escape_rtf_text(trans_remaining)))
                            trans_remaining = ''
                        else:
                            ratio = len(t_val) / max(len(orig_text_full), 1)
                            chars_to_take = max(1, int(len(trans_line) * ratio))
                            chunk = trans_remaining[:chars_to_take]
                            trans_remaining = trans_remaining[chars_to_take:]
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
            elif ord(ch) > 127:
                # Unicode escape: \uN?
                result.append(f'\\u{ord(ch)}?')
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
