# Kiến trúc kỹ thuật và nguyên lý hoạt động của Phiên Dịch Video

`Phiên Dịch Video` là công cụ mã nguồn mở dịch và lồng tiếng video (v4.04), có thể tự động dịch video rồi lồng tiếng bằng ngôn ngữ đích. Tư tưởng thiết kế cốt lõi là mô-đun hóa và dây chuyền đa luồng, dùng các tổ hợp cờ linh hoạt để hỗ trợ nhiều chế độ làm việc khác nhau.

---

## 1. Luồng xử lý cốt lõi

Phần mềm chia quá trình dịch và lồng tiếng video thành **9 giai đoạn độc lập**, tạo thành một dây chuyền tự động. Mỗi tác vụ dùng 5 cờ boolean (`should_recogn`, `should_trans`, `should_dubbing`, `should_hebing`, `should_separate`) để quyết định bỏ qua giai đoạn nào, nhờ đó hỗ trợ được nhiều chế độ làm việc.

### 1.1 Chín giai đoạn xử lý

| Giai đoạn | Phương thức | Nhiệm vụ |
|------|------|------|
| **① Tiền xử lý** | `prepare()` | Tách luồng video câm và luồng âm thanh gốc khỏi video; tùy chọn tách giọng nói/nhạc nền (UVR/Spleeter); tùy chọn khử nhiễu; tạo thư mục đệm và thư mục đầu ra |
| **② Nhận dạng giọng nói** | `recogn()` | Gọi công cụ ASR (mặc định Faster-Whisper, hỗ trợ 26 kênh) để chuyển âm thanh thành phụ đề SRT có dấu thời gian; tùy chọn khôi phục dấu câu, tách câu bằng LLM |
| **③ Phân tách người nói** | `diariz()` | Gọi mô hình phân tách người nói (bốn nền: built, ali_CAM, pyannote, reverb) để gán nhãn người nói cho từng dòng phụ đề |
| **④ Dịch phụ đề** | `trans()` | Dịch phụ đề SRT ngôn ngữ gốc sang ngôn ngữ đích qua kênh dịch (24 kênh); hỗ trợ xuất phụ đề song ngữ |
| **⑤ Lồng tiếng** | `dubbing()` | Dựa vào nội dung và dấu thời gian phụ đề đích, gọi công cụ TTS (34 kênh) tạo từng đoạn lồng tiếng; hỗ trợ nhân bản giọng (cắt đoạn tham chiếu từ âm thanh gốc) |
| **⑥ Đồng bộ hình tiếng** | `align()` | Xử lý qua lớp `SpeedRate`: tăng tốc lồng tiếng, làm chậm video, xóa khoảng lặng giữa phụ đề, ép đồng bộ phụ đề với âm thanh; xong có thể chỉnh âm lượng |
| **⑦ Nhận dạng lần 2** | `recogn2pass()` | Chạy ASR lại trên chính tệp lồng tiếng để tạo phụ đề có dấu thời gian chuẩn và câu ngắn gọn (chỉ chạy khi có lồng tiếng và không nhúng phụ đề song ngữ) |
| **⑧ Dựng video cuối** | `assembling()` | Ghép luồng video câm, âm thanh lồng tiếng, nhạc nền và phụ đề ngôn ngữ đích thành tệp video cuối (ffmpeg) |
| **⑨ Kết thúc** | `task_done()` | Chuyển tệp kết quả từ thư mục tạm sang thư mục đầu ra đã chỉ định, dọn tệp tạm, gửi thông báo hoàn tất |

### 1.2 Các cờ điều khiển luồng

Định nghĩa tại `phiendichvideo/task/_base.py:20-29`, năm cờ này được tính tự động trong `TransCreate.__post_init__()` dựa trên cấu hình:

```python
should_recogn: bool    # có cần nhận dạng giọng nói không (True nếu chưa có phụ đề sẵn)
should_trans: bool     # có cần dịch không (True nếu ngôn ngữ nguồn ≠ ngôn ngữ đích)
should_dubbing: bool   # có cần lồng tiếng không (True nếu đã chọn giọng và khác 'No')
should_hebing: bool    # có cần nhúng và ghép không (True nếu không phải chế độ 'tiqu' và có lồng tiếng hoặc nhúng phụ đề)
should_separate: bool  # có cần tách giọng nói khỏi nhạc nền không
```

### 1.3 Ví dụ chuyển chế độ

Các chức năng khác nhau được tạo ra bằng tổ hợp cờ:

| Chức năng | should_recogn | should_trans | should_dubbing | should_hebing |
|------|:---:|:---:|:---:|:---:|
| Dịch và lồng tiếng video (chế độ chuẩn) | ✓ | ✓ | ✓ | ✓ |
| Chuyển video/audio thành phụ đề (tiqu) | ✓ | tùy chọn | ✗ | ✗ |
| Lồng tiếng cho phụ đề | ✗ | ✗ | ✓ | ✓ |
| Chỉ dịch tệp phụ đề | ✗ | ✓ | ✗ | ✗ |

### 1.4 Hệ thống lớp con của tác vụ

`BaseTask` có bốn lớp con cụ thể, mỗi lớp ứng với một tình huống sử dụng:

| Lớp con | Tệp | TaskCfg kế thừa | Tình huống dùng |
|------|------|----------------|---------|
| `TransCreate` | `task/trans_create.py` | `TaskCfgVTT` | Dịch và lồng tiếng video đầy đủ (chế độ chuẩn / chế độ trích tiqu) |
| `SpeechToText` | `task/speech2text.py` | `TaskCfgSTT` | Chuyển giọng nói thành phụ đề hàng loạt |
| `DubbingSrt` | `task/dubbing.py` | `TaskCfgTTS` | Lồng tiếng hàng loạt cho phụ đề |
| `TranslateSrt` | `task/translate_srt.py` | `TaskCfgSTS` | Dịch hàng loạt tệp phụ đề SRT |

---

## 2. Hệ thống lớp dữ liệu cấu hình tác vụ

Bản v4.03 đã tái cấu trúc cấu hình tác vụ thành hệ thống `@dataclass` kế thừa phân tầng (`phiendichvideo/task/taskcfg.py`, 261 dòng):

```
@dataclass TaskCfgBase              ← trường dùng chung (đường dẫn, mã ngôn ngữ, thư mục đệm...)
    ├── @dataclass TaskCfgSTT       ← trường liên quan nhận dạng (recogn_type, model_name, rephrase...)
    ├── @dataclass TaskCfgTTS       ← trường liên quan lồng tiếng (tts_type, voice_role, voice_autorate...)
    ├── @dataclass TaskCfgSTS       ← trường liên quan dịch (translate_type)
    └── @dataclass TaskCfgVTT       ← toàn bộ trường dịch video (kế thừa STT + TTS + STS, thêm trường riêng của video)
```

Các lớp dữ liệu hỗ trợ:

| Lớp dữ liệu | Tệp | Công dụng |
|--------|------|------|
| `InputFile` | `task/taskcfg.py` | Siêu dữ liệu tệp đầu vào (name, dirname, noextname, basename, ext, uuid, target_dir), truy cập được kiểu dict |
| `SignMsg` | `task/taskcfg.py` | Nội dung thông điệp tín hiệu (type, uuid, text), có `is_stop()` và `is_error()` để kiểm tra trạng thái, dùng để truyền giữa luồng Worker và luồng chính |
| `SrtItem` | `task/taskcfg.py` | Dữ liệu một dòng phụ đề (text, start_time, end_time, startraw, endraw, line, time, spk, filename) |

`SrtItem` cho phép truy cập vừa theo thuộc tính (`item.text`) vừa theo kiểu từ điển (`item['text']`), và duyệt được qua `items()`.

---

## 3. Kiến trúc xử lý tác vụ bất đồng bộ đa luồng

Phần mềm dùng kiến trúc đa luồng nhiều hàng đợi theo **mô hình "nhà sản xuất - người tiêu thụ"**. Luồng `MultVideo` đóng vai nhà sản xuất, đẩy đối tượng tác vụ vào hàng đợi đầu tiên của dây chuyền; 9 lớp con `BaseWorker` chuyên biệt đóng vai người tiêu thụ, mỗi lớp lắng nghe một hàng đợi riêng.

### 3.1 Dây chuyền hàng đợi

