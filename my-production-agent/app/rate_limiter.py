import time
import uuid
import redis
from fastapi import HTTPException, status, Depends

from .config import settings
from .auth import verify_api_key

# Khởi tạo kết nối Redis
r = redis.from_url(settings.REDIS_URL, decode_responses=True)

def check_rate_limit(user_id: str = Depends(verify_api_key)):
    """
    Trạm kiểm soát Spam.
    Sử dụng Sliding Window Log với Redis Sorted Set.
    Giới hạn: settings.RATE_LIMIT_PER_MINUTE requests / 1 phút.
    """
    current_time = time.time()
    window_size = 60  # Kích thước cửa sổ là 60 giây (1 phút)
    
    # Tạo key duy nhất cho user này trong Redis
    key = f"rate_limit:{user_id}"
    
    # Tạo ID duy nhất cho request hiện tại (để làm Value trong ZSET)
    request_id = f"{current_time}-{uuid.uuid4()}"

    # Dùng Pipeline để gộp nhiều lệnh Redis chạy cùng 1 lúc (Atomic & Nhanh hơn)
    pipeline = r.pipeline()

    # Bước 1: Xóa tất cả các request cũ nằm ngoài cửa sổ 60s vừa qua
    pipeline.zremrangebyscore(key, 0, current_time - window_size)

    # Bước 2: Thêm request hiện tại vào Sorted Set (với điểm số chính là thời gian hiện tại)
    pipeline.zadd(key, {request_id: current_time})

    # Bước 3: Đếm xem trong cửa sổ hiện tại còn lại bao nhiêu request
    pipeline.zcard(key)

    # Bước 4: Đặt thời gian tự hủy (TTL) cho key để dọn rác Redis nếu user không chat nữa
    pipeline.expire(key, window_size)

    # Thực thi toàn bộ lệnh trong Pipeline
    results = pipeline.execute()

    # result[2] là kết quả của lệnh thứ 3 (zcard - đếm số lượng)
    request_count = results[2]

    # Kiểm tra nếu vượt quá giới hạn
    if request_count > settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Bạn đã thao tác quá nhanh. Giới hạn là {settings.RATE_LIMIT_PER_MINUTE} câu hỏi mỗi phút.",
            headers={"Retry-After": str(window_size)}, # Báo cho Client biết bao lâu nữa mới được gọi lại
        )