variable "project_name" {
  description = "Project name used for naming resources"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "tags" {
  description = "Tags applied to resources"
  type        = map(string)
  default     = {}
}

# ---------------------------------------------------------
# Lambda Configuration
# ---------------------------------------------------------
variable "lambda_filename" {
  description = "Path to Lambda deployment package zip"
  type        = string
}

variable "lambda_handler" {
  description = "Lambda handler"
  type        = string
  default     = "document_processor_handler.lambda_handler"
}

variable "lambda_runtime" {
  description = "Lambda runtime"
  type        = string
  default     = "python3.11"
}

variable "lambda_timeout" {
  description = "Lambda timeout in seconds"
  type        = number
  default     = 900
}

variable "lambda_memory_size" {
  description = "Lambda memory size in MB"
  type        = number
  default     = 2048
}

variable "lambda_environment_variables" {
  description = "Additional Lambda environment variables"
  type        = map(string)
  default     = {}
}

# ---------------------------------------------------------
# VPC Configuration
# ---------------------------------------------------------
variable "enable_vpc_config" {
  description = "Whether to attach Lambda to VPC"
  type        = bool
  default     = true
}

variable "subnet_ids" {
  description = "Subnet IDs for Lambda VPC config"
  type        = list(string)
  default     = []
}

variable "security_group_ids" {
  description = "Security group IDs for Lambda VPC config"
  type        = list(string)
  default     = []
}

# ---------------------------------------------------------
# S3 Upload Bucket
# ---------------------------------------------------------
variable "upload_bucket_name" {
  description = "Optional custom upload bucket name"
  type        = string
  default     = ""
}

variable "upload_filter_prefix" {
  description = "S3 prefix filter for upload trigger"
  type        = string
  default     = "uploads/"
}

variable "upload_expiration_days" {
  description = "Days after which uploaded files expire"
  type        = number
  default     = 90
}

variable "noncurrent_version_expiration_days" {
  description = "Days after which noncurrent object versions expire"
  type        = number
  default     = 30
}

variable "s3_sse_algorithm" {
  description = "S3 server-side encryption algorithm"
  type        = string
  default     = "AES256"
}

# ---------------------------------------------------------
# OpenSearch / Bedrock / DynamoDB
# ---------------------------------------------------------
variable "opensearch_endpoint" {
  description = "OpenSearch endpoint"
  type        = string
}

variable "opensearch_index" {
  description = "OpenSearch index name"
  type        = string
  default     = "stock-documents"
}

variable "bedrock_embedding_model" {
  description = "Bedrock embedding model ID"
  type        = string
}

variable "document_metadata_table_name" {
  description = "DynamoDB document metadata table name"
  type        = string
}

variable "document_metadata_table_arn" {
  description = "DynamoDB document metadata table ARN"
  type        = string
}
