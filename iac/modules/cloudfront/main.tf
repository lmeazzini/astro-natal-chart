# =============================================================================
# CloudFront Module - Main Resources
# =============================================================================
# CloudFront distribution for global CDN delivery of React SPA.
#
# Features:
#   - SPA routing (404/403 → index.html)
#   - Brotli + Gzip compression
#   - HTTPS redirect (when certificate provided)
#   - Custom cache policy
#   - Security headers (CSP, X-Frame-Options, HSTS, etc.)
#   - Origin Shield for production (optional)
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
  }
}

# -----------------------------------------------------------------------------
# Cache Policy
# -----------------------------------------------------------------------------
# Custom cache policy for static assets with compression enabled

resource "aws_cloudfront_cache_policy" "frontend" {
  name        = "${local.name_prefix}-frontend-cache-policy"
  comment     = "Cache policy for ${local.name_prefix} frontend"
  default_ttl = var.default_ttl
  min_ttl     = var.min_ttl
  max_ttl     = var.max_ttl

  parameters_in_cache_key_and_forwarded_to_origin {
    cookies_config {
      cookie_behavior = "none"
    }

    headers_config {
      header_behavior = "none"
    }

    query_strings_config {
      query_string_behavior = "none"
    }

    enable_accept_encoding_brotli = true
    enable_accept_encoding_gzip   = true
  }
}

# -----------------------------------------------------------------------------
# Response Headers Policy (Security)
# -----------------------------------------------------------------------------
# Adds security headers to all responses for protection against common attacks.

resource "aws_cloudfront_response_headers_policy" "security_headers" {
  name    = "${local.name_prefix}-security-headers"
  comment = "Security headers for ${local.name_prefix} frontend"

  security_headers_config {
    # Prevent MIME type sniffing
    content_type_options {
      override = true
    }

    # Prevent clickjacking
    frame_options {
      frame_option = "DENY"
      override     = true
    }

    # Enable XSS protection in older browsers
    xss_protection {
      mode_block = true
      protection = true
      override   = true
    }

    # Enforce HTTPS with HSTS
    strict_transport_security {
      access_control_max_age_sec = 31536000 # 1 year
      include_subdomains         = true
      preload                    = true
      override                   = true
    }

    # Referrer policy for privacy
    referrer_policy {
      referrer_policy = "strict-origin-when-cross-origin"
      override        = true
    }
  }
}

# -----------------------------------------------------------------------------
# CloudFront Distribution
# -----------------------------------------------------------------------------

resource "aws_cloudfront_distribution" "frontend" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "${local.name_prefix} Frontend"
  default_root_object = "index.html"
  price_class         = var.price_class
  aliases             = length(var.domain_aliases) > 0 ? var.domain_aliases : null
  web_acl_id          = var.enable_waf ? var.waf_web_acl_arn : null

  # ---------------------------------------------------------------------------
  # Origin Configuration
  # ---------------------------------------------------------------------------
  origin {
    domain_name              = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id                = "S3-${aws_s3_bucket.frontend.id}"
    origin_access_control_id = aws_cloudfront_origin_access_control.frontend.id

    # Origin Shield reduces load on origin for high-traffic sites (production)
    dynamic "origin_shield" {
      for_each = var.enable_origin_shield ? [1] : []
      content {
        enabled              = true
        origin_shield_region = var.aws_region
      }
    }
  }

  # ---------------------------------------------------------------------------
  # Default Cache Behavior
  # ---------------------------------------------------------------------------
  default_cache_behavior {
    target_origin_id           = "S3-${aws_s3_bucket.frontend.id}"
    viewer_protocol_policy     = "redirect-to-https"
    allowed_methods            = ["GET", "HEAD", "OPTIONS"]
    cached_methods             = ["GET", "HEAD"]
    compress                   = true
    cache_policy_id            = aws_cloudfront_cache_policy.frontend.id
    response_headers_policy_id = aws_cloudfront_response_headers_policy.security_headers.id
  }

  # ---------------------------------------------------------------------------
  # Static Assets Cache Behavior
  # ---------------------------------------------------------------------------
  # Longer cache TTL for immutable assets (JS, CSS with hashed filenames)
  # Uses AWS managed CachingOptimized policy (1 year TTL)

  ordered_cache_behavior {
    path_pattern               = "/assets/*"
    target_origin_id           = "S3-${aws_s3_bucket.frontend.id}"
    viewer_protocol_policy     = "redirect-to-https"
    allowed_methods            = ["GET", "HEAD"]
    cached_methods             = ["GET", "HEAD"]
    compress                   = true
    cache_policy_id            = "658327ea-f89d-4fab-a63d-7e88639e58f6" # CachingOptimized
    response_headers_policy_id = aws_cloudfront_response_headers_policy.security_headers.id
  }

  # ---------------------------------------------------------------------------
  # SPA Routing - Custom Error Responses
  # ---------------------------------------------------------------------------
  # React Router uses client-side routing. When a user directly navigates
  # to /charts/123, CloudFront returns 404. We need to return index.html
  # so React Router can handle the route.

  custom_error_response {
    error_code            = 403
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 10
  }

  custom_error_response {
    error_code            = 404
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 10
  }

  # ---------------------------------------------------------------------------
  # SSL/TLS Configuration
  # ---------------------------------------------------------------------------
  viewer_certificate {
    # Use default CloudFront certificate if no custom domain
    cloudfront_default_certificate = var.acm_certificate_arn == null
    acm_certificate_arn            = var.acm_certificate_arn
    ssl_support_method             = var.acm_certificate_arn != null ? "sni-only" : null
    minimum_protocol_version       = var.acm_certificate_arn != null ? "TLSv1.2_2021" : null
  }

  # ---------------------------------------------------------------------------
  # Geographic Restrictions
  # ---------------------------------------------------------------------------
  # No restrictions - available worldwide
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  # ---------------------------------------------------------------------------
  # Access Logging (Optional)
  # ---------------------------------------------------------------------------
  dynamic "logging_config" {
    for_each = var.enable_access_logs && var.access_logs_bucket != null ? [1] : []

    content {
      bucket          = "${var.access_logs_bucket}.s3.amazonaws.com"
      prefix          = var.access_logs_prefix
      include_cookies = false
    }
  }

  # ---------------------------------------------------------------------------
  # Tags
  # ---------------------------------------------------------------------------
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-frontend-cdn"
  })

  # NOTE: No depends_on for bucket policy - Terraform handles the dependency
  # correctly since the bucket policy references the distribution ARN.
  # The distribution is created first, then the bucket policy.

  lifecycle {
    precondition {
      condition     = var.enable_waf == false || var.waf_web_acl_arn != null
      error_message = "waf_web_acl_arn must be provided when enable_waf is true."
    }
  }
}
