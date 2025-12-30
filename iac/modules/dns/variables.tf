# =============================================================================
# DNS Module - Variables
# =============================================================================
# Input variables for Route53 and ACM certificate management.
# Supports both creating new hosted zones and using existing ones.
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
  description = "AWS region for ALB certificate"
  type        = string
  default     = "us-east-1"
}

# -----------------------------------------------------------------------------
# Domain Configuration
# -----------------------------------------------------------------------------

variable "domain_name" {
  description = "Root domain name (e.g., astro.example.com)"
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9.-]*[a-z0-9]$", var.domain_name))
    error_message = "Domain name must be a valid domain format."
  }
}

variable "create_hosted_zone" {
  description = "Create new hosted zone (true) or use existing (false)"
  type        = bool
  default     = false
}

variable "frontend_subdomain" {
  description = "Subdomain for frontend (e.g., www, app)"
  type        = string
  default     = "www"
}

variable "api_subdomain" {
  description = "Subdomain for API (e.g., api)"
  type        = string
  default     = "api"
}

variable "enable_root_redirect" {
  description = "Point root domain to CloudFront (same as www)"
  type        = bool
  default     = true
}

# -----------------------------------------------------------------------------
# CloudFront Integration
# -----------------------------------------------------------------------------

variable "cloudfront_domain_name" {
  description = "CloudFront distribution domain name (e.g., d1234.cloudfront.net)"
  type        = string
}

variable "cloudfront_hosted_zone_id" {
  description = "CloudFront distribution hosted zone ID (always Z2FDTNDATAQYW2)"
  type        = string
  default     = "Z2FDTNDATAQYW2" # Global CloudFront hosted zone ID
}

# -----------------------------------------------------------------------------
# ALB Integration
# -----------------------------------------------------------------------------

variable "alb_dns_name" {
  description = "ALB DNS name from ECS module"
  type        = string
}

variable "alb_zone_id" {
  description = "ALB hosted zone ID from ECS module"
  type        = string
}

# -----------------------------------------------------------------------------
# Certificate Configuration
# -----------------------------------------------------------------------------

variable "create_alb_certificate" {
  description = "Create ACM certificate for ALB (set false if using existing)"
  type        = bool
  default     = true
}

variable "wait_for_validation" {
  description = "Wait for certificate validation to complete"
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
