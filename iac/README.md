# Astro Infrastructure as Code

Terraform configurations for deploying the Astro natal chart application to AWS.

## Documentation

| Document | Description |
|----------|-------------|
| [Getting Started](./docs/GETTING_STARTED.md) | Step-by-step deployment guide |
| [Architecture](./docs/ARCHITECTURE.md) | System architecture and diagrams |
| [Modules](./docs/MODULES.md) | Terraform module reference |
| [Environments](./docs/ENVIRONMENTS.md) | Environment configuration guide |
| [Secrets](./docs/SECRETS.md) | Secrets management |
| [Deployment](./docs/DEPLOYMENT.md) | Deployment procedures |
| [Disaster Recovery](./docs/DISASTER_RECOVERY.md) | DR runbooks and procedures |
| [Cost Optimization](./docs/COST_OPTIMIZATION.md) | Cost analysis and optimization |
| [Troubleshooting](./docs/TROUBLESHOOTING.md) | Common issues and solutions |
| [Monitoring](./docs/MONITORING.md) | CloudWatch metrics and alarms |

## Quick Start

```bash
# 1. Setup credentials
cp .env.example .env
# Edit .env with your AWS credentials

# 2. Bootstrap (one-time)
cd bootstrap
source ../scripts/init-backend.sh
terraform init
terraform apply

# 3. Deploy to dev
cd ../environments/dev
# Update backend bucket name in main.tf with output from bootstrap
source ../../scripts/init-backend.sh
terraform init
terraform plan
terraform apply
```

## Structure

```
iac/
├── bootstrap/           # One-time setup (S3 + DynamoDB for state)
├── modules/             # Reusable Terraform modules
│   ├── vpc/             # (Issue #240)
│   ├── rds/             # (Issue #241)
│   ├── elasticache/     # (Issue #242)
│   ├── ecs/             # (Issue #243)
│   ├── cloudfront/      # (Issue #244)
│   ├── secrets/         # (Issue #245)
│   ├── s3/              # (Issue #246)
│   └── dns/             # (Issue #247)
├── environments/
│   └── dev/             # Development environment
├── scripts/
│   └── init-backend.sh  # Load AWS credentials
├── .env.example         # AWS credentials template
└── README.md            # This file
```

## Prerequisites

- **Terraform** >= 1.5.0
- **AWS CLI** (optional, for debugging)
- **AWS Account** with IAM credentials

### Required IAM Permissions

The IAM user/role needs permissions for:
- S3 (state bucket)
- DynamoDB (state locking)
- VPC, EC2 (networking)
- RDS (database)
- ElastiCache (Redis)
- ECS, ECR (containers)
- CloudFront, ACM (CDN, SSL)
- Route53 (DNS)
- Secrets Manager (secrets)
- IAM (roles and policies)

## Environments

| Environment | Branch | Purpose |
|-------------|--------|---------|
| dev | feature/* | Development and testing |
| staging | dev | Pre-production (future) |
| prod | main | Production (future) |

## Architecture Overview

```
                    Internet
                        │
        ┌───────────────┴───────────────┐
        │                               │
   CloudFront                          ALB
   (Frontend)                      (Backend API)
        │                               │
        ▼                               ▼
    S3 Bucket                     ECS Fargate
   (React SPA)                    (FastAPI)
                                        │
                          ┌─────────────┼─────────────┐
                          │             │             │
                        RDS          Redis      Secrets
                    (PostgreSQL)  (ElastiCache)  Manager
```

### Cost Optimization (Single AZ, Spot)

| Component | Specification | Est. Cost/Month |
|-----------|--------------|-----------------|
| ECS Fargate (Spot) | 0.25 vCPU, 512MB × 2 | ~$6 |
| RDS PostgreSQL | db.t3.micro, 20GB | ~$13 |
| ElastiCache Redis | cache.t3.micro | ~$12 |
| NAT Gateway | Single AZ | ~$35 |
| ALB | 1 load balancer | ~$20 |
| CloudFront + S3 | Frontend | ~$2 |
| Other | Secrets, Route53, Logs | ~$10 |
| **Total (Dev)** | | **~$98/month** |

## Related Issues

- #239 - Terraform base setup (this)
- #240 - VPC module (single AZ)
- #241 - RDS PostgreSQL module
- #242 - ElastiCache Redis module
- #243 - ECS Fargate module (Spot)
- #244 - S3 + CloudFront module
- #245 - Secrets Manager module
- #246 - S3 buckets module (PDFs, backups)
- #247 - Route53 + ACM module
- #248 - CI/CD pipeline
- #249 - IaC documentation

## Troubleshooting

See [Troubleshooting Guide](./docs/TROUBLESHOOTING.md) for comprehensive solutions.

### Common Issues

| Error | Solution |
|-------|----------|
| No valid credential sources | `source scripts/init-backend.sh` |
| Backend configuration changed | `terraform init -reconfigure` |
| Resource already exists | `terraform import resource_type.name id` |
| State lock held | `terraform force-unlock LOCK_ID` |

---

*Last updated: 2025-12-26*
