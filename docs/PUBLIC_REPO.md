# Public GitHub — không đăng dữ liệu nhạy cảm

Repo **Direct-Trans** là **công khai**. Trước khi `git push`, đảm bảo không commit hoặc publish:

| Loại | Ví dụ | Ghi chú |
|------|--------|--------|
| **Cấu hình cá nhân** | `config.json` (đã ignore), bản sao config cạnh exe | API key, model, hotkey, `ui_theme`, email… |
| **Bí mật / API** | API key, token, mật khẩu, nội dung key trong ảnh chụp màn hình | Kể cả key che bằng `••••` — vẫn lộ provider, model, thói quen dùng |
| **Ảnh chụp UI trên máy dev** | `src/assets/readme/`, `docs/ui-review/v2.0.1-nord-preview/`, `light_candidate_*.png` | Script capture dùng `Config()` thật → ảnh phản ánh máy bạn |
| **Log / trace** | `directtrans.log`, `boot_trace.txt` | Đã ignore |
| **Ghi chú nội bộ** | `hand-off.md`, `issue.md`, `REVIEW_INTENT.md`, `release_notes.txt` | Đã ignore |

## Ảnh README / user manual

- **README (4 theme):** ảnh mẫu dùng `docs/ui-review/screenshots/` (đã có trong repo, không chụp lại từ máy cá nhân trừ khi chủ đích thay bằng ảnh **generic**).
- **Ảnh local:** `python scripts/capture_readme_settings.py` → `src/assets/readme/` — **chỉ dùng cục bộ**, đã ignore.
- **Manual trong app:** `python scripts/capture_manual_assets.py` — **không commit** output nếu ảnh lấy từ config thật; giữ bản `src/assets/screenshot_*.png` đã có trên remote hoặc thay bằng ảnh chụp với config mặc định / máy ảo.

## Checklist trước push

1. `git status` — không có `config.json`, log, thư mục ignore.
2. Không stage `src/assets/readme/`, preview Nord cá nhân, PNG `light_candidate_*` mới.
3. Diff ảnh PNG: nếu thấy provider/model/hotkey của bạn → `git restore` hoặc không add.
4. Release GitHub: chỉ đính kèm **exe** + release notes; không đính config hay log người dùng.

## Duy trì sau này

Mọi script `capture_*` coi như có thể đọc **config thật**. Ảnh public trong repo: chạy `python scripts/capture_ui_screenshots.py` — dùng `scripts/screenshot_config.py` (English UI, `DEFAULT_CONFIG`, không API key).
