output "log_group_name" {
  description = "Bedrock CloudWatch log group name"
  value       = aws_cloudwatch_log_group.bedrock_logging.name
}

output "logging_role_arn" {
  description = "IAM role ARN used by Bedrock for logging"
  value       = aws_iam_role.bedrock_logging.arn
}