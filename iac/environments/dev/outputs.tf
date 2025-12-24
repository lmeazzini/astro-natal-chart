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
# Future outputs (uncomment as modules are added)
# -----------------------------------------------------------------------------

# output "vpc_id" {
#   description = "VPC ID"
#   value       = module.vpc.vpc_id
# }

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
