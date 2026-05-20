# Low-Level Design (LLD)

## Backend Components
### API Endpoints
- `GET /health`
- `POST /api/v1/chat/message`
- `GET /api/v1/chat/sessions/{session_id}`
- `POST /api/v1/analysis/comprehensive`
- `GET /api/v1/stocks/search`
- `GET /api/v1/stocks/{symbol}/price`
- `POST /api/v1/documents/upload`

### Services
- `OrchestrationService`
- `BedrockService`
- `RAGService`
- `TechnicalAnalysisService`
- `FundamentalAnalysisService`
- `SentimentAnalysisService`
- `SessionService`
- `CacheService`
- `StockDataService`

### Repositories
- `DynamoDBRepository`
- `OpenSearchRepository`
- `S3Repository`

## Data Flow
1. User sends chat request
2. Backend stores user message
3. Orchestrator extracts stock symbol
4. RAG retrieves relevant context
5. Analysis services gather technical/fundamental/sentiment data
6. Bedrock generates grounded response
7. Response stored and returned

## Frontend Components
- Pages: Home, Chat, Analysis, Explore, NotFound
- Chat components: container, input, message, upload
- Analysis components: report, targets, risk, stock search
- Shared state: Zustand stores

## Storage Mapping
- DynamoDB: sessions, messages, document metadata
- S3: raw data lake, uploads, frontend assets
- OpenSearch: vectorized documents
- Redis: cache
