# Deployment Information

## Public URL
https://energetic-transformation-production-2b82.up.railway.app

## Platform
Railway

## Test Commands

```
curl.exe -X POST "https://https://energetic-transformation-production-2b82.up.railway.app/ask" `
  -H "x-api-key: sk-mock-key-12345" `
  -H "Content-Type: application/json" `
  -d "{\`"question\`": \`"Xin chào AI, hãy trả lời tôi từ trên mây nhé!\`", \`"session_id\`": \`"phien_bao_cao_01\`"}"
```

### Health Check
```bash
curl.exe "https://energetic-transformation-production-2b82.up.railway.app/health"
# Expected: {"status": "ok"}
