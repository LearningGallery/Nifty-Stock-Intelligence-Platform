# ---------------------------------------------------------
# Data Sources
# ---------------------------------------------------------
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# ---------------------------------------------------------
# CloudWatch Log Group for Bedrock
# ---------------------------------------------------------
resource "aws_cloudwatch_log_group" "bedrock_logging" {
  name              = "/aws/bedrock/${var.project_name}-${var.environment}-invocations"
  retention_in_days = var.log_retention_days

  tags = var.tags
}

# ---------------------------------------------------------
# IAM Role for Bedrock Logging
# ---------------------------------------------------------
resource "aws_iam_role" "bedrock_logging" {
  name_prefix = "bedrock-log-${var.environment}-" # Short prefix to avoid length limits

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "bedrock.amazonaws.com"
        }
        Action = "sts:AssumeRole"
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
          ArnLike = {
            "aws:SourceArn" = "arn:aws:bedrock:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*"
          }
        }
      }
    ]
  })

  tags = var.tags
}

# ---------------------------------------------------------
# IAM Policy for Bedrock Logging
# ---------------------------------------------------------
resource "aws_iam_role_policy" "bedrock_logging_policy" {
  name = "${var.project_name}-${var.environment}-bedrock-log-policy"
  role = aws_iam_role.bedrock_logging.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.bedrock_logging.arn}:*"
      }
    ]
  })
}

# ---------------------------------------------------------
# Enable Bedrock Model Invocation Logging Natively
# ---------------------------------------------------------
resource "aws_bedrock_model_invocation_logging_configuration" "main" {
  depends_on = [aws_iam_role_policy.bedrock_logging_policy]

  logging_config {
    embedding_data_delivery_enabled = true
    image_data_delivery_enabled     = false
    text_data_delivery_enabled      = true

    cloudwatch_config {
      log_group_name              = aws_cloudwatch_log_group.bedrock_logging.name
      role_arn                    = aws_iam_role.bedrock_logging.arn
    }
  }
}