# =============================================================================
# ECS Module - Variables
# =============================================================================
# Input variables for the ECS Fargate module with Spot instances.
# Single-AZ, cost-optimized configuration.
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
# Network Variables (from VPC module)
# -----------------------------------------------------------------------------

variable "vpc_id" {
  description = "VPC ID for the ECS cluster"
  type        = string
}

variable "public_subnet_ids" {
  description = "Public subnet IDs for the ALB (requires 2+ in different AZs)"
  type        = list(string)
}

variable "private_subnet_id" {
  description = "Private subnet ID for ECS tasks"
  type        = string
}

variable "alb_security_group_id" {
  description = "Security group ID for the ALB (from VPC module)"
  type        = string
}

variable "ecs_security_group_id" {
  description = "Security group ID for ECS tasks (from VPC module)"
  type        = string
}

# -----------------------------------------------------------------------------
# ECS Task Configuration
# -----------------------------------------------------------------------------

variable "cpu" {
  description = "CPU units for the task (256 = 0.25 vCPU)"
  type        = number
  default     = 256

  validation {
    condition     = contains([256, 512, 1024, 2048, 4096, 8192, 16384], var.cpu)
    error_message = "CPU must be a valid Fargate value: 256, 512, 1024, 2048, 4096, 8192, or 16384."
  }
}

variable "memory" {
  description = "Memory in MB for the task"
  type        = number
  default     = 512

  validation {
    condition = (
      (var.memory >= 512 && var.memory <= 30720) ||
      contains([512, 1024, 2048, 3072, 4096, 5120, 6144, 7168, 8192], var.memory)
    )
    error_message = "Memory must be between 512 MB and 30720 MB (valid Fargate values)."
  }
}

variable "desired_count" {
  description = "Number of tasks to run (2+ recommended for Spot resilience)"
  type        = number
  default     = 1
}

variable "container_port" {
  description = "Port the container listens on"
  type        = number
  default     = 8000
}

# -----------------------------------------------------------------------------
# Container Image
# -----------------------------------------------------------------------------

variable "container_image" {
  description = "Container image to run (defaults to nginx placeholder)"
  type        = string
  default     = "nginx:alpine"

  validation {
    condition     = length(var.container_image) > 0
    error_message = "Container image must not be empty."
  }
}

# -----------------------------------------------------------------------------
# Health Check
# -----------------------------------------------------------------------------

variable "health_check_path" {
  description = "Path for ALB health checks"
  type        = string
  default     = "/health"
}

variable "health_check_interval" {
  description = "Interval between health checks (seconds)"
  type        = number
  default     = 30
}

variable "health_check_timeout" {
  description = "Health check timeout (seconds)"
  type        = number
  default     = 5
}

variable "health_check_healthy_threshold" {
  description = "Number of consecutive successes before healthy"
  type        = number
  default     = 2
}

variable "health_check_unhealthy_threshold" {
  description = "Number of consecutive failures before unhealthy"
  type        = number
  default     = 3
}

# -----------------------------------------------------------------------------
# Deployment Configuration
# -----------------------------------------------------------------------------

variable "deployment_maximum_percent" {
  description = "Maximum percent of tasks during deployment"
  type        = number
  default     = 200
}

variable "deployment_minimum_healthy_percent" {
  description = "Minimum percent of healthy tasks during deployment"
  type        = number
  default     = 50
}

variable "deregistration_delay" {
  description = "Seconds to wait before deregistering targets"
  type        = number
  default     = 30
}

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30
}

variable "log_encryption_kms_key_arn" {
  description = "KMS key ARN for CloudWatch Logs encryption (optional, null for no encryption)"
  type        = string
  default     = null
}

# -----------------------------------------------------------------------------
# S3 Access
# -----------------------------------------------------------------------------

variable "s3_bucket_arns" {
  description = "List of S3 bucket ARNs the task can access (for PDF storage, etc.)"
  type        = list(string)
  default     = []

  validation {
    condition = alltrue([
      for arn in var.s3_bucket_arns : can(regex("^arn:aws:s3:::", arn))
    ])
    error_message = "All S3 bucket ARNs must be valid (start with arn:aws:s3:::)."
  }
}

variable "s3_pdf_policy_arn" {
  description = "IAM policy ARN for S3 PDF access (from S3 module, includes KMS permissions)"
  type        = string
  default     = null
}

variable "ecr_pull_policy_arn" {
  description = "IAM policy ARN for pulling images from ECR (from ECR module)"
  type        = string
  default     = null
}

# -----------------------------------------------------------------------------
# SSL/TLS Configuration
# -----------------------------------------------------------------------------

variable "acm_certificate_arn" {
  description = "ACM certificate ARN for HTTPS listener (from DNS module)"
  type        = string
  default     = null
}

variable "ssl_policy" {
  description = "SSL policy for HTTPS listener"
  type        = string
  default     = "ELBSecurityPolicy-TLS13-1-2-2021-06"
}

# -----------------------------------------------------------------------------
# Secrets Manager Integration
# -----------------------------------------------------------------------------

variable "secret_arns" {
  description = "Map of secret ARNs for ECS task environment variable injection"
  type = object({
    database_url          = string
    redis_url             = string
    secret_key            = string
    stripe_secret_key     = optional(string)
    stripe_webhook_secret = optional(string)
    stripe_price_ids      = optional(string)
  })
  default = null
}

variable "kms_key_arn" {
  description = "KMS key ARN used to encrypt secrets (for decrypt permissions)"
  type        = string
  default     = null
}

# -----------------------------------------------------------------------------
# Tags
# -----------------------------------------------------------------------------

variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