```
                     MultVideo (nhà sản xuất)
                           │
                    app_cfg.prepare_queue
                           ▼
                   WorkerPrepare (×N)
                    ┌────────┼────────┐
                    │ should_recogn ?  │
                    ▼        ▼        ▼
           regcon_queue  trans_queue  dubb_queue / assemb_queue / taskdone_queue
                │
                ▼
          WorkerRegcon (×N)
                │
         diariz_queue
                │
                ▼
          WorkerDiariz (×N)
           ┌────┼────┐
           ▼    ▼    ▼
      trans_queue  dubb_queue  assemb_queue / taskdone_queue
           │
           ▼
     WorkerTrans (×1)
      ┌────┼────┐
      ▼    ▼    ▼
 dubb_queue  assemb_queue  taskdone_queue
      │
      ▼
WorkerDubb (×1)
      │
 align_queue
      │
      ▼
WorkerAlign (×1)
 ┌────┼────┐
 ▼    ▼    ▼
regcon2_queue  assemb_queue  taskdone_queue
 │
 ▼
WorkerRegcon2Pass (×1)
 ┌────┼────┐
 ▼    ▼
assemb_queue  taskdone_queue
 │
 ▼
WorkerAssemb (×N)
 │
taskdone_queue
 │
 ▼
WorkerTaskDone (×1)
 │
(kết thúc)
```

### 3.2 Thiết kế lớp cơ sở Worker

Mọi luồng làm việc đều kế thừa `BaseWorker(QThread)` (`phiendichvideo/task/job.py:13-66`):

```python
class BaseWorker(QThread):
    def __init__(self, name, queue):
        self.name = name
        self.queue = queue

    def run(self):
        while True:
            if app_cfg.exit_soft:          # cờ thoát mềm toàn cục
                return
            try:
                trk = self.queue.get(timeout=1)  # chờ lấy tác vụ tối đa 1 giây
            except Empty:
                continue
            if trk.uuid in app_cfg.stoped_uuid_set:  # tác vụ đã bị dừng
                continue
            try:
                self.process_task(trk)       # lớp con cài đặt logic cụ thể
            except Exception as e:
                self.handle_error(e, trk)    # xử lý lỗi tập trung
```

Mỗi lớp con ghi đè các phương thức sau:

| Phương thức | Mô tả |
|------|------|
| `process_task(trk)` | **Bắt buộc** — thực hiện logic của giai đoạn và định tuyến trk sang hàng đợi kế tiếp |
| `get_error_prefix(trk)` | Tùy chọn — trả về chuỗi tiền tố lỗi (ví dụ `"Lỗi nhận dạng[Faster-Whisper]"`) |
| `cleanup_on_error(trk)` | Tùy chọn — logic dọn dẹp khi gặp lỗi |

`handle_error()` gọi thống nhất `get_msg_from_except()` để chuyển ngoại lệ thành thông báo dễ hiểu cho người dùng, rồi gửi thông điệp lỗi qua `trk.signal()`.

### 3.3 Logic định tuyến của Worker

Sau khi chạy xong `process_task(trk)`, mỗi Worker dựa vào các cờ của `trk` để quyết định hàng đợi kế tiếp:

```
WorkerPrepare    →  regcon_queue | trans_queue | dubb_queue | assemb_queue | taskdone_queue
WorkerRegcon     →  diariz_queue  (không điều kiện)
WorkerDiariz     →  trans_queue | dubb_queue | assemb_queue | taskdone_queue  (lỗi diariz không chặn luồng)
WorkerTrans      →  dubb_queue | assemb_queue | taskdone_queue
WorkerDubb       →  align_queue  (không điều kiện)
WorkerAlign      →  regcon2_queue | assemb_queue | taskdone_queue  (regcon2 chỉ khi có thuộc tính recogn2pass)
WorkerRegcon2Pass → assemb_queue | taskdone_queue
WorkerAssemb     →  taskdone_queue  (không điều kiện)
WorkerTaskDone   →  (kết thúc)
```

### 3.4 Tính số luồng động

`start_thread()` (`phiendichvideo/task/job.py:206-245`) quyết định số thực thể của từng Worker dựa trên cấu hình GPU:

| Worker | Số thực thể | Lý do |
|--------|--------|------|
| `WorkerPrepare` | 1 ~ 4 | Nặng về GPU (mã hóa/giải mã video) |
| `WorkerRegcon` | 1 ~ 4 | Nặng về GPU (suy luận ASR) |
| `WorkerDiariz` | 1 ~ 4 | Nặng về GPU (phân tách người nói) |
| `WorkerTrans` | **cố định 1** | Gọi API, tránh bị giới hạn tần suất |
| `WorkerDubb` | **cố định 1** | Gọi API TTS, tránh bị giới hạn tần suất |
| `WorkerRegcon2Pass` | **cố định 1** | Giai đoạn phụ trợ |
| `WorkerAlign` | **cố định 1** | Đồng bộ hình tiếng chạy đơn luồng |
| `WorkerAssemb` | 1 ~ 4 | Nặng về GPU (mã hóa ffmpeg) |
| `WorkerTaskDone` | **cố định 1** | Di chuyển và dọn tệp |

Cách tính `task_nums`: ưu tiên giá trị người dùng đặt tay trong `settings.process_max_gpu`; nếu không thì tự dò theo `multi_gpus` + `NVIDIA_GPU_NUMS` (1 GPU = 1, 2-3 GPU = 2, từ 4 GPU trở lên = 4, không có GPU = 1).

### 3.5 Gửi tác vụ hàng loạt: MultVideo

`MultVideo(QThread)` (`phiendichvideo/task/mult_video.py`, 54 dòng) chịu trách nhiệm tạo lần lượt đối tượng `TransCreate` cho từng tệp video người dùng chọn rồi đẩy vào `prepare_queue`. Số lượng chạy đồng thời mỗi đợt điều khiển bằng tham số `batch_nums`:

- `batch_nums == 0`: đẩy toàn bộ tác vụ vào hàng đợi một lần (đồng thời tối đa)
- `batch_nums == 1`: đẩy từng cái một, xong tác vụ này mới đẩy tác vụ kế
- `batch_nums > 1`: mỗi đợt đẩy N cái, chờ cả đợt xong mới đẩy đợt tiếp

### 3.6 Cơ chế thoát mềm

Khi cờ toàn cục `app_cfg.exit_soft` được đặt `True`, mọi Worker sẽ phát hiện ở vòng lặp kế tiếp và thoát an toàn. `app_cfg.stoped_uuid_set` đánh dấu UUID của những tác vụ bị dừng thủ công; Worker lấy tác vụ ra sẽ bỏ qua chúng.

---

## 4. Thiết kế và quan hệ kế thừa của các lớp cốt lõi

### 4.1 Hệ thống kế thừa

```
@dataclass BaseCon                    ← phiendichvideo/configure/base.py
    │                                  thuộc tính nền và phương thức tiện ích
    ├── @dataclass BaseTask           ← phiendichvideo/task/_base.py
    │       │                          định nghĩa 8 phương thức giai đoạn rỗng và 5 cờ
    │       ├── @dataclass TransCreate ← phiendichvideo/task/trans_create.py (~1678 dòng, phần lõi)
    │       ├── @dataclass SpeechToText ← phiendichvideo/task/speech2text.py (nhận dạng hàng loạt)
    │       ├── @dataclass DubbingSrt  ← phiendichvideo/task/dubbing.py (lồng tiếng phụ đề hàng loạt)
    │       └── @dataclass TranslateSrt ← phiendichvideo/task/translate_srt.py (dịch phụ đề hàng loạt)
    │
    ├── @dataclass BaseRecogn         ← phiendichvideo/recognition/_base.py
    │       │                          cắt âm thanh bằng VAD, gộp phụ đề, xử lý CJK
    │       └── 26 lớp con (nạp lười)  cài đặt cụ thể của từng kênh ASR
    │
    ├── @dataclass BaseTrans          ← phiendichvideo/translator/_base.py
    │       │                          đệm MD5, điều phối dịch theo dòng/toàn văn
    │       └── 24 lớp con (nạp lười)  cài đặt cụ thể của từng kênh dịch
    │
    └── @dataclass BaseTTS            ← phiendichvideo/tts/_base.py
            │                          điều phối bất đồng bộ/đa luồng
            └── 34 lớp con (nạp lười)  cài đặt cụ thể của từng kênh TTS
```

