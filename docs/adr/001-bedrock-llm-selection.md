# ADR 001: Selection of Amazon Bedrock and Claude 3.5 Sonnet

**Status:** Accepted

**Date:** 2024-01-15

**Deciders:** Solutions Architect, AI Architect

---

## Context

The Nifty Stock Intelligence Platform requires a powerful Large Language Model (LLM) to:
- Analyze complex stock data combining technical, fundamental, and sentiment analysis
- Generate comprehensive, structured investment recommendations
- Maintain conversation context in chatbot interactions
- Provide accurate, data-driven insights with minimal hallucination

---

## Decision

We will use **Amazon Bedrock** with **Claude 3.5 Sonnet** as the primary LLM.

**Key Reasons:**

1. **AWS Native Integration**: Seamless integration with other AWS services (S3, DynamoDB, Lambda)
2. **No Infrastructure Management**: Fully managed service, no model hosting required
3. **Claude 3.5 Sonnet Capabilities**:
   - 200K token context window (sufficient for multi-turn conversations + RAG context)
   - Superior reasoning and analysis capabilities
   - Strong performance on financial and numerical data
   - Lower hallucination rates compared to alternatives
4. **Security & Compliance**: Data doesn't leave AWS environment
5. **Cost Efficiency**: Pay-per-use pricing with no upfront commitments
6. **Embedding Support**: Titan Embeddings for RAG implementation

---

## Consequences

### Positive
- ✅ Reduced operational overhead (no model management)
- ✅ High-quality, accurate analysis outputs
- ✅ Strong AWS ecosystem integration
- ✅ Built-in security and compliance
- ✅ Scalable with zero configuration

### Negative
- ❌ Vendor lock-in to AWS
- ❌ Limited model customization (cannot fine-tune)
- ❌ Dependency on Bedrock availability in region
- ❌ Cost can scale with high usage

### Neutral
- 🔸 Requires careful prompt engineering
- 🔸 Need to monitor token usage for cost optimization
- 🔸 Rate limiting considerations

---

## Alternatives Considered

### 1. **OpenAI GPT-4**
- **Pros**: Excellent performance, widely tested
- **Cons**: Data leaves AWS, higher latency, API rate limits, no embedding model
- **Rejected**: Data sovereignty and integration concerns

### 2. **Self-Hosted Open-Source Models (Llama 2, Mistral)**
- **Pros**: Full control, no vendor lock-in, one-time cost
- **Cons**: Infrastructure management, scaling complexity, performance tuning
- **Rejected**: Operational overhead too high for this project

### 3. **Amazon SageMaker with HuggingFace Models**
- **Pros**: More customization, model fine-tuning possible
- **Cons**: Infrastructure management, higher operational cost
- **Rejected**: Bedrock provides better developer experience for this use case

---

## Implementation Details

**Model Configuration:**
```python
model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
max_tokens = 4096
temperature = 0.7  # Balanced between creativity and consistency
```

**Embedding Model:**
```python
embedding_model_id = "amazon.titan-embed-text-v2:0"
embedding_dimension = 1024
```

---

## Monitoring & Review

- **Performance Metrics**: Response quality, latency, token usage
- **Cost Monitoring**: Monthly Bedrock spending
- **Review Schedule**: Quarterly evaluation of alternative models
- **Trigger for Re-evaluation**: 
  - New models become available in Bedrock
  - Cost exceeds budget by 30%
  - Performance degradation

---

## References

- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Claude 3.5 Sonnet Model Card](https://www.anthropic.com/claude)
- [Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)

---

## Related ADRs

- [ADR-002: RAG Pattern Implementation](002-rag-pattern-implementation.md)
- [ADR-008: Data Ingestion Pattern](008-data-ingestion-pattern.md)
