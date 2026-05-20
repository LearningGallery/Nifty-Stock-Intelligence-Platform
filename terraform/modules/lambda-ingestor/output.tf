output "data_lake_bucket_name" {
  description = "Data lake S3 bucket name"
  value       = aws_s3_bucket.data_lake.id
}

output "data_lake_bucket_arn" {
  description = "Data lake S3 bucket ARN"
  value       = aws_s3_bucket.data_lake.arn
}

output "function_name" {
  description = "Ingestor Lambda function name"
  value       = aws_lambda_function.ingestor.function_name
}

output "etl_function_name" {
  description = "ETL Lambda function name"
  value       = aws_lambda_function.etl.function_name
}

