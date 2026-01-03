# =============================================================================
# Secrets Module - Variables
# =============================================================================
# Input variables for AWS Secrets Manager module.
# Manages application secrets with KMS encryption.
# =============================================================================

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

# -----------------------------------------------------------------------------
# Core Secrets (Required)
# -----------------------------------------------------------------------------

variable "database_url" {
  description = "PostgreSQL connection string (from RDS module)"
  type        = string
  sensitive   = true
}

variable "redis_url" {
  description = "Redis connection string (from ElastiCache module)"
  type        = string
  sensitive   = true
}

variable "jwt_secret_key" {
  description = "JWT signing secret key (auto-generated if null)"
  type        = string
  default     = null
  sensitive   = true
}

# -----------------------------------------------------------------------------
# OAuth Credentials (Optional)
# -----------------------------------------------------------------------------

variable "google_oauth" {
  description = "Google OAuth2 credentials"
  type = object({
    client_id     = string
    client_secret = string
  })
  default   = null
  sensitive = true
}

variable "github_oauth" {
  description = "GitHub OAuth credentials"
  type = object({
    client_id     = string
    client_secret = string
  })
  default   = null
  sensitive = true
}

variable "facebook_oauth" {
  description = "Facebook OAuth credentials"
  type = object({
    client_id     = string
    client_secret = string
  })
  default   = null
  sensitive = true
}

# -----------------------------------------------------------------------------
# API Keys (Optional)
# -----------------------------------------------------------------------------

variable "opencage_api_key" {
  description = "OpenCage geocoding API key"
  type        = string
  default     = null
  sensitive   = true
}

variable "openai_api_key" {
  description = "OpenAI API key for AI interpretations"
  type        = string
  default     = null
  sensitive   = true
}

variable "amplitude_api_key" {
  description = "Amplitude analytics API key"
  type        = string
  default     = null
  sensitive   = true
}

# -----------------------------------------------------------------------------
# Stripe Configuration (Optional)
# -----------------------------------------------------------------------------

variable "stripe_secret_key" {
  description = "Stripe Secret API Key for payment processing"
  type        = string
  default     = null
  sensitive   = true
}

variable "stripe_webhook_secret" {
  description = "Stripe Webhook Signing Secret for verifying webhook events"
  type        = string
  default     = null
  sensitive   = true
}

variable "stripe_price_ids" {
  description = "Stripe Price IDs for subscription plans"
  type = object({
    starter   = string
    pro       = string
    unlimited = string
  })
  default   = null
  sensitive = true
}

# -----------------------------------------------------------------------------
# SMTP Configuration (Optional)
# -----------------------------------------------------------------------------

variable "smtp_config" {
  description = "SMTP email configuration"
  type = object({
    host     = string
    port     = number
    username = string
    password = string
  })
  default   = null
  sensitive = true
}

# -----------------------------------------------------------------------------
# IAM Roles (for KMS policy)
# -----------------------------------------------------------------------------

variable "ecs_task_role_arn" {
  description = "ECS task role ARN for KMS access"
  type        = string
}

variable "ecs_execution_role_arn" {
  description = "ECS execution role ARN for Secrets Manager access"
  type        = string
}

# -----------------------------------------------------------------------------
# Tags
# -----------------------------------------------------------------------------

variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
