# =============================================================================
# ECS Module - Celery Worker & Beat
# =============================================================================
# Task definitions and services for Celery workers.
# - Celery Worker: Processes background tasks from Redis queue
# - Celery Beat: Scheduler for periodic tasks (LGPD cleanup, credit reset, etc.)
#
# Both use Fargate Spot for cost optimization (~70% savings).
# =============================================================================

# -----------------------------------------------------------------------------
# CloudWatch Log Group for Celery
# -----------------------------------------------------------------------------

resource "aws_cloudwatch_log_group" "celery" {
  name              = "/ecs/${local.name_prefix}-celery"
  retention_in_days = var.log_retention_days

  # Optional KMS encryption for logs at rest
  kms_key_id = var.log_encryption_kms_key_arn

  tags = merge(local.common_tags, {
    Name = "/ecs/${local.name_prefix}-celery"
  })
}

# -----------------------------------------------------------------------------
# Celery Worker Task Definition
# -----------------------------------------------------------------------------
# Processes background tasks like chart generation, PDF export, etc.
# Uses the same container image as the API.

resource "aws_ecs_task_definition" "celery_worker" {
  family                   = "${local.name_prefix}-celery-worker"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.celery_worker_cpu
  memory                   = var.celery_worker_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name  = "celery-worker"
      image = var.container_image

      # Override the default command to run Celery worker via uv
      command = [
        "uv", "run", "celery", "-A", "app.core.celery_app", "worker",
        "--loglevel=info",
        "--concurrency=2",
        "--max-tasks-per-child=100"
      ]

      essential = true

      # Graceful shutdown for Spot interruptions (2 minutes)
      stopTimeout = 120

      # Environment variables
      environment = concat([
        {
          name  = "ENVIRONMENT"
          value = var.environment
        }
        ], var.qdrant_url != null ? [
        {
          name  = "QDRANT_URL"
          value = var.qdrant_url
        }
        ] : [], var.frontend_url != null ? [
        {
          name  = "FRONTEND_URL"
          value = var.frontend_url
        }
      ] : [])

      # Secrets from Secrets Manager (same as API)
      secrets = local.all_secrets

      # CloudWatch Logs
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.celery.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "worker"
        }
      }
    }
  ])

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-celery-worker-task"
  })
}

# -----------------------------------------------------------------------------
# Celery Beat Task Definition
# -----------------------------------------------------------------------------
# Scheduler for periodic tasks:
# - LGPD cleanup (hard delete after 30 days)
# - Subscription expiration checks
# - Monthly credit reset
# - Password reset token cleanup
# - Interpretation cache cleanup

resource "aws_ecs_task_definition" "celery_beat" {
  family                   = "${local.name_prefix}-celery-beat"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.celery_beat_cpu
  memory                   = var.celery_beat_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name  = "celery-beat"
      image = var.container_image

      # Override the default command to run Celery beat via uv
      command = [
        "uv", "run", "celery", "-A", "app.core.celery_app", "beat",
        "--loglevel=info"
      ]

      essential = true

      # Environment variables
      environment = concat([
        {
          name  = "ENVIRONMENT"
          value = var.environment
        }
        ], var.frontend_url != null ? [
        {
          name  = "FRONTEND_URL"
          value = var.frontend_url
        }
      ] : [])

      # Secrets from Secrets Manager (same as API)
      secrets = local.all_secrets

      # CloudWatch Logs
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.celery.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "beat"
        }
      }
    }
  ])

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-celery-beat-task"
  })
}

# -----------------------------------------------------------------------------
# Celery Worker Service
# -----------------------------------------------------------------------------
# Runs the Celery workers to process background tasks.
# No load balancer needed (workers don't receive HTTP traffic).

resource "aws_ecs_service" "celery_worker" {
  name            = "${local.name_prefix}-celery-worker"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.celery_worker.arn
  desired_count   = var.celery_worker_count

  # Use 100% Fargate Spot for cost savings (~70%)
  capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight            = 100
    base              = 0
  }

  # Network configuration (private subnet, no public IP)
  network_configuration {
    subnets          = [var.private_subnet_id]
    security_groups  = [var.ecs_security_group_id]
    assign_public_ip = false
  }

  # Circuit breaker for automatic rollback on failures
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  # Enable ECS Exec for interactive debugging
  enable_execute_command = true

  # Ensure the service waits for a stable state
  wait_for_steady_state = false

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-celery-worker-service"
  })

  depends_on = [
    aws_iam_role_policy.ecs_task_exec,
    aws_iam_role_policy.ecs_task_logs_celery
  ]

  lifecycle {
    ignore_changes = [
      desired_count, # Allow external scaling
    ]
  }
}

# -----------------------------------------------------------------------------
# Celery Beat Service
# -----------------------------------------------------------------------------
# Runs the Celery beat scheduler.
# ALWAYS exactly 1 instance (avoid duplicate scheduled tasks).

resource "aws_ecs_service" "celery_beat" {
  name            = "${local.name_prefix}-celery-beat"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.celery_beat.arn
  desired_count   = 1 # ALWAYS 1 - never scale this, avoids duplicate schedules

  # Use 100% Fargate Spot for cost savings (~70%)
  capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight            = 100
    base              = 0
  }

  # Network configuration (private subnet, no public IP)
  network_configuration {
    subnets          = [var.private_subnet_id]
    security_groups  = [var.ecs_security_group_id]
    assign_public_ip = false
  }

  # Circuit breaker for automatic rollback on failures
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  # Enable ECS Exec for interactive debugging
  enable_execute_command = true

  # Ensure the service waits for a stable state
  wait_for_steady_state = false

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-celery-beat-service"
  })

  depends_on = [
    aws_iam_role_policy.ecs_task_exec,
    aws_iam_role_policy.ecs_task_logs_celery
  ]

  # Never change desired_count - beat must always be exactly 1
}