Mọi lớp kênh đều là `@dataclass`, khởi tạo bằng `__post_init__` thay vì hàm dựng `__init__` truyền thống.

### 4.2 BaseCon — lớp cơ sở cao nhất

`phiendichvideo/configure/base.py` (296 dòng) định nghĩa các năng lực cốt lõi mà mọi lớp đều dùng chung:

| Phương thức | Nhiệm vụ |
|------|------|
| `_exit()` | Kiểm tra có nên dừng không (`exit_soft` hoặc UUID nằm trong `stoped_uuid_set`) |
| `signal(**kwargs)` | Gửi thông điệp lên giao diện (qua `push_queue()` → `SignalHub`; ở chế độ CLI thì in thẳng) |
| `_set_proxy(type)` | Đặt/xóa proxy HTTP (thao tác trên `app_cfg.proxy` và biến môi trường) |
| `_new_process(callback, title, is_cuda, kwargs)` | **Chạy tác vụ nặng trong tiến trình con** (trả về bộ `(data, error)`) |
| `_signal_of_process(logs_file)` | Đọc tiến độ tiến trình con theo thời gian thực bằng cách theo dõi mtime của tệp nhật ký JSON |
| `convert_to_wav()` | Chuyển âm thanh về WAV 48kHz stereo (tùy chọn bỏ khoảng lặng) |
| `_base64_to_audio()` / `_audio_to_base64()` | Mã hóa/giải mã âm thanh Base64 |
| `_process_callback(data)` | Hàm gọi lại báo tiến độ tải (chuyển tiếp tới `signal()`) |

`BaseCon.__post_init__()` tự gọi `_set_proxy(type='set')` khi khởi tạo để lấy cấu hình proxy.

### 4.3 BaseTask — lớp cơ sở của tác vụ

`phiendichvideo/task/_base.py:10-167` định nghĩa các phương thức giai đoạn rỗng và công cụ dùng chung cho mọi lớp con:

**Phương thức giai đoạn** (đều rỗng, lớp con ghi đè):
`prepare()`, `recogn()`, `diariz()`, `trans()`, `dubbing()`, `align()`, `assembling()`, `task_done()`

> Lưu ý: `recogn2pass()` được định nghĩa trong `TransCreate`, không nằm ở lớp cơ sở `BaseTask`.

**Phương thức dùng chung**:
| Phương thức | Nhiệm vụ |
|------|------|
| `_unlink_size0(file)` | Xóa tệp rỗng (kích thước 0) không hợp lệ |
| `_save_srt_target(srtstr, file)` | Định dạng danh sách SrtItem thành chuỗi SRT rồi ghi ra tệp, gửi tín hiệu `replace_subtitle` |
| `check_target_sub(source, target)` | Kiểm tra số dòng phụ đề trước và sau khi dịch có khớp không; không khớp thì căn theo trục thời gian |
| `set_end(succeed=False)` | Đánh dấu tác vụ kết thúc, nếu thành công thì gửi thông báo và dọn thư mục tạm |
| `_edgetts_single(target_audio, kwargs)` | Lồng tiếng bất đồng bộ một lần bằng Edge-TTS (có dự phòng khi proxy lỗi) |

### 4.4 TransCreate — phần lõi dịch video

`phiendichvideo/task/trans_create.py` (khoảng 1678 dòng) là lớp cài đặt đầy đủ logic 9 giai đoạn. Các phương thức nội bộ quan trọng:

| Phương thức | Nhiệm vụ |
|------|------|
| `__post_init__()` | Khởi tạo mọi đường dẫn tệp, tính các cờ, khởi động luồng đếm tiến độ |
| `_split_novoice_byraw()` | Tách video câm khỏi video gốc (ưu tiên giải mã phần cứng h264_cuvid, dự phòng libx264) |
| `_split_audio_byraw()` | Trích âm thanh PCM 16kHz đơn kênh từ video gốc + tùy chọn tách giọng nói/nhạc nền |
| `_tts()` | Dựng danh sách `queue_tts` (gồm cả đoạn âm thanh tham chiếu để nhân bản giọng), gọi `tts.run()` |
| `_create_ref_from_vocal()` | Cắt các đoạn âm thanh gốc tương ứng làm mẫu nhân bản giọng, chạy đa luồng (ThreadPoolExecutor) |
| `_recogn_succeed()` | Xử lý sau khi nhận dạng xong (chế độ tiqu thì sao chép tệp) |
| `_back_music()` | Trộn nhạc nền người dùng tải lên với âm thanh lồng tiếng |
| `_separate()` | Nhúng lại nhạc nền đã tách vào âm thanh lồng tiếng |
| `_process_subtitles()` | Xử lý logic nhúng phụ đề mềm/cứng (đơn ngữ/song ngữ, thiết lập kiểu dáng) |

### 4.5 Các kênh chạy trong tiến trình con

Để tránh việc `faster-whisper` sập kéo theo cả phần mềm thoát, các kênh `Faster-Whisper`, `Faster-Whisper-XXL` và `Whisper.cpp` (cùng một vài công cụ TTS như `QWEN3LOCAL_TTS`) được ủy thác cho `GlobalProcessManager` chạy trong tiến trình con riêng, thông qua `BaseCon._new_process()`.

Tiến trình con báo tiến độ bằng cách ghi vào tệp nhật ký JSON. `BaseCon._signal_of_process()` chạy trong luồng nền, theo dõi tệp nhật ký đó, phát hiện mtime thay đổi thì đọc JSON và báo lên qua `signal()`.

---

## 5. Hệ thống cấu hình

Phần mềm chia cấu hình thành ba tầng (`phiendichvideo/configure/config.py`, 902 dòng), tất cả đều là `@dataclass`:

| Lớp cấu hình | Lưu trữ | Công dụng | Trường ví dụ |
|--------|--------|------|---------|
| `AppCfg` | Chỉ trong bộ nhớ | Hàng đợi, trạng thái, điều khiển luồng, ngữ cảnh lúc chạy | `prepare_queue`, `exit_soft`, `stoped_uuid_set`, `current_status`, `line_roles`, `exec_mode`, `video_codec`, `onlyone_source_sub`, `onlyone_target_sub`, `proxy`, `SUPPORT_LANG` |
| `AppSettings` | `phiendichvideo/cfg.json` | Thiết lập mặc định toàn cục, danh sách mô hình | `homedir`, `model_list`, `vad_type`, `cuda_com_type` |
| `AppParams` | `phiendichvideo/params.json` | Tùy chọn người dùng, khóa API | `source_language`, `recogn_type`, `chatgpt_key`, `voice_role`, `app_mode` |

Các biến singleton quan trọng được khởi tạo tự động khi nạp mô-đun:

```python
app_cfg: AppCfg = AppCfg()        # trạng thái lúc chạy (chứa 9 thực thể Queue)
settings: AppSettings = AppSettings()  # nạp từ cfg.json
params: AppParams = AppParams()    # nạp từ params.json
```

### 5.1 Đặc điểm của AppSettings

- Hỗ trợ truy cập kiểu từ điển `settings['key']` và phương thức `settings.get('key', default)`
- `get()` tự ép kiểu cho các trường số (theo danh sách trắng `int_type` và `float_type`)
- `_get_defaults()` định nghĩa giá trị mặc định cho khoảng 100 mục cấu hình
- Hỗ trợ ánh xạ tên trường có dấu gạch nối (ví dụ `"initial_prompt_zh-cn"` → `"initial_prompt_zh_cn"`)

### 5.2 Đặc điểm của AppParams

- `_get_defaults()` định nghĩa khoảng 100 tham số người dùng mặc định
- `getset_params(update_data)` hỗ trợ cập nhật hàng loạt (như khi `check_start()` thu thập giá trị mọi widget)
- Các trường khóa API được quản lý tập trung tại đây, phục vụ kiểm tra của `is_input_api()`

### 5.3 Trạng thái lúc chạy trong AppCfg

- 9 hàng đợi `Queue(maxsize=0)` (không giới hạn dung lượng): từ `prepare_queue` đến `taskdone_queue`
- `queue_novice: Dict` — theo dõi tiến độ tách video câm (khóa=uuid, giá trị='ing'|'end')
- `line_roles: Dict` — lưu giọng đọc người dùng gán cho từng dòng ở chế độ một video
- `child_forms: Dict` — đệm các cửa sổ đã mở, tránh tạo lại
- `exec_mode` — chế độ chạy ('gui' hoặc 'cli')
- `video_codec` / `codec_cache` — đệm bộ mã hóa/giải mã video
- `onlyone_source_sub` / `onlyone_target_sub` / `onlyone_trans` — trạng thái phụ đề ở chế độ một video
- `SUPPORT_LANG` — danh sách ngôn ngữ hỗ trợ

