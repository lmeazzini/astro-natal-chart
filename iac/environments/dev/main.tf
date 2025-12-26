# =============================================================================
# Astro Infrastructure - Development Environment
# =============================================================================
# This is the main entry point for the dev environment.
# Run bootstrap first to create the S3 bucket and DynamoDB table.
#
# Usage:
#   cd iac/environments/dev
#   source ../../scripts/init-backend.sh
#   terraform init
#   terraform plan
#   terraform apply
# =============================================================================

terraform {
  required_version = ">= 1.5.0"

  # Remote state configuration
  backend "s3" {
    bucket         = "astro-terraform-state-559050210551"
    key            = "dev/terraform.tfstate"
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

  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zone  = var.availability_zone
  enable_nat_gateway = var.enable_nat_gateway
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

module "ecs" {
  source = "../../modules/ecs"

  environment           = var.environment
  aws_region            = var.aws_region
  vpc_id                = module.vpc.vpc_id
  public_subnet_id      = module.vpc.public_subnet_id
  private_subnet_id     = module.vpc.private_subnet_id
  alb_security_group_id = module.vpc.alb_security_group_id
  ecs_security_group_id = module.vpc.ecs_security_group_id
  cpu                   = var.ecs_cpu
  memory                = var.ecs_memory
  desired_count         = var.ecs_desired_count
}

module "cloudfront" {
  source = "../../modules/cloudfront"

  environment = var.environment
  aws_region  = var.aws_region
  price_class = "PriceClass_100" # US, Canada, Europe only (cheapest)
  default_ttl = 3600             # 1 hour for dev (faster iteration)

  # Dev settings
  force_destroy     = true # Allow bucket deletion for dev
  enable_versioning = true # Keep for rollback capability
}

# Upcoming modules:
#
# module "secrets" {
#   source = "../../modules/secrets"
#   # ... variables
# }
