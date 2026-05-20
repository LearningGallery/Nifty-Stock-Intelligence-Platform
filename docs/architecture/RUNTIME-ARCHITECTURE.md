# Runtime Architecture

## Runtime Path
1. Browser loads SPA from CloudFront
2. SPA calls backend via ALB/API path
3. Backend authenticates user (optional Cognito)
4. Backend orchestrates:
   - cache lookup
   - retrieval
   - analysis
   - Bedrock invocation
5. Response returned to frontend
6. Logs/metrics emitted to CloudWatch

## Runtime Components
- CloudFront
- S3 frontend
- ALB
- ECS Fargate backend
- Redis cache
- DynamoDB
- OpenSearch
- Bedrock
- CloudWatch / X-Ray

## Failure Handling
- fallback to partial analysis if one analysis module fails
- retry external API fetches
- return graceful error if Bedrock unavailable
- cache recent successful responses
