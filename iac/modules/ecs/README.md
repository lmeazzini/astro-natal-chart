# ECS Fargate Module

Terraform module for AWS ECS Fargate with Spot instances.

## Overview

This module creates an ECS Fargate cluster optimized for cost using **Fargate Spot** instances, which provide up to **70% cost savings** compared to on-demand pricing.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Internet                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│              Application Load Balancer (Public)                  │
│                    Port 80 (HTTP)                                │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                    ECS Cluster (Fargate SPOT)                    │
│  ┌─────────────────┐  ┌─────────────────┐                       │
│  │  Task 1 (SPOT)  │  │  Task 2 (SPOT)  │  ← 70% cheaper        │
│  │  FastAPI:8000   │  │  FastAPI:8000   │                       │
│  └─────────────────┘  └─────────────────┘                       │
│                    (Private Subnet)                              │
└─────────────────────────────────────────────────────────────────┘
```

## Features

- **Fargate Spot** - 70% cost savings vs on-demand
- **Container Insights** - Monitoring enabled
- **CloudWatch Logs** - Centralized logging
- **ECS Exec** - Interactive debugging
- **Deployment Circuit Breaker** - Auto-rollback on failures
- **2-minute Stop Timeout** - Graceful Spot interruption handling

## Usage

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

  cpu           = 256   # 0.25 vCPU
  memory        = 512   # 512 MB
  desired_count = 1
}
```

## Inputs

| Name | Description | Type | Default |
|------|-------------|------|---------|
| `environment` | Environment name (dev, staging, prod) | `string` | - |
| `aws_region` | AWS region | `string` | `us-east-1` |
| `vpc_id` | VPC ID | `string` | - |
| `public_subnet_id` | Public subnet for ALB | `string` | - |
| `private_subnet_id` | Private subnet for ECS tasks | `string` | - |
| `alb_security_group_id` | Security group for ALB | `string` | - |
| `ecs_security_group_id` | Security group for ECS tasks | `string` | - |
| `cpu` | CPU units (256 = 0.25 vCPU) | `number` | `256` |
| `memory` | Memory in MB | `number` | `512` |
| `desired_count` | Number of tasks | `number` | `1` |
| `container_image` | Container image | `string` | `nginx:alpine` |
| `container_port` | Container port | `number` | `8000` |
| `health_check_path` | Health check path | `string` | `/health` |

## Outputs

| Name | Description |
|------|-------------|
| `cluster_arn` | ARN of the ECS cluster |
| `cluster_name` | Name of the ECS cluster |
| `service_name` | Name of the ECS service |
| `alb_dns_name` | DNS name of the ALB |
| `alb_arn` | ARN of the ALB |
| `target_group_arn` | ARN of the target group |
| `execution_role_arn` | ARN of the execution role |
| `task_role_arn` | ARN of the task role |
| `api_url` | URL to access the API |

## Cost Estimation

| Configuration | On-Demand | Spot (70% off) |
|--------------|-----------|----------------|
| 0.25 vCPU / 512MB (1 task) | ~$9/mo | ~$3/mo |
| 0.5 vCPU / 1GB (1 task) | ~$18/mo | ~$6/mo |
| ALB | ~$16/mo | ~$16/mo |

**Total for dev (1 task + ALB):** ~$19/month

## Spot Interruption Handling

When AWS needs Spot capacity back:

1. **2-minute warning** sent via task metadata
2. **ECS drains connections** from target group
3. **SIGTERM sent** to container with 120s timeout
4. **Graceful shutdown** completes in-flight requests
5. **New Spot task** launches automatically

### Application Requirements

- Handle SIGTERM signal gracefully
- Complete in-flight requests within 120 seconds
- Use connection draining on ALB

FastAPI with Uvicorn handles this automatically.

## Debugging with ECS Exec

```bash
# List running tasks
aws ecs list-tasks --cluster astro-dev-cluster

# Execute command in container
aws ecs execute-command \
  --cluster astro-dev-cluster \
  --task <task-id> \
  --container api \
  --interactive \
  --command "/bin/sh"
```

## Future Enhancements

- [ ] HTTPS listener (requires ACM certificate - issue #247)
- [ ] Secrets Manager integration (issue #245)
- [ ] Auto-scaling based on CPU/Memory
- [ ] ECR repository integration

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 1.5.0 |
| aws | ~> 5.0 |

## Dependencies

- VPC module (issue #240)
- Secrets Manager module (issue #245) - optional
- ACM certificate (issue #247) - optional for HTTPS
