# VPC Module

Terraform module for creating a VPC with subnets, security groups, and NAT Gateway.

## Architecture

Single AZ architecture optimized for cost in development/staging environments.

```
┌─────────────────────────────────────────────────────────────────┐
│                        VPC (10.0.0.0/16)                        │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Public Subnet  │  │ Private Subnet  │  │ Database Subnet │ │
│  │  10.0.1.0/24    │  │  10.0.11.0/24   │  │  10.0.21.0/24   │ │
│  │                 │  │                 │  │                 │ │
│  │  - ALB          │  │  - ECS Tasks    │  │  - RDS          │ │
│  │  - NAT Gateway  │  │                 │  │  - Redis        │ │
│  └────────┬────────┘  └────────┬────────┘  └─────────────────┘ │
│           │                    │                                │
│           ▼                    ▼                                │
│     Internet GW           NAT Gateway                           │
│           │                    │                                │
└───────────┼────────────────────┼────────────────────────────────┘
            │                    │
            ▼                    │
        Internet ◄───────────────┘
```

## Security Groups

| Security Group | Inbound | Outbound |
|---------------|---------|----------|
| ALB | HTTP/HTTPS from 0.0.0.0/0 | Port 8000 to ECS |
| ECS | Port 8000 from ALB | RDS, Redis, Internet (443/80) |
| RDS | Port 5432 from ECS | - |
| Redis | Port 6379 from ECS | - |

## Usage

```hcl
module "vpc" {
  source = "../../modules/vpc"

  environment        = "dev"
  vpc_cidr           = "10.0.0.0/16"
  availability_zone  = "us-east-1a"
  enable_nat_gateway = true
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| environment | Environment name (dev, staging, prod) | string | - | yes |
| vpc_cidr | CIDR block for the VPC | string | "10.0.0.0/16" | no |
| availability_zone | Single AZ for all resources | string | "us-east-1a" | no |
| public_subnet_cidr | CIDR for public subnet | string | "10.0.1.0/24" | no |
| private_subnet_cidr | CIDR for private subnet | string | "10.0.11.0/24" | no |
| database_subnet_cidr | CIDR for database subnet | string | "10.0.21.0/24" | no |
| enable_nat_gateway | Enable NAT Gateway (~$32/month) | bool | true | no |
| enable_dns_hostnames | Enable DNS hostnames | bool | true | no |
| enable_dns_support | Enable DNS support | bool | true | no |
| tags | Additional tags | map(string) | {} | no |

## Outputs

| Name | Description |
|------|-------------|
| vpc_id | ID of the VPC |
| vpc_cidr_block | CIDR block of the VPC |
| public_subnet_id | ID of the public subnet |
| private_subnet_id | ID of the private subnet |
| database_subnet_id | ID of the database subnet |
| db_subnet_group_name | Name of the DB subnet group |
| elasticache_subnet_group_name | Name of the ElastiCache subnet group |
| alb_security_group_id | ID of the ALB security group |
| ecs_security_group_id | ID of the ECS security group |
| rds_security_group_id | ID of the RDS security group |
| redis_security_group_id | ID of the Redis security group |
| nat_gateway_id | ID of the NAT Gateway (null if disabled) |
| nat_gateway_public_ip | Public IP of the NAT Gateway |

## Cost Estimation

| Resource | Monthly Cost |
|----------|-------------|
| VPC | Free |
| Internet Gateway | Free |
| NAT Gateway | ~$32 |
| Elastic IP | ~$3.60 (only if NAT disabled) |
| Subnets | Free |
| Route Tables | Free |
| Security Groups | Free |
| **Total** | **~$32-36/month** |

## Notes

1. **Single AZ**: This module uses a single availability zone for cost optimization. For production, consider adding a second AZ for high availability.

2. **NAT Gateway**: Can be disabled with `enable_nat_gateway = false` to save ~$32/month. Note that ECS tasks won't be able to access the internet (pull images, call external APIs) without it.

3. **DB Subnet Group**: RDS requires at least 2 subnets in different AZs for Multi-AZ deployments. Since we're using single AZ, the subnet group has only one subnet.
