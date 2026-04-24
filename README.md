# Quản Lý Chi Tiêu AI

Ứng dụng quản lý tài chính cá nhân tích hợp AI phân tích điểm mạnh, điểm yếu và đưa ra giải pháp.

## Kiến trúc

```
Front-end/         ← Giao diện web (HTML/CSS/JS)
Backend/           ← API lưu giao dịch (FastAPI + SQLite, port 8000)
AI_backend/        ← AI phân tích (FastAPI + Ollama + Qwen3 + LangChain, port 8001)
```

## Yêu cầu

- Python 3.10+
- [Ollama](https://ollama.com/download) đã cài đặt
- Model Qwen3: `ollama pull qwen3`

## Khởi động nhanh

```bash
bash start.sh
```

Hoặc chạy thủ công từng phần:

```bash
# Terminal 1 – Ollama
ollama serve

# Terminal 2 – Backend
cd Backend && pip install -r requirements.txt && python main.py

# Terminal 3 – AI Backend
cd AI_backend && pip install -r requirements.txt && python main.py

# Mở trình duyệt
# → Front-end/index.html (hoặc dùng Live Server)
```

## Cách dùng AI

Gõ vào ô "Trợ lý AI" ở đầu trang:

| Lệnh | Kết quả |
|------|---------|
| `ăn phở 50k` | Ghi khoản chi, cập nhật dashboard |
| `nhận lương 10 triệu` | Ghi khoản thu |
| `phân tích chi tiêu` | AI phân tích **điểm mạnh / điểm yếu / hướng đi** |
| `tôi tiêu có nhiều không?` | Tư vấn dựa trên dữ liệu thực |

## Ports

| Service | Port |
|---------|------|
| Backend API | 8000 |
| AI Backend (Qwen3) | 8001 |
| Ollama | 11434 |
