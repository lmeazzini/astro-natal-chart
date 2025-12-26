# S3 Module

Terraform module for managing S3 buckets used by the Astro application.

## Overview

This module creates and manages S3 buckets for:

- **PDFs**: Birth chart PDF reports and user avatars
- **Backups**: PostgreSQL and Qdrant database backups
- **Logs**: Application logs (optional)

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        S3 Buckets                                │
├──────────────────────────────────────────────────────────────────┤
│ astro-{env}-pdfs-{account}                                       │
│   └── {user_id}/{chart_id}/{filename}.pdf                        │
│   └── avatars/{user_id}/{filename}                               │
│   Lifecycle: 90d → Standard-IA, 365d → Glacier                   │
├──────────────────────────────────────────────────────────────────┤
│ astro-{env}-backups-{account}                                    │
│   └── {YYYYMMDD}/astro_backup_{timestamp}.sql.gz                 │
│   └── monthly/{filename}                                         │
│   └── qdrant/{snapshot_name}.tar.gz                              │
│   Lifecycle: 7d → Glacier, 30d expire (daily), 365d (monthly)    │
├──────────────────────────────────────────────────────────────────┤
│ astro-{env}-logs-{account} (optional)                            │
│   └── cloudwatch/, alb/, etc.                                    │
│   Lifecycle: 90d expire                                          │
└──────────────────────────────────────────────────────────────────┘
```

## Features

- **KMS Encryption**: Server-side encryption using the secrets module KMS key
- **Versioning**: Enabled by default for data protection (PDFs and backups)
- **Public Access Blocked**: All buckets have public access completely blocked
- **SSL-Only Access**: Bucket policies deny non-HTTPS requests (enabled by default)
- **CORS**: Configured for presigned URL downloads from frontend
- **Lifecycle Policies**: Automatic tiering to reduce storage costs
- **IAM Policies**: Least-privilege policies for ECS and backup scripts

## Usage

```hcl
module "s3" {
  source = "../../modules/s3"

  environment = "dev"
  aws_region  = "us-east-1"
  kms_key_arn = module.secrets.kms_key_arn

  # CORS origins for presigned URL downloads
  allowed_origins = ["http://localhost:5173", "http://localhost:8000"]

  # Optional: Enable logs bucket
  enable_logs_bucket = false

  # Lifecycle configuration
  pdf_transition_to_ia_days      = 90
  pdf_transition_to_glacier_days = 365
  backup_transition_to_glacier_days = 7
  backup_expiration_days         = 30

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
| `kms_key_arn` | KMS key ARN for encryption | `string` | n/a | yes |
| `allowed_origins` | CORS allowed origins | `list(string)` | `["*"]` | no |
| `enable_logs_bucket` | Create logs bucket | `bool` | `false` | no |
| `enable_versioning` | Enable bucket versioning | `bool` | `true` | no |
| `enable_ssl_only` | Require HTTPS for bucket access | `bool` | `true` | no |
| `force_destroy` | Allow bucket deletion with contents | `bool` | `false` | no |
| `prevent_destroy` | Prevent accidental bucket deletion | `bool` | `false` | no |
| `pdf_transition_to_ia_days` | Days before PDF → Standard-IA | `number` | `90` | no |
| `pdf_transition_to_glacier_days` | Days before PDF → Glacier | `number` | `365` | no |
| `pdf_noncurrent_expiration_days` | Days before noncurrent PDF versions expire | `number` | `30` | no |
| `backup_transition_to_glacier_days` | Days before backup → Glacier | `number` | `7` | no |
| `backup_expiration_days` | Days before daily backups expire | `number` | `30` | no |
| `monthly_backup_expiration_days` | Days before monthly backups expire | `number` | `365` | no |
| `monthly_backup_transition_to_glacier_days` | Days before monthly backups → Glacier | `number` | `30` | no |
| `logs_expiration_days` | Days before logs expire | `number` | `90` | no |
| `tags` | Additional tags | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| `pdfs_bucket_name` | Name of the PDF storage bucket |
| `pdfs_bucket_arn` | ARN of the PDF storage bucket |
| `pdfs_bucket_domain_name` | Domain name for CloudFront |
| `backups_bucket_name` | Name of the backups bucket |
| `backups_bucket_arn` | ARN of the backups bucket |
| `logs_bucket_name` | Name of the logs bucket (null if disabled) |
| `logs_bucket_arn` | ARN of the logs bucket (null if disabled) |
| `pdf_access_policy_arn` | IAM policy ARN for PDF access |
| `backup_access_policy_arn` | IAM policy ARN for backup access |
| `logs_access_policy_arn` | IAM policy ARN for logs access |
| `all_bucket_arns` | List of all bucket ARNs |
| `all_policy_arns` | List of all IAM policy ARNs |

## Integration

### ECS Task Role

Attach the PDF access policy to the ECS task role:

```hcl
resource "aws_iam_role_policy_attachment" "ecs_task_s3" {
  role       = aws_iam_role.ecs_task.name
  policy_arn = module.s3.pdf_access_policy_arn
}
```

### Backup Script

The backup access policy should be attached to the IAM user/role running backup scripts:

```hcl
resource "aws_iam_user_policy_attachment" "backup_s3" {
  user       = aws_iam_user.backup.name
  policy_arn = module.s3.backup_access_policy_arn
}
```

### Application Configuration

Update the application environment variables:

```bash
S3_BUCKET_NAME=astro-dev-pdfs-123456789012
S3_PREFIX=birth-charts
```

## Cost Estimation

| Resource | Dev (1 GB PDFs, 5 GB Backups) |
|----------|------------------------------|
| PDFs (Standard) | ~$0.03/month |
| Backups (Glacier) | ~$0.02/month |
| Requests | ~$0.05/month |
| **Total** | **~$0.10/month** |

Storage costs decrease significantly with lifecycle policies:
- Standard-IA: 54% cheaper than Standard
- Glacier: 85% cheaper than Standard

## Security

- All buckets have public access completely blocked
- **SSL-only access enforced** via bucket policy (denies HTTP requests)
- Server-side encryption with KMS (customer-managed key)
- Presigned URLs for secure, temporary access (1-hour expiration)
- IAM policies follow least-privilege principle (includes `kms:DescribeKey`)
- Versioning protects against accidental deletion
- Lifecycle `prevent_destroy` available for production environments

### Production Recommendations

For production environments, set these values:

```hcl
module "s3" {
  # ... other config ...

  # Security
  enable_ssl_only = true    # Default: true
  force_destroy   = false   # Default: false (don't allow deletion with objects)

  # NOTE: For prevent_destroy, manually set lifecycle.prevent_destroy = true
  # in the bucket resources for production environments.
}
```
