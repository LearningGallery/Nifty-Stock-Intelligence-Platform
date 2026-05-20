# ADR 005: DynamoDB vs RDS for Chat Storage

**Status:** Accepted

**Date:** 2024-01-15

**Deciders:** Cloud Architect, Backend Architect

---

## Context

We need to store chat session data, messages, and conversation history. Key requirements:
- Store chat sessions (user_id, session_id, metadata)
- Store chat messages (session_id, message_id, content, timestamp)
- Fast reads for conversation history
- TTL-based expiration (30 days)
- Scalable for variable load
- Cost-effective

---

## Decision

We will use **Amazon DynamoDB** with on-demand billing.

---

## Rationale

### Why DynamoDB:

#### ✅ Pros:
1. **Serverless & Scalable**
   - No provisioning
   - Auto-scales with load
   - No connection pool limits

2. **Cost-Effective for Variable Load**
   - Pay-per-request model
   - No idle costs
   - Perfect for demo/portfolio

3. **Built-in TTL**
   - Automatic expiration
   - No manual cleanup jobs
   - Reduces storage costs

4. **Single-Digit Millisecond Latency**
   - Fast reads for chat history
   - Consistent performance

5. **Simple Data Model**
   - Key-value access pattern
   - No complex joins needed
   - Schema flexibility

6. **AWS Integration**
   - IAM-based access
   - DynamoDB Streams for triggers
   - CloudWatch metrics

#### ❌ Cons:
- No complex queries (no SQL)
- Need to design partition keys carefully
- Limited transaction support

### Why Not RDS PostgreSQL:

#### ❌ Rejected Because:
1. **Cost**
   - Always running (~$30-50/month minimum)
   - Pay for idle capacity

2. **Operational Overhead**
   - Backups, patches, scaling
   - Connection pooling
   - Performance tuning

3. **Over-Engineering**
   - Don't need ACID transactions
   - Don't need complex JOINs
   - Simple access patterns

4. **Scaling Complexity**
   - Vertical scaling limits
   - Read replicas needed for scale

---

## Data Model

### Tables:

**1. chat-sessions**
```
Partition Key: session_id (String)
Sort Key: created_at (Number - Unix timestamp)
GSI: user_id-created_at-index

Attributes:
- session_id
- user_id
- created_at
- updated_at
- metadata (Map)
- ttl (Number - auto-expiration)
```

**2. chat-messages**
```
Partition Key: session_id (String)
Sort Key: message_id (String)
LSI: session_id-timestamp-index

Attributes:
- session_id
- message_id
- role (user/assistant/system)
- content (String)
- timestamp (Number)
- metadata (Map)
- ttl (Number)
```

**3. document-metadata**
```
Partition Key: document_id (String)
Sort Key: version (Number)
GSI: stock_symbol-ingestion_timestamp-index
GSI: document_type-ingestion_timestamp-index

Attributes:
- document_id
- stock_symbol
- document_type
- ingestion_timestamp
- s3_path
- metadata (Map)
- ttl (Number)
```

---

## Access Patterns

1. **Get chat session by ID:**
   ```
   GetItem: PK=session_id
   ```

2. **Get all messages for session:**
   ```
   Query: PK=session_id, SK begins_with message_
   ```

3. **Get user's sessions:**
   ```
   Query: GSI user_id-created_at-index
   ```

4. **Get documents by stock:**
   ```
   Query: GSI stock_symbol-ingestion_timestamp-index
   ```

---

## Cost Comparison

**Assumptions:** 1000 chat sessions/month, 10 messages per session

| Database | Setup | Monthly Cost | Scaling | Ops |
|----------|-------|--------------|---------|-----|
| DynamoDB (on-demand) | None | ~$5 | Auto | Zero |
| RDS db.t3.micro | Manual | ~$15 | Manual | High |
| RDS db.t3.small | Manual | ~$30 | Manual | High |

**Winner:** DynamoDB (5x cheaper, zero ops)

---

## Implementation Details

**Terraform Configuration:**
```hcl
resource "aws_dynamodb_table" "chat_sessions" {
  name           = "chat-sessions"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "session_id"
  range_key      = "created_at"

  attribute {
    name = "session_id"
    type = "S"
  }

  attribute {
    name = "created_at"
    type = "N"
  }

  attribute {
    name = "user_id"
    type = "S"
  }

  global_secondary_index {
    name            = "user_id-index"
    hash_key        = "user_id"
    range_key       = "created_at"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = true
  }
}
```

---

## Consequences

### Positive:
- ✅ Zero operational overhead
- ✅ Cost-effective (~$5/month)
- ✅ Auto-scaling
- ✅ Built-in TTL
- ✅ Fast performance

### Negative:
- ❌ No SQL queries
- ❌ Limited analytics capabilities
- ❌ Careful key design required

### Mitigation:
- Use DynamoDB Streams → Kinesis → S3 for analytics
- Use DynamoDB PartiQL for simple queries
- Design access patterns upfront

---

## References

- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [DynamoDB TTL](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/TTL.html)

---

## Related ADRs

- [ADR-008: Data Ingestion Pattern](008-data-ingestion-pattern.md)
