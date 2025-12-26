# =============================================================================
# ECR Module - IAM Policies
# =============================================================================
# IAM policies for CI/CD access to ECR repository.
# Attach these policies to GitHub Actions IAM user/role.
# =============================================================================

# -----------------------------------------------------------------------------
# ECR Push Policy (for CI/CD)
# -----------------------------------------------------------------------------
# Allows pushing images to ECR from GitHub Actions.

resource "aws_iam_policy" "ecr_push" {
  name        = "${local.name_prefix}-ecr-push"
  description = "Allow pushing images to ECR repository"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "GetAuthorizationToken"
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken"
        ]
        Resource = "*"
      },
      {
        Sid    = "PushImages"
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
        Resource = aws_ecr_repository.main.arn
      }
    ]
  })

  tags = local.common_tags
}

# -----------------------------------------------------------------------------
# ECR Pull Policy (for ECS)
# -----------------------------------------------------------------------------
# Allows pulling images from ECR (for ECS task execution role).

resource "aws_iam_policy" "ecr_pull" {
  name        = "${local.name_prefix}-ecr-pull"
  description = "Allow pulling images from ECR repository"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "GetAuthorizationToken"
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken"
        ]
        Resource = "*"
      },
      {
        Sid    = "PullImages"
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = aws_ecr_repository.main.arn
      }
    ]
  })

  tags = local.common_tags
}
