# ---------------------------------------------------------
# General Configuration
# ---------------------------------------------------------
variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "nifty-stock-intel"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "ap-south-1" # Mumbai region for India-focused app
}

variable "aws_account_id" {
  description = "AWS account ID"
  type        = string
}

# ---------------------------------------------------------
# Networking Configuration
# ---------------------------------------------------------
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones for multi-AZ deployment"
  type        = list(string)
  default     = ["ap-south-1a", "ap-south-1b"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24"]
}

# ---------------------------------------------------------
# ECS Configuration
# ---------------------------------------------------------
variable "backend_image_tag" {
  description = "Docker image tag for backend service"
  type        = string
  default     = "latest"
}

variable "backend_cpu" {
  description = "CPU units for backend task"
  type        = number
  default     = 1024 # 1 vCPU
}

variable "backend_memory" {
  description = "Memory (MB) for backend task"
  type        = number
  default     = 2048 # 2 GB
}

variable "backend_desired_count" {
  description = "Desired number of backend tasks"
  type        = number
  default     = 2
}

variable "backend_auto_scaling_min" {
  description = "Minimum tasks for auto-scaling"
  type        = number
  default     = 1
}

variable "backend_auto_scaling_max" {
  description = "Maximum tasks for auto-scaling"
  type        = number
  default     = 10
}

# ---------------------------------------------------------
# Bedrock Configuration
# ---------------------------------------------------------
variable "bedrock_model_id" {
  description = "Bedrock model ID for LLM"
  type        = string
  default     = "anthropic.claude-3-5-sonnet-20240620-v1:0"
}

variable "bedrock_embedding_model_id" {
  description = "Bedrock embedding model ID"
  type        = string
  default     = "amazon.titan-embed-text-v2:0"
}

variable "bedrock_max_tokens" {
  description = "Maximum tokens for LLM response"
  type        = number
  default     = 4096
}

variable "bedrock_temperature" {
  description = "Temperature for LLM sampling"
  type        = number
  default     = 0.7
}

# ---------------------------------------------------------
# OpenSearch Configuration
# ---------------------------------------------------------
variable "opensearch_instance_type" {
  description = "OpenSearch instance type"
  type        = string
  default     = "or1.medium.search" # Serverless alternative
}

variable "opensearch_instance_count" {
  description = "Number of OpenSearch instances"
  type        = number
  default     = 2
}

variable "opensearch_ebs_volume_size" {
  description = "EBS volume size (GB) for OpenSearch"
  type        = number
  default     = 100
}

variable "opensearch_version" {
  description = "OpenSearch version"
  type        = string
  default     = "2.11"
}

# ---------------------------------------------------------
# DynamoDB Configuration
# ---------------------------------------------------------
variable "dynamodb_billing_mode" {
  description = "DynamoDB billing mode"
  type        = string
  default     = "PAY_PER_REQUEST"
}

variable "dynamodb_point_in_time_recovery" {
  description = "Enable point-in-time recovery"
  type        = bool
  default     = true
}

# ---------------------------------------------------------
# Cognito Configuration
# ---------------------------------------------------------
variable "cognito_password_minimum_length" {
  description = "Minimum password length"
  type        = number
  default     = 12
}

variable "cognito_mfa_configuration" {
  description = "MFA configuration (OFF, OPTIONAL, ON)"
  type        = string
  default     = "OPTIONAL"
}

# ---------------------------------------------------------
# Lambda Ingestor Configuration
# ---------------------------------------------------------
variable "lambda_runtime" {
  description = "Lambda runtime version"
  type        = string
  default     = "python3.11"
}

variable "lambda_memory_size" {
  description = "Lambda memory size (MB)"
  type        = number
  default     = 512
}

variable "lambda_timeout" {
  description = "Lambda timeout (seconds)"
  type        = number
  default     = 300
}

variable "ingestion_schedule_expression" {
  description = "EventBridge schedule for data ingestion"
  type        = string
  default     = "rate(30 minutes)" # Every 30 minutes during market hours
}

# ---------------------------------------------------------
# CloudFront Configuration
# ---------------------------------------------------------
variable "cloudfront_price_class" {
  description = "CloudFront price class"
  type        = string
  default     = "PriceClass_All"
}

# ---------------------------------------------------------
# WAF Configuration
# ---------------------------------------------------------
variable "waf_rate_limit" {
  description = "Rate limit (requests per 5 minutes)"
  type        = number
  default     = 2000
}

variable "waf_blocked_countries" {
  description = "List of country codes to block"
  type        = list(string)
  default     = [] # Empty for demo, add ["CN", "RU"] for production
}

# ---------------------------------------------------------
# Monitoring Configuration
# ---------------------------------------------------------
variable "cloudwatch_log_retention_days" {
  description = "CloudWatch log retention period"
  type        = number
  default     = 30
}

variable "enable_xray_tracing" {
  description = "Enable AWS X-Ray tracing"
  type        = bool
  default     = true
}

variable "alarm_email_endpoint" {
  description = "Email for CloudWatch alarms"
  type        = string
  default     = ""
}

# ---------------------------------------------------------
# ElastiCache Configuration
# ---------------------------------------------------------
variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "redis_num_cache_nodes" {
  description = "Number of cache nodes"
  type        = number
  default     = 1
}

variable "redis_engine_version" {
  description = "Redis engine version"
  type        = string
  default     = "7.0"
}

variable "news_api_key" {
  description = "API key for News Data"
  type        = string
  sensitive   = true
}

variable "screener_api_key" {
  description = "API key for Screener Data"
  type        = string
  sensitive   = true
}

# ---------------------------------------------------------
# Tags
# ---------------------------------------------------------
variable "additional_tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}
