# Hệ Thống Trợ Lý Ảo Hỗ Trợ Tâm Lý (Psychological Support Chatbot)

Đây là mã nguồn của hệ thống Chatbot/Trợ lý ảo chuyên biệt về tư vấn và hỗ trợ tâm lý. Dự án ứng dụng sức mạnh của các Mô hình Ngôn ngữ Lớn (LLMs) kết hợp với kiến trúc Agentic workflows (sử dụng LangGraph) để mô phỏng quá trình trị liệu, thấu cảm (empathy) và giáo dục tâm lý (psychoeducation) cho người dùng.

## 🌟 Công Nghệ Sử Dụng

- **Frontend:** React 19, Vite (JavaScript/JSX).
- **Backend Core:** Django 5, Django REST Framework.
- **AI/Agent Layer:** LangChain, LangGraph, Google GenAI, OpenAI. Hệ thống được chia các node cụ thể (như `empathy_node`, `psychoeducation_node`).
- **Database:** PostgreSQL (dữ liệu quan hệ, người dùng), MongoDB (lưu trữ lịch sử chat/vector nếu có).
- **Môi trường & Triển khai:** Docker, Docker Compose, `uv` (trình quản lý package Python cực nhanh).

---

## ⚙️ Yêu Cầu Hệ Thống

Trước khi bắt đầu, hãy đảm bảo máy tính của bạn đã cài đặt:
- **Docker** và **Docker Compose** (Khuyến khích - để chạy một cách đồng bộ nhất).
- Nếu muốn chạy thủ công (Local Development):
  - Python >= 3.11.
  - Node.js (>= 18) và npm.
  - Công cụ quản lý gói Python `uv`.
  - PostgreSQL và MongoDB đang chạy trên máy.

---

## 🚀 Hướng Dẫn Cài Đặt và Chạy Dự Án

### Phương pháp 1: Chạy bằng Docker (Khuyên Dùng)

Đây là cách đơn giản nhất để khởi chạy toàn bộ hệ thống bao gồm cơ sở dữ liệu, backend, agent API và frontend mà không cần phải cài đặt thủ công từng thành phần.

1. **Thiết lập biến môi trường:**
   Mở thư mục `SourceCode`, copy file mẫu `.env.example` thành file `.env` và điền các API key của bạn (quan trọng nhất là `GOOGLE_API_KEY` và `OPENAI_API_KEY` nếu hệ thống có yêu cầu).
   ```bash
   cd SourceCode
   cp .env.example .env
   ```

2. **Build và khởi chạy hệ thống:**
   Chạy lệnh sau trong thư mục `SourceCode`:
   ```bash
   docker-compose up --build
   ```
   *Quá trình này có thể mất vài phút ở lần chạy đầu tiên để tải image và cài đặt các dependencies.*

3. **Truy cập ứng dụng:**
   Sau khi terminal báo các service đã chạy thành công, bạn có thể truy cập:
   - **Frontend (Giao diện Chat):** [http://localhost:5173](http://localhost:5173)
   - **Backend API:** [http://localhost:8000](http://localhost:8000)
   - **Agent API:** [http://localhost:8001](http://localhost:8001)

Để dừng hệ thống, nhấn `Ctrl + C` ở terminal, hoặc chạy:
```bash
docker-compose down
```

---

### Phương pháp 2: Chạy trực tiếp trên máy (Local Development)

Dành cho nhà phát triển muốn chỉnh sửa mã nguồn và debug trực tiếp.

**Bước 1: Thiết lập môi trường Python và Backend**
1. Mở terminal tại thư mục `SourceCode`.
2. Tạo file `.env` từ `.env.example` (như ở Phương pháp 1).
3. Sử dụng `uv` để tạo môi trường ảo và cài đặt thư viện nhanh chóng:
   ```bash
   # Tạo môi trường ảo và cài thư viện từ pyproject.toml / uv.lock
   uv sync
   
   # Kích hoạt môi trường ảo:
   # Trên Windows:
   .venv\Scripts\activate
   # Trên macOS/Linux:
   source .venv/bin/activate
   ```
4. Áp dụng migrations cho database và tạo dữ liệu mẫu:
   ```bash
   python manage.py migrate
   python scripts/seed_db.py
   ```
5. Chạy Backend server (Django):
   ```bash
   python manage.py runserver 8000
   ```
6. Mở một terminal mới (nhớ kích hoạt môi trường `.venv`), chạy Agent layer API:
   ```bash
   python -m app.agents.api
   ```

**Bước 2: Cài đặt và chạy Frontend**
1. Mở terminal mới, di chuyển vào thư mục `frontend`:
   ```bash
   cd SourceCode/frontend
   ```
2. Cài đặt các thư viện Node.js:
   ```bash
   npm install
   ```
3. Khởi chạy máy chủ phát triển Vite:
   ```bash
   npm run dev
   ```
4. Truy cập giao diện ứng dụng tại `http://localhost:5173`.

---

## 📂 Cấu Trúc Mã Nguồn Chính

- `SourceCode/app/`: Chứa logic chính của ứng dụng Django Backend và logic AI Agents.
  - `app/agents/`: Mã nguồn của LangGraph, định nghĩa các luồng xử lý (nodes/edges) như giáo dục tâm lý, thấu cảm người dùng.
- `SourceCode/frontend/`: Chứa mã nguồn giao diện người dùng ReactJS, bao gồm màn hình `ChatScreen.jsx` và các file styling.
- `SourceCode/docker-compose.yml`: Khai báo 5 dịch vụ (db, mongo, backend, agent, frontend).
- `SourceCode/pyproject.toml` & `uv.lock`: Quản lý các dependencies của Python bằng công cụ hiện đại `uv`.
