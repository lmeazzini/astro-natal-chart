# Cost Optimization

Guide for understanding and optimizing AWS costs in the Astro infrastructure.

## Current Cost Breakdown

### Development Environment (~$98/month)

| Service | Resource | Cost/Month | % of Total |
|---------|----------|------------|------------|
| NAT Gateway | Single AZ | $35.00 | 36% |
| ALB | Application LB | $20.00 | 20% |
| RDS | db.t3.micro | $13.00 | 13% |
| ElastiCache | cache.t3.micro | $12.00 | 12% |
| ECS Fargate | 0.25 vCPU, Spot | $6.00 | 6% |
| CloudFront | Basic CDN | $2.00 | 2% |
| S3 | Storage + requests | $2.00 | 2% |
| Secrets Manager | 3 secrets | $2.00 | 2% |
| Other | KMS, logs, etc. | $6.00 | 6% |
| **Total** | | **~$98** | 100% |

### Production Environment (~$420/month)

| Service | Resource | Cost/Month | % of Total |
|---------|----------|------------|------------|
| NAT Gateway | 3 AZs | $105.00 | 25% |
| RDS | db.t3.medium, Multi-AZ | $100.00 | 24% |
| ECS Fargate | 3 tasks, mixed | $60.00 | 14% |
| ElastiCache | cache.t3.medium | $50.00 | 12% |
| ALB | Application LB | $25.00 | 6% |
| CloudFront | CDN + requests | $20.00 | 5% |
| S3 | Storage + transfer | $15.00 | 4% |
| Secrets Manager | All secrets | $5.00 | 1% |
| Other | KMS, logs, etc. | $40.00 | 10% |
| **Total** | | **~$420** | 100% |

---

## Top Cost Drivers

### 1. NAT Gateway (36% of dev costs)

**Current**: $35/month for single NAT Gateway

**Why it's expensive**: NAT Gateway charges:
- $0.045/hour (~$32.40/month)
- $0.045/GB processed

**Optimization Options**:

| Option | Savings | Trade-off |
|--------|---------|-----------|
| Disable NAT | ~$35/mo | No outbound internet for ECS |
| NAT Instance (t3.nano) | ~$30/mo | Less reliable, more management |
| VPC Endpoints | Variable | Only for AWS services |

```hcl
# Disable NAT Gateway in dev (if not needed)
module "vpc" {
  enable_nat_gateway = false  # ECS tasks won't have internet
}
```

### 2. RDS PostgreSQL (13% of dev costs)

**Current**: db.t3.micro at $13/month

**Optimization Options**:

| Option | Current | Optimized | Savings |
|--------|---------|-----------|---------|
| Reserved Instance (1yr) | $13/mo | $8/mo | ~$5/mo |
| Reserved Instance (3yr) | $13/mo | $5/mo | ~$8/mo |
| Stop during off-hours | $13/mo | $6/mo | ~$7/mo |

```bash
# Stop RDS during nights/weekends (dev only)
aws rds stop-db-instance --db-instance-identifier astro-dev-db

# Restart when needed
aws rds start-db-instance --db-instance-identifier astro-dev-db
```

### 3. ElastiCache Redis (12% of dev costs)

**Current**: cache.t3.micro at $12/month

**Optimization Options**:

| Option | Savings | Trade-off |
|--------|---------|-----------|
| Reserved Instance (1yr) | ~$4/mo | Commitment |
| Use serverless (low usage) | Variable | Pay per use |
| Remove in dev | $12/mo | Use in-memory |

### 4. ECS Fargate (6% of dev costs)

**Current**: FARGATE_SPOT at ~$6/month

**Already Optimized**: Using Spot instances saves ~70% vs On-Demand

**Further Optimization**:

| Option | Savings | Trade-off |
|--------|---------|-----------|
| Reduce CPU/Memory | Variable | May affect performance |
| Scale to zero at night | ~$3/mo | Slower first request |

---

## Cost Optimization Strategies

### 1. Use Spot Instances (Already Implemented)

```hcl
# ECS Fargate Spot (70% savings)
capacity_provider_strategy {
  capacity_provider = "FARGATE_SPOT"
  weight            = 1
  base              = 0
}
```

**Savings**: ~$15/month for typical workload

### 2. Right-Size Resources

Monitor usage and adjust:

```bash
# Check RDS CPU utilization
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name CPUUtilization \
  --dimensions Name=DBInstanceIdentifier,Value=astro-dev-db \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 86400 \
  --statistics Average

# If <20%, consider smaller instance
```

### 3. Reserved Instances (Production)

| Service | On-Demand | 1yr Reserved | 3yr Reserved |
|---------|-----------|--------------|--------------|
| RDS db.t3.medium | $50/mo | $32/mo (36%) | $20/mo (60%) |
| ElastiCache cache.t3.medium | $25/mo | $16/mo (36%) | $10/mo (60%) |

