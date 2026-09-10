# Hướng dẫn dùng Phiên Dịch Video qua dòng lệnh (CLI)

Phiên Dịch Video hỗ trợ chạy không cần giao diện, phù hợp cho triển khai trên máy chủ, xử lý hàng loạt và các quy trình tự động.

---

## Mục lục

- [Yêu cầu môi trường](#yêu-cầu-môi-trường)
- [Cách dùng cơ bản](#cách-dùng-cơ-bản)
- [Tùy chọn chung](#tùy-chọn-chung)
- [Tổng quan các loại tác vụ](#tổng-quan-các-loại-tác-vụ)
- [STT — Nhận dạng giọng nói](#stt--nhận-dạng-giọng-nói)
- [TTS — Lồng tiếng từ văn bản](#tts--lồng-tiếng-từ-văn-bản)
- [STS — Dịch phụ đề](#sts--dịch-phụ-đề)
- [VTV — Dịch video](#vtv--dịch-video)
- [Công cụ tra cứu](#công-cụ-tra-cứu)
- [Ví dụ đầy đủ](#ví-dụ-đầy-đủ)
- [Câu hỏi thường gặp](#câu-hỏi-thường-gặp)

---

## Yêu cầu môi trường

| Hạng mục | Yêu cầu |
|------|------|
| Python | 3.10 |
| Quản lý gói | [uv](https://docs.astral.sh/uv/) |
| FFmpeg | Bắt buộc cài và thêm vào biến môi trường PATH (bản đóng gói cho Windows đã tích hợp sẵn) |
| Tăng tốc GPU (tùy chọn) | Card NVIDIA + CUDA 12.8 + cuDNN 9.11 |

### Cách khởi động

```bash
# Chạy từ mã nguồn
uv run cli.py [tham số...]

# Bản đóng gói cho Windows
cli.exe [tham số...]
```

> **Lưu ý**: bản đóng gói cho Windows (`cli.exe`) không cần cài Python, chạy trực tiếp là được.

---

## Cách dùng cơ bản

```bash
uv run cli.py --task <loại tác vụ> --name "<đường dẫn tệp>" [tham số khác]
```

**Bốn loại tác vụ:**

| Tác vụ | Mô tả | Quy trình |
|------|------|--------|
| `stt` | Nhận dạng giọng nói — chuyển tiếng nói trong audio/video thành phụ đề SRT | Tiền xử lý → nhận dạng → phân tách người nói → xuất phụ đề |
| `tts` | Lồng tiếng — chuyển phụ đề SRT hoặc văn bản thành âm thanh | Tiền xử lý → lồng tiếng → đồng bộ hình tiếng → xuất âm thanh |
| `sts` | Dịch phụ đề — dịch tệp SRT sang ngôn ngữ đích | Tiền xử lý → dịch → xuất phụ đề |
| `vtv` | Dịch video — trọn quy trình: nhận dạng → dịch → lồng tiếng → dựng video | Tiền xử lý → nhận dạng → phân tách người nói → dịch → lồng tiếng → đồng bộ → nhận dạng lần 2 → dựng video |

---

## Tùy chọn chung

| Tùy chọn | Mô tả | Mặc định |
|------|------|--------|
| `--task {stt,tts,sts,vtv}` | **Bắt buộc** — loại tác vụ | — |
| `--name FILE` | **Bắt buộc** — đường dẫn tuyệt đối của tệp đầu vào | — |
| `--output-dir DIR` | Thư mục đầu ra | `<thư mục phần mềm>/output/<tên tệp>/` |
| `--list {providers,languages,models}` | Tra cứu danh sách kênh / ngôn ngữ / mô hình | — |
| `--log-level {DEBUG,INFO,WARNING,ERROR}` | Mức nhật ký | `WARNING` |
| `-v, --verbose` | In chi tiết (tương đương `--log-level INFO`) | không |
| `-q, --quiet` | Chế độ im lặng, chỉ in lỗi | không |
| `--version` | Hiện số phiên bản | — |
| `-h, --help` | Hiện trợ giúp | — |

---

## Tổng quan các loại tác vụ

### Tham số bắt buộc theo từng tác vụ

| Tác vụ | `--name` | `--voice_role` | `--source_language_code` | `--target_language_code` |
|------|:---:|:---:|:---:|:---:|
| `stt` | ✅ | — | — | — |
| `tts` | ✅ | ✅ | — | — |
| `sts` | ✅ | — | tùy chọn (mặc định auto) | ✅ |
| `vtv` | ✅ | tùy chọn (mặc định No) | ✅ | ✅ |

### Tham số áp dụng cho tác vụ nào

| Tham số | stt | tts | sts | vtv |
|------|:---:|:---:|:---:|:---:|
| `--recogn_type` | ✅ | — | — | ✅ |
| `--detect_language` | ✅ | — | — | ✅ |
| `--model_name` | ✅ | — | — | ✅ |
| `--cuda` | ✅ | — | — | ✅ |
| `--remove_noise` | ✅ | — | — | ✅ |
| `--enable_diariz` | ✅ | — | — | ✅ |
| `--nums_diariz` | ✅ | — | — | ✅ |
| `--rephrase` | ✅ | — | — | ✅ |
| `--fix_punc` | ✅ | — | — | ✅ |
| `--tts_type` | — | ✅ | — | ✅ |
| `--voice_role` | — | ✅ | — | ✅ |
| `--voice_rate` | — | ✅ | — | ✅ |
| `--volume` | — | ✅ | — | ✅ |
| `--pitch` | — | ✅ | — | ✅ |
| `--voice_autorate` | — | ✅ | — | ✅ |
| `--align_sub_audio` | — | ✅ | — | ✅ |
| `--translate_type` | — | — | ✅ | ✅ |
| `--source_language_code` | — | — | ✅ | ✅ |
| `--target_language_code` | — | — | ✅ | ✅ |
| `--video_autorate` | — | — | — | ✅ |
| `--is_separate` | — | — | — | ✅ |
| `--recogn2pass` | — | — | — | ✅ |
| `--subtitle_type` | — | — | — | ✅ |
| `--clear_cache` | — | — | — | ✅ |

---

## STT — Nhận dạng giọng nói

Chuyển tiếng nói trong audio hoặc video thành tệp phụ đề SRT có dấu thời gian.

### Tham số

| Tham số | Kiểu | Mặc định | Mô tả |
|------|------|--------|------|
| `--recogn_type` | int | `0` | Chỉ mục kênh nhận dạng (0=faster-whisper, 1=openai-whisper, ...) |
| `--detect_language` | str | `auto` | Ngôn ngữ nói trong audio (auto=tự nhận diện, vi, zh-cn, en, ja, ...) |
| `--model_name` | str | `tiny` | Tên mô hình (chỉ có tác dụng với faster-whisper/openai-whisper) |
| `--cuda` | cờ | không | Bật tăng tốc GPU bằng CUDA |
| `--remove_noise` | cờ | không | Bật khử nhiễu |
| `--enable_diariz` | cờ | không | Bật nhận dạng người nói |
| `--nums_diariz` | int | `-1` | Số người nói (-1 = tự nhận diện) |
| `--rephrase` | int | `0` | Tách câu lại (0=mặc định, 1=dùng LLM) |
| `--fix_punc` | cờ | không | Khôi phục dấu câu |

### Ví dụ

**Đơn giản nhất — dùng faster-whisper bóc phụ đề:**

```bash
uv run cli.py --task stt --name "60.mp4"
```

> Mặc định dùng faster-whisper + mô hình tiny, xuất tệp SRT vào thư mục `output/60-mp4/`.

**Dùng mô hình large-v3 + tăng tốc GPU:**

```bash
uv run cli.py --task stt --name "60.mp4" --recogn_type 0 --model_name large-v3 --cuda
```

**Chỉ định ngôn ngữ nguồn là tiếng Việt + khử nhiễu:**

```bash
uv run cli.py --task stt --name "60.mp4" --detect_language vi --remove_noise --cuda
```

**Dùng kênh openai-whisper:**

```bash
uv run cli.py --task stt --name "60.mp4" --recogn_type 1 --model_name large-v3 --cuda
```

**Bật nhận dạng người nói (chỉ định 2 người):**

```bash
uv run cli.py --task stt --name "60.mp4" --enable_diariz --nums_diariz 2 --cuda
```

**Bật tách câu bằng LLM + khôi phục dấu câu:**

```bash
uv run cli.py --task stt --name "60.mp4" --rephrase 1 --fix_punc --cuda
```

**Tùy chỉnh thư mục đầu ra:**

```bash
uv run cli.py --task stt --name "60.mp4" --output-dir "D:/ket_qua" --cuda
```

---

## TTS — Lồng tiếng từ văn bản

Chuyển tệp phụ đề SRT hoặc tệp văn bản thuần thành âm thanh.

### Tham số

| Tham số | Kiểu | Mặc định | Mô tả |
|------|------|--------|------|
| `--tts_type` | int | `0` | Chỉ mục kênh lồng tiếng (0=Edge-TTS, ...) |
| `--voice_role` | str | **bắt buộc** | Tên giọng đọc |
| `--voice_rate` | str | `+0%` | Tốc độ đọc (`+20%` nhanh hơn, `-10%` chậm lại) |
| `--volume` | str | `+0%` | Âm lượng (`+50%` to hơn, `-30%` nhỏ đi) |
| `--pitch` | str | `+0Hz` | Cao độ (`+10Hz` cao hơn, `-5Hz` trầm hơn) |
| `--voice_autorate` | cờ | không | Tự tăng tốc âm thanh để khớp dấu thời gian phụ đề |
| `--align_sub_audio` | cờ | không | Ép sửa dấu thời gian phụ đề để khớp âm thanh |
| `--target_language_code` | str | `None` | Mã ngôn ngữ đích |

### Ví dụ

**Đơn giản nhất — dùng Edge-TTS lồng tiếng Việt cho phụ đề:**

```bash
uv run cli.py --task tts --name "phude.srt" --voice_role "vi-VN-NamMinhNeural"
```

> Dùng giọng nam NamMinh miễn phí của Microsoft Edge-TTS để tạo âm thanh cho phụ đề tiếng Việt.

**Lồng tiếng Anh:**

```bash
uv run cli.py --task tts --name "phude.srt" --voice_role "en-US-GuyNeural" --target_language_code en
```

**Chỉnh tốc độ đọc và âm lượng:**

```bash
uv run cli.py --task tts --name "phude.srt" --voice_role "vi-VN-HoaiMyNeural" --voice_rate=+20% --volume=+10%
```

**Chỉnh cao độ (trầm hơn):**

```bash
uv run cli.py --task tts --name "phude.srt" --voice_role "vi-VN-NamMinhNeural" --pitch=-5Hz
```

**Bật tự tăng tốc để khớp phụ đề:**

```bash
uv run cli.py --task tts --name "phude.srt" --voice_role "vi-VN-NamMinhNeural" --voice_autorate
```

**Dùng kênh TTS khác (ví dụ OpenAI TTS, xem chỉ mục kênh bằng `--list providers`):**

```bash
uv run cli.py --task tts --name "phude.srt" --tts_type <chỉ mục kênh> --voice_role "alloy"
```

### Một số giọng Edge-TTS hay dùng

| Tên giọng | Giới tính | Ngôn ngữ | Ghi chú |
|----------|------|------|------|
| `vi-VN-NamMinhNeural` | Nam | Tiếng Việt | Nam Minh — giọng nam tự nhiên |
| `vi-VN-HoaiMyNeural` | Nữ | Tiếng Việt | Hoài My — giọng nữ tự nhiên |
| `zh-CN-YunyangNeural` | Nam | Tiếng Trung | Vân Dương — phong cách đọc bản tin |
| `zh-CN-XiaoxiaoNeural` | Nữ | Tiếng Trung | Hiểu Hiểu — hội thoại tự nhiên |
| `en-US-GuyNeural` | Nam | Tiếng Anh | Guy — giọng nam tự nhiên |
| `en-US-JennyNeural` | Nữ | Tiếng Anh | Jenny — giọng nữ tự nhiên |
| `en-US-AriaNeural` | Nữ | Tiếng Anh | Aria — giọng nữ chuyên nghiệp |
| `en-US-BrianNeural` | Nam | Tiếng Anh | Brian — giọng nam điềm đạm |

> Xem danh sách giọng đầy đủ bằng `uv run cli.py --list providers`, hoặc trong phần cài đặt TTS của giao diện đồ họa.

---

## STS — Dịch phụ đề

Dịch tệp phụ đề SRT từ ngôn ngữ này sang ngôn ngữ khác.

### Tham số

| Tham số | Kiểu | Mặc định | Mô tả |
|------|------|--------|------|
| `--translate_type` | int | `0` | Chỉ mục kênh dịch (0=Google, ...) |
| `--source_language_code` | str | `auto` | Mã ngôn ngữ nguồn (auto=tự nhận diện) |
| `--target_language_code` | str | **bắt buộc** | Mã ngôn ngữ đích |

### Ví dụ

**Đơn giản nhất — dịch phụ đề sang tiếng Việt:**

```bash
uv run cli.py --task sts --name "subs.srt" --target_language_code vi
```

> Mặc định dùng Google Dịch, ngôn ngữ nguồn tự nhận diện.

**Chỉ định ngôn ngữ nguồn là tiếng Trung:**

```bash
uv run cli.py --task sts --name "subs.srt" --source_language_code zh-cn --target_language_code vi
```

**Dùng kênh dịch khác (ví dụ DeepSeek, xem chỉ mục kênh bằng `--list providers`):**

```bash
uv run cli.py --task sts --name "subs.srt" --translate_type <chỉ mục kênh> --target_language_code vi
```

**Dịch sang tiếng Anh:**

```bash
uv run cli.py --task sts --name "subs.srt" --target_language_code en
```

**Dịch sang tiếng Nhật:**

```bash
uv run cli.py --task sts --name "subs.srt" --target_language_code ja
```

---

## VTV — Dịch video

Dịch video trọn quy trình: nhận dạng giọng nói → dịch phụ đề → lồng tiếng → dựng lại video. Đây là loại tác vụ hay dùng nhất và cũng phức tạp nhất.

### Tham số

Chế độ VTV nhận toàn bộ tham số của STT, TTS và STS, cộng thêm:

| Tham số | Kiểu | Mặc định | Mô tả |
|------|------|--------|------|
| `--source_language_code` | str | **bắt buộc** | Mã ngôn ngữ nguồn (không được để auto) |
| `--target_language_code` | str | **bắt buộc** | Mã ngôn ngữ đích |
| `--voice_role` | str | `No` | Giọng lồng tiếng (`No` = không lồng tiếng) |
| `--video_autorate` | cờ | không | Tự làm chậm video để khớp lồng tiếng |
| `--is_separate` | cờ | không | Tách giọng nói khỏi nhạc nền |
| `--recogn2pass` | cờ | không | Nhận dạng lần 2 (cho phụ đề chuẩn hơn) |
| `--subtitle_type` | int | `1` | Kiểu phụ đề (0=không, 1=cứng, 2=mềm, 3=cứng song ngữ, 4=mềm song ngữ) |
| `--clear_cache` | cờ | có | Dọn bộ nhớ đệm sau khi xong |
| `--no-clear-cache` | cờ | — | Không dọn bộ nhớ đệm |

### Ví dụ

**Đơn giản nhất — dịch video tiếng Trung sang tiếng Việt (không lồng tiếng, chỉ thay phụ đề):**

```bash
uv run cli.py --task vtv --name "60.mp4" --source_language_code zh-cn --target_language_code vi
```

> Mặc định dùng faster-whisper để nhận dạng + Google Dịch + không lồng tiếng (voice_role=No), nhúng phụ đề cứng.

**Trọn quy trình — dịch sang tiếng Việt và lồng tiếng:**

```bash
uv run cli.py --task vtv --name "60.mp4" --source_language_code zh-cn --target_language_code vi --voice_role "vi-VN-NamMinhNeural"
```

> Dùng giọng nam Nam Minh của Edge-TTS để lồng tiếng cho phụ đề tiếng Việt đã dịch.

**Tăng tốc GPU + mô hình độ chính xác cao:**

```bash
uv run cli.py --task vtv --name "60.mp4" --source_language_code zh-cn --target_language_code vi --voice_role "vi-VN-NamMinhNeural" --cuda --recogn_type 0 --model_name large-v3
```

**Tách giọng nói khỏi nhạc nền (tăng chất lượng nhận dạng và lồng tiếng):**

```bash
uv run cli.py --task vtv --name "60.mp4" --source_language_code zh-cn --target_language_code vi --voice_role "vi-VN-NamMinhNeural" --is_separate --cuda
```

**Phụ đề cứng song ngữ + nhận dạng lần 2:**

```bash
uv run cli.py --task vtv --name "60.mp4" --source_language_code zh-cn --target_language_code vi --voice_role "vi-VN-NamMinhNeural" --subtitle_type 3 --recogn2pass --cuda
```

**Phụ đề mềm (bật/tắt được trong trình phát) + tự tăng tốc âm thanh:**

```bash
uv run cli.py --task vtv --name "60.mp4" --source_language_code zh-cn --target_language_code vi --voice_role "vi-VN-NamMinhNeural" --subtitle_type 2 --voice_autorate --cuda
```

**Làm chậm video để khớp (khi lồng tiếng dài hơn video):**

```bash
uv run cli.py --task vtv --name "60.mp4" --source_language_code zh-cn --target_language_code vi --voice_role "vi-VN-NamMinhNeural" --video_autorate --cuda
```

**Tùy chỉnh thư mục đầu ra + giữ lại bộ nhớ đệm:**

```bash
uv run cli.py --task vtv --name "60.mp4" --source_language_code zh-cn --target_language_code vi --voice_role "vi-VN-NamMinhNeural" --output-dir "D:/da_dich" --no-clear-cache
```

**Dịch video tiếng Anh sang tiếng Việt:**

```bash
uv run cli.py --task vtv --name "60.mp4" --source_language_code en --target_language_code vi --voice_role "vi-VN-HoaiMyNeural" --cuda
```

**Dịch sang tiếng Nhật và lồng tiếng:**

```bash
uv run cli.py --task vtv --name "60.mp4" --source_language_code vi --target_language_code ja --voice_role "ja-JP-KeitaNeural" --cuda
```

**Chạy chế độ im lặng (chỉ in lỗi):**

```bash
uv run cli.py --task vtv --name "60.mp4" --source_language_code zh-cn --target_language_code vi --voice_role "vi-VN-NamMinhNeural" -q
```

**Chế độ nhật ký chi tiết (để gỡ lỗi):**

```bash
uv run cli.py --task vtv --name "60.mp4" --source_language_code zh-cn --target_language_code vi --voice_role "vi-VN-NamMinhNeural" -v
```

---

## Công cụ tra cứu

### Liệt kê mọi kênh khả dụng

```bash
uv run cli.py --list providers
```

Ví dụ kết quả:

```
=== Kênh khả dụng ===

--- Nhận dạng giọng nói (STT) ---
   0 = faster-whisper(Cục bộ Tích hợp sẵn)
   1 = openai-whisper(Cục bộ Tích hợp sẵn)
   2 = Qwen-ASR(Cục bộ Tích hợp sẵn)
  ...

--- Dịch thuật ---
   0 = Google (miễn phí)
   1 = Microsoft (miễn phí)
   2 = Dịch Baidu
  ...

--- Lồng tiếng (TTS) ---
   0 = Edge-TTS (miễn phí)
   1 = Qwen3-TTS(Cục bộ Tích hợp sẵn)
  ...
```

### Liệt kê mọi ngôn ngữ hỗ trợ

```bash
uv run cli.py --list languages
```

Ví dụ kết quả:

```
=== Mã ngôn ngữ khả dụng ===
  vi         Tiếng Việt
  en         Tiếng Anh
  zh-cn      Tiếng Trung giản thể
  zh-tw      Tiếng Trung phồn thể
  ja         Tiếng Nhật
  ko         Tiếng Hàn
  fr         Tiếng Pháp
  ...
```

### Liệt kê các mô hình faster-whisper

```bash
uv run cli.py --list models
```

Ví dụ kết quả:

```
=== Mô hình faster-whisper ===
  tiny                      Systran/faster-whisper-tiny
  base                      Systran/faster-whisper-base
  small                     Systran/faster-whisper-small
  medium                    Systran/faster-whisper-medium
  large-v3                  Systran/faster-whisper-large-v3
  large-v3-turbo            mobiuslabsgmbh/faster-whisper-large-v3-turbo
  ...
```

---

## Ví dụ đầy đủ

Các ví dụ dưới đây đều giả định:
- Tệp video gốc tiếng Trung là `60.mp4`
- Tệp phụ đề là `subs.srt`
- Ngôn ngữ đích là tiếng Việt
- Lồng tiếng bằng giọng `vi-VN-NamMinhNeural` của Edge-TTS
- Các tham số không bắt buộc khác giữ mặc định

### Tình huống 1: Chỉ bóc phụ đề

```bash
uv run cli.py --task stt --name "60.mp4" --detect_language zh-cn --cuda
```

**Giải thích**: chuyển tiếng nói trong `60.mp4` thành tệp phụ đề `zh-cn.srt`, xuất ra `output/60-mp4/`.

### Tình huống 2: Chỉ dịch phụ đề (tiếng Trung → tiếng Việt)

```bash
uv run cli.py --task sts --name "subs.srt" --source_language_code zh-cn --target_language_code vi
```

**Giải thích**: dịch `subs.srt` thành `vi.srt`, xuất ra `output/subs-srt/`.

### Tình huống 3: Chỉ lồng tiếng (tạo giọng tiếng Việt cho phụ đề)

```bash
uv run cli.py --task tts --name "subs.srt" --voice_role "vi-VN-NamMinhNeural" --target_language_code vi
```

**Giải thích**: tạo tệp WAV lồng tiếng Việt cho nội dung trong `subs.srt`, xuất ra `output/subs-srt/`.

### Tình huống 4: Dịch video trọn gói (tiếng Trung → tiếng Việt, có lồng tiếng)

```bash
uv run cli.py --task vtv --name "60.mp4" --source_language_code zh-cn --target_language_code vi --voice_role "vi-VN-NamMinhNeural" --cuda
```

**Giải thích**: xử lý trọn quy trình:
1. Nhận dạng tiếng Trung trong `60.mp4` → tạo phụ đề tiếng Trung
2. Dịch phụ đề tiếng Trung sang tiếng Việt
3. Dùng giọng Nam Minh của Edge-TTS tạo lồng tiếng Việt
4. Ghép phụ đề tiếng Việt và lồng tiếng vào video

Kết quả: `output/60-mp4/60.mp4` (video đã dịch)

### Tình huống 5: Dịch video chất lượng cao (tách giọng + GPU + nhận dạng lần 2)

```bash
uv run cli.py --task vtv --name "60.mp4" --source_language_code zh-cn --target_language_code vi --voice_role "vi-VN-NamMinhNeural" --cuda --is_separate --recogn2pass --model_name large-v3
```

**Giải thích**:
- `--is_separate`: tách giọng nói khỏi nhạc nền, tăng chất lượng nhận dạng và lồng tiếng
- `--recogn2pass`: nhận dạng lại sau khi lồng tiếng xong, cho dấu thời gian phụ đề chuẩn hơn
- `--model_name large-v3`: dùng mô hình nhận dạng chính xác nhất
- `--cuda`: tăng tốc GPU

### Tình huống 6: Video phụ đề song ngữ

```bash
uv run cli.py --task vtv --name "60.mp4" --source_language_code zh-cn --target_language_code vi --voice_role "vi-VN-NamMinhNeural" --subtitle_type 3 --cuda
```

**Giải thích**: `--subtitle_type 3` tạo phụ đề cứng song ngữ (hiện đồng thời cả hai ngôn ngữ).

### Tình huống 7: Dịch video tiếng Anh sang tiếng Việt

```bash
uv run cli.py --task vtv --name "60.mp4" --source_language_code en --target_language_code vi --voice_role "vi-VN-HoaiMyNeural" --cuda
```

### Tình huống 8: Xử lý hàng loạt nhiều tệp (vòng lặp shell)

```bash
# Bash / Git Bash
for f in *.mp4; do
  uv run cli.py --task vtv --name "$f" --source_language_code zh-cn --target_language_code vi --voice_role "vi-VN-NamMinhNeural" --cuda
done
```

```powershell
# PowerShell
Get-ChildItem *.mp4 | ForEach-Object {
  uv run cli.py --task vtv --name $_.FullName --source_language_code zh-cn --target_language_code vi --voice_role "vi-VN-NamMinhNeural" --cuda
}
```

---

## Câu hỏi thường gặp

### Hỏi: Xem danh sách kênh lồng tiếng và giọng đọc ở đâu?

```bash
uv run cli.py --list providers
```

Hoặc mở giao diện đồ họa, chọn kênh lồng tiếng rồi xem ô danh sách giọng đọc.

### Hỏi: Xem danh sách mã ngôn ngữ ở đâu?

```bash
uv run cli.py --list languages
```

### Hỏi: Đường dẫn có khoảng trắng thì làm sao?

Bọc đường dẫn trong dấu ngoặc kép:

```bash
uv run cli.py --task vtv --name "D:/video cua toi/60.mp4" --source_language_code zh-cn --target_language_code vi
```

### Hỏi: Bật tăng tốc GPU thế nào?

Thêm tham số `--cuda`:

```bash
uv run cli.py --task vtv --name "60.mp4" --source_language_code zh-cn --target_language_code vi --voice_role "vi-VN-NamMinhNeural" --cuda
```

> Điều kiện: đã cài driver card NVIDIA, CUDA 12.8+ và cuDNN 9.11+.

### Hỏi: Dùng mô hình ngôn ngữ lớn chạy trên máy để dịch thế nào?

Trước hết cần triển khai một mô hình tương thích giao diện OpenAI trên máy (ví dụ Ollama), sau đó:

```bash
uv run cli.py --task vtv --name "60.mp4" --source_language_code zh-cn --target_language_code vi --translate_type <chỉ mục kênh AI tương thích> --cuda
```

> Địa chỉ API của kênh dịch phải được cấu hình trước trong phần cài đặt dịch của giao diện đồ họa.

### Hỏi: Xử lý quá chậm thì làm sao?

1. **Bật tăng tốc GPU**: thêm `--cuda`
2. **Dùng mô hình nhỏ**: `--model_name tiny` (nhanh nhưng độ chính xác thấp)
3. **Bỏ qua tách giọng**: không thêm `--is_separate`
4. **Bỏ qua nhận dạng lần 2**: không thêm `--recogn2pass`

### Hỏi: Phụ đề và tiếng bị lệch nhau thì làm sao?

Thêm `--voice_autorate` (tự tăng tốc âm thanh) hoặc `--video_autorate` (tự làm chậm video):

```bash
uv run cli.py --task vtv --name "60.mp4" --source_language_code zh-cn --target_language_code vi --voice_role "vi-VN-NamMinhNeural" --voice_autorate --cuda
```

### Hỏi: Chỉ dịch mà không lồng tiếng thì làm sao?

Không truyền `--voice_role`, hoặc đặt là `No`:

```bash
uv run cli.py --task vtv --name "60.mp4" --source_language_code zh-cn --target_language_code vi
```

### Hỏi: Xem nhật ký xử lý chi tiết thế nào?

```bash
uv run cli.py --task vtv --name "60.mp4" --source_language_code zh-cn --target_language_code vi --voice_role "vi-VN-NamMinhNeural" -v
```

Hoặc chỉ định mức nhật ký:

```bash
uv run cli.py --task vtv --name "60.mp4" --source_language_code zh-cn --target_language_code vi --voice_role "vi-VN-NamMinhNeural" --log-level DEBUG
```

### Hỏi: Dùng phụ đề mềm (bật/tắt được trong trình phát) thế nào?

```bash
uv run cli.py --task vtv --name "60.mp4" --source_language_code zh-cn --target_language_code vi --subtitle_type 2 --cuda
```

> `--subtitle_type 2` = phụ đề mềm, `--subtitle_type 1` = phụ đề cứng (mặc định).

### Hỏi: Giữ lại bộ nhớ đệm để gỡ lỗi thế nào?

```bash
uv run cli.py --task vtv --name "60.mp4" --source_language_code zh-cn --target_language_code vi --voice_role "vi-VN-NamMinhNeural" --no-clear-cache
```

---

## Mã thoát

| Mã thoát | Ý nghĩa |
|--------|------|
| `0` | Tác vụ hoàn tất thành công |
| `1` | Có lỗi khi thực thi |
| `130` | Người dùng ngắt giữa chừng (Ctrl+C) |
| `2` | Sai tham số (argparse tự thoát) |

---

## Tài liệu liên quan

Các liên kết dưới đây trỏ tới tài liệu của dự án gốc pyVideoTrans:

- [Hướng dẫn nhập môn](https://pyvideotrans.com/getstart)
- [Tài liệu chế độ dòng lệnh](https://pyvideotrans.com/cli)
- [Giới thiệu các kênh nhận dạng giọng nói](https://pyvideotrans.com/yuyinshibiequdao)
- [Giới thiệu các kênh dịch](https://pyvideotrans.com/fanyiqudao)
- [Giới thiệu các kênh lồng tiếng](https://pyvideotrans.com/peiyinqudao)
- [Câu hỏi thường gặp](https://pyvideotrans.com/faq)
- [Kiến trúc kỹ thuật](https://pyvideotrans.com/yuanli)
