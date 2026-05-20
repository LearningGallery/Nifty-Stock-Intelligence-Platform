# ---------------------------------------------------------
# OpenSearch Domain
# ---------------------------------------------------------
resource "aws_opensearch_domain" "main" {
  domain_name    = var.domain_name
  engine_version = "OpenSearch_${var.opensearch_version}"

  cluster_config {
    instance_type          = var.instance_type
    instance_count         = var.instance_count
    zone_awareness_enabled = var.instance_count > 1

    dynamic "zone_awareness_config" {
      for_each = var.instance_count > 1 ? [1] : []
      content {
        availability_zone_count = 2
      }
    }
  }

  ebs_options {
    ebs_enabled = true
    volume_size = var.ebs_volume_size
    volume_type = "gp3"
    iops        = 3000
    throughput  = 125
  }

  encrypt_at_rest {
    enabled = var.enable_encryption_at_rest
  }

  node_to_node_encryption {
    enabled = var.enable_node_to_node_encryption
  }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  vpc_options {
    subnet_ids         = var.instance_count > 1 ? var.subnet_ids : [var.subnet_ids[0]]
    security_group_ids = var.security_group_ids
  }

  advanced_options = {
    "rest.action.multi.allow_explicit_index" = "true"
    "override_main_response_version"         = "false"
  }

  access_policies = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "*"
        }
        Action   = "es:*"
        Resource = "arn:aws:es:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:domain/${var.domain_name}/*"
      }
    ]
  })

  advanced_security_options {
    enabled                        = true
    internal_user_database_enabled = true
    master_user_options {
      master_user_name     = var.master_user_name
      master_user_password = var.master_user_password
    }
  }

  log_publishing_options {
    cloudwatch_log_group_arn = aws_cloudwatch_log_group.opensearch_logs.arn
    log_type                 = "INDEX_SLOW_LOGS"
  }

  log_publishing_options {
    cloudwatch_log_group_arn = aws_cloudwatch_log_group.opensearch_logs.arn
    log_type                 = "SEARCH_SLOW_LOGS"
  }

  log_publishing_options {
    cloudwatch_log_group_arn = aws_cloudwatch_log_group.opensearch_application_logs.arn
    log_type                 = "ES_APPLICATION_LOGS"
  }

  tags = var.tags

  depends_on = [
    aws_cloudwatch_log_group.opensearch_logs,
    aws_cloudwatch_log_group.opensearch_application_logs
  ]
}

# ---------------------------------------------------------
# CloudWatch Log Groups
# ---------------------------------------------------------
resource "aws_cloudwatch_log_group" "opensearch_logs" {
  name              = "/aws/opensearch/${var.domain_name}/logs"
  retention_in_days = 30

  tags = var.tags
}

resource "aws_cloudwatch_log_group" "opensearch_application_logs" {
  name              = "/aws/opensearch/${var.domain_name}/application"
  retention_in_days = 30

  tags = var.tags
}

# ---------------------------------------------------------
# CloudWatch Log Resource Policy
# ---------------------------------------------------------
resource "aws_cloudwatch_log_resource_policy" "opensearch" {
  policy_name = "${var.domain_name}-opensearch-logs"

  policy_document = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "es.amazonaws.com"
        }
        Action = [
          "logs:PutLogEvents",
          "logs:CreateLogStream"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

/*
resource "aws_iam_service_linked_role" "opensearch" {
  aws_service_name = "opensearchservice.amazonaws.com"
  description      = "Service-linked role for Amazon OpenSearch Service VPC access"
  
  # Prevents crash if the role already exists in the AWS account
  lifecycle {
    ignore_changes = all
  }
}
*/

# ---------------------------------------------------------
# Data Sources
# ---------------------------------------------------------
data "aws_region" "current" {}
data "aws_caller_identity" "current" {}
