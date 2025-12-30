# Secrets Manager Module

Terraform module for AWS Secrets Manager to securely store and manage application secrets.

## Overview

This module creates AWS Secrets Manager secrets with KMS encryption for the Astro application. It replaces hardcoded `.env` files with centralized, encrypted secrets management.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Secrets Manager                               │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ astro/{env}/database-url    ← From RDS module               ││
│  │ astro/{env}/redis-url       ← From ElastiCache module       ││
│  │ astro/{env}/secret-key      ← Auto-generated JWT key        ││
│  │ astro/{env}/oauth/google    ← Optional OAuth credentials    ││
│  │ astro/{env}/oauth/github    ← Optional OAuth credentials    ││
│  │ astro/{env}/oauth/facebook  ← Optional OAuth credentials    ││
│  │ astro/{env}/opencage-api-key                                 ││
│  │ astro/{env}/openai-api-key                                   ││
│  │ astro/{env}/amplitude-api-key                                ││
│  │ astro/{env}/smtp            ← Optional SMTP config          ││
│  └─────────────────────────────────────────────────────────────┘│
│                              │                                   │
│              ┌───────────────┼───────────────┐                   │
│              ▼               ▼               ▼                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   KMS Key    │  │  IAM Policy  │  │ ECS Task Def │           │
│  │ (encryption) │  │ (access)     │  │ (injection)  │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

## Features

- **KMS Encryption** - Customer-managed key with automatic rotation
- **Core Secrets** - Database URL, Redis URL, JWT secret key (always created)
- **OAuth Secrets** - Optional Google, GitHub, Facebook credentials
- **API Keys** - Optional OpenCage, OpenAI, Amplitude keys
- **SMTP Config** - Optional email configuration
- **ECS Integration** - ARNs ready for task definition injection
- **Audit Logging** - CloudTrail logs all secret access

## Usage

### Basic Usage

```hcl
module "secrets" {
  source = "../../modules/secrets"

  environment = "dev"
  aws_region  = "us-east-1"

  # Required: From RDS and ElastiCache modules
  database_url = module.rds.connection_string
  redis_url    = module.elasticache.redis_url

  # Required: ECS roles for KMS policy
  ecs_task_role_arn      = module.ecs.task_role_arn
  ecs_execution_role_arn = module.ecs.execution_role_arn

  # JWT secret key (auto-generated if not provided)
  # jwt_secret_key = "your-custom-secret"
}
```

### With OAuth and API Keys

```hcl
module "secrets" {
  source = "../../modules/secrets"

  environment = "prod"
  aws_region  = "us-east-1"

  database_url           = module.rds.connection_string
  redis_url              = module.elasticache.redis_url
  ecs_task_role_arn      = module.ecs.task_role_arn
  ecs_execution_role_arn = module.ecs.execution_role_arn

  # OAuth credentials
  google_oauth = {
    client_id     = var.google_client_id
    client_secret = var.google_client_secret
  }

  github_oauth = {
    client_id     = var.github_client_id
    client_secret = var.github_client_secret
  }

  # API keys
  opencage_api_key  = var.opencage_api_key
  openai_api_key    = var.openai_api_key
  amplitude_api_key = var.amplitude_api_key

  # SMTP configuration
  smtp_config = {
    host     = "smtp.gmail.com"
    port     = 587
    username = var.smtp_username
    password = var.smtp_password
  }
}
```

## Inputs

| Name | Description | Type | Required |
|------|-------------|------|----------|
| `environment` | Environment name (dev, staging, prod) | `string` | Yes |
| `aws_region` | AWS region | `string` | Yes |
| `database_url` | PostgreSQL connection string | `string` | Yes |
| `redis_url` | Redis connection string | `string` | Yes |
| `ecs_task_role_arn` | ECS task role ARN | `string` | Yes |
| `ecs_execution_role_arn` | ECS execution role ARN | `string` | Yes |
| `jwt_secret_key` | JWT secret (auto-generated if null) | `string` | No |
| `google_oauth` | Google OAuth credentials | `object` | No |
| `github_oauth` | GitHub OAuth credentials | `object` | No |
| `facebook_oauth` | Facebook OAuth credentials | `object` | No |
| `opencage_api_key` | OpenCage API key | `string` | No |
| `openai_api_key` | OpenAI API key | `string` | No |
| `amplitude_api_key` | Amplitude API key | `string` | No |
| `smtp_config` | SMTP configuration | `object` | No |
| `tags` | Additional tags | `map(string)` | No |

