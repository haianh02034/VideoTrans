# Hướng dẫn cài đặt Whisper.NET

## Đây là gì?

Whisper.NET là một công cụ nhận dạng giọng nói, cho phép card đồ họa AMD của bạn tăng tốc nhận dạng qua Vulkan (không cần CUDA của NVIDIA).

## Dùng cho ai

Phù hợp với người dùng **Windows + card AMD**.

**Bối cảnh**: khi dùng Whisper.cpp, tác giả phát hiện bản mới nhất đã bỏ hỗ trợ GPU AMD trên Windows, khiến người dùng Windows + card AMD chỉ nhận dạng được bằng CPU, rất chậm. Sau khi tham khảo và trao đổi với AI, hướng kỹ thuật Whisper.NET được chọn và triển khai với sự hỗ trợ lập trình của AI.

**Môi trường đã thử nghiệm**: hiện mới chỉ chạy thử thành công trên **Windows 11 23H2 + RX 6650 XT**. Các môi trường khác có thể cần bạn tự kiểm tra, rất mong nhận được phản hồi.

---

## Bước 1: Tải các tệp DLL

### Danh sách tệp cần tải

**DLL quản lý** (tải xong đặt vào thư mục `deps/`):

| Tên tệp | Phiên bản | Liên kết tải |
|--------|------|----------|
| Whisper.net.dll | 1.9.0 | [Tải về](https://www.nuget.org/packages/Whisper.net/1.9.0) |
| Microsoft.Extensions.AI.Abstractions.dll | 10.0.0 | [Tải về](https://www.nuget.org/packages/Microsoft.Extensions.AI.Abstractions/10.0.0) |
| Microsoft.Bcl.AsyncInterfaces.dll | 10.0.0 | [Tải về](https://www.nuget.org/packages/Microsoft.Bcl.AsyncInterfaces/10.0.0) |
| System.Memory.dll | 4.6.3 | [Tải về](https://www.nuget.org/packages/System.Memory/4.6.3) |
| System.Buffers.dll | 4.6.1 | [Tải về](https://www.nuget.org/packages/System.Buffers/4.6.1) |
| System.Runtime.CompilerServices.Unsafe.dll | 6.1.2 | [Tải về](https://www.nuget.org/packages/System.Runtime.CompilerServices.Unsafe/6.1.2) |
| System.Numerics.Vectors.dll | 4.6.1 | [Tải về](https://www.nuget.org/packages/System.Numerics.Vectors/4.6.1) |

**DLL gốc (native)** (tải xong đặt vào thư mục `deps/native/`):

Tải từ [Whisper.net.Runtime.Vulkan 1.9.0](https://www.nuget.org/packages/Whisper.net.Runtime.Vulkan/1.9.0), giải nén rồi chép **toàn bộ tệp DLL** trong thư mục `build/win-x64/` vào `deps/native/`.

Gói NuGet chứa các tệp sau (cần đủ tất cả):

| Tên tệp | Kích thước | Công dụng |
|--------|------|------|
| whisper.dll | 473KB | Lõi nhận dạng giọng nói |
| libwhisper.dll | 473KB | Bí danh của whisper.dll (bắt buộc) |
| ggml-whisper.dll | 66KB | Thư viện tính toán |
| libggml-whisper.dll | 66KB | Bí danh của ggml-whisper.dll |
| ggml-base-whisper.dll | 528KB | Thư viện nền (phụ thuộc bắt buộc) |
| libggml-base-whisper.dll | 528KB | Bí danh của ggml-base-whisper.dll |
| ggml-cpu-whisper.dll | 590KB | Chạy dự phòng bằng CPU |
| libggml-cpu-whisper.dll | 590KB | Bí danh của ggml-cpu-whisper.dll |
| ggml-vulkan-whisper.dll | 45MB | Tăng tốc GPU (Vulkan) |
| libggml-vulkan-whisper.dll | 45MB | Bí danh của ggml-vulkan-whisper.dll |

### Tải từ NuGet thế nào?

1. Bấm liên kết ở trên để mở trang NuGet
2. Bấm **"Download package"** để tải tệp `.nupkg`
3. Đổi phần mở rộng `.nupkg` thành `.zip` rồi mở bằng phần mềm giải nén
4. Tìm các tệp DLL bên trong:
   - DLL quản lý nằm trong thư mục `lib/netstandard2.0/`
   - DLL gốc nằm trong thư mục `build/win-x64/`

---

## Bước 2: Tải mô hình nhận dạng

Tải tệp mô hình định dạng `.bin` từ [ggerganov/whisper.cpp models](https://github.com/ggerganov/whisper.cpp/tree/master/models) rồi đặt vào thư mục `models/`.

Ví dụ tải: `ggml-large-v3-turbo.bin` (chất lượng tốt, tốc độ nhanh)

---

## Bước 3: Kiểm tra cấu trúc thư mục

Đảm bảo cấu trúc thư mục của bạn như sau:

```
VideoTrans/
├─ models/
│  └─ ggml-large-v3-turbo.bin    ← mô hình nhận dạng
└─ deps/
   ├─ Whisper.net.dll            ← 7 tệp dưới đây là DLL quản lý
   ├─ Microsoft.Extensions.AI.Abstractions.dll
   ├─ Microsoft.Bcl.AsyncInterfaces.dll
   ├─ System.Memory.dll
   ├─ System.Buffers.dll
   ├─ System.Runtime.CompilerServices.Unsafe.dll
   ├─ System.Numerics.Vectors.dll
   └─ native/                     ← chép toàn bộ DLL trong build/win-x64/ của gói NuGet vào đây
      ├─ whisper.dll
      ├─ libwhisper.dll
      ├─ ggml-whisper.dll
      ├─ libggml-whisper.dll
      ├─ ggml-base-whisper.dll
      ├─ libggml-base-whisper.dll
      ├─ ggml-cpu-whisper.dll
      ├─ libggml-cpu-whisper.dll
      ├─ ggml-vulkan-whisper.dll
      └─ libggml-vulkan-whisper.dll
```

---

## Bước 4: Bắt đầu dùng

0. Triển khai dự án từ mã nguồn, chạy `uv sync --all-extras`. Nếu đã cài rồi thì chạy riêng `uv sync --extra dotnet` để cài mô-đun `pythonnet`
1. Chạy `uv run sp.py` để mở phần mềm
2. Ở ô "Kênh nhận dạng", chọn **"Whisper.NET"**
3. Chọn tệp mô hình bạn đã tải
4. Bấm bắt đầu

---

## Gặp vấn đề?

### Báo "Native Library not found" hoặc mã lỗi `0x8007007E`

- Kiểm tra thư mục `deps/native/` có đủ 10 tệp DLL không
- Kiểm tra tên tệp có đúng không

### Tăng tốc GPU không hoạt động

- Cập nhật driver card đồ họa
- Card AMD phải hỗ trợ Vulkan (dòng RX 400 trở lên)
- Card NVIDIA phải từ dòng GTX 600 trở lên

### Báo lỗi khởi tạo pythonnet

- Cài [.NET Runtime](https://dotnet.microsoft.com/download/dotnet) (chọn bản .NET 8 hoặc .NET 9 mới nhất)

### Muốn kiểm tra card có hỗ trợ Vulkan không

Mở cửa sổ dòng lệnh và gõ:
```
vulkaninfo
```
Nếu hiện thông tin card đồ họa nghĩa là có hỗ trợ.

---

# Whisper.NET Setup Guide

## What is this?

Whisper.NET is a speech recognition engine that uses Vulkan acceleration for AMD GPUs (no NVIDIA CUDA required).

## Use Case

Designed for **Windows + AMD GPU** users.

**Background**: While using Whisper.cpp, I discovered that the latest version no longer provides AMD GPU support on Windows. This means Windows + AMD GPU users can only use CPU for speech recognition, which is very slow. After consulting and discussing with AI, I chose the Whisper.NET approach and implemented it with AI assistance.

**Tested Environment**: Currently only tested on **Windows 11 23H2 + RX 6650 XT**. Other environments may need further testing. Feedback is welcome.

---

## Step 1: Download DLL Files

### Required Files

**Managed DLLs** (place in `deps/` folder):

| File | Version | Download Link |
|------|---------|---------------|
| Whisper.net.dll | 1.9.0 | [Download](https://www.nuget.org/packages/Whisper.net/1.9.0) |
| Microsoft.Extensions.AI.Abstractions.dll | 10.0.0 | [Download](https://www.nuget.org/packages/Microsoft.Extensions.AI.Abstractions/10.0.0) |
| Microsoft.Bcl.AsyncInterfaces.dll | 10.0.0 | [Download](https://www.nuget.org/packages/Microsoft.Bcl.AsyncInterfaces/10.0.0) |
| System.Memory.dll | 4.6.3 | [Download](https://www.nuget.org/packages/System.Memory/4.6.3) |
| System.Buffers.dll | 4.6.1 | [Download](https://www.nuget.org/packages/System.Buffers/4.6.1) |
| System.Runtime.CompilerServices.Unsafe.dll | 6.1.2 | [Download](https://www.nuget.org/packages/System.Runtime.CompilerServices.Unsafe/6.1.2) |
| System.Numerics.Vectors.dll | 4.6.1 | [Download](https://www.nuget.org/packages/System.Numerics.Vectors/4.6.1) |

**Native DLLs** (place in `deps/native/` folder):

Download from [Whisper.net.Runtime.Vulkan 1.9.0](https://www.nuget.org/packages/Whisper.net.Runtime.Vulkan/1.9.0), extract and copy **all DLL files** from `build/win-x64/` folder to `deps/native/`.

The NuGet package contains these files (all required):

| File | Size | Purpose |
|------|------|---------|
| whisper.dll | 473KB | Speech recognition core |
| libwhisper.dll | 473KB | Alias for whisper.dll (required) |
| ggml-whisper.dll | 66KB | Compute library |
| libggml-whisper.dll | 66KB | Alias for ggml-whisper.dll |
| ggml-base-whisper.dll | 528KB | Base library (required dependency) |
| libggml-base-whisper.dll | 528KB | Alias for ggml-base-whisper.dll |
| ggml-cpu-whisper.dll | 590KB | CPU backend |
| libggml-cpu-whisper.dll | 590KB | Alias for ggml-cpu-whisper.dll |
| ggml-vulkan-whisper.dll | 45MB | GPU acceleration (Vulkan) |
| libggml-vulkan-whisper.dll | 45MB | Alias for ggml-vulkan-whisper.dll |

### How to download from NuGet?

1. Click the download link above to open the NuGet page
2. Click **"Download package"** to download the `.nupkg` file
3. Rename the `.nupkg` file extension to `.zip` and open with any archive tool
4. Find the DLL files inside:
   - Managed DLLs are in `lib/netstandard2.0/` folder
   - Native DLLs are in `build/win-x64/` folder

---

## Step 2: Download Speech Model

Download `.bin` format model files from [ggerganov/whisper.cpp models](https://github.com/ggerganov/whisper.cpp/tree/master/models) and place them in the `models/` folder.

Recommended: `ggml-large-v3-turbo.bin` (good quality, fast)

---

## Step 3: Verify File Structure

Make sure your directory structure looks like this:

```
VideoTrans/
├─ models/
│  └─ ggml-large-v3-turbo.bin    ← Speech model
└─ deps/
   ├─ Whisper.net.dll            ← Managed DLLs (7 files)
   ├─ Microsoft.Extensions.AI.Abstractions.dll
   ├─ Microsoft.Bcl.AsyncInterfaces.dll
   ├─ System.Memory.dll
   ├─ System.Buffers.dll
   ├─ System.Runtime.CompilerServices.Unsafe.dll
   ├─ System.Numerics.Vectors.dll
   └─ native/                     ← Copy all DLLs from build/win-x64/ here
      ├─ whisper.dll
      ├─ libwhisper.dll
      ├─ ggml-whisper.dll
      ├─ libggml-whisper.dll
      ├─ ggml-base-whisper.dll
      ├─ libggml-base-whisper.dll
      ├─ ggml-cpu-whisper.dll
      ├─ libggml-cpu-whisper.dll
      ├─ ggml-vulkan-whisper.dll
      └─ libggml-vulkan-whisper.dll
```

---

## Step 4: Start Using

1. Open Phiên Dịch Video
2. Select **"Whisper.NET"** from the speech recognition dropdown
3. Choose your downloaded model file
4. Click Start

---

## Troubleshooting

### "Native Library not found" or error code `0x8007007E`

- Check if `deps/native/` folder contains all 10 DLL files
- Verify file names are correct

### GPU acceleration not working

- Update your graphics driver
- AMD GPUs require Vulkan support (RX 400 series or newer)
- NVIDIA GPUs require GTX 600 series or newer

### pythonnet initialization failed

- Install [.NET Runtime](https://dotnet.microsoft.com/download/dotnet) (choose the latest .NET 8 or .NET 9)

### Check if your GPU supports Vulkan

Open command line and run:
```
vulkaninfo
```
If it displays your GPU information, Vulkan is supported.