# =============================================================================
# ECS Module - Task Definition
# =============================================================================
# Task definition for the FastAPI application container.
# Configured for Fargate Spot with 2-minute stop timeout.
# =============================================================================

# -----------------------------------------------------------------------------
# Task Definition
# -----------------------------------------------------------------------------

resource "aws_ecs_task_definition" "api" {
  family                   = "${local.name_prefix}-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.cpu
  memory                   = var.memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name  = "api"
      image = var.container_image

      # Graceful shutdown for Spot interruptions (2 minutes)
      stopTimeout = 120

      essential = true

      portMappings = [
        {
          containerPort = var.container_port
          hostPort      = var.container_port
          protocol      = "tcp"
        }
      ]

      # Environment variables (basic config)
      environment = [
        {
          name  = "ENVIRONMENT"
          value = var.environment
        },
        {
          name  = "PORT"
          value = tostring(var.container_port)
        }
      ]

      # Secrets from Secrets Manager (to be configured when #245 is implemented)
      # secrets = [
      #   {
      #     name      = "DATABASE_URL"
      #     valueFrom = "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:astro/${var.environment}/database-url"
      #   },
      #   {
      #     name      = "SECRET_KEY"
      #     valueFrom = "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:astro/${var.environment}/secret-key"
      #   },
      #   {
      #     name      = "REDIS_URL"
      #     valueFrom = "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:astro/${var.environment}/redis-url"
      #   }
      # ]

      # CloudWatch Logs
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "api"
        }
      }

      # Container health check
      healthCheck = {
        command = [
          "CMD-SHELL",
          "curl -f http://localhost:${var.container_port}${var.health_check_path} || exit 1"
        ]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-api-task"
  })
}
