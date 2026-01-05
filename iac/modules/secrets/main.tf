# =============================================================================
# Secrets Module - Main Resources
# =============================================================================
# AWS Secrets Manager for secure application secrets storage.
#
# Features:
#   - KMS encryption with key rotation
#   - Core secrets (database, redis, JWT)
#   - Optional OAuth and API key secrets
#   - ECS integration ready
# =============================================================================

# -----------------------------------------------------------------------------
# Terraform Configuration
# -----------------------------------------------------------------------------

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

# -----------------------------------------------------------------------------
# Local Variables
# -----------------------------------------------------------------------------

locals {
  name_prefix = "astro-${var.environment}"

  common_tags = merge(var.tags, {
    Module = "secrets"
  })
}

# -----------------------------------------------------------------------------
# Data Sources
# -----------------------------------------------------------------------------

data "aws_caller_identity" "current" {}

# -----------------------------------------------------------------------------
# KMS Key for Secrets Encryption
# -----------------------------------------------------------------------------

resource "aws_kms_key" "secrets" {
  description             = "KMS key for Astro ${var.environment} secrets encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  # Prevent accidental destruction in production
  lifecycle {
    prevent_destroy = false # Set to true for production via variable
  }

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "EnableIAMUserPermissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "AllowECSExecutionRole"
        Effect = "Allow"
        Principal = {
          AWS = var.ecs_execution_role_arn
        }
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = "*"
      },
      {
        Sid    = "AllowECSTaskRole"
        Effect = "Allow"
        Principal = {
          AWS = var.ecs_task_role_arn
        }
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = "*"
      },
      {
        Sid    = "AllowCloudWatchLogs"
        Effect = "Allow"
        Principal = {
          Service = "logs.${var.aws_region}.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
        Condition = {
          ArnLike = {
            "kms:EncryptionContext:aws:logs:arn" = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*"
          }
        }
      }
    ]
  })

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-secrets-key"
  })
}

resource "aws_kms_alias" "secrets" {
  name          = "alias/${local.name_prefix}-secrets"
  target_key_id = aws_kms_key.secrets.key_id
}

# -----------------------------------------------------------------------------
# JWT Secret Key (Auto-generate if not provided)
# -----------------------------------------------------------------------------

resource "random_password" "jwt_secret" {
  count   = var.jwt_secret_key == null ? 1 : 0
  length  = 64
  special = true
}

# -----------------------------------------------------------------------------
# Core Secrets (Always Created)
# -----------------------------------------------------------------------------

# Database URL
resource "aws_secretsmanager_secret" "database_url" {
  name                    = "astro/${var.environment}/database-url"
  description             = "PostgreSQL connection string for FastAPI"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = 7

  tags = merge(local.common_tags, {
    Name = "astro/${var.environment}/database-url"
  })
}

resource "aws_secretsmanager_secret_version" "database_url" {
  secret_id     = aws_secretsmanager_secret.database_url.id
  secret_string = var.database_url
}

# Redis URL
resource "aws_secretsmanager_secret" "redis_url" {
  name                    = "astro/${var.environment}/redis-url"
  description             = "Redis connection string"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = 7

  tags = merge(local.common_tags, {
    Name = "astro/${var.environment}/redis-url"
  })
}

resource "aws_secretsmanager_secret_version" "redis_url" {
  secret_id     = aws_secretsmanager_secret.redis_url.id
  secret_string = var.redis_url
}

# JWT Secret Key
resource "aws_secretsmanager_secret" "secret_key" {
  name                    = "astro/${var.environment}/secret-key"
  description             = "JWT signing secret key"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = 7

  tags = merge(local.common_tags, {
    Name = "astro/${var.environment}/secret-key"
  })
}

resource "aws_secretsmanager_secret_version" "secret_key" {
  secret_id = aws_secretsmanager_secret.secret_key.id
  secret_string = coalesce(
    var.jwt_secret_key,
    try(random_password.jwt_secret[0].result, null)
  )
}

# -----------------------------------------------------------------------------
# OAuth Secrets (Conditional)
# -----------------------------------------------------------------------------

# Google OAuth
resource "aws_secretsmanager_secret" "oauth_google" {
  count = var.google_oauth != null ? 1 : 0

  name                    = "astro/${var.environment}/oauth/google"
  description             = "Google OAuth2 credentials"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = 7

  tags = merge(local.common_tags, {
    Name = "astro/${var.environment}/oauth/google"
  })
}

resource "aws_secretsmanager_secret_version" "oauth_google" {
  count = var.google_oauth != null ? 1 : 0

  secret_id = aws_secretsmanager_secret.oauth_google[0].id
  secret_string = jsonencode({
    client_id     = var.google_oauth.client_id
    client_secret = var.google_oauth.client_secret
  })
}

# GitHub OAuth
resource "aws_secretsmanager_secret" "oauth_github" {
  count = var.github_oauth != null ? 1 : 0

  name                    = "astro/${var.environment}/oauth/github"
  description             = "GitHub OAuth credentials"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = 7

  tags = merge(local.common_tags, {
    Name = "astro/${var.environment}/oauth/github"
  })
}

resource "aws_secretsmanager_secret_version" "oauth_github" {
  count = var.github_oauth != null ? 1 : 0

  secret_id = aws_secretsmanager_secret.oauth_github[0].id
  secret_string = jsonencode({
    client_id     = var.github_oauth.client_id
    client_secret = var.github_oauth.client_secret
  })
}

# Facebook OAuth
resource "aws_secretsmanager_secret" "oauth_facebook" {
  count = var.facebook_oauth != null ? 1 : 0

  name                    = "astro/${var.environment}/oauth/facebook"
  description             = "Facebook OAuth credentials"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = 7

  tags = merge(local.common_tags, {
    Name = "astro/${var.environment}/oauth/facebook"
  })
}

