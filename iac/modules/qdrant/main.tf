# =============================================================================
# Qdrant Module - Main Resources
# =============================================================================
# Qdrant vector database on ECS Fargate with EFS persistence.
# Uses AWS Cloud Map for service discovery.
# =============================================================================

# -----------------------------------------------------------------------------
# CloudWatch Log Group
# -----------------------------------------------------------------------------

resource "aws_cloudwatch_log_group" "qdrant" {
  name              = "/ecs/${local.name_prefix}-qdrant"
  retention_in_days = var.log_retention_days
  kms_key_id        = var.kms_key_arn

  tags = merge(local.common_tags, {
    Name = "/ecs/${local.name_prefix}-qdrant"
  })
}

# -----------------------------------------------------------------------------
# ECS Task Definition
# -----------------------------------------------------------------------------

resource "aws_ecs_task_definition" "qdrant" {
  family                   = "${local.name_prefix}-qdrant"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.cpu
  memory                   = var.memory
  execution_role_arn       = aws_iam_role.qdrant_execution.arn
  task_role_arn            = aws_iam_role.qdrant_task.arn

  container_definitions = jsonencode([
    {
      name      = "qdrant"
      image     = "qdrant/qdrant:${var.qdrant_version}"
      essential = true

      portMappings = [
        {
          containerPort = 6333
          hostPort      = 6333
          protocol      = "tcp"
        },
        {
          containerPort = 6334
          hostPort      = 6334
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "QDRANT__SERVICE__GRPC_PORT"
          value = "6334"
        },
        {
          name  = "QDRANT__LOG_LEVEL"
          value = "INFO"
        },
        {
          name  = "QDRANT__STORAGE__WAL__FLUSH_INTERVAL_SEC"
          value = "1"
        }
      ]

      # Mount EFS volume for persistent storage
      mountPoints = [
        {
          sourceVolume  = "qdrant-storage"
          containerPath = "/qdrant/storage"
          readOnly      = false
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.qdrant.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "qdrant"
        }
      }

      healthCheck = {
        command = [
          "CMD-SHELL",
          "wget --no-verbose --tries=1 --spider http://localhost:6333/ || exit 1"
        ]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  # EFS Volume configuration
  volume {
    name = "qdrant-storage"

    efs_volume_configuration {
      file_system_id     = var.efs_file_system_id
      root_directory     = "/"
      transit_encryption = "ENABLED"

      authorization_config {
        access_point_id = var.efs_access_point_id
        iam             = "ENABLED"
      }
    }
  }

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-qdrant-task"
  })
}
