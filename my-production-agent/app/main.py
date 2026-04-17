# app/main.py
import json
import redis
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

from .config import settings
from .auth import verify_api_key
from .rate_limiter import check_rate_limit
from .cost_guard import check_budget

app = FastAPI(title="Production AI Agent")

# Khởi tạo kết nối Redis toàn cục
# decode_responses=True giúp dữ liệu lấy ra tự động là chuỗi string thay vì dạng bytes
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

# Khai báo cấu trúc dữ liệu đầu vào (Body)
class ChatRequest(BaseModel):
    question: str
    session_id: str = "default_session" # Dùng để phân biệt các cuộc hội thoại khác nhau của cùng 1 user

# ──────────────────────────────────────────────────────────
# Health & Readiness Checks (Dành cho Docker/Kubernetes)
# ──────────────────────────────────────────────────────────

@app.get("/health")
def health():
    """Kiểm tra xem container có đang chạy không."""
    return {"status": "ok", "message": "API is alive"}

@app.get("/ready")
def ready():
    """
    Kiểm tra xem các kết nối phụ trợ (như Redis, Database) đã sẵn sàng chưa.
    Nếu Redis sập, Load Balancer sẽ ngừng gửi request vào node này.
    """
    try:
        redis_client.ping()
        return {"status": "ready", "redis": "connected"}
    except redis.ConnectionError:
        raise HTTPException(status_code=503, detail="Redis connection failed")

# ──────────────────────────────────────────────────────────
# Core Agent Endpoint
# ──────────────────────────────────────────────────────────

@app.post("/ask")
def ask(
    request: ChatRequest,
    user_id: str = Depends(verify_api_key),
    _rate_limit: None = Depends(check_rate_limit),
    _budget: None = Depends(check_budget)
):
    """
    Endpoint chính yếu. Chỉ chạy khi qua được 3 trạm gác: Auth, Rate Limit, Cost Guard.
    """
    # Tạo khóa lưu trữ duy nhất cho cuộc hội thoại này trong Redis
    session_key = f"chat_history:{user_id}:{request.session_id}"
    
    # 1. Lấy lịch sử từ Redis (Stateless)
    history_data = redis_client.get(session_key)
    if history_data:
        history = json.loads(history_data)
    else:
        history = [] # Nếu chưa có, khởi tạo mảng rỗng

    # 2. Gọi LLM (Ở đây chúng ta mock logic LLM)
    # Trong thực tế bạn sẽ nối `history` + `request.question` rồi gửi cho OpenAI/Anthropic
    print(f"Đang xử lý câu hỏi từ {user_id}, số lượng tin nhắn cũ: {len(history)}")
    answer = f"AI xin trả lời: '{request.question}'. (Tài khoản gọi: {user_id})"
    
    # 3. Cập nhật lịch sử mới
    history.append({"role": "user", "content": request.question})
    history.append({"role": "assistant", "content": answer})
    
    # Mẹo tối ưu hóa: Chỉ giữ lại 10 tin nhắn gần nhất để tiết kiệm RAM Redis và chi phí LLM
    history = history[-10:]

    # Lưu lại vào Redis với TTL là 3600 giây (1 tiếng)
    # Sau 1 tiếng không ai chat, cuộc hội thoại sẽ tự động bị xóa
    redis_client.setex(session_key, 3600, json.dumps(history))

    # 4. Trả về response
    return {
        "answer": answer,
        "session_id": request.session_id,
        "history_length": len(history) // 2
    }