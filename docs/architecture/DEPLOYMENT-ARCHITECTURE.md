# Deployment Architecture

## Environments
- dev
- prod

## Deployment Units
- Terraform infrastructure
- Backend container image
- Frontend static build
- Lambda deployment packages

## Hosting Pattern
- Frontend: S3 + CloudFront
- Backend: ECS Fargate behind ALB
- Ingestion: Lambda + EventBridge + S3 events
- Data Stores: DynamoDB, OpenSearch, S3, Redis

## Network
- VPC with public/private subnets
- ALB in public subnets
- ECS/Lambda/OpenSearch in private subnets
- NAT for outbound internet where needed
- VPC endpoints for AWS services where feasible

## Security
- Security groups by tier
- IAM least privilege
- S3 private buckets
- WAF on CloudFront
