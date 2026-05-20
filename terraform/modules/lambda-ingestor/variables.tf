variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "lambda_filename" {
  description = "Lambda ingestor deployment package"
  type        = string
}

variable "etl_lambda_filename" {
  description = "Lambda ETL deployment package"
  type        = string
}

variable "lambda_runtime" {
  description = "Lambda runtime"
  type        = string
  default     = "python3.11"
}

variable "lambda_timeout" {
  description = "Lambda timeout"
  type        = number
  default     = 300
}

variable "lambda_memory_size" {
  description = "Lambda memory"
  type        = number
  default     = 512
}

variable "ingestion_schedule_expression" {
  description = "EventBridge schedule"
  type        = string
  default     = "rate(30 minutes)"
}

variable "opensearch_endpoint" {
  description = "OpenSearch endpoint"
  type        = string
}

variable "opensearch_index" {
  description = "OpenSearch index"
  type        = string
  default     = "stock-documents"
}

variable "opensearch_domain_arn" {
  description = "OpenSearch domain ARN"
  type        = string
}

variable "bedrock_embedding_model" {
  description = "Bedrock embedding model ID"
  type        = string
}

variable "document_metadata_table_name" {
  description = "DynamoDB table name"
  type        = string
}

variable "document_metadata_table_arn" {
  description = "DynamoDB table ARN"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs for VPC config"
  type        = list(string)
}

variable "security_group_ids" {
  description = "Security group IDs"
  type        = list(string)
}

variable "tags" {
  description = "Tags"
  type        = map(string)
  default     = {}
}
