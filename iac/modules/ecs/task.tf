# =============================================================================
# ECS Module - Task Definition
# =============================================================================
# Task definition for the FastAPI application container.
# Configured for Fargate Spot with 2-minute stop timeout.
# =============================================================================

# -----------------------------------------------------------------------------
# Local Variables for Secrets
# -----------------------------------------------------------------------------

locals {
  # Core secrets (always included when secret_arns is provided)
  core_secrets = var.secret_arns != null ? [
    {
      name      = "DATABASE_URL"
      valueFrom = var.secret_arns.database_url
    },
    {
      name      = "SECRET_KEY"
      valueFrom = var.secret_arns.secret_key
    },
    {
      name      = "REDIS_URL"
      valueFrom = var.secret_arns.redis_url
    }
  ] : []

  # OpenAI secret (conditionally included)
  openai_secrets = var.secret_arns != null ? (
    var.secret_arns.openai_api_key != null ? [{
      name      = "OPENAI_API_KEY"
      valueFrom = var.secret_arns.openai_api_key
    }] : []
  ) : []

  # Stripe secrets (conditionally included)
  stripe_secrets = var.secret_arns != null ? concat(
    var.secret_arns.stripe_secret_key != null ? [{
      name      = "STRIPE_SECRET_KEY"
      valueFrom = var.secret_arns.stripe_secret_key
    }] : [],
    var.secret_arns.stripe_webhook_secret != null ? [{
      name      = "STRIPE_WEBHOOK_SECRET"
      valueFrom = var.secret_arns.stripe_webhook_secret
    }] : [],
    var.secret_arns.stripe_price_ids != null ? [{
      name      = "STRIPE_PRICE_IDS"
      valueFrom = var.secret_arns.stripe_price_ids
    }] : []
  ) : []

  # All secrets combined
  all_secrets = concat(local.core_secrets, local.openai_secrets, local.stripe_secrets)
}

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
      environment = concat([
        {
          name  = "ENVIRONMENT"
          value = var.environment
        },
        {
          name  = "PORT"
          value = tostring(var.container_port)
        }
      ], var.allowed_origins != "" ? [{
        name  = "ALLOWED_ORIGINS"
        value = var.allowed_origins
      }] : [])

      # Secrets from Secrets Manager (injected from secrets module)
      # Includes core secrets (database, redis, jwt) and optional Stripe secrets
      secrets = local.all_secrets

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
      # Using wget for nginx:alpine compatibility (curl not available)
      # For FastAPI, replace with: curl -f http://localhost:${var.container_port}${var.health_check_path}
      healthCheck = {
        command = [
          "CMD-SHELL",
          "wget --no-verbose --tries=1 --spider http://localhost:${var.container_port}/ || exit 1"
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
