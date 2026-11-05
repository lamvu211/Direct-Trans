# Quy Trình Orchestration: Ben x Cursor CLI

> **Mô hình phối hợp:** Ben (Kiến trúc sư / Lead Reviewer / QA) ⟷ Cursor CLI (Thợ code / Worker)

---

## 1. Sơ Đồ Vòng Lặp Thực Thi (Closed-Loop)

```mermaid
flowchart TD
    User([Người dùng giao việc]) --> Ben_Spec[1. Ben phân tích & lập Spec / Kế hoạch chi tiết]
    Ben_Spec --> Ben_Prompt[2. Ben xuất Prompt đóng gói cho Cursor CLI]
    Ben_Prompt --> Cursor_Exec[3. Chạy Cursor CLI thực thi code]
    Cursor_Exec --> Ben_Audit[4. Ben kiểm tra: git diff + Chạy test suite]
    Ben_Audit --> Check{Đạt chuẩn?}
    Check -- Có lỗi / Không đạt -- --> Ben_FixPrompt[5. Ben lập Feedback & Prompt sửa lỗi]
    Ben_FixPrompt --> Cursor_Exec
    Check -- Đạt 100% -- --> Done([6. Báo cáo hoàn tất cho Người dùng])
```

---

## 2. Phân Vai & Trách Nhiệm

| Vai trò | Phụ trách chính | Nguyên tắc bắt buộc |
| :--- | :--- | :--- |
| **Ben (Lead Agent)** | • Phân tích yêu cầu, bóc tách kiến trúc.<br>• Viết Spec / Task Breakdown với tiêu chí nghiệm thu rõ ràng.<br>• Soát `git diff`, chạy unit test, rà soát regressions.<br>• Phê duyệt cuối cùng trước khi bàn giao. | Không tự tay sửa code tràn lan khi đã giao Cursor; giữ vai trò giám sát, đánh giá khách quan và kiểm soát chất lượng. |
| **Cursor CLI (Worker)** | • Nhận prompt lệnh từ Ben.<br>• Thực thi sửa đổi file trực tiếp trên workspace.<br>• Chạy lệnh theo chỉ dẫn của prompt. | Tuân thủ tuyệt đối phạm vi file được chỉ định trong Spec; không tự ý refactor các file không liên quan. |

---

## 3. Các Bước Vận Hành Chuẩn (SOP)

### Bước 1: Tiếp nhận & Lập Spec (Ben)
Khi bạn giao yêu cầu mới, Ben sẽ:
1. Đọc codebase hiện tại để nắm ngữ cảnh thực tế.
2. Viết file đặc tả công việc (Spec) ngắn gọn gồm:
   * **Mục tiêu thay đổi** (Tại sao phải làm?).
   * **Danh sách file bị tác động** (Chỉ đích danh đường dẫn).
   * **Logic cần triển khai** (Mô tả kỹ thuật chi tiết).
   * **Tiêu chí nghiệm thu (Acceptance Criteria)**: Các test case cần pass.

### Bước 2: Đóng gói lệnh cho Cursor CLI (Ben)
Ben sinh ra câu lệnh CLI hoàn chỉnh để chạy trong terminal:
```powershell
cursor --print-cmd "Đọc kỹ spec và thực hiện các thay đổi..."
```
*(Hoặc Ben gọi trực tiếp công cụ `run_command` để kích hoạt Cursor CLI nếu máy đã cài đặt).*

### Bước 3: Thực thi (Cursor CLI)
Cursor CLI đọc prompt, thực hiện chỉnh sửa mã nguồn và lưu file.

### Bước 4: Review & Test (Ben)
Ben lập tức chạy quy trình kiểm toán 3 lớp:
1. **Kiểm tra `git diff`:** Rà soát từng dòng code xem có phát sinh code thừa, sai lệch kiến trúc hoặc phá vỡ các quy tắc chung không.
2. **Chạy Test Suite:** Chạy pytest / unittest nội bộ để chứng minh logic hoạt động thật.
3. **Đo lường / Benchmark:** Kiểm tra hiệu năng hoặc hành vi thực tế.

### Bước 5: Vòng lặp sửa lỗi (Fix Loop)
* **Nếu phát hiện bug / test fail:** Ben lập biên bản lỗi cụ thể (File nào, dòng nào, lỗi gì, hành vi mong muốn là gì) và đóng gói lại prompt cho Cursor CLI sửa tiếp.
* Quá trình lặp lại cho đến khi toàn bộ test case xanh và code sạch hoàn toàn.

### Bước 6: Nghiệm thu & Báo cáo
Ben thông báo kết quả nghiệm thu cho bạn bằng 1 thông điệp ngắn gọn kèm mã lệnh kiểm chứng.

---

## 4. Mẫu Prompt Ben gửi cho Cursor CLI (Template)

```markdown
[NHIỆM VỤ DÀNH CHO CURSOR CLI]
- Mục tiêu: {Mô tả ngắn}
- Phạm vi can thiệp: {Danh sách file}
- Yêu cầu kỹ thuật:
  1. {Yêu cầu 1}
  2. {Yêu cầu 2}
- Ràng buộc:
  - Giữ nguyên các hàm không liên quan.
  - Không thêm thư viện ngoài trừ khi được yêu cầu.
  - Sau khi sửa, đảm bảo cú pháp hợp lệ.
```
