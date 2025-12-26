# =============================================================================
# S3 Module - Variables
# =============================================================================
# Input variables for S3 buckets module.
# Manages PDF storage, database backups, and optional logs buckets.
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
# KMS Encryption
# -----------------------------------------------------------------------------

variable "kms_key_arn" {
  description = "KMS key ARN for S3 encryption (from secrets module)"
  type        = string
}

# -----------------------------------------------------------------------------
# CORS Configuration
# -----------------------------------------------------------------------------

variable "allowed_origins" {
  description = "Allowed origins for CORS (presigned URL downloads)"
  type        = list(string)
  default     = ["*"]
}

# -----------------------------------------------------------------------------
# Feature Flags
# -----------------------------------------------------------------------------

variable "enable_logs_bucket" {
  description = "Create application logs bucket"
  type        = bool
  default     = false
}

variable "enable_versioning" {
  description = "Enable versioning on buckets"
  type        = bool
  default     = true
}

variable "force_destroy" {
  description = "Allow bucket deletion when not empty (dev only)"
  type        = bool
  default     = false
}

# -----------------------------------------------------------------------------
# Lifecycle Configuration - PDFs
# -----------------------------------------------------------------------------

variable "pdf_transition_to_ia_days" {
  description = "Days before transitioning PDFs to Standard-IA"
  type        = number
  default     = 90
}

variable "pdf_transition_to_glacier_days" {
  description = "Days before transitioning PDFs to Glacier"
  type        = number
  default     = 365
}

variable "pdf_noncurrent_expiration_days" {
  description = "Days before deleting noncurrent PDF versions"
  type        = number
  default     = 30
}

# -----------------------------------------------------------------------------
# Lifecycle Configuration - Backups
# -----------------------------------------------------------------------------

variable "backup_transition_to_glacier_days" {
  description = "Days before transitioning backups to Glacier"
  type        = number
  default     = 7
}

variable "backup_expiration_days" {
  description = "Days before expiring daily backups"
  type        = number
  default     = 30
}

variable "monthly_backup_expiration_days" {
  description = "Days before expiring monthly backups"
  type        = number
  default     = 365
}

# -----------------------------------------------------------------------------
# Lifecycle Configuration - Logs
# -----------------------------------------------------------------------------

variable "logs_expiration_days" {
  description = "Days before expiring logs"
  type        = number
  default     = 90
}

# -----------------------------------------------------------------------------
# Tags
# -----------------------------------------------------------------------------

variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