**Recommendation**: Purchase 1-year reserved for stable production workloads.

### 4. S3 Lifecycle Policies

```hcl
# Transition old PDFs to cheaper storage
lifecycle_rule {
  id      = "archive-old-pdfs"
  enabled = true

  transition {
    days          = 30
    storage_class = "STANDARD_IA"  # 40% cheaper
  }

  transition {
    days          = 90
    storage_class = "GLACIER"      # 80% cheaper
  }
}
```

### 5. CloudFront Price Class

```hcl
# Use cheapest edge locations
price_class = "PriceClass_100"  # US, Canada, Europe only
# vs PriceClass_All which includes Asia, Australia, etc.
```

### 6. Log Retention

```hcl
# Reduce CloudWatch log retention
resource "aws_cloudwatch_log_group" "api" {
  retention_in_days = 14  # Instead of 30
}
```

---

## Development Cost Reduction

### Minimal Dev Setup (~$45/month)

```hcl
# Aggressive cost optimization for dev
module "vpc" {
  enable_nat_gateway = false  # Save $35/month
}

module "rds" {
  instance_class       = "db.t3.micro"
  skip_final_snapshot  = true
  backup_retention     = 1  # Minimal backups
}

module "elasticache" {
  node_type = "cache.t3.micro"
}

module "ecs" {
  cpu           = 256
  memory        = 512
  desired_count = 1
  # FARGATE_SPOT already default
}

module "cloudfront" {
  price_class = "PriceClass_100"
  default_ttl = 86400  # Reduce origin requests
}

module "s3" {
  enable_logs_bucket = false  # Skip logs bucket
}
```

### Shutdown Dev at Night

Create a scheduled shutdown:

```bash
# Lambda or EventBridge to stop/start resources
# Stop at 8 PM, start at 8 AM
# Saves ~$30/month for RDS + ECS
```

---

## Production Cost Efficiency

### Recommended Setup (~$350/month)

```hcl
# Balanced cost vs reliability for production
module "rds" {
  instance_class = "db.t3.small"  # Start small, scale up
  multi_az       = true           # Required for prod
}

module "ecs" {
  desired_count = 2
  capacity_provider_strategy = [
    {
      capacity_provider = "FARGATE"
      weight           = 30
      base             = 1  # 1 On-Demand minimum
    },
    {
      capacity_provider = "FARGATE_SPOT"
      weight           = 70
    }
  ]
}
```

---

## Cost Monitoring

### AWS Cost Explorer

Enable detailed billing:

```bash
# View monthly costs by service
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '30 days ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics "UnblendedCost" \
  --group-by Type=DIMENSION,Key=SERVICE
```

### Budget Alerts

```hcl
resource "aws_budgets_budget" "monthly" {
  name              = "astro-monthly-budget"
  budget_type       = "COST"
  limit_amount      = "100"
  limit_unit        = "USD"
  time_period_start = "2025-01-01_00:00"
  time_unit         = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = ["admin@example.com"]
  }
}
```

### Cost Allocation Tags

All resources are tagged for tracking:

```hcl
default_tags {
  tags = {
    Project     = "astro"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
```

---

## Quick Wins

| Action | Savings | Effort | Impact |
|--------|---------|--------|--------|
| Use Spot for ECS | $15/mo | Low | Low risk with good health checks |
| S3 lifecycle policies | $2-5/mo | Low | None |
| CloudFront caching | $2-5/mo | Low | None |
| Reduce log retention | $2-5/mo | Low | Less history |
| Right-size RDS | $5-10/mo | Medium | Monitor first |
| Disable NAT (dev) | $35/mo | Medium | No outbound internet |
| Reserved instances | 30-60% | Medium | Commitment |

---

## Cost Comparison

### vs Other Hosting Options

| Option | Monthly Cost | Pros | Cons |
|--------|--------------|------|------|
| **Current (AWS)** | ~$98 | Scalable, managed | Complexity |
| Digital Ocean | ~$40 | Simple, cheap | Less features |
| Render | ~$70 | Easy deploy | Less control |
| Railway | ~$50 | Simple | Limited scale |
| Self-hosted VPS | ~$20 | Cheapest | All management |

### Break-Even Analysis

AWS makes sense when:
- Need managed databases (RDS)
- Need CDN (CloudFront)
- Need auto-scaling
- Need high availability
- Team size > 2

---

## Monthly Review Checklist

- [ ] Review AWS Cost Explorer
- [ ] Check for unused resources
- [ ] Verify Spot instance usage
- [ ] Review RDS/ElastiCache utilization
- [ ] Check S3 storage growth
- [ ] Review data transfer costs
- [ ] Update reserved instance needs

---

*Last updated: 2025-12-26*
