# =============================================================================
# Qdrant Module - Variables
# =============================================================================

# -----------------------------------------------------------------------------
# Environment
# -----------------------------------------------------------------------------

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

# -----------------------------------------------------------------------------
# Networking
# -----------------------------------------------------------------------------

variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "private_subnet_id" {
  description = "ID of the private subnet for Qdrant ECS task"
  type        = string
}

variable "qdrant_security_group_id" {
  description = "ID of the Qdrant security group"
  type        = string
}

# -----------------------------------------------------------------------------
# ECS Cluster
# -----------------------------------------------------------------------------

variable "cluster_id" {
  description = "ID of the ECS cluster"
  type        = string
}

variable "cluster_name" {
  description = "Name of the ECS cluster"
  type        = string
}

# -----------------------------------------------------------------------------
# EFS Storage
# -----------------------------------------------------------------------------

variable "efs_file_system_id" {
  description = "ID of the EFS file system"
  type        = string
}

variable "efs_access_point_id" {
  description = "ID of the EFS access point"
  type        = string
}

# -----------------------------------------------------------------------------
# Task Configuration
# -----------------------------------------------------------------------------

variable "cpu" {
  description = "CPU units for the Qdrant task (1 vCPU = 1024)"
  type        = number
  default     = 512
}

variable "memory" {
  description = "Memory (MB) for the Qdrant task"
  type        = number
  default     = 1024
}

variable "qdrant_version" {
  description = "Qdrant Docker image version"
  type        = string
  default     = "v1.7.4"
}

variable "desired_count" {
  description = "Number of Qdrant tasks to run"
  type        = number
  default     = 1
}

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30
}

variable "kms_key_arn" {
  description = "ARN of the KMS key for log encryption"
  type        = string
  default     = null
}
