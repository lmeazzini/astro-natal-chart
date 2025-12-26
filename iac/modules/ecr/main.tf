# =============================================================================
# ECR Module - Main Resources
# =============================================================================
# AWS Elastic Container Registry for storing Docker images.
#
# Features:
#   - Private ECR repository for API container images
#   - Image scanning on push for vulnerability detection
#   - Lifecycle policy to manage image retention
#   - Encryption at rest (default AWS managed key)
# =============================================================================

# -----------------------------------------------------------------------------
# Terraform Configuration
# -----------------------------------------------------------------------------

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# -----------------------------------------------------------------------------
# Data Sources
# -----------------------------------------------------------------------------

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

# -----------------------------------------------------------------------------
# Local Variables
# -----------------------------------------------------------------------------

locals {
  name_prefix = "astro-${var.environment}"

  # Full repository name includes environment
  full_repository_name = "${var.repository_name}-${var.environment}"

  common_tags = merge(var.tags, {
    Module = "ecr"
  })
}

# -----------------------------------------------------------------------------
# ECR Repository
# -----------------------------------------------------------------------------

resource "aws_ecr_repository" "main" {
  name                 = local.full_repository_name
  image_tag_mutability = var.image_tag_mutability

  image_scanning_configuration {
    scan_on_push = var.scan_on_push
  }

  # Use default encryption (AWS managed key)
  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ecr"
  })
}

# -----------------------------------------------------------------------------
# Lifecycle Policy
# -----------------------------------------------------------------------------
# Automatically clean up old images to control storage costs.
# Rules are evaluated in order of priority (lower number = higher priority).

resource "aws_ecr_lifecycle_policy" "main" {
  repository = aws_ecr_repository.main.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Expire untagged images after ${var.untagged_image_expiry_days} days"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = var.untagged_image_expiry_days
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2
        description  = "Keep only the last ${var.max_image_count} images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = var.max_image_count
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}
