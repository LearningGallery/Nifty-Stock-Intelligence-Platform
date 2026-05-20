# ---------------------------------------------------------
# Data Sources
# ---------------------------------------------------------
data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

# ---------------------------------------------------------
# ECR Repository
# ---------------------------------------------------------
resource "aws_ecr_repository" "backend" {
  name                 = var.ecr_repository_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = var.tags
}

# ---------------------------------------------------------
# ECR Lifecycle Policy
# ---------------------------------------------------------
resource "aws_ecr_lifecycle_policy" "backend" {
  repository = aws_ecr_repository.backend.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["v"]
          countType     = "imageCountMoreThan"
          countNumber   = 10
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2
        description  = "Expire untagged images older than 7 days"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 7
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# ---------------------------------------------------------
# IAM Role for ECS Task Execution
# ---------------------------------------------------------
resource "aws_iam_role" "ecs_task_execution" {
  name_prefix = "ecs-exec-${var.tags["Environment"]}-" # 13 characters + variable = 17 chars (Well under 38)

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

# ---------------------------------------------------------
# Attach AWS Managed Policy for ECS Task Execution
# ---------------------------------------------------------
resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ---------------------------------------------------------
# Additional Permissions for Secrets and Parameters
# ---------------------------------------------------------
resource "aws_iam_role_policy" "ecs_task_execution_secrets" {
  name_prefix = "${var.service_name}-execution-secrets-"
  role        = aws_iam_role.ecs_task_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "ssm:GetParameters",
          "ssm:GetParameter",
          "kms:Decrypt"
        ]
        Resource = "*"
      }
    ]
  })
}

# ---------------------------------------------------------
# IAM Role for ECS Task
# ---------------------------------------------------------
resource "aws_iam_role" "ecs_task" {
  name_prefix = "${var.service_name}-task-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

# ---------------------------------------------------------
# IAM Policy for ECS Task (Application Permissions)
# ---------------------------------------------------------
resource "aws_iam_role_policy" "ecs_task" {
  name_prefix = "${var.service_name}-task-policy-"
  role        = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:DeleteItem",
          "dynamodb:BatchGetItem",
          "dynamodb:BatchWriteItem"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "es:ESHttpGet",
          "es:ESHttpPost",
          "es:ESHttpPut",
          "es:ESHttpDelete",
          "aoss:APIAccessAll"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# ---------------------------------------------------------
# CloudWatch Log Group
# ---------------------------------------------------------
resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/${var.service_name}"
  retention_in_days = 30

  tags = var.tags
}

# ---------------------------------------------------------
# ECS Task Definition
# ---------------------------------------------------------
resource "aws_ecs_task_definition" "backend" {
  family                   = var.service_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "backend"
      image     = "${aws_ecr_repository.backend.repository_url}:${var.image_tag}"
      essential = true

      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]

      environment = [
        for key, value in var.environment_variables : {
          name  = key
          value = value
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.backend.name
          "awslogs-region"        = data.aws_region.current.name
          "awslogs-stream-prefix" = "ecs"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = var.tags
}

# ---------------------------------------------------------
# Application Load Balancer
# ---------------------------------------------------------
resource "aws_lb" "backend" {
  name               = "${var.tags["Environment"]}-nsip-backend-alb" # 25 characters (Well under 32)
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.alb_security_group_id]
  subnets            = var.public_subnet_ids

  enable_deletion_protection = false
  enable_http2               = true
  enable_cross_zone_load_balancing = true

  tags = var.tags
}

# ---------------------------------------------------------
# ALB Target Group
# ---------------------------------------------------------
resource "aws_lb_target_group" "backend" {
  name        = "${var.service_name}-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = var.healthy_threshold
    unhealthy_threshold = var.unhealthy_threshold
    timeout             = var.health_check_timeout
    interval            = var.health_check_interval
    path                = var.health_check_path
    protocol            = "HTTP"
    matcher             = "200"
  }

  deregistration_delay = 30

  tags = var.tags
}

# ---------------------------------------------------------
# ALB Listener (HTTP -> HTTPS Redirect)
# ---------------------------------------------------------
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.backend.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# ---------------------------------------------------------
# ALB Listener (HTTPS) - Self-Signed Cert for Demo
# Note: In production, use ACM certificate
# ---------------------------------------------------------
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.backend.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = aws_acm_certificate.backend.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }
}

