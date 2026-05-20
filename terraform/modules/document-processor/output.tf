output "lambda_function_name" {
  description = "Document processor Lambda function name"
  value       = aws_lambda_function.document_processor.function_name
}

output "lambda_function_arn" {
  description = "Document processor Lambda function ARN"
  value       = aws_lambda_function.document_processor.arn
}

output "lambda_role_arn" {
  description = "IAM role ARN used by the document processor Lambda"
  value       = aws_iam_role.lambda_role.arn
}

output "upload_bucket_name" {
  description = "S3 upload bucket name"
  value       = aws_s3_bucket.uploads.id
}

output "upload_bucket_arn" {
  description = "S3 upload bucket ARN"
  value       = aws_s3_bucket.uploads.arn
}
