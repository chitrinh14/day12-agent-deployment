# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. Ghi trực tiếp OPENAI_API_KEY và DATABASE_URL vào code.

**Hệ quả**: Khi đẩy code lên GitHub, bất kỳ ai cũng có thể thấy và sử dụng Key hoặc truy cập vào database.

2. Các thông số như DEBUG, MAX_TOKENS nằm rải rác trong code.

**Hệ quả**: Mỗi lần muốn đổi thông số lại phải vào sửa code và deploy lại. Rất khó quản lý khi ứng dụng lớn dần.

3. Dùng print() thay về logging để theo dõi.

**Hệ quả**: print() không có timestamp (thời gian), không có level (INFO, ERROR, WARNING). Đặc biệt nguy hiểm khi print cả API Key ra màn hình log.

4. Không có endpoint /health hoặc /ping.

**Hệ quả**: Khi deploy lên các nền tảng như Railway, AWS hay Docker, các hệ thống này cần một endpoint để biết app có đang "sống" hay không. Nếu app bị treo mà không có health check, server sẽ không biết để tự khởi động lại (restart).

5. Gán cứng host="localhost" và port=8000.

**Hệ quả**: `localhost` nghĩa là app chỉ chấp nhận kết nối từ chính nó. Khi đưa lên Cloud, người dùng bên ngoài sẽ không thể truy cập được, gán cứng `port=8000` thì app sẽ không khởi động được trên Cloud.

### Exercise 1.2:

```
[DEBUG] Got question: {"question": "Hello"}
[DEBUG] Using key: sk-hardcoded-fake-key-never-do-this
[DEBUG] Response: Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé.
```

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important? |
|---------|---------|------------|----------------|
| Config  | Hardcode | Env vars | Tránh lộ thông tin nhạy cảm lên GitHub. Có thể dễ dàng thay đổi cấu hình giữa các môi trường (Dev, Staging, Prod) mà không cần phải sửa code hay build lại ứng dụng. |
| Health check | None | Có `/health`, `/ready`  | `/health` báo cho hệ thống biết app còn sống không để tự động restart nếu bị treo.`/ready` báo hiệu app đã khởi tạo xong để tránh việc rớt request của user khi app đang khởi động. |
| Logging | print() | JSON | Dễ dàng theo dõi và phân tích. Các hệ thống quản lý log tập trung có thể tự động parse định dạng JSON thành các trường dữ liệu riêng biệt. |
| Shutdown | Đột ngột | Graceful | Graceful shutdown giúp app dừng nhận request mới, chờ hoàn thành nốt các request đang xử lý dang dở, và đóng kết nối Database an toàn. |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: python:3.11
2. Working directory: 

Working directory được đặt là /app.

3. Tại sao COPY requirements.txt trước?

Tận dụng tính năng layer cache của Docker. Bằng cách copy riêng requirements.txt và chạy pip install trước khi copy phần còn lại của mã nguồn, Docker sẽ lưu lại (cache) lớp cài đặt thư viện này. Nếu lần build sau chỉ sửa code mà không đổi thư viện, Docker sẽ sử dụng lại cache cũ, giúp quá trình build nhanh hơn rất nhiều.

Nếu chạy luôn lệnh pip install sẽ không tìm được file requirements.txt và gặp lỗi

4. CMD vs ENTRYPOINT khác nhau thế nào?

**CMD**: Định nghĩa lệnh và tham số mặc định sẽ được thực thi khi container khởi chạy. Lệnh này rất dễ bị ghi đè. Ví dụ, nếu bạn chạy docker run agent-develop bash, Docker sẽ bỏ qua lệnh python app.py và chạy shell bash thay thế.

**ENTRYPOINT**: Cố định lệnh thực thi chính của container, biến container hoạt động giống như một phần mềm độc lập. Bất kỳ tham số nào bạn thêm vào sau lệnh docker run sẽ được nối thêm vào ENTRYPOINT chứ không ghi đè nó (trừ khi bạn chủ động dùng cờ --entrypoint). Người ta thường dùng ENTRYPOINT cho lệnh khởi chạy chính và dùng CMD để cung cấp các tham số mặc định cho ENTRYPOINT đó.

### Exercise 2.3: Image size comparison
- Develop: 424 MB
- Production: 56.6 MB
- Difference: ~86.65%

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://considerate-insight-production-f96f.up.railway.app
- Screenshot: 

![alt text](image.png)

```
railway logs:
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
Starting Container
INFO:     100.64.0.2:45030 - "GET / HTTP/1.1" 200 OK
INFO:     100.64.0.2:45712 - "GET /docs HTTP/1.1" 200 OK
INFO:     100.64.0.3:13090 - "GET /openapi.json HTTP/1.1" 200 OK
INFO:     100.64.0.4:31498 - "GET /health HTTP/1.1" 200 OK
```

