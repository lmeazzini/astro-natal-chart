# Secrets Management

Guide for managing application secrets using AWS Secrets Manager in the Astro infrastructure.

## Overview

The Astro infrastructure uses AWS Secrets Manager with KMS encryption for secure secret storage. Secrets are injected into ECS tasks as environment variables at runtime.

```mermaid
graph LR
    subgraph Secrets Module
        KMS[KMS Key]
        SM[Secrets Manager]
    end

    subgraph ECS
        Task[ECS Task]
    end

    SM -->|Encrypted with| KMS
    Task -->|Reads secrets at startup| SM
    KMS -->|Decrypt| Task
```

## Secrets Inventory

### Core Secrets (Always Created)

| Secret Path | Description | Source |
|-------------|-------------|--------|
| `astro/{env}/database-url` | PostgreSQL connection string | RDS module output |
| `astro/{env}/redis-url` | Redis connection URL | ElastiCache module output |
| `astro/{env}/secret-key` | JWT signing key (64 chars) | Auto-generated or provided |

### OAuth Secrets (Conditional)

| Secret Path | Description | Required For |
|-------------|-------------|--------------|
| `astro/{env}/oauth/google` | Google OAuth credentials | Google Sign-In |
| `astro/{env}/oauth/github` | GitHub OAuth credentials | GitHub Sign-In |
| `astro/{env}/oauth/facebook` | Facebook OAuth credentials | Facebook Sign-In |

### API Key Secrets (Conditional)

| Secret Path | Description | Required For |
|-------------|-------------|--------------|
| `astro/{env}/opencage-api-key` | OpenCage geocoding API | Location search |
| `astro/{env}/openai-api-key` | OpenAI API key | AI interpretations |
| `astro/{env}/amplitude-api-key` | Amplitude analytics | Event tracking |

### SMTP Configuration (Conditional)

| Secret Path | Description | Required For |
|-------------|-------------|--------------|
| `astro/{env}/smtp` | SMTP server configuration | Email sending |

---

## Secret Structure

### Simple Secrets (String)

```json
"postgresql+asyncpg://user:pass@host:5432/dbname"
```

### Complex Secrets (JSON)

OAuth credentials:
```json
{
  "client_id": "your-client-id",
  "client_secret": "your-client-secret"
}
```

SMTP configuration:
```json
{
  "host": "smtp.gmail.com",
  "port": 587,
  "username": "your-email@gmail.com",
  "password": "your-app-password"
}
```

---

## Adding New Secrets

### Via Terraform (Recommended)

#### Step 1: Add Variable

In `modules/secrets/variables.tf`:

```hcl
variable "my_new_api_key" {
  description = "API key for MyService"
  type        = string
  default     = null
  sensitive   = true
}
```

#### Step 2: Create Secret Resource

In `modules/secrets/main.tf`:

```hcl
resource "aws_secretsmanager_secret" "my_new_api" {
  count = var.my_new_api_key != null ? 1 : 0

  name                    = "astro/${var.environment}/my-new-api-key"
  description             = "MyService API key"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = 7

  tags = merge(local.common_tags, {
    Name = "astro/${var.environment}/my-new-api-key"
  })
}

resource "aws_secretsmanager_secret_version" "my_new_api" {
  count = var.my_new_api_key != null ? 1 : 0

  secret_id     = aws_secretsmanager_secret.my_new_api[0].id
  secret_string = var.my_new_api_key
}
```

#### Step 3: Add Output

In `modules/secrets/outputs.tf`:

```hcl
output "my_new_api_secret_arn" {
  description = "MyService API key secret ARN"
  value       = try(aws_secretsmanager_secret.my_new_api[0].arn, null)
}
```

#### Step 4: Pass to Environment

In `environments/dev/main.tf`:

```hcl
module "secrets" {
  source = "../../modules/secrets"

  # ... existing config ...
  my_new_api_key = var.my_new_api_key
}
```

#### Step 5: Apply

```bash
terraform apply -var="my_new_api_key=your-key-here"
```

### Via AWS CLI (Quick Updates)

```bash
# Create new secret
aws secretsmanager create-secret \
  --name "astro/dev/my-new-secret" \
  --secret-string "secret-value" \
  --kms-key-id alias/astro-dev-secrets

# Update existing secret
aws secretsmanager put-secret-value \
  --secret-id "astro/dev/my-new-secret" \
  --secret-string "new-value"
```

---

## Rotating Secrets

### JWT Secret Key Rotation

1. **Generate new key**:
```bash
openssl rand -base64 64 | tr -d '\n'
```

2. **Update secret**:
```bash
aws secretsmanager put-secret-value \
  --secret-id astro/dev/secret-key \
  --secret-string "new-64-char-key-here"
```

3. **Restart ECS tasks** (picks up new secret):
```bash
aws ecs update-service \
  --cluster astro-dev-cluster \
  --service astro-dev-api \
  --force-new-deployment
```

### Database Password Rotation

1. **Change password in RDS**:
```bash
aws rds modify-db-instance \
  --db-instance-identifier astro-dev-db \
  --master-user-password "new-password"
```

2. **Update connection string**:
```bash
# Build new connection string
NEW_URL="postgresql+asyncpg://postgres:new-password@endpoint:5432/astro"

aws secretsmanager put-secret-value \
  --secret-id astro/dev/database-url \
  --secret-string "$NEW_URL"
```

