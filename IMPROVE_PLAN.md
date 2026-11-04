# Kế hoạch Cải tiến Tốc độ Phản hồi Direct-Trans
*(Benchmarking & Architectural Optimization dựa trên đối sánh QTranslate)*

---

## 1. Mục tiêu & Chỉ số Đo lường (KPIs)

- **Mục tiêu chính:** Tối ưu hóa luồng xử lý kỹ thuật của Direct-Trans để đạt tốc độ phản hồi tức thì ngang ngửa QTranslate mà **không cần cắt giảm chất lượng hay độ chi tiết của System Prompt**.
- **Mức giảm độ trễ kỳ vọng:** **300ms – 530ms** cho mỗi lần dịch phím tắt.

| Thành phần | Hiện trạng (Baseline) | Sau tối ưu (Target) | Thời gian tiết kiệm |
|---|---|---|---|
| **Mở kết nối TCP/TLS** | 150ms – 350ms (mỗi lần dịch) | **0ms** (tái sử dụng socket) | **~150ms – 350ms** |
| **Đồng bộ UI Barrier** | 50ms – 150ms (chặn luồng nền) | **0ms** (bắn API song song UI) | **~50ms – 150ms** |
| **Bắt Clipboard Sequence** | 50ms (chu kỳ lặp đầu tiên) | **20ms** (quét tần số cao) | **~30ms** |
| **Tổng độ trễ kỹ thuật giảm** | — | — | **~230ms – 530ms** |

---

## 2. Chi tiết 3 Hạng mục Cải tiến Kỹ thuật

