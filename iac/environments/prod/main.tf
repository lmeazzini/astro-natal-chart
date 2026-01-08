# =============================================================================
# Astro Infrastructure - Production Environment
# =============================================================================
# This is the main entry point for the production environment.
# Run bootstrap first to create the S3 bucket and DynamoDB table.
#
# Usage:
#   cd iac/environments/prod
#   terraform init
#   terraform plan
#   terraform apply
# =============================================================================

terraform {
  required_version = ">= 1.5.0"

  # Remote state configuration
  backend "s3" {
    bucket         = "astro-terraform-state-559050210551"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "astro-terraform-locks"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# -----------------------------------------------------------------------------
# Provider Configuration
# -----------------------------------------------------------------------------

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "astro"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# Provider for us-east-1 (required for CloudFront ACM certificates)
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"

  default_tags {
    tags = {
      Project     = "astro"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# -----------------------------------------------------------------------------
# Data Sources
# -----------------------------------------------------------------------------

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

# -----------------------------------------------------------------------------
# Modules
# -----------------------------------------------------------------------------

module "vpc" {
  source = "../../modules/vpc"

  environment                    = var.environment
  vpc_cidr                       = var.vpc_cidr
  availability_zone              = var.availability_zone
  availability_zone_secondary    = var.availability_zone_secondary
  public_subnet_cidr             = var.public_subnet_cidr
  public_subnet_cidr_secondary   = var.public_subnet_cidr_secondary
  private_subnet_cidr            = var.private_subnet_cidr
  database_subnet_cidr           = var.database_subnet_cidr
  database_subnet_cidr_secondary = var.database_subnet_cidr_secondary
  enable_nat_gateway             = var.enable_nat_gateway
}

module "rds" {
  source = "../../modules/rds"

  environment          = var.environment
  instance_class       = var.db_instance_class
  db_subnet_group_name = module.vpc.db_subnet_group_name
  security_group_id    = module.vpc.rds_security_group_id
  availability_zone    = var.availability_zone
}

module "elasticache" {
  source = "../../modules/elasticache"

  environment       = var.environment
  node_type         = var.redis_node_type
  subnet_group_name = module.vpc.elasticache_subnet_group_name
  security_group_id = module.vpc.redis_security_group_id
  availability_zone = var.availability_zone
}

# -----------------------------------------------------------------------------
# ECS and Secrets Modules
# -----------------------------------------------------------------------------
# NOTE: These modules have mutual dependencies that Terraform handles correctly:
#   - ECS module creates IAM roles first
#   - Secrets module uses role ARNs for KMS policy
#   - ECS task definition references secret ARNs
# Terraform's dependency graph resolves this automatically.
# -----------------------------------------------------------------------------

module "ecs" {
  source = "../../modules/ecs"

  environment           = var.environment
  aws_region            = var.aws_region
  vpc_id                = module.vpc.vpc_id
  public_subnet_ids     = module.vpc.public_subnet_ids
  private_subnet_id     = module.vpc.private_subnet_id
  alb_security_group_id = module.vpc.alb_security_group_id
  ecs_security_group_id = module.vpc.ecs_security_group_id
  cpu                   = var.ecs_cpu
  memory                = var.ecs_memory
  desired_count         = var.ecs_desired_count

  # Container image from ECR
  container_image = "${module.ecr.repository_url}:latest"

  # CORS configuration
  allowed_origins = join(",", var.allowed_origins)

  # Qdrant URL (via Cloud Map service discovery)
  qdrant_url = module.qdrant.service_discovery_url

  # Frontend URL for email links
  frontend_url = var.domain_name != null ? "https://${var.domain_name}" : null

  # Stripe publishable key (public, safe for environment variables)
  stripe_publishable_key = var.stripe_publishable_key

  # Secrets Manager integration
  secret_arns = {
    database_url          = module.secrets.database_url_arn
    redis_url             = module.secrets.redis_url_arn
    secret_key            = module.secrets.secret_key_arn
    openai_api_key        = module.secrets.openai_api_key_arn
    stripe_secret_key     = module.secrets.stripe_secret_key_arn
    stripe_webhook_secret = module.secrets.stripe_webhook_secret_arn
    stripe_price_ids      = module.secrets.stripe_price_ids_arn
  }
  kms_key_arn = module.secrets.kms_key_arn

  # S3 integration for PDF storage
  s3_pdf_policy_arn = module.s3.pdf_access_policy_arn

  # ECR integration for container image pulling
  ecr_pull_policy_arn = module.ecr.pull_policy_arn

  # SSL/TLS for ALB (optional - requires DNS module)
  acm_certificate_arn = var.domain_name != null ? module.dns[0].alb_certificate_arn : null

  # Celery configuration for background task processing
  celery_worker_count  = 1    # Number of worker instances
  celery_worker_cpu    = 512  # 0.5 vCPU
  celery_worker_memory = 1024 # 1 GB
  celery_beat_cpu      = 256  # 0.25 vCPU (scheduler is lightweight)
  celery_beat_memory   = 512  # 0.5 GB
}

module "secrets" {
  source = "../../modules/secrets"

  environment = var.environment
  aws_region  = var.aws_region

  # Core secrets (from RDS and ElastiCache modules)
  database_url = module.rds.connection_string
  redis_url    = module.elasticache.redis_url

  # ECS roles for KMS policy
  ecs_task_role_arn      = module.ecs.task_role_arn
  ecs_execution_role_arn = module.ecs.execution_role_arn

  # Stripe secrets (for payment processing)
  stripe_secret_key     = var.stripe_secret_key
  stripe_webhook_secret = var.stripe_webhook_secret
  stripe_price_ids      = var.stripe_price_ids

  # API Keys
  openai_api_key = var.openai_api_key

  # Optional: OAuth and API keys can be added via variables later
  # google_oauth = var.google_oauth
  # github_oauth = var.github_oauth
  # opencage_api_key = var.opencage_api_key
  # amplitude_api_key = var.amplitude_api_key
}

module "s3" {
  source = "../../modules/s3"

  environment = var.environment
  aws_region  = var.aws_region
  kms_key_arn = module.secrets.kms_key_arn

  # CORS origins for presigned URL downloads
  allowed_origins = var.allowed_origins

  # Production settings - protect data
  enable_logs_bucket = true
  enable_versioning  = true
  force_destroy      = false # Prevent accidental deletion in prod
}

# -----------------------------------------------------------------------------
# EFS Module (Persistent Storage for Qdrant)
# -----------------------------------------------------------------------------

module "efs" {
  source = "../../modules/efs"

  environment           = var.environment
  vpc_id                = module.vpc.vpc_id
  private_subnet_id     = module.vpc.private_subnet_id
  efs_security_group_id = module.vpc.efs_security_group_id
  kms_key_arn           = module.secrets.kms_key_arn
  enable_backups        = true
}

# -----------------------------------------------------------------------------
# Qdrant Module (Vector Database for RAG)
# -----------------------------------------------------------------------------

module "qdrant" {
  source = "../../modules/qdrant"

  environment              = var.environment
  aws_region               = var.aws_region
  vpc_id                   = module.vpc.vpc_id
  private_subnet_id        = module.vpc.private_subnet_id
  qdrant_security_group_id = module.vpc.qdrant_security_group_id
  cluster_id               = module.ecs.cluster_id
  cluster_name             = module.ecs.cluster_name
  efs_file_system_id       = module.efs.file_system_id
  efs_access_point_id      = module.efs.access_point_id
  kms_key_arn              = module.secrets.kms_key_arn
  cpu                      = var.qdrant_cpu
  memory                   = var.qdrant_memory
  qdrant_version           = var.qdrant_version
}

module "cloudfront" {
  source = "../../modules/cloudfront"

  environment = var.environment
  aws_region  = var.aws_region
  price_class = var.cloudfront_price_class
  default_ttl = var.cloudfront_default_ttl

  # Production settings - protect data
  force_destroy     = false # Prevent accidental deletion
  enable_versioning = true

  # Custom domain (optional - requires DNS module)
  # Include both www and apex domain for proper SSL coverage
  acm_certificate_arn = var.domain_name != null ? module.dns[0].cloudfront_certificate_arn : null
  domain_aliases      = var.domain_name != null ? [module.dns[0].frontend_fqdn, var.domain_name] : []
}

# -----------------------------------------------------------------------------
# DNS Module (optional - only when domain_name is set)
# -----------------------------------------------------------------------------
# Creates Route53 hosted zone, ACM certificates, and DNS records.
# Set domain_name variable to enable custom domain configuration.
# -----------------------------------------------------------------------------

module "dns" {
  source = "../../modules/dns"
  count  = var.domain_name != null ? 1 : 0

  providers = {
    aws           = aws
    aws.us_east_1 = aws.us_east_1
  }

  environment = var.environment
  aws_region  = var.aws_region
  domain_name = var.domain_name

  # Hosted zone configuration
  create_hosted_zone = var.create_hosted_zone
  frontend_subdomain = var.frontend_subdomain
  api_subdomain      = var.api_subdomain

  # CloudFront integration
  cloudfront_domain_name    = module.cloudfront.distribution_domain_name
  cloudfront_hosted_zone_id = module.cloudfront.distribution_hosted_zone_id

  # ALB integration
  alb_dns_name = module.ecs.alb_dns_name
  alb_zone_id  = module.ecs.alb_zone_id

  # Certificate options
  create_alb_certificate = true
  wait_for_validation    = true
}

# -----------------------------------------------------------------------------
# ECR Module (Container Registry for CI/CD)
# -----------------------------------------------------------------------------
# Private container registry for storing API Docker images.
# Used by GitHub Actions to push images and ECS to pull them.
# -----------------------------------------------------------------------------

module "ecr" {
  source = "../../modules/ecr"

  environment = var.environment
  aws_region  = var.aws_region

  # Repository configuration
  repository_name      = "astro-api"
  image_tag_mutability = "MUTABLE"
  scan_on_push         = true

  # Lifecycle policy (cost optimization)
  max_image_count            = 50 # Keep more images in prod for rollback
  untagged_image_expiry_days = 14

  tags = {
    Project = "astro"
  }
}
