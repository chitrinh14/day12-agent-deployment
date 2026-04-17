# app/auth.py
from fastapi import Header, HTTPException, status
from .config import settings

def verify_api_key(x_api_key: str = Header(..., description="Vui lòng cung cấp API Key hợp lệ")):
    """
    Trạm kiểm soát bảo mật (Authentication Dependency).
    Kiểm tra API Key từ Header của request.
    """
    # 1. So sánh Key khách gửi với Key của hệ thống (trong file .env)
    if x_api_key != settings.AGENT_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai API Key. Từ chối truy cập!",
            # Best practice: Báo cho Client biết cần dùng phương thức xác thực nào
            headers={"WWW-Authenticate": "ApiKey"}, 
        )
    
    # 2. Sinh ra user_id (Mock)
    # Trong thực tế: Bạn sẽ lấy `x_api_key` này đem đi query Database (PostgreSQL/MySQL) 
    # để xem nó thuộc về User nào, rồi trả về ID của User đó.
    # Trong bài Lab này: Chúng ta giả lập một user_id dựa trên 5 ký tự đầu của API Key
    # để có dữ liệu truyền cho trạm Rate Limit và Cost Guard ở phía sau.
    user_id = f"user_{x_api_key[:5]}"
    
    return user_id