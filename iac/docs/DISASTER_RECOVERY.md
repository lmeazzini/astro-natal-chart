# Disaster Recovery

Disaster recovery procedures and business continuity planning for the Astro infrastructure.

## Recovery Objectives

| Environment | RTO | RPO | Priority |
|-------------|-----|-----|----------|
| **Production** | 1 hour | 5 minutes | Critical |
| **Staging** | 4 hours | 1 hour | High |
| **Dev** | 24 hours | 24 hours | Low |

- **RTO** (Recovery Time Objective): Maximum acceptable downtime
- **RPO** (Recovery Point Objective): Maximum acceptable data loss

---

## Backup Strategy

### RDS PostgreSQL

| Feature | Dev | Staging | Prod |
|---------|-----|---------|------|
| Automated Backups | Yes | Yes | Yes |
| Retention Period | 7 days | 14 days | 30 days |
| PITR (Point-in-Time) | Yes | Yes | Yes |
| PITR Granularity | 5 minutes | 5 minutes | 5 minutes |
| Manual Snapshots | Weekly | Weekly | Daily |
| Cross-Region Backup | No | No | Yes |

### S3 Buckets

| Bucket | Versioning | Lifecycle | Cross-Region |
|--------|------------|-----------|--------------|
| Frontend | Yes | 30 days | No |
| PDFs | Yes | 90 days | Yes (prod) |
| Backups | Yes | 90 days | Yes |

### Secrets Manager

- **Deletion Protection**: 7-day recovery window
- **Backup**: Included in Terraform state

### Terraform State

| Protection | Status |
|------------|--------|
| S3 Versioning | Enabled |
| S3 Encryption | AES-256 |
| DynamoDB Locking | Enabled |

---

## Disaster Scenarios

### 1. RDS Database Corruption

**Symptoms**: Application errors, data inconsistency

**Recovery Steps**:

```bash
# Option A: Point-in-Time Recovery (< 5 min data loss)
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier astro-prod-db \
  --target-db-instance-identifier astro-prod-db-restored \
  --restore-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%SZ)

# Option B: Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier astro-prod-db-restored \
  --db-snapshot-identifier rds:astro-prod-db-2025-01-15-03-00

# Update DNS/connection string after verification
# Test restored database before switching traffic
```

### 2. RDS Instance Failure

**Symptoms**: Database unreachable, connection timeouts

**Recovery Steps** (Multi-AZ enabled):
- Automatic failover to standby (< 2 minutes)
- No action required for Multi-AZ

**Recovery Steps** (Single-AZ):
```bash
# Restore from latest automated backup
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier astro-dev-db \
  --target-db-instance-identifier astro-dev-db-new \
  --use-latest-restorable-time

# Update connection string in Secrets Manager
aws secretsmanager put-secret-value \
  --secret-id astro/dev/database-url \
  --secret-string "postgresql+asyncpg://user:pass@new-endpoint:5432/astro"

# Restart ECS tasks
aws ecs update-service \
  --cluster astro-dev-cluster \
  --service astro-dev-api \
  --force-new-deployment
```

### 3. ElastiCache Redis Failure

**Symptoms**: Rate limiting not working, cache misses

**Recovery Steps**:
```bash
# Redis data is ephemeral (cache only)
# No data recovery needed - just ensure cluster is running

# Check cluster status
aws elasticache describe-cache-clusters \
  --cache-cluster-id astro-dev-redis

# If failed, recreate via Terraform
cd iac/environments/dev
terraform apply -target=module.elasticache
```

### 4. ECS Tasks Failing

**Symptoms**: 503 errors, API unreachable

**Recovery Steps**:
```bash
# Check failed tasks
aws ecs describe-tasks \
  --cluster astro-dev-cluster \
  --tasks $(aws ecs list-tasks --cluster astro-dev-cluster --desired-status STOPPED --query 'taskArns[:5]' --output text)

# Force new deployment with previous image
aws ecs update-service \
  --cluster astro-dev-cluster \
  --service astro-dev-api \
  --task-definition astro-dev-api:42 \
  --force-new-deployment

# Check CloudWatch logs for root cause
aws logs tail /ecs/astro-dev-api --follow
```

### 5. S3 Bucket Data Loss

**Symptoms**: Missing files, 404 errors

**Recovery Steps**:
```bash
# S3 versioning enabled - recover deleted objects
aws s3api list-object-versions \
  --bucket astro-dev-pdfs-xyz \
  --prefix "user123/chart456/" \
  --query "DeleteMarkers[].{Key:Key,VersionId:VersionId}"

# Remove delete marker to restore
aws s3api delete-object \
  --bucket astro-dev-pdfs-xyz \
  --key "user123/chart456/report.pdf" \
  --version-id "delete-marker-version-id"

# Or restore specific version
aws s3api copy-object \
  --bucket astro-dev-pdfs-xyz \
  --copy-source "astro-dev-pdfs-xyz/file.pdf?versionId=version123" \
  --key "file.pdf"
```

### 6. Terraform State Corruption

**Symptoms**: Terraform plan shows unexpected changes

**Recovery Steps**:
```bash
# List state file versions
aws s3api list-object-versions \
  --bucket astro-terraform-state-123456789 \
  --prefix "dev/terraform.tfstate"

# Download previous version
aws s3api get-object \
  --bucket astro-terraform-state-123456789 \
  --key "dev/terraform.tfstate" \
  --version-id "previous-version-id" \
  terraform.tfstate.backup

# Verify backup state
terraform show terraform.tfstate.backup

# Restore by uploading to S3
aws s3 cp terraform.tfstate.backup s3://astro-terraform-state-123456789/dev/terraform.tfstate

# Remove lock if stuck
aws dynamodb delete-item \
  --table-name astro-terraform-locks \
  --key '{"LockID": {"S": "astro-terraform-state-123456789/dev/terraform.tfstate"}}'
```

