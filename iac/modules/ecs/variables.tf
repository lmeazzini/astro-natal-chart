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

variable "public_subnet_id" {
  description = "Public subnet ID for the ALB"
  type        = string
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
}

variable "memory" {
  description = "Memory in MB for the task"
  type        = number
  default     = 512
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

# -----------------------------------------------------------------------------
# Tags
# -----------------------------------------------------------------------------

variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
