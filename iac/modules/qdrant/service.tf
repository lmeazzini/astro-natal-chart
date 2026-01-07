# =============================================================================
# Qdrant Module - ECS Service & Service Discovery
# =============================================================================
# ECS Service with AWS Cloud Map for internal DNS-based service discovery.
# =============================================================================

# -----------------------------------------------------------------------------
# Service Discovery Namespace
# -----------------------------------------------------------------------------
# Creates a private DNS namespace for internal service discovery.
# Format: {service}.{environment}.local (e.g., qdrant.astro-prod.local)

resource "aws_service_discovery_private_dns_namespace" "main" {
  name        = "${local.name_prefix}.local"
  description = "Service discovery namespace for ${var.environment} environment"
  vpc         = var.vpc_id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-namespace"
  })
}

# -----------------------------------------------------------------------------
# Service Discovery Service
# -----------------------------------------------------------------------------
# Registers Qdrant with Cloud Map for DNS-based discovery.

resource "aws_service_discovery_service" "qdrant" {
  name = "qdrant"

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.main.id

    dns_records {
      ttl  = 10
      type = "A"
    }

    routing_policy = "MULTIVALUE"
  }

  # NOTE: health_check_custom_config is NOT set here to avoid forcing replacement
  # of existing service discovery services with registered instances.
  # ECS handles health checks automatically via the service integration.

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-qdrant-discovery"
  })
}

# -----------------------------------------------------------------------------
# ECS Service
# -----------------------------------------------------------------------------
# NOTE: Uses standard Fargate (NOT Spot!) because Qdrant is a stateful service.
# Spot interruptions can cause data corruption during writes.

resource "aws_ecs_service" "qdrant" {
  name            = "${local.name_prefix}-qdrant"
  cluster         = var.cluster_id
  task_definition = aws_ecs_task_definition.qdrant.arn
  desired_count   = var.desired_count

  # Use standard Fargate for stateful workload (NOT Spot!)
  capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 100
    base              = 1
  }

  network_configuration {
    subnets          = [var.private_subnet_id]
    security_groups  = [var.qdrant_security_group_id]
    assign_public_ip = false
  }

  # Service Discovery registration
  service_registries {
    registry_arn = aws_service_discovery_service.qdrant.arn
  }

  # Deployment configuration
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  deployment_maximum_percent         = 100
  deployment_minimum_healthy_percent = 0

  # ECS Exec for debugging
  enable_execute_command = true

  # EFS requires platform version 1.4.0+
  platform_version = "1.4.0"

  # Prevent service from starting before EFS is ready
  depends_on = [
    aws_iam_role_policy.qdrant_task_efs
  ]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-qdrant-service"
  })

  lifecycle {
    ignore_changes = [desired_count]
  }
}
