# Task 2.0.16 — Popup Provider & OpenRouter

## Mục tiêu

1. **Minimum size popup**: Không cho resize quá nhỏ (toolbar không overlap).
2. **Provider dropdown trên popup**: Thay "Translated by …", đồng bộ với Settings; cảnh báo thiếu API key; dịch lại khi đổi provider.
3. **OpenRouter thay Mistral**: Xóa Mistral khỏi Settings; thêm OpenRouter; model mặc định free tier.

## Checklist

### 1. Minimum popup size
- [x] Tăng `POPUP_WINDOW_MIN_WIDTH` (900px) và đồng bộ `config`.
- [x] Sửa layout toolbar (provider combo + stretch, không overlap).
- [x] Clamp kích thước sau resize / màn hình nhỏ.
- [x] Test: `tests/test_ui_qa_fixes.py`.

### 2. Provider trên popup
- [x] Combo provider thay `status_label`.
- [x] `config.set_provider` + sync Settings / popup hai chiều.
- [x] Banner thiếu API key (`err_api_key_msg`).
- [x] `TranslationManager.translate_with_provider` + dịch lại từ `main.py`.
- [x] Test popup provider / API notice.

### 3. OpenRouter
- [x] `constants`: `OPENROUTER`, migration `mistral` → `openrouter`.
- [x] `OpenRouterTranslator`, Settings API, Load Models (free tier).
- [x] Tests translator + fallback.

### 4. Release
- [x] `APP_VERSION` 2.0.16, `CHANGELOG.md`.
- [x] `pytest tests/ -q` — 105 passed.
- [x] `build.bat` → `dist\DirectTrans_v2.0.16.exe` (`DirectTrans.spec` đọc `APP_VERSION` từ `constants.py`).

## Ghi chú kỹ thuật

- OpenRouter API: `POST https://openrouter.ai/api/v1/chat/completions`.
- Model mặc định: `openrouter/free`; Load Models lọc model `:free` hoặc pricing 0.