### 7. Complete Region Failure

**Symptoms**: All AWS services in region unavailable

**Recovery Steps** (requires cross-region setup):

```bash
# 1. Update DNS to failover region
# 2. Deploy infrastructure in backup region
cd iac/environments/prod-dr
terraform init
terraform apply

# 3. Restore RDS from cross-region backup
aws rds restore-db-instance-from-db-snapshot \
  --region us-west-2 \
  --db-instance-identifier astro-prod-db \
  --db-snapshot-identifier arn:aws:rds:us-west-2:123:snapshot:cross-region-backup

# 4. Sync S3 data (if not already replicated)
aws s3 sync s3://astro-prod-pdfs-useast1/ s3://astro-prod-pdfs-uswest2/
```

---

## Recovery Procedures

### Full Infrastructure Rebuild

If all infrastructure is lost:

```bash
# 1. Bootstrap (if state bucket lost)
cd iac/bootstrap
terraform init
terraform apply

# 2. Deploy environment
cd iac/environments/prod
# Update backend configuration if bucket name changed
terraform init
terraform apply

# 3. Restore data
# - RDS: Restore from snapshot or cross-region backup
# - S3: Sync from cross-region replication or backup
# - Secrets: Recreate via Terraform or backup

# 4. Verify
curl https://api.example.com/health
```

### Database Restoration Runbook

```bash
#!/bin/bash
# restore-rds.sh

ENV=${1:-dev}
SNAPSHOT_ID=${2:-latest}

echo "Restoring RDS for $ENV environment..."

# Get latest snapshot if not specified
if [ "$SNAPSHOT_ID" == "latest" ]; then
  SNAPSHOT_ID=$(aws rds describe-db-snapshots \
    --db-instance-identifier astro-$ENV-db \
    --query 'sort_by(DBSnapshots,&SnapshotCreateTime)[-1].DBSnapshotIdentifier' \
    --output text)
fi

echo "Using snapshot: $SNAPSHOT_ID"

# Restore
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier astro-$ENV-db-restored \
  --db-snapshot-identifier $SNAPSHOT_ID \
  --db-subnet-group-name astro-$ENV-db-subnet \
  --vpc-security-group-ids sg-xxx

# Wait for availability
aws rds wait db-instance-available \
  --db-instance-identifier astro-$ENV-db-restored

echo "Restoration complete!"
echo "New endpoint: $(aws rds describe-db-instances \
  --db-instance-identifier astro-$ENV-db-restored \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text)"
```

---

## Backup Verification

### Monthly Backup Tests

```bash
# 1. Restore RDS snapshot to test instance
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier astro-backup-test \
  --db-snapshot-identifier rds:astro-prod-db-$(date +%Y-%m-%d)-03-00

# 2. Verify data integrity
psql -h backup-test-endpoint -U postgres -d astro -c "SELECT COUNT(*) FROM users;"

# 3. Clean up test instance
aws rds delete-db-instance \
  --db-instance-identifier astro-backup-test \
  --skip-final-snapshot
```

### State File Backup Verification

```bash
# Verify state file versions exist
aws s3api list-object-versions \
  --bucket astro-terraform-state-123456789 \
  --prefix "prod/terraform.tfstate" \
  --query 'length(Versions)'
```

---

## Preventive Measures

### 1. Enable Deletion Protection

```hcl
# RDS
resource "aws_db_instance" "main" {
  deletion_protection = true  # Prod only
}

# S3 - prevent accidental deletion
resource "aws_s3_bucket" "main" {
  force_destroy = false  # Prod only
}
```

### 2. Cross-Region Replication

```hcl
# S3 cross-region replication
resource "aws_s3_bucket_replication_configuration" "pdfs" {
  bucket = aws_s3_bucket.pdfs.id

  rule {
    status = "Enabled"
    destination {
      bucket        = "arn:aws:s3:::astro-prod-pdfs-dr"
      storage_class = "STANDARD_IA"
    }
  }
}
```

### 3. Automated Alerts

```hcl
# CloudWatch alarm for RDS
resource "aws_cloudwatch_metric_alarm" "rds_cpu" {
  alarm_name          = "astro-prod-rds-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_actions       = [aws_sns_topic.alerts.arn]
}
```

---

## Contacts

| Role | Contact | When to Notify |
|------|---------|----------------|
| On-Call Engineer | PagerDuty | Automated alerts |
| DevOps Lead | [email] | Major incidents |
| Database Admin | [email] | Data corruption |
| Management | [email] | Extended outages (>1hr) |

---

## Runbook Checklist

### RDS Recovery

- [ ] Identify failure type (instance/data/corruption)
- [ ] Select appropriate snapshot or PITR time
- [ ] Restore to new instance
- [ ] Verify data integrity
- [ ] Update connection string
- [ ] Restart application
- [ ] Monitor for issues
- [ ] Document incident

### Full Outage Recovery

- [ ] Assess scope of outage
- [ ] Notify stakeholders
- [ ] Begin infrastructure rebuild
- [ ] Restore databases
- [ ] Restore secrets
- [ ] Deploy application
- [ ] Verify all services
- [ ] Update status page
- [ ] Conduct post-mortem

---

*Last updated: 2025-12-26*
