# ---------------------------------------------------------
# Chat Sessions Table
# ---------------------------------------------------------
resource "aws_dynamodb_table" "chat_sessions" {
  name           = "${var.project_name}-${var.environment}-chat-sessions"
  billing_mode   = var.billing_mode
  hash_key       = "session_id"
  range_key      = "created_at"

  attribute {
    name = "session_id"
    type = "S"
  }

  attribute {
    name = "created_at"
    type = "N"
  }

  attribute {
    name = "user_id"
    type = "S"
  }

  global_secondary_index {
    name            = "UserIdIndex"
    hash_key        = "user_id"
    range_key       = "created_at"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = var.point_in_time_recovery
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-chat-sessions"
    }
  )
}

# ---------------------------------------------------------
# Chat Messages Table
# ---------------------------------------------------------
resource "aws_dynamodb_table" "chat_messages" {
  name           = "${var.project_name}-${var.environment}-chat-messages"
  billing_mode   = var.billing_mode
  hash_key       = "session_id"
  range_key      = "message_id"

  attribute {
    name = "session_id"
    type = "S"
  }

  attribute {
    name = "message_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  local_secondary_index {
    name            = "TimestampIndex"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = var.point_in_time_recovery
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-chat-messages"
    }
  )
}

# ---------------------------------------------------------
# Document Metadata Table
# ---------------------------------------------------------
resource "aws_dynamodb_table" "document_metadata" {
  name           = "${var.project_name}-${var.environment}-document-metadata"
  billing_mode   = var.billing_mode
  hash_key       = "document_id"
  range_key      = "version"

  attribute {
    name = "document_id"
    type = "S"
  }

  attribute {
    name = "version"
    type = "N"
  }

  attribute {
    name = "stock_symbol"
    type = "S"
  }

  attribute {
    name = "document_type"
    type = "S"
  }

  attribute {
    name = "ingestion_timestamp"
    type = "N"
  }

  global_secondary_index {
    name            = "StockSymbolIndex"
    hash_key        = "stock_symbol"
    range_key       = "ingestion_timestamp"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "DocumentTypeIndex"
    hash_key        = "document_type"
    range_key       = "ingestion_timestamp"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = var.point_in_time_recovery
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-document-metadata"
    }
  )
}

# ---------------------------------------------------------
# Stock Analysis Cache Table
# ---------------------------------------------------------
resource "aws_dynamodb_table" "stock_analysis_cache" {
  name           = "${var.project_name}-${var.environment}-stock-analysis-cache"
  billing_mode   = var.billing_mode
  hash_key       = "stock_symbol"
  range_key      = "analysis_type"

  attribute {
    name = "stock_symbol"
    type = "S"
  }

  attribute {
    name = "analysis_type"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = var.point_in_time_recovery
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-stock-analysis-cache"
    }
  )
}
