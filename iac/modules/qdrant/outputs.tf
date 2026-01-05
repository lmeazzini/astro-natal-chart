# =============================================================================
# Qdrant Module - Outputs
# =============================================================================

output "service_discovery_endpoint" {
  description = "DNS endpoint for Qdrant service discovery"
  value       = "qdrant.${aws_service_discovery_private_dns_namespace.main.name}"
}

output "service_discovery_url" {
  description = "Full URL for Qdrant HTTP API via service discovery"
  value       = "http://qdrant.${aws_service_discovery_private_dns_namespace.main.name}:6333"
}

output "service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.qdrant.name
}

output "task_definition_arn" {
  description = "ARN of the Qdrant task definition"
  value       = aws_ecs_task_definition.qdrant.arn
}

output "log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.qdrant.name
}

output "namespace_id" {
  description = "ID of the Cloud Map namespace"
  value       = aws_service_discovery_private_dns_namespace.main.id
}

output "namespace_name" {
  description = "Name of the Cloud Map namespace"
  value       = aws_service_discovery_private_dns_namespace.main.name
}
