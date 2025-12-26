# =============================================================================
# DNS Module - Route53 Records
# =============================================================================
# A records for frontend and API subdomains using alias targets.
#
# Records:
#   - www.domain.com   → CloudFront distribution
#   - domain.com       → CloudFront (optional, for root redirect)
#   - api.domain.com   → ALB
# =============================================================================

# -----------------------------------------------------------------------------
# Frontend A Record (www → CloudFront)
# -----------------------------------------------------------------------------
# Points www subdomain to CloudFront distribution.
# Uses alias record for better performance and no extra DNS charges.

resource "aws_route53_record" "frontend" {
  zone_id = local.zone_id
  name    = local.frontend_fqdn
  type    = "A"

  alias {
    name                   = var.cloudfront_domain_name
    zone_id                = var.cloudfront_hosted_zone_id
    evaluate_target_health = false
  }
}

# -----------------------------------------------------------------------------
# Root Domain A Record (optional)
# -----------------------------------------------------------------------------
# Points root domain to CloudFront (same as www).
# Useful for users who type domain.com instead of www.domain.com.
# CloudFront can handle redirect or serve the same content.

resource "aws_route53_record" "root" {
  count = var.enable_root_redirect ? 1 : 0

  zone_id = local.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = var.cloudfront_domain_name
    zone_id                = var.cloudfront_hosted_zone_id
    evaluate_target_health = false
  }
}

# -----------------------------------------------------------------------------
# API A Record (api → ALB)
# -----------------------------------------------------------------------------
# Points API subdomain to Application Load Balancer.
# Uses alias record for seamless integration with ALB.

resource "aws_route53_record" "api" {
  zone_id = local.zone_id
  name    = local.api_fqdn
  type    = "A"

  alias {
    name                   = var.alb_dns_name
    zone_id                = var.alb_zone_id
    evaluate_target_health = true # Enable health checking for ALB
  }
}
