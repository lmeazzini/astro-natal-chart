# =============================================================================
# ElastiCache Module - Main Resources
# =============================================================================
# Creates ElastiCache Redis cluster with single-node configuration.
# Cost-optimized for development/staging environments.
#
# Features:
#   - Redis 7.1
#   - Single node (no replication)
#   - LRU eviction policy
#   - No snapshots (cache-only use case)
# =============================================================================

# -----------------------------------------------------------------------------
# Terraform Configuration
# -----------------------------------------------------------------------------

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# -----------------------------------------------------------------------------
# Local Variables
# -----------------------------------------------------------------------------

locals {
  name_prefix = "astro-${var.environment}"

  common_tags = merge(var.tags, {
    Module = "elasticache"
  })
}

# -----------------------------------------------------------------------------
# Parameter Group
# -----------------------------------------------------------------------------

resource "aws_elasticache_parameter_group" "redis" {
  name        = "${local.name_prefix}-redis-params"
  family      = var.parameter_family
  description = "Redis parameter group for ${var.environment}"

  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-redis-params"
  })
}

# -----------------------------------------------------------------------------
# ElastiCache Cluster
# -----------------------------------------------------------------------------

resource "aws_elasticache_cluster" "redis" {
  cluster_id = "${local.name_prefix}-redis"

  # Engine
  engine         = "redis"
  engine_version = var.engine_version

  # Instance
  node_type       = var.node_type
  num_cache_nodes = 1 # SINGLE NODE (cost optimization)

  # Network
  port               = var.port
  subnet_group_name  = var.subnet_group_name
  security_group_ids = [var.security_group_id]
  availability_zone  = var.availability_zone

  # Parameters
  parameter_group_name = aws_elasticache_parameter_group.redis.name

  # Maintenance
  maintenance_window = var.maintenance_window

  # No snapshots (cache-only use case)
  snapshot_retention_limit = 0

  # Apply changes
  apply_immediately = var.apply_immediately

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-redis"
  })
}
