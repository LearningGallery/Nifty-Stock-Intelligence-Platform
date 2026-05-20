# Troubleshooting Guide

Common issues, their symptoms, causes, and solutions for the Nifty Stock Intelligence Platform.

---

## Table of Contents

1. [Backend API Issues](#backend-api-issues)
2. [Frontend Issues](#frontend-issues)
3. [Database Issues](#database-issues)
4. [AI/LLM Issues](#aillm-issues)
5. [Infrastructure Issues](#infrastructure-issues)
6. [Data Ingestion Issues](#data-ingestion-issues)
7. [Performance Issues](#performance-issues)
8. [Authentication Issues](#authentication-issues)

---

## Backend API Issues

### Issue: API Returns 500 Internal Server Error

**Symptoms:**
- All API requests return 500 status
- Frontend shows "Server Error"
- Health check endpoint fails

**Diagnosis:**
```bash
# Check ECS service status
aws ecs describe-services \
  --cluster ${CLUSTER_NAME} \
  --services ${SERVICE_NAME} \
  --query 'services[0].[status,runningCount,desiredCount]'

# Check recent logs
aws logs tail /ecs/${SERVICE_NAME} --follow --since 5m

# Check task failures
aws ecs list-tasks --cluster ${CLUSTER_NAME} --service ${SERVICE_NAME}
```

**Common Causes & Solutions:**

1. **Application Crash**
   ```bash
   # Check logs for Python errors
   aws logs filter-pattern /ecs/${SERVICE_NAME} --filter-pattern "ERROR" --start-time 1h
   
   # Solution: Fix code error and redeploy
   ```

2. **Out of Memory**
   ```bash
   # Check memory metrics
   aws cloudwatch get-metric-statistics \
     --namespace AWS/ECS \
     --metric-name MemoryUtilization \
     --dimensions Name=ServiceName,Value=${SERVICE_NAME}
   
   # Solution: Increase task memory
   aws ecs update-service --cluster ${CLUSTER_NAME} \
     --service ${SERVICE_NAME} \
     --task-definition new-task-def-with-more-memory
   ```

3. **Database Connection Issues**
   ```bash
   # Test DynamoDB access
   aws dynamodb describe-table --table-name chat-sessions
   
   # Check IAM permissions
   aws iam simulate-principal-policy \
     --policy-source-arn ${TASK_ROLE_ARN} \
     --action-names dynamodb:PutItem dynamodb:GetItem
   
   # Solution: Fix IAM permissions
   ```

4. **Bedrock Access Denied**
   ```bash
   # Test Bedrock access
   aws bedrock-runtime invoke-model \
     --model-id anthropic.claude-3-5-sonnet-20240620-v1:0 \
     --body '{"messages":[{"role":"user","content":"test"}],"max_tokens":10,"anthropic_version":"bedrock-2023-05-31"}' \
     --region ${AWS_REGION} \
     output.json
   
   # Solution: Request Bedrock model access in console
   ```

---

### Issue: Slow API Response Times (>30s)

**Symptoms:**
- Requests timeout
- p99 latency > 30 seconds
- Users report chatbot is slow

**Diagnosis:**
```bash
# Check ALB metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name TargetResponseTime \
  --dimensions Name=LoadBalancer,Value=${ALB_ARN_SUFFIX} \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum

# Check slow queries in logs
aws logs filter-pattern /ecs/${SERVICE_NAME} \
  --filter-pattern '[timestamp, request, duration > 20000]'
```

**Common Causes & Solutions:**

1. **OpenSearch Slow Queries**
   ```bash
   # Check OpenSearch performance
   curl -u admin:password "https://${OPENSEARCH_ENDPOINT}/_nodes/stats" | jq '.nodes[].indices.search'
   
   # Solution: Optimize queries, add caching, or scale up
   ```

2. **Bedrock Rate Limiting**
   ```bash
   # Check for throttling
   aws cloudwatch get-metric-statistics \
     --namespace AWS/Bedrock \
     --metric-name ModelInvocationThrottles
   
   # Solution: Request quota increase or implement retry logic
   ```

3. **Cache Miss**
   ```bash
   # Check Redis connectivity
   redis-cli -h ${REDIS_ENDPOINT} ping
   
   # Check cache hit rate
   redis-cli -h ${REDIS_ENDPOINT} info stats | grep keyspace_hits
   
   # Solution: Verify cache TTL, increase cache memory
   ```

4. **Technical Analysis Computation**
   ```bash
   # Enable profiling in code
   # Check if pandas/ta-lib operations are slow
   
   # Solution: Pre-compute and cache technical indicators
   ```

---

### Issue: Chat History Not Persisting

**Symptoms:**
- Chat messages don't appear in history
- Session IDs not found
- Users lose conversation context

**Diagnosis:**
```bash
# Check DynamoDB table
aws dynamodb scan --table-name chat-sessions --limit 10

# Check IAM permissions
aws iam get-role-policy \
  --role-name ${ECS_TASK_ROLE} \
  --policy-name dynamodb-access

# Check application logs
aws logs filter-pattern /ecs/${SERVICE_NAME} --filter-pattern "DynamoDB"
```

**Solutions:**

1. **Missing Permissions**
   ```hcl
   # In Terraform, ensure task role has:
   resource "aws_iam_role_policy" "dynamodb" {
     policy = jsonencode({
       Statement = [{
         Effect = "Allow"
         Action = [
           "dynamodb:PutItem",
           "dynamodb:GetItem",
           "dynamodb:Query",
           "dynamodb:UpdateItem"
         ]
         Resource = aws_dynamodb_table.chat_sessions.arn
       }]
     })
   }
   ```

2. **Table Not Found**
   ```bash
   # Verify table exists
   aws dynamodb describe-table --table-name chat-sessions
   
   # Check environment variable in task definition
   aws ecs describe-task-definition --task-definition ${SERVICE_NAME} \
     | jq '.taskDefinition.containerDefinitions[0].environment'
   ```

3. **TTL Expired Records**
   ```bash
   # Check TTL configuration
   aws dynamodb describe-time-to-live --table-name chat-sessions
   
   # Increase TTL if needed (in code)
   ttl = int(datetime.utcnow().timestamp()) + (30 * 24 * 60 * 60)  # 30 days
   ```

---

## Frontend Issues

### Issue: Frontend Shows White Screen

**Symptoms:**
- Blank page loads
- Browser console shows errors
- CloudFront serves but app doesn't load

**Diagnosis:**
```bash
# Check CloudFront distribution
aws cloudfront get-distribution --id ${CLOUDFRONT_ID}

# Test S3 bucket directly
aws s3 ls s3://${FRONTEND_BUCKET}/

# Check browser console (F12)
# Look for JavaScript errors
```

**Solutions:**

1. **Build Artifacts Missing**
   ```bash
   # Rebuild and redeploy
   cd frontend
   npm run build
   aws s3 sync dist/ s3://${FRONTEND_BUCKET}/ --delete
   
   # Invalidate cache
   aws cloudfront create-invalidation \
     --distribution-id ${CLOUDFRONT_ID} \
     --paths "/*"
   ```

2. **CORS Issues**
   ```bash
   # Check CORS on ALB
   curl -I -X OPTIONS https://${API_URL}/api/v1/chat/message \
     -H "Origin: https://${FRONTEND_URL}" \
     -H "Access-Control-Request-Method: POST"
   
   # Should return Access-Control-Allow-Origin header
   
   # Fix: Update backend CORS settings
   ALLOWED_ORIGINS=https://your-cloudfront-domain.cloudfront.net
   ```

3. **Environment Variables Not Set**
   ```bash
   # Check .env.production
   cat frontend/.env.production
   
   # Should contain:
   VITE_API_URL=https://your-alb-dns.elb.amazonaws.com
   VITE_COGNITO_USER_POOL_ID=ap-south-1_XXXXXXXXX
   ```

---

### Issue: "Failed to Connect to API" Error

**Symptoms:**
- Frontend loads but shows connection error
- API calls fail with network error
- Browser shows CORS errors

**Diagnosis:**
```bash
# Test API from command line
curl https://${API_URL}/health

# Check CloudFront origin configuration
aws cloudfront get-distribution-config --id ${CLOUDFRONT_ID} \
  | jq '.DistributionConfig.Origins'

# Check security groups
aws ec2 describe-security-groups --group-ids ${ALB_SG_ID}
```

**Solutions:**

1. **Security Group Misconfigured**
   ```bash
   # Allow HTTPS from CloudFront
   aws ec2 authorize-security-group-ingress \
     --group-id ${ALB_SG_ID} \
     --protocol tcp \
     --port 443 \
     --cidr 0.0.0.0/0
   ```

2. **Wrong API URL**
   ```javascript
   // Check frontend/.env.production
   // Should match ALB DNS or custom domain
   VITE_API_URL=https://correct-alb-dns.ap-south-1.elb.amazonaws.com
   ```

3. **SSL Certificate Issues**
   ```bash
   # Check certificate on ALB
   aws elbv2 describe-listeners --load-balancer-arn ${ALB_ARN}
   
   # If using self-signed cert (dev only), browser may block
   # Solution: Accept self-signed cert or use ACM cert
   ```

---

## Database Issues

### Issue: DynamoDB Throttling

**Symptoms:**
- ProvisionedThroughputExceededException
- Slow chat response times
- "Database unavailable" errors

**Diagnosis:**
```bash
# Check throttle metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name UserErrors \
  --dimensions Name=TableName,Value=chat-sessions \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# Check table capacity mode
aws dynamodb describe-table --table-name chat-sessions \
  | jq '.Table.BillingModeSummary'
```

**Solutions:**

1. **Switch to On-Demand Mode**
   ```bash
   aws dynamodb update-table \
     --table-name chat-sessions \
     --billing-mode PAY_PER_REQUEST
   ```

2. **Increase Provisioned Capacity** (if using provisioned mode)
   ```bash
   aws dynamodb update-table \
     --table-name chat-sessions \
     --provisioned-throughput ReadCapacityUnits=100,WriteCapacityUnits=100
   ```

3. **Implement Exponential Backoff** (in code)
   ```python
   from tenacity import retry, stop_after_attempt, wait_exponential
   
   @retry(
       stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=1, min=1, max=10)
   )
   def put_item_with_retry(table, item):
       table.put_item(Item=item)
   ```

---

### Issue: OpenSearch Cluster Red/Yellow

**Symptoms:**
- Cluster status: RED or YELLOW
- Search queries fail
- RAG retrieval returns no results

**Diagnosis:**
```bash
# Check cluster health
curl -u admin:password "https://${OPENSEARCH_ENDPOINT}/_cluster/health?pretty"

# Check indices
curl -u admin:password "https://${OPENSEARCH_ENDPOINT}/_cat/indices?v"

# Check unassigned shards
curl -u admin:password "https://${OPENSEARCH_ENDPOINT}/_cat/shards?v" | grep UNASSIGNED
```

**Solutions:**

1. **Cluster RED - Data Loss**
   ```bash
   # Identify problem indices
   curl -u admin:password "https://${OPENSEARCH_ENDPOINT}/_cluster/allocation/explain?pretty"
   
   # If data loss is acceptable, delete and recreate
   curl -X DELETE "https://${OPENSEARCH_ENDPOINT}/problematic-index"
   
   # Re-run ETL to reindex data
   aws lambda invoke \
     --function-name ${ETL_LAMBDA} \
     --payload '{"reindex": true}' \
     response.json
   ```

2. **Cluster YELLOW - Replica Issues**
   ```bash
   # Reduce replica count (single node cluster)
   curl -X PUT "https://${OPENSEARCH_ENDPOINT}/stock-documents/_settings" \
     -H 'Content-Type: application/json' \
     -d '{"index": {"number_of_replicas": 0}}'
   
   # Or scale up cluster
   aws opensearch update-domain-config \
     --domain-name ${OPENSEARCH_DOMAIN} \
     --cluster-config InstanceCount=2
   ```

3. **Disk Space Issues**
   ```bash
   # Check disk usage
   curl -u admin:password "https://${OPENSEARCH_ENDPOINT}/_cat/allocation?v"
   
   # Solution: Scale up storage
   aws opensearch update-domain-config \
     --domain-name ${OPENSEARCH_DOMAIN} \
     --ebs-options EBSEnabled=true,VolumeSize=200
   ```

---

## AI/LLM Issues

### Issue: Bedrock Model Returns Empty or Invalid Response

**Symptoms:**
- Chat returns blank responses
- "Failed to generate response" error
- Incomplete analysis

**Diagnosis:**
```bash
# Check Bedrock logs
aws logs tail /aws/bedrock/modelinvocations --follow

# Test model directly
aws bedrock-runtime invoke-model \
  --model-id anthropic.claude-3-5-sonnet-20240620-v1:0 \
  --body '{
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1024,
    "messages": [{
      "role": "user",
      "content": "Hello"
    }]
  }' \
  --region ${AWS_REGION} \
  output.json

cat output.json
```

**Solutions:**

1. **Malformed Prompt**
   ```python
   # Check prompt structure in logs
   # Ensure proper format for Claude:
   {
       "anthropic_version": "bedrock-2023-05-31",
       "max_tokens": 4096,
       "messages": [
           {"role": "user", "content": "Your prompt here"}
       ],
       "system": "System prompt here"
   }
   ```

2. **Context Length Exceeded**
   ```python
   # Check token count
   import anthropic
   
   def count_tokens(text):
       # Approximate: ~4 chars per token
       return len(text) // 4
   
   # Solution: Truncate context or use longer context model
   if count_tokens(prompt) > 190000:  # Leave buffer
       prompt = truncate_prompt(prompt, max_tokens=180000)
   ```

3. **Rate Limiting**
   ```bash
   # Check for throttles
   aws cloudwatch get-metric-statistics \
     --namespace AWS/Bedrock \
     --metric-name ModelInvocationClientErrors
   
   # Solution: Implement retry with backoff
   ```

---

### Issue: RAG Returns Irrelevant Documents

**Symptoms:**
- Stock analysis includes unrelated information
- Citations don't match query
- Poor answer quality

**Diagnosis:**
```bash
# Check OpenSearch query
# Enable query logging in code temporarily

# Test semantic search directly
curl -X POST "https://${OPENSEARCH_ENDPOINT}/stock-documents/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "knn": {
        "embedding": {
          "vector": [0.1, 0.2, ...],  # Sample embedding
          "k": 5
        }
      }
    }
  }'
```

**Solutions:**

1. **Embeddings Not Generated Correctly**
   ```python
   # Verify embedding generation
   from app.services.bedrock_service import BedrockService
   
   bedrock = BedrockService()
   embedding = bedrock.generate_embedding("Test text")
   print(f"Embedding dimension: {len(embedding)}")  # Should be 1024 for Titan v2
   ```

2. **Low Similarity Threshold**
   ```python
   # Adjust threshold in config
   RAG_SIMILARITY_THRESHOLD = 0.75  # Increase from 0.7
   ```

3. **Poor Document Chunking**
   ```python
   # Review chunk size
   CHUNK_SIZE = 512  # tokens
   CHUNK_OVERLAP = 50  # tokens
   
   # Consider semantic chunking instead of fixed size
   ```

4. **Stale Index Data**
   ```bash
   # Re-run data ingestion
   aws lambda invoke \
     --function-name ${LAMBDA_INGESTOR} \
     --payload '{"ingestion_type": "manual"}' \
     response.json
   ```

---

## Infrastructure Issues

### Issue: ECS Tasks Keep Stopping

**Symptoms:**
- Tasks repeatedly stop and restart
- Service never reaches desired count
- "Essential container exited" errors

**Diagnosis:**
```bash
# Get stopped task IDs
aws ecs list-tasks \
  --cluster ${CLUSTER_NAME} \
  --service ${SERVICE_NAME} \
  --desired-status STOPPED \
  --max-items 5

# Describe stopped task
aws ecs describe-tasks \
  --cluster ${CLUSTER_NAME} \
  --tasks <TASK_ID> \
  | jq '.tasks[0].stoppedReason'

# Check CloudWatch logs for that task
aws logs get-log-events \
  --log-group-name /ecs/${SERVICE_NAME} \
  --log-stream-name ecs/${SERVICE_NAME}/<TASK_ID>
```

**Solutions:**

1. **Health Check Failing**
   ```bash
   # Test health endpoint manually
   curl http://<TASK_IP>:8000/health
   
   # Adjust health check in task definition
   "healthCheck": {
     "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
     "interval": 30,
     "timeout": 10,
     "retries": 5,
     "startPeriod": 120  # Increase if app takes time to start
   }
   ```

2. **Out of Memory (OOMKilled)**
   ```bash
   # Check for OOM in task definition
   aws ecs describe-tasks --tasks <TASK_ID> | jq '.tasks[0].containers[0].reason'
   
   # Solution: Increase memory
   "memory": 4096  # Increase from 2048
   ```

3. **Application Crash on Startup**
   ```bash
   # Check initialization code
   # Look for missing environment variables
   # Verify all dependencies are accessible
   ```

---

### Issue: Lambda Function Timeout

**Symptoms:**
- "Task timed out after 300.00 seconds"
- Data ingestion incomplete
- ETL processing fails

**Diagnosis:**
```bash
# Check function configuration
aws lambda get-function-configuration \
  --function-name ${LAMBDA_FUNCTION}

# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=${LAMBDA_FUNCTION}
```

**Solutions:**

1. **Increase Timeout**
   ```bash
   aws lambda update-function-configuration \
     --function-name ${LAMBDA_FUNCTION} \
     --timeout 900  # 15 minutes (max)
   ```

2. **Increase Memory** (also increases CPU)
   ```bash
   aws lambda update-function-configuration \
     --function-name ${LAMBDA_FUNCTION} \
     --memory-size 1024  # Increase from 512
   ```

3. **Process in Batches**
   ```python
   # Split processing into smaller batches
   def lambda_handler(event, context):
       stocks = get_stock_list()
       batch_size = 10
       
       for i in range(0, len(stocks), batch_size):
           batch = stocks[i:i+batch_size]
           process_batch(batch)
           
           # Check remaining time
           if context.get_remaining_time_in_millis() < 30000:
               # Re-invoke self for remaining items
               lambda_client.invoke(
                   FunctionName=context.function_name,
                   InvocationType='Event',
                   Payload=json.dumps({'start_index': i + batch_size})
               )
               break
   ```

---

## Performance Issues

### Issue: High Database Costs

**Diagnosis:**
```bash
# Check DynamoDB usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --dimensions Name=TableName,Value=chat-sessions

# Check itemcount
aws dynamodb describe-table --table-name chat-sessions \
  | jq '.Table.ItemCount'
```

**Solutions:**

1. **Implement TTL**
   ```bash
   aws dynamodb update-time-to-live \
     --table-name chat-sessions \
     --time-to-live-specification "Enabled=true,AttributeName=ttl"
   ```

2. **Use DynamoDB Streams for Archives**
   ```bash
   # Enable streams
   aws dynamodb update-table \
     --table-name chat-sessions \
     --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES
   
   # Create Lambda to archive to S3
   ```

3. **Optimize Query Patterns**
   ```python
   # Use query instead of scan
   response = table.query(
       KeyConditionExpression=Key('user_id').eq(user_id)
   )
   
   # Not:
   response = table.scan(
       FilterExpression=Attr('user_id').eq(user_id)
   )
   ```

---

### Issue: High Bedrock Costs

**Diagnosis:**
```bash
# Check invocation metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Bedrock \
  --metric-name Invocations

# Estimate cost
# Claude 3.5 Sonnet: $3/1M input tokens, $15/1M output tokens
```

**Solutions:**

1. **Implement Aggressive Caching**
   ```python
   # Cache analysis results for 30 minutes
   cache_key = f"analysis:{symbol}:{timeframe}"
   cached = await cache_service.get(cache_key)
   if cached:
       return cached
   
   result = await generate_analysis(symbol, timeframe)
   await cache_service.set(cache_key, result, ttl=1800)
   ```

2. **Optimize Prompts**
   ```python
   # Reduce unnecessary context
   # Use Claude Haiku for simple queries
   if is_simple_query(message):
       model_id = "anthropic.claude-3-haiku-20240307-v1:0"  # Cheaper
   else:
       model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
   ```

3. **Batch Requests**
   ```python
   # Instead of 10 separate calls, combine into one
   combined_prompt = generate_batch_prompt([stock1, stock2, ...])
   response = await bedrock.generate_response(combined_prompt)
   parse_batch_response(response)
   ```

---

## Authentication Issues

### Issue: "Authentication Failed" Error

**Symptoms:**
- Users cannot login
- Token validation fails
- API returns 401 Unauthorized

**Diagnosis:**
```bash
# Check Cognito user pool
aws cognito-idp describe-user-pool \
  --user-pool-id ${USER_POOL_ID}

# Test authentication
aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id ${CLIENT_ID} \
  --auth-parameters USERNAME=test@example.com,PASSWORD=TestPass123!
```

**Solutions:**

1. **Invalid Credentials**
   ```bash
   # Reset user password
   aws cognito-idp admin-set-user-password \
     --user-pool-id ${USER_POOL_ID} \
     --username test@example.com \
     --password NewPassword123! \
     --permanent
   ```

2. **Token Expired**
   ```javascript
   // Frontend should refresh token
   const refreshToken = localStorage.getItem('refresh_token')
   
   const response = await fetch(`https://cognito-idp.${region}.amazonaws.com/`, {
     method: 'POST',
     headers: {
       'X-Amz-Target': 'AWSCognitoIdentityProviderService.InitiateAuth',
       'Content-Type': 'application/x-amz-json-1.1'
     },
     body: JSON.stringify({
       AuthFlow: 'REFRESH_TOKEN_AUTH',
       ClientId: clientId,
       AuthParameters: {
         REFRESH_TOKEN: refreshToken
       }
     })
   })
   ```

3. **CORS Issues with Cognito**
   ```bash
   # Verify app client settings
   aws cognito-idp describe-user-pool-client \
     --user-pool-id ${USER_POOL_ID} \
     --client-id ${CLIENT_ID}
   
   # Ensure allowed callback URLs are correct
   ```

---

## Getting Help

### Log Collection for Support

```bash
#!/bin/bash
# collect-logs.sh

SUPPORT_BUNDLE="support-bundle-$(date +%Y%m%d-%H%M%S).tar.gz"

mkdir -p support-bundle

# Collect ECS logs
aws logs get-log-events \
  --log-group-name /ecs/${SERVICE_NAME} \
  --log-stream-name $(aws logs describe-log-streams \
    --log-group-name /ecs/${SERVICE_NAME} \
    --order-by LastEventTime \
    --descending \
    --max-items 1 \
    --query 'logStreams[0].logStreamName' \
    --output text) \
  --start-time $(($(date +%s) - 3600))000 \
  > support-bundle/ecs-logs.json

# Collect Lambda logs
for FUNCTION in ${LAMBDA_INGESTOR} ${LAMBDA_ETL}; do
  aws logs tail /aws/lambda/${FUNCTION} \
    --since 1h \
    > support-bundle/${FUNCTION}-logs.txt
done

# Collect service status
aws ecs describe-services \
  --cluster ${CLUSTER_NAME} \
  --services ${SERVICE_NAME} \
  > support-bundle/ecs-service-status.json

# Collect recent deployments
aws ecs list-task-definitions \
  --family-prefix ${SERVICE_NAME} \
  --max-items 5 \
  > support-bundle/task-definitions.json

# Create archive
tar -czf ${SUPPORT_BUNDLE} support-bundle/
rm -rf support-bundle/

echo "Support bundle created: ${SUPPORT_BUNDLE}"
```

### Contact & Resources

- **GitHub Issues**: https://github.com/LearningGallery/nifty-stock-intelligence/issues
- **Documentation**: https://github.com/LearningGallery/nifty-stock-intelligence/tree/main/docs
- **LinkedIn**: Im-AbuTalha

---

**Last Updated:** 2024-01-15
**Document Owner:** Engineering Team
