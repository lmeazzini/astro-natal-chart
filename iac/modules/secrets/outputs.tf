# =============================================================================
# Secrets Module - Outputs
# =============================================================================
# Output values for ECS task definition integration.
# All secret ARNs are exposed for injection into containers.
# =============================================================================

# -----------------------------------------------------------------------------
# KMS Key
# -----------------------------------------------------------------------------

output "kms_key_arn" {
  description = "ARN of the KMS key used for secrets encryption"
  value       = aws_kms_key.secrets.arn
}

output "kms_key_id" {
  description = "ID of the KMS key"
  value       = aws_kms_key.secrets.key_id
}

output "kms_key_alias" {
  description = "Alias of the KMS key"
  value       = aws_kms_alias.secrets.name
}

# -----------------------------------------------------------------------------
# Core Secret ARNs
# -----------------------------------------------------------------------------

output "database_url_arn" {
  description = "ARN of the database URL secret"
  value       = aws_secretsmanager_secret.database_url.arn
}

output "redis_url_arn" {
  description = "ARN of the Redis URL secret"
  value       = aws_secretsmanager_secret.redis_url.arn
}

output "secret_key_arn" {
  description = "ARN of the JWT secret key"
  value       = aws_secretsmanager_secret.secret_key.arn
}

# -----------------------------------------------------------------------------
# OAuth Secret ARNs (Conditional)
# -----------------------------------------------------------------------------

output "oauth_google_arn" {
  description = "ARN of the Google OAuth secret (null if not configured)"
  value       = try(aws_secretsmanager_secret.oauth_google[0].arn, null)
}

output "oauth_github_arn" {
  description = "ARN of the GitHub OAuth secret (null if not configured)"
  value       = try(aws_secretsmanager_secret.oauth_github[0].arn, null)
}

output "oauth_facebook_arn" {
  description = "ARN of the Facebook OAuth secret (null if not configured)"
  value       = try(aws_secretsmanager_secret.oauth_facebook[0].arn, null)
}

# -----------------------------------------------------------------------------
# API Key Secret ARNs (Conditional)
# -----------------------------------------------------------------------------

output "opencage_api_key_arn" {
  description = "ARN of the OpenCage API key secret (null if not configured)"
  value       = try(aws_secretsmanager_secret.opencage[0].arn, null)
}

output "openai_api_key_arn" {
  description = "ARN of the OpenAI API key secret (null if not configured)"
  value       = try(aws_secretsmanager_secret.openai[0].arn, null)
}

output "amplitude_api_key_arn" {
  description = "ARN of the Amplitude API key secret (null if not configured)"
  value       = try(aws_secretsmanager_secret.amplitude[0].arn, null)
}

# -----------------------------------------------------------------------------
# SMTP Secret ARN (Conditional)
# -----------------------------------------------------------------------------

output "smtp_arn" {
  description = "ARN of the SMTP configuration secret (null if not configured)"
  value       = try(aws_secretsmanager_secret.smtp[0].arn, null)
}

# -----------------------------------------------------------------------------
# All Core Secret ARNs (for ECS task definition)
# -----------------------------------------------------------------------------

output "core_secret_arns" {
  description = "Map of core secret ARNs for ECS task injection"
  value = {
    database_url = aws_secretsmanager_secret.database_url.arn
    redis_url    = aws_secretsmanager_secret.redis_url.arn
    secret_key   = aws_secretsmanager_secret.secret_key.arn
  }
}

# -----------------------------------------------------------------------------
# Secret Count (for diagnostics)
# -----------------------------------------------------------------------------

output "total_secrets_created" {
  description = "Total number of secrets created"
  # Using nonsensitive() because this is just a count, not actual secret data
  value = nonsensitive(
    3 + # Core secrets (database, redis, secret_key)
    (var.google_oauth != null ? 1 : 0) +
    (var.github_oauth != null ? 1 : 0) +
    (var.facebook_oauth != null ? 1 : 0) +
    (var.opencage_api_key != null ? 1 : 0) +
    (var.openai_api_key != null ? 1 : 0) +
    (var.amplitude_api_key != null ? 1 : 0) +
    (var.smtp_config != null ? 1 : 0)
  )
}

# -----------------------------------------------------------------------------
# All Secret ARNs (for IAM policies)
# -----------------------------------------------------------------------------

output "all_secret_arns" {
  description = "List of all secret ARNs for IAM policies"
  value = compact([
    aws_secretsmanager_secret.database_url.arn,
    aws_secretsmanager_secret.redis_url.arn,
    aws_secretsmanager_secret.secret_key.arn,
    try(aws_secretsmanager_secret.oauth_google[0].arn, ""),
    try(aws_secretsmanager_secret.oauth_github[0].arn, ""),
    try(aws_secretsmanager_secret.oauth_facebook[0].arn, ""),
    try(aws_secretsmanager_secret.opencage[0].arn, ""),
    try(aws_secretsmanager_secret.openai[0].arn, ""),
    try(aws_secretsmanager_secret.amplitude[0].arn, ""),
    try(aws_secretsmanager_secret.smtp[0].arn, ""),
  ])
}
