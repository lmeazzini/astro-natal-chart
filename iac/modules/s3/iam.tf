# =============================================================================
# S3 Module - IAM Policies
# =============================================================================
# Least-privilege IAM policies for S3 bucket access.
#
# Policies:
#   - PDF Access: For ECS tasks (upload, download, delete PDFs)
#   - Backup Access: For backup scripts (upload, download backups)
# =============================================================================

# -----------------------------------------------------------------------------
# PDF Access Policy
# -----------------------------------------------------------------------------
# Grants ECS tasks permission to:
#   - Upload PDFs and avatars (PutObject)
#   - Download PDFs (GetObject)
#   - Delete PDFs (DeleteObject)
#   - List bucket contents (ListBucket)
#   - Use KMS for encryption/decryption

resource "aws_iam_policy" "pdf_access" {
  name        = "${local.name_prefix}-s3-pdf-access"
  description = "Allows access to PDF storage bucket for birth chart reports"
  path        = "/"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ListBucket"
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ]
        Resource = aws_s3_bucket.pdfs.arn
      },
      {
        Sid    = "ObjectOperations"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:GetObjectVersion",
          "s3:GetObjectTagging",
          "s3:PutObjectTagging"
        ]
        Resource = "${aws_s3_bucket.pdfs.arn}/*"
      },
      {
        Sid    = "KMSAccess"
        Effect = "Allow"
        Action = [
          "kms:GenerateDataKey",
          "kms:Decrypt",
          "kms:Encrypt"
        ]
        Resource = var.kms_key_arn
      }
    ]
  })

  tags = local.common_tags
}

# -----------------------------------------------------------------------------
# Backup Access Policy
# -----------------------------------------------------------------------------
# Grants backup scripts permission to:
#   - Upload backups (PutObject)
#   - Download backups for restore (GetObject)
#   - List backups (ListBucket)
#   - Delete old backups (DeleteObject)
#   - Use KMS for encryption/decryption

resource "aws_iam_policy" "backup_access" {
  name        = "${local.name_prefix}-s3-backup-access"
  description = "Allows access to backup bucket for database backups"
  path        = "/"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ListBucket"
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ]
        Resource = aws_s3_bucket.backups.arn
      },
      {
        Sid    = "ObjectOperations"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:GetObjectVersion"
        ]
        Resource = "${aws_s3_bucket.backups.arn}/*"
      },
      {
        Sid    = "KMSAccess"
        Effect = "Allow"
        Action = [
          "kms:GenerateDataKey",
          "kms:Decrypt",
          "kms:Encrypt"
        ]
        Resource = var.kms_key_arn
      }
    ]
  })

  tags = local.common_tags
}

# -----------------------------------------------------------------------------
# Logs Access Policy (Optional)
# -----------------------------------------------------------------------------
# Grants permission to write logs to the logs bucket.
# Used by CloudWatch, ALB, or other AWS services.

resource "aws_iam_policy" "logs_access" {
  count = var.enable_logs_bucket ? 1 : 0

  name        = "${local.name_prefix}-s3-logs-access"
  description = "Allows write access to application logs bucket"
  path        = "/"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ListBucket"
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.logs[0].arn
      },
      {
        Sid    = "WriteObjects"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject"
        ]
        Resource = "${aws_s3_bucket.logs[0].arn}/*"
      }
    ]
  })

  tags = local.common_tags
}
