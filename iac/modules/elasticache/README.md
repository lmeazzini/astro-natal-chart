# ElastiCache Module

Terraform module for creating an ElastiCache Redis cluster with single-node configuration.

## Architecture

Single-node deployment optimized for cost in development/staging environments.

```
┌─────────────────────────────────────────┐
│            Database Subnet              │
│                                         │
│   ┌─────────────────────────────────┐   │
│   │      ElastiCache Redis 7.1      │   │
│   │      cache.t3.micro             │   │
│   │                                 │   │
│   │   - Single node (no replica)    │   │
│   │   - LRU eviction policy         │   │
│   │   - No snapshots                │   │
│   │   - In-transit encryption       │   │
│   └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

## Usage

```hcl
module "elasticache" {
  source = "../../modules/elasticache"

  environment       = "dev"
  node_type         = "cache.t3.micro"
  subnet_group_name = module.vpc.elasticache_subnet_group_name
  security_group_id = module.vpc.redis_security_group_id
  availability_zone = "us-east-1a"
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| environment | Environment name (dev, staging, prod) | string | - | yes |
| node_type | ElastiCache node type | string | "cache.t3.micro" | no |
| engine_version | Redis version | string | "7.1" | no |
| parameter_family | Parameter group family | string | "redis7" | no |
| subnet_group_name | Subnet group name | string | - | yes |
| security_group_id | Security group ID | string | - | yes |
| availability_zone | Availability zone | string | - | yes |
| port | Redis port | number | 6379 | no |
| maintenance_window | Maintenance window (UTC) | string | "sun:05:00-sun:06:00" | no |
| apply_immediately | Apply changes immediately | bool | true | no |

## Outputs

| Name | Description |
|------|-------------|
| endpoint | Redis endpoint (hostname) |
| port | Redis port (6379) |
| redis_url | Full Redis URL |
| cluster_id | ElastiCache cluster ID |
| cluster_arn | ElastiCache cluster ARN |
| availability_zone | Node availability zone |
| parameter_group_name | Parameter group name |

## Cost Estimation

| Node Type | Monthly Cost |
|-----------|-------------|
| cache.t3.micro | ~$12 |
| cache.t3.small | ~$24 |
| cache.t3.medium | ~$48 |

Note: Single node. Replication doubles the cost.

## Use Cases

This Redis instance is configured for:

- **Rate Limiting** (SlowAPI)
- **Celery Broker/Backend**
- **Session Caching**
- **General Caching**

## Failure Scenario

If the Redis node fails:

1. ElastiCache auto-detects failure (~1 min)
2. New node provisioned (~3-5 min)
3. Cache is cold (empty) - rebuilds naturally

**Impact**: Temporary increased latency, rate limiting resets.

**Mitigation**: Application handles Redis unavailability gracefully.

## Notes

1. **Single Node**: No automatic failover. ~5 min recovery on failure.
2. **No Snapshots**: Cache-only use case, data is ephemeral.
3. **LRU Eviction**: Least Recently Used keys evicted when memory is full.
4. **Same AZ**: Placed in same AZ as ECS/RDS for low latency.
