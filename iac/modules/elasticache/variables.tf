# =============================================================================
# ElastiCache Module - Variables
# =============================================================================
# Input variables for the ElastiCache Redis module.
# Single-node configuration for cost optimization.
# =============================================================================

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "engine_version" {
  description = "Redis engine version"
  type        = string
  default     = "7.1"
}

variable "parameter_family" {
  description = "Redis parameter group family"
  type        = string
  default     = "redis7"
}

variable "subnet_group_name" {
  description = "ElastiCache subnet group name (from VPC module)"
  type        = string
}

variable "security_group_id" {
  description = "Security group ID for Redis (from VPC module)"
  type        = string
}

variable "availability_zone" {
  description = "Availability zone for the Redis node"
  type        = string
}

variable "port" {
  description = "Redis port"
  type        = number
  default     = 6379
}

variable "maintenance_window" {
  description = "Weekly maintenance window (UTC)"
  type        = string
  default     = "sun:05:00-sun:06:00"
}

variable "apply_immediately" {
  description = "Apply changes immediately (vs during maintenance window)"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
