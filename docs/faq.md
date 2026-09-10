---
title: Lỗi thường gặp và cách khắc phục
date: 2024-01-22 14:33:00
description: Trong Menu → Trợ giúp/Giới thiệu có nhiều liên kết hữu ích như địa chỉ tải mô hình, cấu hình CUDA... Gặp vấn đề có thể mở ra dùng thử.
---

# Câu hỏi thường gặp về Phiên Dịch Video

Tài liệu này tổng hợp các vấn đề hay gặp và cách khắc phục.

Trong **Menu → Trợ giúp/Giới thiệu** có nhiều liên kết hữu ích như địa chỉ tải mô hình, hướng dẫn cấu hình CUDA... Gặp vấn đề có thể mở ra xem.

> **Xem nhật ký ở đâu**: thư mục `logs/` ở thư mục gốc phần mềm chứa các tệp `.log` đặt tên theo ngày. Khi báo lỗi, hãy chép khoảng 30 dòng cuối của nhật ký để nhờ hỗ trợ.
>
> **Khôi phục cài đặt gốc**: xóa bốn tệp `cfg.json`, `params.json`, `codec.json`, `ass.json` trong thư mục `phiendichvideo/` rồi khởi động lại phần mềm.

---

## Phần 1: Cài đặt và khởi động

### 1. Bấm đúp `sp.exe` mà phần mềm không mở hoặc rất lâu không phản hồi?

Đây thường là chuyện bình thường, đừng vội.

*   **Nguyên nhân**: phần mềm viết bằng `PySide6`, giao diện chính có khá nhiều thành phần cần khởi tạo ở lần tải đầu tiên. Tùy cấu hình máy, thời gian khởi động có thể từ **5 giây đến 2 phút**.
*   **Cách xử lý**:
    1.  **Kiên nhẫn đợi**: sau khi bấm đúp, hãy đợi một lúc.
    2.  **Kiểm tra phần mềm diệt virus**: một số phần mềm bảo mật có thể chặn chương trình khởi động. Hãy thử tắt tạm hoặc thêm phần mềm vào danh sách tin cậy.
    3.  **Kiểm tra đường dẫn**: đảm bảo đường dẫn chứa phần mềm **chỉ gồm chữ cái tiếng Anh và số**, không có dấu tiếng Việt, khoảng trắng hay ký tự đặc biệt. Ví dụ `D:\PhienDichVideo` là đường dẫn tốt, còn `D:\program file\video của tôi` có thể gây lỗi.
    4.  **Lỗi do gói nâng cấp**: nếu bạn ghi đè gói nâng cấp rồi không khởi động được, nghĩa là thao tác sai. Hãy tải lại gói đầy đủ, giải nén rồi mới ghi đè gói nâng cấp lên.

### 2. Khởi động báo thiếu tệp `python310.dll` thì làm sao?

Vấn đề này nghĩa là bạn mới tải gói vá nâng cấp mà chưa tải chương trình chính.

*   **Cách xử lý**:
    1.  Tải **gói đầy đủ** trước.
    2.  Giải nén gói đầy đủ vào thư mục mong muốn.
    3.  Sau đó tải gói vá mới nhất rồi ghi đè lên thư mục gói đầy đủ.

### 3. Phần mềm có cần cài đặt không?

Đây là bản chạy trực tiếp, **không cần cài đặt**. Tải gói đầy đủ, giải nén rồi bấm đúp `sp.exe` là chạy được.

### 4. Vì sao phần mềm diệt virus báo có virus hoặc chặn lại?

*   **Nguyên nhân**: phần mềm được đóng gói bằng `PyInstaller` và không có chứng thực chữ ký số thương mại. Một số phần mềm bảo mật cảnh báo dựa trên đặc điểm này, đây là **báo nhầm phổ biến**.
*   **Cách xử lý**:
    1.  **Thêm vào danh sách tin cậy** của phần mềm diệt virus.
    2.  **Chạy từ mã nguồn**: nếu bạn là lập trình viên, có thể triển khai và chạy trực tiếp từ mã nguồn để tránh hẳn vấn đề này.

### 5. Phần mềm có hỗ trợ Windows 7 không?

**Không**. Nhiều thành phần cốt lõi mà phần mềm phụ thuộc (PyTorch, PySide6) đã ngừng hỗ trợ Windows 7. Hãy dùng Windows 10 hoặc Windows 11.

### 6. macOS / Linux triển khai từ mã nguồn thế nào?

*   **Yêu cầu trước**:
    *   Python 3.10
    *   FFmpeg (`brew install ffmpeg` / `apt install ffmpeg`)
    *   Trình quản lý gói uv
    *   libsndfile
*   **Các bước**:
    ```bash
    git clone https://github.com/haianh02034/VideoTrans.git
    cd VideoTrans
    uv sync
    uv run sp.py
    ```
*   **Thư viện tùy chọn**: `uv sync --all-extras` cài tất cả các nhóm (webui, mosstts, dotnet)

### 7. Chạy từ mã nguồn nhưng khởi động báo lỗi thì làm sao?

Nguyên nhân thường gặp và cách xử lý:
*   **Chưa cài FFmpeg**: đảm bảo hệ thống đã cài FFmpeg và thêm vào biến môi trường PATH
*   **Thiếu thư viện**: chạy lại `uv sync`
*   **Sai phiên bản Python**: bắt buộc dùng Python 3.10 (tệp `.python-version` đã chỉ định)

