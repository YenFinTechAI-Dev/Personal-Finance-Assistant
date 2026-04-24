import json
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage




app = FastAPI(title="AI Backend qwen2.5:3b / Ollama")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Khởi tạo model Qwen3 qua Ollama ---
llm = ChatOllama(
    model="qwen2.5:3b",
    base_url="http://localhost:11434",
    temperature=0.3,
)

SYSTEM_PROMPT = """Bạn là chuyên gia tài chính cá nhân thông minh. Nhiệm vụ của bạn là giúp người dùng quản lý chi tiêu.

== TRƯỜNG HỢP 1: Người dùng ghi chép giao dịch ==
Ví dụ: "ăn sáng 30k", "mua xăng 50k", "nhận lương 5 triệu"
→ Trả về JSON với amount > 0, type = "Chi" hoặc "Thu", category phù hợp.

Danh mục chuẩn: Ăn uống | Di chuyển | Mua sắm | Hóa đơn | Lương | Giải trí | Y tế | Giáo dục | Khác

== TRƯỜNG HỢP 2: Người dùng hỏi phân tích / tư vấn ==
Ví dụ: "phân tích chi tiêu", "tôi tiêu có nhiều không", "điểm mạnh yếu", "tư vấn tài chính"
→ Dựa vào context dashboard (số liệu thực) để phân tích THEO CẤU TRÚC sau trong trường "note":

**TỔNG QUAN:** [nhận xét nhanh về tình hình tài chính]

** ĐIỂM MẠNH:**
• [điểm mạnh 1 – có số liệu cụ thể]
• [điểm mạnh 2]

**ĐIỂM YẾU:**
• [điểm yếu 1 – có số liệu cụ thể]
• [điểm yếu 2]

**HƯỚNG ĐI & GIẢI PHÁP:**
• [giải pháp cụ thể, khả thi 1]
• [giải pháp cụ thể, khả thi 2]
• [giải pháp 3 nếu cần]

Trả về JSON với amount = 0.

== QUY TẮC QUAN TRỌNG ==
- CHỈ trả về JSON hợp lệ duy nhất, KHÔNG thêm bất kỳ text nào bên ngoài.
- KHÔNG dùng markdown code block (``` json ```).
- Nếu chưa có dữ liệu thì thông báo thân thiện trong "note".

Format JSON bắt buộc:
{
    "amount": <số nguyên>,
    "type": "Chi hoặc Thu",
    "category": "Ăn uống/Di chuyển/Mua sắm/Hóa đơn/Lương/Giải trí/Y tế/Giáo dục/Khác",
    "note": "<ghi chú hoặc phân tích theo cấu trúc>"
}"""


class AIRequest(BaseModel):
    text: str
    context: str = "Chưa có dữ liệu"


@app.get("/")
def home():
    return {
        "status": "online",
        "model": "qwen3",
        "backend": "Ollama + LangChain",
        "port": 8001
    }


@app.get("/health")
async def health_check():
    """Kiểm tra kết nối tới Ollama"""
    try:
        test_messages = [HumanMessage(content="Hi, reply OK")]
        await llm.ainvoke(test_messages)
        return {"status": "ok", "ollama": "connected", "model": "qwen3"}
    except Exception as e:
        return {"status": "error", "message": f"Ollama không phản hồi: {str(e)}"}


@app.post("/api/analyze")
async def analyze_text(request: AIRequest):
    try:
        user_message = (
            f"Ngữ cảnh dashboard hiện tại:\n{request.context}\n\n"
            f"Người dùng nói: {request.text}"
        )

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]

        response = await llm.ainvoke(messages)
        raw_text = response.content.strip()

        # Xóa thẻ <think>...</think> nếu Qwen3 bật chế độ thinking
        raw_text = re.sub(r'<think>.*?</think>', '', raw_text, flags=re.DOTALL).strip()

        # Xóa markdown code fence nếu có
        raw_text = re.sub(r'^```(?:json)?\s*', '', raw_text).strip()
        raw_text = re.sub(r'\s*```$', '', raw_text).strip()

        # Parse JSON
        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                return {
                    "status": "error",
                    "message": "AI trả về định dạng không hợp lệ. Vui lòng thử lại."
                }

        # Đảm bảo amount luôn là số nguyên không âm
        data["amount"] = max(0, int(data.get("amount", 0)))

        return {"status": "success", "data": data}

    except Exception as e:
        return {"status": "error", "message": f"Lỗi xử lý: {str(e)}"}


if __name__ == "__main__":
    print("=" * 50)
    print("  AI Backend – Qwen3 via Ollama + LangChain")
    print("  Đang chạy tại: http://127.0.0.1:8001")
    print("  Yêu cầu: ollama run qwen3")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8001)
