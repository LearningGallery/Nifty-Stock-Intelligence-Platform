# API Documentation

## Base URL
- Dev: `https://<alb-or-cloudfront-domain>`
- Local: `http://localhost:8000`

## Health
### `GET /health`
Returns basic health status.

## Chat
### `POST /api/v1/chat/message`
Request:
```json
{
  "session_id": "optional-session-id",
  "message": "Analyze TCS for short term"
}
```

Response:
```json
{
  "session_id": "uuid",
  "message_id": "uuid",
  "content": "AI response",
  "role": "assistant",
  "timestamp": "2024-01-15T10:30:00Z",
  "analysis_data": {},
  "sources": []
}
```

## Analysis
### `POST /api/v1/analysis/comprehensive`
Request:
```json
{
  "stock_symbol": "TCS",
  "analysis_type": "comprehensive",
  "timeframe": "short_term"
}
```

## Stocks
### `GET /api/v1/stocks/search?query=TCS`
### `GET /api/v1/stocks/{symbol}/price`
### `GET /api/v1/stocks/{symbol}/historical`
### `GET /api/v1/stocks/{symbol}/fundamentals`

## Documents
### `POST /api/v1/documents/upload`
Multipart upload for PDF/XLS/XLSX

### `GET /api/v1/documents/status/{document_id}`
Returns processing status

## Auth
Bearer JWT token via Cognito for protected routes.