## Outputs

| Name | Description |
|------|-------------|
| `kms_key_arn` | KMS key ARN for secrets encryption |
| `database_url_arn` | Database URL secret ARN |
| `redis_url_arn` | Redis URL secret ARN |
| `secret_key_arn` | JWT secret key ARN |
| `oauth_google_arn` | Google OAuth secret ARN (null if not configured) |
| `oauth_github_arn` | GitHub OAuth secret ARN (null if not configured) |
| `oauth_facebook_arn` | Facebook OAuth secret ARN (null if not configured) |
| `opencage_api_key_arn` | OpenCage API key ARN (null if not configured) |
| `openai_api_key_arn` | OpenAI API key ARN (null if not configured) |
| `amplitude_api_key_arn` | Amplitude API key ARN (null if not configured) |
| `smtp_arn` | SMTP secret ARN (null if not configured) |
| `core_secret_arns` | Map of core secret ARNs for ECS |
| `total_secrets_created` | Total number of secrets created |

## ECS Integration

Pass secret ARNs to the ECS module for task definition injection:

```hcl
module "ecs" {
  source = "../../modules/ecs"

  # ... other config ...

  secret_arns = module.secrets.core_secret_arns
  kms_key_arn = module.secrets.kms_key_arn
}
```

In the ECS task definition, secrets are injected as environment variables:

```json
{
  "secrets": [
    {
      "name": "DATABASE_URL",
      "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:astro/dev/database-url-AbCdEf"
    },
    {
      "name": "REDIS_URL",
      "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:astro/dev/redis-url-GhIjKl"
    },
    {
      "name": "SECRET_KEY",
      "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:astro/dev/secret-key-MnOpQr"
    }
  ]
}
```

## Secret Path Structure

All secrets follow the naming pattern: `astro/{environment}/{secret-name}`

```
astro/dev/database-url       → postgresql+asyncpg://...
astro/dev/redis-url          → redis://...
astro/dev/secret-key         → (auto-generated 64-char string)
astro/dev/oauth/google       → {"client_id": "...", "client_secret": "..."}
astro/dev/oauth/github       → {"client_id": "...", "client_secret": "..."}
astro/dev/oauth/facebook     → {"client_id": "...", "client_secret": "..."}
astro/dev/opencage-api-key   → (plain string)
astro/dev/openai-api-key     → (plain string)
astro/dev/amplitude-api-key  → (plain string)
astro/dev/smtp               → {"host": "...", "port": 587, "username": "...", "password": "..."}
```

## Security

- **KMS Encryption** - All secrets encrypted with customer-managed KMS key
- **Key Rotation** - KMS key rotation enabled (automatic yearly rotation)
- **IAM Access Control** - Only ECS roles can decrypt secrets
- **Audit Logging** - CloudTrail logs all secret access
- **No Plaintext in State** - Secrets marked as `sensitive = true`

## Cost Estimation

| Resource | Monthly Cost |
|----------|-------------|
| Secrets Manager (~10 secrets) | ~$4.00 |
| KMS key | ~$1.00 |
| API calls (10k/month) | ~$0.05 |
| **Total** | **~$5/month** |

## Secret Rotation

This module does not implement automatic secret rotation. For production:

1. **Database passwords** - Consider using RDS IAM authentication
2. **JWT keys** - Rotate manually and update the secret
3. **OAuth credentials** - Update in provider console and secret

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 1.5.0 |
| aws | ~> 5.0 |
| random | ~> 3.0 |

## Dependencies

- RDS module (for `connection_string` output)
- ElastiCache module (for `redis_url` output)
- ECS module (for role ARNs and task integration)
