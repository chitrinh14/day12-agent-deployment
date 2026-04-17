# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """
    Quản lý toàn bộ cấu hình của hệ thống thông qua biến môi trường.
    Mọi thông số đều có giá trị mặc định để chạy ở môi trường development.
    """
    
    # 1. Cấu hình Server
    PORT: int = Field(default=8000, description="Cổng chạy server (uvicorn)")
    LOG_LEVEL: str = Field(default="INFO", description="Mức độ log (INFO, DEBUG, ERROR)")
    
    # 2. Cấu hình Redis (Bắt buộc cho Stateless design và Rate Limiting)
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0", 
        description="Đường dẫn kết nối Redis"
    )
    
    # 3. Cấu hình Bảo mật (Authentication)
    AGENT_API_KEY: str = Field(
        default="sk-mock-key-12345", 
        description="Khóa API bí mật để bảo vệ endpoint"
    )
    
    # 4. Cấu hình Rate Limiting & Cost Guard (Business Logic)
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=10, 
        description="Số request tối đa mỗi user được phép gọi trong 1 phút"
    )
    MONTHLY_BUDGET_USD: float = Field(
        default=10.0, 
        description="Ngân sách tối đa mỗi user được phép tiêu trong 1 tháng"
    )

    # 5. Load file .env (Rất quan trọng khi code ở máy tính cá nhân)
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Bỏ qua nếu có biến lạ trong file .env
    )

# Khởi tạo đối tượng settings để các file khác import vào dùng
settings = Settings()