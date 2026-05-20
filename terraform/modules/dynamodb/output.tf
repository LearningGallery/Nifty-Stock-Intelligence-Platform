output "chat_sessions_table_name" {
  description = "Chat sessions table name"
  value       = aws_dynamodb_table.chat_sessions.name
}

output "chat_sessions_table_arn" {
  description = "Chat sessions table ARN"
  value       = aws_dynamodb_table.chat_sessions.arn
}

output "chat_messages_table_name" {
  description = "Chat messages table name"
  value       = aws_dynamodb_table.chat_messages.name
}

output "chat_messages_table_arn" {
  description = "Chat messages table ARN"
  value       = aws_dynamodb_table.chat_messages.arn
}

output "document_metadata_table_name" {
  description = "Document metadata table name"
  value       = aws_dynamodb_table.document_metadata.name
}

output "document_metadata_table_arn" {
  description = "Document metadata table ARN"
  value       = aws_dynamodb_table.document_metadata.arn
}

output "stock_analysis_cache_table_name" {
  description = "Stock analysis cache table name"
  value       = aws_dynamodb_table.stock_analysis_cache.name
}

output "stock_analysis_cache_table_arn" {
  description = "Stock analysis cache table ARN"
  value       = aws_dynamodb_table.stock_analysis_cache.arn
}
