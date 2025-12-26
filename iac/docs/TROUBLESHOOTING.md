# Troubleshooting Guide

Common issues and solutions for the Astro infrastructure.

## Quick Diagnostics

```bash
# Check ECS service status
aws ecs describe-services \
  --cluster astro-dev-cluster \
  --services astro-dev-api \
  --query 'services[0].{status:status,running:runningCount,desired:desiredCount}'

# Check RDS status
aws rds describe-db-instances \
  --db-instance-identifier astro-dev-db \
  --query 'DBInstances[0].DBInstanceStatus'

# Check ElastiCache status
aws elasticache describe-cache-clusters \
  --cache-cluster-id astro-dev-redis \
  --query 'CacheClusters[0].CacheClusterStatus'

# Check recent ECS events
aws ecs describe-services \
  --cluster astro-dev-cluster \
  --services astro-dev-api \
  --query 'services[0].events[:5]'
```

---

## Terraform Issues

### "No valid credential sources found"

**Symptoms**: Terraform commands fail with credential errors

**Solution**:
```bash
# Reload AWS credentials
source scripts/init-backend.sh

# Verify credentials
aws sts get-caller-identity
```

### "Backend configuration changed"

**Symptoms**: `terraform init` fails

**Solution**:
```bash
terraform init -reconfigure
```

### "State lock held"

**Symptoms**: `Error acquiring the state lock`

**Solution**:
```bash
# Check who holds the lock
aws dynamodb scan \
  --table-name astro-terraform-locks \
  --filter-expression "attribute_exists(LockID)"

# Force unlock (use with caution!)
terraform force-unlock LOCK_ID

# Or manually delete lock
aws dynamodb delete-item \
  --table-name astro-terraform-locks \
  --key '{"LockID": {"S": "astro-terraform-state-123/dev/terraform.tfstate"}}'
```

### "Resource already exists"

**Symptoms**: `Error creating X: X already exists`

**Solution**:
```bash
# Import existing resource
terraform import aws_s3_bucket.example bucket-name

# Or destroy and recreate (dev only!)
terraform destroy -target=aws_s3_bucket.example
terraform apply
```

### "Cycle detected"

**Symptoms**: Terraform plan fails with dependency cycle

**Solution**:
- Review module dependencies
- Use `depends_on` explicitly
- Split circular dependencies into separate applies

---

## ECS Issues

### Task Won't Start

**Symptoms**: ECS tasks stuck in PENDING or fail immediately

**Diagnose**:
```bash
# Get stopped task reason
aws ecs describe-tasks \
  --cluster astro-dev-cluster \
  --tasks $(aws ecs list-tasks --cluster astro-dev-cluster --desired-status STOPPED --query 'taskArns[0]' --output text) \
  --query 'tasks[0].{reason:stoppedReason,code:stopCode}'
```

**Common Causes**:

| Reason | Solution |
|--------|----------|
| `CannotPullContainerError` | Check ECR permissions, image exists |
| `ResourceInitializationError` | Check secrets access |
| `OutOfMemory` | Increase task memory |
| `HealthCheckFailure` | Check app health endpoint |

### Container Keeps Crashing

**Symptoms**: Tasks start but restart repeatedly

**Diagnose**:
```bash
# Check container logs
aws logs tail /ecs/astro-dev-api --since 1h

# Search for errors
aws logs filter-log-events \
  --log-group-name /ecs/astro-dev-api \
  --filter-pattern "ERROR" \
  --start-time $(date -d '1 hour ago' +%s000)
```

### Can't Connect to Database

**Symptoms**: Database connection errors in logs

**Check**:
```bash
# Verify security group allows connection
aws ec2 describe-security-group-rules \
  --filters Name=group-id,Values=sg-xxx \
  --query 'SecurityGroupRules[?FromPort==`5432`]'

# Check ECS task is in correct subnet
aws ecs describe-tasks \
  --cluster astro-dev-cluster \
  --tasks $TASK_ARN \
  --query 'tasks[0].containers[0].networkInterfaces[0].privateIpv4Address'
```

### ECS Exec Not Working

**Symptoms**: Can't connect to running container

**Check**:
```bash
# Verify ECS Exec is enabled
aws ecs describe-services \
  --cluster astro-dev-cluster \
  --services astro-dev-api \
  --query 'services[0].enableExecuteCommand'

# Check IAM permissions for SSM
aws iam get-role-policy \
  --role-name astro-dev-ecs-task-role \
  --policy-name astro-dev-ecs-task-exec
```

**Solution**:
```bash
# Force new deployment with ECS Exec
aws ecs update-service \
  --cluster astro-dev-cluster \
  --service astro-dev-api \
  --enable-execute-command \
  --force-new-deployment
```

---

## RDS Issues

### Can't Connect to RDS

**Symptoms**: Connection timeouts or refused

**Check**:
```bash
# Verify RDS is running
aws rds describe-db-instances \
  --db-instance-identifier astro-dev-db \
  --query 'DBInstances[0].DBInstanceStatus'

# Check security group
aws rds describe-db-instances \
  --db-instance-identifier astro-dev-db \
  --query 'DBInstances[0].VpcSecurityGroups'
```

**Common Causes**:

| Issue | Solution |
|-------|----------|
| Security group blocks | Add ECS SG as source on port 5432 |
| Wrong credentials | Check Secrets Manager value |
| RDS stopped | Start the instance |
| Subnet issues | Verify RDS is in correct subnet |

### RDS Out of Storage

**Symptoms**: Write operations fail

**Solution**:
```bash
# Check current storage
aws rds describe-db-instances \
  --db-instance-identifier astro-dev-db \
  --query 'DBInstances[0].{Allocated:AllocatedStorage,FreeSpace:FreeStorageSpace}'

# Increase storage (takes ~30 min)
aws rds modify-db-instance \
  --db-instance-identifier astro-dev-db \
  --allocated-storage 50 \
  --apply-immediately
```

