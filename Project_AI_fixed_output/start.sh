#!/bin/bash


echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   Quản Lý Chi Tiêu AI – Khởi động hệ thống  ║"
echo "╚══════════════════════════════════════════════╝"
echo ""


echo "Kiểm tra Ollama..."
if ! command -v ollama &> /dev/null; then
    echo " Ollama chưa được cài. Tải tại: https://ollama.com/download"
    exit 1
fi

# Kéo model Qwen3 nếu chưa có
echo "Đảm bảo model qwen3 đã được tải..."
ollama pull qwen3

# Chạy Ollama server nền
echo "Khởi động Ollama server..."
ollama serve &> /tmp/ollama.log &
sleep 2
echo "   Ollama đang chạy (port 11434)"


echo ""
echo "Khởi động Backend API (port 8000)..."
cd Backend
pip install -r requirements.txt -q
python main.py &
BACKEND_PID=$!
cd ..
sleep 1
echo "   Backend đang chạy (PID $BACKEND_PID)"


echo ""
echo "Khởi động AI Backend – Qwen3 (port 8001)..."
cd AI_backend
pip install -r requirements.txt -q
python main.py &
AI_PID=$!
cd ..
sleep 1
echo "   AI Backend đang chạy (PID $AI_PID)"


echo ""
echo "Mở giao diện web..."
if command -v xdg-open &> /dev/null; then
    xdg-open "Front-end/index.html"
elif command -v open &> /dev/null; then
    open "Front-end/index.html"
else
    echo "   → Mở thủ công: Front-end/index.html"
fi

echo ""
echo "════════════════════════════════════════════"
echo "  Backend API  : http://127.0.0.1:8000"
echo "  AI Backend   : http://127.0.0.1:8001"
echo "  Ollama       : http://localhost:11434"
echo "  Nhấn Ctrl+C để dừng tất cả"
echo "════════════════════════════════════════════"
echo ""


wait
