# DirectTrans Hand-off Document (Phiên bản v1.0)

## 0.00. Các cải tiến và sửa lỗi trong phiên bản v1.1.1
- **Xóa bỏ Cache Dịch thuật**: Khắc phục hiện tượng dịch ngay lập tức một câu đã dịch bằng cách gỡ bỏ triệt để cơ chế cache ngầm (LRU cache trong `translator.py` và các thiết lập trong `config.py`). Từ nay, mọi yêu cầu dịch thuật đều được gọi mới hoàn toàn đến nhà cung cấp API, đáp ứng đúng yêu cầu của hệ thống là không bao giờ sử dụng lại bản dịch cũ.

## 0.00. Các cải tiến và sửa lỗi trong phiên bản v1.1.0
- **User Manual Overhaul**: Viết lại toàn bộ hướng dẫn sử dụng offline (`user_manual.html`) sang tiếng Anh với văn phong khách quan, ngắn gọn. Mở rộng chiều rộng container lên 1400px (chiếm 95% màn hình) để tận dụng tối đa không gian hiển thị trên máy tính.
- **Updated Settings Imagery**: Chuyển sang sử dụng hình ảnh chụp màn hình thực tế (screenshots) thay vì CSS mockups cho phần hướng dẫn cấu hình API Key và Popup Mode để người dùng dễ hình dung đúng giao diện thực.

## 0.0. Các cải tiến và sửa lỗi trong phiên bản v1.0.9
- **Smart Model Filtering v2**: Nâng cấp hệ thống lọc model của "Load Models" thành bộ lọc ba lớp (Whitelist + Blacklist + Regex) để dọn sạch hoàn toàn các model rác (TTS, Embed, Code, Math, Preview...) và chỉ giữ lại những model cốt lõi chuyên dụng cho dịch thuật.
  - Bổ sung `gpt` vào Whitelist và đặt mặc định cho Groq là `gpt-oss-120b`.
  - Chặn thêm các model `vibe`, `tiny`, `small`, `open` của Mistral, chỉ ưu tiên `large` và `medium`.
  - Khắc phục lỗi model `openai/gpt-oss-120b` của Groq bị loại bỏ oan do blacklist của Mistral.
- **Groq 403 Bypass**: Cập nhật logic API call tới máy chủ Groq bằng cách thêm fake `User-Agent`, xử lý dứt điểm tình trạng bị từ chối truy cập (HTTP 403) với các key mới.
- **Sequential API Key Testing**: Nâng cấp chức năng của nút "Test". Thay vì chỉ test model đang chọn, giờ đây hệ thống sẽ quét và gửi test request lần lượt tới toàn bộ các models đang có trong Combobox. Kết quả cuối cùng sẽ được gạn lọc lại một lần nữa, đảm bảo Combobox chỉ chứa các model phản hồi 100% thành công.
- **UI & UX**: Khóa các nút Load/Save/Test và Combobox trong khi đang Test model để tránh xung đột; Nới rộng nhãn báo trạng thái; Đổi link API key của Mistral thành `/api-keys`.

## 0. Các cải tiến và sửa lỗi trong phiên bản v1.0.2
- **Đổi tên Provider**: Cập nhật provider từ Grok (xAI) sang **GroqCloud**. Các endpoint API và link đăng ký key đã được chuyển sang hệ thống của Groq (`api.groq.com/openai/v1`).
- **Translation Filter**: Bổ sung bộ lọc bằng regex để tự động xóa các đoạn nội suy (reasoning block nằm trong thẻ `<think>...</think>`) do các model như Qwen sinh ra trên Groq. Điều này đảm bảo kết quả dịch luôn sạch sẽ, không bị lẫn các câu lệnh suy nghĩ của AI.
- **Lọc Model Thông minh (Smart Model Filtering)**: Khi dùng tính năng Load Models cho Groq và Mistral, ứng dụng sẽ tự động lọc và loại bỏ các model không dùng để chat/dịch thuật (như `embed`, `moderation`, `whisper`), giúp danh sách trả về gọn gàng và chính xác hơn.

## 0.1. Các cải tiến và sửa lỗi trong phiên bản v1.0
- **Tích hợp Groq & Mistral**: Thêm 2 dịch vụ AI mới hỗ trợ dịch thuật với free-tier API. Các model mặc định được cấu hình là `qwen/qwen3-32b` (cho Groq) và `mistral-large-latest` (cho Mistral).
- **Giao diện Cài đặt Động (Dynamic UI)**: Tái thiết kế mục cấu hình API Key. Giờ đây, giao diện chỉ hiển thị duy nhất trường nhập API key và chọn model của dịch vụ (Provider) đang được kích hoạt. Khi đổi sang provider khác, form cũ sẽ tự động ẩn đi. Khi chọn Google Free, toàn bộ form API được dọn dẹp sạch sẽ để tránh gây rối mắt.
- **Tính năng Load Models**: Hỗ trợ fetch model động từ API đối với cả Groq và Mistral. Bổ sung cơ chế khóa an toàn (UI Lock): Toàn bộ model dropdown, nút "Load Models", nút "Test" và nút "Lưu Key" sẽ bị vô hiệu hóa (disabled) trong lúc hệ thống đang thực hiện fetch API từ máy chủ để tránh người dùng thao tác sai (race conditions).

