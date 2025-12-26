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
# RDS Outputs
# -----------------------------------------------------------------------------

output "rds_endpoint" {
  description = "RDS endpoint"
  value       = module.rds.endpoint
}

output "rds_database_name" {
  description = "RDS database name"
  value       = module.rds.database_name
}

output "rds_connection_string" {
  description = "RDS connection string"
  value       = module.rds.connection_string
  sensitive   = true
}

# -----------------------------------------------------------------------------
# ElastiCache Outputs
# -----------------------------------------------------------------------------

output "redis_endpoint" {
  description = "Redis endpoint"
  value       = module.elasticache.endpoint
}

output "redis_url" {
  description = "Redis connection URL"
  value       = module.elasticache.redis_url
}

# -----------------------------------------------------------------------------
# ECS Outputs
# -----------------------------------------------------------------------------

output "alb_dns_name" {
  description = "ALB DNS name"
  value       = module.ecs.alb_dns_name
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = module.ecs.cluster_name
}

output "ecs_service_name" {
  description = "ECS service name"
  value       = module.ecs.service_name
}

output "api_url" {
  description = "URL to access the API"
  value       = module.ecs.api_url
}

# -----------------------------------------------------------------------------
# CloudFront Outputs
# -----------------------------------------------------------------------------

output "frontend_url" {
  description = "URL to access the frontend"
  value       = module.cloudfront.frontend_url
}

output "cloudfront_domain" {
  description = "CloudFront distribution domain"
  value       = module.cloudfront.distribution_domain_name
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID (for cache invalidation)"
  value       = module.cloudfront.distribution_id
}

output "frontend_bucket" {
  description = "S3 bucket name for frontend files"
  value       = module.cloudfront.bucket_name
}

output "frontend_deploy_command" {
  description = "AWS CLI command to deploy frontend files"
  value       = module.cloudfront.deploy_command
}

output "frontend_invalidate_command" {
  description = "AWS CLI command to invalidate CloudFront cache"
  value       = module.cloudfront.invalidate_command
}
