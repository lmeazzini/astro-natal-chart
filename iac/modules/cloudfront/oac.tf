# =============================================================================
# CloudFront Module - Origin Access Control (OAC)
# =============================================================================
# Modern replacement for Origin Access Identity (OAI).
# More secure and supports additional features like signing requests.
# =============================================================================

# -----------------------------------------------------------------------------
# Origin Access Control
# -----------------------------------------------------------------------------
# OAC is the recommended way to secure S3 origins for CloudFront.
# It uses AWS Signature Version 4 for authenticated requests.

resource "aws_cloudfront_origin_access_control" "frontend" {
  name                              = "${local.name_prefix}-frontend-oac"
  description                       = "OAC for ${local.name_prefix} frontend S3 bucket"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}
