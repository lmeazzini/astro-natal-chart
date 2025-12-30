# =============================================================================
# CloudFront Module - Outputs
# =============================================================================
# Output values for integration with other modules and deployment scripts.
# =============================================================================

# -----------------------------------------------------------------------------
# S3 Bucket Outputs
# -----------------------------------------------------------------------------

output "bucket_name" {
  description = "Name of the S3 bucket for frontend files"
  value       = aws_s3_bucket.frontend.id
}

output "bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.frontend.arn
}

output "bucket_regional_domain_name" {
  description = "Regional domain name of the S3 bucket"
  value       = aws_s3_bucket.frontend.bucket_regional_domain_name
}

# -----------------------------------------------------------------------------
# CloudFront Distribution Outputs
# -----------------------------------------------------------------------------

output "distribution_id" {
  description = "ID of the CloudFront distribution (used for cache invalidation)"
  value       = aws_cloudfront_distribution.frontend.id
}

output "distribution_arn" {
  description = "ARN of the CloudFront distribution"
  value       = aws_cloudfront_distribution.frontend.arn
}

output "distribution_domain_name" {
  description = "Domain name of the CloudFront distribution (e.g., d111111abcdef8.cloudfront.net)"
  value       = aws_cloudfront_distribution.frontend.domain_name
}

output "distribution_hosted_zone_id" {
  description = "CloudFront hosted zone ID (for Route53 alias records)"
  value       = aws_cloudfront_distribution.frontend.hosted_zone_id
}

# -----------------------------------------------------------------------------
# URLs
# -----------------------------------------------------------------------------

output "frontend_url" {
  description = "URL to access the frontend (HTTPS)"
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "custom_domain_url" {
  description = "Custom domain URL (if configured)"
  value       = length(var.domain_aliases) > 0 ? "https://${var.domain_aliases[0]}" : null
}

# -----------------------------------------------------------------------------
# Deployment Helpers
# -----------------------------------------------------------------------------

output "deploy_command" {
  description = "AWS CLI command to deploy frontend files"
  value       = "aws s3 sync ./dist s3://${aws_s3_bucket.frontend.id} --delete"
}

output "invalidate_command" {
  description = "AWS CLI command to invalidate CloudFront cache"
  value       = "aws cloudfront create-invalidation --distribution-id ${aws_cloudfront_distribution.frontend.id} --paths '/*'"
}