### 5.4 Khởi tạo biến môi trường

`_set_env()` chạy tự động khi nạp mô-đun (`phiendichvideo/configure/config.py:44-72`), thiết lập:
- `MODELSCOPE_CACHE` / `HF_HOME` / `HF_HUB_CACHE` → `ROOT_DIR/models`
- `QT_API = 'pyside6'`
- Thêm thư mục ffmpeg/sox vào `PATH`
- `OMP_NUM_THREADS = 1`
- `HF_HUB_DOWNLOAD_TIMEOUT = 3600`
- `HF_HUB_DISABLE_XET = 1`

---

## 6. GlobalProcessManager — quản lý nhóm tiến trình con

`phiendichvideo/process/signelobj.py` (167 dòng) cài đặt `GlobalProcessManager` dạng singleton ở cấp lớp:

```
GlobalProcessManager (singleton cấp lớp)
    ├── _executor_cpu: multiprocessing.Pool
    │       workers = max(min(RAM_khả_dụng/4GB, 8, cpu_count), 1)  ← tính theo bộ nhớ còn trống
    │       maxtasksperchild = 1  ← mỗi tiến trình con chạy một tác vụ rồi khởi động lại, chống rò rỉ bộ nhớ
    │
    └── _executor_gpu: multiprocessing.Pool
            workers = số GPU (ưu tiên giá trị đặt tay settings.process_max_gpu)
            maxtasksperchild = 1
```

### 6.1 Quy mô nhóm tiến trình CPU

Không dùng công thức cố định nữa, mà lấy bộ nhớ còn trống của hệ thống qua `psutil.virtual_memory().available`, tính mỗi 4GB một tiến trình, giới hạn trong khoảng **1~8** và không vượt quá `os.cpu_count()`. Có thể ghi đè thủ công bằng `settings.process_max`.

### 6.2 Quy mô nhóm tiến trình GPU

Ưu tiên giá trị đặt tay `settings.process_max_gpu`; nếu không thì xác định theo `multi_gpus` và `NVIDIA_GPU_NUMS` (không có card = 1, có card nhưng chưa bật nhiều card = 1, bật nhiều card = min(số GPU, 8, cpu_count)).

### 6.3 Giao diện gửi tác vụ

```python
GlobalProcessManager.submit_task_cpu(func, **kwargs)   → AsyncResultFutureWrapper
GlobalProcessManager.submit_task_gpu(func, **kwargs)   → AsyncResultFutureWrapper
```

`AsyncResultFutureWrapper` bọc `AsyncResult` của `Pool.apply_async` thành giao diện tương thích `Future` (`.result()`, `.done()`).

### 6.4 Tình huống sử dụng

Được gọi thống nhất qua `BaseCon._new_process()`, dùng để chạy: suy luận ASR, tổng hợp TTS, khử nhiễu, tách giọng nói, phân tách người nói, khôi phục dấu câu — tất cả đều chạy trong tiến trình con riêng, sập cũng không ảnh hưởng tiến trình chính.

---

## 7. SignalHub — trung tâm thông điệp giữa các luồng

`phiendichvideo/configure/signal_hub.py` (33 dòng) cài đặt cơ chế truyền thông điệp singleton dựa trên tín hiệu của Qt:

```python
class SignalHub(QObject):
    _instance = None
    new_message = Signal(str, object)  # (uuid, SignMsg)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @Slot(str, object)
    def post(self, uuid=None, data=None):
        self.new_message.emit(uuid, data)  # tự dùng QueuedConnection khi qua luồng khác
```

### Luồng thông điệp

```
BaseCon.signal(**kwargs)
    → push_queue(uuid, SignMsg(**kwargs))     [configure/config.py]
        → SignalHub.instance().post(uuid, data)
            → tín hiệu new_message (QueuedConnection)
                → WinAction.update_data(uuid, data)   [mainwin/_actions.py]
                    → phân nhánh theo type:
                        'logs'|'error'|'succeed'|'set_precent' → set_process_btn_text()
                        'edit_subtitle_source' → mở EditRecognResultDialog
                        'edit_subtitle_target' → mở SpeakerAssignmentDialog
                        'edit_dubbing' → mở EditDubbingResultDialog
                        'replace_subtitle' → cập nhật vùng soạn phụ đề
                        'end' → update_status('end')
```

### Các loại thông điệp

| type | Ý nghĩa | Xử lý |
|------|------|---------|
| `logs` | Nhật ký thường | Cập nhật chữ trên thanh tiến độ |
| `error` | Lỗi | Thanh tiến độ chuyển đỏ, đưa vào hàng đợi thử lại |
| `succeed` | Thành công | Thanh tiến độ chuyển xanh, đánh dấu hoàn tất |
| `set_precent` | Phần trăm tiến độ | Định dạng `text="thời gian???phần trăm"` |
| `edit_subtitle_source` | Mở hộp thoại sửa phụ đề gốc | Điểm dừng ① của chế độ một video |
| `edit_subtitle_target` | Mở hộp thoại sửa phụ đề đã dịch | Điểm dừng ② của chế độ một video |
| `edit_dubbing` | Mở hộp thoại sửa kết quả lồng tiếng | Điểm dừng ③ của chế độ một video |
| `replace_subtitle` | Thay nội dung vùng phụ đề | Dùng chung cho cả hàng loạt và một video |
| `subtitle` | Thêm dòng phụ đề | Xuất từng dòng ra trình soạn |
| `end` | Tác vụ hoàn tất | Kích hoạt update_status('end') |
| `disabled_edit` | Cấm sửa phụ đề | Khóa trình soạn ở chế độ hàng loạt |
| `refreshtts` | Làm mới lựa chọn TTS | Đặt lại ô chọn TTS |
| `shitingerror` | Lỗi nghe thử | Hiện thông báo lỗi |
| `ffmpeg` | Trạng thái ffmpeg | Cập nhật chữ trên nút bắt đầu |

---

## 8. Nạp kênh động

`phiendichvideo/__init__.py` (35 dòng) cung cấp cơ chế nạp lười dùng chung:

```python
@dataclass
class ChannelProvider:
    name: str           # tên hiển thị trên giao diện
    imp: str            # hậu tố tên mô-đun (ví dụ "._whisper" → "phiendichvideo.recognition._whisper")
    key_name: str|None  # tên trường khóa API tương ứng trong params.json (để is_input_api kiểm tra)
    win: str|None       # tên cửa sổ cài đặt tương ứng trong winform

def get_class(channel_id=0, provider_type=None, _ID_NAME_DICT=None):
    _key = f'{provider_type}-{channel_id}'
    if _key in _loaded_modules:
        return _loaded_modules[_key]
    module = importlib.import_module(f'phiendichvideo.{provider_type}{_module_map.imp}')
    for _, obj in inspect.getmembers(module, inspect.isclass):
        if obj.__module__ == module.__name__:
            _loaded_modules[_key] = obj
            return obj
```

`_ID_NAME_DICT` của ba mô-đun chính:

| Mô-đun | Số kênh | Nơi định nghĩa |
|------|--------|---------|
| Nhận dạng (recognition) | 26 | `phiendichvideo/recognition/__init__.py` |
| Dịch (translator) | 24 | `phiendichvideo/translator/__init__.py` |
| Lồng tiếng (tts) | **34** | `phiendichvideo/tts/__init__.py` |

### 8.1 Hàm vào thống nhất

Mỗi mô-đun đều có hàm `run()` làm điểm vào chung, bên trong gọi `get_class()` để lấy lớp kênh tương ứng rồi khởi tạo và chạy:

```python
# recognition/__init__.py
def run(*, recogn_type, detect_language, audio_file, ...) -> List[SrtItem]:
    _cls = get_class(recogn_type, "recognition", _ID_NAME_DICT)
    return _cls(**kwargs).run()

# translator/__init__.py
def run(*, translate_type, text_list, source_code, target_code, ...) -> List[SrtItem]:
    _cls = get_class(translate_type, "translator", _ID_NAME_DICT)
    return _cls(**kwargs).run()

# tts/__init__.py
def run(*, queue_tts, language, tts_type, ...) -> None:
    _cls = get_class(tts_type, "tts", _ID_NAME_DICT)
    return _cls(**kwargs).run()
```

