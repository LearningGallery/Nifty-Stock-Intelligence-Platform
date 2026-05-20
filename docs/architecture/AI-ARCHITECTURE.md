# AI Architecture

## AI Capabilities
- Conversational stock analysis
- Prompt orchestration
- RAG over uploaded and ingested documents
- Multi-signal synthesis:
  - technical
  - fundamental
  - sentiment
  - retrieved documents

## Model Selection
- **Primary LLM:** Claude 3.5 Sonnet via Amazon Bedrock
- **Embedding Model:** Titan Text Embeddings v2

## Prompting Strategy
### System Prompt
Defines:
- market scope
- response structure
- safety/disclaimer constraints
- hallucination mitigation expectations

### Dynamic Context
Prompt includes:
- recent conversation history
- retrieved RAG chunks
- technical indicators
- fundamental metrics
- sentiment/news summaries

## Hallucination Mitigation
- Retrieve before generate
- cite sources when available
- instruct model to acknowledge uncertainty
- avoid unsupported claims
- keep recommendations bounded and disclaimer-backed

## AI Safety
- No guaranteed returns language
- No advice outside supported stock universe
- Explicit financial disclaimer
- User-uploaded content isolated by metadata/user ownership