### Hạng mục 1: Tái sử dụng HTTP Connection Pooling (Keep-Alive)
- **Vị trí file:** [`src/translator.py`](file:///E:/Github/direct-trans/src/translator.py)
- **Vấn đề hiện tại:**
  Trong `BaseHTTPTranslator._make_request_with_retry()`, ứng dụng đang gọi `requests.post()` và `requests.get()` trực tiếp ở cấp module. Mỗi lần bấm phím dịch là một lần mở kết nối mới hoàn toàn: truy vấn DNS, bắt tay 3 bước TCP SYN-ACK, và đàm phán bảo mật TLS 1.3 với máy chủ Google/Groq/Mistral (thường đặt ở nước ngoài).
- **Giải pháp kỹ thuật:**
  1. Khởi tạo một `requests.Session()` dùng chung trong `BaseHTTPTranslator` (hoặc cấp `TranslationManager`).
  2. Gắn `HTTPAdapter` với cấu hình connection pool:
     ```python
     adapter = requests.adapters.HTTPAdapter(
         pool_connections=4,
         pool_maxsize=8,
         max_retries=urllib3.util.Retry(total=0)  # Để BaseHTTPTranslator tự quản lý retry
     )
     self.session.mount("https://", adapter)
     self.session.mount("http://", adapter)
     ```
  3. Thay thế toàn bộ lệnh gọi `requests.post(...)` và `requests.get(...)` bằng `self.session.post(...)` và `self.session.get(...)`.
  4. Đảm bảo đóng session sạch sẽ khi ứng dụng tắt (`session.close()`).

---

### Hạng mục 2: Xóa bỏ Rào cản Đồng bộ Giao diện (`popup_event.wait()`)
- **Vị trí file:** [`src/main.py`](file:///E:/Github/direct-trans/src/main.py)
- **Vấn đề hiện tại:**
  Trong hàm `DirectTransApp._process_translation()` (khoảng dòng 427-450):
  ```python
  if mode == MODE_POPUP:
      def create_popup():
          ...
          popup_event.set()
      self._run_on_main(create_popup)
      popup_event.wait(timeout=5.0)  # <-- Luồng dịch bị dừng chờ UI Qt vẽ xong!
  ```
  Background thread bị dừng chờ (sleep/wait) cho tới khi Qt Main Thread hoàn tất việc khởi tạo đối tượng `PopupWindow` và hiển thị giao diện loading. Nếu Qt Main Thread đang bận xử lý đồ họa hoặc sự kiện chuột, luồng dịch bị trễ thêm 50ms – 150ms trước khi bắt đầu gửi request mạng.
- **Giải pháp kỹ thuật:**
  1. Bỏ hoàn toàn `popup_event = threading.Event()` và lệnh `popup_event.wait(5.0)`.
  2. Cho phép background thread tiếp tục chạy ngay lập tức sau lệnh `self._run_on_main(create_popup)`.
  3. Dùng cơ chế container an toàn luồng (`popup_holder = {"popup": None}` hoặc signal/slot) để kết nối kết quả từ luồng nền về giao diện popup đang mở.
  4. Khi API dịch xong, gửi kết quả về main thread để popup hiển thị hoặc fallback tạo popup mới nếu cửa sổ chưa kịp vẽ xong.

---

### Hạng mục 3: Tăng tần số quét Clipboard Sequence
- **Vị trí file:** [`src/clipboard_util.py`](file:///E:/Github/direct-trans/src/clipboard_util.py)
- **Vấn đề hiện tại:**
  Trong hàm `ClipboardUtil.get_selected_text()`:
  ```python
  for _ in range(12):
      time.sleep(0.05)  # 50ms mỗi vòng lặp
      if user32.GetClipboardSequenceNumber() != seq_before:
          changed = True
          break
  ```
  Hầu hết các phần mềm Windows render clipboard trong vòng 10ms – 25ms sau khi nhận `Ctrl+C`. Chu kỳ sleep 50ms khiến Direct-Trans luôn phải chờ trọn vẹn 50ms mới nhận diện được dữ liệu.
- **Giải pháp kỹ thuật:**
  1. Giảm khoảng cách sleep xuống **20ms** (`time.sleep(0.02)` giống như `pollIntervalMs = 20L` của QTranslate).
  2. Tăng số vòng lặp lên **30 lần** để giữ nguyên tổng thời gian timeout tối đa là **600ms** (`30 * 0.02 = 0.6s`):
     ```python
     for _ in range(30):
         time.sleep(0.02)
         if user32.GetClipboardSequenceNumber() != seq_before:
             changed = True
             break
     ```

---

## 3. Hạng mục Mở rộng Tùy chọn (Optional Enhancements)

### Tắt Thinking Budget cho Reasoning Models (Gemini 2.0 / Groq DeepSeek R1)
- **Vấn đề:** Khi người dùng chọn các model thế hệ mới có tính năng reasoning, model sẽ tốn 1 – 3 giây để "suy nghĩ nội tâm" (thẻ `<think>...</think>`) trước khi xuất bản dịch.
- **Giải pháp:**
  - Trong payload gửi tới Gemini: thêm `"generationConfig": {"thinkingConfig": {"thinkingBudget": 0}}`.
  - Trong payload gửi tới Groq / OpenAI compatible: thêm `"reasoning_effort": "low"` hoặc `"max_completion_tokens"` phù hợp.

---

## 4. Kế hoạch Triển khai Từng bước (Step-by-Step Execution Plan)

### Bước 1: Chuẩn bị & Kiểm thử Cơ sở (Baseline Testing)
- [ ] Chạy bộ test hiện tại để đảm bảo hệ thống đang xanh: `python -m pytest tests/ -q`
- [ ] Đo đạc thời gian phản hồi trung bình trước khi sửa (ghi log timestamp tại lúc ấn hotkey và lúc nhận response).

### Bước 2: Triển khai Session Pooling trong `src/translator.py`
- [ ] Thêm `requests.Session` vào `BaseHTTPTranslator`.
- [ ] Cập nhật phương thức `_make_request_with_retry` sử dụng session.
- [ ] Thêm phương thức `close()` để giải phóng kết nối khi thoát app.
- [ ] Chạy lại `tests/test_translator.py`.

### Bước 3: Triển khai Async Dispatch trong `src/main.py`
- [ ] Gỡ bỏ `popup_event.wait()` trong `_process_translation()`.
- [ ] Cập nhật cơ chế truyền kết quả dịch về `PopupWindow` mà không gây deadlock hay race condition.
- [ ] Kiểm thử thủ công: Bấm phím tắt dịch văn bản nhanh liên tục để kiểm tra độ mượt của popup loading.

### Bước 4: Tinh chỉnh Polling trong `src/clipboard_util.py`
- [ ] Cập nhật loop sleep: 30 lần x 0.02s.
- [ ] Kiểm tra tính tương thích khi copy từ các app nặng (Excel, Word, Visual Studio).

### Bước 5: Kiểm chứng Toàn diện & Đóng gói
- [ ] Chạy toàn bộ test suite: `python -m pytest tests/ -q`
- [ ] Test thực tế với cùng provider và model để so sánh trực quan với QTranslate.
- [ ] Cập nhật `CHANGELOG.md` và đóng gói thử nghiệm bằng `.\build.bat`.

---

## 5. Đánh giá Rủi ro & Phương án Dự phòng (Risk & Rollback)

- **Rủi ro rò rỉ socket hoặc kết nối hỏng (Broken Pipe):** Khi máy tính sleep/wake, session HTTP cũ có thể bị timeout ngầm.
  - *Biện pháp:* `BaseHTTPTranslator` đã có sẵn cơ chế retry; nếu session gặp `ConnectionError`, tự động đóng và khởi tạo session mới.
- **Rủi ro Race Condition giữa Popup và Translation Thread:**
  - *Biện pháp:* Đảm bảo mọi thao tác can thiệp vào UI đều đi qua `self._run_on_main()`, kiểm tra `popup.is_open()` trước khi gán dữ liệu.
