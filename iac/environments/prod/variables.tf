# =============================================================================
# Production Environment Variables
# =============================================================================

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-2"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

# -----------------------------------------------------------------------------
# VPC Variables
# -----------------------------------------------------------------------------

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.1.0.0/16" # Different CIDR from dev
}

variable "availability_zone" {
  description = "Availability zone for single-AZ deployment"
  type        = string
  default     = "us-east-2a"
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway (~$32/month). Required for private subnet internet access."
  type        = bool
  default     = true
}

variable "availability_zone_secondary" {
  description = "Secondary availability zone (required by RDS and ALB)"
  type        = string
  default     = "us-east-2b"
}

variable "public_subnet_cidr" {
  description = "CIDR block for the primary public subnet"
  type        = string
  default     = "10.1.1.0/24"
}

variable "public_subnet_cidr_secondary" {
  description = "CIDR block for the secondary public subnet"
  type        = string
  default     = "10.1.2.0/24"
}

variable "private_subnet_cidr" {
  description = "CIDR block for the private subnet"
  type        = string
  default     = "10.1.11.0/24"
}

variable "database_subnet_cidr" {
  description = "CIDR block for the primary database subnet"
  type        = string
  default     = "10.1.21.0/24"
}

variable "database_subnet_cidr_secondary" {
  description = "CIDR block for the secondary database subnet"
  type        = string
  default     = "10.1.22.0/24"
}

# -----------------------------------------------------------------------------
# RDS Variables
# -----------------------------------------------------------------------------

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro" # Can upgrade to db.t3.small for more performance
}

# -----------------------------------------------------------------------------
# ElastiCache Variables
# -----------------------------------------------------------------------------

variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro" # Can upgrade for more memory/performance
}

# -----------------------------------------------------------------------------
# ECS Variables
# -----------------------------------------------------------------------------

variable "ecs_cpu" {
  description = "ECS task CPU units (256 = 0.25 vCPU)"
  type        = number
  default     = 512 # More CPU for production
}

variable "ecs_memory" {
  description = "ECS task memory (MB)"
  type        = number
  default     = 1024 # More memory for production
}

variable "ecs_desired_count" {
  description = "Number of ECS tasks to run"
  type        = number
  default     = 1 # Can increase for HA
}

# -----------------------------------------------------------------------------
# S3/CloudFront Variables
# -----------------------------------------------------------------------------

variable "allowed_origins" {
  description = "CORS allowed origins for S3 presigned URLs"
  type        = list(string)
  default     = [] # Set in terraform.tfvars with your domain
}

variable "cloudfront_price_class" {
  description = "CloudFront price class"
  type        = string
  default     = "PriceClass_100" # US, Canada, Europe
}

variable "cloudfront_default_ttl" {
  description = "Default TTL for CloudFront cache (seconds)"
  type        = number
  default     = 86400 # 24 hours for production
}

# -----------------------------------------------------------------------------
# DNS Variables (optional - skip DNS module if not set)
# -----------------------------------------------------------------------------

variable "domain_name" {
  description = "Root domain name for the application (optional, skip DNS if null)"
  type        = string
  default     = null
}

variable "create_hosted_zone" {
  description = "Create new hosted zone (true) or use existing (false)"
  type        = bool
  default     = false
}

variable "frontend_subdomain" {
  description = "Subdomain for frontend"
  type        = string
  default     = "www"
}

variable "api_subdomain" {
  description = "Subdomain for API"
  type        = string
  default     = "api"
}

# -----------------------------------------------------------------------------
# API Keys (optional)
# -----------------------------------------------------------------------------

variable "openai_api_key" {
  description = "OpenAI API Key for AI interpretations"
  type        = string
  default     = null
  sensitive   = true
}

# -----------------------------------------------------------------------------
# Stripe Variables (optional - for payment processing)
# -----------------------------------------------------------------------------

variable "stripe_secret_key" {
  description = "Stripe Secret API Key (sk_live_...)"
  type        = string
  default     = null
  sensitive   = true
}

variable "stripe_webhook_secret" {
  description = "Stripe Webhook Signing Secret (whsec_...)"
  type        = string
  default     = null
  sensitive   = true
}

variable "stripe_price_ids" {
  description = "Stripe Price IDs for subscription plans"
  type = object({
    starter   = string
    pro       = string
    unlimited = string
  })
  default   = null
  sensitive = true
}
