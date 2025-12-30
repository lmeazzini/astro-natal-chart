# =============================================================================
# DNS Module - ACM Certificates
# =============================================================================
# SSL/TLS certificates for CloudFront and ALB.
#
# Notes:
#   - CloudFront certificate MUST be in us-east-1 (AWS requirement)
#   - ALB certificate is created in the same region as the ALB
#   - DNS validation is automatic via Route53
#   - Wildcard certificate for CloudFront covers all subdomains
# =============================================================================

# -----------------------------------------------------------------------------
# CloudFront Certificate (us-east-1)
# -----------------------------------------------------------------------------
# Wildcard certificate for all frontend subdomains.
# Uses the aws.us_east_1 provider alias passed from the environment.

resource "aws_acm_certificate" "cloudfront" {
  provider = aws.us_east_1

  domain_name = var.domain_name
  subject_alternative_names = [
    "*.${var.domain_name}"
  ]
  validation_method = "DNS"

  tags = merge(local.common_tags, {
    Name    = "${local.name_prefix}-cloudfront-cert"
    Purpose = "CloudFront SSL certificate"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# -----------------------------------------------------------------------------
# ALB Certificate (same region as ALB)
# -----------------------------------------------------------------------------
# Certificate for API subdomain only.

resource "aws_acm_certificate" "alb" {
  count = var.create_alb_certificate ? 1 : 0

  domain_name = local.api_fqdn
  subject_alternative_names = [
    # Add staging API subdomain if in prod environment
    # This allows the same cert to cover staging.api.domain.com
  ]
  validation_method = "DNS"

  tags = merge(local.common_tags, {
    Name    = "${local.name_prefix}-alb-cert"
    Purpose = "ALB HTTPS certificate"
  })

  lifecycle {
    create_before_destroy = true
  }
}

# -----------------------------------------------------------------------------
# DNS Validation Records - CloudFront Certificate
# -----------------------------------------------------------------------------
# Create Route53 records for DNS validation of CloudFront certificate.

resource "aws_route53_record" "cloudfront_validation" {
  for_each = {
    for dvo in aws_acm_certificate.cloudfront.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = local.zone_id
}

# -----------------------------------------------------------------------------
# DNS Validation Records - ALB Certificate
# -----------------------------------------------------------------------------
# Create Route53 records for DNS validation of ALB certificate.

resource "aws_route53_record" "alb_validation" {
  for_each = var.create_alb_certificate ? {
    for dvo in aws_acm_certificate.alb[0].domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  } : {}

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = local.zone_id
}

# -----------------------------------------------------------------------------
# Certificate Validation - CloudFront
# -----------------------------------------------------------------------------
# Wait for CloudFront certificate to be validated.

resource "aws_acm_certificate_validation" "cloudfront" {
  count    = var.wait_for_validation ? 1 : 0
  provider = aws.us_east_1

  certificate_arn         = aws_acm_certificate.cloudfront.arn
  validation_record_fqdns = [for record in aws_route53_record.cloudfront_validation : record.fqdn]

  timeouts {
    create = "30m"
  }
}

# -----------------------------------------------------------------------------
# Certificate Validation - ALB
# -----------------------------------------------------------------------------
# Wait for ALB certificate to be validated.

resource "aws_acm_certificate_validation" "alb" {
  count = var.create_alb_certificate && var.wait_for_validation ? 1 : 0

  certificate_arn         = aws_acm_certificate.alb[0].arn
  validation_record_fqdns = [for record in aws_route53_record.alb_validation : record.fqdn]

  timeouts {
    create = "30m"
  }
}
