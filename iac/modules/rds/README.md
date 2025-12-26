# RDS Module

Terraform module for creating an RDS PostgreSQL instance with single-AZ configuration.

## Architecture

Single-AZ deployment optimized for cost in development/staging environments.

```
┌─────────────────────────────────────────┐
│            Database Subnet              │
│                                         │
│   ┌─────────────────────────────────┐   │
│   │      RDS PostgreSQL 16          │   │
│   │      db.t3.micro                │   │
│   │                                 │   │
│   │   - Single-AZ (no Multi-AZ)     │   │
│   │   - 20-100 GB gp3 storage       │   │
│   │   - Encrypted at rest           │   │
│   │   - 7-day backup retention      │   │
│   │   - Performance Insights        │   │
│   └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

## Usage

```hcl
module "rds" {
  source = "../../modules/rds"

  environment          = "dev"
  instance_class       = "db.t3.micro"
  db_subnet_group_name = module.vpc.db_subnet_group_name
  security_group_id    = module.vpc.rds_security_group_id
  availability_zone    = "us-east-1a"
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| environment | Environment name (dev, staging, prod) | string | - | yes |
| instance_class | RDS instance class | string | "db.t3.micro" | no |
| allocated_storage | Initial storage in GB | number | 20 | no |
| max_allocated_storage | Max storage for autoscaling | number | 100 | no |
| db_name | Database name | string | "astro" | no |
| db_username | Master username | string | "astro_admin" | no |
| engine_version | PostgreSQL version | string | "16" | no |
| db_subnet_group_name | DB subnet group name | string | - | yes |
| security_group_id | Security group ID | string | - | yes |
| availability_zone | Availability zone | string | - | yes |
| backup_retention_period | Backup retention days | number | 7 | no |
| deletion_protection | Enable deletion protection | bool | false | no |
| skip_final_snapshot | Skip final snapshot | bool | true | no |

## Outputs

| Name | Description |
|------|-------------|
| endpoint | RDS endpoint (hostname:port) |
| address | RDS address (hostname only) |
| port | RDS port (5432) |
| database_name | Database name |
| username | Master username |
| password | Master password (sensitive) |
| connection_string | Full connection string (sensitive) |
| instance_id | RDS instance ID |
| instance_arn | RDS instance ARN |

## Cost Estimation

| Instance | Monthly Cost |
|----------|-------------|
| db.t3.micro | ~$13 |
| db.t3.small | ~$26 |
| db.t3.medium | ~$52 |

Note: Costs are for single-AZ. Multi-AZ doubles the cost.

## Disaster Recovery

Without Multi-AZ, recovery options are:

1. **Point-in-time recovery**: Restore to any point in last 7 days (~15-30 min)
2. **Snapshot restore**: Restore from daily snapshot (~15-30 min)

**RTO**: ~30 minutes
**RPO**: 5 minutes (with continuous backups)

## Notes

1. **Single-AZ**: No automatic failover. ~30 min downtime during maintenance/failure.
2. **Storage Autoscaling**: Automatically scales from 20GB to 100GB as needed.
3. **Performance Insights**: Enabled with 7-day retention (free tier).
4. **Encryption**: Data encrypted at rest with AWS-managed keys.