### RDS High CPU

**Symptoms**: Slow queries, high latency

**Diagnose**:
```bash
# Get CPU metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name CPUUtilization \
  --dimensions Name=DBInstanceIdentifier,Value=astro-dev-db \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 \
  --statistics Average
```

**Solutions**:
- Add indexes for slow queries
- Upgrade instance class
- Enable Performance Insights
- Review query patterns

---

## ElastiCache Issues

### Redis Connection Refused

**Symptoms**: Can't connect to Redis

**Check**:
```bash
# Verify cluster is available
aws elasticache describe-cache-clusters \
  --cache-cluster-id astro-dev-redis

# Check security group
aws ec2 describe-security-groups \
  --group-ids sg-xxx \
  --query 'SecurityGroups[0].IpPermissions'
```

### Redis Out of Memory

**Symptoms**: Evictions, slow performance

**Check**:
```bash
# Get memory metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ElastiCache \
  --metric-name BytesUsedForCache \
  --dimensions Name=CacheClusterId,Value=astro-dev-redis \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 300 \
  --statistics Maximum
```

**Solutions**:
- Increase node size
- Review TTL policies
- Clear unnecessary keys

---

## CloudFront / S3 Issues

### 403 Forbidden on Frontend

**Symptoms**: Can't access frontend files

**Check**:
```bash
# Verify S3 bucket policy
aws s3api get-bucket-policy --bucket astro-dev-frontend-xyz

# Check CloudFront OAC
aws cloudfront get-distribution --id E1234ABCD \
  --query 'Distribution.DistributionConfig.Origins.Items[0].OriginAccessControlId'
```

### Stale Content After Deploy

**Symptoms**: Old version still showing

**Solution**:
```bash
# Create cache invalidation
aws cloudfront create-invalidation \
  --distribution-id E1234ABCD \
  --paths "/*"

# Check invalidation status
aws cloudfront list-invalidations --distribution-id E1234ABCD
```

### S3 Upload Fails

**Symptoms**: Can't upload files to S3

**Check**:
```bash
# Verify IAM permissions
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123:role/astro-dev-ecs-task-role \
  --action-names s3:PutObject \
  --resource-arns arn:aws:s3:::astro-dev-pdfs-xyz/*
```

---

## Secrets Manager Issues

### Can't Read Secrets

**Symptoms**: ECS task fails to start with secret errors

**Check**:
```bash
# Verify secret exists
aws secretsmanager describe-secret \
  --secret-id astro/dev/database-url

# Check KMS permissions
aws kms describe-key \
  --key-id alias/astro-dev-secrets
```

### Secret Version Mismatch

**Symptoms**: App uses old secret value

**Solution**:
```bash
# Force ECS to pull new secrets
aws ecs update-service \
  --cluster astro-dev-cluster \
  --service astro-dev-api \
  --force-new-deployment
```

---

## Network Issues

### NAT Gateway Issues

**Symptoms**: ECS tasks can't reach internet

**Check**:
```bash
# Verify NAT Gateway is active
aws ec2 describe-nat-gateways \
  --filter Name=tag:Name,Values=astro-dev-nat

# Check route table
aws ec2 describe-route-tables \
  --filters Name=association.subnet-id,Values=subnet-xxx
```

### VPC Endpoint Issues

**Symptoms**: Can't reach AWS services

**Check**:
```bash
# List VPC endpoints
aws ec2 describe-vpc-endpoints \
  --filters Name=vpc-id,Values=vpc-xxx
```

---

## CI/CD Issues

### GitHub Actions Failing

**Check**:
1. Verify GitHub secrets are set
2. Check AWS credentials are valid
3. Review workflow logs

**Common Issues**:

| Error | Solution |
|-------|----------|
| `Invalid credentials` | Rotate AWS access keys |
| `Image not found` | Check ECR repository name |
| `Service not stabilizing` | Review ECS task logs |

### Deployment Stuck

**Symptoms**: ECS deployment doesn't complete

**Solution**:
```bash
# Check deployment status
aws ecs describe-services \
  --cluster astro-dev-cluster \
  --services astro-dev-api \
  --query 'services[0].deployments'

# Cancel stuck deployment
aws ecs update-service \
  --cluster astro-dev-cluster \
  --service astro-dev-api \
  --force-new-deployment
```

---

## Log Analysis

### Find Errors in Logs

```bash
# Recent errors
aws logs filter-log-events \
  --log-group-name /ecs/astro-dev-api \
  --filter-pattern "ERROR" \
  --start-time $(date -d '1 hour ago' +%s000)

# Find specific request
aws logs filter-log-events \
  --log-group-name /ecs/astro-dev-api \
  --filter-pattern "request_id=abc123"
```

### Export Logs for Analysis

```bash
# Export to S3
aws logs create-export-task \
  --log-group-name /ecs/astro-dev-api \
  --from $(date -d '24 hours ago' +%s000) \
  --to $(date +%s000) \
  --destination astro-dev-logs-xyz \
  --destination-prefix "exports"
```

---

## Quick Reference

| Issue | Command |
|-------|---------|
| Check ECS health | `aws ecs describe-services --cluster X --services Y` |
| View recent logs | `aws logs tail /ecs/astro-dev-api --since 1h` |
| Force redeploy | `aws ecs update-service --cluster X --service Y --force-new-deployment` |
| Check RDS status | `aws rds describe-db-instances --db-instance-identifier X` |
| Invalidate cache | `aws cloudfront create-invalidation --distribution-id X --paths "/*"` |
| Unlock Terraform | `terraform force-unlock LOCK_ID` |

---

*Last updated: 2025-12-26*