## Part 4: API Security

### Exercise 4.1: API Key authentication
log:
![alt text](image-1.png)
* Không có key
```
{"question":"hello","answer":"Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ OpenAI/Anthropic."}
```
* Có key
```
{"detail":"Invalid API key."}
```

### Exercise 4.2: JWT authentication 
log:
![alt text](image-2.png)
* Lấy token

```
{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHVkZW50Iiwicm9sZSI6InVzZXIiLCJpYXQiOjE3NzY0MjIyNTEsImV4cCI6MTc3NjQyNTg1MX0.AVlL8aiiQcMolH4lG5PR-OxhPN5TNrSnLEN56HT0AQw","token_type":"bearer","expires_in_minutes":60,"hint":"Include in header: Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."}
```

* Dùng token để gọi API

```
{"question":"Explain JWT flow to me","answer":"Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ OpenAI/Anthropic.","usage":{"requests_remaining":9,"budget_remaining_usd":2.2e-05}}
```

### Exercise 4.3: Rate limiting

![alt text](image-3.png)

### Exercise 4.4: Cost guard implementation

Đoạn code thiết lập một hệ thống kiểm soát chi phí đa tầng nhằm bảo vệ tài chính cho dự án AI bằng cách chặn các yêu cầu tốn kém trước khi chúng kịp gửi tới LLM. Cơ chế này vận hành thông qua ba lớp bảo vệ: ngân sách tổng để ngăn chặn rủi ro "cháy túi" toàn hệ thống (trả về lỗi 503), ngân sách cá nhân để đảm bảo sự công bằng giữa các người dùng (trả về lỗi 402), và hệ thống cảnh báo sớm giúp đội ngũ vận hành can thiệp kịp thời khi chi phí sắp chạm ngưỡng. Đây là một cách tiếp cận "thất bại sớm" (fail-fast) chuyên nghiệp, giúp tối ưu hóa ngân sách và tăng cường tính ổn định cho ứng dụng trên môi trường Cloud.

## Part 5: Scaling & Reliability

### Exercise 5.1: Implementation notes

### Exercise 5.2: Graceful shutdown
![alt text](image-4.png)

* Kết luận: Request được hoàn thành xong rồi mới shutdown server.

### Exercise 5.3: Stateless design

### Exercise 5.4: Load balancing

```
(venv) PS C:\Chiiko\Study\AI_Course\day_12_cloud_infrastructure_and_deployment\day12_ha-tang-cloud_va_deployment\05-scaling-reliability\production> docker compose logs agent | Select-String "POST"

agent-3  | INFO:     172.18.0.6:48290 - "POST /ask HTTP/1.1" 200 OK
agent-3  | INFO:     172.18.0.6:48290 - "POST /ask HTTP/1.1" 200 OK
agent-2  | INFO:     172.18.0.6:49786 - "POST /ask HTTP/1.1" 200 OK
agent-2  | INFO:     172.18.0.6:49786 - "POST /ask HTTP/1.1" 200 OK
agent-2  | INFO:     172.18.0.6:49786 - "POST /ask HTTP/1.1" 200 OK
agent-3  | INFO:     172.18.0.6:48290 - "POST /ask HTTP/1.1" 200 OK
agent-3  | INFO:     172.18.0.6:48290 - "POST /ask HTTP/1.1" 200 OK
agent-1  | INFO:     172.18.0.6:37132 - "POST /ask HTTP/1.1" 200 OK
agent-1  | INFO:     172.18.0.6:37132 - "POST /ask HTTP/1.1" 200 OK
agent-1  | INFO:     172.18.0.6:37132 - "POST /ask HTTP/1.1" 200 OK
```

### Exercise 5.5: Test stateless

```
============================================================
Stateless Scaling Demo
============================================================

Session ID: 156bf928-5c41-41dd-aedb-c37999737940

Request 1: [instance-bfc107]
  Q: What is Docker?
  A: Container là cách đóng gói app để chạy ở mọi nơi. Build once, run anywhere!...

Request 2: [instance-623ec9]
  Q: Why do we need containers?
  A: Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ O...

Request 3: [instance-b46f73]
  Q: What is Kubernetes?
  A: Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận....

Request 4: [instance-bfc107]
  Q: How does load balancing work?
  A: Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé....

Request 5: [instance-623ec9]
  Q: What is Redis used for?
  A: Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ O...

------------------------------------------------------------
Total requests: 5
Instances used: {'instance-623ec9', 'instance-b46f73', 'instance-bfc107'}
✅ All requests served despite different instances!

--- Conversation History ---
Total messages: 2
  [user]: What is Kubernetes?...
  [assistant]: Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã đư...

✅ Session history preserved across all instances via Redis!
```