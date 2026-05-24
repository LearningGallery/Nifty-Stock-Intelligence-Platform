# Deployment Guide

Complete step-by-step guide to deploy the Nifty Stock Intelligence Platform on AWS.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [AWS Account Setup](#aws-account-setup)
3. [Local Environment Setup](#local-environment-setup)
4. [Terraform Deployment](#terraform-deployment)
5. [Application Deployment](#application-deployment)
6. [Post-Deployment Configuration](#post-deployment-configuration)
7. [Validation](#validation)
8. [Rollback Procedure](#rollback-procedure)

---

## Prerequisites

### Required Tools

| Tool | Version | Purpose |
|------|---------|---------|
| AWS CLI | >= 2.13.0 | AWS resource management |
| Terraform | >= 1.5.0 | Infrastructure provisioning |
| Docker | >= 24.0.0 | Container builds |
| Node.js | >= 18.0.0 | Frontend build |
| Python | >= 3.11 | Backend development |
| Git | >= 2.40.0 | Version control |

### Installation Commands

```bash
# macOS
brew install awscli terraform docker node python@3.11

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y awscli terraform docker.io nodejs python3.11

# Windows (via Chocolatey)
choco install awscli terraform docker-desktop nodejs python
```

### AWS Account Requirements

- AWS Account with admin access (or specific IAM permissions)
- AWS region: `ap-south-1` (Mumbai) recommended for India-focused app
- Service quotas:
  - ECS Fargate: At least 2 vCPUs
  - OpenSearch: Domain creation allowed
  - Bedrock: Model access enabled

---

## AWS Account Setup

### 1. Configure AWS CLI

```bash
aws configure

# Enter:
# AWS Access Key ID: YOUR_ACCESS_KEY
# AWS Secret Access Key: YOUR_SECRET_KEY
# Default region: ap-south-1
# Default output format: json
```

### 2. Verify Credentials

```bash
aws sts get-caller-identity
```

Expected output:
```json
{
    "UserId": "AIDAXXXXXXXXXXXXXXXXX",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/your-user"
}
```

### 3. Enable Bedrock Model Access

```bash
# Navigate to AWS Console → Bedrock → Model access
# Enable:
# - Anthropic Claude 3.5 Sonnet
# - Amazon Titan Text Embeddings v2

# Or via CLI:
aws bedrock put-model-invocation-logging-configuration \
  --region ap-south-1 \
  --logging-config '{"cloudWatchConfig":{"logGroupName":"/aws/bedrock/modelinvocations","roleArn":"arn:aws:iam::ACCOUNT_ID:role/BedrockLoggingRole"}}'
```

### 4. Create S3 Backend for Terraform State

```bash
# Create S3 bucket for Terraform state
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export TERRAFORM_STATE_BUCKET="nsip-terraform-state-${AWS_ACCOUNT_ID}"

aws s3 mb s3://${TERRAFORM_STATE_BUCKET} --region ap-south-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket ${TERRAFORM_STATE_BUCKET} \
  --versioning-configuration Status=Enabled

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name nsip-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region ap-south-1
```

---

## Local Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/LearningGallery/nifty-stock-intelligence.git
cd nifty-stock-intelligence
```

### 2. Install Backend Dependencies

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install TA-Lib (required for technical analysis)
# macOS
brew install ta-lib

# Ubuntu
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
cd ..

pip install TA-Lib
```

### 3. Install Frontend Dependencies

```bash
cd ../frontend
npm install
```

---

## Terraform Deployment

### 1. Initialize Terraform

```bash
cd ../terraform

# Copy example variables
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values
vim terraform.tfvars
```

**Required Variables in `terraform.tfvars`:**

```hcl
aws_region     = "ap-south-1"
aws_account_id = "123456789012"  # Your AWS account ID
project_name   = "nifty-stock-intel"
environment    = "dev"

# Email for CloudWatch alarms
alarm_email_endpoint = "your-email@example.com"

# Adjust resources based on budget
backend_desired_count = 2
opensearch_instance_count = 2

# Security
cognito_password_minimum_length = 12
cognito_mfa_configuration = "OPTIONAL"
```

### 2. Initialize Terraform Backend

```bash
# Update backend.tf with your bucket name
sed -i "s/nsip-terraform-state-\${var.aws_account_id}/${TERRAFORM_STATE_BUCKET}/g" backend.tf

# Initialize
terraform init
```

### 3. Plan Infrastructure

```bash
terraform plan -out=tfplan

# Review the plan carefully
# Expected resources: ~80-100 resources
```

### 4. Apply Infrastructure

```bash
# Apply in stages for better control
terraform apply tfplan

# This will take 15-20 minutes
# Key resources being created:
# - VPC with public/private subnets
# - ECS cluster
# - OpenSearch domain (longest wait ~15 min)
# - DynamoDB tables
# - Cognito user pool
# - Lambda functions
# - S3 buckets
```

### 5. Save Outputs

```bash
terraform output > ../deployment-outputs.txt

# Important outputs:
# - alb_dns_name
# - cloudfront_domain_name
# - cognito_user_pool_id
# - opensearch_endpoint
```

---

## Application Deployment

### 1. Build and Push Backend Docker Image

```bash
cd ../backend

# Get ECR repository URL
export ECR_REPO=$(terraform output -raw backend_ecr_repository_url)
export AWS_REGION="ap-south-1"

# Login to ECR
aws ecr get-login-password --region ${AWS_REGION} | \
  docker login --username AWS --password-stdin ${ECR_REPO}

# Build image
docker build -t nifty-stock-backend:latest .

# Tag for ECR
docker tag nifty-stock-backend:latest ${ECR_REPO}:latest

# Push to ECR
docker push ${ECR_REPO}:latest
```

### 2. Update ECS Service

```bash
# Get cluster and service names
export CLUSTER_NAME=$(terraform output -raw ecs_cluster_name)
export SERVICE_NAME=$(terraform output -raw backend_service_name)

# Force new deployment
aws ecs update-service \
  --cluster ${CLUSTER_NAME} \
  --service ${SERVICE_NAME} \
  --force-new-deployment \
  --region ${AWS_REGION}

# Wait for service to stabilize
aws ecs wait services-stable \
  --cluster ${CLUSTER_NAME} \
  --services ${SERVICE_NAME} \
  --region ${AWS_REGION}
```

### 3. Build and Deploy Frontend

```bash
cd ../frontend

# Get CloudFront distribution and S3 bucket
export CLOUDFRONT_ID=$(terraform output -raw cloudfront_distribution_id)
export FRONTEND_BUCKET=$(terraform output -raw frontend_bucket_name)
export API_URL=$(terraform output -raw alb_dns_name)

# Create .env.production
cat > .env.production << EOF
VITE_API_URL=https://${API_URL}
VITE_COGNITO_USER_POOL_ID=$(terraform output -raw cognito_user_pool_id)
VITE_COGNITO_CLIENT_ID=$(terraform output -raw cognito_user_pool_client_id)
VITE_COGNITO_REGION=${AWS_REGION}
VITE_ENVIRONMENT=production
EOF

# Build
npm run build

# Deploy to S3
aws s3 sync dist/ s3://${FRONTEND_BUCKET}/ \
  --delete \
  --cache-control "public, max-age=31536000, immutable" \
  --exclude "*.html" \
  --region ${AWS_REGION}

# HTML files with shorter cache
aws s3 sync dist/ s3://${FRONTEND_BUCKET}/ \
  --exclude "*" \
  --include "*.html" \
  --cache-control "public, max-age=0, must-revalidate" \
  --region ${AWS_REGION}

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id ${CLOUDFRONT_ID} \
  --paths "/*"
```

### 4. Deploy Lambda Functions

```bash
cd ../ingestor

# Create deployment package
pip install -r requirements.txt -t package/
cd package
zip -r ../lambda-ingestor.zip . **or** Compress-Archive -Path * -DestinationPath ..\lambda-ingestor.zip -Force
cd ..
zip -g lambda-ingestor.zip src/*.py src/**/*.py

# 1. Collect all Python files inside the src folder and its subfolders
$files = Get-ChildItem -Path src -Filter *.py -Recurse | Select-Object -ExpandProperty FullName
# 2. Append those files into your existing zip archive
Compress-Archive -Path $files -Update -DestinationPath .\lambda-ingestor.zip


# Update Lambda function
export LAMBDA_INGESTOR=$(terraform output -raw lambda_ingestor_function_name)

aws lambda update-function-code \
  --function-name ${LAMBDA_INGESTOR} \
  --zip-file fileb://lambda-ingestor.zip \
  --region ${AWS_REGION}

# Wait for update to complete
aws lambda wait function-updated \
  --function-name ${LAMBDA_INGESTOR} \
  --region ${AWS_REGION}
```

---

## Post-Deployment Configuration

### 1. Configure Secrets

```bash
# Get secrets manager ARN
export SECRETS_ARN=$(terraform output -raw api_keys_secret_arn)

# Update API keys (if you have them)
aws secretsmanager update-secret \
  --secret-id ${SECRETS_ARN} \
  --secret-string '{
    "news_api_key": "your-newsapi-key",
    "screener_api_key": "your-screener-key"
  }' \
  --region ${AWS_REGION}
```

### 2. Create Initial Admin User (Optional)

```bash
export USER_POOL_ID=$(terraform output -raw cognito_user_pool_id)

aws cognito-idp admin-create-user \
  --user-pool-id ${USER_POOL_ID} \
  --username admin@example.com \
  --user-attributes Name=email,Value=admin@example.com Name=email_verified,Value=true \
  --temporary-password "TempPassword123!" \
  --message-action SUPPRESS \
  --region ${AWS_REGION}
```

### 3. Trigger Initial Data Ingestion

```bash
# Invoke Lambda manually for initial data load
aws lambda invoke \
  --function-name ${LAMBDA_INGESTOR} \
  --payload '{"ingestion_type": "manual"}' \
  response.json \
  --region ${AWS_REGION}

# Check response
cat response.json
```

### 4. Configure CloudWatch Alarms

```bash
# Subscribe to alarm notifications
export SNS_TOPIC=$(terraform output -raw alarm_sns_topic_arn)

aws sns subscribe \
  --topic-arn ${SNS_TOPIC} \
  --protocol email \
  --notification-endpoint your-email@example.com \
  --region ${AWS_REGION}

# Confirm subscription in your email
```

---

## Validation

### 1. Health Check

```bash
export API_URL=$(terraform output -raw alb_dns_name)

# Basic health check
curl -s https://${API_URL}/health | jq

# Expected output:
# {
#   "status": "healthy",
#   "timestamp": "2024-01-15T10:30:00Z",
#   "environment": "dev",
#   "version": "1.0.0"
# }

# Detailed health check
curl -s https://${API_URL}/health/detailed | jq
```

### 2. Test Backend API

```bash
# Test stock search
curl -s "https://${API_URL}/api/v1/stocks/search?query=TCS" | jq

# Test chat endpoint (requires authentication)
# Get a token first via Cognito, then:
curl -X POST https://${API_URL}/api/v1/chat/message \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Analyze TCS stock",
    "session_id": null
  }' | jq
```

### 3. Test Frontend

```bash
export FRONTEND_URL=$(terraform output -raw frontend_url)

# Open in browser
open ${FRONTEND_URL}

# Or curl
curl -I ${FRONTEND_URL}
# Should return 200 OK
```

### 4. Verify OpenSearch

```bash
export OPENSEARCH_ENDPOINT=$(terraform output -raw opensearch_endpoint)

# Check cluster health (from within VPC or via VPN)
curl -u admin:Admin@12345 "https://${OPENSEARCH_ENDPOINT}/_cluster/health" | jq

# Check if index exists
curl -u admin:Admin@12345 "https://${OPENSEARCH_ENDPOINT}/stock-documents/_count" | jq
```

### 5. Check Logs

```bash
export LOG_GROUP=$(terraform output -raw cloudwatch_log_group_name)

# Tail backend logs
aws logs tail ${LOG_GROUP} --follow --region ${AWS_REGION}

# Check Lambda logs
aws logs tail /aws/lambda/${LAMBDA_INGESTOR} --follow --region ${AWS_REGION}
```

---

## Rollback Procedure

### Quick Rollback (Application Only)

```bash
# Rollback ECS service to previous task definition
aws ecs update-service \
  --cluster ${CLUSTER_NAME} \
  --service ${SERVICE_NAME} \
  --task-definition <PREVIOUS_TASK_DEF_ARN> \
  --region ${AWS_REGION}

# Rollback frontend
# Get previous CloudFront version (if enabled)
aws cloudfront get-distribution --id ${CLOUDFRONT_ID} | jq '.Distribution.DistributionConfig.DefaultCacheBehavior.OriginRequestPolicyId'

# Or restore from S3 versioning
aws s3api list-object-versions --bucket ${FRONTEND_BUCKET} | jq
```

### Full Infrastructure Rollback

```bash
# Revert to previous Terraform state
terraform state pull > current-state.json

# Restore from backup
terraform state push previous-state.json

# Apply previous configuration
terraform apply
```

### Emergency Rollback (Complete Teardown)

```bash
# Only if deployment is completely broken
terraform destroy -auto-approve

# This will DELETE all resources
# Make sure to backup data first!
```

---

## Monitoring Post-Deployment

### CloudWatch Dashboard

```bash
# Get dashboard URL
export DASHBOARD_URL=$(terraform output -raw cloudwatch_dashboard_url)
echo "Dashboard: ${DASHBOARD_URL}"
```

### Key Metrics to Monitor

1. **ECS Service**
   - CPU Utilization (target: <70%)
   - Memory Utilization (target: <80%)
   - Task count (should match desired count)

2. **API Gateway / ALB**
   - Request count
   - Error rate (target: <1%)
   - Latency (p99 <30s)

3. **Bedrock**
   - Invocation count
   - Token usage
   - Error rate

4. **OpenSearch**
   - Cluster status (should be green)
   - Search latency
   - Indexing rate

5. **Lambda Functions**
   - Invocation count
   - Error rate
   - Duration

---

## Cost Optimization Tips

### For Development/Testing

```hcl
# In terraform.tfvars:
backend_desired_count = 1           # Reduce from 2
opensearch_instance_count = 1       # Reduce from 2
redis_num_cache_nodes = 1           # Already minimal
enable_nat_gateway = true
single_nat_gateway = true           # Use single NAT
```

### Estimated Monthly Costs (Dev Environment)

| Service | Cost (USD) |
|---------|-----------|
| ECS Fargate (1 task) | ~$30 |
| OpenSearch (1 node) | ~$50 |
| NAT Gateway | ~$32 |
| ALB | ~$20 |
| Bedrock (moderate usage) | ~$50 |
| DynamoDB (on-demand) | ~$5 |
| S3 + CloudFront | ~$5 |
| **Total** | **~$192/month** |

### For Production

- Enable auto-scaling
- Use Reserved Instances for predictable workloads
- Implement caching aggressively
- Use CloudWatch cost anomaly detection
- Set up billing alarms

---

## Troubleshooting Common Issues

### Issue: Terraform Apply Fails on OpenSearch

**Error:** `Error creating OpenSearch domain: LimitExceededException`

**Solution:**
```bash
# Check service quotas
aws service-quotas list-service-quotas \
  --service-code es \
  --region ${AWS_REGION}

# Request quota increase if needed
aws service-quotas request-service-quota-increase \
  --service-code es \
  --quota-code L-XXXXXX \
  --desired-value 5
```

### Issue: ECS Task Fails to Start

**Error:** Task stopped with exit code 1

**Solution:**
```bash
# Check task logs
aws ecs describe-tasks \
  --cluster ${CLUSTER_NAME} \
  --tasks $(aws ecs list-tasks --cluster ${CLUSTER_NAME} --service ${SERVICE_NAME} --query 'taskArns[0]' --output text) \
  --region ${AWS_REGION}

# Check CloudWatch logs
aws logs get-log-events \
  --log-group-name ${LOG_GROUP} \
  --log-stream-name <STREAM_NAME> \
  --region ${AWS_REGION}
```

### Issue: Frontend Shows API Connection Error

**Solution:**
```bash
# Verify CORS settings
# Check ALB security group allows traffic from CloudFront

# Test API directly
curl https://${API_URL}/health

# Check CloudFront origin settings
aws cloudfront get-distribution-config --id ${CLOUDFRONT_ID}
```

---

## Next Steps

After successful deployment:

1. ✅ Review [RUNBOOK.md](RUNBOOK.md) for operational procedures
2. ✅ Read [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
3. ✅ Set up monitoring alerts
4. ✅ Configure backup procedures
5. ✅ Review [SECURITY.md](../security/SECURITY.md) hardening checklist
6. ✅ Plan for production migration

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/LearningGallery/nifty-stock-intelligence/issues
- Contact: Im-AbuTalha (LinkedIn)

---

**Last Updated:** 2024-01-15
