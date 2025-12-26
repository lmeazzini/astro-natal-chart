# =============================================================================
# ECS Module - Main Resources
# =============================================================================
# Creates ECS Fargate cluster with Spot capacity providers.
# Cost-optimized: 100% Fargate Spot for ~70% savings.
#
# Features:
#   - Fargate Spot (70% cost savings)
#   - Container Insights monitoring
#   - CloudWatch logging
#   - Single-AZ deployment
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
# Local Variables
# -----------------------------------------------------------------------------

locals {
  common_tags = merge(var.tags, {
    Module = "ecs"
  })
}

# -----------------------------------------------------------------------------
# ECS Cluster
# -----------------------------------------------------------------------------

resource "aws_ecs_cluster" "main" {
  name = "${local.name_prefix}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-cluster"
  })
}

# -----------------------------------------------------------------------------
# Capacity Providers
# -----------------------------------------------------------------------------
# Configure Fargate Spot as the default (100%) for cost savings.
# Fargate on-demand available as fallback if Spot unavailable.

resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name = aws_ecs_cluster.main.name

  capacity_providers = ["FARGATE_SPOT", "FARGATE"]

  # Default strategy: 100% Fargate Spot
  default_capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight            = 100
    base              = 0
  }
}

# -----------------------------------------------------------------------------
# CloudWatch Log Group
# -----------------------------------------------------------------------------

resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/${local.name_prefix}-api"
  retention_in_days = var.log_retention_days

  # Optional KMS encryption for logs at rest
  kms_key_id = var.log_encryption_kms_key_arn

  tags = merge(local.common_tags, {
    Name = "/ecs/${local.name_prefix}-api"
  })
}
