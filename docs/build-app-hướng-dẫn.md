# Xây dựng ứng dụng (App) từ Phiên Dịch Video

## Câu hỏi: Project này có thể build thành app không?

**CÓ THỂ.** Project này hoàn toàn có thể build thành file `.exe` (Windows) hoặc ứng dụng độc lập. Ngay từ bây giờ, chính tác giả đã build sẵn bản `.exe` đóng gói sẵn cho Windows trên trang [Releases](https://github.com/jianchang512/pyvideotrans/releases).

---

## 1. Công cụ build có sẵn trong project

Trong file `pyproject.toml` (dòng 172-173) đã có sẵn:

```toml
pyinstaller==6.16.0
pyinstaller-hooks-contrib==2025.8
```

`PyInstaller` là công cụ đóng gói Python app thành file `.exe` độc lập (không cần cài Python).

---

## 2. Các chế độ chạy hiện tại (có thể build app)

| Chế độ | File chính | Loại app |
|--------|-----------|----------|
| **GUI Desktop** (mặc định) | `sp.py` | Ứng dụng desktop PySide6 (Qt) |
| **WebUI** | `webui.py` | Web server dùng Gradio (truy cập qua browser) |
| **CLI** | `cli.py` | Command-line tool (không giao diện) |

---

## 3. Cách build app

### a. Build GUI Desktop App (khuyên dùng)

Sử dụng PyInstaller để đóng gói `sp.py`:

```bash
# Cơ bản
pyinstaller --onefile --windowed --name "PhienDichVideo" sp.py

# Với icon
pyinstaller --onefile --windowed --name "PhienDichVideo" --icon "./phiendichvideo/styles/icon.ico" sp.py

# Thêm dữ liệu kèm theo
pyinstaller --onefile --windowed --name "PhienDichVideo" --icon "./phiendichvideo/styles/icon.ico" --add-data "phiendichvideo:phiendichvideo" sp.py
```

### b. Build WebUI App

Build thành web server độc lập:

```bash
pyinstaller --onefile --name "PhienDichVideo-WebUI" webui.py
```

### c. Build CLI App

```bash
pyinstaller --onefile --name "PhienDichVideo-CLI" cli.py
```

---

## 4. Cấu trúc Spec file (khuyến nghị)

Tạo file `PhienDichVideo.spec` để build chuẩn hơn:

```python
# PhienDichVideo.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['sp.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('phiendichvideo/styles/*', 'phiendichvideo/styles'),
        ('phiendichvideo/language/*', 'phiendichvideo/language'),
        ('phiendichvideo/prompts/**/*', 'phiendichvideo/prompts'),
        ('phiendichvideo/voicejson/*', 'phiendichvideo/voicejson'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'phiendichvideo.ui.dark.darkstyle_rc',
        'phiendichvideo.recognition',
        'phiendichvideo.translator',
        'phiendichvideo.tts',
        'phiendichvideo.process',
        'phiendichvideo.task',
        'phiendichvideo.util',
        'phiendichvideo.mainwin',
        'phiendichvideo.component',
        'phiendichvideo.configure',
        'phiendichvideo.winform',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'PIL'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PhienDichVideo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # False = ẩn cửa sổ console (GUI app), True = hiện console (debug)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='./phiendichvideo/styles/icon.ico',
)
```

Build bằng lệnh:

```bash
pyinstaller PhienDichVideo.spec
```

---

## 5. Lưu ý quan trọng

| Vấn đề | Giải pháp |
|--------|-----------|
| **Kích thước file lớn** (～1-3GB) | Do PyTorch, CUDA, Transformers,... nặng. Có thể dùng `--exclude` để bỏ bớt model không cần thiết |
| **PyTorch + CUDA** | Nếu build trên máy có CUDA, file .exe sẽ yêu cầu CUDA runtime. Cần build với CPU-only PyTorch nếu muốn portable: |
| **Build CPU-only** | `pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu` rồi mới build |
| **Thiếu model files** | Các model như faster-whisper, F5-TTS, CosyVoice sẽ tự động download lần đầu chạy. Không cần nhúng vào installer |
| **ffmpeg** | Phải kèm ffmpeg.exe / ffprobe.exe vào thư mục output hoặc dùng đường dẫn tuyệt đối |

---

## 6. Tóm tắt

| App type | Có thể build? | Công cụ | Độ khó |
|----------|:------------:|---------|:------:|
| GUI Desktop (.exe) | ✅ | PyInstaller | Trung bình |
| WebUI (Gradio server) | ✅ | PyInstaller | Dễ |
| CLI tool | ✅ | PyInstaller | Dễ |
| Docker container | ✅ | Dockerfile (đã có sẵn) | Dễ |
| macOS .app | ✅ | PyInstaller + py2app | Trung bình |
| Linux AppImage | ✅ | PyInstaller + appimagetool | Khó |

---

## Kết luận

Project này **hoàn toàn có thể build thành app** (file .exe cho Windows). 
Tác giả đã tích hợp sẵn **PyInstaller** trong dependencies. 
Cách build đơn giản nhất:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "PhienDichVideo" sp.py
```

File `.exe` sẽ nằm trong thư mục `dist/`.