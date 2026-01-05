# =============================================================================
# EFS Module - Variables
# =============================================================================

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "private_subnet_id" {
  description = "ID of the private subnet for EFS mount target"
  type        = string
}

variable "efs_security_group_id" {
  description = "ID of the EFS security group"
  type        = string
}

variable "kms_key_arn" {
  description = "ARN of the KMS key for EFS encryption"
  type        = string
}

variable "enable_backups" {
  description = "Enable automatic backups via AWS Backup"
  type        = bool
  default     = true
}
