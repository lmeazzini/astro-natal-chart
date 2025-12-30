# DNS Module

Terraform module for managing Route53 DNS and ACM SSL certificates for the Astro application.

## Overview

This module creates and manages:

- **Route53 Hosted Zone**: Create new or use existing hosted zone
- **ACM Certificates**: SSL/TLS certificates for CloudFront (us-east-1) and ALB
- **DNS Records**: A records for frontend and API subdomains
- **DNS Validation**: Automatic certificate validation via Route53

## Architecture

```
+---------------------------------------------------------------------+
|                     DNS & SSL Architecture                           |
+---------------------------------------------------------------------+
|                                                                      |
|  Route53 Hosted Zone (astro.example.com)                            |
|  +-- www.astro.example.com  --> CloudFront (A Alias)                |
|  +-- astro.example.com      --> CloudFront (A Alias, optional)      |
|  +-- api.astro.example.com  --> ALB (A Alias)                       |
|                                                                      |
|  ACM Certificates                                                    |
|  +-- CloudFront cert (us-east-1): *.astro.example.com               |
|  +-- ALB cert (same region): api.astro.example.com                  |
|                                                                      |
|  DNS Validation Records (auto-created)                               |
|  +-- _acme-challenge.astro.example.com (CNAME)                      |
|                                                                      |
+---------------------------------------------------------------------+
```

## Features

- **Flexible Zone Management**: Create new hosted zone or reference existing one
- **Wildcard Certificate**: CloudFront certificate covers all subdomains (`*.domain.com`)
- **Multi-Region Support**: CloudFront cert in us-east-1, ALB cert in deployment region
- **Automatic Validation**: DNS validation via Route53 (no manual steps)
- **Optional Root Redirect**: Point root domain to CloudFront (same as www)
- **Health Checking**: ALB records use `evaluate_target_health` for failover

## Usage

```hcl
module "dns" {
  source = "../../modules/dns"

  providers = {
    aws           = aws
    aws.us_east_1 = aws.us_east_1
  }

  environment = "dev"
  domain_name = "astro.example.com"

  # Use existing hosted zone (recommended if domain registered elsewhere)
  create_hosted_zone = false

  # Subdomain configuration
  frontend_subdomain   = "www"
  api_subdomain        = "api"
  enable_root_redirect = true

  # CloudFront integration
  cloudfront_domain_name    = module.cloudfront.distribution_domain_name
  cloudfront_hosted_zone_id = module.cloudfront.distribution_hosted_zone_id

  # ALB integration
  alb_dns_name = module.ecs.alb_dns_name
  alb_zone_id  = module.ecs.alb_zone_id

  # Certificate options
  create_alb_certificate = true
  wait_for_validation    = true

  tags = {
    Project = "astro"
  }
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `environment` | Environment name (dev, staging, prod) | `string` | n/a | yes |
| `aws_region` | AWS region for ALB certificate | `string` | `"us-east-1"` | no |
| `domain_name` | Root domain name (e.g., astro.example.com) | `string` | n/a | yes |
| `create_hosted_zone` | Create new hosted zone (true) or use existing (false) | `bool` | `false` | no |
| `frontend_subdomain` | Subdomain for frontend (e.g., www, app) | `string` | `"www"` | no |
| `api_subdomain` | Subdomain for API | `string` | `"api"` | no |
| `enable_root_redirect` | Point root domain to CloudFront | `bool` | `true` | no |
| `cloudfront_domain_name` | CloudFront distribution domain name | `string` | n/a | yes |
| `cloudfront_hosted_zone_id` | CloudFront distribution hosted zone ID | `string` | `"Z2FDTNDATAQYW2"` | no |
| `alb_dns_name` | ALB DNS name from ECS module | `string` | n/a | yes |
| `alb_zone_id` | ALB hosted zone ID from ECS module | `string` | n/a | yes |
| `create_alb_certificate` | Create ACM certificate for ALB | `bool` | `true` | no |
| `wait_for_validation` | Wait for certificate validation to complete | `bool` | `true` | no |
| `tags` | Additional tags | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| `zone_id` | Route53 hosted zone ID |
| `zone_name` | Route53 hosted zone name |
| `name_servers` | Name servers (only if zone created) |
| `cloudfront_certificate_arn` | ARN of CloudFront ACM certificate |
| `cloudfront_certificate_domain` | Domain of CloudFront certificate |
| `alb_certificate_arn` | ARN of ALB ACM certificate |
| `alb_certificate_domain` | Domain of ALB certificate |
| `frontend_fqdn` | Frontend FQDN (e.g., www.astro.example.com) |
| `api_fqdn` | API FQDN (e.g., api.astro.example.com) |
| `root_fqdn` | Root domain name |

## Integration

### CloudFront Module

Pass the certificate ARN to CloudFront for HTTPS:

```hcl
module "cloudfront" {
  source = "../../modules/cloudfront"

  # Enable custom domain with SSL
  acm_certificate_arn = module.dns.cloudfront_certificate_arn
  domain_aliases      = [module.dns.frontend_fqdn]

  # ... other config ...
}
```

### ECS Module

Pass the certificate ARN to ECS for ALB HTTPS listener:

```hcl
module "ecs" {
  source = "../../modules/ecs"

  # Enable HTTPS on ALB
  acm_certificate_arn = module.dns.alb_certificate_arn

  # ... other config ...
}
```

### Using Existing Hosted Zone

If your domain is registered with a different registrar (e.g., GoDaddy, Namecheap):

1. Set `create_hosted_zone = false`
2. Create the hosted zone manually in AWS Route53
3. Copy the NS records to your registrar
4. Wait for DNS propagation (up to 48 hours)

## Certificate Validation

ACM certificates require DNS validation. This module:

1. Creates validation CNAME records in Route53
2. Waits for validation to complete (if `wait_for_validation = true`)
3. Timeout is 30 minutes per certificate

**Note**: If validation times out, check:
- NS records are correctly delegated to Route53
- TTL has expired on any cached DNS lookups
- Domain ownership is correct

## Cost Estimation

| Resource | Monthly Cost |
|----------|-------------|
| Route53 Hosted Zone | $0.50 |
| DNS Queries (1M) | $0.40 |
| ACM Certificates | Free |
| **Total** | **~$1/month** |

## Security

- **HTTPS Everywhere**: Certificates enable HTTPS for both frontend and API
- **Wildcard Certificate**: CloudFront cert covers all current and future subdomains
- **Automatic Renewal**: ACM certificates auto-renew before expiration
- **DNS Validation**: No email validation required (more secure)

## Troubleshooting

### Certificate Stuck in "Pending Validation"

1. Verify Route53 is authoritative for the domain:
   ```bash
   dig NS astro.example.com
   ```
2. Check validation records exist:
   ```bash
   dig CNAME _acme-challenge.astro.example.com
   ```
3. Wait for DNS propagation (can take up to 48 hours for new domains)

### CloudFront Returns 403

1. Ensure certificate is validated (status: ISSUED)
2. Verify certificate ARN is passed to CloudFront module
3. Check domain aliases include the FQDN

### ALB Returns 502/503

1. Verify ECS tasks are healthy
2. Check security group allows traffic on port 443
3. Ensure HTTPS listener has valid certificate
