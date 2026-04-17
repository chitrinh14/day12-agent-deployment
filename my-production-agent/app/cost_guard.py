# app/cost_guard.py
import datetime
import redis
from fastapi import HTTPException, status, Depends

from .config import settings
from .auth import verify_api_key

# Khởi tạo kết nối Redis
r = redis.from_url(settings.REDIS_URL, decode_responses=True)

def check_budget(user_id: str = Depends(verify_api_key)):
    """
    Trạm kiểm soát Chi phí.
    Tính toán dựa trên tháng hiện tại.
    """
    current_month = datetime.datetime.now().strftime("%Y-%m")
    key = f"budget:{user_id}:{current_month}"

    # 1. Lấy số tiền đã tiêu trong tháng này
    spent = r.get(key)
    current_spent = float(spent) if spent else 0.0

    # 2. Kiểm tra nếu vượt ngân sách
    if current_spent >= settings.MONTHLY_BUDGET_USD:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Ngân sách tháng {current_month} đã cạn. Đã tiêu: ${current_spent:.2f}/${settings.MONTHLY_BUDGET_USD}"
        )

    # 3. Giả lập trừ tiền cho request này (Ví dụ: 0.05$ / request)
    # Trong thực tế, bạn sẽ cộng số tiền này SAU KHI nhận được response từ OpenAI
    estimated_cost_per_request = 0.05
    r.incrbyfloat(key, estimated_cost_per_request)

    # 4. Đặt thời gian sống (TTL) cho dữ liệu này là khoảng 31 ngày
    if not spent:
        r.expire(key, 31 * 24 * 60 * 60)