# Terraform Bootstrap

This module creates the foundational infrastructure for Terraform remote state management.

## What It Creates

| Resource | Name | Purpose |
|----------|------|---------|
| S3 Bucket | `astro-terraform-state-{account_id}` | Store Terraform state files |
| DynamoDB Table | `astro-terraform-locks` | Prevent concurrent state modifications |

## Prerequisites

- AWS CLI configured with appropriate credentials
- Terraform >= 1.5.0
- IAM permissions for S3 and DynamoDB

## Usage

**This is a one-time setup. Run only once per AWS account.**

```bash
# 1. Navigate to bootstrap directory
cd iac/bootstrap

# 2. Create .env file with AWS credentials
cp ../env.example ../.env
# Edit ../.env with your AWS credentials

# 3. Load environment variables
source ../scripts/init-backend.sh

# 4. Initialize Terraform
terraform init

# 5. Review the plan
terraform plan

# 6. Apply (creates S3 bucket and DynamoDB table)
terraform apply
```

## After Bootstrap

Once complete, you'll see output like:

```
state_bucket_name = "astro-terraform-state-123456789012"
dynamodb_table_name = "astro-terraform-locks"
backend_config = <<EOT
  backend "s3" {
    bucket         = "astro-terraform-state-123456789012"
    key            = "<environment>/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "astro-terraform-locks"
  }
EOT
```

Use the `backend_config` output to configure your environment backends.

## State Management

The bootstrap module uses **local state** (stored in `terraform.tfstate` in this directory). This is intentional - you can't store state in S3 before the bucket exists.

**Important:** Back up `terraform.tfstate` after running bootstrap, or migrate it to S3 manually:

```bash
# Optional: Migrate bootstrap state to S3 after creation
terraform init -migrate-state \
  -backend-config="bucket=astro-terraform-state-YOUR_ACCOUNT_ID" \
  -backend-config="key=bootstrap/terraform.tfstate" \
  -backend-config="region=us-east-1" \
  -backend-config="dynamodb_table=astro-terraform-locks"
```

## Destroying Bootstrap

**WARNING:** Destroying bootstrap will delete all Terraform state for all environments!

Only destroy if you're completely decommissioning the infrastructure:

```bash
# Remove prevent_destroy lifecycle rule first (edit main.tf)
terraform destroy
```
