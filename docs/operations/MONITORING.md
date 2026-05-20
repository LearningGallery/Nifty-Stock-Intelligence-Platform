# Monitoring

## Key Metrics
- ECS CPU / Memory
- ALB 5xx errors
- ALB latency
- Lambda errors/duration
- OpenSearch health
- Bedrock invocation failures
- DynamoDB throttles

## Dashboards
CloudWatch dashboard aggregates:
- ECS metrics
- ALB metrics
- recent error logs

## Alerting
SNS-backed alerts for:
- unhealthy targets
- high CPU
- high memory
- Lambda errors
- elevated 5xx responses
