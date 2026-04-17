# ==========================================
# Stage 1: Builder (Cài đặt thư viện)
# ==========================================
FROM python:3.11-slim as builder

WORKDIR /build

# Copy requirements và cài đặt vào thư mục local của user
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ==========================================
# Stage 2: Runtime (Chạy ứng dụng)
# ==========================================
FROM python:3.11-slim

WORKDIR /app

# Chỉ copy những thư viện đã được cài đặt thành công từ Stage 1 sang
COPY --from=builder /root/.local /root/.local

# Copy mã nguồn của ứng dụng
COPY ./app ./app

# Đảm bảo Python nhận diện được các thư viện cài đặt ở local
ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000

# Lệnh khởi động server
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}