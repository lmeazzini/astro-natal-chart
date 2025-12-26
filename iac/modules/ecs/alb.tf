# =============================================================================
# ECS Module - Application Load Balancer
# =============================================================================
# ALB configuration for routing traffic to ECS tasks.
# HTTP only initially; HTTPS requires ACM certificate (issue #247).
# =============================================================================

# -----------------------------------------------------------------------------
# Application Load Balancer
# -----------------------------------------------------------------------------

resource "aws_lb" "main" {
  name               = "${local.name_prefix}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.alb_security_group_id]
  subnets            = [var.public_subnet_id]

  # Enable deletion protection in production
  enable_deletion_protection = var.environment == "prod" ? true : false

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-alb"
  })
}

# -----------------------------------------------------------------------------
# Target Group
# -----------------------------------------------------------------------------

resource "aws_lb_target_group" "api" {
  name        = "${local.name_prefix}-api-tg"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip" # Required for Fargate with awsvpc network mode

  # Quick deregistration for Spot interruptions
  deregistration_delay = var.deregistration_delay

  health_check {
    enabled             = true
    path                = var.health_check_path
    port                = "traffic-port"
    protocol            = "HTTP"
    interval            = var.health_check_interval
    timeout             = var.health_check_timeout
    healthy_threshold   = var.health_check_healthy_threshold
    unhealthy_threshold = var.health_check_unhealthy_threshold
    matcher             = "200-299"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-api-tg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# -----------------------------------------------------------------------------
# HTTP Listener
# -----------------------------------------------------------------------------

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-http-listener"
  })
}

# -----------------------------------------------------------------------------
# HTTPS Listener (to be enabled when ACM certificate is available - issue #247)
# -----------------------------------------------------------------------------
#
# resource "aws_lb_listener" "https" {
#   load_balancer_arn = aws_lb.main.arn
#   port              = 443
#   protocol          = "HTTPS"
#   ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
#   certificate_arn   = var.certificate_arn
#
#   default_action {
#     type             = "forward"
#     target_group_arn = aws_lb_target_group.api.arn
#   }
#
#   tags = merge(local.common_tags, {
#     Name = "${local.name_prefix}-https-listener"
#   })
# }
#
# # Redirect HTTP to HTTPS
# resource "aws_lb_listener" "http_redirect" {
#   load_balancer_arn = aws_lb.main.arn
#   port              = 80
#   protocol          = "HTTP"
#
#   default_action {
#     type = "redirect"
#
#     redirect {
#       port        = "443"
#       protocol    = "HTTPS"
#       status_code = "HTTP_301"
#     }
#   }
# }
