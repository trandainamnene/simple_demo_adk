## my_agent – Gemini ADK Python agent

Đây là dự án mẫu dùng **Agent Development Kit (ADK) cho Python** để xây dựng một agent đơn giản trả lời giờ hiện tại của một thành phố, dựa trên hướng dẫn từ tài liệu ADK Python Quickstart (`https://google.github.io/adk-docs/get-started/python/`).

### 1. Yêu cầu hệ thống

- **Python**: 3.10 trở lên  
- **pip**: đã cài sẵn  
- Khuyến nghị: dùng **virtual environment** (`.venv`)

### 2. Cài đặt môi trường

Từ thư mục gốc dự án:

```powershell
# Tạo và kích hoạt virtual environment (Windows PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# Cài ADK (nếu chưa cài)
pip install google-adk python-dotenv
```

### 3. Cấu hình API key

Project sử dụng **Gemini API** nên cần API key:

1. Tạo API key trong Google AI Studio (trang API Keys).  
2. Tạo file `.env` trong thư mục gốc dự án với nội dung:

```env
GOOGLE_API_KEY=YOUR_API_KEY_HERE
```

Lưu ý:
- File phải được lưu với **encoding UTF-8 (không BOM)**.
- Không có dấu ngoặc kép bao quanh giá trị (không viết `"YOUR_API_KEY"`).

### 4. Cấu trúc dự án

```text
my_agent/
  agent.py       # code chính của agent (root_agent)
  __init__.py    # đánh dấu package Python
  .env           # chứa GOOGLE_API_KEY (không commit lên GitHub)
```

Trong `agent.py`, agent được định nghĩa bằng `google.adk.agents.llm_agent.Agent` với tool mẫu `get_current_time`.

### 5. Chạy agent bằng CLI

Từ thư mục **cha** chứa `my_agent/`:

```powershell
# Đảm bảo lệnh `adk` có trong PATH
$env:Path += ";$env:USERPROFILE\AppData\Roaming\Python\Python313\Scripts"

# Chạy agent ở chế độ CLI
adk run my_agent
```

### 6. Chạy agent bằng Web UI (ADK Web)

Từ thư mục **cha** chứa `my_agent/`:

```powershell
adk web --port 8000
```

Sau đó mở trình duyệt và truy cập:

- `http://localhost:8000`

Chọn agent `my_agent` ở góc trên bên trái và chat với agent.

> Lưu ý: ADK Web chỉ dùng cho phát triển và debug, **không dùng cho production** (theo khuyến cáo trong tài liệu ADK).

### 7. Ghi chú về lỗi thường gặp

- **`adk : The term 'adk' is not recognized...`**  
  - Nguyên nhân: thư mục `Scripts` của Python (chứa `adk.exe`) chưa nằm trong `PATH`.  
  - Cách khắc phục (tạm thời trong PowerShell):
    ```powershell
    $env:Path += ";$env:USERPROFILE\AppData\Roaming\Python\Python313\Scripts"
    ```

- **`'utf-8' codec can't decode byte 0xff in position 0...` khi đọc `.env`**  
  - Nguyên nhân: file `.env` lưu với UTF-16 (có BOM 0xFF 0xFE).  
  - Cách khắc phục: mở `.env` bằng editor, chọn **Save with encoding → UTF-8 (no BOM)**.

- **`Missing key inputs argument! To use the Google AI API, provide (api_key)...`**  
  - Nguyên nhân: biến môi trường `GOOGLE_API_KEY` không load được (sai tên key, sai encoding, có BOM).  
  - Cách khắc phục:
    - Đảm bảo `.env` có dòng:
      ```env
      GOOGLE_API_KEY=YOUR_API_KEY_HERE
      ```
    - Đảm bảo encoding UTF-8 không BOM.

### 8. Hướng dẫn push lên GitHub

1. Khởi tạo git (nếu chưa có):

```powershell
git init
git add .
git commit -m "Initial commit: Gemini ADK my_agent"
```

2. Tạo repository mới trên GitHub (ví dụ: `my_agent`) và lấy URL dạng:

```text
https://github.com/<username>/my_agent.git
```

3. Thêm remote và push:

```powershell
git remote add origin https://github.com/<username>/my_agent.git
git branch -M main
git push -u origin main
```

> Đừng quên thêm `.env` vào `.gitignore` để không push API key lên GitHub.


