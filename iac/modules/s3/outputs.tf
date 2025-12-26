# =============================================================================
# S3 Module - Outputs
# =============================================================================
# Output values for integration with other modules and environment config.
# All bucket information and IAM policy ARNs are exposed.
# =============================================================================

# -----------------------------------------------------------------------------
# PDF Bucket Outputs
# -----------------------------------------------------------------------------

output "pdfs_bucket_name" {
  description = "Name of the PDF storage bucket"
  value       = aws_s3_bucket.pdfs.id
}

output "pdfs_bucket_arn" {
  description = "ARN of the PDF storage bucket"
  value       = aws_s3_bucket.pdfs.arn
}

output "pdfs_bucket_domain_name" {
  description = "Domain name of the PDF bucket (for CloudFront)"
  value       = aws_s3_bucket.pdfs.bucket_domain_name
}

output "pdfs_bucket_regional_domain_name" {
  description = "Regional domain name of the PDF bucket"
  value       = aws_s3_bucket.pdfs.bucket_regional_domain_name
}

# -----------------------------------------------------------------------------
# Backups Bucket Outputs
# -----------------------------------------------------------------------------

output "backups_bucket_name" {
  description = "Name of the database backups bucket"
  value       = aws_s3_bucket.backups.id
}

output "backups_bucket_arn" {
  description = "ARN of the database backups bucket"
  value       = aws_s3_bucket.backups.arn
}

# -----------------------------------------------------------------------------
# Logs Bucket Outputs (Optional)
# -----------------------------------------------------------------------------

output "logs_bucket_name" {
  description = "Name of the application logs bucket (null if not enabled)"
  value       = var.enable_logs_bucket ? aws_s3_bucket.logs[0].id : null
}

output "logs_bucket_arn" {
  description = "ARN of the application logs bucket (null if not enabled)"
  value       = var.enable_logs_bucket ? aws_s3_bucket.logs[0].arn : null
}

# -----------------------------------------------------------------------------
# IAM Policy ARNs
# -----------------------------------------------------------------------------

output "pdf_access_policy_arn" {
  description = "ARN of the IAM policy for PDF bucket access"
  value       = aws_iam_policy.pdf_access.arn
}

output "backup_access_policy_arn" {
  description = "ARN of the IAM policy for backup bucket access"
  value       = aws_iam_policy.backup_access.arn
}

output "logs_access_policy_arn" {
  description = "ARN of the IAM policy for logs bucket access (null if not enabled)"
  value       = var.enable_logs_bucket ? aws_iam_policy.logs_access[0].arn : null
}

# -----------------------------------------------------------------------------
# All Bucket ARNs (for IAM policies)
# -----------------------------------------------------------------------------

output "all_bucket_arns" {
  description = "List of all bucket ARNs for IAM policies"
  value = compact([
    aws_s3_bucket.pdfs.arn,
    aws_s3_bucket.backups.arn,
    var.enable_logs_bucket ? aws_s3_bucket.logs[0].arn : ""
  ])
}

# -----------------------------------------------------------------------------
# All IAM Policy ARNs
# -----------------------------------------------------------------------------

output "all_policy_arns" {
  description = "List of all IAM policy ARNs"
  value = compact([
    aws_iam_policy.pdf_access.arn,
    aws_iam_policy.backup_access.arn,
    var.enable_logs_bucket ? aws_iam_policy.logs_access[0].arn : ""
  ])
}