## 0.1. Các cải tiến và sửa lỗi trong phiên bản v0.4.6 & v0.4.5
- **Khắc phục lỗi mất phím tắt âm thầm (v0.4.6)**: Thay thế thư viện `keyboard` (dựa trên Low-Level Hook vốn dễ bị hệ điều hành tắt ngầm do `LowLevelHooksTimeout`) bằng API gốc của Windows `RegisterHotKey` thông qua `ctypes`. Sự thay đổi này đảm bảo phím tắt 100% không bị rớt kể cả khi máy đang bị quá tải hoặc để máy sleep lâu ngày. Thư viện `keyboard` vẫn được giữ lại nhưng chỉ dùng phục vụ UI thu âm phím tắt ở màn hình Cài đặt.
- **Fix lỗi DevTools & kẹt phím Shift (v0.4.5)**: Ép hệ điều hành "nhả" toàn bộ phím modifier (`Shift`, `Ctrl`) bị kẹt trước khi mô phỏng bấm `Ctrl+C` để copy, tránh trình duyệt hiểu nhầm là bấm `Ctrl+Shift+C` và mở DevTools.
## 1. Các cải tiến và sửa lỗi trong phiên bản v0.2

### 1.1. Ngăn chặn Trùng Phím tắt (Yêu cầu 1)
*   **Chi tiết**: Thêm logic kiểm tra trùng lặp phím tắt trong hàm `do_save` của Dialog phím tắt.
*   **Hoạt động**: Khi người dùng nhấn nút Thêm hoặc Lưu phím tắt, ứng dụng sẽ quét danh sách phím tắt hiện có trong config (ngoại trừ chính phím tắt đang sửa nếu đang ở chế độ Edit). Nếu tổ hợp phím (đã chuẩn hóa viết thường) đã được gán trước đó, hệ thống sẽ hiện thông báo cảnh báo: `"phím tắt đã được sử dụng"` và chặn không cho lưu.

### 1.2. Chuyển đổi Giao diện sang Light Mode (Yêu cầu 2)
*   **Chi tiết**: Thay đổi toàn bộ các hằng số màu sắc sang bảng màu **Catppuccin Latte** dịu mắt cho cả cửa sổ Cài đặt (`src/settings_window.py`) và cửa sổ Popup kết quả dịch (`src/popup_window.py`).
*   **Tối ưu tương phản**: Đổi màu chữ của các nút Lưu, Copy, Thay thế (nền xanh lá/cam) sang màu trắng `#ffffff` thay vì màu nền `BASE` để đảm bảo chữ nổi bật và dễ đọc trong môi trường sáng.

### 1.3. Cố định Kích thước & Căn lề Đối xứng (Yêu cầu 3)
*   **Chi tiết**: 
    *   Đặt kích thước settings window cố định chiều rộng ở `540x650` và chỉ cho phép thay đổi chiều cao (`self.window.resizable(False, True)`).
    *   Đồng bộ chiều rộng của `scroll_frame` bên trong với chiều rộng của `canvas` thông qua việc bind sự kiện `<Configure>` của canvas:
        ```python
        canvas_window_id = canvas.create_window((0, 0), window=self.scroll_frame, anchor='nw')
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_window_id, width=e.width))
        ```
    *   Các nhóm khối giao diện (`LabelFrame`) cách đều hai biên trái-phải 16px đối xứng hoàn hảo, giải quyết triệt để khoảng trống thừa màu tối ở lề bên phải.

### 1.4. Khắc phục Lỗi Mất Ký Tự khi Dịch trong PowerPoint (Yêu cầu 4)
*   **Nguyên nhân gốc rễ**: PowerPoint khi sao chép văn bản nhiều dòng chứa các ký tự tiếng Việt có dấu sẽ mã hóa chúng dưới dạng Unicode Escape `\uN?` hoặc Hex Escape `\'XX`. Bộ tokenize RTF cũ coi các chuỗi escape này là token `control` nên giữ nguyên chúng và chèn đè lên bản dịch mới, làm sai lệch tỉ lệ phân bổ ký tự và chèn lẫn lộn chữ gốc vào bản dịch mới, gây ra lỗi hiển thị mất ký tự, lẫn chữ và sai cấu trúc dòng.
*   **Giải pháp**:
    *   Cập nhật hàm `_tokenize_rtf` trong `src/clipboard_util.py` to parse các chuỗi `\uN?` và `\'XX` thành token `text` thông thường.
    *   Theo dõi giá trị `uc_value` động để bỏ qua chính xác số byte của ký tự fallback.
    *   Văn bản gốc được tokenize sạch sẽ, giúp việc tính toán độ dài và map bản dịch mới diễn ra chính xác 100%. Các ký tự Unicode/Hex của bản gốc được loại bỏ hoàn toàn khỏi RTF dịch mới, đảm bảo PowerPoint hiển thị đầy đủ bản dịch mà không mất ký tự nào.

### 1.5. Gỡ bỏ Tùy chọn Không Cần thiết (Yêu cầu 5)
*   **Chi tiết**: Gỡ bỏ 2 checkbox "Fallback tự động" và "Cache bản dịch" khỏi UI `_create_options_section` để tối giản hóa giao diện. Các tính năng này mặc định vẫn được bật ngầm trong `config.json` để tối ưu hóa tốc độ và độ tin cậy dịch thuật.

