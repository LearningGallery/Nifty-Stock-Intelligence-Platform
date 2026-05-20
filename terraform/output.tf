# ---------------------------------------------------------
# VPC Outputs
# ---------------------------------------------------------
output "vpc_id" {
  description = "VPC ID"
  value       = module.networking.vpc_id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.networking.private_subnet_ids
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.networking.public_subnet_ids
}

# ---------------------------------------------------------
# ECS Outputs
# ---------------------------------------------------------
output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = module.ecs_cluster.cluster_name
}

output "backend_service_name" {
  description = "Backend ECS service name"
  value       = module.backend_service.service_name
}

output "backend_task_definition_arn" {
  description = "Backend task definition ARN"
  value       = module.backend_service.task_definition_arn
}

# ---------------------------------------------------------
# Load Balancer Outputs
# ---------------------------------------------------------
output "alb_dns_name" {
  description = "Application Load Balancer DNS name"
  value       = module.backend_service.alb_dns_name
}

output "alb_zone_id" {
  description = "ALB hosted zone ID"
  value       = module.backend_service.alb_zone_id
}

# ---------------------------------------------------------
# CloudFront Outputs
# ---------------------------------------------------------
output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = module.cloudfront.distribution_id
}

output "cloudfront_domain_name" {
  description = "CloudFront domain name"
  value       = module.cloudfront.domain_name
}

output "frontend_url" {
  description = "Frontend application URL"
  value       = "https://${module.cloudfront.domain_name}"
}

# ---------------------------------------------------------
# S3 Outputs
# ---------------------------------------------------------
output "frontend_bucket_name" {
  description = "Frontend S3 bucket name"
  value       = module.cloudfront.frontend_bucket_name
}

output "data_lake_bucket_name" {
  description = "Data lake S3 bucket name"
  value       = module.lambda_ingestor.data_lake_bucket_name
}

# ---------------------------------------------------------
# OpenSearch Outputs
# ---------------------------------------------------------
output "opensearch_endpoint" {
  description = "OpenSearch endpoint"
  value       = module.opensearch.endpoint
  sensitive   = true
}

output "opensearch_dashboard_endpoint" {
  description = "OpenSearch Dashboards endpoint"
  value       = module.opensearch.dashboard_endpoint
}

# ---------------------------------------------------------
# DynamoDB Outputs
# ---------------------------------------------------------
output "chat_sessions_table_name" {
  description = "Chat sessions DynamoDB table name"
  value       = module.dynamodb.chat_sessions_table_name
}

output "chat_messages_table_name" {
  description = "Chat messages DynamoDB table name"
  value       = module.dynamodb.chat_messages_table_name
}

output "document_metadata_table_name" {
  description = "Document metadata table name"
  value       = module.dynamodb.document_metadata_table_name
}

# ---------------------------------------------------------
# Cognito Outputs
# ---------------------------------------------------------
output "cognito_user_pool_id" {
  description = "Cognito User Pool ID"
  value       = module.cognito.user_pool_id
}

output "cognito_user_pool_client_id" {
  description = "Cognito User Pool Client ID"
  value       = module.cognito.user_pool_client_id
  sensitive   = true
}

output "cognito_domain" {
  description = "Cognito hosted UI domain"
  value       = module.cognito.domain
}

# ---------------------------------------------------------
# Lambda Outputs
# ---------------------------------------------------------
output "lambda_ingestor_function_name" {
  description = "Lambda ingestor function name"
  value       = module.lambda_ingestor.function_name
}

output "lambda_etl_function_name" {
  description = "Lambda ETL function name"
  value       = module.lambda_ingestor.etl_function_name
}

# ---------------------------------------------------------
# ElastiCache Outputs
# ---------------------------------------------------------
output "redis_endpoint" {
  description = "Redis endpoint"
  value       = module.backend_service.redis_endpoint
  sensitive   = true
}

# ---------------------------------------------------------
# ECR Outputs
# ---------------------------------------------------------
output "backend_ecr_repository_url" {
  description = "Backend ECR repository URL"
  value       = module.backend_service.ecr_repository_url
}

# ---------------------------------------------------------
# Monitoring Outputs
# ---------------------------------------------------------
output "cloudwatch_log_group_name" {
  description = "CloudWatch log group name"
  value       = module.monitoring.log_group_name
}

output "cloudwatch_dashboard_url" {
  description = "CloudWatch dashboard URL"
  value       = module.monitoring.dashboard_url
}

# ---------------------------------------------------------
# Security Outputs
# ---------------------------------------------------------
output "waf_web_acl_id" {
  description = "WAF Web ACL ID"
  value       = module.waf.web_acl_id
}

# ---------------------------------------------------------
# Secrets Manager Outputs
# ---------------------------------------------------------
output "api_keys_secret_arn" {
  description = "API keys secret ARN"
  value       = module.backend_service.api_keys_secret_arn
}

# ---------------------------------------------------------
# Quick Access Commands
# ---------------------------------------------------------
output "useful_commands" {
  description = "Useful commands for operations"
  value = <<-EOT
    # Access Backend Logs:
    aws logs tail ${module.monitoring.log_group_name} --follow --region ${var.aws_region}
    
    # Update Backend Service:
    aws ecs update-service --cluster ${module.ecs_cluster.cluster_name} --service ${module.backend_service.service_name} --force-new-deployment --region ${var.aws_region}
    
    # Invalidate CloudFront Cache:
    aws cloudfront create-invalidation --distribution-id ${module.cloudfront.distribution_id} --paths "/*"
    
    # Access OpenSearch Dashboard:
    ${module.opensearch.dashboard_endpoint}
    
    # Frontend URL:
    https://${module.cloudfront.domain_name}
    
    # Backend API URL:
    https://${module.backend_service.alb_dns_name}
  EOT
}

output "document_processor_lambda_function_name" {
  description = "Document processor Lambda function name"
  value       = module.document_processor.lambda_function_name
}

output "document_upload_bucket_name" {
  description = "Document upload bucket name"
  value       = module.document_processor.upload_bucket_name
}

output "document_upload_bucket_arn" {
  description = "Document upload bucket ARN"
  value       = module.document_processor.upload_bucket_arn
}
