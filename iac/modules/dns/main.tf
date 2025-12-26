# =============================================================================
# DNS Module - Main Resources
# =============================================================================
# Route53 hosted zone configuration for custom domain management.
#
# Features:
#   - Create new or use existing hosted zone
#   - ACM certificates for CloudFront (us-east-1) and ALB
#   - Automatic DNS validation
#   - A records for frontend and API
# =============================================================================

# -----------------------------------------------------------------------------
# Terraform Configuration
# -----------------------------------------------------------------------------

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source                = "hashicorp/aws"
      version               = "~> 5.0"
      configuration_aliases = [aws.us_east_1]
    }
  }
}

# -----------------------------------------------------------------------------
# Local Variables
# -----------------------------------------------------------------------------

locals {
  name_prefix = "astro-${var.environment}"

  # Determine zone ID based on whether we create or reference existing
  zone_id = var.create_hosted_zone ? aws_route53_zone.main[0].zone_id : data.aws_route53_zone.main[0].zone_id

  # Fully qualified domain names
  frontend_fqdn = "${var.frontend_subdomain}.${var.domain_name}"
  api_fqdn      = "${var.api_subdomain}.${var.domain_name}"

  common_tags = merge(var.tags, {
    Module = "dns"
  })
}

# -----------------------------------------------------------------------------
# Route53 Hosted Zone
# -----------------------------------------------------------------------------
# Either create a new hosted zone or reference an existing one.
# Use create_hosted_zone = false if domain is registered elsewhere.

# Data source for existing hosted zone
data "aws_route53_zone" "main" {
  count = var.create_hosted_zone ? 0 : 1

  name         = var.domain_name
  private_zone = false
}

# Resource for new hosted zone
resource "aws_route53_zone" "main" {
  count = var.create_hosted_zone ? 1 : 0

  name    = var.domain_name
  comment = "Hosted zone for ${local.name_prefix} - managed by Terraform"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-zone"
  })

  # Prevent accidental deletion in production
  lifecycle {
    prevent_destroy = false # Set to true for production
  }
}