### 1.6. Cơ chế Lưu Cài đặt Tức thì - Auto-Save (Yêu cầu 6)
*   **Chi tiết**: 
    *   Xóa bỏ hoàn toàn cụm nút "Lưu" và "Hủy" chính ở dưới cùng của Settings window.
    *   Tự động lưu và áp dụng ngay lập tức các thay đổi lên hệ thống:
        *   Thay đổi **Nguồn dịch**: Tự động lưu khi chọn trong combobox.
        *   Thay đổi **API Key**: Lưu tức thì khi người dùng nhấn nút "Lưu" cục bộ bên cạnh entry.
        *   Thay đổi **Phím tắt**: Tự động lưu và cập nhật hotkey hook khi Thêm/Sửa phím tắt thành công, hoặc khi nhấn nút xóa `✕`.
        *   Thay đổi **Khởi động cùng Windows**: Lưu tức thì khi nhấn click vào checkbox.

### 1.7. Khắc phục Lỗi Dịch Đoạn Văn Bị Gộp Dòng và Sót Tiếng Anh (Yêu cầu 7)
*   **Chi tiết**: Sửa lỗi khi dùng Google Translate dịch văn bản trong text box PowerPoint, văn bản dịch bị gộp thành 1 dòng, và tiếng Anh gốc ở cuối bị sót lại không thay thế hết.
*   **Nguyên nhân gốc rễ**: 
    1. PowerPoint dùng ký tự `\x0b` (Vertical Tab) thay cho `\n` để ngắt đoạn. Các API như Google Translate thường bỏ qua ký tự lạ này và nối toàn bộ thành 1 câu, trả về ít dòng hơn ban đầu.
    2. Thuật toán phân bổ RTF cũ (`RTFManipulator`) gặp lỗi thiết kế: nếu số dòng trả về ít hơn số đoạn có văn bản, nó sẽ bỏ mặc các đoạn dưới cùng không thèm xóa, làm tiếng Anh cũ ở lại.
    3. Mã nguồn cũ vô tình xem các ký tự `;` bên trong khối định dạng `\colortbl` là text thường để thay thế, sinh ra chữ rác như `ere?` trên bản dịch.
*   **Giải pháp**:
    *   **Chuẩn hóa Line breaks**: Replace toàn bộ `\x0b`, `\r\n` thành `\n` chuẩn khi đọc từ Windows Clipboard trước khi mang đi dịch.
    *   **Clear text thừa**: Trong lúc chèn bản dịch vào RTF, nếu bản dịch hết dòng sớm hơn văn bản gốc, ép toàn bộ text thừa còn lại về chuỗi rỗng `""`.
    *   **Skip RTF Scopes**: Cải tiến logic `_tokenize_rtf` to nhận diện scope, bỏ qua không dịch các token chữ nằm trong `\colortbl`, `\stylesheet`, `\info`...

---

## 2. Các cải tiến và sửa lỗi trong phiên bản v0.3.x

### 2.1. Tối ưu hóa Codebase & Fix 12 Issue (v0.3)
- Tạo `.gitignore` và gom các file cấu hình PyInstaller về `DirectTrans.spec`.
- Thay thế API ngầm `keyboard._hotkeys.clear()` bằng `keyboard.remove_hotkey()`.
- Xóa code rỗng, dọn dẹp biến thừa, thêm `threading.Lock` cho LRU Cache của bộ dịch.

### 2.2. Khắc phục Lỗi Cửa sổ Popup (v0.3.1)
- Đảm bảo luôn dọn dẹp các cửa sổ popup cũ trước khi sinh popup mới, triệt để lỗi màn hình tràn ngập cửa sổ khi bấm phím tắt liên tiếp.

### 2.3. Ngăn chặn Lỗi Xung Đột Đa Tiến Trình (v0.3.2)
- Cập nhật Mutex kiểm tra `ERROR_ACCESS_DENIED`, ngăn chặn việc 2 app chạy ngầm song song.
- Thêm cơ chế Debounce 1.0 giây cho hotkey để tránh `keyboard` trigger quá nhạy.

### 2.4. Cải tiến trải nghiệm Gemini API (v0.3.3 - v0.3.5)
- **Hỗ trợ System Instructions (v0.3.3):** Cập nhật payload của `translator.py` theo định dạng `systemInstruction` chuẩn của Google thay vì gắn cứng vào `contents`.
- **Lựa chọn Model Động (v0.3.3):** Bổ sung danh sách xổ xuống (Combobox) trong giao diện Cài đặt cho phép người dùng tự do chuyển đổi giữa các model Gemini. Cung cấp nút `Load Models` để quét toàn bộ các model khả dụng cho API Key hiện tại từ máy chủ Google.
- **Tự động Lưu API Key (v0.3.4):** Vá lỗi "bẫy UX" nghiêm trọng nơi người dùng test key thành công nhưng quên bấm lưu. Từ nay, mọi hành động như `Load Models` hoặc `Test` (nếu Pass) đều tự động ghim API Key xuống `config.json`.
- **Sàng lọc Model Thông minh (v0.3.5):** Tính năng `Load Models` sẽ ping thử từng model một và chỉ hiển thị 100% những model vượt qua bài test.

---

## 3. Các cải tiến và sửa lỗi trong phiên bản v0.4