3. **Restart ECS tasks**:
```bash
aws ecs update-service \
  --cluster astro-dev-cluster \
  --service astro-dev-api \
  --force-new-deployment
```

### OAuth Credentials Rotation

```bash
aws secretsmanager put-secret-value \
  --secret-id astro/dev/oauth/google \
  --secret-string '{"client_id":"new-id","client_secret":"new-secret"}'
```

---

## Access Control

### ECS Access to Secrets

The ECS execution role has permission to read secrets:

```hcl
# In ECS module
resource "aws_iam_role_policy" "ecs_execution_secrets" {
  policy = jsonencode({
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = ["arn:aws:secretsmanager:*:*:secret:astro/${var.environment}/*"]
    }]
  })
}
```

### KMS Key Policy

Only authorized roles can decrypt secrets:

```hcl
resource "aws_kms_key" "secrets" {
  policy = jsonencode({
    Statement = [
      {
        Sid    = "AllowECSExecutionRole"
        Effect = "Allow"
        Principal = { AWS = var.ecs_execution_role_arn }
        Action    = ["kms:Decrypt", "kms:DescribeKey"]
        Resource  = "*"
      }
    ]
  })
}
```

---

## ECS Integration

### Task Definition Secrets

Secrets are injected as environment variables:

```hcl
container_definitions = jsonencode([{
  name = "api"
  secrets = [
    {
      name      = "DATABASE_URL"
      valueFrom = "arn:aws:secretsmanager:us-east-1:123456:secret:astro/dev/database-url"
    },
    {
      name      = "REDIS_URL"
      valueFrom = "arn:aws:secretsmanager:us-east-1:123456:secret:astro/dev/redis-url"
    },
    {
      name      = "SECRET_KEY"
      valueFrom = "arn:aws:secretsmanager:us-east-1:123456:secret:astro/dev/secret-key"
    }
  ]
}])
```

### Reading JSON Secrets

For JSON secrets, use `::key` suffix:

```hcl
secrets = [
  {
    name      = "GOOGLE_CLIENT_ID"
    valueFrom = "arn:aws:secretsmanager:...:astro/dev/oauth/google::client_id"
  },
  {
    name      = "GOOGLE_CLIENT_SECRET"
    valueFrom = "arn:aws:secretsmanager:...:astro/dev/oauth/google::client_secret"
  }
]
```

---

## Viewing Secrets

### Via AWS Console

1. Go to AWS Secrets Manager
2. Find secret by name (e.g., `astro/dev/database-url`)
3. Click "Retrieve secret value"

### Via AWS CLI

```bash
# Get secret value
aws secretsmanager get-secret-value \
  --secret-id astro/dev/database-url \
  --query SecretString \
  --output text

# List all secrets
aws secretsmanager list-secrets \
  --filter Key=name,Values=astro/dev
```

### Via Terraform

```bash
cd iac/environments/dev
terraform output -json | jq '.secret_arns'
```

---

## Deleting Secrets

### Soft Delete (Default)

Secrets have a 7-day recovery window:

```bash
aws secretsmanager delete-secret \
  --secret-id astro/dev/my-secret
# Recoverable for 7 days
```

### Immediate Delete

```bash
aws secretsmanager delete-secret \
  --secret-id astro/dev/my-secret \
  --force-delete-without-recovery
# Cannot be recovered!
```

### Recover Deleted Secret

```bash
aws secretsmanager restore-secret \
  --secret-id astro/dev/my-secret
```

---

## Security Best Practices

### 1. Never Commit Secrets

```bash
# .gitignore should include:
*.tfvars
.env
```

### 2. Use Terraform Variables for Secrets

```bash
# Pass via environment variable
export TF_VAR_google_oauth_secret="secret-value"
terraform apply

# Or use tfvars file (gitignored)
# terraform.tfvars
google_oauth = {
  client_id     = "your-id"
  client_secret = "your-secret"
}
```

### 3. Limit Access

- Use IAM policies to restrict who can read secrets
- Enable CloudTrail logging for secret access
- Use separate secrets per environment

### 4. Enable Rotation

For production, consider automatic rotation:

```hcl
resource "aws_secretsmanager_secret_rotation" "rds" {
  secret_id           = aws_secretsmanager_secret.database_url.id
  rotation_lambda_arn = aws_lambda_function.rotation.arn

  rotation_rules {
    automatically_after_days = 30
  }
}
```

### 5. Monitor Access

Enable CloudWatch alarms for unusual secret access patterns.

---

## Troubleshooting

### "Access Denied" Errors

1. **Check IAM role**:
```bash
aws sts get-caller-identity
```

2. **Verify KMS permissions**:
```bash
aws kms describe-key --key-id alias/astro-dev-secrets
```

3. **Check secret policy**:
```bash
aws secretsmanager get-resource-policy --secret-id astro/dev/database-url
```

### "Secret Not Found"

1. **Verify secret exists**:
```bash
aws secretsmanager describe-secret --secret-id astro/dev/database-url
```

2. **Check region**:
```bash
aws secretsmanager list-secrets --region us-east-1
```

### ECS Task Fails to Start

1. **Check ECS events**:
```bash
aws ecs describe-services \
  --cluster astro-dev-cluster \
  --services astro-dev-api \
  --query 'services[0].events[:5]'
```

2. **Verify execution role**:
```bash
aws iam get-role --role-name astro-dev-ecs-execution-role
```

---

*Last updated: 2025-12-26*
