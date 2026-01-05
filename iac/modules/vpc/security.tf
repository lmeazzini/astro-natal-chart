# =============================================================================
# VPC Module - Security Groups
# =============================================================================
# Security groups for all application components with least-privilege access.
#
# Traffic flow:
#   Internet → ALB (80/443) → ECS (8000) → RDS (5432)
#                                       → Redis (6379)
# =============================================================================

# -----------------------------------------------------------------------------
# ALB Security Group
# -----------------------------------------------------------------------------
# Allows inbound HTTP/HTTPS from the internet.
# Outbound to ECS tasks only.

resource "aws_security_group" "alb" {
  name        = "${local.name_prefix}-alb-sg"
  description = "Security group for Application Load Balancer"
  vpc_id      = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-alb-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_vpc_security_group_ingress_rule" "alb_http" {
  security_group_id = aws_security_group.alb.id
  description       = "Allow HTTP from internet"
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
  cidr_ipv4         = "0.0.0.0/0"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-alb-http"
  })
}

resource "aws_vpc_security_group_ingress_rule" "alb_https" {
  security_group_id = aws_security_group.alb.id
  description       = "Allow HTTPS from internet"
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
  cidr_ipv4         = "0.0.0.0/0"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-alb-https"
  })
}

resource "aws_vpc_security_group_egress_rule" "alb_to_ecs" {
  security_group_id            = aws_security_group.alb.id
  description                  = "Allow traffic to ECS tasks"
  from_port                    = 8000
  to_port                      = 8000
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.ecs.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-alb-to-ecs"
  })
}

# -----------------------------------------------------------------------------
# ECS Security Group
# -----------------------------------------------------------------------------
# Allows inbound from ALB only.
# Outbound to RDS, Redis, and internet (for pulling images and external APIs).

resource "aws_security_group" "ecs" {
  name        = "${local.name_prefix}-ecs-sg"
  description = "Security group for ECS tasks"
  vpc_id      = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ecs-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_vpc_security_group_ingress_rule" "ecs_from_alb" {
  security_group_id            = aws_security_group.ecs.id
  description                  = "Allow traffic from ALB"
  from_port                    = 8000
  to_port                      = 8000
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.alb.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ecs-from-alb"
  })
}

resource "aws_vpc_security_group_egress_rule" "ecs_to_rds" {
  security_group_id            = aws_security_group.ecs.id
  description                  = "Allow traffic to RDS"
  from_port                    = 5432
  to_port                      = 5432
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.rds.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ecs-to-rds"
  })
}

resource "aws_vpc_security_group_egress_rule" "ecs_to_redis" {
  security_group_id            = aws_security_group.ecs.id
  description                  = "Allow traffic to Redis"
  from_port                    = 6379
  to_port                      = 6379
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.redis.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ecs-to-redis"
  })
}

resource "aws_vpc_security_group_egress_rule" "ecs_to_internet_https" {
  security_group_id = aws_security_group.ecs.id
  description       = "Allow HTTPS to internet (for pulling images and external APIs)"
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
  cidr_ipv4         = "0.0.0.0/0"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ecs-to-internet-https"
  })
}

resource "aws_vpc_security_group_egress_rule" "ecs_to_internet_http" {
  security_group_id = aws_security_group.ecs.id
  description       = "Allow HTTP to internet (for some package managers)"
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
  cidr_ipv4         = "0.0.0.0/0"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ecs-to-internet-http"
  })
}

# -----------------------------------------------------------------------------
# RDS Security Group
# -----------------------------------------------------------------------------
# Allows inbound from ECS only.
# No outbound rules needed (stateful).

resource "aws_security_group" "rds" {
  name        = "${local.name_prefix}-rds-sg"
  description = "Security group for RDS PostgreSQL"
  vpc_id      = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-rds-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_vpc_security_group_ingress_rule" "rds_from_ecs" {
  security_group_id            = aws_security_group.rds.id
  description                  = "Allow PostgreSQL from ECS"
  from_port                    = 5432
  to_port                      = 5432
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.ecs.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-rds-from-ecs"
  })
}

# -----------------------------------------------------------------------------
# Redis Security Group
# -----------------------------------------------------------------------------
# Allows inbound from ECS only.
# No outbound rules needed (stateful).

resource "aws_security_group" "redis" {
  name        = "${local.name_prefix}-redis-sg"
  description = "Security group for ElastiCache Redis"
  vpc_id      = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-redis-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_vpc_security_group_ingress_rule" "redis_from_ecs" {
  security_group_id            = aws_security_group.redis.id
  description                  = "Allow Redis from ECS"
  from_port                    = 6379
  to_port                      = 6379
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.ecs.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-redis-from-ecs"
  })
}

# -----------------------------------------------------------------------------
# Qdrant Security Group
# -----------------------------------------------------------------------------
# Allows inbound from ECS API tasks only.
# Outbound to EFS for persistent storage.

resource "aws_security_group" "qdrant" {
  name        = "${local.name_prefix}-qdrant-sg"
  description = "Security group for Qdrant vector database"
  vpc_id      = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-qdrant-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_vpc_security_group_ingress_rule" "qdrant_http_from_ecs" {
  security_group_id            = aws_security_group.qdrant.id
  description                  = "Allow HTTP API from ECS"
  from_port                    = 6333
  to_port                      = 6333
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.ecs.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-qdrant-http-from-ecs"
  })
}

resource "aws_vpc_security_group_ingress_rule" "qdrant_grpc_from_ecs" {
  security_group_id            = aws_security_group.qdrant.id
  description                  = "Allow gRPC from ECS"
  from_port                    = 6334
  to_port                      = 6334
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.ecs.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-qdrant-grpc-from-ecs"
  })
}

resource "aws_vpc_security_group_egress_rule" "qdrant_to_efs" {
  security_group_id            = aws_security_group.qdrant.id
  description                  = "Allow NFS to EFS"
  from_port                    = 2049
  to_port                      = 2049
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.efs.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-qdrant-to-efs"
  })
}

resource "aws_vpc_security_group_egress_rule" "qdrant_to_https" {
  security_group_id = aws_security_group.qdrant.id
  description       = "Allow HTTPS for CloudWatch Logs and ECR"
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
  cidr_ipv4         = "0.0.0.0/0"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-qdrant-to-https"
  })
}

# ECS egress to Qdrant
resource "aws_vpc_security_group_egress_rule" "ecs_to_qdrant" {
  security_group_id            = aws_security_group.ecs.id
  description                  = "Allow traffic to Qdrant"
  from_port                    = 6333
  to_port                      = 6334
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.qdrant.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ecs-to-qdrant"
  })
}

# -----------------------------------------------------------------------------
# EFS Security Group
# -----------------------------------------------------------------------------
# Allows inbound NFS from Qdrant only.
# No outbound rules needed (stateful).

resource "aws_security_group" "efs" {
  name        = "${local.name_prefix}-efs-sg"
  description = "Security group for EFS mount targets"
  vpc_id      = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-efs-sg"
  })

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_vpc_security_group_ingress_rule" "efs_from_qdrant" {
  security_group_id            = aws_security_group.efs.id
  description                  = "Allow NFS from Qdrant"
  from_port                    = 2049
  to_port                      = 2049
  ip_protocol                  = "tcp"
  referenced_security_group_id = aws_security_group.qdrant.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-efs-from-qdrant"
  })
}
