# Báo Cáo Các Vấn Đề Code Logic & Hướng Xử Lý — DirectTrans v1.0.3

Tài liệu này tổng hợp các vấn đề được phát hiện trong mã nguồn DirectTrans v1.0.3 và đề xuất các hướng giải quyết tương ứng.

---

## 🚨 PHẦN A: VẤN ĐỀ NGHIÊM TRỌNG (Cần xử lý ngay)

### A1. Định nghĩa trùng lặp hàm mã hóa/giải mã API Key
- **File:** `config.py` (dòng 49-74 và 119-138)
- **Vấn đề:** Hàm `_encrypt_key` và `_decrypt_key` bị định nghĩa 2 lần (lần 1 dùng base64, lần 2 dùng hex). Bản hex sẽ đè lên bản base64. Nếu user cập nhật lên bản này và config cũ dùng base64, việc giải mã sẽ thất bại, rơi vào nhánh `except` và trả về plaintext dạng base64. User sẽ mất key. Lỗi bị nuốt im lặng và code base64 trở thành dead code.
- **Hướng xử lý:** Xóa bỏ đoạn mã dùng base64 (giữ lại bản hex vì hiện đại hơn). Thêm `logging.warning` khi decrypt thất bại để thông báo cho người dùng biết key có thể đã bị hỏng, thay vì nuốt lỗi.

### A2. Rò rỉ API Key qua cache khi dịch vụ gặp lỗi
- **File:** `translator.py` (dòng 265-273)
- **Vấn đề:** Phương thức `TranslationManager.translate()` ghi `backend.api_key` trực tiếp lên instance của singleton `backend`. Nếu provider gặp lỗi và fallback sang provider khác, key cũ không bị reset. Hơn nữa, vì `self.backends` là singleton dict, key vẫn tồn tại trong RAM cho đến khi tắt app (hoặc bị GC).
- **Hướng xử lý:** Tạo backend mới cho mỗi lần dịch thay vì dùng singleton, **hoặc** truyền key trực tiếp qua tham số của hàm `translate(text, target_lang, api_key=...)` để không lưu trữ state.

### A3. Logic fallback chọn "google_free" trước provider chính
- **File:** `translator.py` (dòng 244-247 và 259)
- **Vấn đề:** Khi `fallback_enabled=True`, nếu provider chính là Gemini nhưng chưa cấu hình key, hệ thống skip sang Groq -> Mistral -> Google Free (logic đúng). Tuy nhiên, nếu user chọn "Google Free" làm provider chính, nó thử đầu tiên, thất bại thì fallback sang Gemini (nếu có key). Vấn đề lớn nhất ở đây là comment bị thiếu số (`# 2.`), cho thấy dấu hiệu refactor dang dở gây khó đọc.
- **Hướng xử lý:** Dọn dẹp lại code, bỏ các comment rỗng hoặc đánh số lại cho logic và minh bạch hơn. Thêm unit test cho fallback chain.

### A4. Hàm `is_first_run()` kiểm tra sai logic
- **File:** `config.py` (dòng 242-245)
- **Vấn đề:** Hàm này dùng để kiểm tra lần chạy đầu tiên nhưng lại chỉ check xem có key của Gemini hay không. Nếu user chỉ dùng Groq, app vẫn báo là "first run". Hàm này dường như là dead code vì không được gọi trong codebase.
- **Hướng xử lý:** Xóa bỏ hàm `is_first_run()` nếu không còn sử dụng để dọn dẹp codebase.

---

## ⚠️ PHẦN B: VẤN ĐỀ QUAN TRỌNG (Nên xử lý trong v1.0.4)

### B1. Race condition khi người dùng đổi ngôn ngữ UI
- **File:** `settings_window.py` (dòng 229-234, 266-269)
- **Vấn đề:** Phương thức `update_ui_language` tự động lưu config (`self.config.save()`) khi người dùng đổi ngôn ngữ hiển thị. Đây là side-effect không mong muốn vì người dùng chỉ muốn đổi giao diện chứ không có ý định lưu đè các thay đổi API key chưa lưu khác.
- **Hướng xử lý:** Tách biệt logic thay đổi ngôn ngữ hiển thị và logic lưu config. Không tự động gọi `save()` khi chỉ thay đổi UI language.

### B2. Phím tắt bị kích hoạt không chủ đích (Race condition do Popup)
- **File:** `main.py` (dòng 168-190)
- **Vấn đề:** Hàm `_on_hotkey` có debounce 1 giây nhưng nếu người dùng giữ phím tắt liên tục trong lúc popup đang xử lý hiển thị, thread mới có thể được tạo ra liên tục khiến nhiều popup chồng lên nhau hoặc đóng nhầm popup đang đọc.
- **Hướng xử lý:** Thêm biến khóa (lock) `_processing_lock` (dùng `threading.Lock`) hoặc thêm kiểm tra `if self._processing: return` ở đầu hàm `_on_hotkey`.

