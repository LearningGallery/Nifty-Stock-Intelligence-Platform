# ADR 002: RAG Pattern Implementation with OpenSearch

**Status:** Accepted

**Date:** 2024-01-15

**Deciders:** AI Architect, Solutions Architect

---

## Context

The chatbot needs to provide accurate, up-to-date information about Indian stocks, including:
- Latest news articles
- Quarterly financial reports
- Regulatory filings
- Historical price data
- Analyst reports

Direct LLM prompting alone has limitations:
- No access to recent data (training cutoff)
- Potential hallucination on specific facts
- Cannot cite sources

---

## Decision

Implement **Retrieval-Augmented Generation (RAG)** pattern using:
- **Vector Storage**: Amazon OpenSearch Serverless
- **Embeddings**: Amazon Titan Text Embeddings v2
- **Retrieval Strategy**: Semantic search with hybrid filtering
- **Context Window**: Top-5 most relevant documents

---

## Consequences

### Positive
- ✅ LLM responses grounded in actual data
- ✅ Ability to cite sources
- ✅ Up-to-date information (as recent as last ingestion)
- ✅ Reduced hallucination risk
- ✅ Transparency in decision-making

### Negative
- ❌ Increased latency (retrieval + generation)
- ❌ Additional infrastructure cost (OpenSearch)
- ❌ Complexity in document preprocessing
- ❌ Embedding generation cost

### Neutral
- 🔸 Requires continuous data ingestion pipeline
- 🔸 Need to tune retrieval parameters (top-k, similarity threshold)

---

## Implementation Strategy

**Data Flow:**
```
Raw Data → S3 → Lambda ETL → Chunking → Embedding → OpenSearch
                                                            ↓
User Query → Embedding → Semantic Search → Top-K Docs → LLM Prompt
```

**Retrieval Configuration:**
```python
top_k = 5
similarity_threshold = 0.7
chunk_size = 512 tokens
chunk_overlap = 50 tokens
```

---

## Alternatives Considered

### 1. **Direct LLM Prompting (No RAG)**
- **Pros**: Simpler, lower latency, lower cost
- **Cons**: Cannot access recent data, higher hallucination risk
- **Rejected**: Insufficient for financial analysis accuracy

### 2. **Fine-Tuning LLM**
- **Pros**: Model learns domain-specific knowledge
- **Cons**: Expensive, data becomes stale, requires frequent retraining
- **Rejected**: RAG provides better flexibility and freshness

### 3. **Traditional Keyword Search**
- **Pros**: Simpler, faster
- **Cons**: Poor semantic understanding, misses context
- **Rejected**: Semantic search provides better relevance

---

## Related ADRs

- [ADR-001: Bedrock LLM Selection](001-bedrock-llm-selection.md)
- [ADR-003: OpenSearch vs Pinecone](003-opensearch-vs-pinecone.md)

---

## References

- [RAG Pattern Documentation](https://aws.amazon.com/blogs/machine-learning/build-rag-applications/)
- [OpenSearch Vector Search](https://opensearch.org/docs/latest/search-plugins/knn/)
