# Getting Started

Step-by-step guide to deploy the Astro infrastructure from scratch.

## Prerequisites

### Required Tools

| Tool | Version | Installation |
|------|---------|--------------|
| Terraform | >= 1.5.0 | [terraform.io/downloads](https://terraform.io/downloads) |
| AWS CLI | >= 2.0 | [aws.amazon.com/cli](https://aws.amazon.com/cli/) |
| Git | Any | [git-scm.com](https://git-scm.com/) |

### Verify Installation

```bash
# Check Terraform
terraform version
# Expected: Terraform v1.5.0 or higher

# Check AWS CLI
aws --version
# Expected: aws-cli/2.x.x

# Check Git
git --version
```

### AWS Account Setup

1. **Create IAM User** with programmatic access
2. **Attach Policies** (or use AdministratorAccess for dev):
   - AmazonVPCFullAccess
   - AmazonRDSFullAccess
   - AmazonElastiCacheFullAccess
   - AmazonECS_FullAccess
   - AmazonS3FullAccess
   - CloudFrontFullAccess
   - AmazonRoute53FullAccess
   - SecretsManagerReadWrite
   - IAMFullAccess

3. **Get Credentials**:
   - Access Key ID
   - Secret Access Key

## Step 1: Clone Repository

```bash
git clone https://github.com/your-org/astro-iac.git
cd astro-iac/iac
```

## Step 2: Configure AWS Credentials

```bash
# Copy the example file
cp .env.example .env

# Edit with your credentials
nano .env
```

**`.env` contents:**
```bash
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_DEFAULT_REGION="us-east-1"
```

**Load credentials:**
```bash
source scripts/init-backend.sh
```

## Step 3: Bootstrap (One-Time Setup)

The bootstrap creates:
- S3 bucket for Terraform state
- DynamoDB table for state locking

```bash
cd bootstrap

# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Apply (creates S3 bucket + DynamoDB)
terraform apply
```

**Expected output:**
```
Outputs:

dynamodb_table_name = "astro-terraform-locks"
s3_bucket_name = "astro-terraform-state-123456789012"
```

**Note the S3 bucket name** - you'll need it for the next step.

## Step 4: Deploy Dev Environment

```bash
cd ../environments/dev

# Update backend bucket name in main.tf if different from default
# Look for: bucket = "astro-terraform-state-ACCOUNT_ID"

# Initialize with backend
terraform init

# Preview changes (this will take 1-2 minutes)
terraform plan

# Deploy infrastructure (10-15 minutes)
terraform apply
```

**Expected resources created:**
- VPC with 3 subnets
- RDS PostgreSQL instance
- ElastiCache Redis cluster
- ECS cluster and service
- ALB with target group
- S3 buckets (frontend, PDFs, backups)
- CloudFront distribution
- Secrets Manager secrets
- IAM roles and policies

## Step 5: Verify Deployment

```bash
# Get outputs
terraform output

# Test API endpoint
curl $(terraform output -raw api_url)/health

# Expected: {"status": "healthy"}
```

### Key Outputs

| Output | Description |
|--------|-------------|
| `api_url` | Backend API URL (ALB) |
| `frontend_url` | Frontend URL (CloudFront) |
| `rds_endpoint` | Database endpoint |
| `redis_endpoint` | Redis endpoint |

## Step 6: Configure Application Secrets

The infrastructure creates placeholder secrets. Update them:

```bash
# Get secret ARN
terraform output -json | jq '.secret_arns'

# Update secrets via AWS Console or CLI
aws secretsmanager put-secret-value \
  --secret-id astro/dev/database-url \
  --secret-string "postgresql+asyncpg://user:pass@host:5432/db"
```

## Common Issues

### "No valid credential sources found"

```bash
# Reload credentials
source scripts/init-backend.sh

# Verify
aws sts get-caller-identity
```

### "Backend configuration changed"

```bash
terraform init -reconfigure
```

### "Error creating resource: already exists"

```bash
# Import existing resource
terraform import aws_s3_bucket.example bucket-name

# Or destroy and recreate (DEV ONLY)
terraform destroy -target=aws_s3_bucket.example
terraform apply
```

### "Timeout waiting for service to stabilize"

ECS tasks may fail to start. Check:
```bash
# View ECS service events
aws ecs describe-services \
  --cluster astro-dev-cluster \
  --services astro-dev-api \
  --query 'services[0].events[:5]'

# View task logs
aws logs tail /ecs/astro-dev-api --follow
```

## Next Steps

1. **Deploy Application**: Push Docker image to ECR
2. **Configure DNS**: Set up custom domain (optional)
3. **Set Up CI/CD**: Configure GitHub Actions
4. **Review Security**: Check IAM policies and security groups

## Cleanup

To destroy all resources:

```bash
cd environments/dev

# Destroy environment (10-15 minutes)
terraform destroy

# Destroy bootstrap (optional)
cd ../bootstrap
terraform destroy
```

**Warning**: This permanently deletes all data including databases and S3 objects.

---

*Last updated: 2025-12-26*
