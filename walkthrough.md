# Báo cáo kết quả nâng cấp & sửa lỗi DirectTrans (Phiên bản v0.2)

Chúng tôi đã hoàn thành toàn bộ các hạng mục nâng cấp và sửa lỗi của phiên bản **v0.2** theo yêu cầu mới nhất của bạn. Phiên bản chính thức v0.2 được đóng gói dưới dạng file EXE portable chạy ngầm, không hiển thị màn hình Console, đảm bảo trải nghiệm người dùng tối ưu.

## Các thay đổi chính đã hoàn thành trong v0.2:

1. **Ngăn chặn Trùng Phím tắt**:
   - Khi Thêm hoặc Sửa phím tắt, hệ thống tự động kiểm tra xem tổ hợp phím có bị trùng với phím tắt khác hay không.
   - Nếu trùng, ứng dụng sẽ hiển thị cảnh báo: `"phím tắt đã được sử dụng"` và chặn không cho lưu.
2. **Giao diện Light Mode Hiện đại (Catppuccin Latte)**:
   - Chuyển toàn bộ theme màu của cửa sổ Settings và cửa sổ Popup kết quả dịch sang Light Mode.
   - Tối ưu hóa độ tương phản của chữ (chữ trắng trên các nút Lưu, Copy, Thay thế màu xanh lá/cam) để người dùng dễ quan sát.
3. **Cố định Kích thước & Lề Đối xứng**:
   - Cố định chiều rộng của Settings window ở kích thước `540x650` (`resizable(False, True)`).
   - Tự động đồng bộ chiều rộng của khung cuộn bên trong với canvas, giúp căn lề trái-phải đối xứng hoàn hảo 16px ở hai bên.
4. **Sửa Lỗi Mất Ký Tự PowerPoint**:
   - Cập nhật bộ tokenize RTF để parse các chuỗi escape Unicode (`\uN?`) và Hex (`\'XX`) thành các token văn bản thông thường.
   - Loại bỏ triệt để các control Unicode/Hex cũ của văn bản gốc khỏi chuỗi RTF dịch mới, giải quyết hoàn toàn lỗi mất chữ và lẫn chữ khi dịch văn bản nhiều dòng trong PowerPoint.
5. **Gỡ bỏ Tùy chọn Không Cần thiết**:
   - Gỡ bỏ 2 tùy chọn "Fallback tự động" và "Cache bản dịch" khỏi giao diện chính để tối giản hóa UI.
6. **Lưu Cài đặt Tức thì (Auto-Save)**:
   - Gỡ bỏ cụm nút Lưu và Hủy ở dưới cùng cửa sổ chính.
   - Mọi thay đổi về Nguồn dịch, API Key, Phím tắt, hay tùy chọn khởi động cùng Windows sẽ được lưu trực tiếp vào `config.json` và áp dụng ngay lập tức lên hệ thống.

---

## Hướng dẫn sử dụng bản Release v0.2:
1. Tải bản portable chính thức v0.2 tại [DirectTrans.exe](file:///e:/Github/direct-trans/dist/DirectTrans.exe).
2. Nhấp đúp chuột để chạy ứng dụng. Cửa sổ **DirectTrans Settings** màu sáng hiện đại sẽ ngay lập tức hiện lên.
3. Bạn có thể sử dụng các tính năng cấu hình phím tắt và API key, mọi thao tác sẽ tự động lưu tức thì.
4. Để ẩn cửa sổ cài đặt xuống System Tray, hãy nhấn nút Minimize ở góc trên bên phải cửa sổ. Nhấp đúp chuột vào biểu tượng **DT màu xanh** ở khay hệ thống để khôi phục lại cửa sổ.