---

## Phần 2: Chức năng chính và cài đặt

### 8. Làm sao tăng độ chính xác khi nhận dạng giọng nói?

Độ chính xác chủ yếu phụ thuộc vào kích thước mô hình bạn chọn và các thiết lập đi kèm.

*   **Chọn mô hình**: ở chế độ "faster" hoặc "openai", mô hình càng lớn thì càng chính xác nhưng càng chậm và tốn tài nguyên.
    *   `tiny`: nhỏ nhất, nhanh nhất, độ chính xác thấp.
    *   `base` / `small` / `medium`: cân bằng giữa chất lượng và tài nguyên, hay dùng nhất.
    *   `large-v3`: lớn nhất, tốt nhất, đòi hỏi phần cứng cao nhất (cần từ 8GB VRAM).
*   **Tinh chỉnh**: vào **Menu → Công cụ → Tùy chọn nâng cao**

Tìm phần điều chỉnh nhận dạng faster/openai rồi sửa như sau:

- **Ngưỡng giọng nói** đặt `0.5`
- **Đoạn nói ngắn nhất (ms)** đặt `3000`
- **Đoạn nói dài nhất (giây)** đặt `6`
- **Khoảng lặng để tách (ms)** đặt `140`
- **Từ khóa ưu tiên**: nếu video có thuật ngữ riêng, điền vào đây, cách nhau bằng dấu phẩy

*   **Khử nhiễu**: nếu video có nhạc nền hoặc tạp âm, vào `Thêm cài đặt` chọn `Tách giọng nói/nhạc nền` sẽ cải thiện rõ rệt.

### 9. Vì sao video sau khi xử lý bị giảm chất lượng?

Mọi thao tác có **mã hóa lại** đều làm giảm chất lượng video. Muốn giữ chất lượng gốc tối đa, hãy đảm bảo đủ các điều kiện sau:

1.  **Định dạng video gốc**: dùng tệp MP4 mã hóa **H.264 (libx264)** — tương thích tốt nhất.
2.  **Tắt làm chậm video**: không chọn "Tự động làm chậm video".
3.  **Không nhúng phụ đề cứng**: chọn không nhúng phụ đề, hoặc chỉ nhúng **phụ đề mềm**. Phụ đề cứng buộc phải mã hóa lại toàn bộ video.
4.  **Tùy chọn nâng cao → Kiểm soát chất lượng video đầu ra**: mặc định 23, có thể giảm xuống 18 hoặc thấp hơn (thấp nhất 0). Càng thấp chất lượng càng cao nhưng dung lượng càng lớn.
5.  **Tùy chọn nâng cao → Mức nén video đầu ra**: mặc định `fast`, có thể chọn slow hoặc slower cho chất lượng cao hơn nhưng lâu hơn.
6.  **Tùy chọn nâng cao → Mã hóa 264/265**: mặc định `264`, chọn 265 sẽ cho chất lượng cao hơn.

### 10. Vì sao video xuất ra dung lượng quá lớn?

1. Đặt **Tùy chọn nâng cao → Kiểm soát chất lượng video đầu ra** thành 25-51. Số càng lớn dung lượng càng nhỏ nhưng chất lượng cũng giảm theo.
2. **Tùy chọn nâng cao → Mã hóa 264/265**: chọn 265, cùng chất lượng thì 265 cho dung lượng nhỏ hơn.

### 11. Cấu hình proxy thế nào?

Một số dịch vụ dịch hoặc lồng tiếng (Google, OpenAI, Gemini) có thể không truy cập trực tiếp được, cần đi qua proxy.

*   **Cách đặt**: điền địa chỉ máy chủ proxy vào ô "Địa chỉ proxy" trên giao diện chính.
*   **Định dạng**: thường là `http://127.0.0.1:10808` (số cổng tùy theo cấu hình phần mềm proxy của bạn).
*   **Lưu ý quan trọng**: nếu bạn không hiểu về proxy hoặc không có proxy khả dụng, **hãy để trống ô này**. Điền sai sẽ gây lỗi.
*   **Các API trong nước không cần proxy**: Baidu, Tencent, Ali, DeepSeek, Zhipu AI, ByteDance... mặc định không đi qua proxy.
*   **Dịch vụ chạy trên máy không cần proxy**: GPT-SoVITS, ChatTTS, F5-TTS... tự động bỏ qua proxy.

### 12. Tùy chỉnh phông chữ, màu sắc, kiểu phụ đề thế nào?

Trên giao diện chính, vào **Thêm cài đặt → Chỉnh kiểu phụ đề cứng**.

---

## Phần 3: Vấn đề nhận dạng giọng nói

### 13. Kết quả nhận dạng rỗng hoặc bị lỗi ký tự

*   **Nguyên nhân**: có thể chọn sai ngôn ngữ, video không có giọng người, hoặc thiếu VRAM
*   **Cách xử lý**:
    1.  Kiểm tra "Ngôn ngữ gốc" đã chọn đúng chưa (đừng phụ thuộc quá vào Auto)
    2.  Kiểm tra video có bị nhạc nền lấn át không (thử bật khử nhiễu)
    3.  Thiếu VRAM: giảm `beam_size`, đổi sang lượng tử `int8`, hoặc dùng mô hình `small`
    4.  Thử đổi kênh nhận dạng (ví dụ từ faster-whisper sang openai-whisper)

