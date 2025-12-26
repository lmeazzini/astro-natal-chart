# =============================================================================
# S3 Module - Main Resources
# =============================================================================
# S3 buckets for PDF storage, database backups, and optional logs.
#
# Features:
#   - KMS encryption at rest
#   - Versioning for data protection
#   - Public access blocked
#   - CORS for presigned URL downloads
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
  name_prefix = "astro-${var.environment}"

  common_tags = merge(var.tags, {
    Module = "s3"
  })
}

# -----------------------------------------------------------------------------
# Data Sources
# -----------------------------------------------------------------------------

data "aws_caller_identity" "current" {}

# =============================================================================
# PDF Storage Bucket
# =============================================================================
# Stores birth chart PDFs and user avatars.
# Key structure: {prefix}/{user_id}/{chart_id}/{filename}.pdf
#                avatars/{user_id}/{filename}

resource "aws_s3_bucket" "pdfs" {
  bucket        = "${local.name_prefix}-pdfs-${data.aws_caller_identity.current.account_id}"
  force_destroy = var.force_destroy

  tags = merge(local.common_tags, {
    Name    = "${local.name_prefix}-pdfs"
    Purpose = "Birth chart PDF reports and avatars"
  })
}

resource "aws_s3_bucket_versioning" "pdfs" {
  bucket = aws_s3_bucket.pdfs.id

  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Suspended"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "pdfs" {
  bucket = aws_s3_bucket.pdfs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = var.kms_key_arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "pdfs" {
  bucket = aws_s3_bucket.pdfs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# CORS configuration for presigned URL downloads
resource "aws_s3_bucket_cors_configuration" "pdfs" {
  bucket = aws_s3_bucket.pdfs.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD", "PUT"]
    allowed_origins = var.allowed_origins
    expose_headers  = ["ETag", "Content-Length", "Content-Type"]
    max_age_seconds = 3600
  }
}

# =============================================================================
# Database Backups Bucket
# =============================================================================
# Stores PostgreSQL and Qdrant backups.
# Key structure: {YYYYMMDD}/astro_backup_{timestamp}.sql.gz
#                qdrant/{snapshot_name}.tar.gz
#                monthly/{filename} (for monthly archives)

resource "aws_s3_bucket" "backups" {
  bucket        = "${local.name_prefix}-backups-${data.aws_caller_identity.current.account_id}"
  force_destroy = var.force_destroy

  tags = merge(local.common_tags, {
    Name    = "${local.name_prefix}-backups"
    Purpose = "Database backups (PostgreSQL, Qdrant)"
  })
}

resource "aws_s3_bucket_versioning" "backups" {
  bucket = aws_s3_bucket.backups.id

  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Suspended"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = var.kms_key_arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "backups" {
  bucket = aws_s3_bucket.backups.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# =============================================================================
# Application Logs Bucket (Optional)
# =============================================================================
# Stores CloudWatch logs exports, ALB access logs, etc.

resource "aws_s3_bucket" "logs" {
  count = var.enable_logs_bucket ? 1 : 0

  bucket        = "${local.name_prefix}-logs-${data.aws_caller_identity.current.account_id}"
  force_destroy = var.force_destroy

  tags = merge(local.common_tags, {
    Name    = "${local.name_prefix}-logs"
    Purpose = "Application logs"
  })
}

resource "aws_s3_bucket_versioning" "logs" {
  count  = var.enable_logs_bucket ? 1 : 0
  bucket = aws_s3_bucket.logs[0].id

  versioning_configuration {
    status = "Suspended" # No versioning needed for logs
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "logs" {
  count  = var.enable_logs_bucket ? 1 : 0
  bucket = aws_s3_bucket.logs[0].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256" # Use default encryption for logs (cheaper)
    }
  }
}

resource "aws_s3_bucket_public_access_block" "logs" {
  count  = var.enable_logs_bucket ? 1 : 0
  bucket = aws_s3_bucket.logs[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
