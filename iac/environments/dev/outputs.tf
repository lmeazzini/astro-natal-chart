# =============================================================================
# Development Environment Outputs
# =============================================================================

output "account_id" {
  description = "AWS Account ID"
  value       = data.aws_caller_identity.current.account_id
}

output "region" {
  description = "AWS Region"
  value       = data.aws_region.current.name
}

output "environment" {
  description = "Environment name"
  value       = var.environment
}

# -----------------------------------------------------------------------------
# VPC Outputs
# -----------------------------------------------------------------------------

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "public_subnet_id" {
  description = "Public subnet ID"
  value       = module.vpc.public_subnet_id
}

output "private_subnet_id" {
  description = "Private subnet ID"
  value       = module.vpc.private_subnet_id
}

output "database_subnet_id" {
  description = "Database subnet ID"
  value       = module.vpc.database_subnet_id
}

output "nat_gateway_public_ip" {
  description = "NAT Gateway public IP"
  value       = module.vpc.nat_gateway_public_ip
}

# -----------------------------------------------------------------------------
# Future outputs (uncomment as modules are added)
# -----------------------------------------------------------------------------

# output "alb_dns_name" {
#   description = "ALB DNS name"
#   value       = module.ecs.alb_dns_name
# }

# output "rds_endpoint" {
#   description = "RDS endpoint"
#   value       = module.rds.endpoint
# }

# output "redis_endpoint" {
#   description = "Redis endpoint"
#   value       = module.elasticache.endpoint
# }

# output "cloudfront_domain" {
#   description = "CloudFront distribution domain"
#   value       = module.cloudfront.distribution_domain_name
# }
