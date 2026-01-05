# =============================================================================
# Qdrant Module - IAM Roles
# =============================================================================
# IAM roles for Qdrant ECS task execution and runtime.
# =============================================================================

locals {
  name_prefix = "astro-${var.environment}"

  common_tags = {
    Module = "qdrant"
  }
}

# -----------------------------------------------------------------------------
# ECS Execution Role (for ECS Agent)
# -----------------------------------------------------------------------------
# Used by ECS agent to pull images, write logs, etc.

resource "aws_iam_role" "qdrant_execution" {
  name = "${local.name_prefix}-qdrant-execution-role"

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

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-qdrant-execution-role"
  })
}

# Attach the standard ECS execution policy
resource "aws_iam_role_policy_attachment" "qdrant_execution" {
  role       = aws_iam_role.qdrant_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# -----------------------------------------------------------------------------
# ECS Task Role (for Container Runtime)
# -----------------------------------------------------------------------------
# Used by the Qdrant container for EFS access and other AWS services.

resource "aws_iam_role" "qdrant_task" {
  name = "${local.name_prefix}-qdrant-task-role"

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

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-qdrant-task-role"
  })
}

# EFS access policy for Qdrant task
resource "aws_iam_role_policy" "qdrant_task_efs" {
  name = "${local.name_prefix}-qdrant-efs-access"
  role = aws_iam_role.qdrant_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "elasticfilesystem:ClientMount",
          "elasticfilesystem:ClientWrite",
          "elasticfilesystem:ClientRootAccess"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "elasticfilesystem:AccessPointArn" = "arn:aws:elasticfilesystem:${var.aws_region}:*:access-point/${var.efs_access_point_id}"
          }
        }
      }
    ]
  })
}

# CloudWatch Logs policy for Qdrant task
resource "aws_iam_role_policy" "qdrant_task_logs" {
  name = "${local.name_prefix}-qdrant-logs"
  role = aws_iam_role.qdrant_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.qdrant.arn}:*"
      }
    ]
  })
}

# ECS Exec policy (for debugging via AWS CLI)
resource "aws_iam_role_policy" "qdrant_task_exec" {
  name = "${local.name_prefix}-qdrant-exec"
  role = aws_iam_role.qdrant_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssmmessages:CreateControlChannel",
          "ssmmessages:CreateDataChannel",
          "ssmmessages:OpenControlChannel",
          "ssmmessages:OpenDataChannel"
        ]
        Resource = "*"
      }
    ]
  })
}
