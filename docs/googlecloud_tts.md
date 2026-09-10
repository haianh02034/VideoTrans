# Tích hợp Google Cloud Text-to-Speech

## Tổng quan
Phần tích hợp này thêm Google Cloud Text-to-Speech làm một kênh lồng tiếng mới trong Phiên Dịch Video, cho chất lượng tổng hợp giọng nói cao với nhiều ngôn ngữ và giọng đọc.

## Tính năng
- Hỗ trợ hơn 16 ngôn ngữ, gồm:
  - Tiếng Bồ Đào Nha (Brazil)
  - Tiếng Anh (Mỹ/Anh)
  - Tiếng Tây Ban Nha
  - Tiếng Pháp
  - Tiếng Đức
  - Tiếng Ý
  - Tiếng Nhật
  - Tiếng Hàn
  - Tiếng Trung
  - Tiếng Nga
  - Tiếng Hindi
  - Tiếng Ả Rập
  - Tiếng Thổ Nhĩ Kỳ
  - Tiếng Thái
  - Tiếng Việt
  - Tiếng Indonesia
- Nhiều lựa chọn giọng đọc cho mỗi ngôn ngữ
- Điều chỉnh được tốc độ đọc và cao độ
- Hỗ trợ nhiều định dạng âm thanh (MP3, LINEAR16, OGG_OPUS)
- Giao diện cấu hình dễ dùng

## Yêu cầu
1. Thư viện Python:
   ```bash
   pip install google-cloud-texttospeech>=2.14.0
   ```

2. Dự án Google Cloud:
   - Tạo một dự án trong [Google Cloud Console](https://console.cloud.google.com)
   - Bật Cloud Text-to-Speech API
   - Tạo tài khoản dịch vụ (service account) và tải tệp JSON chứng thực về

## Cấu hình
1. Trong Phiên Dịch Video, vào **Cài đặt → Google Cloud TTS**
2. Thiết lập các mục sau:
   - **Tệp JSON chứng thực**: đường dẫn tới tệp chứng thực tài khoản dịch vụ Google Cloud
   - **Ngôn ngữ**: chọn ngôn ngữ đích (ví dụ `vi-VN` cho tiếng Việt, `pt-BR` cho tiếng Bồ Đào Nha Brazil)
   - **Giọng đọc**: chọn trong danh sách giọng có sẵn của ngôn ngữ đã chọn
   - **Mã hóa âm thanh**: chọn định dạng đầu ra (MP3, LINEAR16 hoặc OGG_OPUS)

## Cách dùng
1. Chọn "Google Cloud TTS" làm kênh lồng tiếng
2. Chọn ngôn ngữ đích
3. Chọn một giọng đọc trong danh sách
4. Chỉnh tốc độ đọc và cao độ nếu cần
5. Tiến hành dịch video như bình thường

## Khắc phục sự cố
Các lỗi thường gặp và cách xử lý:

1. **"Credentials not found" (không tìm thấy chứng thực)**
   - Kiểm tra lại đường dẫn tới tệp JSON chứng thực
   - Đảm bảo tệp có quyền đọc

2. **"No voices available" (không có giọng đọc)**
   - Kiểm tra chứng thực của bạn đã được cấp quyền dùng Text-to-Speech API chưa
   - Kiểm tra ngôn ngữ đã chọn có được hỗ trợ không
   - Xem nhật ký để biết thông báo lỗi chi tiết

3. **"Invalid speaking rate" (tốc độ đọc không hợp lệ)**
   - Tốc độ đọc phải ở dạng phần trăm (ví dụ `+10%`, `-5%`)
   - Mặc định là `+0%`

4. **"Invalid pitch" (cao độ không hợp lệ)**
   - Cao độ phải tính bằng Hz (ví dụ `+2Hz`, `-1Hz`)
   - Mặc định là `+0Hz`

## Đóng góp
Bạn có thể tự nhiên:
- Báo lỗi
- Đề xuất cải tiến
- Thêm hỗ trợ cho ngôn ngữ khác
- Cải thiện giao diện cấu hình

## Giấy phép
Phần tích hợp này theo cùng giấy phép với dự án Phiên Dịch Video.

## Ghi nhận
- Google Cloud Text-to-Speech API
- Dự án gốc [pyVideoTrans](https://github.com/jianchang512/pyvideotrans) của jianchang512
- Những người đã đóng góp cho phần tích hợp này
