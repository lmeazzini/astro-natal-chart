# =============================================================================
# ECS Module - Service
# =============================================================================
# ECS Service using 100% Fargate Spot for cost optimization.
# Includes deployment circuit breaker and ECS Exec for debugging.
# =============================================================================

# -----------------------------------------------------------------------------
# ECS Service
# -----------------------------------------------------------------------------

resource "aws_ecs_service" "api" {
  name            = "${local.name_prefix}-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = var.desired_count

  # Use 100% Fargate Spot for cost savings (~70%)
  capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight            = 100
    base              = 0
  }

  # Network configuration
  network_configuration {
    subnets          = [var.private_subnet_id]
    security_groups  = [var.ecs_security_group_id]
    assign_public_ip = false # Private subnet, NAT Gateway for internet
  }

  # Load balancer integration
  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = var.container_port
  }

  # Deployment configuration for Spot resilience
  deployment_maximum_percent         = var.deployment_maximum_percent
  deployment_minimum_healthy_percent = var.deployment_minimum_healthy_percent

  # Circuit breaker for automatic rollback on failures
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  # Enable ECS Exec for interactive debugging
  enable_execute_command = true

  # Wait for load balancer to be ready
  health_check_grace_period_seconds = 60

  # Ensure the service waits for a stable state
  wait_for_steady_state = false

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-api-service"
  })

  # Ensure the target group exists before creating the service
  depends_on = [
    aws_lb_listener.http,
    aws_iam_role_policy.ecs_task_exec
  ]

  lifecycle {
    ignore_changes = [
      desired_count, # Allow external scaling (auto-scaling)
    ]
  }
}