### 14. Nhận dạng rất chậm

*   **Nguyên nhân**: dùng mô hình lớn nhưng chưa bật tăng tốc GPU
*   **Cách xử lý**:
    1.  **Bật CUDA**: đảm bảo đã cài CUDA 12.8+ và cuDNN 9.x, rồi tick `Tăng tốc CUDA`
    2.  **Dùng mô hình nhỏ hơn**: đổi `large-v3` thành `medium` hoặc `small`
    3.  **Tối ưu chế độ CPU**: trong tùy chọn nâng cao, đổi `Kiểu dữ liệu tính toán` thành `int8`

### 15. Báo thiếu VRAM hoặc bộ nhớ (`Unable to allocate`, `CUDA out of memory`)

*   **Nguyên nhân**: mô hình quá lớn hoặc VRAM đang bị chương trình khác chiếm
*   **Cách xử lý (theo thứ tự khuyến nghị)**:
    1.  **Dùng mô hình nhỏ hơn**: đổi từ `large-v3` sang `medium`, `small` hoặc `base`. Mô hình `large-v3` cần tối thiểu 8GB VRAM.
    2.  **Chỉnh tùy chọn nâng cao** trong **Công cụ → Tùy chọn nâng cao**:
        *   `Kiểu dữ liệu tính toán`: đổi `float32` thành `float16` hoặc `int8`
        *   `beam_size`: đổi `5` thành `1`
        *   `best_of`: đổi `5` thành `1`
        *   `Nhận biết ngữ cảnh`: đổi `true` thành `false`
    3.  **Kiểm tra nhiều card**: nếu máy có nhiều card đồ họa, kiểm tra xem card thứ nhất có quá ít VRAM không. Phần mềm mặc định dùng card đầu tiên.

### 16. Nhận dạng người nói không chính xác

*   **Nguyên nhân**: mô hình phân tách người nói bị hạn chế ở một số tình huống (nhiều người nói cùng lúc, nhiễu nền lớn)
*   **Cách xử lý**:
    1.  Trong `Thêm cài đặt`, tick `Phân tách người nói` và chỉ định số người
    2.  Trong tùy chọn nâng cao, đổi mô hình phân tách người nói (tích hợp sẵn, Ali CAM++, pyannote)
    3.  Dùng mô hình pyannote thì cần đăng ký token trên HuggingFace và đồng ý thỏa thuận cấp phép

### 17. Tách câu bằng LLM cho kết quả tệ hơn

*   **Nguyên nhân**: mô hình nhỏ chạy cục bộ (như 7B) chưa đủ thông minh, hoặc prompt quá phức tạp
*   **Cách xử lý**:
    1.  Dùng mô hình trực tuyến mạnh hơn (DeepSeek-V3, GPT-4o...)
    2.  Rút gọn prompt (sửa trong `phiendichvideo/prompts/resegment/llm.txt`)
    3.  Khi dùng giọng `clone` để nhân bản giọng gốc, **không nên** dùng tách câu bằng LLM

### 18. Lồng tiếng xong thì phụ đề và tiếng bị lệch

Đây là hiện tượng thường gặp khi dịch và lồng tiếng, do khác biệt độ dài giữa các ngôn ngữ.

*   **Nguyên nhân**: cùng một ý nhưng số âm tiết và cấu trúc ngữ pháp của mỗi ngôn ngữ khác nhau, nên thời lượng đọc khác nhau. Ví dụ một câu tiếng Trung 2 giây, dịch sang tiếng Anh có thể đọc mất 3-4 giây.
*   **Cách xử lý**:
    1.  **Bật tăng tốc âm thanh**: tick `Tăng tốc lồng tiếng`, phần lồng tiếng quá dài sẽ được tăng tốc cho khớp phụ đề
    2.  **Bật làm chậm video**: tick `Làm chậm video` để hình khớp với thời lượng lồng tiếng
    3.  **Bật cả hai**: khi tỉ lệ > 1.2x, tăng tốc âm thanh và làm chậm video mỗi bên gánh một nửa chênh lệch
    4.  **Chỉnh tốc độ đọc**: đặt `Tốc độ lồng tiếng` (ví dụ `+10%`) để đọc nhanh hơn
    5.  **Dùng nhận dạng lần 2**: tick `Nhận dạng lần 2` để tạo dấu thời gian phụ đề chuẩn hơn sau khi lồng tiếng

> Nguyên lý chi tiết xem [Nguyên lý đồng bộ dấu thời gian hình và tiếng](Synchronize.md)

### 19. "Nhận dạng lần 2" là gì? Khi nào cần?

Nhận dạng lần 2 là việc nhận dạng lại chính tệp lồng tiếng vừa tạo, để sinh ra phụ đề có dấu thời gian chuẩn hơn và câu ngắn gọn hơn.

*   **Trường hợp dùng**: khi chọn nhúng phụ đề đơn ngữ (cứng hoặc mềm) và cần phụ đề khớp chính xác với lồng tiếng
*   **Cách bật**: tick `Nhận dạng lần 2`, rồi đặt độ dài đoạn nói dài nhất/ngắn nhất cho lần 2 trong tùy chọn nâng cao
*   **Lưu ý**: nhận dạng lần 2 tốn thêm thời gian xử lý

---

## Phần 4: Vấn đề dịch thuật

