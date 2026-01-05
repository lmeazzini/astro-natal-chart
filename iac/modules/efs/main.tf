# =============================================================================
# EFS Module - Elastic File System
# =============================================================================
# Provides persistent storage for Qdrant vector database.
# Configured with encryption, lifecycle policies, and automatic backups.
# =============================================================================

locals {
  name_prefix = "astro-${var.environment}"

  common_tags = {
    Module = "efs"
  }
}

# -----------------------------------------------------------------------------
# EFS File System
# -----------------------------------------------------------------------------

resource "aws_efs_file_system" "main" {
  creation_token = "${local.name_prefix}-qdrant-efs"
  encrypted      = true
  kms_key_id     = var.kms_key_arn

  performance_mode = "generalPurpose"
  throughput_mode  = "bursting"

  # Move infrequently accessed data to cheaper storage tier
  lifecycle_policy {
    transition_to_ia = "AFTER_30_DAYS"
  }

  # Move data back to standard when accessed
  lifecycle_policy {
    transition_to_primary_storage_class = "AFTER_1_ACCESS"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-qdrant-efs"
  })
}

# -----------------------------------------------------------------------------
# EFS Mount Target
# -----------------------------------------------------------------------------
# Mount target in the private subnet where Qdrant ECS task runs.

resource "aws_efs_mount_target" "main" {
  file_system_id  = aws_efs_file_system.main.id
  subnet_id       = var.private_subnet_id
  security_groups = [var.efs_security_group_id]
}

# -----------------------------------------------------------------------------
# EFS Access Point
# -----------------------------------------------------------------------------
# Provides application-specific entry point with POSIX user/group.

resource "aws_efs_access_point" "qdrant" {
  file_system_id = aws_efs_file_system.main.id

  # POSIX user for Qdrant container (runs as uid 1000)
  posix_user {
    uid = 1000
    gid = 1000
  }

  # Root directory for Qdrant data
  root_directory {
    path = "/qdrant"
    creation_info {
      owner_uid   = 1000
      owner_gid   = 1000
      permissions = "755"
    }
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-qdrant-ap"
  })
}

# -----------------------------------------------------------------------------
# EFS Backup Policy
# -----------------------------------------------------------------------------
# Enables automatic daily backups via AWS Backup.

resource "aws_efs_backup_policy" "main" {
  file_system_id = aws_efs_file_system.main.id

  backup_policy {
    status = var.enable_backups ? "ENABLED" : "DISABLED"
  }
}
