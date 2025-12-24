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
# Future variables (uncomment as modules are added)
# -----------------------------------------------------------------------------

# variable "vpc_cidr" {
#   description = "CIDR block for VPC"
#   type        = string
#   default     = "10.0.0.0/16"
# }

# variable "availability_zone" {
#   description = "Availability zone for single-AZ deployment"
#   type        = string
#   default     = "us-east-1a"
# }

# variable "db_instance_class" {
#   description = "RDS instance class"
#   type        = string
#   default     = "db.t3.micro"
# }

# variable "redis_node_type" {
#   description = "ElastiCache node type"
#   type        = string
#   default     = "cache.t3.micro"
# }

# variable "ecs_cpu" {
#   description = "ECS task CPU units"
#   type        = number
#   default     = 256
# }

# variable "ecs_memory" {
#   description = "ECS task memory (MB)"
#   type        = number
#   default     = 512
# }
