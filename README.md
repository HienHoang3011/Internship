# ViMind - Nền tảng web AI hỗ trợ tham vấn tâm lý sơ cấp

Đề tài "ViMind" phát triển nền tảng web AI hỗ trợ tham vấn tâm lý sơ cấp 24/7 cho người Việt. Bằng cách ứng dụng kiến trúc Multi-Agent RAG và mô hình LLM tinh chỉnh chuyên biệt để phân rã tác vụ, hệ thống khắc phục triệt để tình trạng cung cấp thông tin sai lệch của AI truyền thống. Mục tiêu cốt lõi là mang đến một công cụ chăm sóc sức khỏe tinh thần an toàn, thấu cảm và chuẩn xác về chuyên môn cho cộng đồng, trường học và doanh nghiệp.

## 🌟 Công Nghệ Sử Dụng

- **Frontend:** React 19, Vite (JavaScript/JSX).
- **Backend Core:** Django 5, Django REST Framework.
- **AI/Agent Layer:** LangChain, LangGraph, Google GenAI, OpenAI. Hệ thống được chia các node cụ thể (như `empathy_node`, `psychoeducation_node`).
- **Database:** PostgreSQL (dữ liệu quan hệ, người dùng, các bài test, lịch sử chat), MongoDB (lưu cở sở tri thức, các bài học tâm lý).
- **Môi trường & Triển khai:** Docker, Docker Compose, `uv` 

---

## ⚙️ Yêu Cầu Hệ Thống

Trước khi bắt đầu, hãy đảm bảo máy tính của bạn đã cài đặt:
- **Docker** và **Docker Compose** (Khuyến khích - để chạy một cách đồng bộ nhất).
- Nếu muốn chạy thủ công (Local Development):
  - Python >= 3.11.
  - Node.js (>= 18) và npm.
  - Công cụ quản lý gói Python `uv` (Cài đặt nhanh: `pip install uv` hoặc xem [hướng dẫn chính thức](https://docs.astral.sh/uv/getting-started/installation/)).
  - PostgreSQL và MongoDB đang chạy trên máy.

---

## 🚀 Hướng Dẫn Cài Đặt và Chạy Dự Án

### Bước Chuẩn Bị (Bắt Buộc): Host Mô Hình LLM
Trước khi chạy ứng dụng, bạn cần cung cấp endpoint mô hình ngôn ngữ (LLM) cho dự án:
1. Mở notebook `SourceCode/notebook/host_llm_ngrok.ipynb`.
2. **Khuyến nghị:** Chạy notebook này trên các môi trường đám mây như **Google Colab** hoặc các nền tảng tương tự có hỗ trợ **GPU A100 trở lên** để đảm bảo tốc độ và hiệu năng sinh văn bản tốt nhất cho hệ thống chat và các service khác.
3. Chạy toàn bộ các cell trong notebook để tải model và khởi chạy server. Sau khi chạy thành công, notebook sẽ cung cấp một đường dẫn public (URL) thông qua ngrok.
4. Copy URL ngrok đó để cấu hình vào file `.env` ở các bước cài đặt bên dưới.

---

### Phương pháp 1: Chạy bằng Docker (Khuyên Dùng)

Đây là cách đơn giản nhất để khởi chạy toàn bộ hệ thống bao gồm cơ sở dữ liệu, backend, agent API và frontend mà không cần phải cài đặt thủ công từng thành phần.

1. **Thiết lập biến môi trường:**
   Mở thư mục `SourceCode`, copy file mẫu `.env.example` thành file `.env` và điền các API key của bạn .
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
3. Cài đặt `uv` (nếu chưa có) và thiết lập môi trường ảo:
   ```bash
   # Cài đặt uv qua pip
   pip install uv
   
   # Tự động tạo môi trường ảo và cài thư viện từ pyproject.toml / uv.lock
   uv sync
   
   # Kích hoạt môi trường ảo:
   # Trên Windows:
   .venv\Scripts\activate
   # Trên macOS/Linux:
   source .venv/bin/activate
   ```
4. Áp dụng migrations cho database và tạo dữ liệu mẫu:
   ```bash
   uv run python manage.py migrate
   uv run python scripts/seed_db.py
   ```
5. Chạy Backend server (Django):
   ```bash
   uv run python manage.py runserver 8000
   ```
6. Mở một terminal mới, chạy Agent layer API:
   ```bash
   uv run python -m app.agents.api
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
