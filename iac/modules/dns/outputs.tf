# =============================================================================
# DNS Module - Outputs
# =============================================================================
# Exports zone information, certificate ARNs, and FQDNs for other modules.
# =============================================================================

# -----------------------------------------------------------------------------
# Route53 Hosted Zone
# -----------------------------------------------------------------------------

output "zone_id" {
  description = "Route53 hosted zone ID"
  value       = local.zone_id
}

output "zone_name" {
  description = "Route53 hosted zone name"
  value       = var.domain_name
}

output "name_servers" {
  description = "Name servers for the hosted zone (only if created)"
  value       = var.create_hosted_zone ? aws_route53_zone.main[0].name_servers : null
}

# -----------------------------------------------------------------------------
# ACM Certificates
# -----------------------------------------------------------------------------

output "cloudfront_certificate_arn" {
  description = "ARN of the CloudFront ACM certificate (us-east-1)"
  value       = aws_acm_certificate.cloudfront.arn
}

output "cloudfront_certificate_domain" {
  description = "Domain name of the CloudFront certificate"
  value       = aws_acm_certificate.cloudfront.domain_name
}

output "alb_certificate_arn" {
  description = "ARN of the ALB ACM certificate (same region)"
  value       = var.create_alb_certificate ? aws_acm_certificate.alb[0].arn : null
}

output "alb_certificate_domain" {
  description = "Domain name of the ALB certificate"
  value       = var.create_alb_certificate ? aws_acm_certificate.alb[0].domain_name : null
}

# -----------------------------------------------------------------------------
# Fully Qualified Domain Names
# -----------------------------------------------------------------------------

output "frontend_fqdn" {
  description = "Fully qualified domain name for frontend (e.g., www.astro.example.com)"
  value       = local.frontend_fqdn
}

output "api_fqdn" {
  description = "Fully qualified domain name for API (e.g., api.astro.example.com)"
  value       = local.api_fqdn
}

output "root_fqdn" {
  description = "Root domain name (e.g., astro.example.com)"
  value       = var.domain_name
}

# -----------------------------------------------------------------------------
# DNS Records
# -----------------------------------------------------------------------------

output "frontend_record_name" {
  description = "DNS record name for frontend"
  value       = aws_route53_record.frontend.name
}

output "api_record_name" {
  description = "DNS record name for API"
  value       = aws_route53_record.api.name
}

output "root_record_name" {
  description = "DNS record name for root domain (null if disabled)"
  value       = var.enable_root_redirect ? aws_route53_record.root[0].name : null
}

# -----------------------------------------------------------------------------
# Certificate Validation Status
# -----------------------------------------------------------------------------

output "cloudfront_certificate_status" {
  description = "Status of CloudFront certificate validation"
  value       = aws_acm_certificate.cloudfront.status
}

output "alb_certificate_status" {
  description = "Status of ALB certificate validation (null if not created)"
  value       = var.create_alb_certificate ? aws_acm_certificate.alb[0].status : null
}
