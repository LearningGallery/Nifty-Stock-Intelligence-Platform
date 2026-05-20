# Operations Runbook

Operational procedures and day-to-day management guide for the Nifty Stock Intelligence Platform.

---

## Table of Contents

1. [Daily Operations](#daily-operations)
2. [Monitoring & Alerts](#monitoring--alerts)
3. [Incident Response](#incident-response)
4. [Maintenance Procedures](#maintenance-procedures)
5. [Backup & Recovery](#backup--recovery)
6. [Scaling Operations](#scaling-operations)
7. [Security Operations](#security-operations)
8. [Cost Management](#cost-management)

---

## Daily Operations

### Morning Health Check (5 minutes)

```bash
#!/bin/bash
# daily-health-check.sh

export AWS_REGION="ap-south-1"
export CLUSTER_NAME="nifty-stock-intel-dev-cluster"
export SERVICE_NAME="nifty-stock-intel-dev-backend"

echo "=== Daily Health Check ==="
date

# 1. Check ECS Service Health
echo "\n1. ECS Service Status:"
aws ecs describe-services \
  --cluster ${CLUSTER_NAME} \
  --services ${SERVICE_NAME} \
  --query 'services[0].[serviceName,status,runningCount,desiredCount]' \
  --output table

# 2. Check API Health
echo "\n2. API Health:"
curl -s https://your-alb-dns.ap-south-1.elb.amazonaws.com/health | jq

# 3. Check OpenSearch Cluster
echo "\n3. OpenSearch Status:"
curl -s -u admin:password https://your-opensearch-endpoint/_cluster/health | jq '.status'

# 4. Check Lambda Function Errors (last 24h)
echo "\n4. Lambda Errors (24h):"
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=nsip-ingestor \
  --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Sum \
  --region ${AWS_REGION}

# 5. Check Recent Deployments
echo "\n5. Recent Task Definitions:"
aws ecs list-task-definitions --family-prefix ${SERVICE_NAME} --max-items 3 --region ${AWS_REGION}

# 6. Cost Check (MTD)
echo "\n6. Cost This Month:"
aws ce get-cost-and-usage \
  --time-period Start=$(date -u +%Y-%m-01),End=$(date -u +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --region us-east-1

echo "\n=== Health Check Complete ==="
```

### Weekly Checks

**Every Monday (15 minutes):**

1. **Review CloudWatch Alarms**
   ```bash
   aws cloudwatch describe-alarms \
     --state-value ALARM \
     --region ${AWS_REGION}
   ```

2. **Check OpenSearch Index Size**
   ```bash
   curl -u admin:password https://opensearch-endpoint/_cat/indices?v
   ```

3. **Review DynamoDB Capacity**
   ```bash
   aws dynamodb describe-table \
     --table-name nifty-stock-intel-dev-chat-sessions \
     --query 'Table.[TableSizeBytes,ItemCount]' \
     --region ${AWS_REGION}
   ```

4. **Check S3 Bucket Sizes**
   ```bash
   aws s3 ls s3://nifty-stock-intel-dev-data-lake/ --recursive --summarize
   ```

5. **Review Security Group Rules**
   ```bash
   aws ec2 describe-security-groups \
     --filters "Name=tag:Project,Values=NiftyStockIntelligence" \
     --region ${AWS_REGION}
   ```

---

## Monitoring & Alerts

### Key Metrics Dashboard

**Access:** CloudWatch Console → Dashboards → `nsip-dashboard`

**Critical Metrics:**

| Metric | Normal Range | Alert Threshold | Action |
|--------|--------------|-----------------|--------|
| ECS CPU Utilization | 30-60% | >80% for 5 min | Scale out |
| ECS Memory Utilization | 40-70% | >85% for 5 min | Scale out |
| API Error Rate | <0.5% | >2% | Investigate logs |
| API Response Time (p99) | <20s | >30s | Check bottlenecks |
| OpenSearch CPU | <60% | >80% | Scale up |
| Lambda Errors | 0-5/hour | >50/hour | Check logs |
| Bedrock Throttles | 0 | >10/hour | Request limit increase |

### Alert Configuration

**SNS Topic:** `nsip-alerts-dev`

**Subscriptions:**
- Email: your-email@example.com
- Slack: #nsip-alerts (via AWS Chatbot)

### Log Locations

```bash
# Backend Application Logs
/ecs/nifty-stock-intel-dev-backend

# Lambda Ingestor Logs
/aws/lambda/nifty-stock-intel-dev-ingestor

# Lambda ETL Logs
/aws/lambda/nifty-stock-intel-dev-etl

# OpenSearch Logs
/aws/opensearch/nifty-stock-intel-dev-search/logs
```

### Querying Logs

**CloudWatch Insights Queries:**

```sql
-- Find API errors (last 1 hour)
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 100

-- Top 5 slowest API requests
fields @timestamp, request.path, duration
| filter duration > 10000
| sort duration desc
| limit 5

-- Count requests by endpoint
stats count() by request.path
| sort count desc
```

---

## Incident Response

### Severity Levels

| Level | Description | Response Time | Escalation |
|-------|-------------|---------------|------------|
| P1 - Critical | Complete outage | Immediate | All hands on deck |
| P2 - High | Partial outage or severe degradation | 15 minutes | On-call engineer |
| P3 - Medium | Minor issues affecting some users | 1 hour | Team lead |
| P4 - Low | Cosmetic issues or minor bugs | Next business day | Backlog |

### P1: Complete Outage

**Symptoms:** API returning 500 errors, frontend unreachable

**Immediate Actions:**

1. **Check Service Status**
   ```bash
   aws ecs describe-services \
     --cluster ${CLUSTER_NAME} \
     --services ${SERVICE_NAME}
   ```

2. **Check Recent Deployments**
   ```bash
   aws ecs describe-task-definition \
     --task-definition ${SERVICE_NAME}:$(aws ecs list-task-definitions --family-prefix ${SERVICE_NAME} --query 'taskDefinitionArns[0]' --output text | rev | cut -d: -f1 | rev)
   ```

3. **Rollback if Recent Deployment**
   ```bash
   # Get previous task definition
   PREVIOUS_TASK_DEF=$(aws ecs list-task-definitions \
     --family-prefix ${SERVICE_NAME} \
     --max-items 2 \
     --query 'taskDefinitionArns[1]' \
     --output text)
   
   # Rollback
   aws ecs update-service \
     --cluster ${CLUSTER_NAME} \
     --service ${SERVICE_NAME} \
     --task-definition ${PREVIOUS_TASK_DEF}
   ```

4. **Check Dependencies**
   ```bash
   # OpenSearch
   curl -u admin:password https://opensearch-endpoint/_cluster/health
   
   # DynamoDB
   aws dynamodb describe-table --table-name chat-sessions-table
   
   # Bedrock (attempt invocation)
   aws bedrock-runtime invoke-model \
     --model-id anthropic.claude-3-5-sonnet-20240620-v1:0 \
     --body '{"prompt":"test","max_tokens":10}' \
     /dev/stdout
   ```

5. **Create Incident Report**
   - Document time of outage
   - Note actions taken
   - Estimate user impact

### P2: Partial Degradation

**Symptoms:** Slow responses, intermittent errors

**Actions:**

1. **Identify Bottleneck**
   ```bash
   # Check ECS metrics
   aws cloudwatch get-metric-statistics \
     --namespace AWS/ECS \
     --metric-name CPUUtilization \
     --dimensions Name=ServiceName,Value=${SERVICE_NAME} \
     --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
     --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
     --period 300 \
     --statistics Average
   ```

2. **Scale Up if Needed**
   ```bash
   aws ecs update-service \
     --cluster ${CLUSTER_NAME} \
     --service ${SERVICE_NAME} \
     --desired-count 4
   ```

3. **Clear Cache if Stale**
   ```bash
   # Connect to Redis and flush
   redis-cli -h your-redis-endpoint.cache.amazonaws.com FLUSHDB
   ```

4. **Monitor Recovery**

### Incident Communication Template

```
Subject: [P1/P2/P3] NSIP Incident - [Brief Description]

Status: INVESTIGATING / IDENTIFIED / MONITORING / RESOLVED

Impact:
- Services affected: [Backend API / Frontend / Data Ingestion]
- Users affected: [All / Partial / Minimal]
- Started at: [Timestamp]

Current Status:
[Description of current situation]

Actions Taken:
1. [Action 1]
2. [Action 2]

Next Steps:
- [Next action]
- ETA for resolution: [Estimate]

Will update in 15 minutes or when status changes.
```

---

## Maintenance Procedures

### Planned Deployment

**Schedule:** Tuesdays/Thursdays, 10:00-11:00 AM IST (off-peak hours)

**Pre-Deployment Checklist:**

- [ ] Code reviewed and approved
- [ ] Tests passing in CI/CD
- [ ] Database migrations tested
- [ ] Rollback plan prepared
- [ ] Stakeholders notified
- [ ] Maintenance window scheduled

**Deployment Steps:**

1. **Create Snapshot** (if applicable)
   ```bash
   # Snapshot DynamoDB tables
   aws dynamodb create-backup \
     --table-name chat-sessions \
     --backup-name "chat-sessions-$(date +%Y%m%d-%H%M%S)"
   ```

2. **Deploy Backend**
   ```bash
   # Build and push new image
   docker build -t nsip-backend:v1.2.0 .
   docker tag nsip-backend:v1.2.0 ${ECR_REPO}:v1.2.0
   docker push ${ECR_REPO}:v1.2.0
   
   # Update task definition
   # Update service
   aws ecs update-service \
     --cluster ${CLUSTER_NAME} \
     --service ${SERVICE_NAME} \
     --task-definition ${NEW_TASK_DEF} \
     --force-new-deployment
   ```

3. **Smoke Test**
   ```bash
   # Wait for service to stabilize
   aws ecs wait services-stable \
     --cluster ${CLUSTER_NAME} \
     --services ${SERVICE_NAME}
   
   # Test health endpoint
   curl https://api-endpoint/health
   
   # Test critical functionality
   curl -X POST https://api-endpoint/api/v1/chat/message \
     -H "Authorization: Bearer ${TEST_TOKEN}" \
     -d '{"message":"test"}'
   ```

4. **Monitor for 15 Minutes**
   - Watch CloudWatch metrics
   - Check error rates
   - Review logs

5. **Rollback if Issues**
   ```bash
   aws ecs update-service \
     --cluster ${CLUSTER_NAME} \
     --service ${SERVICE_NAME} \
     --task-definition ${PREVIOUS_TASK_DEF}
   ```

### Database Maintenance

**Monthly OpenSearch Index Optimization:**

```bash
# Reindex old data (older than 30 days)
curl -X POST "https://opensearch-endpoint/_reindex" \
  -H 'Content-Type: application/json' \
  -d '{
    "source": {
      "index": "stock-documents",
      "query": {
        "range": {
          "timestamp": {
            "lt": "now-30d"
          }
        }
      }
    },
    "dest": {
      "index": "stock-documents-archive"
    }
  }'

# Delete old archived data (older than 90 days)
curl -X POST "https://opensearch-endpoint/stock-documents/_delete_by_query" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "range": {
        "timestamp": {
          "lt": "now-90d"
        }
      }
    }
  }'

# Force merge
curl -X POST "https://opensearch-endpoint/stock-documents/_forcemerge?max_num_segments=1"
```

**DynamoDB Cleanup:**

```bash
# TTL is configured, but verify
aws dynamodb describe-time-to-live \
  --table-name chat-sessions

# Manual cleanup if needed (use with caution)
aws dynamodb scan \
  --table-name chat-sessions \
  --filter-expression "created_at < :old_date" \
  --expression-attribute-values '{":old_date":{"N":"'$(date -d '90 days ago' +%s)'"}}' \
  | jq -r '.Items[].session_id.S' \
  | xargs -I {} aws dynamodb delete-item \
      --table-name chat-sessions \
      --key '{"session_id":{"S":"{}"}}'
```

---

## Backup & Recovery

### Automated Backups

**DynamoDB:**
- Point-in-time recovery: ENABLED
- Retention: 35 days
- Daily backup: Automated via AWS Backup

**S3:**
- Versioning: ENABLED
- Lifecycle policy: Move to Glacier after 90 days

**OpenSearch:**
- Automated snapshots: Daily at 03:00 UTC
- Retention: 14 days

### Manual Backup

```bash
#!/bin/bash
# manual-backup.sh

BACKUP_DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_BUCKET="nsip-backups"

# 1. Backup DynamoDB tables
for TABLE in chat-sessions chat-messages document-metadata; do
  aws dynamodb create-backup \
    --table-name ${TABLE} \
    --backup-name "${TABLE}-manual-${BACKUP_DATE}"
done

# 2. Backup OpenSearch snapshot
curl -X PUT "https://opensearch-endpoint/_snapshot/manual/snapshot-${BACKUP_DATE}" \
  -H 'Content-Type: application/json' \
  -d '{
    "indices": "stock-documents",
    "ignore_unavailable": true,
    "include_global_state": false
  }'

# 3. Export Terraform state
terraform state pull > terraform-state-${BACKUP_DATE}.json
aws s3 cp terraform-state-${BACKUP_DATE}.json s3://${BACKUP_BUCKET}/terraform/

# 4. Backup application config
aws secretsmanager get-secret-value \
  --secret-id nsip-api-keys \
  --query SecretString \
  --output text > secrets-${BACKUP_DATE}.json
aws s3 cp secrets-${BACKUP_DATE}.json s3://${BACKUP_BUCKET}/secrets/ --sse AES256

echo "Backup completed: ${BACKUP_DATE}"
```

### Disaster Recovery

**RTO (Recovery Time Objective):** 2 hours  
**RPO (Recovery Point Objective):** 24 hours

**Full Recovery Procedure:**

1. **Restore Infrastructure**
   ```bash
   # Clone repository
   git clone https://github.com/LearningGallery/nifty-stock-intelligence.git
   cd nifty-stock-intelligence/terraform
   
   # Restore state
   aws s3 cp s3://nsip-backups/terraform/terraform-state-latest.json .
   terraform state push terraform-state-latest.json
   
   # Apply infrastructure
   terraform apply -auto-approve
   ```

2. **Restore DynamoDB**
   ```bash
   aws dynamodb restore-table-from-backup \
     --target-table-name chat-sessions \
     --backup-arn arn:aws:dynamodb:region:account:table/chat-sessions/backup/latest
   ```

3. **Restore OpenSearch**
   ```bash
   curl -X POST "https://new-opensearch-endpoint/_snapshot/manual/snapshot-latest/_restore" \
     -H 'Content-Type: application/json' \
     -d '{
       "indices": "stock-documents",
       "ignore_unavailable": true,
       "include_global_state": false
     }'
   ```

4. **Redeploy Applications**
   ```bash
   # Follow deployment guide
   ./scripts/deploy.sh
   ```

5. **Validate**
   ```bash
   ./scripts/run-tests.sh
   ```

---

## Scaling Operations

### Horizontal Scaling (Add/Remove Tasks)

**Scale Out:**
```bash
aws ecs update-service \
  --cluster ${CLUSTER_NAME} \
  --service ${SERVICE_NAME} \
  --desired-count 5
```

**Scale In:**
```bash
aws ecs update-service \
  --cluster ${CLUSTER_NAME} \
  --service ${SERVICE_NAME} \
  --desired-count 2
```

### Vertical Scaling (Increase Task Resources)

**Update Task Definition:**
```bash
# Get current task definition
aws ecs describe-task-definition \
  --task-definition ${SERVICE_NAME} > task-def.json

# Edit CPU/Memory
jq '.taskDefinition.cpu = "2048" | .taskDefinition.memory = "4096"' task-def.json > task-def-new.json

# Register new task definition
NEW_TASK_DEF=$(aws ecs register-task-definition \
  --cli-input-json file://task-def-new.json \
  --query 'taskDefinition.taskDefinitionArn' \
  --output text)

# Update service
aws ecs update-service \
  --cluster ${CLUSTER_NAME} \
  --service ${SERVICE_NAME} \
  --task-definition ${NEW_TASK_DEF}
```

### OpenSearch Scaling

```bash
# Update cluster configuration
aws opensearch update-domain-config \
  --domain-name nifty-stock-intel-search \
  --cluster-config InstanceCount=3,InstanceType=r6g.large.search
```

### Auto-Scaling Review

**Check Current Configuration:**
```bash
aws application-autoscaling describe-scalable-targets \
  --service-namespace ecs \
  --resource-ids service/${CLUSTER_NAME}/${SERVICE_NAME}

aws application-autoscaling describe-scaling-policies \
  --service-namespace ecs \
  --resource-id service/${CLUSTER_NAME}/${SERVICE_NAME}
```

---

## Security Operations

### Rotate Secrets

**Every 90 Days:**

```bash
# 1. Generate new API keys
NEW_NEWS_API_KEY="your-new-key"

# 2. Update Secrets Manager
aws secretsmanager update-secret \
  --secret-id nsip-api-keys \
  --secret-string "{\"news_api_key\":\"${NEW_NEWS_API_KEY}\"}"

# 3. Restart service to pick up new secrets
aws ecs update-service \
  --cluster ${CLUSTER_NAME} \
  --service ${SERVICE_NAME} \
  --force-new-deployment

# 4. Verify
aws ecs wait services-stable \
  --cluster ${CLUSTER_NAME} \
  --services ${SERVICE_NAME}
```

### Security Audit

**Monthly Security Checklist:**

- [ ] Review IAM roles and policies
- [ ] Check security group rules
- [ ] Review CloudTrail logs for suspicious activity
- [ ] Verify encryption at rest
- [ ] Check SSL/TLS certificates
- [ ] Review Cognito user pool settings
- [ ] Scan container images for vulnerabilities
- [ ] Update dependencies with security patches

**Run Security Scan:**
```bash
# Scan ECR images
aws ecr start-image-scan \
  --repository-name nsip-backend \
  --image-id imageTag=latest

# Get scan results
aws ecr describe-image-scan-findings \
  --repository-name nsip-backend \
  --image-id imageTag=latest
```

---

## Cost Management

### Monthly Cost Review

```bash
# Get cost breakdown
aws ce get-cost-and-usage \
  --time-period Start=$(date -d "last month" +%Y-%m-01),End=$(date +%Y-%m-01) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=SERVICE \
  --region us-east-1
```

### Cost Optimization Actions

1. **Right-Size Resources**
   - Review ECS task CPU/memory utilization
   - Scale down underutilized OpenSearch nodes
   - Use Fargate Spot for non-critical tasks

2. **Implement Caching**
   - Increase cache TTL for frequently accessed data
   - Use CloudFront edge caching effectively

3. **Data Lifecycle**
   - Archive old S3 data to Glacier
   - Delete old DynamoDB items via TTL
   - Purge old OpenSearch indices

4. **Reserved Capacity**
   - Consider Savings Plans for predictable workloads
   - Use Reserved Instances for long-term stable capacity

---

## On-Call Runbook

### On-Call Schedule

- **Primary:** Rotating weekly
- **Secondary:** Team lead (escalation)
- **Coverage:** 24/7

### On-Call Responsibilities

1. Respond to P1/P2 incidents within SLA
2. Monitor alert channels
3. Perform daily health checks
4. Escalate when needed
5. Document all incidents

### Escalation Path

```
P1 Incident
    ↓
On-Call Engineer (15 min)
    ↓
Team Lead (30 min)
    ↓
Engineering Manager (1 hour)
    ↓
CTO
```

### Contact Information

Store in encrypted vault or internal wiki.

---

**Last Updated:** 2024-01-15
**Document Owner:** DevOps Team
**Review Schedule:** Monthly
