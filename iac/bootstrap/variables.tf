# =============================================================================
# Bootstrap Variables
# =============================================================================

variable "aws_region" {
  description = "AWS region for the state bucket and lock table"
  type        = string
  default     = "us-east-1"
}
