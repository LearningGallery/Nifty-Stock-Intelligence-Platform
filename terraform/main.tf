# ---------------------------------------------------------
# Data Sources
# ---------------------------------------------------------
data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

# ---------------------------------------------------------
# Random Suffix for Unique Resource Names
# ---------------------------------------------------------
resource "random_id" "suffix" {
  byte_length = 4
}

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.additional_tags
  )
}

# ---------------------------------------------------------
# Networking Module
# ---------------------------------------------------------
module "networking" {
  source = "./modules/networking"

  project_name           = var.project_name
  environment            = var.environment
  vpc_cidr               = var.vpc_cidr
  availability_zones     = var.availability_zones
  public_subnet_cidrs    = var.public_subnet_cidrs
  private_subnet_cidrs   = var.private_subnet_cidrs
  enable_nat_gateway     = true
  single_nat_gateway     = var.environment == "dev" ? true : false
  enable_dns_hostnames   = true
  enable_dns_support     = true
  enable_vpn_gateway     = false
  
  tags = local.common_tags
}

# ---------------------------------------------------------
# Security Groups Module
# ---------------------------------------------------------
module "security_groups" {
  source = "./modules/security-groups"

  vpc_id       = module.networking.vpc_id
  project_name = var.project_name
  environment  = var.environment
  
  tags = local.common_tags
}

# ---------------------------------------------------------
# ECS Cluster Module
# ---------------------------------------------------------
module "ecs_cluster" {
  source = "./modules/ecs-cluster"

  cluster_name          = "${local.name_prefix}-cluster"
  enable_container_insights = true
  
  tags = local.common_tags
}

# ---------------------------------------------------------
# DynamoDB Module
# ---------------------------------------------------------
module "dynamodb" {
  source = "./modules/dynamodb"

  project_name               = var.project_name
  environment                = var.environment
  billing_mode               = var.dynamodb_billing_mode
  point_in_time_recovery     = var.dynamodb_point_in_time_recovery
  
  tags = local.common_tags
}

# ---------------------------------------------------------
# OpenSearch Module
# ---------------------------------------------------------
module "opensearch" {
  source = "./modules/opensearch"

  domain_name               = "${local.name_prefix}-search"
  opensearch_version        = var.opensearch_version
  instance_type             = var.opensearch_instance_type
  instance_count            = var.opensearch_instance_count
  ebs_volume_size           = var.opensearch_ebs_volume_size
  vpc_id                    = module.networking.vpc_id
  subnet_ids                = module.networking.private_subnet_ids
  security_group_ids        = [module.security_groups.opensearch_sg_id]
  enable_node_to_node_encryption = true
  enable_encryption_at_rest = true
  
  tags = local.common_tags
}

# ---------------------------------------------------------
# Cognito Module
# ---------------------------------------------------------
module "cognito" {
  source = "./modules/cognito"

  user_pool_name            = "${local.name_prefix}-users"
  password_minimum_length   = var.cognito_password_minimum_length
  mfa_configuration         = var.cognito_mfa_configuration
  
  tags = local.common_tags
}

# ---------------------------------------------------------
# Lambda Ingestor Module
# ---------------------------------------------------------
module "lambda_ingestor" {
  source = "./modules/lambda-ingestor"

  project_name                  = var.project_name
  environment                   = var.environment
  aws_region                    = var.aws_region
  
  # File paths to your lambda deployment packages
  # (Make sure these zip files actually exist at these paths before applying)
  lambda_filename               = "../ingestor/lambda-ingestor.zip"
  etl_lambda_filename           = "../ingestor/lambda-etl.zip"
  
  lambda_runtime                = var.lambda_runtime
  lambda_memory_size            = var.lambda_memory_size
  lambda_timeout                = var.lambda_timeout
  ingestion_schedule_expression = var.ingestion_schedule_expression
  
  subnet_ids                    = module.networking.private_subnet_ids
  security_group_ids            = [module.security_groups.lambda_sg_id]
  
  opensearch_endpoint           = module.opensearch.endpoint
  opensearch_domain_arn         = module.opensearch.domain_arn
  
  document_metadata_table_name  = module.dynamodb.document_metadata_table_name
  document_metadata_table_arn   = module.dynamodb.document_metadata_table_arn
  
  bedrock_embedding_model       = var.bedrock_embedding_model_id
  
  tags = local.common_tags
}

# ---------------------------------------------------------
# Backend Service Module (ECS Fargate)
# ---------------------------------------------------------
module "backend_service" {
  source = "./modules/backend-service"

  service_name              = "${local.name_prefix}-backend"
  cluster_id                = module.ecs_cluster.cluster_id
  cluster_name              = module.ecs_cluster.cluster_name
  
  task_cpu                  = var.backend_cpu
  task_memory               = var.backend_memory
  desired_count             = var.backend_desired_count
  
  image_tag                 = var.backend_image_tag
  ecr_repository_name       = "${local.name_prefix}-backend"
  
  vpc_id                    = module.networking.vpc_id
  private_subnet_ids        = module.networking.private_subnet_ids
  public_subnet_ids         = module.networking.public_subnet_ids
  
  alb_security_group_id     = module.security_groups.alb_sg_id
  ecs_security_group_id     = module.security_groups.ecs_sg_id
  