### 8.2 Kiểm tra khóa API

Mỗi mô-đun có hàm `is_input_api(recogn_type/translate_type/tts_type)` để kiểm tra trường `key_name` của kênh tương ứng đã được điền trong `params` chưa. Chưa điền thì tự mở cửa sổ cài đặt winform tương ứng.

### 8.3 Đệm bản dịch

`BaseTrans` (`phiendichvideo/translator/_base.py`) cài đặt cơ chế đệm bản dịch dựa trên MD5:
- Khóa đệm = `md5(tên_kênh + api_url + model + ngôn_ngữ_nguồn + ngôn_ngữ_đích + văn_bản)`
- Tệp đệm lưu tại `{TEMP_ROOT}/translate_cache/`
- Ghi qua `_set_cache()`, đọc qua `_get_cache()`

### 8.4 Xử lý riêng cho CJK

`BaseRecogn` (`phiendichvideo/recognition/_base.py:58-80`) xử lý riêng cho các ngôn ngữ Trung, Nhật, Hàn... trong `__post_init__`:
- `join_word_flag`: với ngôn ngữ CJK (zh, ja, ko, yu, th, km, yue) thì không chèn khoảng trắng giữa các từ trong phụ đề (ngôn ngữ khác thì có)
- `maxlen`: ngôn ngữ CJK dùng `settings.cjk_len` ký tự mỗi dòng (mặc định 15), ngôn ngữ khác dùng `settings.other_len` (mặc định 40)
- `jianfan`: bật chuyển phồn thể sang giản thể khi là tiếng Trung và `settings.zh_hant_s=True`

### 8.5 Chiến lược điều phối dịch

`BaseTrans.run()` chọn chiến lược theo cờ `aisendsrt`:

| Chế độ | Điều kiện | Phương thức | Số luồng đồng thời |
|------|------|------|--------|
| Dịch theo dòng | Kênh không phải AI | `_run_text()` → `_item_task()` | `settings.trans_thread` (mặc định 10) |
| Dịch toàn văn | Kênh AI + `aisendsrt=True` | `_run_srt()` | `settings.aitrans_thread` (mặc định 50) |

### 8.6 Chiến lược điều phối TTS

`BaseTTS.run()` chọn cách chạy theo loại kênh:

| Loại kênh | Cách điều phối | Ghi chú |
|---------|---------|------|
| Edge-TTS | Bất đồng bộ `asyncio` | Chạy async đồng thời trong một luồng |
| Kênh khác | `ThreadPoolExecutor` | Số luồng đồng thời do `dubbing_thread` quyết định (mặc định 1) |

Lớp con của kênh có thể ghi đè `_exec()` để tự điều phối. Mặc định `BaseTTS` gọi `__local_mul_thread()` → `_item_task()`.

---

## 9. Chế độ xử lý một video có tương tác

Khi người dùng chọn **1 video** và đang ở **chế độ chuẩn (biaozhun)**, chương trình dùng mô hình xử lý khác với dây chuyền hàng loạt.

### 9.1 Cài đặt: Worker(QThread)

Lớp `Worker` trong `phiendichvideo/task/only_one.py` (148 dòng) chạy **tuần tự cả 9 giai đoạn trong một QThread duy nhất**, giao tiếp với luồng chính qua `uito = Signal(str, SignMsg)`:

```
Worker.run()
    ├── trk = TransCreate(cfg=TaskCfgVTT(**self.cfg | obj))
    ├── trk.prepare()
    ├── trk.recogn()
    ├── trk.diariz()
    ├── [Điểm dừng ①] → _post(type='edit_subtitle_source')
    │    người dùng soát phụ đề gốc → bấm "Đồng ý" hoặc đợi hết đếm ngược
    ├── trk.trans() (nếu should_trans)
    ├── [Điểm dừng ②] → _post(type='edit_subtitle_target')
    │    người dùng soát phụ đề đã dịch + gán giọng cho người nói → bấm "Đồng ý"
    ├── trk.dubbing() (nếu should_dubbing)
    ├── [Điểm dừng ③] → _post(type='edit_dubbing')
    │    người dùng sửa kết quả lồng tiếng → bấm "Đồng ý"
    ├── trk.align()
    ├── trk.recogn2pass()
    ├── trk.assembling()
    └── trk.task_done()
```

### 9.2 Khác biệt chính so với chế độ hàng loạt

| Khía cạnh | Chế độ một video | Chế độ hàng loạt |
|------|-----------|---------|
| Luồng thực thi | `Worker(QThread)` chạy trực tiếp, không dùng đường ống hàng đợi | `TransCreate` đẩy vào `prepare_queue`, chảy qua 9 hàng đợi Worker |
| Kênh thông điệp | Tín hiệu `uito` nối thẳng tới `WinAction.update_data()` | `BaseCon.signal()` → `push_queue()` → `SignalHub` |
| Cơ chế tạm dừng | Ba điểm dừng, người dùng sửa được ở giữa chừng | Không hỗ trợ dừng để sửa |
| Hiển thị tiến độ | Hiện trực tiếp trong vùng soạn phụ đề | Thanh tiến độ + chữ trên nút |

### 9.3 Cơ chế đếm ngược và tạm dừng

1. **Đếm ngược tự động**: `app_cfg.set_countdown(86400)` đặt giá trị ban đầu. Luồng Worker giảm dần mỗi `sleep(1)`. Giá trị đếm ngược mặc định do `settings.countdown_sec` quyết định.
2. **Dừng vô thời hạn**: người dùng bấm nút "Dừng" sẽ đặt `app_cfg.current_status` thành `'stop'`, `_exit()` của Worker phát hiện và thoát; hoặc `set_countdown(-1)` để bỏ đếm ngược.
3. **Tiếp tục thủ công**: khi người dùng bấm "Đồng ý" trong hộp thoại soát lỗi, `WinAction.set_djs_timeout()` gọi `app_cfg.set_countdown(-1)` cho đếm ngược về 0 ngay lập tức.

### 9.4 Các hộp thoại soát lỗi

| Hộp thoại | Tệp | Chức năng |
|--------|------|------|
| `EditRecognResultDialog` | `component/onlyone_set_recogn.py` | Sửa phụ đề gốc (nội dung + trục thời gian) |
| `SpeakerAssignmentDialog` | `component/onlyone_set_role.py` | Sửa phụ đề đã dịch + gán giọng lồng tiếng cho từng dòng |
| `EditDubbingResultDialog` | `component/onlyone_set_editdubb.py` | Nghe thử kết quả lồng tiếng + lồng tiếng lại từng dòng |

---

## 10. Bộ máy đồng bộ hình tiếng (SpeedRate)

`phiendichvideo/task/_rate.py` (877 dòng) cài đặt hai bộ máy đồng bộ là `SpeedRate` và `TtsSpeedRate`:

### 10.1 SpeedRate (dùng khi dịch video)

Chiến lược xử lý (theo thứ tự ưu tiên):

| Điều kiện | Chiến lược |
|------|------|
| Bật cả tăng tốc âm thanh và làm chậm video | Mỗi bên gánh một nửa chênh lệch (bỏ qua giới hạn tỉ lệ) |
| Chỉ bật tăng tốc âm thanh | Tăng tốc lồng tiếng cho khớp thời lượng phụ đề (không vượt `max_audio_speed_rate`) |
| Chỉ bật làm chậm video | Làm chậm đoạn video cho khớp thời lượng lồng tiếng (không vượt `max_video_pts_rate`) |
| Không bật cả hai | Ghép các đoạn âm thanh theo trục thời gian phụ đề, bù khoảng lặng cho phần chênh lệch |

Xử lý thêm:
- `remove_silent_mid`: xóa khoảng lặng giữa các dòng phụ đề
- `align_sub_audio`: ép trục thời gian phụ đề khớp vị trí lồng tiếng thực tế
- Xóa khoảng lặng ở cuối

> Nguyên lý chi tiết xem [Nguyên lý đồng bộ dấu thời gian hình và tiếng](Synchronize.md)

### 10.2 TtsSpeedRate (chỉ lồng tiếng)

Bản rút gọn, chỉ lo ghép và tăng tốc âm thanh, không có logic làm chậm video.

