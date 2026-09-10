# Nguyên lý đồng bộ dấu thời gian hình và tiếng

Tài liệu này giải thích chi tiết cách hoạt động của mô-đun "đồng bộ lồng tiếng, phụ đề và video" trong Phiên Dịch Video (`phiendichvideo/task/_rate.py`). Mô-đun này chịu trách nhiệm căn khớp chính xác phần lồng tiếng đã dịch với video câm gốc trên trục thời gian, rồi ghép thành video mới mượt mà.

---

## Mục lục

- [1. Bối cảnh vấn đề](#1-bối-cảnh-vấn-đề)
- [2. Những khó khăn cốt lõi](#2-những-khó-khăn-cốt-lõi)
- [3. Tổng quan các chiến lược đồng bộ](#3-tổng-quan-các-chiến-lược-đồng-bộ)
- [4. Tiền xử lý dữ liệu: mở rộng trục thời gian](#4-tiền-xử-lý-dữ-liệu-mở-rộng-trục-thời-gian)
- [5. Chế độ 1: chỉ tăng tốc âm thanh](#5-chế-độ-1-chỉ-tăng-tốc-âm-thanh)
- [6. Chế độ 2: chỉ làm chậm video](#6-chế-độ-2-chỉ-làm-chậm-video)
- [7. Chế độ 3: kết hợp âm thanh và video](#7-chế-độ-3-kết-hợp-âm-thanh-và-video)
- [8. Chế độ 4: ghép nối không đổi tốc độ](#8-chế-độ-4-ghép-nối-không-đổi-tốc-độ)
- [9. Chi tiết cách đổi tốc độ âm thanh](#9-chi-tiết-cách-đổi-tốc-độ-âm-thanh)
- [10. Chi tiết cách đổi tốc độ video](#10-chi-tiết-cách-đổi-tốc-độ-video)
- [11. Ghép nối âm thanh cuối cùng](#11-ghép-nối-âm-thanh-cuối-cùng)
- [12. Ghép nối các đoạn video](#12-ghép-nối-các-đoạn-video)
- [13. TtsSpeedRate: trường hợp chỉ lồng tiếng](#13-ttsspeedrate-trường-hợp-chỉ-lồng-tiếng)
- [14. Tương thích đa nền tảng](#14-tương-thích-đa-nền-tảng)
- [15. Giới hạn đã biết và lưu ý](#15-giới-hạn-đã-biết-và-lưu-ý)

---

## 1. Bối cảnh vấn đề

Quy trình đầy đủ khi Phiên Dịch Video dịch một video từ ngôn ngữ A sang ngôn ngữ B:

```text
Video gốc (ngôn ngữ A)
    │
    ├─→ Tách luồng video câm (novoice.mp4)
    ├─→ Trích âm thanh → nhận dạng (ASR) → phụ đề ngôn ngữ A
    ├─→ Dịch → phụ đề ngôn ngữ B
    ├─→ Lồng tiếng (TTS) → từng tệp wav lồng tiếng ngôn ngữ B
    │
    └─→ 【MÔ-ĐUN NÀY】lồng tiếng B + phụ đề B + video câm → đồng bộ và ghép → video mới
```

**Mâu thuẫn cốt lõi**: cùng một ý nhưng số âm tiết và cấu trúc ngữ pháp của mỗi ngôn ngữ khác nhau, khiến thời lượng lồng tiếng không khớp thời lượng phụ đề gốc.

**Ví dụ**:
- Đoạn phụ đề gốc: `0:03.000 ~ 0:06.000` (dài 3 giây)
- Lồng tiếng sau khi dịch: thực tế tạo ra âm thanh dài 4,2 giây
- Chênh lệch: `4.2 - 3.0 = 1.2` giây bị tràn

Nếu không xử lý sẽ dẫn tới:
1. Lồng tiếng lệch với hình (miệng đã mấp máy nhưng tiếng chưa tới)
2. Phụ đề không khớp tiếng
3. Sai lệch dấu thời gian tích lũy dần qua nhiều dòng phụ đề

---

## 2. Những khó khăn cốt lõi

### 2.1 Giới hạn độ chính xác của FFmpeg

FFmpeg không xử lý video chính xác tới từng mili giây. Khi đổi tốc độ bằng PTS (Presentation Time Stamp), video xuất ra có thể ngắn hoặc dài hơn thời lượng mong muốn một chút. Sai số này rất nhỏ ở từng đoạn (vài mili giây) nhưng sẽ tích lũy sau khi ghép hàng trăm đoạn.

### 2.2 Tốc độ khung hình không cố định

Video có thể ở 25fps, 29.97fps, 30fps... Một số đoạn có thể ngắn hơn một khung hình, và FFmpeg gần như chắc chắn thất bại khi đổi tốc độ những đoạn cực ngắn như vậy.

### 2.3 Khác biệt ngôn ngữ khó lường trước

Thời lượng lồng tiếng thay đổi tùy theo:
- Mật độ âm tiết khác nhau giữa ngôn ngữ nguồn và ngôn ngữ đích
- Đặc tính tốc độ đọc của công cụ TTS
- Khác biệt cấu trúc ngữ pháp của câu
- Có dùng nhân bản giọng nói hay không (ở chế độ nhân bản, thời lượng càng khó kiểm soát)

---

## 3. Tổng quan các chiến lược đồng bộ

Phiên Dịch Video có bốn chế độ đồng bộ, điều khiển bởi hai cờ boolean:

| Chế độ | `should_audiorate` | `should_videorate` | Mô tả |
|------|:---:|:---:|------|
| **Chỉ tăng tốc âm thanh** | ✅ | ✗ | Tăng tốc lồng tiếng cho khớp thời lượng phụ đề |
| **Chỉ làm chậm video** | ✗ | ✅ | Làm chậm hình cho khớp thời lượng lồng tiếng |
| **Kết hợp cả hai** | ✅ | ✅ | Mỗi bên gánh một nửa chênh lệch |
| **Không đổi tốc độ** | ✗ | ✗ | Ghép thẳng, chèn khoảng lặng vào chỗ trống |

```text
                    ┌───────────────────────────┐
                    │ Lồng tiếng > phụ đề?      │
                    └──────────┬────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │                      │
                  Không                    Có
                    │                      │
            ┌───────┴───────┐    ┌─────────┴─────────┐
            │ Không cần xử  │    │ Tính tỉ lệ tăng   │
            │ lý, ghép thẳng│    │ ratio = tiếng/phụ │
            └───────────────┘    └─────────┬─────────┘
                                           │
                              ┌────────────┴──────────┐
                              │                       │
                     ratio ≤ 1.2               ratio > 1.2
                              │                       │
                     ┌────────┴────────┐    ┌─────────┴────────┐
                     │ Chỉ tăng tốc    │    │ Âm thanh và video│
                     │ âm thanh        │    │ mỗi bên một nửa  │
                     └─────────────────┘    └──────────────────┘
```

---

## 4. Tiền xử lý dữ liệu: mở rộng trục thời gian

### 4.1 Vấn đề: khoảng lặng giữa các dòng phụ đề

Trục thời gian của phụ đề gốc thường có khoảng trống:

```text
Phụ đề 1: 0:00.000 ~ 0:03.000  (3s)
       ─────── lặng 0.5s ───────
Phụ đề 2: 0:03.500 ~ 0:07.000  (3.5s)
```

Nếu tăng tốc thẳng phần lồng tiếng của phụ đề 1 xuống còn 3s, trong khi không gian thực tế có tới 3,5s (đến lúc phụ đề kế tiếp bắt đầu), ta lãng phí 0,5s đệm và tăng tốc nhiều hơn mức cần thiết.

### 4.2 Giải pháp: mở rộng thời điểm kết thúc của mỗi dòng phụ đề

Ở bước tiền xử lý, `end_time` của mỗi dòng phụ đề được đổi thành `start_time` của dòng kế tiếp, nhờ đó khoảng lặng được tính vào quỹ thời gian khả dụng của dòng hiện tại:

```text
Trước khi xử lý:
Phụ đề 1: start=0ms,    end=3000ms   (3s)
Phụ đề 2: start=3500ms, end=7000ms   (3.5s)

Sau khi xử lý:
Phụ đề 1: start=0ms,    end=3500ms   (3.5s) ← mở rộng tới lúc dòng sau bắt đầu
Phụ đề 2: start=3500ms, end=7000ms   (3.5s) ← dòng cuối mở rộng tới hết video
```

### 4.3 Mã nguồn then chốt

```python
def _prepare_data(self):
    """Làm sạch và tiền xử lý dữ liệu"""
    for i in range(len(self.queue_tts)):
        current = self.queue_tts[i]

        # Lưu lại thời điểm bắt đầu gốc
        current['start_time_source'] = current['start_time']

        # Nếu có làm chậm video và dòng đầu bắt đầu < 100ms thì cho bắt đầu từ 0
        if self.should_videorate and i == 0 and current['start_time'] < 100:
            current['start_time_source'] = 0

        # Then chốt: mở rộng thời điểm kết thúc tới lúc dòng kế tiếp bắt đầu
        if i < len(self.queue_tts) - 1:
            next_sub = self.queue_tts[i + 1]
            current['end_time_source'] = next_sub['start_time']
            current['end_time'] = next_sub['start_time']
        else:
            # Dòng cuối: mở rộng tới hết video
            current['end_time_source'] = self.raw_total_time
            current['end_time'] = self.raw_total_time

        # Tính thời lượng khả dụng sau khi mở rộng
        current['source_duration'] = current['end_time_source'] - current['start_time_source']
```

### 4.4 So sánh hiệu quả

```text
Giả sử dữ liệu gốc:
Phụ đề 1: start=1000ms, end=3000ms (2s), lồng tiếng=3.5s
Phụ đề 2: start=3500ms, end=6000ms (2.5s), lồng tiếng=2.0s

Sau khi xử lý:
Phụ đề 1: source_duration = 3500 - 1000 = 2500ms (đã gộp thêm 500ms khoảng lặng)
Phụ đề 2: source_duration = 6000 - 3500 = 2500ms

Tỉ lệ tăng tốc:
Phụ đề 1: 3.5 / 2.5 = 1.4x (nếu không mở rộng thì phải 3.5/2.0 = 1.75x)
Phụ đề 2: không cần tăng tốc (2.0 < 2.5)
```

**Kết luận**: việc mở rộng trục thời gian đã giảm tỉ lệ tăng tốc của phụ đề 1 từ 1,75x xuống 1,4x, giảm đáng kể mức can thiệp vào âm thanh và giữ chất lượng tiếng tốt hơn.

---

## 5. Chế độ 1: chỉ tăng tốc âm thanh

### 5.1 Chiến lược

Khi lồng tiếng dài hơn quỹ thời gian của phụ đề, âm thanh được tăng tốc cho khớp. Tỉ lệ tăng tốc không được vượt quá `max_audio_speed_rate` (mặc định 100).

```text
Lồng tiếng: ═══════════════════════  (3500ms)
Phụ đề:     ══════════════           (2500ms)
                         ↓ tăng tốc 1.4x
Kết quả:    ══════════════           (2500ms) + chèn khoảng lặng
```

### 5.2 Mã nguồn then chốt

```python
# Chỉ tăng tốc âm thanh
if self.should_audiorate and not self.should_videorate:
    if dubb_dur > source_dur:
        ratio = dubb_dur / source_dur
        if ratio > self.max_audio_speed_rate:
            # Vượt tỉ lệ tăng tốc tối đa, giới hạn lại mức tăng
            audio_target = int(dubb_dur / self.max_audio_speed_rate)
        else:
            # Tăng tốc cho khớp thời lượng phụ đề
            audio_target = source_dur
```

### 5.3 Đăng ký tác vụ tăng tốc

```python
if self.should_audiorate and audio_target < dubb_dur:
    self.audio_data.append({
        "filename": it['filename'],       # đường dẫn tệp lồng tiếng
        "dubb_time": dubb_dur,            # thời lượng lồng tiếng gốc
        "target_time": audio_target        # thời lượng đích sau khi tăng tốc
    })
```

---

## 6. Chế độ 2: chỉ làm chậm video

### 6.1 Chiến lược

Khi lồng tiếng dài hơn quỹ thời gian phụ đề, đoạn video tương ứng được phát chậm lại để kéo dài cho khớp. Hệ số PTS không được vượt quá `max_video_pts_rate` (mặc định 10).

```text
Đoạn video: ══════════════       (2500ms)
Lồng tiếng: ═══════════════════  (3500ms)
                       ↓ làm chậm PTS=1.4
Kết quả:    ═══════════════════  (3500ms)
```

### 6.2 Nguyên lý PTS

PTS (Presentation Time Stamp) điều khiển thời điểm hiển thị của từng khung hình. Bộ lọc `setpts` của FFmpeg thay đổi được PTS:

```text
setpts=1.0*PTS  → tốc độ bình thường
setpts=2.0*PTS  → chậm 2 lần (thời gian hiển thị mỗi khung hình tăng gấp đôi)
setpts=0.5*PTS  → nhanh 2 lần (thời gian hiển thị mỗi khung hình giảm một nửa)
```

### 6.3 Mã nguồn then chốt

```python
# Chỉ làm chậm video
elif not self.should_audiorate and self.should_videorate:
    if dubb_dur > source_dur:
        video_target = dubb_dur  # thời lượng video đích = thời lượng lồng tiếng
        pts = video_target / source_dur
        if pts > self.max_video_pts_rate:
            # Vượt hệ số làm chậm tối đa, giới hạn lại
            video_target = int(source_dur * self.max_video_pts_rate)
```

### 6.4 Đăng ký đoạn video

```python
if self.should_videorate:
    pts = video_target / source_dur if source_dur > 0 else 1.0
    self.video_for_clips.append({
        "start": it['start_time_source'],   # điểm bắt đầu cắt video
        "end": it['end_time_source'],        # điểm kết thúc cắt video
        "target_time": video_target,         # thời lượng đích cần xuất
        "pts": pts,                          # hệ số PTS
        "tts_index": i,                      # chỉ số phụ đề tương ứng
        "line": it['line']                   # số dòng phụ đề
    })
```

---

## 7. Chế độ 3: kết hợp âm thanh và video

### 7.1 Chiến lược

Khi bật đồng thời tăng tốc âm thanh và làm chậm video, chương trình chọn chiến lược tùy theo tỉ lệ lồng tiếng/phụ đề:

| Tỉ lệ (ratio) | Chiến lược | Lý do |
|:---:|------|------|
| ≤ 1.2 | Chỉ tăng tốc âm thanh | Tỉ lệ nhỏ, tăng tốc gần như không ảnh hưởng chất lượng tiếng, chưa cần chạm vào video |
| > 1.2 | Mỗi bên gánh một nửa | Tăng tốc âm thanh và làm chậm video chia đôi phần chênh lệch |

```text
Ví dụ: phụ đề 2500ms, lồng tiếng 6000ms, ratio = 2.4

Phương án A (ratio ≤ 1.2):
  Tăng tốc âm thanh xuống 2500ms (2.4x) → chất lượng tiếng giảm nhiều
  Video giữ nguyên → 2500ms

Phương án B (ratio > 1.2, đây là phương án thực dùng):
  diff = 6000 - 2500 = 3500ms
  joint_target = 2500 + 3500/2 = 4250ms
  Tăng tốc âm thanh xuống 4250ms (1.41x) → chất lượng tiếng giảm ít
  Làm chậm video tới 4250ms (PTS=1.7) → hình hơi chậm nhưng chấp nhận được
```

### 7.2 Mã nguồn then chốt

```python
elif self.should_audiorate and self.should_videorate:
    if dubb_dur > source_dur:
        ratio = dubb_dur / source_dur
        if ratio <= self.BOTH_MODE_AUDIO_ONLY_THRESHOLD:  # 1.2
            # Tỉ lệ nhỏ, chỉ cần tăng tốc âm thanh, không cần làm chậm video
            audio_target = source_dur
            video_target = source_dur
        else:
            # Tỉ lệ lớn, tăng tốc âm thanh và làm chậm video mỗi bên gánh một nửa
            diff = dubb_dur - source_dur
            joint_target = int(source_dur + (diff / 2))
            audio_target = joint_target
            video_target = joint_target
```

### 7.3 Vì sao chọn ngưỡng 1.2?

- **Tăng tốc âm thanh ≤ 1.2x**: tai người gần như không nhận ra thay đổi chất lượng
- **Vượt quá 1.2x**: tác dụng phụ của việc chỉ dùng một biện pháp bắt đầu lộ rõ, cần chia sẻ gánh nặng

---

## 8. Chế độ 4: ghép nối không đổi tốc độ

### 8.1 Chiến lược

Khi không bật cả tăng tốc âm thanh lẫn làm chậm video, chương trình ghép thẳng các tệp lồng tiếng theo trục thời gian phụ đề, chèn khoảng lặng vào chỗ trống — hoặc bỏ luôn khoảng lặng nếu bạn chọn xóa chúng.

Nếu chọn đồng bộ trục thời gian phụ đề, dấu thời gian phụ đề sẽ được sửa theo thời lượng âm thanh thực tế, để phụ đề hiện lên đúng lúc tiếng bắt đầu và biến mất khi tiếng kết thúc.

### 8.2 Quy tắc ghép nối

```text
Trục thời gian phụ đề:
├── 0ms ──── 1000ms ──── 3500ms ──── 6000ms ──── 8000ms
│   lặng     phụ đề 1     phụ đề 2     phụ đề 3
│  (1000ms)  (2500ms)     (2500ms)     (2000ms)

Kết quả ghép:
├── [lặng 1000ms] + [tiếng 1] + [tiếng 2] + [tiếng 3] + [lặng đuôi]
```

### 8.3 Mã nguồn then chốt

```python
def _run_no_rate_change_mode(self):
    audio_concat_list = []
    total_audio_duration = 0

    for i, it in enumerate(self.queue_tts):
        prev_end = 0 if i == 0 else self.queue_tts[i-1].get('end_pos_for_concat', 0)
        start_time = it['start_time']

        # Tính khoảng trống so với dòng trước
        gap = start_time - prev_end

        # Nếu không xóa khoảng lặng thì chèn khoảng lặng vào
        if not self.remove_silent_mid and gap > 0:
            audio_concat_list.append(self._create_silen_file(f"gap_{i}", gap))
            total_audio_duration += gap

        # Ghép tệp lồng tiếng
        if it.get('filename') and Path(it['filename']).exists():
            audio_concat_list.append(it['filename'])
            dubb_len = len(AudioSegment.from_file(it['filename']))
        # ...

        total_audio_duration += dubb_len
        it['end_pos_for_concat'] = total_audio_duration

        # Đồng bộ trục thời gian phụ đề
        if self.align_sub_audio:
            it['start_time'] = total_audio_duration - dubb_len
            it['end_time'] = total_audio_duration

    # Khoảng lặng đuôi: nếu tổng thời lượng âm thanh < tổng thời lượng video
    if self.raw_total_time > total_audio_duration:
        audio_concat_list.append(
            self._create_silen_file("tail_end", self.raw_total_time - total_audio_duration)
        )
```

---

## 9. Chi tiết cách đổi tốc độ âm thanh

### 9.1 Hai công cụ đổi tốc độ

Phiên Dịch Video hỗ trợ hai cách đổi tốc độ âm thanh, tự chọn theo thứ tự ưu tiên:

| Công cụ | Ưu tiên | Phụ thuộc | Đặc điểm |
|------|:---:|------|------|
| **Rubber Band** | Cao | `pyrubberband` + `rubberband` CLI | Chất lượng tốt nhất, giữ nguyên cao độ |
| **FFmpeg atempo** | Thấp | FFmpeg (có sẵn) | Không cần cài thêm gì, chất lượng kém hơn chút |

### 9.2 Đổi tốc độ bằng Rubber Band

```python
def _change_speed_rubberband(input_path, target_duration):
    # Đọc âm thanh
    y, sr = sf.read(input_path)
    current_duration = round((len(y) / sr) * 1000)

    # Tính hệ số đổi tốc độ
    time_stretch_rate = current_duration / target_duration
    time_stretch_rate = max(0.2, min(time_stretch_rate, 50.0))

    # Thực hiện đổi tốc độ (giữ nguyên cao độ)
    y_stretched = pyrb.time_stretch(y, sr, time_stretch_rate)

    # Chuyển đơn kênh thành hai kênh
    if y_stretched.ndim == 1:
        y_stretched = np.column_stack((y_stretched, y_stretched))

    # Ghi lại vào tệp
    sf.write(input_path, y_stretched, sr)
```

**Ưu điểm của Rubber Band**:
- Dùng thuật toán Phase Vocoder, đổi tốc độ mà vẫn giữ nguyên cao độ
- Chịu được hệ số lớn (tới 50x) mà không mất chất lượng rõ rệt
- Xử lý nhanh, hỗ trợ đa luồng

### 9.3 Đổi tốc độ bằng FFmpeg atempo (phương án dự phòng)

```python
def _precise_speed_up_audio(input_path, target_duration):
    current_duration_ms = len(AudioSegment.from_file(input_path, format='wav'))

    # Giới hạn của atempo: tham số phải nằm trong [0.5, 2.0]
    # Vượt ngoài khoảng này thì phải nối chuỗi nhiều atempo lại
    atempo_list = []
    speed_factor = current_duration_ms / target_duration

    while speed_factor > 2.0:
        atempo_list.append("atempo=2.0")
        speed_factor /= 2.0

    atempo_list.append(f"atempo={speed_factor}")
    filter_str = ",".join(atempo_list)

    # Ví dụ: tăng tốc 8x → "atempo=2.0,atempo=2.0,atempo=2.0"
    cmd = [
        '-y', '-i', input_path,
        '-filter:a', filter_str,
        '-t', f"{target_duration/1000.0}",  # ép cắt về đúng thời lượng đích
        '-ar', "48000", '-ac', "2",
        '-c:a', 'pcm_s16le',
        f'{input_path}-after.wav'
    ]
    tools.runffmpeg(cmd)
    shutil.copy2(f'{input_path}-after.wav', input_path)
```

**Nguyên lý nối chuỗi atempo**:

```text
Khoảng cho phép của atempo: [0.5, 2.0]

Cần tăng tốc 8x:
  8.0 = 2.0 × 2.0 × 2.0
  → "atempo=2.0,atempo=2.0,atempo=2.0"

Cần tăng tốc 3x:
  3.0 = 2.0 × 1.5
  → "atempo=2.0,atempo=1.5"

Cần tăng tốc 1.3x:
  1.3 < 2.0, không cần tách
  → "atempo=1.3"
```

### 9.4 Tăng tốc song song bằng đa tiến trình

Các tác vụ đổi tốc độ âm thanh chạy song song qua `ProcessPoolExecutor`:

```python
def _execute_audio_speedup_rubberband(self):
    _wok = min(12, len(self.audio_data), max(os.cpu_count() - 1, 1))

    with ProcessPoolExecutor(max_workers=int(_wok)) as pool:
        for i, d in enumerate(self.audio_data):
            pool.submit(
                _change_speed_rubberband if HAS_RUBBERBAND else _precise_speed_up_audio,
                d['filename'],
                d['target_time']
            )
```

---

## 10. Chi tiết cách đổi tốc độ video

### 10.1 Nguyên lý đổi tốc độ bằng PTS

Bộ lọc `setpts` của FFmpeg đổi tốc độ bằng cách sửa PTS:

```text
Chuỗi khung hình gốc:
  Khung 1(0ms) → Khung 2(33ms) → Khung 3(66ms) → Khung 4(100ms)  [30fps]

setpts=2.0*PTS (chậm 2x):
  Khung 1(0ms) → Khung 2(66ms) → Khung 3(132ms) → Khung 4(200ms)

setpts=0.5*PTS (nhanh 2x):
  Khung 1(0ms) → Khung 2(16ms) → Khung 3(33ms) → Khung 4(50ms)
```

### 10.2 Dựng lệnh FFmpeg

```python
def _cut_video_get_duration(i, task, novoice_mp4_original, preset, crf, fps_mode):
    # Tham số cắt
    ss_time = tools.ms_to_time_string(ms=task['start'], sepflag='.')
    source_duration_s = (task['end'] - task['start']) / 1000.0
    target_duration_s = task.get('target_time', source_duration_ms) / 1000.0
    pts_factor = task.get('pts', 1.0)

    cmd = [
        '-y',
        '-ss', ss_time,                    # thời điểm bắt đầu
        '-t', f'{source_duration_s:.6f}',  # thời lượng cắt
        '-i', input_video_path,
        '-an',                             # bỏ âm thanh
        '-c:v', 'libx264',                # bộ mã hóa video
        '-g', '1',                         # GOP=1, đảm bảo cắt chính xác
        '-preset', preset,                 # tốc độ mã hóa
        '-crf', crf,                       # chất lượng
        '-pix_fmt', 'yuv420p'              # định dạng điểm ảnh
    ]

    # Bộ lọc đổi tốc độ PTS
    if abs(pts_factor - 1.0) >= 0.001:
        cmd.extend(['-vf', f'setpts={pts_factor}*PTS'])
    else:
        cmd.extend(['-vf', 'setpts=PTS'])

    cmd.extend(fps_mode)  # chế độ VFR hoặc CFR
    cmd.extend(['-t', f'{target_duration_s:.6f}'])  # ép giới hạn thời lượng đầu ra
    cmd.append(os.path.basename(task['filename']))
```

### 10.3 Chọn chế độ tốc độ khung hình

```python
self.fps_mode = ["-fps_mode", "vfr"]  # mặc định là tốc độ khung hình biến thiên

if settings.get('fps_mode') == 'cfr':
    video_fps = tools.get_video_info(novoice_mp4, video_fps=True)
    self.fps_mode = ["-r", f"{video_fps}", "-fps_mode", "cfr"]
```

| Chế độ | Mô tả | Trường hợp dùng |
|------|------|---------|
| **VFR** (khung hình biến thiên) | Cho phép tốc độ khung hình thay đổi, đổi tốc độ mượt hơn | Khuyến nghị mặc định |
| **CFR** (khung hình cố định) | Ép tốc độ khung hình cố định, tương thích tốt hơn | Dùng khi gặp lỗi tương thích với một số trình phát |

### 10.4 Cơ chế dự phòng

Nếu việc đổi tốc độ thất bại (tệp xuất ra < 1024B), chương trình tự động quay về cắt không đổi tốc độ:

```python
if not file_path.exists() or file_path.stat().st_size < 1024:
    # Dự phòng: cắt không đổi tốc độ
    cmd_backup = [
        '-y', '-ss', ss_time,
        '-t', f'{source_duration_s:.6f}',
        '-i', input_video_path,
        '-an', '-c:v', 'libx264',
        '-g', '1', '-preset', preset, '-crf', crf,
        '-pix_fmt', 'yuv420p',
        '-vf', 'setpts=PTS',  # giữ nguyên PTS gốc một cách tường minh
    ] + fps_mode
    cmd_backup.append(os.path.basename(task['filename']))
    tools.runffmpeg(cmd_backup, force_cpu=True, cmd_dir=work_dir)
```

### 10.5 Xử lý song song bằng đa tiến trình

```python
def _video_speeddown(self):
    _wok = min(12, len(data), max(os.cpu_count() - 1, 1))

    with ProcessPoolExecutor(max_workers=int(_wok)) as pool:
        for i, d in enumerate(data):
            pool.submit(_cut_video_get_duration, i, d,
                       self.novoice_mp4_original,
                       self.preset, self.crf, self.fps_mode)
```

---

## 11. Ghép nối âm thanh cuối cùng

### 11.1 Nguyên tắc

Dù dùng chế độ đổi tốc độ nào, bước ghép âm thanh cuối cùng đều theo cùng nguyên tắc:

1. **Mỗi đoạn lồng tiếng chiếm một "ô"**, độ dài ô do chiến lược đổi tốc độ quyết định
2. **Lồng tiếng ngắn hơn ô**: chèn khoảng lặng vào cuối
3. **Lồng tiếng dài hơn ô**: cắt bớt cho vừa ô
4. **Bằng đúng ô**: đặt thẳng vào

```text
Trục thời gian:
├── [ô 1: 3500ms] ├── [ô 2: 2500ms] ├── [ô 3: 2000ms] ──→

Nội dung ô 1:
├── [tiếng 1: 3200ms] + [lặng: 300ms]

Nội dung ô 2:
├── [tiếng 2: 2500ms]  (khớp chính xác)

Nội dung ô 3:
├── [tiếng 3: 2800ms] → cắt còn 2000ms
```

### 11.2 Mã nguồn then chốt

```python
def _concat_audio_aligned(self):
    audio_list = []
    current_timeline = self.queue_tts[0]['start_time']

    # Khoảng lặng đầu
    if current_timeline > 0:
        audio_list.append(self._create_silen_file("head_0", current_timeline))

    for i, it in enumerate(self.queue_tts):
        # Độ dài ô: có làm chậm video thì lấy thời lượng video thực tế,
        # nếu không thì lấy độ dài khoảng phụ đề
        slot_duration = it.get('final_duration', it['source_duration'])

        # Dự phòng: nếu độ dài ô bằng 0 thì quay về giá trị gốc
        if slot_duration <= 0:
            slot_duration = max(1, it['source_duration'])

        # Đọc tệp lồng tiếng
        seg = AudioSegment.from_file(audio_file)
        current_slot_audio_len = len(seg)

        # Ba trường hợp
        if current_slot_audio_len > slot_duration:
            # Tràn: cắt bớt
            cut_seg = seg[:slot_duration]
            cut_seg.export(final_slot_path, format='wav')
            audio_list.append(final_slot_path)

        elif current_slot_audio_len < slot_duration:
            # Thiếu: bù khoảng lặng
            diff = slot_duration - current_slot_audio_len
            audio_list.append(audio_file)
            audio_list.append(self._create_silen_file(f"tail_{i}", diff))

        else:
            # Khớp chính xác
            audio_list.append(audio_file)

        # Cập nhật trục thời gian phụ đề
        it['start_time'] = current_timeline
        it['end_time'] = current_timeline + slot_duration
        current_timeline += slot_duration

    self._exec_concat_audio(audio_list)
```

### 11.3 Tạo tệp khoảng lặng

```python
def _create_silen_file(self, name, duration_ms):
    path = Path(self.cache_folder, f"silence_{name}.wav").as_posix()
    duration_ms = max(1, int(duration_ms))
    AudioSegment.silent(duration=duration_ms, frame_rate=48000) \
                .set_channels(2) \
                .export(path, format="wav")
    return path
```

### 11.4 Ghép nối bằng FFmpeg

```python
def _exec_concat_audio(self, file_list):
    # Tạo tệp danh sách để ghép
    concat_txt = Path(self.cache_folder, 'final_audio_concat.txt').as_posix()
    tools.create_concat_txt(file_list, concat_txt=concat_txt)

    # Ghép bằng FFmpeg concat
    cmd = [
        '-y', '-f', 'concat', '-safe', '0',
        '-i', concat_txt,
        '-c:a', 'copy',  # chép thẳng, không mã hóa lại
        temp_wav
    ]
    tools.runffmpeg(cmd, force_cpu=True, cmd_dir=self.cache_folder)
```

---

## 12. Ghép nối các đoạn video

### 12.1 Luồng xử lý

```text
Video câm gốc (novoice.mp4)
    │
    ├─→ Cắt đoạn 1 (clip_0_1.400.mp4)  ← PTS=1.4 làm chậm
    ├─→ Cắt đoạn 2 (clip_1_1.000.mp4)  ← PTS=1.0 giữ nguyên
    ├─→ Cắt đoạn 3 (clip_2_1.700.mp4)  ← PTS=1.7 làm chậm
    │
    └─→ Ghép bằng FFmpeg concat → novoice.mp4 mới
```

### 12.2 Lệnh ghép nối

```python
def _concat_video(self, processed_clips):
    # Tạo danh sách ghép
    txt_content = []
    for clip in processed_clips:
        if clip.get('actual_duration', 0) > 0 and Path(clip['filename']).exists():
            txt_content.append(f"file '{clip['filename']}'")

    # FFmpeg concat (chép thẳng, không mã hóa lại)
    cmd = [
        '-y', '-f', 'concat', '-safe', '0',
        '-i', concat_list,
        '-c', 'copy',  # ghép không mất chất lượng
        output_path
    ]
    tools.runffmpeg(cmd, force_cpu=True, cmd_dir=self.cache_folder)

    # Thay thế video gốc
    shutil.move(output_path, self.novoice_mp4)
```

---

## 13. TtsSpeedRate: trường hợp chỉ lồng tiếng

### 13.1 Khác biệt so với SpeedRate

`TtsSpeedRate` kế thừa từ `SpeedRate`, dùng riêng cho tình huống "lồng tiếng hàng loạt cho phụ đề":

| Đặc điểm | SpeedRate | TtsSpeedRate |
|------|-----------|-------------|
| Làm chậm video | Có hỗ trợ | **Tắt** (`should_videorate=False`) |
| Tỉ lệ tăng tốc tối đa | Cấu hình được (mặc định 100) | Cố định 100 |
| Mở rộng trục thời gian | Đầy đủ (có lưu `start_time_source`) | Rút gọn (chỉ dời `end_time`) |
| Đầu ra | Video + âm thanh | Chỉ âm thanh |

### 13.2 Tiền xử lý rút gọn

```python
class TtsSpeedRate(SpeedRate):
    def _prepare_data(self):
        _len = len(self.queue_tts)
        for i in range(_len):
            current = self.queue_tts[i]
            if i < _len - 1:
                # Chỉ dời thời điểm kết thúc, không lưu thời điểm bắt đầu gốc
                current['end_time'] = self.queue_tts[i + 1]['start_time']

            current['source_duration'] = current['end_time'] - current['start_time']
            # ...
```

### 13.3 Chiến lược tính toán rút gọn

```python
def _calculate_adjustments(self):
    for i, it in enumerate(self.queue_tts):
        source_dur = it['source_duration']
        dubb_dur = it['dubb_time']

        if dubb_dur > source_dur:
            # Không giới hạn, ép tăng tốc cho khớp
            self.audio_data.append({
                "filename": it['filename'],
                "dubb_time": dubb_dur,
                "target_time": source_dur
            })
```

---

## 14. Tương thích đa nền tảng

### 14.1 Xử lý đường dẫn

Mọi đường dẫn tệp đều được chuyển sang dạng gạch chéo xuôi bằng `Path.as_posix()`, đảm bảo FFmpeg đọc đúng trên Windows, Linux lẫn macOS:

```python
input_video_path = Path(novoice_mp4_original).resolve().as_posix()
work_dir = Path(task['filename']).parent.as_posix()
```

### 14.2 Gọi FFmpeg

Mọi lời gọi FFmpeg đều đi qua `tools.runffmpeg()`, hàm này tự xử lý:
- Vấn đề khoảng trắng trong đường dẫn trên Windows
- Việc tìm tệp thực thi FFmpeg (trong PATH hệ thống hoặc thư mục `ffmpeg/` đi kèm)
- Ghép nối tham số dòng lệnh cho đúng

### 14.3 Nhóm tiến trình

Dùng `ProcessPoolExecutor` thay cho `multiprocessing.Pool` để tương thích đa nền tảng tốt hơn và quản lý tài nguyên gọn hơn.

### 14.4 Dọn tệp

Dùng `Path.glob()` + `Path.unlink()` thay cho `os.scandir()` + `os.remove()`, giữ API nhất quán.

---

## 15. Giới hạn đã biết và lưu ý

### 15.1 Giới hạn độ chính xác của FFmpeg

- FFmpeg không chính xác tới từng mili giây, video sau khi đổi tốc độ bằng PTS có thể ngắn hoặc dài hơn mong muốn một chút
- Sai số mỗi đoạn khoảng 10-50ms, ghép hàng trăm đoạn có thể tích lũy tới cỡ giây
- **Cách giảm thiểu**: ở bước ghép âm thanh cuối cùng, chương trình cắt bớt hoặc bù khoảng lặng để tổng thời lượng luôn khớp

### 15.2 Xử lý đoạn cực ngắn

- Đoạn ngắn hơn một khung hình (ví dụ dưới 33ms ở 30fps) gần như chắc chắn làm FFmpeg thất bại khi đổi tốc độ
- **Cách giảm thiểu**: bước tiền xử lý gộp khoảng trống vào dòng phụ đề hiện tại, đảm bảo mỗi đoạn dài ít nhất vài trăm mili giây

### 15.3 Mất chất lượng khi tăng tốc âm thanh

- Rubber Band: tăng tốc dưới 3x thì chất lượng gần như không đổi, trên 5x bắt đầu nghe máy móc
- FFmpeg atempo: tăng tốc trên 2x có thể làm thay đổi nhẹ âm sắc
- **Khuyến nghị**: với trường hợp cần tăng tốc nhiều (trên 3x), nên bật thêm làm chậm video để chia sẻ gánh nặng

### 15.4 Hình bị giật khi làm chậm video

- Làm chậm bằng PTS không sinh ra khung hình mới, chỉ kéo dài thời gian hiển thị của mỗi khung
- Video tốc độ khung hình thấp (như 24fps) sau khi chậm 2x thì mỗi khung hiển thị 83ms, có thể hơi giật
- **Khuyến nghị**: nên giữ hệ số làm chậm video trong khoảng 2x

### 15.5 Lọc bỏ đoạn không hợp lệ

Đoạn video nhỏ hơn 1024 byte được coi là không hợp lệ (chỉ chứa phần đầu tệp và siêu dữ liệu), sẽ tự động bị bỏ qua khi ghép:

```python
if clip.get('actual_duration', 0) > 0 and Path(clip['filename']).exists():
    # Đoạn hợp lệ, thêm vào danh sách ghép
    txt_content.append(f"file '{path}'")
else:
    logger.warning(f"[Video-Concat] Bỏ qua đoạn không hợp lệ: {clip.get('filename')}")
```

---

## Phụ lục: sơ đồ luồng xử lý đầy đủ

```text
                    ┌──────────────────────────┐
                    │  Đầu vào: danh sách       │
                    │  queue_tts (phụ đề + wav) │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────┴─────────────┐
                    │  should_audiorate hoặc    │
                    │  should_videorate bật?    │
                    └────────────┬─────────────┘
                                 │
                  ┌──────────────┴──────────────┐
                  │                             │
                 Có                           Không
                  │                             │
         ┌────────┴────────┐          ┌─────────┴─────────┐
         │ _prepare_data() │          │ _run_no_rate_      │
         │ mở rộng trục    │          │ change_mode()      │
         │ thời gian       │          │ ghép thẳng         │
         └────────┬────────┘          └─────────┬─────────┘
                  │                              │
         ┌────────┴────────┐                     │
         │ _calculate_     │                     │
         │ adjustments()   │                     │
         │ tính chiến lược │                     │
         └────────┬────────┘                     │
                  │                              │
    ┌─────────────┴─────────────┐                │
    │                           │                │
 đổi tốc âm thanh          đổi tốc video         │
    │                           │                │
 ┌──┴───┐                 ┌─────┴─────┐          │
 │RB/   │                 │_cut_video │          │
 │atempo│                 │_get_dur-  │          │
 │tăng  │                 │ation()    │          │
 │tốc   │                 │đổi PTS    │          │
 └──┬───┘                 └─────┬─────┘          │
    │                           │                │
    │                     ┌─────┴─────┐          │
    │                     │_concat_   │          │
    │                     │video()    │          │
    │                     │ghép video │          │
    │                     └─────┬─────┘          │
    │                           │                │
    └─────────────┬─────────────┘                │
                  │                              │
         ┌────────┴────────┐                     │
         │ _concat_audio_  │◄────────────────────┘
         │ aligned()       │
         │ ghép âm thanh   │
         └────────┬────────┘
                  │
         ┌────────┴────────┐
         │ _exec_concat_   │
         │ audio()         │
         │ FFmpeg ghép     │
         └────────┬────────┘
                  │
         ┌────────┴────────┐
         │ Đầu ra: âm thanh│
         │ cuối + trục thời│
         │ gian phụ đề mới │
         └─────────────────┘
```
