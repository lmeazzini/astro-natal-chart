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

# Upcoming modules:
#
# module "rds" {
#   source = "../../modules/rds"
#   # ... variables
# }
#
# module "elasticache" {
#   source = "../../modules/elasticache"
#   # ... variables
# }
#
# module "ecs" {
#   source = "../../modules/ecs"
#   # ... variables
# }