---

## 11. Khởi động phần mềm và cài đặt giao diện

### 11.1 Luồng khởi động

`sp.py` là điểm vào duy nhất (221 dòng), quá trình khởi động như sau:

```
sp.py (if __name__ == "__main__")
  │
  ├── 1. multiprocessing.freeze_support() / set_start_method('spawn')
  ├── 2. qInstallMessageHandler() chặn cảnh báo của Qt
  ├── 3. atexit.register(cleanup) đăng ký dọn dẹp khi thoát
  ├── 4. QApplication.setHighDpiScaleFactorRoundingPolicy(PassThrough)
  ├── 5. Tạo QApplication
  ├── 6. Kiểm tra có đang chạy từ trong tệp nén không (bản đóng gói PyInstaller)
  ├── 7. Tạo StartWindow (màn hình khởi động, không viền, nền trong suốt)
  │       └── QTimer.singleShot(100ms) → initialize_full_app()
  │           ├── Chuyển hướng sys.stdout/stderr sang tệp nhật ký
  │           ├── Đặt bẫy ngoại lệ toàn cục show_global_error_dialog
  │           ├── Đọc tham số dòng lệnh --lang
  │           ├── Nạp darkstyle_rc (tài nguyên QRC đã biên dịch)
  │           ├── Nạp bảng kiểu QSS (phiendichvideo/styles/style.qss)
  │           ├── Khôi phục kích thước cửa sổ lần trước (QSettings)
  │           └── Khởi tạo MainWindow → nối uito với splash.update_lable
  │               └── MainWindow.__init__()
  │                   ├── setupUi() → đổ dữ liệu vào các ô chọn (kênh dịch/nhận dạng/TTS, danh sách ngôn ngữ)
  │                   ├── Khởi động AiLoaderThread → dò GPU → gọi lại _start_workers()
  │                   ├── _start_workers() → start_thread() khởi động 9 loại luồng Worker
  │                   ├── _set_default() → khôi phục lựa chọn lần trước của người dùng
  │                   ├── _bind_signal() → nối khoảng 60 sự kiện của các widget
  │                   ├── SignalHub.new_message.connect(win_action.update_data)
  │                   └── uito.emit('end') → đóng màn hình khởi động
  └── 8. app.exec() → vòng lặp sự kiện Qt
```

### 11.2 Cơ chế thoát

Khi người dùng bấm nút đóng:
1. Đặt `app_cfg.exit_soft = True`, `app_cfg.current_status = 'stop'`
2. Ẩn cửa sổ chính ngay (`hide()`)
3. Lưu kích thước cửa sổ vào `QSettings`
4. Ẩn/đóng mọi cửa sổ con
5. Đợi khoảng 4 giây để các Worker hoàn tất việc đang làm và thoát an toàn
6. Dọn thư mục tạm `TEMP_ROOT`
7. Hàm dọn dẹp `atexit` chạy → chương trình kết thúc
8. Nếu là chế độ khởi động lại thì mở tiến trình mới rồi `os._exit(0)`

### 11.3 Phân tầng kiến trúc giao diện

```
Tầng định nghĩa UI    phiendichvideo/ui/         ← tệp bố cục giao diện PySide6 (~75 tệp), tài nguyên dark/
    ↓
Tầng logic UI         phiendichvideo/component/  ← thành phần dùng chung: thanh tiến độ, biểu mẫu cài đặt, trình soạn phụ đề, nhận dạng thời gian thực, cắt video, so khớp văn bản
    ↓
Tầng quản lý cửa sổ   phiendichvideo/winform/    ← khoảng 65 mô-đun cửa sổ cài đặt/chức năng, nạp lười
    ↓
Tầng cửa sổ chính     phiendichvideo/mainwin/
    ├── main_win.py                      ← MainWindow(QMainWindow): khởi tạo UI, nối tín hiệu, khởi động Worker, vòng đời cửa sổ (528 dòng)
    ├── _actions.py                       ← WinAction: logic nghiệp vụ cốt lõi → thu thập tham số → khởi động tác vụ → phân phối trạng thái (798 dòng)
    └── _actions_base.py                 ← WinActionBase: quản lý proxy, chuyển chế độ, chọn tệp, dò CUDA, nghe thử (590 dòng)
    ↓
Tầng tác vụ           phiendichvideo/task/       ← TransCreate, SpeechToText, DubbingSrt, TranslateSrt, luồng Worker, SpeedRate
```

### 11.4 MainWindow — cửa sổ chính

Nhiệm vụ của `phiendichvideo/mainwin/main_win.py` (528 dòng):
- `setupUi()`: nạp bố cục giao diện, đổ dữ liệu vào các ô chọn (kênh dịch, kênh nhận dạng, kênh TTS, ngôn ngữ, kiểu phụ đề)
- `_bind_signal()`: nối khoảng 60 sự kiện widget tới các phương thức của `WinAction`
- `_start_workers(status)`: sau khi dò GPU xong thì khởi động 9 loại luồng Worker chạy nền
- `open_winform(name)`: điểm vào thống nhất để mở cửa sổ (ưu tiên dùng lại cửa sổ đã đệm trong `app_cfg.child_forms`, nếu chưa có thì gọi `winform.get_win(name).openwin()`)
- `closeEvent()`: quy trình đóng an toàn (đánh dấu thoát → ẩn cửa sổ → dừng luồng → dọn tệp tạm)
- `restart_app()`: hỏi xác nhận rồi kích hoạt `closeEvent()` và mở tiến trình mới

### 11.5 WinAction — bộ điều khiển cốt lõi

`WinAction` kế thừa từ `WinActionBase` (cả hai đều là `@dataclass`), là đầu mối then chốt nối giao diện với tác vụ chạy nền:

**WinActionBase** (`mainwin/_actions_base.py`, 590 dòng) cung cấp:
- Chọn tệp (`get_mp4()`) — chế độ một tệp/thư mục
- Đặt thư mục đầu ra (`get_save_dir()`)
- Cấu hình proxy (`change_proxy()`, `check_proxy()`, `proxy_alert()`)
- Chuyển chế độ (`set_biaozhun()`, `set_tiquzimu()`) — điều khiển ẩn/hiện các thành phần giao diện
- Dò CUDA (`check_cuda()`, `cuda_isok()`)
- Nghe thử (`listen_voice_fun()`) — tạo luồng `ListenVoice`
- Cập nhật danh sách giọng (`tts_type_change()`, `set_voice_role()`)
- Thu gọn tùy chọn nâng cao (`toggle_adv()`)
- Bật/tắt các thành phần giao diện (`disabled_widget()`, `_disabled_button()`)

**WinAction** (`mainwin/_actions.py`, 798 dòng) cung cấp:
- `check_start()`: thu thập giá trị mọi widget → dựng từ điển `cfg` → kiểm tra tham số → gọi `create_btns()`
- `create_btns()`: chuẩn hóa đường dẫn tệp đầu vào → tạo thanh tiến độ → một video thì khởi động `Worker`, hàng loạt thì khởi động `MultVideo`
- `update_data(uuid, SignMsg)`: nối với tín hiệu `SignalHub.new_message` → phân nhánh theo loại thông điệp
- `update_status(type)`: chuyển trạng thái `ing`/`stop`/`end`, điều khiển nút và thanh tiến độ
- `set_process_btn_text(d)`: cập nhật chữ/phần trăm/màu của thanh tiến độ
- `retry()`: xử lý lại các tác vụ thất bại
- `_check_all_done()`: kiểm tra đã xong hết tác vụ chưa

---

## 12. Hệ thống ngoại lệ

`phiendichvideo/configure/excepts.py` (376 dòng) định nghĩa hệ thống ngoại lệ phân tầng:

```
VideoTransError (lớp cơ sở)
    ├── TranslateSrtError       # lỗi liên quan dịch thuật
    ├── DubbingSrtError         # lỗi liên quan lồng tiếng
    ├── SpeechToTextError       # lỗi liên quan nhận dạng giọng nói
    ├── LLMSegmentError         # lỗi tách câu bằng LLM
    ├── FFmpegError             # lỗi thao tác FFmpeg
    ├── DownloadModelsError     # lỗi tải mô hình
    ├── SttTimeoutError         # tiến trình con STT quá hạn
    ├── StopTask                # ngoại lệ cần dừng tác vụ ngay
    └── StopRetry               # lỗi không thể thử lại
```

