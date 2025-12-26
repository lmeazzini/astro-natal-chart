# ECR Module

Terraform module for managing AWS Elastic Container Registry for the Astro application.

## Overview

This module creates and manages:

- **ECR Repository**: Private container registry for API Docker images
- **Lifecycle Policy**: Automatic cleanup of old/untagged images
- **IAM Policies**: Push (CI/CD) and Pull (ECS) access policies
- **Image Scanning**: Vulnerability scanning on push

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     ECR Repository                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Repository: astro-api-{env}                                    │
│  ├── Image scanning on push (vulnerability detection)           │
│  ├── AES256 encryption at rest                                  │
│  └── Lifecycle policy (auto-cleanup)                            │
│                                                                  │
│  Lifecycle Rules:                                                │
│  1. Expire untagged images after 7 days                         │
│  2. Keep only last 30 tagged images                             │
│                                                                  │
│  IAM Policies:                                                   │
│  ├── ecr-push: For GitHub Actions CI/CD                         │
│  └── ecr-pull: For ECS task execution                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Usage

```hcl
module "ecr" {
  source = "../../modules/ecr"

  environment = "dev"
  aws_region  = "us-east-1"

  # Repository configuration
  repository_name      = "astro-api"
  image_tag_mutability = "MUTABLE"
  scan_on_push         = true

  # Lifecycle policy
  max_image_count            = 30
  untagged_image_expiry_days = 7

  tags = {
    Project = "astro"
  }
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `environment` | Environment name (dev, staging, prod) | `string` | n/a | yes |
| `aws_region` | AWS region | `string` | `"us-east-1"` | no |
| `repository_name` | Name of the ECR repository | `string` | `"astro-api"` | no |
| `image_tag_mutability` | MUTABLE or IMMUTABLE | `string` | `"MUTABLE"` | no |
| `scan_on_push` | Enable image scanning | `bool` | `true` | no |
| `max_image_count` | Max images to retain | `number` | `30` | no |
| `untagged_image_expiry_days` | Days before untagged images expire | `number` | `7` | no |
| `tags` | Additional tags | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| `repository_url` | Full URL for docker push/pull |
| `repository_arn` | ARN of the ECR repository |
| `repository_name` | Name of the ECR repository |
| `registry_id` | Registry ID (AWS account ID) |
| `push_policy_arn` | IAM policy ARN for pushing images |
| `pull_policy_arn` | IAM policy ARN for pulling images |
| `docker_login_command` | AWS CLI command to login to ECR |
| `docker_push_command` | Example docker push command |

## Integration

### GitHub Actions CI/CD

1. Attach `push_policy_arn` to the IAM user/role used by GitHub Actions
2. Use the `docker_login_command` output to authenticate
3. Build and push images using `repository_url`

```yaml
# In GitHub Actions workflow
- name: Login to Amazon ECR
  run: |
    aws ecr get-login-password --region us-east-1 | \
      docker login --username AWS --password-stdin \
      123456789012.dkr.ecr.us-east-1.amazonaws.com

- name: Build and push
  run: |
    docker build -t astro-api:${{ github.sha }} apps/api/
    docker tag astro-api:${{ github.sha }} \
      123456789012.dkr.ecr.us-east-1.amazonaws.com/astro-api-dev:${{ github.sha }}
    docker push \
      123456789012.dkr.ecr.us-east-1.amazonaws.com/astro-api-dev:${{ github.sha }}
```

### ECS Task Definition

The ECS execution role needs `pull_policy_arn` to pull images:

```hcl
resource "aws_iam_role_policy_attachment" "ecs_ecr" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = module.ecr.pull_policy_arn
}
```

## Lifecycle Policy

The module automatically manages image retention:

1. **Untagged images**: Deleted after 7 days (configurable)
2. **Tagged images**: Only the most recent 30 are kept (configurable)

This prevents storage costs from growing unbounded.

## Security

- **Private repository**: No public access
- **Encryption at rest**: AES256 (AWS managed key)
- **Image scanning**: Vulnerabilities detected on push
- **Least privilege**: Separate push/pull IAM policies

## Cost Estimation

| Resource | Monthly Cost |
|----------|-------------|
| Storage (first 500MB) | Free |
| Storage (next 49.5GB) | $0.10/GB |
| Data transfer (out) | $0.09/GB after 1GB |
| **Typical usage (5GB)** | **~$0.50/month** |

## Troubleshooting

### Authentication Failed

```bash
# Refresh ECR login (expires after 12 hours)
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789012.dkr.ecr.us-east-1.amazonaws.com
```

### Image Not Found

Ensure the image tag exists:
```bash
aws ecr describe-images \
  --repository-name astro-api-dev \
  --image-ids imageTag=latest
```

### Permission Denied

Verify IAM permissions:
```bash
aws ecr get-authorization-token
```
