# =============================================================================
# S3 Module - Lifecycle Policies
# =============================================================================
# Cost-optimized lifecycle policies for data tiering and expiration.
#
# Tiers:
#   - STANDARD:        Hot storage (default)
#   - STANDARD_IA:     Infrequent access (30+ day minimum storage)
#   - GLACIER:         Archive storage (90-180 day retrieval)
#   - DEEP_ARCHIVE:    Long-term archive (12-48 hour retrieval)
# =============================================================================

# -----------------------------------------------------------------------------
# PDF Bucket Lifecycle
# -----------------------------------------------------------------------------
# - Current versions: 90d → Standard-IA, 365d → Glacier
# - Noncurrent versions: 30d → expire
# - Aborted multipart uploads: 7d → expire

resource "aws_s3_bucket_lifecycle_configuration" "pdfs" {
  bucket = aws_s3_bucket.pdfs.id

  # Transition older PDFs to cheaper storage tiers
  rule {
    id     = "transition-to-ia"
    status = "Enabled"

    filter {
      prefix = ""
    }

    transition {
      days          = var.pdf_transition_to_ia_days
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = var.pdf_transition_to_glacier_days
      storage_class = "GLACIER"
    }
  }

  # Clean up old versions (when versioning is enabled)
  rule {
    id     = "expire-noncurrent-versions"
    status = var.enable_versioning ? "Enabled" : "Disabled"

    filter {
      prefix = ""
    }

    noncurrent_version_expiration {
      noncurrent_days = var.pdf_noncurrent_expiration_days
    }
  }

  # Clean up incomplete multipart uploads
  rule {
    id     = "abort-incomplete-multipart"
    status = "Enabled"

    filter {
      prefix = ""
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# -----------------------------------------------------------------------------
# Backups Bucket Lifecycle
# -----------------------------------------------------------------------------
# Backup structure:
#   - {YYYYMMDD}/astro_backup_{timestamp}.sql.gz (daily PostgreSQL)
#   - monthly/{filename} (monthly archives, longer retention)
#   - qdrant/{snapshot_name}.tar.gz (vector DB snapshots)
#
# NOTE: S3 lifecycle applies earliest expiration when multiple rules match.
# To avoid conflicts, we only set expiration on specific prefixes.

resource "aws_s3_bucket_lifecycle_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  # Monthly backups - longer retention for compliance/disaster recovery
  rule {
    id     = "monthly-backups"
    status = "Enabled"

    filter {
      prefix = "monthly/"
    }

    transition {
      days          = 30
      storage_class = "GLACIER"
    }

    expiration {
      days = var.monthly_backup_expiration_days
    }
  }

  # Qdrant vector DB snapshots - same retention as daily backups
  rule {
    id     = "qdrant-snapshots"
    status = "Enabled"

    filter {
      prefix = "qdrant/"
    }

    transition {
      days          = var.backup_transition_to_glacier_days
      storage_class = "GLACIER"
    }

    expiration {
      days = var.backup_expiration_days
    }
  }

  # Archive all backups to Glacier after configured days
  # Expiration is handled by backup script (deletes old YYYYMMDD/ folders)
  rule {
    id     = "archive-all-backups"
    status = "Enabled"

    filter {
      prefix = ""
    }

    transition {
      days          = var.backup_transition_to_glacier_days
      storage_class = "GLACIER"
    }
  }

  # Clean up incomplete multipart uploads
  rule {
    id     = "abort-incomplete-multipart"
    status = "Enabled"

    filter {
      prefix = ""
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 1
    }
  }
}

# -----------------------------------------------------------------------------
# Logs Bucket Lifecycle (Optional)
# -----------------------------------------------------------------------------
# - All logs: expire after configured days (default 90)
# - No archival - logs are ephemeral

resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  count  = var.enable_logs_bucket ? 1 : 0
  bucket = aws_s3_bucket.logs[0].id

  rule {
    id     = "expire-logs"
    status = "Enabled"

    filter {
      prefix = ""
    }

    expiration {
      days = var.logs_expiration_days
    }
  }

  # Clean up incomplete multipart uploads quickly
  rule {
    id     = "abort-incomplete-multipart"
    status = "Enabled"

    filter {
      prefix = ""
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 1
    }
  }
}
