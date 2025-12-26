# =============================================================================
# ECR Module - Variables
# =============================================================================
# Input variables for AWS Elastic Container Registry management.
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
  description = "AWS region for the ECR repository"
  type        = string
  default     = "us-east-1"
}

# -----------------------------------------------------------------------------
# Repository Configuration
# -----------------------------------------------------------------------------

variable "repository_name" {
  description = "Name of the ECR repository (defaults to astro-api)"
  type        = string
  default     = "astro-api"
}

variable "image_tag_mutability" {
  description = "Image tag mutability setting (MUTABLE or IMMUTABLE)"
  type        = string
  default     = "MUTABLE"

  validation {
    condition     = contains(["MUTABLE", "IMMUTABLE"], var.image_tag_mutability)
    error_message = "Image tag mutability must be MUTABLE or IMMUTABLE."
  }
}

variable "scan_on_push" {
  description = "Enable image scanning on push"
  type        = bool
  default     = true
}

# -----------------------------------------------------------------------------
# Lifecycle Policy
# -----------------------------------------------------------------------------

variable "max_image_count" {
  description = "Maximum number of images to retain (older images are deleted)"
  type        = number
  default     = 30
}

variable "untagged_image_expiry_days" {
  description = "Days after which untagged images expire"
  type        = number
  default     = 7
}

# -----------------------------------------------------------------------------
# Tags
# -----------------------------------------------------------------------------

variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
