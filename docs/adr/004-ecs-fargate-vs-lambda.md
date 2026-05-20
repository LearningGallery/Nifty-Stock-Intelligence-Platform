# ADR 004: ECS Fargate vs Lambda for Backend Service

**Status:** Accepted

**Date:** 2024-01-15

**Deciders:** Cloud Architect, DevOps Architect

---

## Context

The backend API service needs to:
- Handle chat requests with variable response times (5-30 seconds)
- Maintain WebSocket connections for streaming responses
- Perform complex analysis with multiple service calls
- Support auto-scaling for variable load

---

## Decision

Use **Amazon ECS Fargate** for the backend API service.

**Key Reasons:**

1. **Long-Running Requests**: Stock analysis can take 10-30 seconds
2. **WebSocket Support**: Fargate supports persistent connections
3. **Complex Dependencies**: pandas, ta-lib, transformers libraries
4. **Container Portability**: Easy local development and testing
5. **Memory Requirements**: Analysis requires 2GB+ RAM

---

## Consequences

### Positive
- ✅ No 15-minute Lambda timeout limit
- ✅ Full control over runtime environment
- ✅ Easy local development with Docker
- ✅ Supports streaming responses
- ✅ Predictable performance

### Negative
- ❌ Higher baseline cost (always running)
- ❌ More complex deployment than Lambda
- ❌ Slower cold start than Lambda

---

## Lambda Usage

Lambda is still used for:
- **Data Ingestion**: Event-driven, short-duration tasks
- **ETL Processing**: S3-triggered document processing
- **Scheduled Jobs**: Periodic data refresh

---

## Alternatives Considered

### 1. **AWS Lambda**
- **Pros**: Serverless, pay-per-use, auto-scaling
- **Cons**: 15-min timeout, 10GB memory limit, cold starts
- **Rejected**: Timeout and WebSocket limitations

### 2. **AWS App Runner**
- **Pros**: Simpler than ECS, auto-scaling
- **Cons**: Less control, limited configuration
- **Considered**: Good alternative for simpler use cases

### 3. **EC2 Instances**
- **Pros**: Full control, cost-effective at scale
- **Cons**: Infrastructure management, scaling complexity
- **Rejected**: Too much operational overhead

---

## Configuration

```hcl
task_cpu    = 1024  # 1 vCPU
task_memory = 2048  # 2 GB
desired_count = 2
auto_scaling_min = 1
auto_scaling_max = 10
```

---

## Related ADRs

- [ADR-008: Data Ingestion Pattern](008-data-ingestion-pattern.md)
