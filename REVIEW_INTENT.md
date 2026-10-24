# Review intent — do not flag as issues

Các hành vi sau là **chủ đích sản phẩm**, không coi là bug trong code review:

1. **`kill_old_processes` (frozen exe):** Khi khởi chạy bản build mới, dừng toàn bộ tiến trình tên `DirectTrans*` để bản mới nhất chiếm quyền (upgrade / autostart).
2. **`reset_provider_models_to_defaults` (frozen exe):** Mỗi lần mở `.exe`, reset tên model Gemini/Groq/Mistral về default; API key được giữ.
3. **Fallback chain:** Tự động theo `DEFAULT_FALLBACK_ORDER` trong code/config mặc định — **không có UI** chỉnh thứ tự hoặc bật/tắt trong Settings.
