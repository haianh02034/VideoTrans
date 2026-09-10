# Thêm gói ngôn ngữ

Phần mềm tự động phát hiện mọi tệp `*.json` trong thư mục `phiendichvideo/language/`. Thêm một tệp vào đó là có thêm một ngôn ngữ, **không cần sửa dòng mã nào**.

Hiện có sẵn ba gói: `vi.json` (Tiếng Việt), `en.json` (Tiếng Anh), `zh.json` (Tiếng Trung).

---

## 1. Cấu trúc tệp ngôn ngữ

Mỗi tệp là một đối tượng JSON **phẳng**, gồm các cặp `"khóa": "văn bản hiển thị"`. Hiện mỗi tệp có 873 khóa.

```json
{
    "&Help": "Trợ giúp/Giới thiệu(&H)",
    "Start": "Bắt đầu",
    "Dubbing role": "Chọn giọng đọc",
    "Dubbing succeeded {}，failed {}": "Thành công: {}, Thất bại: {}"
}
```

**Chỉ sửa phần giá trị bên phải. Tuyệt đối không đổi tên khóa** — khóa chính là thứ mã nguồn dùng để tra cứu, đổi tên là phần đó mất bản dịch.

### Về dấu ngoặc nhọn `{}`

Một số giá trị chứa `{}` — đó là chỗ điền biến lúc chạy (tên tệp, số lượng, thông báo lỗi...). Bản dịch **phải giữ đúng số lượng `{}`** như bản gốc, nếu không phần mềm sẽ báo lỗi khi hiển thị chuỗi đó.

```
Đúng : "Dubbing succeeded {}，failed {}" -> "Thành công: {}, Thất bại: {}"      (2 dấu, 2 dấu)
Sai   : "Dubbing succeeded {}，failed {}" -> "Thành công và thất bại"           (mất dấu -> lỗi)
```

Thứ tự `{}` trong câu có thể thay đổi cho hợp ngữ pháp tiếng Việt, miễn giữ đủ số lượng.

---

## 2. Các bước tạo gói ngôn ngữ mới

1. Chép `en.json` thành tệp mới, đặt tên theo **mã ngôn ngữ 2 chữ cái viết thường** rồi thêm `.json`. Ví dụ tiếng Thái là `th.json`, tiếng Nhật là `ja.json`.
2. Dịch phần giá trị của từng khóa, giữ nguyên tên khóa và số lượng `{}`.
3. Lưu tệp bằng mã hóa **UTF-8**.
4. Đặt vào thư mục `phiendichvideo/language/`.
5. Khởi động lại phần mềm.

Kiểm tra tệp trước khi dùng — sai cú pháp JSON là phần mềm bỏ qua và quay về tiếng Anh:

```bash
python -c "import json,io; d=json.load(io.open('phiendichvideo/language/th.json',encoding='utf-8')); print(len(d),'khóa, JSON hợp lệ')"
```

Đối chiếu xem có thiếu khóa nào so với bản gốc không:

```bash
python -c "
import json,io
en=json.load(io.open('phiendichvideo/language/en.json',encoding='utf-8'))
new=json.load(io.open('phiendichvideo/language/th.json',encoding='utf-8'))
print('Thiếu:',sorted(set(en)-set(new)))
print('Thừa :',sorted(set(new)-set(en)))
"
```

Khóa nào thiếu thì phần mềm hiển thị chính tên khóa đó thay vì bản dịch — không gây lỗi, chỉ xấu giao diện.

---

## 3. Phần mềm chọn ngôn ngữ như thế nào

Theo thứ tự ưu tiên (xem `phiendichvideo/configure/_i18n.py`):

1. **Biến môi trường `PYVIDEOTRANS_LANG`** — cũng chính là thứ mà tham số dòng lệnh `--lang` đặt vào.
   ```bash
   python sp.py --lang vi
   ```
2. **Giá trị `lang` trong tệp cấu hình** `phiendichvideo/cfg.json`. Đây là giá trị được lưu khi bạn đổi ngôn ngữ trong phần mềm qua **Công cụ → Tùy chọn nâng cao → Ngôn ngữ giao diện**.
3. **Ngôn ngữ hệ thống** — lấy 2 ký tự đầu của locale hệ điều hành, viết thường.

Nếu mã ngôn ngữ tìm được không có tệp `.json` tương ứng, phần mềm quay về **tiếng Anh**.

Lần chạy đầu tiên, mã ngôn ngữ xác định được sẽ tự động ghi vào `cfg.json`.

---

## 4. Một số lưu ý

- **Ký tự `&` trong khóa menu** (ví dụ `"&Help": "Trợ giúp/Giới thiệu(&H)"`) đánh dấu phím tắt Alt. Giữ lại nếu muốn có phím tắt, đặt ở vị trí phù hợp với ngôn ngữ của bạn.
- **Ký tự xuống dòng** viết là `\n` trong JSON.
- **Không dịch tên riêng** như `Edge-TTS`, `faster-whisper`, `CosyVoice`, `API`, `CUDA`, `SRT`, hay tên các mô hình.
- Ô chọn ngôn ngữ trong phần mềm đọc danh sách trực tiếp từ các tệp có trong thư mục, nên gói mới sẽ tự xuất hiện sau khi khởi động lại.