### 20. Kết quả dịch có dòng trống hoặc lẫn cả prompt

*   **Nguyên nhân**: mô hình nhỏ chạy cục bộ chưa đủ thông minh, hoặc AI gộp các dòng phụ đề lại
*   **Cách xử lý**:
    1.  Mô hình nhỏ (như 7B) chưa đủ thông minh, nên đổi sang mô hình trực tuyến như DeepSeek/GPT-4
    2.  Bỏ chọn "Gửi toàn bộ phụ đề", chuyển sang dịch theo dòng
    3.  Đặt `trans_thread=1` để giảm số luồng đồng thời
    4.  [Xem nguyên lý và cách khắc phục chi tiết](https://pyvideotrans.com/faq17)

### 21. Dịch bằng AI bị chặn vì vi phạm chính sách nội dung

*   **Thông báo lỗi**: `Nội dung bị AI lọc do vi phạm chính sách`
*   **Nguyên nhân**: nội dung dịch bị hệ thống kiểm duyệt của dịch vụ AI chặn lại
*   **Cách xử lý**:
    1.  Sửa tay phụ đề, bỏ phần nội dung có thể bị chặn
    2.  Đổi kênh dịch (ví dụ từ OpenAI sang DeepSeek)

### 22. Bản dịch không khớp với bản gốc (lệch dòng phụ đề)

*   **Nguyên nhân**: AI gộp các dòng phụ đề khi dịch nên số dòng bị lệch
*   **Cách xử lý**:
    1.  Bỏ chọn "Gửi toàn bộ phụ đề" trong tùy chọn nâng cao
    2.  Đặt số luồng dịch đồng thời bằng 1
    3.  Dùng mô hình AI trực tuyến hỗ trợ ngữ cảnh dài

### 23. Bộ nhớ đệm dịch làm kết quả bất thường

*   **Nguyên nhân**: kết quả dịch đã được lưu đệm, nên sửa prompt hay đổi kênh dịch không có tác dụng
*   **Cách xử lý**:
    1.  Tick tùy chọn `Dọn kết quả đã tạo` trên giao diện chính
    2.  Hoặc xóa tay các tệp đệm trong thư mục `tmp/translate_cache/`

---

## Phần 5: Vấn đề lồng tiếng

### 24. Edge-TTS báo lỗi 403 hoặc tạo ra tiếng câm

*   **Nguyên nhân**: Microsoft giới hạn tần suất do gửi quá nhiều yêu cầu trong thời gian ngắn
*   **Cách xử lý**:
    1.  Trong tùy chọn nâng cao, đặt "Số luồng lồng tiếng đồng thời" bằng 1
    2.  Đặt "Nghỉ sau mỗi yêu cầu lồng tiếng" thành 5-10 giây
    3.  Nếu đang dùng proxy, Edge-TTS có thể lỗi vì proxy. Tạo tệp rỗng tên `edgetts-noproxy.txt` ở thư mục gốc phần mềm để ép bỏ qua proxy

### 25. F5-TTS / CosyVoice / GPT-SoVITS không kết nối được

*   **Nguyên nhân**: dịch vụ TTS cục bộ chưa khởi động hoặc điền sai địa chỉ
*   **Cách xử lý**:
    1.  Đảm bảo cửa sổ dòng lệnh của dịch vụ TTS bên ngoài chưa bị đóng
    2.  Kiểm tra địa chỉ API có đúng không (chú ý số cổng)
    3.  GPT-SoVITS phải khởi động `api.py` hoặc `api_v2.py`, không dùng được cổng 7860 của bản web
    4.  Nếu điền địa chỉ là `0.0.0.0`, hãy đổi thành `127.0.0.1`

### 26. GPT-SoVITS báo lỗi `{"detail":"Not Found"}`

*   **Nguyên nhân**: sai phiên bản API hoặc sai cổng
*   **Cách xử lý**:
    1.  Kiểm tra bạn khởi động `api.py` hay `api_v2.py`, rồi tick đúng tùy chọn `api_v2?` trong phần mềm
    2.  Đảm bảo điền địa chỉ API (mặc định 9880) chứ không phải địa chỉ bản web (7860)

### 27. Index-TTS báo lỗi `Value: 'Same as the voice reference' is not in the list`

*   **Nguyên nhân**: lỗi dịch đa ngôn ngữ không nhất quán bên trong Index-TTS
*   **Cách xử lý**: mở tệp `webui.py` ở thư mục gốc dự án Index-TTS, thay `i18n("与音色参考音频相同")` thành `Same as the voice reference`

### 28. Azure-TTS báo lỗi `Could not find module Microsoft.CognitiveServices.Speech.core.dll`

*   **Nguyên nhân**: thiếu thư viện VC++ Runtime của Microsoft
*   **Cách xử lý**:
    1.  Nếu bạn tải gói vá, hãy tải lại gói đầy đủ
    2.  Nếu đã là gói đầy đủ, cài [bộ VC++ Runtime của Microsoft](https://aka.ms/vs/17/release/vc_redist.x64.exe) rồi khởi động lại máy

### 29. Lồng tiếng xong nghe máy móc hoặc có tạp âm

*   **Nguyên nhân**: tỉ lệ tăng tốc âm thanh quá cao (> 3x), hoặc âm thanh mẫu chất lượng kém
*   **Cách xử lý**:
    1.  Bật làm chậm video để chia sẻ bớt chênh lệch thời lượng với tăng tốc âm thanh
    2.  Nâng chất lượng âm thanh mẫu: dùng tệp WAV 5-10 giây, một giọng, rõ ràng
    3.  Tick `Tách giọng nói/nhạc nền` để loại bỏ tạp âm nền

---

## Phần 6: Vấn đề nhân bản giọng nói

### 30. Lồng tiếng bằng giọng `clone` thất bại hoặc chất lượng kém

*   **Nguyên nhân**: âm thanh mẫu không nằm trong khoảng 3-10 giây, hoặc dấu thời gian phụ đề bị tách câu bằng LLM làm xáo trộn
*   **Cách xử lý**:
    1.  **Không dùng tách câu bằng LLM**: việc này làm xáo trộn dấu thời gian, khiến đoạn âm thanh mẫu bị cắt lệch
    2.  **Ép kiểm soát thời lượng phụ đề**: trong **Tùy chọn nâng cao → Tham số nhận dạng**, đặt `Đoạn nói dài nhất (giây)` thành 6-10, `Đoạn nói ngắn nhất (ms)` thành 3000-4000
    3.  Tick `Gộp phụ đề ngắn` và `Cắt trước âm thanh cho Whisper`
    4.  Dùng kênh `OmniVoice-TTS`, tương thích tốt hơn với âm thanh mẫu ngắn
    5.  Tick `Tách giọng nói/nhạc nền` để nâng chất lượng âm thanh mẫu

### 31. Dùng âm thanh mẫu của riêng mình thế nào?

1.  Thu hoặc cắt một đoạn WAV dài 5-10 giây (một giọng, không tạp âm nền)
2.  Chép tệp đó vào thư mục `f5-tts` trong thư mục phần mềm
3.  Vào **Menu → Cài đặt TTS → Đặt âm thanh mẫu**, điền `tên_tệp.wav#nội dung lời nói trong tệp`
4.  Chọn tên tệp đó trong ô giọng lồng tiếng trên giao diện chính

> **Lưu ý**: âm thanh mẫu của GPT-SoVITS phải đặt ở thư mục gốc của phần mềm GPT-SoVITS, không phải thư mục `f5-tts`.

---

## Phần 7: Vấn đề dựng và xuất video

### 32. Chạy giữa chừng báo lỗi `ffprobe exec error` hoặc lỗi liên quan `ffmpeg`

*   **Nguyên nhân**: đường dẫn tệp quá dài hoặc chứa ký tự đặc biệt
*   **Cách xử lý**:
    1.  Chuyển tệp video sang thư mục nông hơn (ví dụ `D:\videos`)
    2.  Đổi tên thành tên ngắn bằng chữ tiếng Anh hoặc số
    3.  Bỏ ký tự đặc biệt trong tên tệp (`?*`, biểu tượng cảm xúc...)

### 33. Phần mềm báo video "không có luồng âm thanh"

*   **Nguyên nhân 1**: video thật sự không có tiếng (tải từ một số trang web thì hình và tiếng bị tách riêng)
*   **Nguyên nhân 2**: định dạng mã hóa không được hỗ trợ (ví dụ AV1)
*   **Nguyên nhân 3**: tạp âm nền quá lớn, giọng người bị lấn át
*   **Cách xử lý**:
    1.  Mở bằng trình phát để xác nhận có tiếng hay không
    2.  Thử chuyển video sang định dạng chuẩn H.264/MP4 trước
    3.  Bật khử nhiễu hoặc tách giọng nói

### 34. Làm sao xuất video không mất chất lượng?

Video sẽ được xuất không mã hóa lại khi thỏa mãn tất cả điều kiện sau:
1.  Video gốc mã hóa `mp4/h.264/yuv420p`
2.  Trong tùy chọn nâng cao, `Mã hóa 264/265` chọn `264`
3.  Không bật `Làm chậm video`
4.  Không nhúng `phụ đề cứng` (phụ đề mềm không ảnh hưởng)

> Lưu ý: nếu lồng tiếng dài hơn video gốc, phần vượt quá sẽ bị cắt.

### 35. Sau khi xử lý, tiếng, phụ đề và hình không khớp nhau

Đây là hiện tượng bình thường khi dịch giữa các ngôn ngữ.

*   **Nguyên nhân**: cùng một ý nhưng độ dài câu và số âm tiết của mỗi ngôn ngữ khác nhau, nên thời lượng phát âm chắc chắn thay đổi.
*   **Cách xử lý**:
    1.  Bật `Tăng tốc lồng tiếng` và/hoặc `Làm chậm video`
    2.  Đặt `Tốc độ lồng tiếng` (ví dụ `+10%`) để đọc nhanh hơn
    3.  Bật `Nhận dạng lần 2` để có dấu thời gian phụ đề chuẩn hơn
    4.  Nguyên lý chi tiết xem [Nguyên lý đồng bộ dấu thời gian hình và tiếng](Synchronize.md)

### 36. Liên tục báo thiếu VRAM (ví dụ lỗi `Unable to allocate`)

Lỗi này nghĩa là card đồ họa không đủ VRAM hoặc bộ nhớ để chạy tác vụ hiện tại.

*   **Cách xử lý (theo thứ tự khuyến nghị)**:
    1.  **Dùng mô hình nhỏ hơn**: đổi từ `large-v3` sang `medium`, `small` hoặc `base`
    2.  **Chỉnh tùy chọn nâng cao**:
        *   `Kiểu dữ liệu tính toán`: đổi `float32` thành `float16` hoặc `int8`
        *   `beam_size`: đổi `5` thành `1`
        *   `best_of`: đổi `5` thành `1`
        *   `Nhận biết ngữ cảnh`: đổi `true` thành `false`

### 37. Đã cài CUDA rồi nhưng vì sao phần mềm vẫn không dùng được GPU?

Hãy kiểm tra các khả năng sau:

*   **Phiên bản CUDA không tương thích**: phần mềm yêu cầu CUDA từ 12.8 trở lên
*   **Driver card quá cũ**: cập nhật driver NVIDIA lên bản mới nhất
*   **Thiếu cuDNN**: đảm bảo đã cài cuDNN 9.x và cấu hình biến môi trường
*   **Phần cứng không tương thích**: tăng tốc GPU chỉ hỗ trợ card NVIDIA. Card AMD hoặc Intel không dùng được CUDA
*   **Chưa cấu hình biến môi trường**: kiểm tra biến môi trường hệ thống đã có thư mục `bin` và `lib` của CUDA chưa

### 38. Mức sử dụng GPU rất thấp, có bình thường không?

**Bình thường**. Quy trình của phần mềm là: `nhận dạng giọng nói → dịch → lồng tiếng → dựng video`.

Chỉ ở bước đầu tiên — **nhận dạng giọng nói** — mới dùng nhiều GPU. Các bước còn lại (dịch, dựng video) chủ yếu dùng CPU, nên việc GPU nhàn rỗi phần lớn thời gian là đúng như thiết kế.

### 39. Xử lý vài video xong thì ổ cứng đầy?

Thường do bật chức năng "làm chậm video" và sinh ra rất nhiều tệp tạm.

*   **Nguyên nhân**: chức năng này cắt video thành nhiều đoạn nhỏ theo phụ đề rồi xử lý từng đoạn, tạo ra lượng tệp đệm lớn hơn nhiều so với video gốc.
*   **Cách xử lý**:
    1.  **Dọn thủ công**: xử lý xong thì xóa toàn bộ nội dung trong thư mục **`tmp/`** ở thư mục gốc phần mềm
    2.  **Dọn tự động**: khi đóng phần mềm đúng cách, chương trình sẽ tự dọn các tệp đệm này

### 40. Xử lý lại cùng một video, vì sao kết quả nhận dạng và phụ đề luôn không đổi?

*   **Nguyên nhân**: phần mềm mặc định bật cơ chế đệm, nếu phát hiện video đã từng sinh tệp phụ đề thì dùng luôn kết quả đệm
*   **Cách xử lý**: tick ô **`Dọn kết quả đã tạo`** ở góc trên bên trái giao diện chính

---

## Phần 8: Vấn đề xử lý hàng loạt

### 41. Dịch video hàng loạt hay bị treo

Mặc định khi chạy hàng loạt, mỗi tác vụ được chia thành nhiều giai đoạn và chạy đan xen song song. Quá nhiều tác vụ có thể làm cạn tài nguyên.

*   **Cách xử lý**: vào **Tùy chọn nâng cao → Cài đặt chung**, đặt `Số video mỗi đợt dịch` (`batch_nums`) bằng `1` để xử lý lần lượt từng video thay vì chạy song song.

### 42. Kiểm soát số tác vụ chạy đồng thời thế nào?

Trong **Tùy chọn nâng cao → Cài đặt chung**:
*   `Số tác vụ CPU`: số tác vụ CPU chạy đồng thời tối đa, không nên vượt quá số nhân CPU
*   `Số tác vụ GPU`: số tác vụ GPU chạy đồng thời, trừ khi có nhiều card hoặc VRAM > 24G thì hãy đặt 1
*   `Số video mỗi đợt dịch`: đặt 1 để xử lý lần lượt, đặt 0 thì chạy tất cả cùng lúc

---

## Phần 9: Giải thích tùy chọn nâng cao

### 43. Khác nhau giữa tăng tốc âm thanh và làm chậm video?

| Tùy chọn | Tác dụng | Trường hợp dùng |
|------|------|---------|
| **Tăng tốc âm thanh** | Tăng tốc lồng tiếng cho khớp thời lượng phụ đề, chất lượng tiếng có thể giảm nhẹ | Lồng tiếng dài hơn phụ đề 1-2 lần |
| **Làm chậm video** | Làm chậm hình cho khớp thời lượng lồng tiếng, hình có thể hơi giật | Lồng tiếng dài hơn phụ đề trên 2 lần |
| **Bật cả hai** | Mỗi bên gánh một nửa chênh lệch, kết quả tốt nhất | Lồng tiếng dài hơn phụ đề rất nhiều |

### 44. Tùy chọn `Gửi toàn bộ phụ đề` có tác dụng gì?

Khi bật, phần mềm gửi kèm số dòng và dấu thời gian cho AI, chất lượng dịch tốt hơn nhưng AI có thể gộp dòng. Khuyến nghị:
*   **Bật** khi dùng mô hình trực tuyến lớn (DeepSeek, GPT-4o)
*   **Tắt** khi dùng mô hình nhỏ chạy trên máy

### 45. Khác nhau giữa `Nhận dạng lần 2` và `Tách câu bằng LLM`?

| Tùy chọn | Thời điểm | Tác dụng |
|------|------|------|
| **Tách câu bằng LLM** | Sau khi nhận dạng giọng nói | AI sửa lỗi chính tả, chia lại đoạn văn dài |
| **Nhận dạng lần 2** | Sau khi lồng tiếng xong | Nhận dạng lại tệp lồng tiếng để có dấu thời gian chuẩn hơn |

> Khi dùng giọng `clone`, **không nên** dùng tách câu bằng LLM.

### 46. Chọn kiểu nhúng phụ đề thế nào?

| Kiểu | Mô tả | Trường hợp dùng |
|------|------|---------|
| Không nhúng phụ đề | Chỉ thay tiếng, không thêm phụ đề | Chỉ cần lồng tiếng |
| Nhúng phụ đề cứng | Phụ đề khắc vĩnh viễn vào hình, không tắt được | Trình phát nào cũng hiển thị được |
| Nhúng phụ đề mềm | Phụ đề là một luồng riêng, trình phát bật/tắt được | Cần linh hoạt bật tắt phụ đề |
| Phụ đề cứng song ngữ | Phụ đề cứng hai ngôn ngữ | Cần đối chiếu song ngữ |
| Phụ đề mềm song ngữ | Phụ đề mềm hai ngôn ngữ | Cần đối chiếu song ngữ và tắt được |

---

## Phần 10: Vấn đề tệp và đường dẫn

### 47. Đường dẫn tệp đầu vào có yêu cầu gì?

1.  **Độ dài đường dẫn**: dòng lệnh Windows giới hạn 260 ký tự, nên để đường dẫn càng ngắn càng tốt
2.  **Ký tự đặc biệt**: tên tệp không nên chứa `?*`, biểu tượng cảm xúc hay ký tự đặc biệt khác
3.  **Đường dẫn có dấu tiếng Việt**: tuy hỗ trợ nhưng nên dùng đường dẫn không dấu để tránh lỗi tương thích
4.  **Khoảng trắng**: đường dẫn có thể có khoảng trắng nhưng nên tránh

### 48. Tệp kết quả lưu ở đâu?

*   **Mặc định**: thư mục `_video_out/` nằm cùng cấp với video gốc
*   **Các chức năng độc lập**: bóc phụ đề hàng loạt, lồng tiếng, dịch SRT... xuất vào thư mục `output/`
*   **Tùy chỉnh**: có thể đặt thư mục đầu ra trên giao diện chính

### 49. Nhập tệp phụ đề SRT có sẵn thế nào?

1.  Tạo thư mục `_video_out/` cùng cấp với tệp video
2.  Trong đó tạo thư mục con trùng tên video (ví dụ `myvideo-mp4`, bắt buộc kèm phần mở rộng)
3.  Chép tệp phụ đề vào thư mục con, đổi tên thành `zh-cn.srt` (ngôn ngữ nguồn) và `vi.srt` (ngôn ngữ đích)
4.  Nhập video rồi chạy dịch, phần mềm sẽ tự bỏ qua bước nhận dạng và dịch

---

## Phần 11: Vấn đề dòng lệnh (CLI)

### 50. Cách dùng CLI cơ bản

```bash
uv run cli.py --task <loại tác vụ> --name "<đường dẫn tệp>" [tham số khác]
```

Các loại tác vụ: `stt` (nhận dạng giọng nói), `tts` (lồng tiếng), `sts` (dịch phụ đề), `vtv` (dịch video)

### 51. Xem danh sách kênh và ngôn ngữ khả dụng thế nào?

```bash
uv run cli.py --list providers    # xem mọi kênh
uv run cli.py --list languages    # xem mọi mã ngôn ngữ
uv run cli.py --list models       # xem các mô hình faster-whisper
```

### 52. Lỗi CLI thường gặp

*   **`--name is required`**: chưa chỉ định tệp đầu vào
*   **`File not found`**: sai đường dẫn hoặc tệp không tồn tại
*   **`--voice_role is required`**: chế độ TTS bắt buộc phải chỉ định giọng lồng tiếng
*   **`--target_language_code is required`**: chế độ STS/VTV bắt buộc phải chỉ định ngôn ngữ đích

---

## Phần 12: Thông tin chung

### 53. Phần mềm có hỗ trợ triển khai bằng Docker không?

**Có**. Thư mục gốc dự án có sẵn `Dockerfile`, dựng được cả bản CPU lẫn bản GPU:

```bash
docker build -t phiendichvideo-webui .                                  # bản CPU
docker build --build-arg USE_CUDA=true -t phiendichvideo-webui:gpu .    # bản GPU
```

Xem hướng dẫn chi tiết tại [tài liệu WebUI](webui.md).

### 54. Có nhận dạng được phụ đề cứng in trên hình không (chức năng OCR)?

**Không**. Nguyên lý của phần mềm là phân tích **luồng âm thanh** trong video, nhận ra tiếng người rồi chuyển thành văn bản. Phần mềm không có khả năng nhận dạng chữ trong ảnh (OCR).
[Nếu cần, xem một dự án khác chuyên bóc phụ đề cứng trong video](https://pyvideotrans.com/ocrsp)

### 55. Tôi có thể thêm ngôn ngữ mới không?

Có. Xem [hướng dẫn thêm gói ngôn ngữ giao diện](language.md), hoặc [hướng dẫn thêm ngôn ngữ đích của dự án gốc](https://pyvideotrans.com/newlanguage).

### 56. Phần mềm có thu phí không? Có dùng cho mục đích thương mại được không?

*   **Chi phí**: đây là phần mềm **miễn phí và mã nguồn mở**, bạn dùng được mọi chức năng mà không mất phí. Lưu ý rằng nếu bạn dùng dịch vụ dịch, TTS hay nhận dạng của bên thứ ba thì các nhà cung cấp đó có thể thu phí, việc này không liên quan tới phần mềm.
*   **Thương mại**: cá nhân và công ty đều được **tự do sử dụng**. Nhưng nếu bạn muốn tích hợp mã nguồn của dự án này vào sản phẩm thương mại của mình thì phải tuân thủ **giấy phép mã nguồn mở GPL-v3**. Ngoài ra, mô hình hoặc API trực tuyến của một số kênh có thể có điều khoản riêng — có được dùng cho mục đích thương mại hay không, vui lòng hỏi nền tảng tương ứng.

### 57. Có hỗ trợ khách hàng trực tiếp không?

Không. Đây là phần mềm mã nguồn mở miễn phí do cá nhân phát triển, không có lợi nhuận nên không có đội ngũ hỗ trợ riêng. Gặp vấn đề, trước hết hãy đọc kỹ tài liệu này.

### 58. Tải phần mềm và mô hình ở đâu?

*   **Kho mã nguồn của bản Việt hóa này**: [github.com/haianh02034/VideoTrans](https://github.com/haianh02034/VideoTrans)
*   **Trang tải của dự án gốc**: [pyvideotrans.com/downpackage](https://pyvideotrans.com/downpackage)
*   **Kho mã nguồn dự án gốc**: [github.com/jianchang512/pyvideotrans](https://github.com/jianchang512/pyvideotrans)

> Lưu ý: bản dựng sẵn trên trang của dự án gốc **không có phần Việt hóa**. Muốn dùng giao diện tiếng Việt, hãy chạy từ mã nguồn của kho này.

### 59. Báo lỗi và nhật ký

*   **Vị trí nhật ký**: thư mục `logs` ở thư mục gốc phần mềm chứa các tệp `.log` đặt tên theo ngày tháng năm
*   **Cách phản hồi**: khi báo lỗi, bấm "Báo lỗi" trên hộp thoại để mở trang gửi lỗi; hoặc chép 30 dòng cuối nhật ký để hỏi AI

> Lưu ý về quyền riêng tư: nội dung gửi qua nút "Báo lỗi" bao gồm cả đường dẫn cài đặt phần mềm trên máy bạn, và trang đó là diễn đàn công khai của dự án gốc. Bạn vẫn phải bấm nút đăng lần nữa trên trang web thì nội dung mới thực sự được gửi đi.

### 60. Vì sao bản mới không còn "tự động nhận diện" trong danh sách ngôn ngữ nói?

Ở chức năng "Bóc phụ đề hàng loạt" vẫn chọn được "Tự động nhận diện", nhưng chức năng "Dịch video hoặc audio" đã bỏ mục này. Lý do là các bước sau của quy trình dịch video — như dịch phụ đề, lồng tiếng (có liên quan tới âm thanh mẫu) — ở một số kênh bắt buộc phải biết rõ ngôn ngữ gốc, nếu không sẽ báo lỗi. Nếu bạn chỉ muốn bóc phụ đề, hãy dùng riêng chức năng "Bóc phụ đề hàng loạt" ở bảng bên trái.

---

## Bảng tra nhanh

| Vấn đề | Nguyên nhân có thể | Cách xử lý |
|------|---------|---------|
| Phần mềm không khởi động | Bị diệt virus chặn / lỗi đường dẫn | Thêm vào danh sách tin cậy / chuyển sang đường dẫn không dấu |
| Thiếu python310.dll | Chỉ tải gói vá | Tải gói đầy đủ rồi ghi đè gói vá |
| Kết quả nhận dạng rỗng | Chọn sai ngôn ngữ / không có giọng người | Chọn đúng ngôn ngữ / bật khử nhiễu |
| Thiếu VRAM | Mô hình quá lớn | Đổi mô hình nhỏ / dùng int8 / giảm beam_size |
| Không dùng được GPU | Chưa cài CUDA / driver cũ | Cài CUDA 12.8+ / cập nhật driver |
| Bản dịch có dòng trống | AI gộp dòng phụ đề | Bỏ "Gửi toàn bộ phụ đề" / dùng mô hình trực tuyến |
| Edge-TTS lỗi 403 | Microsoft giới hạn tần suất | Giảm số luồng / tăng thời gian nghỉ |
| Tiếng và phụ đề lệch nhau | Khác biệt độ dài giữa các ngôn ngữ | Bật tăng tốc âm thanh / làm chậm video |
| Lỗi ffprobe | Đường dẫn quá dài hoặc có ký tự đặc biệt | Rút gọn tên tệp / chuyển sang thư mục nông |
| Ổ cứng đầy | Làm chậm video sinh nhiều tệp tạm | Dọn thư mục tmp/ |
| Giọng clone kém | Âm thanh mẫu sai độ dài | Giữ 3-10 giây / tắt tách câu bằng LLM |
| GPT-SoVITS lỗi 404 | Sai phiên bản API | Kiểm tra api.py hay api_v2.py |