### 3.1. Đa ngôn ngữ giao diện & Font chữ tối ưu hóa
- **Đa ngôn ngữ**: Bổ sung dropdown lựa chọn ngôn ngữ giao diện ở góc phải Header gồm 5 ngôn ngữ: Tiếng Việt (vi), English (en), 한국어 (ko), 中文 (zh), 日本語 (ja). Toàn bộ nhãn, thông báo và nút trong cửa sổ cài đặt sẽ thay đổi theo ngôn ngữ được chọn.
- **Font chữ động**: Sử dụng `FontMapper` để tự động thay đổi font chữ tương ứng với ngôn ngữ đã chọn nhằm tối ưu hóa trải nghiệm đọc (ví dụ: dùng Malgun Gothic cho tiếng Hàn, Microsoft YaHei cho tiếng Trung, Meiryo cho tiếng Nhật, Segoe UI cho tiếng Việt/Anh).

### 3.2. Cấu trúc lại Header (Sticky Header) & Align lề
- **Sticky Header**: Tách phần tiêu đề ra khỏi canvas cuộn bên dưới và pack trực tiếp vào cửa sổ cha `self.window`. Điều này giúp:
  - Loại bỏ hoàn toàn khoảng trắng phía trên cùng.
  - Cố định Header (Sticky) ở trên cùng cửa sổ settings để người dùng có thể thoải mái cuộn xem danh sách phím tắt bên dưới mà không mất tiêu đề.
- **Rút gọn tiêu đề**: Tiêu đề được đổi thành "DirectTrans" tối giản, bỏ các chữ "Settings" và "Translation toolkit".
- **Info Icon**: Tích hợp thêm biểu tượng "ⓘ" nhỏ bên cạnh tiêu đề, trỏ trực tiếp đến trang hướng dẫn sử dụng / dự án.
- **Căn lề chuẩn xác**:
  - Tiêu đề "DirectTrans" căn thẳng hàng bên trái với phần tiêu đề "Nguồn dịch".
  - Dropdown chọn ngôn ngữ UI và dropdown chọn Provider (Nguồn dịch) có cùng chiều rộng (`width=14`) và cùng căn lề phải (`side='right'`), thẳng hàng dọc tuyệt đối.
  - Giảm padding biên 2 bên từ 16px xuống 10px để giao diện gọn gàng hơn.

