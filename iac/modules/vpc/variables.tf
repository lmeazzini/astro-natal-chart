# =============================================================================
# VPC Module - Variables
# =============================================================================
# Input variables for the VPC module.
# Single AZ architecture optimized for cost (dev/staging environments).
# =============================================================================

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid IPv4 CIDR block."
  }
}

variable "availability_zone" {
  description = "Single availability zone for all resources (cost optimization)"
  type        = string
  default     = "us-east-1a"
}

variable "public_subnet_cidr" {
  description = "CIDR block for the public subnet (ALB, NAT Gateway)"
  type        = string
  default     = "10.0.1.0/24"
}

variable "private_subnet_cidr" {
  description = "CIDR block for the private subnet (ECS tasks)"
  type        = string
  default     = "10.0.11.0/24"
}

variable "database_subnet_cidr" {
  description = "CIDR block for the database subnet (RDS, ElastiCache)"
  type        = string
  default     = "10.0.21.0/24"
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnet internet access (adds ~$32/month)"
  type        = bool
  default     = true
}

variable "enable_dns_hostnames" {
  description = "Enable DNS hostnames in the VPC"
  type        = bool
  default     = true
}

variable "enable_dns_support" {
  description = "Enable DNS support in the VPC"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
