# =============================================================================
# CloudFront Module - Variables
# =============================================================================
# Input variables for S3 + CloudFront static site hosting.
# Optimized for React SPA deployment with global CDN distribution.
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
  description = "AWS region for S3 bucket (CloudFront is global)"
  type        = string
  default     = "us-east-1"
}

# -----------------------------------------------------------------------------
# CloudFront Distribution Configuration
# -----------------------------------------------------------------------------

variable "domain_aliases" {
  description = "Custom domain names for the distribution (requires ACM certificate)"
  type        = list(string)
  default     = []

  validation {
    condition = alltrue([
      for domain in var.domain_aliases : can(regex("^[a-z0-9][a-z0-9-]*(\\.[a-z0-9][a-z0-9-]*)+$", domain))
    ])
    error_message = "All domain aliases must be valid domain names."
  }
}

variable "acm_certificate_arn" {
  description = "ACM certificate ARN for HTTPS (must be in us-east-1 for CloudFront)"
  type        = string
  default     = null

  validation {
    condition     = var.acm_certificate_arn == null || can(regex("^arn:aws:acm:us-east-1:", var.acm_certificate_arn))
    error_message = "ACM certificate must be in us-east-1 region for CloudFront."
  }
}

variable "price_class" {
  description = "CloudFront price class (PriceClass_100 = US/Canada/Europe, PriceClass_200 = adds Asia, PriceClass_All = global)"
  type        = string
  default     = "PriceClass_100"

  validation {
    condition     = contains(["PriceClass_100", "PriceClass_200", "PriceClass_All"], var.price_class)
    error_message = "Price class must be one of: PriceClass_100, PriceClass_200, PriceClass_All."
  }
}

# -----------------------------------------------------------------------------
# Cache Configuration
# -----------------------------------------------------------------------------

variable "default_ttl" {
  description = "Default TTL in seconds (how long objects are cached)"
  type        = number
  default     = 86400 # 1 day

  validation {
    condition     = var.default_ttl >= 0 && var.default_ttl <= 31536000
    error_message = "Default TTL must be between 0 and 31536000 seconds (1 year)."
  }
}

variable "min_ttl" {
  description = "Minimum TTL in seconds"
  type        = number
  default     = 0

  validation {
    condition     = var.min_ttl >= 0
    error_message = "Minimum TTL must be 0 or greater."
  }
}

variable "max_ttl" {
  description = "Maximum TTL in seconds"
  type        = number
  default     = 31536000 # 1 year

  validation {
    condition     = var.max_ttl >= 0 && var.max_ttl <= 31536000
    error_message = "Maximum TTL must be between 0 and 31536000 seconds (1 year)."
  }
}

# -----------------------------------------------------------------------------
# Security
# -----------------------------------------------------------------------------

variable "enable_waf" {
  description = "Enable AWS WAF for the distribution (additional cost)"
  type        = bool
  default     = false
}

variable "waf_web_acl_arn" {
  description = "ARN of WAF Web ACL to associate with the distribution"
  type        = string
  default     = null
}

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

variable "enable_access_logs" {
  description = "Enable CloudFront access logging to S3"
  type        = bool
  default     = false
}

variable "access_logs_bucket" {
  description = "S3 bucket for access logs (must exist if enable_access_logs is true)"
  type        = string
  default     = null
}

variable "access_logs_prefix" {
  description = "Prefix for access log files in S3"
  type        = string
  default     = "cloudfront-logs/"
}

# -----------------------------------------------------------------------------
# S3 Bucket Configuration
# -----------------------------------------------------------------------------

variable "force_destroy" {
  description = "Allow bucket deletion even when not empty (USE WITH CAUTION)"
  type        = bool
  default     = false
}

variable "enable_versioning" {
  description = "Enable S3 bucket versioning for rollback capability"
  type        = bool
  default     = true
}

# -----------------------------------------------------------------------------
# Tags
# -----------------------------------------------------------------------------

variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
