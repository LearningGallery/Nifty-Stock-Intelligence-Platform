resource "random_id" "suffix" {
  byte_length = 4
}

# ---------------------------------------------------------
# S3 Upload Bucket
# ---------------------------------------------------------
resource "aws_s3_bucket" "uploads" {
  bucket = var.upload_bucket_name != "" ? var.upload_bucket_name : "${var.project_name}-${var.environment}-uploads-${random_id.suffix.hex}"

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-uploads"
    }
  )
}

resource "aws_s3_bucket_versioning" "uploads" {
  bucket = aws_s3_bucket.uploads.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "uploads" {
  bucket = aws_s3_bucket.uploads.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = var.s3_sse_algorithm
    }
  }
}

resource "aws_s3_bucket_public_access_block" "uploads" {
  bucket = aws_s3_bucket.uploads.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "uploads" {
  bucket = aws_s3_bucket.uploads.id

  rule {
    id     = "delete-old-uploads"
    status = "Enabled"

    filter {}

    expiration {
      days = var.upload_expiration_days
    }

    noncurrent_version_expiration {
      noncurrent_days = var.noncurrent_version_expiration_days
    }
  }
}

# ---------------------------------------------------------
# IAM Role for Lambda
# ---------------------------------------------------------
resource "aws_iam_role" "lambda_role" {
  name_prefix = "${var.project_name}-${var.environment}-doc-processor-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "LambdaAssumeRole"
        Effect = "Allow"
        Action = "sts:AssumeRole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "document_processor_policy" {
  name = "${var.project_name}-${var.environment}-doc-processor-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "TextractAccess"
        Effect = "Allow"
        Action = [
          "textract:StartDocumentTextDetection",
          "textract:GetDocumentTextDetection"
        ]
        Resource = "*"
      },
      {
        Sid    = "S3UploadBucketAccess"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "${aws_s3_bucket.uploads.arn}/*"
      },
      {
        Sid    = "S3BucketListAccess"
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.uploads.arn
      },
      {
        Sid    = "BedrockInvoke"
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = "*"
      },
      {
        Sid    = "DynamoDBAccess"
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query"
        ]
        Resource = var.document_metadata_table_arn
      },
      {
        Sid    = "OpenSearchAccess"
        Effect = "Allow"
        Action = [
          "es:ESHttpGet",
          "es:ESHttpPost",
          "es:ESHttpPut",
          "es:ESHttpDelete",
          "aoss:APIAccessAll"
        ]
        Resource = "*"
      }
    ]
  })
}

# ---------------------------------------------------------
# VPC Access for Lambda
# ---------------------------------------------------------
resource "aws_iam_role_policy_attachment" "lambda_vpc_access" {
  count      = var.enable_vpc_config ? 1 : 0
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# ---------------------------------------------------------
# Lambda Function
# ---------------------------------------------------------
resource "aws_lambda_function" "document_processor" {
  function_name = "${var.project_name}-${var.environment}-doc-processor"
  role          = aws_iam_role.lambda_role.arn
  handler       = var.lambda_handler
  runtime       = var.lambda_runtime
  timeout       = var.lambda_timeout
  memory_size   = var.lambda_memory_size

  filename         = var.lambda_filename
  source_code_hash = filebase64sha256(var.lambda_filename)

  environment {
    variables = merge(
      {
        OPENSEARCH_ENDPOINT      = var.opensearch_endpoint
        OPENSEARCH_INDEX         = var.opensearch_index
        BEDROCK_EMBEDDING_MODEL  = var.bedrock_embedding_model
        DOCUMENT_METADATA_TABLE  = var.document_metadata_table_name
        #AWS_REGION               = var.aws_region
        UPLOAD_BUCKET            = aws_s3_bucket.uploads.id
      },
      var.lambda_environment_variables
    )
  }

  dynamic "vpc_config" {
    for_each = var.enable_vpc_config ? [1] : []
    content {
      subnet_ids         = var.subnet_ids
      security_group_ids = var.security_group_ids
    }
  }

  tags = var.tags

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic_execution,
    aws_iam_role_policy.document_processor_policy
  ]
}

# ---------------------------------------------------------
# S3 Notification to Lambda
# ---------------------------------------------------------
resource "aws_lambda_permission" "allow_s3_pdf" {
  statement_id  = "AllowExecutionFromS3Pdf"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.document_processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.uploads.arn
}

resource "aws_s3_bucket_notification" "uploads" {
  bucket = aws_s3_bucket.uploads.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.document_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = var.upload_filter_prefix
    filter_suffix       = ".pdf"
  }

  lambda_function {
    lambda_function_arn = aws_lambda_function.document_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = var.upload_filter_prefix
    filter_suffix       = ".xlsx"
  }

  lambda_function {
    lambda_function_arn = aws_lambda_function.document_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = var.upload_filter_prefix
    filter_suffix       = ".xls"
  }

  depends_on = [
    aws_lambda_permission.allow_s3_pdf
  ]
}