  # Environment variables
  environment_variables = {
    ENVIRONMENT               = var.environment
    AWS_REGION                = var.aws_region
    
    # Bedrock
    BEDROCK_MODEL_ID          = var.bedrock_model_id
    BEDROCK_EMBEDDING_MODEL   = var.bedrock_embedding_model_id
    BEDROCK_MAX_TOKENS        = tostring(var.bedrock_max_tokens)
    BEDROCK_TEMPERATURE       = tostring(var.bedrock_temperature)
    
    # OpenSearch
    OPENSEARCH_ENDPOINT       = module.opensearch.endpoint
    OPENSEARCH_INDEX          = "stock-documents"
    
    # DynamoDB
    CHAT_SESSIONS_TABLE       = module.dynamodb.chat_sessions_table_name
    CHAT_MESSAGES_TABLE       = module.dynamodb.chat_messages_table_name
    DOCUMENT_METADATA_TABLE   = module.dynamodb.document_metadata_table_name
    
    # Cognito
    COGNITO_USER_POOL_ID      = module.cognito.user_pool_id
    COGNITO_CLIENT_ID         = module.cognito.user_pool_client_id
    
    # S3
    DATA_LAKE_BUCKET          = module.lambda_ingestor.data_lake_bucket_name
    
    # Cache
    REDIS_ENDPOINT            = "" # Will be set by module
    REDIS_PORT                = "6379"
    CACHE_TTL_SECONDS         = "300"
    
    # Application
    LOG_LEVEL                 = var.environment == "prod" ? "INFO" : "DEBUG"
    ENABLE_XRAY               = tostring(var.enable_xray_tracing)

    UPLOAD_BUCKET                = module.document_processor.upload_bucket_name
    DOCUMENT_PROCESSOR_LAMBDA    = module.document_processor.lambda_function_name

  }
  
  # Auto-scaling configuration
  auto_scaling_min_capacity = var.backend_auto_scaling_min
  auto_scaling_max_capacity = var.backend_auto_scaling_max
  auto_scaling_cpu_target   = 70
  auto_scaling_memory_target = 80
  
  # Redis cache
  enable_redis              = true
  redis_node_type           = var.redis_node_type
  redis_num_cache_nodes     = var.redis_num_cache_nodes
  redis_engine_version      = var.redis_engine_version
  
  # Health check
  health_check_path         = "/health"
  health_check_interval     = 30
  health_check_timeout      = 5
  healthy_threshold         = 2
  unhealthy_threshold       = 3
  
  tags = local.common_tags
}

# ---------------------------------------------------------
# WAF Module
# ---------------------------------------------------------
module "waf" {
  source = "./modules/waf"

  providers = {
    aws = aws.us_east_1
  }

  project_name      = var.project_name
  environment       = var.environment
  rate_limit        = var.waf_rate_limit
  blocked_countries = var.waf_blocked_countries
  
  tags = local.common_tags
}

# ---------------------------------------------------------
# CloudFront Module
# ---------------------------------------------------------
module "cloudfront" {
  source = "./modules/cloudfront"

  project_name              = var.project_name
  environment               = var.environment
  frontend_bucket_name      = "${local.name_prefix}-frontend-${random_id.suffix.hex}"
  alb_domain_name           = module.backend_service.alb_dns_name
  price_class               = var.cloudfront_price_class
  waf_web_acl_id            = module.waf.web_acl_arn
  
  tags = local.common_tags
}

# ---------------------------------------------------------
# Monitoring Module
# ---------------------------------------------------------
module "monitoring" {
  source = "./modules/monitoring"

  project_name              = var.project_name
  environment               = var.environment
  
  log_group_name            = "/aws/ecs/${local.name_prefix}"
  log_retention_days        = var.cloudwatch_log_retention_days
  
  ecs_cluster_name          = module.ecs_cluster.cluster_name
  ecs_service_name          = module.backend_service.service_name
  
  alb_arn_suffix            = module.backend_service.alb_arn_suffix
  target_group_arn_suffix   = module.backend_service.target_group_arn_suffix
  
  lambda_function_names     = [
    module.lambda_ingestor.function_name,
    module.lambda_ingestor.etl_function_name
  ]
  
  alarm_email_endpoint      = var.alarm_email_endpoint
  
  tags = local.common_tags
}

# Document Processor Module
module "document_processor" {
  source = "./modules/document-processor"

  project_name = var.project_name
  environment  = var.environment
  aws_region   = var.aws_region

  lambda_filename    = "../ingestor/lambda-doc-processor.zip"
  lambda_handler     = "document_processor_handler.lambda_handler"
  lambda_runtime     = "python3.11"
  lambda_timeout     = 900
  lambda_memory_size = 2048

  enable_vpc_config  = true
  subnet_ids         = module.networking.private_subnet_ids
  security_group_ids = [module.security_groups.lambda_sg_id]

  opensearch_endpoint         = module.opensearch.endpoint
  opensearch_index            = "stock-documents"
  bedrock_embedding_model     = var.bedrock_embedding_model_id
  document_metadata_table_name = module.dynamodb.document_metadata_table_name
  document_metadata_table_arn  = module.dynamodb.document_metadata_table_arn

  lambda_environment_variables = {
    LOG_LEVEL = var.environment == "prod" ? "INFO" : "DEBUG"
  }

  tags = local.common_tags
}
