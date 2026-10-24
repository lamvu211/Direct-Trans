# DirectTrans

Ứng dụng Windows chạy nền (khay hệ thống): chọn văn bản trong bất kỳ app nào, nhấn phím tắt toàn cục để dịch qua AI hoặc Google Translate, hiển thị popup hoặc thay thế trực tiếp đoạn đã chọn (có hỗ trợ RTF).

---

## Cài đặt (file exe)

1. Tải `DirectTrans_v*.exe` từ [Releases](https://github.com/lamvu211/Direct-Trans/releases) (hoặc thư mục `dist` sau khi build).
2. Đặt file ở vị trí cố định (ví dụ `C:\Apps\DirectTrans\`).
3. Chạy lần đầu — cửa sổ **Cài đặt** mở tự động; cấu hình API key và phím tắt (xem **Hướng dẫn sử dụng** trong app).
4. App thu nhỏ về **khay hệ thống**. Double-click icon khay hoặc chuột phải → **Cài đặt** để mở lại Settings.
5. Cấu hình lưu cạnh file exe (`config.json`); log: `directtrans.log`.

> Chạy bản exe mới khi bản cũ còn mở: bản cũ sẽ được tắt để bản mới tiếp quản (cùng một instance).

---

## Giao diện cơ bản

### Cài đặt (Settings)

Một màn hình: ngôn ngữ UI, theme (Midnight Gold, Aurora Glass, Rose Champagne, Nord Snow), nguồn dịch (provider), API key & model, phím tắt, tùy chọn khởi động Windows / cập nhật.

Bấm ảnh thu nhỏ để xem kích thước đầy đủ; hoặc mở từng mục 🔍 bên dưới. (Ảnh trong repo là mẫu UI review; không chứa ảnh chụp máy cá nhân — xem [docs/PUBLIC_REPO.md](docs/PUBLIC_REPO.md).)

<table>
  <tr>
    <td align="center" width="25%">
      <a href="docs/ui-review/screenshots/settings_midnight_gold.png"><img src="docs/ui-review/screenshots/settings_midnight_gold.png" width="200" alt="Midnight Gold" /></a><br>Midnight Gold
    </td>
    <td align="center" width="25%">
      <a href="docs/ui-review/screenshots/settings_aurora_glass.png"><img src="docs/ui-review/screenshots/settings_aurora_glass.png" width="200" alt="Aurora Glass" /></a><br>Aurora Glass
    </td>
    <td align="center" width="25%">
      <a href="docs/ui-review/screenshots/settings_rose_champagne.png"><img src="docs/ui-review/screenshots/settings_rose_champagne.png" width="200" alt="Rose Champagne" /></a><br>Rose Champagne
    </td>
    <td align="center" width="25%">
      Nord Snow<br><sub>Chọn trong app; ảnh review chưa đưa lên repo công khai.</sub>
    </td>
  </tr>
</table>

<details>
<summary>🔍 Midnight Gold</summary>
<img src="docs/ui-review/screenshots/settings_midnight_gold.png" alt="Midnight Gold — Settings" />
</details>
<details>
<summary>🔍 Aurora Glass</summary>
<img src="docs/ui-review/screenshots/settings_aurora_glass.png" alt="Aurora Glass — Settings" />
</details>
<details>
<summary>🔍 Rose Champagne</summary>
<img src="docs/ui-review/screenshots/settings_rose_champagne.png" alt="Rose Champagne — Settings" />
</details>

### Popup dịch

Hiện sau phím tắt chế độ **Popup**: nội dung dịch, theme, cỡ/màu chữ, **Copy** / **Replace**.

![Popup dịch](src/assets/screenshot_popup.png)

### Khay hệ thống

Menu: bật/tắt dịch tạm thời, mở Cài đặt, Thoát.

---

## Cách dùng nhanh

1. **Bôi chọn** văn bản trong Word, browser, chat, …
2. Nhấn **phím tắt** đã gán (mặc định thường có Popup → Việt / Anh).
3. **Popup:** đọc kết quả, Copy hoặc Replace. **Replace (hotkey):** thay trực tiếp không qua popup.

Chi tiết API key, Test/Save key, quản lý phím tắt, tùy chọn popup: mở **User manual** trong Settings hoặc file `src/assets/user_manual.html`.

---

## Cấu trúc dự án (dev)

```text
direct-trans/
├── src/
│   ├── main.py              # Entry, tray + Qt loop, hotkeys
│   ├── config.py            # config.json, API keys (DPAPI)
│   ├── translator.py        # Gemini, Groq, Mistral, Google Free
│   ├── hotkey_manager.py    # RegisterHotKey (Windows)
│   ├── clipboard_util.py    # Copy / replace RTF
│   ├── process_util.py      # Kill stale DirectTrans processes
│   ├── assets/              # icon, user_manual.html, screenshots
│   └── ui/qt/               # Settings, popup, themes, dialogs
├── tests/
├── scripts/                 # capture_manual_assets.py, UI screenshots
├── DirectTrans.spec         # PyInstaller
├── build.bat
└── requirements.txt
```

### Chạy từ source

```bash
pip install -r requirements.txt
python src/main.py
```

### Build exe

```cmd
.\build.bat
```

### Tests

```bash
python -m pytest tests/ -q
```

Ảnh cho tài liệu:

```bash
python scripts/capture_ui_screenshots.py    # docs/ui-review (review trước khi commit ảnh)
python scripts/capture_manual_assets.py     # src/assets — không commit nếu ảnh từ config máy bạn
python scripts/capture_readme_settings.py   # local only → src/assets/readme/ (gitignored)
```

Chính sách repo công khai: [docs/PUBLIC_REPO.md](docs/PUBLIC_REPO.md).

---

## License

[MIT License](LICENSE)
