# =============================================================================
# RDS Module - Main Resources
# =============================================================================
# Creates RDS PostgreSQL instance with single-AZ configuration.
# Cost-optimized for development/staging environments.
#
# Features:
#   - PostgreSQL 16
#   - Single-AZ (no Multi-AZ for cost savings)
#   - Automated backups (7 days retention)
#   - Storage autoscaling
#   - Encryption at rest
#   - Performance Insights (free tier)
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
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

# -----------------------------------------------------------------------------
# Local Variables
# -----------------------------------------------------------------------------

locals {
  name_prefix = "astro-${var.environment}"

  common_tags = merge(var.tags, {
    Module = "rds"
  })
}

# -----------------------------------------------------------------------------
# Random Password for Database
# -----------------------------------------------------------------------------

resource "random_password" "db" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# -----------------------------------------------------------------------------
# RDS Instance
# -----------------------------------------------------------------------------

resource "aws_db_instance" "main" {
  identifier = "${local.name_prefix}-db"

  # Engine
  engine         = "postgres"
  engine_version = var.engine_version

  # Instance
  instance_class = var.instance_class

  # Storage
  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true

  # Database
  db_name  = var.db_name
  username = var.db_username
  password = random_password.db.result

  # NO HIGH AVAILABILITY (cost optimization)
  multi_az          = false
  availability_zone = var.availability_zone

  # Network
  db_subnet_group_name   = var.db_subnet_group_name
  vpc_security_group_ids = [var.security_group_id]
  publicly_accessible    = false
  port                   = 5432

  # Backups
  backup_retention_period = var.backup_retention_period
  backup_window           = var.backup_window

  # Maintenance
  maintenance_window         = var.maintenance_window
  auto_minor_version_upgrade = true

  # Monitoring
  performance_insights_enabled          = true
  performance_insights_retention_period = 7 # Free tier

  # Protection
  deletion_protection = var.deletion_protection
  skip_final_snapshot = var.skip_final_snapshot

  final_snapshot_identifier = var.skip_final_snapshot ? null : "${local.name_prefix}-db-final-snapshot"

  # Parameter group (use default for now)
  parameter_group_name = "default.postgres16"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db"
  })

  lifecycle {
    ignore_changes = [
      password, # Don't replace on password change
    ]
  }
}