Hàm `get_msg_from_except(e)` ánh xạ hàng chục loại ngoại lệ của thư viện bên thứ ba thành thông báo lỗi dễ hiểu (bao phủ `httpx`, `openai`, `requests`, `deepgram`, `elevenlabs`, `tenacity`...).

Bộ `NO_RETRY_EXCEPT` định nghĩa các loại ngoại lệ không thể khắc phục; mô-đun dịch/lồng tiếng gặp những ngoại lệ này trong vòng lặp thử lại sẽ bỏ cuộc ngay.

---

## 13. Tổng quan cấu trúc mã nguồn

```
/
├── sp.py                       # ★ điểm vào chương trình chính (221 dòng)
├── cli.py                      # ★ điểm vào dòng lệnh
├── models/                     # chứa các tệp mô hình AI cục bộ (ONNX...)
├── logs/                       # thư mục tệp nhật ký (YYYYMMDD.log)
├── ffmpeg/                     # tệp nhị phân ffmpeg và sox
├── f5-tts/                     # thư mục chứa âm thanh mẫu để nhân bản giọng
├── docs/                       # tài liệu
├── tmp/                        # thư mục gốc chứa tệp tạm
│   ├── _temp/                  # thư mục tạm cấp tiến trình
│   └── translate_cache/        # thư mục đệm bản dịch theo MD5
│
└── phiendichvideo/             # mã nguồn nghiệp vụ cốt lõi
    │   __init__.py             # ★ VERSION, định nghĩa ChannelProvider, get_class() nạp lười
    │   cfg.json                # tệp lưu settings
    │   params.json             # tệp lưu params
    │   codec.json              # đệm bộ mã hóa/giải mã video
    │
    ├── codes/
    │   └── model.py            # định nghĩa liên quan mô hình
    │
    ├── configure/              # cấu hình toàn cục, định nghĩa hàng đợi, lớp cơ sở cao nhất
    │   ├── config.py           # ★ AppCfg / AppSettings / AppParams / logger / hàng đợi / tr() / push_queue() (902 dòng)
    │   ├── base.py             # ★ lớp cơ sở BaseCon (_new_process, signal, _exit, convert_to_wav...) (296 dòng)
    │   ├── contants.py         # ★ hằng số toàn cục (danh sách mô hình, văn bản thử ngôn ngữ, dấu câu, danh sách trắng proxy...)
    │   ├── excepts.py          # ★ hệ thống ngoại lệ + get_msg_from_except() (376 dòng)
    │   ├── signal_hub.py       # ★ singleton SignalHub (tín hiệu Qt giữa các luồng) (33 dòng)
    │   └── whispernet_config.py # cấu hình Whisper.NET
    │
    ├── task/                   # logic xử lý tác vụ và luồng nền
    │   ├── _base.py            # ★ lớp cơ sở BaseTask (8 phương thức giai đoạn rỗng + 5 cờ + tiện ích chung) (167 dòng)
    │   ├── taskcfg.py          # ★ TaskCfgBase/VTT/STT/TTS/STS + InputFile + SignMsg + SrtItem (261 dòng)
    │   ├── trans_create.py     # ★ cài đặt đầy đủ TransCreate (~1678 dòng, lõi dịch video)
    │   ├── speech2text.py      # ★ SpeechToText (chuyển giọng nói thành phụ đề hàng loạt)
    │   ├── dubbing.py          # ★ DubbingSrt (lồng tiếng phụ đề hàng loạt)
    │   ├── translate_srt.py    # ★ TranslateSrt (dịch phụ đề SRT hàng loạt)
    │   ├── job.py              # ★ 9 lớp con BaseWorker + điểm vào start_thread() (245 dòng)
    │   ├── only_one.py         # ★ Worker(QThread) tương tác một video + tín hiệu uito (148 dòng)
    │   ├── mult_video.py       # ★ MultVideo(QThread) gửi nhiều video hàng loạt (54 dòng)
    │   ├── _rate.py            # bộ máy đồng bộ hình tiếng SpeedRate / TtsSpeedRate (877 dòng)
    │   ├── separate_worker.py  # SeparateWorker, QThread tách giọng nói độc lập
    │   ├── simple_runnable_qt.py # tiện ích nhóm luồng QRunnable
    │   ├── child_win_sign.py   # xử lý tín hiệu cửa sổ con
    │   └── update_ffmpeg.py    # quản lý cập nhật ffmpeg
    │
    ├── recognition/            # mô-đun nhận dạng giọng nói (ASR) — 26 kênh
    │   ├── __init__.py         # ★ hằng số ID kênh, _ID_NAME_DICT, run(), is_allow_lang(), is_input_api()
    │   ├── _base.py            # ★ BaseRecogn (cắt bằng VAD, xử lý CJK, gộp phụ đề, 400 dòng)
    │   └── _*.py               # cài đặt từng kênh (_whisper, _whisperx, _whispernet, _qwenasrlocal, _funasr...)
    │
    ├── translator/             # mô-đun dịch phụ đề — 24 kênh
    │   ├── __init__.py         # ★ hằng số kênh, _ID_NAME_DICT, LANG_CODE, run(), is_allow_translate() (860 dòng)
    │   ├── _base.py            # ★ BaseTrans (đệm MD5, điều phối dịch theo dòng/toàn văn, 176 dòng)
    │   └── _*.py               # cài đặt từng kênh (_google, _chatgpt, _deepseek, _gemini, _deepl, _baidu...)
    │
    ├── tts/                    # mô-đun chuyển văn bản thành giọng nói (TTS) — **34** kênh
    │   ├── __init__.py         # ★ hằng số ID kênh, _ID_NAME_DICT, SUPPORT_CLONE, CHANGE_BY_LANGUAGE, run() (192 dòng)
    │   ├── _base.py            # ★ BaseTTS (điều phối bất đồng bộ/đa luồng, 304 dòng)
    │   └── _*.py               # cài đặt từng kênh (_edgetts, _openaitts, _azuretts, _gptsovits, _cosyvoice...)
    │
    ├── process/                # cài đặt chạy trong tiến trình con
    │   ├── __init__.py         # xuất các hàm chạy tiến trình con
    │   ├── signelobj.py        # ★ GlobalProcessManager (hai nhóm tiến trình CPU/GPU, 167 dòng)
    │   ├── prepare_audio.py    # tách giọng nói, khử nhiễu, khôi phục dấu câu, phân tách người nói (4 nền)
    │   ├── stt_fun.py          # điểm vào ASR trong tiến trình con (openai_whisper, faster_whisper, paraformer, funasr_mlt, qwen3asr_fun...)
    │   ├── tts_fun.py          # điểm vào TTS trong tiến trình con (qwen3tts_fun)
    │   └── vad.py              # dò hoạt động giọng nói VAD (Silero VAD)
    │
    ├── mainwin/                # giao diện cửa sổ chính và logic nghiệp vụ
    │   ├── main_win.py         # ★ MainWindow(QMainWindow) khởi tạo, nối tín hiệu, khởi động luồng (528 dòng)
    │   ├── _actions.py         # ★ bộ điều khiển cốt lõi WinAction (kiểm tra, khởi động, cập nhật trạng thái, 798 dòng)
    │   └── _actions_base.py    # ★ lớp cơ sở WinActionBase (proxy, chuyển chế độ, CUDA, chọn tệp, 590 dòng)
    │
    ├── component/              # thành phần giao diện dùng chung
    │   ├── progressbar.py      # thanh tiến độ bấm được
    │   ├── set_form.py         # biểu mẫu cài đặt chung / trang giới thiệu
    │   ├── onlyone_set_recogn.py    # chế độ một video: hộp thoại sửa phụ đề gốc
    │   ├── onlyone_set_role.py      # chế độ một video: hộp thoại gán giọng cho người nói
    │   ├── onlyone_set_editdubb.py  # chế độ một video: hộp thoại sửa kết quả lồng tiếng
    │   ├── clip_video.py       # thành phần cắt video
    │   ├── realtime_stt.py     # cửa sổ nhận dạng giọng nói thời gian thực
    │   ├── textmatching.py     # cửa sổ so khớp văn bản
    │   ├── set_proxy.py        # hộp thoại cài đặt proxy
    │   ├── set_ass.py          # cài đặt kiểu phụ đề ASS
    │   ├── set_cpp.py          # cài đặt đường dẫn Whisper.cpp
    │   ├── set_xxl.py          # cài đặt đường dẫn Faster-Whisper-XXL
    │   ├── set_subtitles_length.py # cài đặt độ dài phụ đề
    │   ├── set_threads.py      # cài đặt số luồng
    │   └── controlobj.py       # quản lý đối tượng widget
    │
    ├── ui/                     # tệp định nghĩa giao diện PySide6 (~75 tệp .py)
    │   ├── en.py               # ★ định nghĩa bố cục cửa sổ chính
    │   ├── chatgpt.py, deepseek.py, gemini.py, ...    # bố cục hộp thoại cài đặt từng kênh
    │   ├── videoandaudio.py, separate.py, peiyin.py, ... # bố cục các cửa sổ chức năng
    │   └── dark/               # tài nguyên giao diện tối (darkstyle_rc.py, palette.py)
    │
    ├── winform/                # quản lý nạp lười cửa sổ cài đặt từng kênh (~65 mô-đun)
    │   ├── __init__.py         # ★ điểm vào nạp lười get_win() + _module_map (91 dòng)
    │   ├── chatgpt.py, azure.py, baidu.py, ...  # ~50 cửa sổ cài đặt kênh (openwin())
    │   └── fn_*.py             # ~10 cửa sổ chức năng độc lập (bóc phụ đề hàng loạt, lồng tiếng hàng loạt, dịch SRT hàng loạt...)
    │
    ├── styles/                 # kiểu giao diện và tài nguyên đa phương tiện
    │   ├── style.qss           # bảng kiểu Qt
    │   ├── logo.png            # logo màn hình khởi động
    │   ├── icon.ico            # biểu tượng ứng dụng
    │   ├── simhei.ttf          # phông chữ Hán SimHei
    │   ├── preview.png         # ảnh xem trước
    │   ├── no-remove.mp4       # video giữ chỗ, không được xóa
    │   └── no-remove.wav       # âm thanh giữ chỗ, không được xóa
    │
    ├── util/                   # hàm tiện ích dùng chung (18 tệp)
    │   ├── tools.py            # ★ hàm tiện ích cốt lõi (bọc ffmpeg, đọc/định dạng phụ đề, thao tác tệp, thông báo hệ thống, tải mô hình)
    │   ├── gpus.py             # dò và phân bổ GPU (get_cudaX lấy chỉ số GPU khả dụng)
    │   ├── checkgpu.py         # luồng dò GPU (AiLoaderThread)
    │   ├── ListenVoice.py      # chức năng nghe thử giọng (ListenVioce QThread)
    │   ├── req_fac.py          # nhà máy tạo session tùy chỉnh cho HuggingFace
    │   ├── cn_tn.py            # chuẩn hóa văn bản tiếng Trung
    │   ├── en_tn.py            # chuẩn hóa văn bản tiếng Anh
    │   ├── help_down.py        # hàm tiện ích tải về
    │   ├── help_ffmpeg.py      # dò bộ mã hóa/giải mã video của ffmpeg
    │   ├── help_misc.py        # tiện ích linh tinh
    │   ├── help_role.py        # tiện ích về giọng lồng tiếng
    │   ├── help_srt.py         # tiện ích về tệp phụ đề
    │   ├── helper_supertonic.py # hỗ trợ Supertonic TTS
    │   ├── TestSrtTrans.py     # công cụ thử dịch
    │   └── TestSTT.py          # công cụ thử nhận dạng
    │
    ├── language/               # tệp JSON đa ngôn ngữ cho giao diện
    │   ├── vi.json             # Tiếng Việt
    │   ├── en.json             # Tiếng Anh
    │   └── zh.json             # Tiếng Trung
    │
    ├── prompts/                # mẫu prompt cho dịch bằng AI
    │   ├── srt/                # prompt dịch định dạng SRT (chatgpt.txt, deepseek.txt...)
    │   ├── text/               # prompt dịch văn bản thuần (tương ứng)
    │   ├── recogn/             # prompt nhận dạng giọng nói (gemini_recogn.txt)
    │   └── resegment/          # prompt tách câu bằng LLM (llm.txt, llm2.txt)
    │
    └── voicejson/              # tệp cấu hình giọng đọc của TTS
        ├── edge_tts.json       # danh sách giọng Edge-TTS theo từng ngôn ngữ
        ├── azure_voice_list.json # danh sách giọng Azure TTS
        ├── qwen3tts.json       # giọng Qwen3-TTS
        └── ...                 # cấu hình giọng của các kênh khác
```

