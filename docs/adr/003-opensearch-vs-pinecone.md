# ADR 003: OpenSearch vs Pinecone for Vector Storage

**Status:** Accepted

**Date:** 2024-01-15

**Deciders:** AI Architect, Cloud Architect

---

## Context

We need a vector database to store document embeddings for RAG (Retrieval-Augmented Generation). Key requirements:
- Store 1024-dimension vectors (Titan Embeddings)
- Semantic search with k-NN
- Handle ~100K documents initially
- Integration with AWS ecosystem
- Cost-effective for portfolio project

### Options Evaluated

1. **Amazon OpenSearch Service**
2. **Pinecone**
3. **pgvector (PostgreSQL extension)**
4. **Chroma (self-hosted)**

---

## Decision

We will use **Amazon OpenSearch Service (with k-NN plugin)**.

---

## Rationale

### Why OpenSearch:

#### ✅ Pros:
1. **AWS Native Integration**
   - Seamless IAM integration
   - VPC endpoint support
   - AWS SDK support
   - CloudWatch monitoring

2. **Cost Transparency**
   - Pay for what you use
   - No per-vector pricing
   - Predictable monthly cost (~$50/month for t3.medium)

3. **Full-Text + Vector Search**
   - Hybrid search capabilities
   - Filter by metadata
   - Traditional text search + semantic search

4. **Data Sovereignty**
   - Data stays in AWS
   - No third-party data sharing

5. **Scalability**
   - Managed service
   - Auto-scaling available
   - Multi-AZ deployment

6. **Portfolio Value**
   - Demonstrates AWS expertise
   - Shows complex service integration

#### ❌ Cons:
- Requires infrastructure management (vs. Pinecone SaaS)
- More complex setup
- Need to manage index optimization

### Why Not Pinecone:

#### ❌ Rejected Because:
1. **Data Leaves AWS**
   - External SaaS dependency
   - Data residency concerns

2. **Cost Model**
   - Per-vector pricing
   - Hidden costs at scale
   - Free tier limitations

3. **Vendor Lock-In**
   - Proprietary API
   - Hard to migrate

4. **Portfolio Perception**
   - Less impressive than AWS-native
   - Doesn't demonstrate cloud architecture skills

### Why Not pgvector:

#### ❌ Rejected Because:
1. Limited vector search optimizations
2. Not designed for high-dimension vectors
3. Requires PostgreSQL expertise
4. Slower than purpose-built solutions

### Why Not Chroma:

#### ❌ Rejected Because:
1. Self-hosting operational overhead
2. No managed service
3. Scaling challenges
4. Less production-ready

---

## Implementation Details

**OpenSearch Configuration:**
```hcl
instance_type = "t3.medium.search"
instance_count = 2  # Multi-AZ
ebs_volume_size = 100 GB
opensearch_version = "2.11"
```

**Index Mapping:**
```json
{
  "settings": {
    "index.knn": true
  },
  "mappings": {
    "properties": {
      "embedding": {
        "type": "knn_vector",
        "dimension": 1024,
        "method": {
          "name": "hnsw",
          "space_type": "cosinesimilarity",
          "engine": "nmslib"
        }
      },
      "content": { "type": "text" },
      "metadata": { "type": "object" }
    }
  }
}
```

---

## Consequences

### Positive:
- ✅ Full AWS stack integration
- ✅ Predictable costs
- ✅ Hybrid search capabilities
- ✅ Data sovereignty
- ✅ Portfolio credibility

### Negative:
- ❌ More infrastructure to manage
- ❌ Initial setup complexity
- ❌ Need to tune performance

### Neutral:
- 🔸 Learning curve for OpenSearch k-NN
- 🔸 Monitor index performance
- 🔸 Implement backup strategy

---

## Cost Analysis

| Service | Monthly Cost (Dev) | Scalability | Vendor Lock-In |
|---------|-------------------|-------------|----------------|
| OpenSearch (t3.medium x2) | ~$100 | High | Medium |
| Pinecone (free tier) | $0 → $70+ | High | High |
| pgvector (RDS) | ~$50 | Medium | Low |
| Chroma (self-hosted) | ~$30 + ops | Low | Low |

**Winner:** OpenSearch (best cost-performance for AWS-native solution)

---

## References

- [OpenSearch k-NN Documentation](https://opensearch.org/docs/latest/search-plugins/knn/)
- [Bedrock + OpenSearch Pattern](https://aws.amazon.com/blogs/machine-learning/build-a-powerful-question-answering-bot-with-amazon-sagemaker-amazon-opensearch-service-streamlit-and-langchain/)

---

## Related ADRs

- [ADR-002: RAG Pattern Implementation](002-rag-pattern-implementation.md)
- [ADR-001: Bedrock LLM Selection](001-bedrock-llm-selection.md)
