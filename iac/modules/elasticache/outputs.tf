# =============================================================================
# ElastiCache Module - Outputs
# =============================================================================
# Outputs for use by application configuration and other modules.
# =============================================================================

output "endpoint" {
  description = "Redis endpoint (hostname)"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
}

output "port" {
  description = "Redis port"
  value       = aws_elasticache_cluster.redis.port
}

output "redis_url" {
  description = "Redis connection URL"
  value       = "redis://${aws_elasticache_cluster.redis.cache_nodes[0].address}:${aws_elasticache_cluster.redis.port}/0"
}

output "cluster_id" {
  description = "ElastiCache cluster ID"
  value       = aws_elasticache_cluster.redis.cluster_id
}

output "cluster_arn" {
  description = "ElastiCache cluster ARN"
  value       = aws_elasticache_cluster.redis.arn
}

output "availability_zone" {
  description = "Availability zone of the Redis node"
  value       = aws_elasticache_cluster.redis.availability_zone
}

output "parameter_group_name" {
  description = "Name of the parameter group"
  value       = aws_elasticache_parameter_group.redis.name
}
