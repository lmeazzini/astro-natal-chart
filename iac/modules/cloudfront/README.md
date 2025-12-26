# CloudFront + S3 Module

Terraform module for hosting React SPA frontend using S3 + CloudFront CDN.

## Overview

This module creates a globally distributed static site hosting infrastructure optimized for React single-page applications (SPAs).

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Internet                                 │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────┐
│                  CloudFront Distribution                         │
│   - 400+ edge locations worldwide                                │
│   - HTTPS with TLS 1.2+ (default or ACM certificate)             │
│   - Brotli + Gzip compression                                    │
│   - SPA routing (404/403 → index.html)                           │
└─────────────────────────────────┬───────────────────────────────┘
                                  │ (OAC - Origin Access Control)
┌─────────────────────────────────▼───────────────────────────────┐
│                    S3 Bucket (Origin)                            │
│   - Private access (CloudFront only via OAC)                     │
│   - Versioning enabled (rollback capability)                     │
│   - AES256 server-side encryption                                │
│   - Static files: HTML, JS, CSS, assets                          │
└─────────────────────────────────────────────────────────────────┘
```

## Features

- **Global CDN** - 400+ edge locations for low-latency worldwide
- **Origin Access Control (OAC)** - Modern, secure S3 access (replaces OAI)
- **SPA Routing** - Automatic 404/403 → index.html for React Router
- **Compression** - Brotli and Gzip for smaller payloads
- **HTTPS** - TLS 1.2+ with CloudFront default or custom ACM certificate
- **Versioning** - S3 versioning for deployment rollback
- **Private S3** - Bucket completely private, only accessible via CloudFront

## Usage

### Basic Usage (Dev)

```hcl
module "cloudfront" {
  source = "../../modules/cloudfront"

  environment = "dev"
  aws_region  = "us-east-1"
  price_class = "PriceClass_100"  # US, Canada, Europe only
  default_ttl = 3600              # 1 hour for dev

  # Allow bucket deletion for dev
  force_destroy = true
}
```

### Production with Custom Domain

```hcl
module "cloudfront" {
  source = "../../modules/cloudfront"

  environment         = "prod"
  aws_region          = "us-east-1"
  price_class         = "PriceClass_All"        # Global distribution
  default_ttl         = 86400                   # 1 day cache
  domain_aliases      = ["app.astro.com"]
  acm_certificate_arn = aws_acm_certificate.frontend.arn

  # Production settings
  force_destroy     = false
  enable_versioning = true
}
```

## Inputs

| Name | Description | Type | Default |
|------|-------------|------|---------|
| `environment` | Environment name (dev, staging, prod) | `string` | - |
| `aws_region` | AWS region for S3 bucket | `string` | `us-east-1` |
| `domain_aliases` | Custom domain names (requires ACM cert) | `list(string)` | `[]` |
| `acm_certificate_arn` | ACM certificate ARN (must be in us-east-1) | `string` | `null` |
| `price_class` | CloudFront price class | `string` | `PriceClass_100` |
| `default_ttl` | Default cache TTL in seconds | `number` | `86400` |
| `min_ttl` | Minimum cache TTL in seconds | `number` | `0` |
| `max_ttl` | Maximum cache TTL in seconds | `number` | `31536000` |
| `enable_waf` | Enable WAF protection | `bool` | `false` |
| `waf_web_acl_arn` | WAF Web ACL ARN | `string` | `null` |
| `enable_access_logs` | Enable CloudFront access logging | `bool` | `false` |
| `access_logs_bucket` | S3 bucket for access logs | `string` | `null` |
| `access_logs_prefix` | Prefix for log files | `string` | `cloudfront-logs/` |
| `force_destroy` | Allow bucket deletion when not empty | `bool` | `false` |
| `enable_versioning` | Enable S3 versioning | `bool` | `true` |
| `tags` | Additional tags | `map(string)` | `{}` |

### Price Classes

| Price Class | Coverage | Cost |
|-------------|----------|------|
| `PriceClass_100` | US, Canada, Europe | Lowest |
| `PriceClass_200` | + Asia, Africa, Middle East | Medium |
| `PriceClass_All` | All 400+ edge locations | Highest |

## Outputs

| Name | Description |
|------|-------------|
| `bucket_name` | S3 bucket name for frontend files |
| `bucket_arn` | S3 bucket ARN |
| `bucket_regional_domain_name` | S3 regional domain name |
| `distribution_id` | CloudFront distribution ID (for invalidation) |
| `distribution_arn` | CloudFront distribution ARN |
| `distribution_domain_name` | CloudFront domain (*.cloudfront.net) |
| `distribution_hosted_zone_id` | Hosted zone ID for Route53 alias |
| `frontend_url` | Full HTTPS URL to frontend |
| `custom_domain_url` | Custom domain URL (if configured) |
| `deploy_command` | AWS CLI command to deploy files |
| `invalidate_command` | AWS CLI command to invalidate cache |

## Deployment

### Manual Deployment

```bash
# Build the React app
cd apps/web
npm run build

# Deploy to S3
aws s3 sync ./dist s3://astro-dev-frontend-ACCOUNT_ID --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id DISTRIBUTION_ID \
  --paths "/*"
```

### CI/CD Deployment (GitHub Actions Example)

```yaml
deploy:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Build
      run: npm run build

    - name: Deploy to S3
      run: aws s3 sync ./dist s3://${{ secrets.S3_BUCKET }} --delete

    - name: Invalidate CloudFront
      run: |
        aws cloudfront create-invalidation \
          --distribution-id ${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }} \
          --paths "/*"
```

## Cost Estimation

| Resource | Monthly Cost (dev) |
|----------|-------------------|
| S3 storage (1 GB) | ~$0.02 |
| S3 requests (100k) | ~$0.04 |
| CloudFront (10 GB transfer) | ~$0.85 |
| **Total** | **~$1/month** |

**Notes:**
- First 1 TB CloudFront transfer/month is free (12-month free tier)
- First 1,000 cache invalidations/month are free
- Additional invalidations: $0.005 per path

## SPA Routing

React Router uses client-side routing. When a user navigates directly to `/charts/123`:

1. CloudFront requests `/charts/123` from S3
2. S3 returns 404 (file doesn't exist)
3. Custom error response converts 404 → 200 with `/index.html`
4. React Router handles the route on the client

This ensures deep links work correctly.

## Security

- **Private S3 bucket** - No public access, CloudFront OAC only
- **OAC (Origin Access Control)** - Modern, secure S3 access with SigV4 signing
- **HTTPS enforced** - All HTTP requests redirected to HTTPS
- **TLS 1.2+** - Modern protocol versions only
- **Server-side encryption** - AES256 encryption at rest

## Future Enhancements

- [ ] Custom domain with Route53 (issue #247)
- [ ] ACM certificate provisioning
- [ ] WAF Web ACL for DDoS protection
- [ ] Real-time logs to Kinesis
- [ ] Lambda@Edge for advanced routing

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 1.5.0 |
| aws | ~> 5.0 |

## Dependencies

- ACM certificate in us-east-1 (optional, for custom domain)
- Route53 hosted zone (optional, for custom domain - issue #247)
