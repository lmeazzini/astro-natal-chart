# =============================================================================
# Production Environment Values
# =============================================================================

aws_region  = "us-east-2"
environment = "prod"

# -----------------------------------------------------------------------------
# VPC Configuration
# -----------------------------------------------------------------------------

vpc_cidr                       = "10.1.0.0/16"
availability_zone              = "us-east-2a"
availability_zone_secondary    = "us-east-2b"
public_subnet_cidr             = "10.1.1.0/24"
public_subnet_cidr_secondary   = "10.1.2.0/24"
private_subnet_cidr            = "10.1.11.0/24"
database_subnet_cidr           = "10.1.21.0/24"
database_subnet_cidr_secondary = "10.1.22.0/24"
enable_nat_gateway             = true

# -----------------------------------------------------------------------------
# RDS Configuration
# -----------------------------------------------------------------------------

db_instance_class = "db.t3.micro"

# -----------------------------------------------------------------------------
# ElastiCache Configuration
# -----------------------------------------------------------------------------

redis_node_type = "cache.t3.micro"

# -----------------------------------------------------------------------------
# ECS Configuration
# -----------------------------------------------------------------------------

ecs_cpu           = 512
ecs_memory        = 1024
ecs_desired_count = 1

# -----------------------------------------------------------------------------
# S3/CloudFront Configuration
# -----------------------------------------------------------------------------

# Production domain for CORS
allowed_origins        = ["https://www.realastrology.ai", "https://realastrology.ai"]
cloudfront_price_class = "PriceClass_100"
cloudfront_default_ttl = 86400

# -----------------------------------------------------------------------------
# DNS Configuration (optional - enable after initial deployment)
# -----------------------------------------------------------------------------
# NOTE: Deploy infrastructure first without domain, then enable for custom domain
domain_name        = "realastrology.ai"
create_hosted_zone = true
frontend_subdomain = "www"
api_subdomain      = "api"

# -----------------------------------------------------------------------------
# Stripe Configuration (payment processing)
# -----------------------------------------------------------------------------
stripe_publishable_key = "pk_live_51Sl86OPXpwjspox5W9FSVQJNxyKmEucewdiLdpUmSlIgHAUxzio52MO0OPvF5onNDeIduhRAmMKQ5UGsbpzYTkot00kh1UMNzX"
