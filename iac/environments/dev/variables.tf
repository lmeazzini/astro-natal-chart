# =============================================================================
# Development Environment Variables
# =============================================================================

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

# -----------------------------------------------------------------------------
# VPC Variables
# -----------------------------------------------------------------------------

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zone" {
  description = "Availability zone for single-AZ deployment"
  type        = string
  default     = "us-east-1a"
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway (~$32/month). Set to false to save costs."
  type        = bool
  default     = true
}

# -----------------------------------------------------------------------------
# RDS Variables
# -----------------------------------------------------------------------------

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

# -----------------------------------------------------------------------------
# ElastiCache Variables
# -----------------------------------------------------------------------------

variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro"
}

# -----------------------------------------------------------------------------
# ECS Variables
# -----------------------------------------------------------------------------

variable "ecs_cpu" {
  description = "ECS task CPU units (256 = 0.25 vCPU)"
  type        = number
  default     = 256
}

variable "ecs_memory" {
  description = "ECS task memory (MB)"
  type        = number
  default     = 512
}

variable "ecs_desired_count" {
  description = "Number of ECS tasks to run"
  type        = number
  default     = 1
}

# -----------------------------------------------------------------------------
# Future variables (uncomment as modules are added)
# -----------------------------------------------------------------------------

# variable "s3_bucket_prefix" {
#   description = "Prefix for S3 bucket names"
#   type        = string
#   default     = "astro"
# }