### B3. Logic `replace_text_preserve_format` chia text sai tỷ lệ
- **File:** `clipboard_util.py` (dòng 379-383)
- **Vấn đề:** Khi chia đoạn dịch vào các text-token gốc theo tỷ lệ chiều dài, nếu bản dịch ngắn hơn bản gốc, một số token sẽ bị rỗng. Nếu dịch dài hơn, phần dư cuối cùng bị cắt bỏ gây mất nội dung. Cách làm này cũng có thể phá vỡ escape sequence của RTF.
- **Hướng xử lý:** Thay đổi logic: Đặt toàn bộ `trans_line` (bản dịch) vào text-token đầu tiên có nội dung, các token sau gán bằng chuỗi rỗng để bảo toàn định dạng mà không bị mất chữ.

### B4. Khôi phục Clipboard có thể gây mất dữ liệu giữa chừng
- **File:** `clipboard_util.py` (dòng 88, 116, 157)
- **Vấn đề:** Hàm `replace_selected_text` ghi đè clipboard bằng dict `{CF_RTF, CF_UNICODETEXT}` rồi simulate `Ctrl+V`. Việc này tạo ra một khoảng thời gian (khoảng 200ms) mà clipboard đang chứa RTF mới trước khi được khôi phục. Nếu user thực hiện thao tác paste trong thời gian này, dữ liệu sẽ bị sai.
- **Hướng xử lý:** Ghi nhận rủi ro này và xem xét tối ưu latency (có thể dùng Win32 SendInput thay vì sleep). Cần comment rõ ràng để theo dõi.

### B5. Lỗi phân tích nested groups trong RTF khi gặp \uN với fallback
- **File:** `clipboard_util.py` (dòng 431-451)
- **Vấn đề:** Logic skip các ký tự fallback sau `\uN` hoạt động theo biến `uc_value`. Tuy nhiên nếu `\uc` thay đổi giữa chừng thì position có thể bị tính toán sai, mặc dù đây là edge-case rất hiếm gặp.
- **Hướng xử lý:** Không cần ưu tiên cao nhưng có thể tái cấu trúc nhẹ RTF tokenizer để theo dõi `uc_value` chặt chẽ hơn trong các group con.

### B6. Thiếu validation cho hotkey từ config cũ
- **File:** `hotkey_manager.py` (dòng 117-120)
- **Vấn đề:** Nếu config từ bản cũ bị lỗi (ví dụ chứa ký tự lạ), hàm `parse_hotkey` sẽ dịch thành phím mặc định rác (`vk = 63`) dẫn đến việc đăng ký nhầm phím tắt.
- **Hướng xử lý:** Bổ sung hàm validate định dạng hotkey (`key_combo`) trước khi tải hoặc lưu vào config.

---

## 💡 PHẦN C: CẢI THIỆN CHẤT LƯỢNG (Code Quality)

### C1. Code duplication tại UI cấu hình API
- **File:** `api_config_tab.py` (dòng 200-342)
- **Vấn đề:** Ba hàm `_build_gemini_frame`, `_build_groq_frame`, `_build_mistral_frame` gần như giống hệt nhau.
- **Hướng xử lý:** Gộp thành 1 hàm `_build_provider_frame(provider_name, ...)` để giảm bớt ~140 dòng code lặp.

### C2. Magic strings rải rác
- **Vấn đề:** Các chuỗi như `"popup"`, `"replace"`, `"gemini"` xuất hiện nhiều nơi trong file.
- **Hướng xử lý:** Đưa tất cả vào file `constants.py` hoặc sử dụng `enum`.

### C3. `_resolve_config_path` hoạt động sai ở môi trường Dev
- **File:** `config.py` (dòng 80-81)
- **Vấn đề:** Khi chạy dev, path của config bị trỏ ra thư mục cha (project root). Nếu project nằm trong thư mục chỉ đọc, app sẽ crash khi `save()`.
- **Hướng xử lý:** Đổi logic luôn trỏ lưu config vào `%APPDATA%/DirectTrans/` để đồng nhất giữa môi trường Dev và Release.

### C4. Lazy import bên trong hàm gây khó đọc
- **File:** `config.py`, `clipboard_util.py`, `main.py`, `popup_window.py`
- **Vấn đề:** Import module bên trong hàm (để tránh lỗi khi bundle PyInstaller) làm code khó theo dõi.
- **Hướng xử lý:** Có thể giữ nguyên nếu đây là workaround cho PyInstaller, nhưng cần thêm comment giải thích rõ lý do.

### C5. Thiếu Rate limit và Timeout toàn cục
- **File:** `translator.py`
- **Vấn đề:** Timeout chỉ có cho POST request, không có giới hạn (rate limit) giữa các provider. Fallback khi bị HTTP 429 có thể làm khuếch đại vấn đề.
- **Hướng xử lý:** Triển khai cơ chế backoff / rate limit cho `BaseHTTPTranslator`.

### C6. Xử lý xóa tag `<think>` chưa tối ưu
- **File:** `translator.py` (dòng 278-281)
- **Vấn đề:** Kiểm tra `if '<think>' in result` rồi mới chạy Regex `.sub()` là dư thừa.
- **Hướng xử lý:** Chạy trực tiếp `_re.sub(..., count=1)` gọn gàng hơn.

