# Phiên Dịch Video

<div align="center">

**Công cụ mã nguồn mở dịch video, nhận dạng giọng nói, lồng tiếng AI và dịch phụ đề**

[![License](https://img.shields.io/badge/License-GPL_v3-blue.svg)](LICENSE) [![Python](https://img.shields.io/badge/Python-3.10-green.svg)](https://www.python.org/) [![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

</div>

**Phiên Dịch Video** chuyển video từ ngôn ngữ này sang ngôn ngữ khác qua một quy trình khép kín: nhận dạng giọng nói, dịch phụ đề, lồng tiếng nhiều giọng và đồng bộ hình tiếng. Phần mềm chạy được hoàn toàn ngoại tuyến trên máy, hoặc kết nối tới hàng chục dịch vụ API trực tuyến tùy bạn chọn.

> Đây là bản Việt hóa của [pyVideoTrans](https://github.com/jianchang512/pyvideotrans) do [jianchang512](https://github.com/jianchang512) phát triển, phát hành lại theo giấy phép GPL-v3. Xem mục [Giấy phép và ghi nhận](#-giấy-phép-và-ghi-nhận).

---

## ✨ Tính năng chính

- **🎥 Dịch video tự động** — một lần bấm: nhận dạng giọng nói (ASR) → dịch phụ đề → tổng hợp giọng nói (TTS) → dựng video.
- **🎙️ Bóc phụ đề hàng loạt** — chuyển audio/video thành tệp SRT, có **phân tách người nói**.
- **🗣️ Lồng tiếng nhiều giọng** — gán giọng AI riêng cho từng người nói.
- **🧬 Nhân bản giọng nói** — tích hợp **F5-TTS, CosyVoice, GPT-SoVITS**.
- **🖥️ Chỉnh sửa xen giữa** — tạm dừng để soát lại ở từng bước: nhận dạng, dịch, lồng tiếng.
- **🛠️ Bộ công cụ phụ trợ** — tách giọng/nhạc nền, ghép video và phụ đề, đồng bộ hình tiếng, cắt video theo phụ đề.
- **💻 Dòng lệnh (CLI)** — chạy không cần giao diện, tiện cho máy chủ và xử lý hàng loạt.
- **🌐 Giao diện web (WebUI)** — truy cập qua trình duyệt.
- **🌏 Ba ngôn ngữ giao diện** — Tiếng Việt, Tiếng Anh, Tiếng Trung.

---

## 🚀 Cài đặt từ mã nguồn

Khuyến nghị dùng **[`uv`](https://docs.astral.sh/uv/)** để quản lý gói.

### 1. Yêu cầu

- **Python 3.10** (dự án yêu cầu `>=3.10, <3.11`)
- **FFmpeg** đã cài và có trong biến môi trường PATH:
  - macOS: `brew install ffmpeg libsndfile git`
  - Linux (Ubuntu/Debian): `sudo apt-get install ffmpeg libsndfile1-dev`
  - Windows: [tải FFmpeg](https://ffmpeg.org/download.html) rồi thêm vào PATH, hoặc đặt `ffmpeg.exe` và `ffprobe.exe` ngay trong thư mục dự án.

### 2. Cài uv (nếu chưa có)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. Tải mã nguồn và cài thư viện

```bash
git clone https://github.com/haianh02034/VideoTrans.git
cd VideoTrans
uv sync
```

Các nhóm thư viện tùy chọn hiện có: `webui`, `mosstts`, `dotnet`.

```bash
uv sync --extra webui      # giao diện web
uv sync --extra mosstts    # kênh MOSS-TTS
uv sync --all-extras       # cài tất cả
```

---

## ▶️ Chạy phần mềm

### Giao diện đồ họa

```bash
uv run sp.py               # theo ngôn ngữ hệ thống
uv run sp.py --lang vi     # ép dùng tiếng Việt
```

Đổi ngôn ngữ trong phần mềm: **Công cụ → Tùy chọn nâng cao → Ngôn ngữ giao diện**, chọn `vi` rồi khởi động lại.

### Dòng lệnh

```bash
# Dịch video
uv run cli.py --task vtv --name "./video.mp4" \
  --source_language_code zh-cn --target_language_code vi \
  --voice_role "vi-VN-NamMinhNeural"

# Bóc phụ đề từ audio
uv run cli.py --task stt --name "./audio.wav" --model_name large-v3

# Dịch tệp phụ đề
uv run cli.py --task sts --name "./subs.srt" --target_language_code vi

# Lồng tiếng từ phụ đề
uv run cli.py --task tts --name "./subs.srt" --voice_role "vi-VN-HoaiMyNeural"

# Xem danh sách kênh / ngôn ngữ / mô hình
uv run cli.py --list providers
```

Xem [tài liệu CLI đầy đủ](docs/cli.md).

### Giao diện web

```bash
uv sync --extra webui
uv run webui.py
```

> ⚠️ WebUI mặc định lắng nghe trên `0.0.0.0`, nghĩa là **mọi máy trong mạng LAN đều truy cập được** và không có xác thực. Nếu chỉ dùng trên máy mình, hãy chạy `uv run webui.py --host 127.0.0.1`. Cờ `--share` sẽ tạo liên kết công khai ra Internet — chỉ bật khi bạn thực sự cần.

Xem [tài liệu WebUI](docs/webui.md).

### Docker

```bash
# Bản CPU
docker build -t phiendichvideo-webui .

# Bản GPU
docker build --build-arg USE_CUDA=true -t phiendichvideo-webui:gpu .

# Chạy
docker run -d -p 7860:7860 --name phiendichvideo phiendichvideo-webui

# Giữ lại kết quả và mô hình đã tải
docker run -d -p 7860:7860 \
  -v ./data/output:/app/output \
  -v ./data/models:/app/models \
  --name phiendichvideo phiendichvideo-webui
```

Image được dựng từ mã nguồn trong thư mục hiện tại (`COPY`), không tải từ GitHub, nên mọi thay đổi cục bộ đều có hiệu lực ngay. Tệp `.dockerignore` loại `.venv/`, `models/`, `ffmpeg/` cùng các tệp cấu hình cá nhân ra khỏi image.

> ⚠️ Đừng gắn volume vào `/app/phiendichvideo` — thư mục đó là mã nguồn của phần mềm, gắn đè lên sẽ che mất và phần mềm không chạy được. Tệp `cfg.json` và `params.json` cố ý không được đưa vào image (chúng chứa khóa API); phần mềm tự sinh lại với giá trị mặc định khi khởi động.

---

## ⚡ Tăng tốc bằng GPU

Nếu có card NVIDIA, cài bản PyTorch hỗ trợ CUDA:

```bash
uv remove torch torchaudio
uv add torch==2.7 torchaudio==2.7 --index-url https://download.pytorch.org/whl/cu128
uv add nvidia-cublas-cu12 nvidia-cudnn-cu12
```

Cần **CUDA 12.8** và **cuDNN 9.11**. Với card AMD, xem [hướng dẫn Whisper.NET](docs/whisper_net_setup.md).

---

## 🧩 Các kênh hỗ trợ (một phần)

| Nhóm | Kênh / Mô hình | Ghi chú |
| :--- | :--- | :--- |
| **Nhận dạng giọng nói** | **Faster-Whisper** (cục bộ) | Khuyến nghị, nhanh và chính xác |
| | WhisperX / Parakeet | Căn chỉnh dấu thời gian, phân tách người nói |
| | Qwen3-ASR, ByteDance, Deepgram | API trực tuyến |
| **Dịch thuật** | **DeepSeek** / ChatGPT / Gemini | Hiểu ngữ cảnh, bản dịch tự nhiên hơn |
| | Google / Microsoft | Dịch máy truyền thống, miễn phí, nhanh |
| | Ollama / M2M100 | Dịch hoàn toàn ngoại tuyến |
| **Lồng tiếng** | **Edge-TTS** | Miễn phí, có giọng tiếng Việt, chất lượng tốt |
| | **F5-TTS / CosyVoice** | Nhân bản giọng, cần tự triển khai |
| | GPT-SoVITS / ChatTTS | TTS mã nguồn mở chất lượng cao |
| | OpenAI / Azure / Minimaxi | API thương mại |

Xem danh sách đầy đủ bằng `uv run cli.py --list providers`.

---

## 🔒 Về dữ liệu và quyền riêng tư

Phần mềm chỉ tự động kết nối ra ngoài ở hai chỗ: kiểm tra phiên bản mới và dò xem có vào được `huggingface.co` không (nếu không thì chuyển sang máy chủ gương).

Ngoài ra, **dữ liệu chỉ được gửi đi khi bạn chọn một kênh trực tuyến**. Ví dụ chọn Google Dịch thì phụ đề được gửi tới Google, chọn Edge-TTS thì văn bản được gửi tới Microsoft. Muốn hoàn toàn ngoại tuyến, hãy chọn các kênh có nhãn *Cục bộ*: faster-whisper cho nhận dạng, M2M100 hoặc Ollama cho dịch, và một TTS chạy trên máy.

---

## 📚 Tài liệu

- [Kiến trúc kỹ thuật](docs/architecture.md) · [Dòng lệnh](docs/cli.md) · [WebUI](docs/webui.md) · [Đồng bộ hình tiếng](docs/Synchronize.md) · [Câu hỏi thường gặp](docs/faq.md)
- Tài liệu của dự án gốc: [pyvideotrans.com](https://pyvideotrans.com) · [Diễn đàn hỏi đáp](https://bbs.pyvideotrans.com)

---

## ⚠️ Miễn trừ trách nhiệm

Đây là phần mềm mã nguồn mở, miễn phí, phi thương mại. Người dùng tự chịu trách nhiệm về mọi hậu quả pháp lý phát sinh khi sử dụng, bao gồm nhưng không giới hạn ở việc gọi API của bên thứ ba hay xử lý video có bản quyền. Vui lòng tuân thủ pháp luật sở tại và điều khoản sử dụng của các nhà cung cấp dịch vụ.

---

## 📜 Giấy phép và ghi nhận

Dự án phát hành theo giấy phép [GPL-v3](LICENSE).

Toàn bộ phần lõi do **[jianchang512](https://github.com/jianchang512)** phát triển trong dự án [pyVideoTrans](https://github.com/jianchang512/pyvideotrans). Kho này là bản phái sinh, phần đóng góp thêm là Việt hóa giao diện và đổi tên sản phẩm. Xin cảm ơn tác giả gốc.

Phần mềm dựa trên các dự án mã nguồn mở sau (một phần):

[FFmpeg](https://github.com/FFmpeg/FFmpeg) · [PySide6](https://pypi.org/project/PySide6/) · [faster-whisper](https://github.com/SYSTRAN/faster-whisper) · [openai-whisper](https://github.com/openai/whisper) · [edge-tts](https://github.com/rany2/edge-tts) · [F5-TTS](https://github.com/SWivid/F5-TTS) · [CosyVoice](https://github.com/FunAudioLLM/CosyVoice) · [Gradio](https://www.gradio.app/)
