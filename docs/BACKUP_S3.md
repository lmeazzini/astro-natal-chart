# 📦 Backup S3 Storage - Configuration Guide

This guide explains how to configure automated S3 upload for PostgreSQL backups in the Astro Natal Chart application.

## Overview

The backup system supports automatic upload of database backups to AWS S3 for offsite storage, providing:

- **Durability**: 99.999999999% (11 nines) durability with S3
- **Retry Logic**: 3 upload attempts with exponential backoff (5s → 10s → 20s)
- **Integrity Verification**: MD5 checksum validation after upload
- **Dev Mode**: Works without AWS credentials (local storage only)
- **Cost Effective**: ~$0.72/year for 1 backup/day (50MB)

## Prerequisites

1. **AWS Account** with S3 access
2. **S3 Bucket** for backups (separate from PDF bucket)
3. **IAM Credentials** with appropriate permissions

## Quick Setup

### 1. Create S3 Bucket

```bash
# Using AWS CLI
aws s3 mb s3://your-backup-bucket-name --region us-east-1

# Or use AWS Console: https://s3.console.aws.amazon.com/
```

**Recommended naming:**
- Development: `astro-backups-dev`
- Production: `astro-backups-prod`

### 2. Configure IAM Policy

Create an IAM user or role with this policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::your-backup-bucket-name/*",
        "arn:aws:s3:::your-backup-bucket-name"
      ]
    }
  ]
}
```

### 3. Configure Environment Variables

Add to `apps/api/.env`:

```bash
# AWS Credentials (shared with PDF storage)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1

# Backup S3 Configuration
BACKUP_S3_BUCKET=astro-backups-dev
BACKUP_S3_PREFIX=backups
BACKUP_S3_RETENTION_DAYS=30
BACKUP_S3_GLACIER_DAYS=30
BACKUP_S3_DELETE_DAYS=90
```

### 4. Test Configuration

```bash
# Run backup manually
cd apps/api
./scripts/backup-db.sh

# Verify S3 upload
aws s3 ls s3://your-backup-bucket-name/backups/ --recursive
```

## Usage

### Automatic Backups

The backup script automatically uploads to S3 if `BACKUP_S3_BUCKET` is configured:

```bash
# Scheduled via cron (recommended)
0 3 * * * /path/to/astro/apps/api/scripts/backup-db.sh

# Manual backup
./scripts/backup-db.sh
```

**Upload Process:**
1. Creates local backup with `pg_dump`
2. Compresses with gzip (level 9)
3. Verifies backup integrity with `pg_restore --list`
4. Uploads to S3 with retry logic (3 attempts)
5. Verifies upload integrity with MD5 checksum
6. Logs success/failure

### List Backups in S3

```bash
# Using restore script
./scripts/restore-db.sh --list-s3

# Output:
# Found 30 backups in S3:
#
# Date         Size       Filename                              S3 URL
# --------------------------------------------------------------------------------------------
# 2025-01-20     48.50MB  astro_backup_20250120_143000.sql.gz  s3://...
# 2025-01-19     47.80MB  astro_backup_20250119_030000.sql.gz  s3://...
# ...
```

### Restore from S3

```bash
# 1. List backups to find S3 URL
./scripts/restore-db.sh --list-s3

# 2. Download and restore specific backup
./scripts/restore-db.sh --download-s3 s3://bucket/backups/20250120/astro_backup_20250120_143000.sql.gz

# With auto-confirmation (dangerous!)
./scripts/restore-db.sh --download-s3 s3://... --no-confirm
```

## S3 Lifecycle Policy (Optional)

To automatically transition backups to Glacier and delete old backups, configure an S3 Lifecycle Policy:

### Using AWS Console

1. Go to S3 Console → Your Bucket → Management → Lifecycle rules
2. Create rule: "Backup Retention"
3. Apply to prefix: `backups/`
4. Add transitions:
   - Transition to Glacier after **30 days**
   - Expire after **90 days**

### Using AWS CLI

Create `lifecycle-policy.json`:

```json
{
  "Rules": [
    {
      "Id": "BackupRetentionPolicy",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "backups/"
      },
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "GLACIER"
        }
      ],
      "Expiration": {
        "Days": 90
      }
    }
  ]
}
```

Apply policy:

```bash
aws s3api put-bucket-lifecycle-configuration \
  --bucket your-backup-bucket-name \
  --lifecycle-configuration file://lifecycle-policy.json
```

## S3 Key Structure

Backups are organized by date for easy lifecycle management:

```
s3://your-backup-bucket-name/
└── backups/
    ├── 20250120/
    │   ├── astro_backup_20250120_030000.sql.gz  (daily backup)
    │   └── astro_backup_20250120_143000.sql.gz  (manual backup)
    ├── 20250119/
    │   └── astro_backup_20250119_030000.sql.gz
    └── 20250118/
        └── astro_backup_20250118_030000.sql.gz
```

## Cost Estimation

### Storage Costs (us-east-1)

| Scenario | Storage | S3 Standard | Glacier | Total/Month | Total/Year |
|----------|---------|-------------|---------|-------------|------------|
| **Small** (30 days, 50MB/day) | 1.5 GB | $0.035 | - | **$0.04** | **$0.48** |
| **Medium** (90 days, 100MB/day) | 9 GB | $0.21 | - | **$0.21** | **$2.52** |
| **Large** (90 days, 500MB/day) | 45 GB | $1.04 | - | **$1.04** | **$12.48** |
| **With Glacier** (30 days S3, 60 days Glacier, 50MB/day) | 4.5 GB | $0.035 | $0.012 | **$0.06** | **$0.72** |

### Request Costs

- **PUT requests**: $0.005 per 1,000 (1 backup/day = $0.00015/month)
- **GET requests**: $0.0004 per 1,000 (rare, mostly for restores)
- **LIST requests**: Included in standard pricing

### AWS Free Tier (First 12 Months)

- 5 GB S3 Standard storage (FREE)
- 20,000 GET requests
- 2,000 PUT requests

**Conclusion**: First year is **FREE** for typical usage, then < $1/month.

## Security Best Practices

### 1. Private Bucket

Ensure bucket is not publicly accessible:

```bash
# Check public access
aws s3api get-public-access-block --bucket your-backup-bucket-name

# Block all public access (recommended)
aws s3api put-public-access-block \
  --bucket your-backup-bucket-name \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

### 2. Encryption

S3 automatically encrypts objects at rest with AES-256 (SSE-S3). For additional security, enable:

```bash
# Enable default encryption
aws s3api put-bucket-encryption \
  --bucket your-backup-bucket-name \
  --server-side-encryption-configuration \
    '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
```

### 3. Separate IAM Credentials

For production, use separate IAM credentials for backups vs PDFs:

```bash
# .env
AWS_ACCESS_KEY_ID=pdf-storage-key         # For PDF uploads
AWS_SECRET_ACCESS_KEY=pdf-storage-secret

BACKUP_AWS_ACCESS_KEY_ID=backup-key       # For backups (optional)
BACKUP_AWS_SECRET_ACCESS_KEY=backup-secret
```

### 4. Versioning (Optional)

Enable versioning for accidental deletion protection:

```bash
aws s3api put-bucket-versioning \
  --bucket your-backup-bucket-name \
  --versioning-configuration Status=Enabled
```

⚠️ **Warning**: Versioning increases storage costs (keeps all versions).

## Troubleshooting

### Issue: "S3 upload skipped (BACKUP_S3_BUCKET not configured)"

**Solution**: Set `BACKUP_S3_BUCKET` in `.env` file.

### Issue: "Failed to upload backup to S3: NoCredentialsError"

**Solutions**:
1. Check `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are set
2. Verify credentials are valid: `aws sts get-caller-identity`
3. Ensure IAM user has `s3:PutObject` permission

### Issue: "Integrity verification failed"

**Possible causes**:
1. Network corruption during upload
2. S3 transfer issues

**Solution**: The backup script automatically retries (3 attempts). Check logs for details:

```bash
tail -f /var/log/astro-backup.log
```

### Issue: "Upload takes too long"

**Solutions**:
1. Check backup size: `ls -lh /var/backups/astro-db/`
2. Test network speed to S3: `aws s3 cp test-file s3://bucket/ --debug`
3. Consider multipart upload for large backups (future enhancement)

### Issue: "Cannot list backups: AccessDenied"

**Solution**: Ensure IAM user has `s3:ListBucket` permission on the bucket resource (not object resource).

## Dev Mode (No S3)

For local development without AWS credentials:

```bash
# .env
BACKUP_S3_BUCKET=  # Leave empty

# Backups will only be stored locally
./scripts/backup-db.sh
```

**Dev mode behavior:**
- `upload_backup()` returns `file:///path/to/backup`
- `list_backups()` returns empty list
- `download_backup()` returns False

## Monitoring & Alerts

### Healthcheck Integration

The backup script supports healthcheck monitoring (e.g., healthchecks.io):

```bash
# .env
BACKUP_HEALTHCHECK_URL=https://hc-ping.com/your-uuid
BACKUP_HEALTHCHECK_FAIL_URL=https://hc-ping.com/your-uuid/fail
```

### CloudWatch Metrics (Advanced)

For production monitoring, consider setting up:

1. **S3 Bucket Metrics**: Monitor PUT requests, object count
2. **CloudWatch Alarms**: Alert on failed uploads
3. **Lambda Function**: Verify backup age and size

## LGPD/GDPR Compliance

⚠️ **Important**: Backups contain personal data (birth dates, locations).

### Data Retention

- **S3 Lifecycle**: Auto-delete after 90 days
- **User Deletion**: When user requests deletion, manually remove from old backups:

```bash
# Find user data in backups
aws s3 ls s3://your-backup-bucket-name/backups/ --recursive | grep "20250"

# Download backup
aws s3 cp s3://your-backup-bucket-name/backups/20250120/astro_backup_20250120_030000.sql.gz .

# Restore, remove user data, re-backup
# (Complex - recommend automated solution for production)
```

### Audit Logs

Backup operations are logged in:
- `/var/log/astro-backup.log` (script logs)
- Application audit logs (database table `audit_logs`)

## References

- [AWS S3 Pricing](https://aws.amazon.com/s3/pricing/)
- [S3 Lifecycle Configuration](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html)
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [Boto3 S3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)

## Support

For issues or questions:
1. Check logs: `tail -f /var/log/astro-backup.log`
2. Test S3 access: `aws s3 ls s3://your-backup-bucket-name/`
3. Open GitHub issue: [astro-natal-chart/issues](https://github.com/lmeazzini/astro-natal-chart/issues)
