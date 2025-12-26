# =============================================================================
# ECS Module - IAM Roles
# =============================================================================
# IAM roles for ECS task execution and task runtime.
# - Execution role: Used by ECS agent to pull images, write logs
# - Task role: Used by the container itself for AWS API calls
# =============================================================================

# -----------------------------------------------------------------------------
# Local Variables
# -----------------------------------------------------------------------------

locals {
  name_prefix = "astro-${var.environment}"
}

# -----------------------------------------------------------------------------
# Data Sources
# -----------------------------------------------------------------------------

data "aws_caller_identity" "current" {}

# -----------------------------------------------------------------------------
# ECS Execution Role
# -----------------------------------------------------------------------------
# This role is used by the ECS agent to:
# - Pull container images from ECR
# - Write logs to CloudWatch
# - Retrieve secrets from Secrets Manager (optional)

resource "aws_iam_role" "ecs_execution" {
  name = "${local.name_prefix}-ecs-execution-role"

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

  tags = merge(var.tags, {
    Name   = "${local.name_prefix}-ecs-execution-role"
    Module = "ecs"
  })
}

# Attach the AWS managed policy for ECS task execution
resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Additional policy for Secrets Manager access (for future use)
resource "aws_iam_role_policy" "ecs_execution_secrets" {
  name = "${local.name_prefix}-ecs-execution-secrets"
  role = aws_iam_role.ecs_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:astro/${var.environment}/*"
        ]
      }
    ]
  })
}

# -----------------------------------------------------------------------------
# ECS Task Role
# -----------------------------------------------------------------------------
# This role is used by the container itself to:
# - Write to CloudWatch Logs
# - Use ECS Exec for interactive debugging
# - Access other AWS services as needed

resource "aws_iam_role" "ecs_task" {
  name = "${local.name_prefix}-ecs-task-role"

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

  tags = merge(var.tags, {
    Name   = "${local.name_prefix}-ecs-task-role"
    Module = "ecs"
  })
}

# Policy for ECS Exec (interactive debugging)
resource "aws_iam_role_policy" "ecs_task_exec" {
  name = "${local.name_prefix}-ecs-task-exec"
  role = aws_iam_role.ecs_task.id

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

# Policy for CloudWatch Logs
resource "aws_iam_role_policy" "ecs_task_logs" {
  name = "${local.name_prefix}-ecs-task-logs"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/ecs/${local.name_prefix}-api:*"
        ]
      }
    ]
  })
}

# Policy for S3 access (for PDF storage - future use)
resource "aws_iam_role_policy" "ecs_task_s3" {
  name = "${local.name_prefix}-ecs-task-s3"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::astro-*-${data.aws_caller_identity.current.account_id}",
          "arn:aws:s3:::astro-*-${data.aws_caller_identity.current.account_id}/*"
        ]
      }
    ]
  })
}