### 3.3. Đồng bộ hóa Logo con chim giấy chính thức
- **Nguồn logo**: Sử dụng biểu tượng con chim giấy chính thức từ file [logo-direct-trans.png](file:///e:/Github/direct-trans/logo-direct-trans.png).
- **Sao chép và Chuyển đổi**:
  - Sao chép tệp logo con chim giấy vào thư mục tài nguyên [src/assets/logo-direct-trans.png](file:///e:/Github/direct-trans/src/assets/logo-direct-trans.png).
  - Tự động convert PNG logo này thành tệp biểu tượng đa kích thước [icon.ico](file:///e:/Github/direct-trans/src/assets/icon.ico) (gồm các kích thước 16x16, 32x32, 48x48, 64x64, 128x128, 256x256 px) để làm icon titlebar cửa sổ và icon chính khi build file EXE.
- **Tối ưu hiển thị khay hệ thống**: Cập nhật [tray.py](file:///e:/Github/direct-trans/src/tray.py) để ưu tiên tải tệp PNG logo con chim giấy thay vì ICO. Điều này đảm bảo Windows hiển thị biểu tượng khay hệ thống siêu sắc nét với độ trong suốt hoàn hảo, loại bỏ hiện tượng mờ hoặc xám màu của tệp ICO cũ.
- **Tích hợp Header**: Cửa sổ Cài đặt tự động load và resize tệp PNG này về kích thước **24x24 pixels** bằng Pillow để hiển thị mượt mà trên header.

### 3.4. API Key Compact (2 dòng)
- Thu gọn giao diện API Key của Gemini xuống còn 2 dòng:
  - Dòng 1: Label + Entry nhập key (co dãn linh hoạt) + link Lấy API Key.
  - Dòng 2: Model selection dropdown + Nút ↻ Load, nút Test và nút Lưu Key (thiết kế màu Warm Coral `#cc785c` của Claude).

### 3.5. Palette màu Claude Design
- Áp dụng các mã màu từ `DESIGN-claude.md` thay thế cho Catppuccin Latte:
  - Nền canvas chính: `#faf9f5` (Warm cream nhạt).
  - Nền Header / bảng / hàng: `#efe9de` và `#f5f0e8` (Cream ấm sậm).
  - Màu chữ: `#141413` (charcoal ink).
  - Màu nút CTA chính: `#cc785c` (Warm Coral).

### 3.6. Đồng bộ hóa mã màu & Font chữ động cho Popup Dịch
- **Đồng bộ hóa giao diện**: Cập nhật tệp [popup_window.py](file:///e:/Github/direct-trans/src/popup_window.py) để áp dụng hoàn toàn bảng màu Claude:
  - Nền cửa sổ popup: `#faf9f5` (Canvas).
  - Nền vùng văn bản kết quả: `#f5f0e8` (Surface-soft).
  - Nút **Thay thế**: Màu Warm Coral `#cc785c` (Primary).
  - Nút **Copy**: Màu Teal dịu `#5db8a6` (Accent Teal) để hài hòa và phân biệt rõ chức năng chính-phụ.
  - Nút đóng **✕**: Màu đỏ `#c64545`.
- **Font chữ động cho bản dịch**: Kết quả dịch hiển thị trong Textarea tự động áp dụng font chữ tối ưu hóa theo ngôn ngữ đích (nhận diện qua `target_lang_code`), ví dụ: tiếng Hàn hiển thị bằng font `Malgun Gothic` tự nhiên của Windows thay vì font mặc định, giúp tối ưu tối đa trải nghiệm đọc kết quả.
- **Font giao diện đồng bộ**: Các nhãn ngôn ngữ và nút bấm trên popup tự động áp dụng font chữ theo ngôn ngữ giao diện (UI language) được chọn trong Settings.

### 3.7. Tài liệu hướng dẫn sử dụng offline song ngữ & Trình duyệt mặc định
- **Tài liệu HTML tích hợp song ngữ**: Thiết kế và tạo tệp tài liệu hướng dẫn sử dụng ngoại tuyến tuyệt đẹp [user_manual.html](file:///e:/Github/direct-trans/src/assets/user_manual.html) hỗ trợ song ngữ động (Tiếng Việt và Tiếng Anh). 
  - Ứng dụng tự động truyền tham số ngôn ngữ giao diện hiện tại (`?lang=vi` hoặc `?lang=en`) khi mở tài liệu.
  - Sử dụng Javascript và CSS để toggle hiển thị nội dung theo ngôn ngữ được chọn một cách mượt mà.
  - Phông chữ tự động thích ứng tối ưu cho từng ngôn ngữ: Tiếng Việt hiển thị phông chữ hệ thống tiêu chuẩn (`Segoe UI`), Tiếng Anh sử dụng phông chữ cao cấp `Inter` từ Google Fonts giúp tối đa hóa trải nghiệm đọc.
- **CSS Mockups & Fallback hình ảnh**:
  - Do giới hạn phân quyền chụp ảnh màn hình của Windows Sandbox từ terminal ngầm, tài liệu được tích hợp các **CSS Mockups** giả lập giao diện thật của Settings Window và Popup Dịch sắc nét ở mọi độ phân giải.
  - Thẻ `<img>` ảnh chụp thật được cấu hình sự kiện `onerror` tự động ẩn ảnh và hiển thị CSS Mockup thay thế nếu không tìm thấy tệp ảnh vật lý, cho phép người dùng tự động thay thế bằng ảnh chụp thật bất cứ lúc nào bằng cách ghi đè file ảnh vào assets.
- **Mở tài liệu bằng trình duyệt mặc định thực tế (như Chrome)**:
  - Khắc phục lỗi Python `webbrowser.open` đôi khi tự động kích hoạt Edge hoặc lỗi mã hóa ổ đĩa `:` thành `%3A`.
  - Logic mới chỉ thay thế khoảng trắng thành `%20` để bảo toàn ký tự tên ổ đĩa (ví dụ `E:`), giúp Windows ShellExecute nhận diện chính xác đường dẫn tệp.
  - Thay thế `webbrowser.open` bằng lệnh CMD `start` thông qua `subprocess.Popen(..., shell=True)` để luôn gọi chính xác trình duyệt mặc định thực tế hiện tại của Windows (như Google Chrome) xử lý tệp tin. Có fallback an toàn quay lại `webbrowser.open` nếu lệnh shell bị chặn.

---

## 4. Các cải tiến và sửa lỗi trong phiên bản v0.4.2

### 4.1. Vá lỗi crash PopupWindow trong Replace Mode (P0)
*   **File:** `src/main.py` dòng ~260.
*   **Vấn đề:** Khi chế độ Thay thế thất bại và app cố tạo fallback popup, `PopupWindow` được khởi tạo thiếu tham số `config` bắt buộc → crash `AttributeError` ngay lập tức.
*   **Giải pháp:** Sửa `PopupWindow(self.root)` → `PopupWindow(self.root, self.config)`.

### 4.2. Bảo vệ async callback khi cửa sổ Settings đóng (P1)
*   **File:** `src/settings_window.py`.
*   **Vấn đề:** Các callback UI được schedule qua `window.after(0, ...)` từ bên trong thread nền (`fetch_models`, `_test_key`) không kiểm tra xem cửa sổ còn tồn tại không. Đóng Settings khi đang fetch model/test API → crash `TclError`.
*   **Giải pháp:** Thêm `if not self.window.winfo_exists(): return` ở đầu 7 callback nội tuyến liên quan.

### 4.3. Sửa MouseWheel ăn event toàn app (P1)
*   **File:** `src/settings_window.py`.
*   **Vấn đề:** `canvas.bind_all("<MouseWheel>")` intercept cả dialog con (hotkey editor) → cuộn trong dialog con làm canvas settings cũng cuộn.
*   **Giải pháp:** Đổi sang `canvas.bind("<MouseWheel>")` và unbind tương ứng.

### 4.4. Tray menu đa ngôn ngữ (P1)
*   **File:** `src/tray.py`.
*   **Vấn đề:** Menu tray hardcode tiếng Việt trong khi toàn bộ app đã hỗ trợ 5 ngôn ngữ từ v0.4.
*   **Giải pháp:** Thêm dict `TRAY_STRINGS` với 5 ngôn ngữ (vi/en/ko/zh/ja). `TrayIcon.__init__` nhận thêm param `config=None`, đọc `ui_language` để chọn bộ string phù hợp. `main.py` truyền `config=self.config` khi khởi tạo TrayIcon.

### 4.5. Settings window không còn always-on-top (P1)
*   **File:** `src/settings_window.py`.
*   **Vấn đề:** `-topmost True` vĩnh viễn khiến Settings đè lên mọi cửa sổ kể cả khi người dùng đang làm việc ở app khác.
*   **Giải pháp:** Topmost chỉ kéo dài 200ms sau khi mở (thu hút focus), rồi tự tắt.

### 4.6. DPI Awareness (P2)
*   **File:** `src/main.py`.
*   **Vấn đề:** App không khai báo DPI awareness → font/widget bị nhỏ hoặc blurry trên màn hình 4K hoặc scale 125%/150%.
*   **Giải pháp:** Gọi `ctypes.windll.shcore.SetProcessDpiAwareness(1)` trước khi tạo `DirectTransApp()`. Có fallback `try/except` an toàn cho Windows < 8.1.

### 4.7. Đổi tên biến màu (P2)
*   **File:** `src/settings_window.py`.
*   **Vấn đề:** Sau khi chuyển sang Claude palette ở v0.4, các biến `BLUE`, `GREEN`, `MAUVE`, `PEACH` vẫn giữ tên cũ nhưng tất cả đều mang giá trị `#cc785c` (Warm Coral) → gây nhầm lẫn nghiêm trọng.
*   **Giải pháp:** Gộp thành 1 biến `PRIMARY = '#cc785c'` và find-replace toàn bộ references trong file.

### 4.8. Các cải tiến nhỏ (P2-P3)
*   **Font init safety** (`settings_window.py`): Bọc `update_ui_language()` trong `try/except` để lỗi font không crash cửa sổ.
*   **Popup event timeout** (`main.py`): Khi popup không được tạo kịp trong 2s, log warning rõ ràng thay vì drop silently.
*   **Paste delay** (`popup_window.py`): Tăng sleep từ 150ms → 250ms, thêm comment giải thích.
*   **Tray fallback icon color** (`tray.py`): Đổi màu `#89b4fa` (Catppuccin) → `#cc785c` (Claude Coral).
*   **Dead hover binding** (`settings_window.py`): Xóa `<Enter>`/`<Leave>` binding vô nghĩa trên Gemini link.

---

## 5. Các cải tiến và sửa lỗi trong phiên bản v0.4.3

### 5.1. Thiết kế Giao diện mới theo Apple Design Palette
*   **Chi tiết**: Chuyển đổi toàn bộ bảng màu của ứng dụng sang phong cách của **Apple**:
    *   Nền cửa sổ chính (`BASE`): `#ffffff` (Canvas White).
    *   Nền Header / khung trên cùng: `#f5f5f7` (Parchment).
    *   Viền của các nhóm khối: `#e0e0e0` (Hairline).
    *   Khối nền phụ (`SURFACE0`): `#f5f5f7` (Parchment).
    *   Màu tương tác chính (`PRIMARY`/`BLUE`/`PEACH`): `#0066cc` (Action Blue).
    *   Màu chữ chính: `#1d1d1f` (Ink), chữ phụ: `#7a7a7a` (Muted 48).
    *   Màu nút phụ (Copy): `#34c759` (System Green) và đóng/lỗi: `#ff453a` (System Red).
*   **Phạm vi**: Đồng bộ màu sắc này trên cả **Settings Window**, **Dialog phím tắt** và **Popup dịch**.

### 5.2. Khắc phục vấn đề hòa lẫn màu sắc của các khung nhập (Độ tương phản cao) & Căn lề phải thẳng hàng (Align Right)
*   **Tăng độ tương phản**: 
    *   Thiết lập viền solid 1px rõ ràng màu `#d2d2d7` (Hairline Strong) xung quanh các khung nhập liệu.
    *   Cấu hình hiệu ứng focus đổi màu viền sang Action Blue (`#0066cc`) tức thì khi người dùng nhấp chuột vào ô nhập.
    *   Đồng bộ viền và tăng độ tương phản màu nền cho khung kết quả dịch trong Popup.
*   **Căn lề phải thẳng hàng (Align to Right)**:
    *   Điều chỉnh dropdown chọn ngôn ngữ giao diện ở header dịch chuyển sang trái (thêm lề phải 22px) để thẳng hàng tuyệt đối với dropdown "Nguồn dịch" ở dưới.
    *   Đưa nút "Lưu Key" API ra ngoài cùng bên phải, dịch chuyển nút "Test" và status label sang trái, loại bỏ hoàn toàn khoảng trống lệch lề phải của phần API Key.

### 5.3. Sửa lỗi Crash Dialog Phím tắt (P0)
*   **Vấn đề**: Khi bấm nút "+ Thêm phím tắt" hoặc nhấp đúp vào dòng phím tắt để sửa, dialog bị trống rỗng hoàn toàn do crash `AttributeError` vì vẫn tham chiếu đến các biến màu cũ `self.BLUE` và `self.GREEN` đã bị xóa.
*   **Giải pháp**: Cập nhật tất cả các tham chiếu màu trong dialog phím tắt sang biến `self.PRIMARY` mới.

### 5.4. Khắc phục lỗi Mất ngôn ngữ hiển thị của tài liệu hướng dẫn (P1)
*   **Vấn đề**: Do cơ chế mở file cục bộ (`file:///`) của Windows Shell (`ShellExecute`/`start`) luôn tự động nuốt mất các tham số query (`?lang=vi`), dẫn đến User Manual luôn luôn bị mở ở giao diện tiếng Anh.
*   **Giải pháp**: Triển khai file HTML chuyển hướng trung gian (`redirect`). Python sẽ ghi một tệp HTML chuyển hướng tạm thời và mở nó bằng trình duyệt mặc định, trình duyệt sau đó chuyển hướng nội bộ an toàn và giữ nguyên tham số ngôn ngữ `?lang=vi` hoặc `?lang=en`.

## 6. Các cải tiến và sửa lỗi trong phiên bản v0.4.4

### 6.1. Vá lỗi Treo Popup "⏳ Đang dịch..." (P0)
*   **Vấn đề**: Khi dịch xảy ra lỗi (như 503 hoặc mất mạng), popup kết quả dịch không hiển thị được thông điệp lỗi mà cứ bị treo ở trạng thái đang dịch mãi mãi. 
*   **Nguyên nhân gốc rễ**: Lỗi late-binding trong Python. Hàm `_process_translation` đưa callback `lambda: popup.show_error(str(e))` vào main thread để hiển thị lỗi, nhưng lúc callback thực thi thì biến Exception `e` của block `except` đã bị Python giải phóng, sinh ra lỗi `NameError` âm thầm làm crash luồng vẽ.
*   **Giải pháp**: Sử dụng kĩ thuật early-binding bằng tham số mặc định của lambda: `lambda msg=err_msg: popup.show_error(msg)`. Giá trị lỗi được đóng băng ngay lập tức, đảm bảo hiển thị thông tin lỗi an toàn.

### 6.2. Sửa lỗi Không bắt được text & Lỗi tự mở F12 DevTools (P1)
*   **Vấn đề**: Nhấn phím tắt dịch thì app báo không tìm thấy văn bản đang chọn. Khi dùng trình duyệt, đôi khi nhấn phím tắt lại vô tình mở DevTools (F12) hoặc focus vào thanh menu.
*   **Nguyên nhân gốc rễ**: Lệnh Win32 API trước đây gửi tín hiệu "nhả phím" (KeyUp) một cách mù quáng cho mã phím chung chung (`VK_SHIFT`), khiến ứng dụng như Chrome/Edge vẫn nhận diện được phím Shift vật lý đang bị đè, gây xung đột khiến trình duyệt tưởng nhầm có tổ hợp phím ẩn (Ctrl+Shift+C).
*   **Giải pháp**: Sử dụng `win32api.GetAsyncKeyState` để chỉ gửi lệnh nhả cụ thể đối với từng phím vật lý Trái/Phải (`VK_LSHIFT`, `VK_RSHIFT`, `VK_LCONTROL`, v.v.) kết hợp với cờ `KEYEVENTF_EXTENDEDKEY` để triệt để xóa trạng thái phím, giúp chức năng giả lập `Ctrl+C` hoạt động hoàn hảo.

### 6.3. Tích hợp cơ chế Tự động Thử lại (Retry) cho API Dịch (P1)
*   **Vấn đề**: Lỗi 503 (Service Unavailable) thỉnh thoảng xảy ra do máy chủ Google quá tải tạm thời làm quá trình dịch bị lỗi hoàn toàn.
*   **Giải pháp**: Triển khai cơ chế tự động thử lại (Retry) thông minh với exponential backoff (thử lại tối đa 3 lần, delay bắt đầu từ 1.0 giây và nhân đôi mỗi lần tiếp theo) cho cả **Gemini API** và **Google Free Translate** đối với các lỗi tạm thời như 503, 429, Timeout hoặc ConnectionError.

### 6.4. Thay đổi Kích thước mặc định của Cửa sổ Dịch (P2)
*   **Chi tiết**: Tăng kích thước mặc định của popup kết quả dịch từ `380x220` lên **`880x465`**.
*   **Lợi ích**: Giúp hiển thị trọn vẹn các đoạn văn bản dịch dài mà không bị ngắt dòng hoặc tràn khung quá sớm, nâng cao trải nghiệm đọc của người dùng.

### 6.5. Đặt Model "gemini-3.1-flash-lite" làm Mặc định (P2)
*   **Chi tiết**: Cấu hình mặc định của Gemini được cập nhật từ model cũ `gemini-1.5-flash` sang model thế hệ mới tối ưu hơn là **`gemini-3.1-flash-lite`**.
*   **Áp dụng**: Thay đổi này được đồng bộ xuyên suốt từ defaults của `Config`, method `get_gemini_model()`, translator backend, cho tới tệp cấu hình mẫu `config.json`.

### 6.6. Quản lý Log Thông minh (P2)
*   **Chi tiết**: Cấu hình lại `logging` sử dụng `TimedRotatingFileHandler` thay cho `basicConfig` cố định.
*   **Áp dụng**: Log file `directtrans.log` giờ đây chỉ lưu thông tin trong 1 giờ gần nhất (`when="H", interval=1, backupCount=1`), tự động dọn dẹp để tiết kiệm dung lượng ổ cứng.

---

## 7. Các cải tiến và sửa lỗi trong phiên bản v0.4.5

### 7.1. Sửa lỗi Xung đột Phím Tắt khi bấm quá nhanh (P0)
*   **Vấn đề**: Khi bấm tổ hợp phím dịch thuật rất nhanh rồi thả ra, ứng dụng không lấy được văn bản (lỗi sao chép rỗng) và vẫn tiếp tục kích hoạt DevTools (F12) của trình duyệt. Nhưng nếu giữ phím chậm thì hoạt động bình thường.
*   **Nguyên nhân gốc rễ**: Hiện tượng *Race Condition* (Xung đột tranh chấp) giữa hệ điều hành và Win32 API. Khi người dùng thả phím cực nhanh, lệnh `win32api.GetAsyncKeyState` có thể trả về `False` nên không gửi tín hiệu giả lập "nhả phím" (KeyUp). Đồng thời, thông điệp "nhả phím" vật lý của người dùng đang nằm trong hàng đợi sự kiện (event queue) của OS và chưa được trình duyệt xử lý kịp, dẫn đến việc trình duyệt vẫn tưởng người dùng đang đè phím `Shift`. Kết hợp với tín hiệu giả lập `Ctrl+C` của chúng ta, trình duyệt nhận nhầm thành tổ hợp `Ctrl+Shift+C`.
*   **Giải pháp**: Thay đổi phương thức từ "Chỉ nhả phím nếu đang giữ" sang **"Nhả phím vô điều kiện cho TẤT CẢ các phím Modifier"**. Trước khi giả lập lệnh `Ctrl+C` hoặc `Ctrl+V`, hệ thống chủ động ép toàn bộ 11 mã phím modifier (Left/Right Shift, Ctrl, Alt, Win và mã chung) phải nhận trạng thái KeyUp. Điều này tạo ra một khoảng đệm an toàn "sạch sẽ", xóa bỏ mọi trạng thái modifier bị kẹt lại trong Chrome/Edge, giải quyết triệt để lỗi mở DevTools và kẹt clipboard kể cả khi người dùng gõ siêu nhanh.

---

## 8. Hướng dẫn tiếp tục ở Session mới
Nếu bạn muốn tiếp tục kiểm tra hoặc chỉnh sửa:
1.  Đóng các tiến trình đang chạy:
    ```powershell
    taskkill /F /IM DirectTrans.exe
    taskkill /F /IM DirectTrans_v0.4.exe
    taskkill /F /IM DirectTrans_v0.4.1.exe
    taskkill /F /IM DirectTrans_v0.4.2.exe
    taskkill /F /IM DirectTrans_v0.4.3.exe
    taskkill /F /IM DirectTrans_v0.4.4.exe
    taskkill /F /IM DirectTrans_v0.4.5.exe
    ```
2.  Chạy thử file thực thi mới đã build để kiểm chứng giao diện và tính năng:
    ```powershell
    .\dist\DirectTrans_v0.4.5.exe
    ```
3.  Bôi đen và dịch thử văn bản trong PowerPoint để xác minh output hiển thị chuẩn xác, không mất chữ và không bị trùng lặp cửa sổ.

## 9. Các cải tiến và sửa lỗi trong phiên bản v1.0.6
- **Thống nhất Nhãn API Key**: Đồng bộ tất cả các nhãn API key riêng biệt của từng provider (ví dụ: "Gemini API key:") thành một nhãn duy nhất "API key:" cho toàn bộ giao diện.
- **Tái cấu trúc lưới giao diện (Grid Layout)**: Sắp xếp lại hoàn toàn hệ thống lưới của mục cấu hình Provider theo chuẩn thói quen người dùng:
  - Hàng 1: Nhãn API key, Khung nhập API key, Nút "Load Models", Link "Lấy API key".
  - Hàng 2: Nhãn Model, Dropdown chọn Model, Nút "Test", Nhãn trạng thái Pass-Fail, Nút "Lưu Key".
- **Giải phóng không gian nhập liệu**: Loại bỏ thiết lập "chiếm chỗ vô hình" (width cố định) của nhãn báo trạng thái Pass-Fail. Điều này giúp toàn bộ mảng trắng thừa ở giữa bị xóa sổ, và hệ quả là Khung nhập API key cùng Dropdown Model được tự do giãn dài tràn viền, chiếm trọn mọi khoảng trống sẵn có (lên tới độ rộng cửa sổ mới là 580px).
  - Vá lỗi Crash PyInstaller: Khắc phục dứt điểm lỗi cú pháp dư dấu ngoặc `)` (SyntaxError) trong `settings_window.py` ngăn cản PyInstaller đóng gói file vào bản build, gây ra lỗi `ModuleNotFoundError` khi khởi chạy app ở đầu version 1.0.6.

## 10. Các cải tiến và sửa lỗi trong phiên bản v1.0.7
- **API UI Grid Realignment**: Tái cấu trúc lại lưới hiển thị (grid layout) của màn hình cài đặt API Key cho 3 provider:
  - Cố định nút "Load Models" và link "Lấy API key" lên hàng đầu tiên, song song với khung nhập key.
  - Cố định nút "Test", trạng thái "Pass/Fail", và nút "Lưu Key" xuống hàng thứ hai, song song với dropdown chọn model.
  - Sửa lỗi nút "Load Models" bị đẩy xuống hàng thứ 2 nằm chen ngang cùng combobox ở phiên bản trước.

## 11. Các cải tiến và sửa lỗi trong phiên bản v1.0.8
- **Ngăn chặn Layout Shift (Xê dịch UI)**: Cấu hình `width=5` (kích thước cố định) cho nhãn trạng thái Pass/Fail của API Key. Khi người dùng bấm nút "Test", dòng chữ "Pass" hiện ra sẽ không làm thay đổi kích thước thật của cột, tránh hiện tượng ô nhập API Key bị bóp hẹp lại gây cảm giác giật layout khó chịu.