# ---------------------------------------------------------
# Self-Signed Certificate (Demo Only)
# Production: Use aws_acm_certificate with DNS validation
# ---------------------------------------------------------
resource "tls_private_key" "backend" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

resource "tls_self_signed_cert" "backend" {
  private_key_pem = tls_private_key.backend.private_key_pem

  subject {
    common_name  = aws_lb.backend.dns_name
    organization = "Nifty Stock Intelligence"
  }

  validity_period_hours = 8760 # 1 year

  allowed_uses = [
    "key_encipherment",
    "digital_signature",
    "server_auth",
  ]
}

resource "time_sleep" "wait_for_acm" {
  depends_on = [tls_self_signed_cert.backend]

  create_duration = "15s"
}

resource "aws_acm_certificate" "backend" {
  depends_on = [time_sleep.wait_for_acm]

  private_key      = tls_private_key.backend.private_key_pem
  certificate_body = tls_self_signed_cert.backend.cert_pem

  tags = merge(
    var.tags,
    {
      Name = "${var.service_name}-cert"
      Note = "Self-signed certificate for demo. Use ACM with DNS validation in production."
    }
  )

  lifecycle {
    create_before_destroy = true
  }
}

# ---------------------------------------------------------
# ECS Service
# ---------------------------------------------------------
resource "aws_ecs_service" "backend" {
  name            = var.service_name
  cluster         = var.cluster_id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.ecs_security_group_id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "backend"
    container_port   = 8000
  }

  health_check_grace_period_seconds = 60

  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  tags = var.tags

  depends_on = [aws_lb_listener.https]
}

# ---------------------------------------------------------
# Auto Scaling Target
# ---------------------------------------------------------
resource "aws_appautoscaling_target" "backend" {
  max_capacity       = var.auto_scaling_max_capacity
  min_capacity       = var.auto_scaling_min_capacity
  resource_id        = "service/${var.cluster_name}/${aws_ecs_service.backend.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# ---------------------------------------------------------
# Auto Scaling Policy - CPU
# ---------------------------------------------------------
resource "aws_appautoscaling_policy" "cpu" {
  name               = "${var.service_name}-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.backend.resource_id
  scalable_dimension = aws_appautoscaling_target.backend.scalable_dimension
  service_namespace  = aws_appautoscaling_target.backend.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value = var.auto_scaling_cpu_target

    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }

    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

# ---------------------------------------------------------
# Auto Scaling Policy - Memory
# ---------------------------------------------------------
resource "aws_appautoscaling_policy" "memory" {
  name               = "${var.service_name}-memory-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.backend.resource_id
  scalable_dimension = aws_appautoscaling_target.backend.scalable_dimension
  service_namespace  = aws_appautoscaling_target.backend.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value = var.auto_scaling_memory_target

    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }

    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

# ---------------------------------------------------------
# ElastiCache Redis (Optional)
# ---------------------------------------------------------
resource "aws_elasticache_subnet_group" "redis" {
  count = var.enable_redis ? 1 : 0

  name       = "${var.service_name}-redis-subnet"
  subnet_ids = var.private_subnet_ids

  tags = var.tags
}

resource "aws_elasticache_cluster" "redis" {
  count = var.enable_redis ? 1 : 0

  cluster_id           = "${var.service_name}-redis"
  engine               = "redis"
  node_type            = var.redis_node_type
  num_cache_nodes      = var.redis_num_cache_nodes
  parameter_group_name = "default.redis7"
  engine_version       = var.redis_engine_version
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.redis[0].name
  security_group_ids   = [var.ecs_security_group_id]

  tags = var.tags
}

# ---------------------------------------------------------
# Secrets Manager - API Keys
# ---------------------------------------------------------
resource "aws_secretsmanager_secret" "api_keys" {
  name_prefix             = "${var.service_name}-api-keys-"
  description             = "API keys for external data sources"
  recovery_window_in_days = 7

  tags = var.tags
}

resource "aws_secretsmanager_secret_version" "api_keys" {
  secret_id = aws_secretsmanager_secret.api_keys.id
  secret_string = jsonencode({
    news_api_key     = "placeholder"
    screener_api_key = "placeholder"
  })

  lifecycle {
    ignore_changes = [secret_string]
  }
}