resource "aws_secretsmanager_secret_version" "oauth_facebook" {
  count = var.facebook_oauth != null ? 1 : 0

  secret_id = aws_secretsmanager_secret.oauth_facebook[0].id
  secret_string = jsonencode({
    client_id     = var.facebook_oauth.client_id
    client_secret = var.facebook_oauth.client_secret
  })
}

# -----------------------------------------------------------------------------
# API Key Secrets (Conditional)
# -----------------------------------------------------------------------------

# OpenCage API Key
resource "aws_secretsmanager_secret" "opencage" {
  count = var.opencage_api_key != null ? 1 : 0

  name                    = "astro/${var.environment}/opencage-api-key"
  description             = "OpenCage geocoding API key"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = 7

  tags = merge(local.common_tags, {
    Name = "astro/${var.environment}/opencage-api-key"
  })
}

resource "aws_secretsmanager_secret_version" "opencage" {
  count = var.opencage_api_key != null ? 1 : 0

  secret_id     = aws_secretsmanager_secret.opencage[0].id
  secret_string = var.opencage_api_key
}

# OpenAI API Key
resource "aws_secretsmanager_secret" "openai" {
  count = var.openai_api_key != null ? 1 : 0

  name                    = "astro/${var.environment}/openai-api-key"
  description             = "OpenAI API key for AI interpretations"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = 7

  tags = merge(local.common_tags, {
    Name = "astro/${var.environment}/openai-api-key"
  })
}

resource "aws_secretsmanager_secret_version" "openai" {
  count = var.openai_api_key != null ? 1 : 0

  secret_id     = aws_secretsmanager_secret.openai[0].id
  secret_string = var.openai_api_key
}

# Amplitude API Key
resource "aws_secretsmanager_secret" "amplitude" {
  count = var.amplitude_api_key != null ? 1 : 0

  name                    = "astro/${var.environment}/amplitude-api-key"
  description             = "Amplitude analytics API key"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = 7

  tags = merge(local.common_tags, {
    Name = "astro/${var.environment}/amplitude-api-key"
  })
}

resource "aws_secretsmanager_secret_version" "amplitude" {
  count = var.amplitude_api_key != null ? 1 : 0

  secret_id     = aws_secretsmanager_secret.amplitude[0].id
  secret_string = var.amplitude_api_key
}

# -----------------------------------------------------------------------------
# SMTP Configuration (Conditional)
# -----------------------------------------------------------------------------

resource "aws_secretsmanager_secret" "smtp" {
  count = var.smtp_config != null ? 1 : 0

  name                    = "astro/${var.environment}/smtp"
  description             = "SMTP email configuration"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = 7

  tags = merge(local.common_tags, {
    Name = "astro/${var.environment}/smtp"
  })
}

resource "aws_secretsmanager_secret_version" "smtp" {
  count = var.smtp_config != null ? 1 : 0

  secret_id = aws_secretsmanager_secret.smtp[0].id
  secret_string = jsonencode({
    host     = var.smtp_config.host
    port     = var.smtp_config.port
    username = var.smtp_config.username
    password = var.smtp_config.password
  })
}

# -----------------------------------------------------------------------------
# Stripe Secrets (Conditional)
# -----------------------------------------------------------------------------

# Stripe Secret Key (for backend API calls)
resource "aws_secretsmanager_secret" "stripe_secret_key" {
  count = var.stripe_secret_key != null ? 1 : 0

  name                    = "astro/${var.environment}/stripe-secret-key"
  description             = "Stripe Secret API Key for payment processing"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = 7

  tags = merge(local.common_tags, {
    Name = "astro/${var.environment}/stripe-secret-key"
  })
}

resource "aws_secretsmanager_secret_version" "stripe_secret_key" {
  count = var.stripe_secret_key != null ? 1 : 0

  secret_id     = aws_secretsmanager_secret.stripe_secret_key[0].id
  secret_string = var.stripe_secret_key
}

# Stripe Webhook Secret (for verifying webhook signatures)
resource "aws_secretsmanager_secret" "stripe_webhook_secret" {
  count = var.stripe_webhook_secret != null ? 1 : 0

  name                    = "astro/${var.environment}/stripe-webhook-secret"
  description             = "Stripe Webhook Signing Secret"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = 7

  tags = merge(local.common_tags, {
    Name = "astro/${var.environment}/stripe-webhook-secret"
  })
}

resource "aws_secretsmanager_secret_version" "stripe_webhook_secret" {
  count = var.stripe_webhook_secret != null ? 1 : 0

  secret_id     = aws_secretsmanager_secret.stripe_webhook_secret[0].id
  secret_string = var.stripe_webhook_secret
}

# Stripe Price IDs (for subscription plans)
resource "aws_secretsmanager_secret" "stripe_price_ids" {
  count = var.stripe_price_ids != null ? 1 : 0

  name                    = "astro/${var.environment}/stripe-price-ids"
  description             = "Stripe Price IDs for subscription plans"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = 7

  tags = merge(local.common_tags, {
    Name = "astro/${var.environment}/stripe-price-ids"
  })
}

resource "aws_secretsmanager_secret_version" "stripe_price_ids" {
  count = var.stripe_price_ids != null ? 1 : 0

  secret_id = aws_secretsmanager_secret.stripe_price_ids[0].id
  secret_string = jsonencode({
    starter   = var.stripe_price_ids.starter
    pro       = var.stripe_price_ids.pro
    unlimited = var.stripe_price_ids.unlimited
  })
}