---

## 14. Hướng dẫn mở rộng

### 14.1 Thêm một kênh dịch mới

Giả sử muốn thêm kênh dịch `MyTranslator`:

#### Bước 1: Tạo tệp cài đặt kênh

Tạo `_mytranslator.py` trong `phiendichvideo/translator/`:

```python
from dataclasses import dataclass
from phiendichvideo.translator._base import BaseTrans

@dataclass
class MyTranslator(BaseTrans):
    def __post_init__(self):
        super().__post_init__()
        self.api_url = 'https://api.example.com/translate'

    def _item_task(self, data: dict) -> str:
        text = data['text']
        source = data['source_code']
        target = data['target_code']
        result = call_my_api(text, source, target)
        return result
```

#### Bước 2: Cấp ID kênh và đăng ký

Trong `phiendichvideo/translator/__init__.py`:

```python
MYTRANSLATOR_INDEX = 24   # cấp một ID số nguyên chưa trùng

# Thêm vào cuối _ID_NAME_DICT:
_ID_NAME_DICT[MYTRANSLATOR_INDEX] = ChannelProvider(
    "My Translator",
    imp="._mytranslator",
    key_name="mytranslator_key",
    win="mytranslator"
)
```

#### Bước 3: Thêm trường cấu hình người dùng

Thêm vào `AppParams._get_defaults()` trong `phiendichvideo/configure/config.py`:

```python
"mytranslator_key": "",
"mytranslator_model": "model-v1",
```

#### Bước 4: Tạo cửa sổ cài đặt

Tạo `mytranslator.py` trong `phiendichvideo/winform/`, cài đặt hàm `openwin()`. Đăng ký vào `_module_map` trong `phiendichvideo/winform/__init__.py`:

```python
"mytranslator": ".mytranslator",
```

#### Bước 5: Mở rộng tùy chọn

- Thêm kiểm tra tương thích ngôn ngữ trong `is_allow_translate()`
- Thêm tệp giao diện trong thư mục `ui/`
- Thêm Action tương ứng vào menu trong `ui/en.py`

---

### 14.2 Thêm một kênh TTS mới

Các bước tương tự kênh dịch:

1. Tạo `phiendichvideo/tts/_mytts.py`, kế thừa `BaseTTS`
2. Cấp ID và đăng ký vào `_ID_NAME_DICT` trong `phiendichvideo/tts/__init__.py`
3. Nếu cần hỗ trợ nhân bản giọng, thêm ID vào danh sách `SUPPORT_CLONE`
4. Nếu cần giọng thay đổi theo ngôn ngữ, thêm ID vào danh sách `CHANGE_BY_LANGUAGE`
5. Thêm trường cấu hình khóa API / URL tương ứng vào `AppParams._get_defaults()`
6. Đăng ký cửa sổ cài đặt trong `phiendichvideo/winform/` và `_module_map`

### 14.3 Thêm một kênh nhận dạng mới

Các bước giống kênh dịch/TTS. Lớp cài đặt kênh kế thừa `BaseRecogn` và bắt buộc phải cài đặt phương thức `.run()` trả về `List[SrtItem]`.

### 14.4 Quy ước chung

- Mọi lớp kênh dùng `@dataclass` + `__post_init__`
- Nạp lười qua `get_class(channel_id, "recognition/translator/tts", _ID_NAME_DICT)`
- Việc kiểm tra khóa API dựa vào hàm `is_input_api()` cùng hai trường `key_name` / `win` trong `_ID_NAME_DICT`
- Số luồng đồng thời bên trong bộ máy dịch/lồng tiếng do các trường tương ứng trong `settings` quyết định

---

> **Phiên bản**: v4.04 (VERSION_NUM=404)
> **Kho mã nguồn bản Việt hóa**: https://github.com/haianh02034/VideoTrans
> **Dự án gốc**: https://github.com/jianchang512/pyvideotrans
> **Tài liệu dự án gốc**: https://pyvideotrans.com
