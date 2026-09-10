# Hướng dẫn dùng Phiên Dịch Video WebUI

## ⚠️ Lưu ý quan trọng

> **Bản WebUI chỉ có một phần chức năng**, chủ yếu dùng cho các trường hợp:
> - Triển khai trên máy chủ đám mây (truy cập dịch vụ dịch từ xa)
> - Triển khai trong mạng nội bộ (máy chủ tách khỏi máy sử dụng)
> - Triển khai bằng Docker
>
> **Nếu cần đầy đủ chức năng**, hãy dùng bản desktop (`sp.exe`) hoặc chạy từ mã nguồn (`sp.py`).
> Bản desktop hỗ trợ cấu hình nhiều kênh API hơn, chỉnh sửa xen giữa theo thời gian thực, xử lý hàng loạt và các tính năng nâng cao khác.

---

## 1. Cách triển khai

### 1.1 Chạy từ mã nguồn (khuyến nghị)

```bash
git clone https://github.com/haianh02034/VideoTrans.git
cd VideoTrans
uv sync --extra webui
```

Khởi động dịch vụ:

```bash
uv run webui.py                    # mặc định 0.0.0.0:7860
uv run webui.py --port 8080        # chỉ định cổng
uv run webui.py --host 127.0.0.1   # chỉ truy cập được từ máy này
uv run webui.py --share            # tạo liên kết Gradio công khai ra Internet
```

Truy cập: `http://127.0.0.1:7860` hoặc `http://<IP máy chủ>:7860`

> ⚠️ **Về bảo mật:** mặc định WebUI lắng nghe trên `0.0.0.0`, nghĩa là **mọi máy trong mạng đều vào được và không có bước xác thực nào**. Nếu chỉ dùng trên máy mình, hãy luôn thêm `--host 127.0.0.1`. Cờ `--share` tạo liên kết công khai ra Internet — chỉ bật khi bạn thực sự cần và ý thức được rằng ai có liên kết đều dùng được.

### 1.2 Triển khai bằng Docker

```bash
# Dựng image
git clone https://github.com/haianh02034/VideoTrans.git
cd VideoTrans
docker build -t phiendichvideo-webui .

# Chạy
docker run -d -p 7860:7860 --name phiendichvideo phiendichvideo-webui

# Giữ lại kết quả và mô hình đã tải
docker run -d -p 7860:7860 \
  -v ./data/output:/app/output \
  -v ./data/models:/app/models \
  --name phiendichvideo phiendichvideo-webui

# Tăng tốc bằng GPU
docker run -d -p 7860:7860 --gpus all \
  -v ./data/output:/app/output \
  -v ./data/models:/app/models \
  --name phiendichvideo phiendichvideo-webui
```

> ⚠️ Đừng gắn volume vào `/app/phiendichvideo` — đó là thư mục mã nguồn của phần mềm, gắn đè lên sẽ che mất và container không khởi động được.

### 1.3 Google Colab

1. Mở https://colab.research.google.com/drive/1kPTeAMz3LnWRnGmabcz4AWW42hiehmfm?usp=sharing
2. Đăng nhập tài khoản Google → bấm **Chạy tất cả**
3. Đợi liên kết `*.gradio.live` hiện ra rồi bấm vào để dùng

> ⚠️ Bản Colab miễn phí giới hạn thời gian dùng 4-6 tiếng.

---

## 2. Giới thiệu giao diện

WebUI chia thành ba thẻ:

### 2.1 🎬 Dịch video (màn hình chính)

**Chọn tệp**: hỗ trợ các định dạng mp4/mkv/avi/mov/webm/wav/mp3/m4a/flac...

**Nhận dạng giọng nói**: chọn faster-whisper / openai-whisper / Qwen-ASR / FunASR / Huggingface_ASR (đều là kênh cục bộ tích hợp sẵn, miễn phí)

**Dịch phụ đề**: chọn Google / Microsoft / M2M100 (kênh miễn phí)

**Lồng tiếng phụ đề**: chọn Edge-TTS / Qwen3-TTS / MOSS-TTS / Piper / VITS / Supertonic / ChatterBox / gTTS (kênh miễn phí hoặc cục bộ tích hợp sẵn)

**Đồng bộ và phụ đề**: tăng tốc lồng tiếng, làm chậm video, chỉnh tốc độ đọc / âm lượng / cao độ, kiểu nhúng phụ đề

**Thêm cài đặt**: khử nhiễu, xử lý dấu câu, tách giọng nói khỏi nhạc nền, nhúng lại nhạc nền, tăng tốc CUDA

**Chỉnh kiểu phụ đề cứng**: tùy chỉnh đầy đủ phông chữ, màu sắc, viền, đổ bóng, căn lề...

### 2.2 ⚙️ Cài đặt kênh

Cấu hình địa chỉ API, khóa SK, mô hình... của từng kênh. **Dùng chung với bản desktop**, cấu hình được lưu trong `phiendichvideo/params.json`.

Bao gồm: kênh dịch, kênh nhận dạng giọng nói, kênh lồng tiếng, cài đặt âm thanh mẫu.

> Trước khi dùng kênh API, cần cấu hình sẵn địa chỉ API và khóa SK bằng bản desktop (sp.exe).

### 2.3 🔧 Tùy chọn nâng cao

Cấu hình tham số nâng cao toàn cục, dùng chung hoàn toàn với **Menu → Công cụ → Tùy chọn nâng cao** của bản desktop.

Bao gồm: cài đặt chung, kiểm soát video đầu ra, tham số nhận dạng giọng nói, điều chỉnh dịch phụ đề, điều chỉnh lồng tiếng, đồng bộ phụ đề với hình và tiếng, prompt cho mô hình Whisper.

---

## 3. Thực hiện dịch

1. Chọn tệp video/audio
2. Cấu hình tham số nhận dạng / dịch / lồng tiếng
3. Bấm **🚀 Bắt đầu**

Trong quá trình chạy:
- Nút chuyển thành **⏳ Đang chạy...** và bị vô hiệu hóa
- Nhật ký bên phải hiển thị tiến độ 8 giai đoạn theo thời gian thực
- Xong thì nút trở lại bình thường, khu vực xem trước phát được video ngay, khu vực tệp cho phép tải về

---

## 4. So sánh với bản desktop

| Chức năng | WebUI | Bản desktop |
|------|:-----:|:-----:|
| Quy trình dịch video đầy đủ | ✅ | ✅ |
| Kênh API (cần cấu hình trước bằng bản desktop) | ✅ | ✅ |
| Cấu hình tùy chọn nâng cao | ✅ | ✅ |
| Chỉnh sửa phụ đề xen giữa | ❌ | ✅ |
| Xử lý hàng loạt | ❌ | ✅ |
| Xem trước video | ✅ | ❌ |
| Truy cập từ xa / Docker | ✅ | ❌ |

---

## 5. Câu hỏi thường gặp

**Hỏi: Khởi động báo lỗi No module named gradio**
Chạy `uv sync --extra webui`

**Hỏi: Docker giữ lại dữ liệu thế nào**
`-v ./data/output:/app/output -v ./data/models:/app/models`

**Hỏi: Docker dùng GPU thế nào**
Cài nvidia-container-toolkit rồi chạy: `docker run --gpus all ...`

**Hỏi: Dùng kênh API thế nào**
Cấu hình sẵn địa chỉ API và khóa SK bằng bản desktop, WebUI sẽ tự đọc `params.json`

**Hỏi: Tạo liên kết công khai thế nào**
`uv run webui.py --share`, cửa sổ dòng lệnh sẽ in ra liên kết `*.gradio.live` tạm thời
