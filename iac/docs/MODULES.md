# Module Reference

Quick reference for all Terraform modules in the Astro infrastructure.

## Module Overview

| Module | Purpose | Dependencies | Cost Impact |
|--------|---------|--------------|-------------|
| [bootstrap](#bootstrap) | State storage | None | ~$1/mo |
| [vpc](#vpc) | Networking | None | ~$35/mo (NAT) |
| [rds](#rds) | PostgreSQL database | VPC | ~$13/mo |
| [elasticache](#elasticache) | Redis cache | VPC | ~$12/mo |
| [ecs](#ecs) | Container orchestration | VPC, Secrets, S3, ECR | ~$26/mo |
| [ecr](#ecr) | Container registry | None | ~$1/mo |
| [s3](#s3) | Object storage | None | ~$2/mo |
| [cloudfront](#cloudfront) | CDN for frontend | None | ~$2/mo |
| [secrets](#secrets) | Secrets management | ECS | ~$2/mo |
| [dns](#dns) | DNS and SSL | CloudFront, ECS | ~$1/mo |

## Dependency Graph

```
                    ┌─────────────┐
                    │  bootstrap  │
                    │ (run first) │
                    └─────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌─────────┐  ┌─────────┐  ┌─────────┐
        │   vpc   │  │   ecr   │  │   s3    │
        │ (base)  │  │         │  │         │
        └────┬────┘  └────┬────┘  └────┬────┘
             │            │            │
    ┌────────┼────────┐   │            │
    ▼        ▼        ▼   │            │
┌───────┐┌───────┐┌───────┴───┐        │
│  rds  ││ redis ││    ecs    │◄───────┘
└───────┘└───────┘└─────┬─────┘
                        │
                  ┌─────┴─────┐
                  ▼           ▼
            ┌─────────┐ ┌───────────┐
            │ secrets │ │cloudfront │
            └─────────┘ └─────┬─────┘
                              │
                        ┌─────┴─────┐
                        ▼           ▼
                   ┌─────────┐
                   │   dns   │
                   └─────────┘
```

---

## bootstrap

One-time setup for Terraform state management.

**Location**: `iac/bootstrap/`

**Creates**:
- S3 bucket for Terraform state
- DynamoDB table for state locking

**Usage**:
```hcl
# Run directly, no module call needed
cd bootstrap && terraform apply
```

**Outputs**:
| Name | Description |
|------|-------------|
| `s3_bucket_name` | State bucket name |
| `dynamodb_table_name` | Lock table name |

[Full Documentation](../bootstrap/README.md)

---

## vpc

Virtual Private Cloud with single-AZ, cost-optimized design.

**Location**: `iac/modules/vpc/`

**Creates**:
- VPC (10.0.0.0/16)
- 3 subnets (public, private, database)
- Internet Gateway
- NAT Gateway (single AZ)
- Security groups (ALB, ECS, RDS, Redis)

**Usage**:
```hcl
module "vpc" {
  source = "../../modules/vpc"

  environment        = "dev"
  vpc_cidr           = "10.0.0.0/16"
  availability_zone  = "us-east-1a"
  enable_nat_gateway = true
}
```

**Key Outputs**:
| Name | Description |
|------|-------------|
| `vpc_id` | VPC ID |
| `public_subnet_id` | Public subnet ID |
| `private_subnet_id` | Private subnet ID |
| `database_subnet_id` | Database subnet ID |
| `alb_security_group_id` | ALB security group |
| `ecs_security_group_id` | ECS security group |

[Full Documentation](../modules/vpc/README.md)

---

## rds

PostgreSQL database on RDS.

**Location**: `iac/modules/rds/`

**Creates**:
- RDS PostgreSQL 16 instance
- DB subnet group
- Parameter group
- Automated backups

**Usage**:
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

**Key Outputs**:
| Name | Description |
|------|-------------|
| `endpoint` | Database endpoint |
| `connection_string` | Full connection URL (sensitive) |
| `database_name` | Database name |

[Full Documentation](../modules/rds/README.md)

---

## elasticache

Redis cache cluster on ElastiCache.

**Location**: `iac/modules/elasticache/`

**Creates**:
- ElastiCache Redis 7.1 cluster
- Subnet group
- Parameter group

**Usage**:
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

**Key Outputs**:
| Name | Description |
|------|-------------|
| `endpoint` | Redis endpoint |
| `redis_url` | Full Redis URL |
| `port` | Redis port (6379) |

[Full Documentation](../modules/elasticache/README.md)

---

## ecs

ECS Fargate cluster with Spot instances.

**Location**: `iac/modules/ecs/`

**Creates**:
- ECS cluster with Fargate Spot
- Task definition
- ECS service
- Application Load Balancer
- Target group
- IAM roles (execution, task)
- CloudWatch log group

**Usage**:
```hcl
module "ecs" {
  source = "../../modules/ecs"

  environment           = "dev"
  aws_region            = "us-east-1"
  vpc_id                = module.vpc.vpc_id
  public_subnet_id      = module.vpc.public_subnet_id
  private_subnet_id     = module.vpc.private_subnet_id
  alb_security_group_id = module.vpc.alb_security_group_id
  ecs_security_group_id = module.vpc.ecs_security_group_id
  cpu                   = 256
  memory                = 512
  desired_count         = 1

  secret_arns         = module.secrets.core_secret_arns
  kms_key_arn         = module.secrets.kms_key_arn
  s3_pdf_policy_arn   = module.s3.pdf_access_policy_arn
  ecr_pull_policy_arn = module.ecr.pull_policy_arn
}
```

**Key Outputs**:
| Name | Description |
|------|-------------|
| `cluster_name` | ECS cluster name |
| `service_name` | ECS service name |
| `alb_dns_name` | ALB DNS name |
| `api_url` | Full API URL |
| `task_role_arn` | Task role ARN |
| `execution_role_arn` | Execution role ARN |

[Full Documentation](../modules/ecs/README.md)

---

## ecr

Elastic Container Registry for Docker images.

**Location**: `iac/modules/ecr/`

**Creates**:
- ECR repository
- Lifecycle policy
- IAM policies (push, pull)

**Usage**:
```hcl
module "ecr" {
  source = "../../modules/ecr"

  environment              = "dev"
  repository_name          = "astro-api"
  image_tag_mutability     = "MUTABLE"
  max_image_count          = 30
  untagged_image_expiry_days = 7
}
```

**Key Outputs**:
| Name | Description |
|------|-------------|
| `repository_url` | ECR repository URL |
| `repository_arn` | ECR repository ARN |
| `push_policy_arn` | IAM policy for pushing |
| `pull_policy_arn` | IAM policy for pulling |

[Full Documentation](../modules/ecr/README.md)

---

## s3

S3 buckets for PDFs, backups, and logs.

**Location**: `iac/modules/s3/`

**Creates**:
- PDF storage bucket
- Backups bucket
- Logs bucket (optional)
- Lifecycle policies
- IAM access policies

**Usage**:
```hcl
module "s3" {
  source = "../../modules/s3"

  environment     = "dev"
  kms_key_arn     = module.secrets.kms_key_arn
  allowed_origins = ["http://localhost:5173"]
  force_destroy   = true  # Dev only
}
```

**Key Outputs**:
| Name | Description |
|------|-------------|
| `pdf_bucket_name` | PDF bucket name |
| `pdf_bucket_arn` | PDF bucket ARN |
| `pdf_access_policy_arn` | IAM policy for PDF access |
| `backups_bucket_name` | Backups bucket name |

[Full Documentation](../modules/s3/README.md)

---

## cloudfront

CloudFront CDN with S3 origin for frontend.

**Location**: `iac/modules/cloudfront/`

**Creates**:
- S3 bucket (frontend assets)
- CloudFront distribution
- Origin Access Control
- Cache policy

**Usage**:
```hcl
module "cloudfront" {
  source = "../../modules/cloudfront"

  environment   = "dev"
  price_class   = "PriceClass_100"
  default_ttl   = 3600
  force_destroy = true  # Dev only
}
```

**Key Outputs**:
| Name | Description |
|------|-------------|
| `distribution_id` | CloudFront distribution ID |
| `distribution_domain_name` | CloudFront domain |
| `bucket_name` | Frontend S3 bucket |
| `frontend_url` | Full frontend URL |
| `deploy_command` | CLI command to deploy |
| `invalidate_command` | CLI command to invalidate cache |

[Full Documentation](../modules/cloudfront/README.md)

---

## secrets

AWS Secrets Manager for application secrets.

**Location**: `iac/modules/secrets/`

**Creates**:
- KMS key for encryption
- Secrets (database URL, Redis URL, JWT key)
- IAM policies

**Usage**:
```hcl
module "secrets" {
  source = "../../modules/secrets"

  environment            = "dev"
  database_url           = module.rds.connection_string
  redis_url              = module.elasticache.redis_url
  ecs_task_role_arn      = module.ecs.task_role_arn
  ecs_execution_role_arn = module.ecs.execution_role_arn
}
```

**Key Outputs**:
| Name | Description |
|------|-------------|
| `kms_key_arn` | KMS key ARN |
| `kms_key_alias` | KMS key alias |
| `core_secret_arns` | Map of secret ARNs |

[Full Documentation](../modules/secrets/README.md)

---

## dns

Route53 DNS and ACM certificates.

**Location**: `iac/modules/dns/`

**Creates**:
- Route53 hosted zone (optional)
- ACM certificates (CloudFront, ALB)
- DNS records (A, CNAME)
- Certificate validation records

**Usage**:
```hcl
module "dns" {
  source = "../../modules/dns"

  providers = {
    aws           = aws
    aws.us_east_1 = aws.us_east_1
  }

  environment        = "dev"
  domain_name        = "example.com"
  create_hosted_zone = true
  frontend_subdomain = "app"
  api_subdomain      = "api"

  cloudfront_domain_name    = module.cloudfront.distribution_domain_name
  cloudfront_hosted_zone_id = module.cloudfront.distribution_hosted_zone_id
  alb_dns_name              = module.ecs.alb_dns_name
  alb_zone_id               = module.ecs.alb_zone_id
}
```

**Key Outputs**:
| Name | Description |
|------|-------------|
| `hosted_zone_id` | Route53 zone ID |
| `name_servers` | NS records |
| `frontend_fqdn` | Frontend domain |
| `api_fqdn` | API domain |
| `cloudfront_certificate_arn` | CloudFront cert ARN |
| `alb_certificate_arn` | ALB cert ARN |

[Full Documentation](../modules/dns/README.md)

---

## Best Practices

### Module Versioning

For production, pin module versions:
```hcl
module "vpc" {
  source = "git::https://github.com/org/repo//iac/modules/vpc?ref=v1.0.0"
}
```

### Variable Validation

All modules include input validation:
```hcl
variable "environment" {
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}
```

### Tagging

All resources are tagged consistently:
```hcl
default_tags {
  tags = {
    Project     = "astro"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
```

---

*Last updated: 2025-12-26*