### C7. Hardcode message tiếng Việt trong Main
- **File:** `main.py` (dòng 213, 218, 256)
- **Vấn đề:** Lỗi hiển thị cứng bằng tiếng Việt ("Không thể truy cập clipboard."). Không hỗ trợ i18n.
- **Hướng xử lý:** Áp dụng hệ thống TRANSLATIONS dict cho các error message ở file main.py.

### C8. Lỗi treo khi dừng `HotkeyManager`
- **File:** `hotkey_manager.py` (dòng 150-155)
- **Vấn đề:** Hàm `stop()` gọi `PostThreadMessageW(WM_QUIT)` nhưng nếu thread đang bận xử lý message khác thì có thể phải đợi hết `timeout=1.0` giây.
- **Hướng xử lý:** Chấp nhận mức timeout này, hoặc cải thiện message loop.

### C9. Crash có thể xảy ra khi gọi os._exit() và luồng Tray
- **File:** `main.py`
- **Vấn đề:** System tray chạy daemon thread, Tkinter main loop chạy main thread. Đóng app dùng `os._exit(0)` thay vì `sys.exit(0)`.
- **Hướng xử lý:** Nên thêm docstring giải thích lý do phải force kill toàn bộ thread bằng `os._exit`.

### C10. Cache font fallback vĩnh viễn trong session
- **File:** `font_mapper.py` (dòng 91-93)
- **Vấn đề:** Nếu winreg bị lỗi đọc tạm thời, `FontMapper` đánh dấu lỗi font đó và cache `False` suốt phiên làm việc, khiến app vĩnh viễn dùng font dự phòng.
- **Hướng xử lý:** Cân nhắc không cache kết quả `False` hoặc có cơ chế retry sau một khoảng thời gian.

---

## 🔐 PHẦN D: BẢO MẬT (Security)

1. **Nuốt Exception khi Decrypt (D2):** Không được bỏ qua exception ở hàm `_decrypt_key`. Nếu ciphertext hỏng, trả về string rỗng và log lỗi để tránh user lưu đè chuỗi rác.
2. **Rate Limit (D3):** Bổ sung giới hạn số lượng request khi ấn hotkey liên tục để tránh lạm dụng dịch vụ, gây khóa API key hoặc tăng chi phí bất thường.
3. **Copy-protection API Key (D4):** Ô nhập API key trong mục cài đặt đang dùng `show='•'` nhưng user vẫn copy được ra clipboard (Ctrl+C). Cần set `state='readonly'` hoặc thiết lập xóa clipboard.
4. **Giới hạn DPAPI (D1):** Ghi nhận DPAPI chỉ an toàn với user hiện tại, malware cùng phân quyền vẫn có thể lấy được key. (Mức độ bảo vệ trung bình, chấp nhận được).

---

## 🎯 DANH SÁCH HÀNH ĐỘNG ƯU TIÊN (Action Items)

| Ưu tiên | Nhiệm vụ | Khu vực | Đánh giá | Trạng thái |
| :--- | :--- | :--- | :--- | :--- |
| **1** | Sửa lỗi trùng lặp `_encrypt_key` & `_decrypt_key` (bỏ base64) | `config.py` | 🔴 Critical | ✅ Đã sửa (phiên trước) |
| **2** | Sửa `_processing` flag không reset sau dịch thành công | `main.py` | 🔴 Critical | ✅ Đã sửa |
| **3** | Refactor gộp 3 hàm build cấu hình Provider | `api_config_tab.py` | 🔴 High | ✅ Đã sửa (phiên trước) |
| **4** | Sửa rò rỉ API key khi truyền tham số thay vì gán vào instance | `translator.py` | 🟠 Medium | ✅ Đã sửa (phiên trước) |
| **5** | Sửa save() side-effect khi đổi UI language | `settings_window.py` | 🟠 Medium | ✅ Đã sửa |
| **6** | Thêm cảnh báo (Log warning) khi decrypt key bị lỗi | `config.py` | 🟠 Medium | ✅ Đã sửa (phiên trước) |
| **7** | Bổ sung i18n keys thiếu cho ko/zh/ja | `i18n.py` | 🟡 Low | ✅ Đã sửa |
| **8** | Xóa hàm `is_first_run` (Dead code) | `config.py` | 🟡 Low | ✅ Đã xóa (phiên trước) |
| **9** | Thread-safety cho FontMapper | `font_mapper.py` | 🟡 Low | ✅ Đã sửa |
| **10** | Tray menu cập nhật ngôn ngữ động | `tray.py` | 🟡 Low | ✅ Đã sửa |
| **11** | Move lazy `import re` ra top-level | `translator.py` | 🟡 Low | ✅ Đã sửa |
| **12** | Sửa thuật toán chia nhỏ bản dịch để thay thế RTF gốc | `clipboard_util.py`| 🟠 Medium | ⏳ Chưa xử lý |
| **13** | Bổ sung Unit Test cho cơ chế Fallback | `translator.py` | 🔴 High | ⏳ Chưa xử lý |
| **14** | Thêm docs giải thích các quyết định trong code | Nhiều file | 🟡 Low | ⏳ Chưa xử lý |
