output "service_name" {
  description = "ECS service name"
  value       = aws_ecs_service.backend.name
}

output "service_id" {
  description = "ECS service ID"
  value       = aws_ecs_service.backend.id
}

output "task_definition_arn" {
  description = "Task definition ARN"
  value       = aws_ecs_task_definition.backend.arn
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.backend.repository_url
}

output "alb_dns_name" {
  description = "ALB DNS name"
  value       = aws_lb.backend.dns_name
}

output "alb_arn" {
  description = "ALB ARN"
  value       = aws_lb.backend.arn
}

output "alb_arn_suffix" {
  description = "ALB ARN suffix for CloudWatch metrics"
  value       = aws_lb.backend.arn_suffix
}

output "alb_zone_id" {
  description = "ALB hosted zone ID"
  value       = aws_lb.backend.zone_id
}

output "target_group_arn" {
  description = "Target group ARN"
  value       = aws_lb_target_group.backend.arn
}

output "target_group_arn_suffix" {
  description = "Target group ARN suffix"
  value       = aws_lb_target_group.backend.arn_suffix
}

output "redis_endpoint" {
  description = "Redis endpoint"
  value       = var.enable_redis ? aws_elasticache_cluster.redis[0].cache_nodes[0].address : ""
}

output "api_keys_secret_arn" {
  description = "API keys secret ARN"
  value       = aws_secretsmanager_secret.api_keys.arn
}

output "task_role_arn" {
  description = "ECS task role ARN"
  value       = aws_iam_role.ecs_task.arn
}

output "execution_role_arn" {
  description = "ECS execution role ARN"
  value       = aws_iam_role.ecs_task_execution.arn
}
