# ---------------------------------------------------------
# Data Lake S3 Bucket
# ---------------------------------------------------------
resource "random_id" "suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "data_lake" {
  bucket = "${var.project_name}-${var.environment}-data-lake-${random_id.suffix.hex}"
  tags   = merge(var.tags, { Name = "${var.project_name}-${var.environment}-data-lake" })
}

resource "aws_s3_bucket_versioning" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_lifecycle_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id
  rule {
    id     = "archive-old-data"
    status = "Enabled"
    filter {}
    transition { 
     days = 90
     storage_class = "GLACIER"
     }
    expiration {
      days = 365
      }
  }
}

# ---------------------------------------------------------
# S3 Deployment Bucket & Objects
# ---------------------------------------------------------
resource "aws_s3_bucket" "deployment_bucket" {
  bucket = "${var.project_name}-${var.environment}-lambda-deployments"
}

resource "aws_s3_object" "ingestor_zip" {
  bucket = aws_s3_bucket.deployment_bucket.id
  key    = "lambda-ingestor.zip"
  source = var.lambda_filename
  etag   = filemd5(var.lambda_filename)
}

resource "aws_s3_object" "etl_zip" {
  bucket = aws_s3_bucket.deployment_bucket.id
  key    = "lambda-etl.zip"
  source = var.etl_lambda_filename
  etag   = filemd5(var.etl_lambda_filename)
}

# ---------------------------------------------------------
# IAM Roles & Policies
# ---------------------------------------------------------
resource "aws_iam_role" "lambda_ingestor" {
  name_prefix = "${var.project_name}-${var.environment}-ingestor-"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{ Effect = "Allow", Principal = { Service = "lambda.amazonaws.com" }, Action = "sts:AssumeRole" }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_ingestor.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "ingestor_policy" {
  name = "${var.project_name}-${var.environment}-ingestor-policy"
  role = aws_iam_role.lambda_ingestor.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      { Effect = "Allow", Action = ["s3:PutObject", "s3:GetObject", "s3:ListBucket"], Resource = [aws_s3_bucket.data_lake.arn, "${aws_s3_bucket.data_lake.arn}/*"] },
      { Effect = "Allow", Action = ["secretsmanager:GetSecretValue"], Resource = "*" }
    ]
  })
}

resource "aws_iam_role" "lambda_etl" {
  name_prefix = "${var.project_name}-${var.environment}-etl-"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{ Effect = "Allow", Principal = { Service = "lambda.amazonaws.com" }, Action = "sts:AssumeRole" }]
  })
}

resource "aws_iam_role_policy_attachment" "etl_basic" {
  role = aws_iam_role.lambda_etl.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  }
resource "aws_iam_role_policy_attachment" "etl_vpc" {
  role = aws_iam_role.lambda_etl.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
  }

resource "aws_iam_role_policy" "etl_policy" {
  name = "${var.project_name}-${var.environment}-etl-policy"
  role = aws_iam_role.lambda_etl.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      { Effect = "Allow", Action = ["s3:GetObject", "s3:ListBucket"], Resource = [aws_s3_bucket.data_lake.arn, "${aws_s3_bucket.data_lake.arn}/*"] },
      { Effect = "Allow", Action = ["bedrock:InvokeModel"], Resource = "*" },
      { Effect = "Allow", Action = ["es:ESHttpPost", "es:ESHttpPut", "aoss:APIAccessAll"], Resource = var.opensearch_domain_arn },
      { Effect = "Allow", Action = ["dynamodb:PutItem", "dynamodb:UpdateItem"], Resource = var.document_metadata_table_arn }
    ]
  })
}

# ---------------------------------------------------------
# Lambda Functions
# ---------------------------------------------------------
resource "aws_lambda_function" "ingestor" {
  function_name = "${var.project_name}-${var.environment}-ingestor"
  role          = aws_iam_role.lambda_ingestor.arn
  handler       = "handler.lambda_handler"
  runtime       = var.lambda_runtime
  timeout       = var.lambda_timeout
  memory_size   = var.lambda_memory_size
  s3_bucket     = aws_s3_bucket.deployment_bucket.id
  s3_key        = aws_s3_object.ingestor_zip.key
  source_code_hash = filebase64sha256(var.lambda_filename)
  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = var.security_group_ids
  }
  environment { variables = { DATA_LAKE_BUCKET = aws_s3_bucket.data_lake.id } }
  tags       = var.tags
  depends_on = [aws_s3_object.ingestor_zip]
}

# Attach the VPC Access Execution role policy
resource "aws_iam_role_policy_attachment" "ingestor_vpc_access" {
  role       = aws_iam_role.lambda_ingestor.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_lambda_function" "etl" {
  function_name = "${var.project_name}-${var.environment}-etl"
  role          = aws_iam_role.lambda_etl.arn
  handler       = "etl_handler.lambda_handler"
  runtime       = var.lambda_runtime
  timeout       = var.lambda_timeout
  memory_size   = var.lambda_memory_size
  s3_bucket     = aws_s3_bucket.deployment_bucket.id
  s3_key        = aws_s3_object.etl_zip.key
  source_code_hash = filebase64sha256(var.etl_lambda_filename)
  environment {
    variables = {
      OPENSEARCH_ENDPOINT     = var.opensearch_endpoint
      OPENSEARCH_INDEX        = var.opensearch_index
      BEDROCK_EMBEDDING_MODEL = var.bedrock_embedding_model
      DOCUMENT_METADATA_TABLE = var.document_metadata_table_name
    }
  }
  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = var.security_group_ids
  }
  tags       = var.tags
  depends_on = [aws_s3_object.etl_zip]
}

# ---------------------------------------------------------
# Triggers & Permissions
# ---------------------------------------------------------
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.etl.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.data_lake.arn
}

resource "aws_s3_bucket_notification" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id
  lambda_function {
    lambda_function_arn = aws_lambda_function.etl.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "raw/stocks/"
    filter_suffix       = ".json"
  }
  depends_on = [aws_lambda_permission.allow_s3]
}

resource "aws_cloudwatch_event_rule" "ingestor_schedule" {
  name                = "${var.project_name}-${var.environment}-ingestor-schedule"
  schedule_expression = var.ingestion_schedule_expression
}

resource "aws_cloudwatch_event_target" "ingestor" {
  rule      = aws_cloudwatch_event_rule.ingestor_schedule.name
  arn       = aws_lambda_function.ingestor.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ingestor.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.ingestor_schedule.arn
}