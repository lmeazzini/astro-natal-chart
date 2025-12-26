# Disaster Recovery Plan

**Astro Natal Chart Application**
**Version:** 1.1.0
**Last Updated:** 2025-12-26
**Owner:** DevOps Team

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Recovery Objectives](#recovery-objectives)
3. [Backup Strategy](#backup-strategy)
4. [Recovery Procedures](#recovery-procedures)
5. [Testing & Validation](#testing--validation)
6. [Emergency Contacts](#emergency-contacts)
7. [Post-Recovery Checklist](#post-recovery-checklist)

---

## Executive Summary

This document outlines the disaster recovery (DR) procedures for the Astro Natal Chart application. It provides step-by-step instructions for recovering from various failure scenarios, ensuring business continuity and data integrity.

### Key Points

- **Automated daily backups** of PostgreSQL and Qdrant databases
- **30-day retention** for local backups
- **Offsite storage** via AWS S3 (optional but recommended)
- **RTO (Recovery Time Objective):** 4 hours
- **RPO (Recovery Point Objective):** 24 hours (daily backups)
- **Tested restore procedures** via automated tests

---

## Recovery Objectives

### RTO (Recovery Time Objective)

**Target: 4 hours**

Maximum acceptable downtime from disaster detection to full service restoration.

| Scenario | Expected RTO |
|----------|--------------|
| Database corruption | 1-2 hours |
| Server failure | 2-4 hours |
| Complete infrastructure loss | 4-8 hours |
| Accidental data deletion | 30 minutes - 1 hour |

### RPO (Recovery Point Objective)

**Target: 24 hours**

Maximum acceptable data loss measured in time. Daily backups mean we can lose at most 24 hours of data.

**Mitigation:**
- Backups run daily at 2 AM (configurable via cron)
- Increase backup frequency to hourly for production if required
- Consider real-time replication for critical production workloads

---

## Backup Strategy

### What is Backed Up

1. **PostgreSQL Database** (Critical)
   - All user accounts and authentication data
   - Birth chart metadata and calculations
   - Audit logs and user consent records
   - OAuth account linkages

2. **Qdrant Vector Database** (Important)
   - Astrological knowledge base vectors
   - RAG (Retrieval-Augmented Generation) embeddings
   - Not critical - can be regenerated from source documents

3. **Not Backed Up** (by database backup)
   - Redis cache data (non-persistent, can be rebuilt)
   - Static files and application code (in Git)
   - Docker volumes (should be recreated from code)

### Backup Schedule

**Automated daily backups** via cron:

```bash
# /etc/cron.d/astro-backup
0 2 * * * /opt/astro/scripts/backup-db.sh >> /var/log/astro-backup.log 2>&1
```

### Backup Locations

1. **Primary (Local):** `/var/backups/astro-db/`
   - Retention: 30 days
   - Compressed with gzip (compression level 9)
   - Format: PostgreSQL custom format (`.sql.gz`)

2. **Offsite (S3):** `s3://your-bucket/backups/`
   - Indefinite retention (S3 lifecycle policies can be configured)
   - Automatic upload after successful backup
   - MD5 verification for integrity

### Backup File Naming

```
PostgreSQL: astro_backup_YYYYMMDD_HHMMSS.sql.gz
Qdrant:     qdrant_backup_YYYYMMDD_HHMMSS.snapshot
```

Example: `astro_backup_20250125_020000.sql.gz`

---

## Recovery Procedures

### Scenario 1: Database Corruption

**Symptoms:**
- PostgreSQL errors in logs
- Application unable to connect to database
- Data integrity violations
- Unexpected crashes or restarts

**Recovery Steps:**

1. **Identify the issue**
   ```bash
   # Check PostgreSQL logs
   docker logs astro-db-1

   # Check database connectivity
   docker exec astro-db-1 psql -U astro_user -d astro -c "SELECT 1"
   ```

2. **Stop dependent services**
   ```bash
   docker-compose stop api celery_worker web
   ```

3. **List available backups**
   ```bash
   ls -lh /var/backups/astro-db/astro_backup_*.sql.gz
   ```

4. **Restore from most recent backup**
   ```bash
   ./scripts/restore-db.sh \
     --backup-file /var/backups/astro-db/astro_backup_YYYYMMDD_HHMMSS.sql.gz
   ```

5. **Validate restoration**
   ```bash
   docker exec astro-db-1 psql -U astro_user -d astro -c "SELECT COUNT(*) FROM users"
   ```

6. **Restart services**
   ```bash
   docker-compose up -d api celery_worker web
   ```

7. **Verify application health**
   ```bash
   curl http://localhost:8000/health
   ```

**Expected Recovery Time:** 1-2 hours

---

### Scenario 2: Complete Server Failure

**Symptoms:**
- Server unresponsive
- Hardware failure
- Operating system corruption
- Cannot SSH into server

**Recovery Steps:**

1. **Provision new server**
   - Same OS version (Ubuntu 22.04 LTS)
   - Minimum specs: 4 CPU, 8GB RAM, 100GB SSD
   - Install Docker and Docker Compose

2. **Clone application repository**
   ```bash
   git clone https://github.com/your-org/astro-natal-chart.git
   cd astro-natal-chart
   ```

3. **Configure environment**
   ```bash
   cp apps/api/.env.example apps/api/.env
   cp apps/web/.env.example apps/web/.env
   # Edit .env files with production values
   ```

4. **Start infrastructure services**
   ```bash
   docker-compose up -d db redis qdrant
   # Wait for services to be ready
   sleep 30
   ```

5. **Download backup from S3 (if using offsite)**
   ```bash
   mkdir -p /var/backups/astro-db
   aws s3 cp s3://your-bucket/backups/astro_backup_YYYYMMDD_HHMMSS.sql.gz \
     /var/backups/astro-db/
   ```

6. **Restore database**
   ```bash
   ./scripts/restore-db.sh \
     --backup-file /var/backups/astro-db/astro_backup_YYYYMMDD_HHMMSS.sql.gz \
     --skip-services \
     --confirm
   ```

7. **Run database migrations** (if needed for newer code)
   ```bash
   cd apps/api
   alembic upgrade head
   ```

8. **Start application services**
   ```bash
   docker-compose up -d api celery_worker web
   ```

9. **Verify health**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:5173
   ```

10. **Update DNS** (if server IP changed)
    - Point domain to new server IP
    - Update SSL certificates if needed

**Expected Recovery Time:** 2-4 hours

---

### Scenario 3: Accidental Table/Data Deletion

**Symptoms:**
- User reports missing data
- "Table does not exist" errors
- Empty query results
- Specific user or chart data missing

**Recovery Steps:**

1. **Identify affected data and timeframe**
   - When was the data last known to exist?
   - What specific tables or records are affected?

2. **Find appropriate backup**
   ```bash
   # List backups before the incident
   ls -lh /var/backups/astro-db/astro_backup_20250125_*.sql.gz
   ```

3. **Option A: Restore entire database** (if recent incident)
   ```bash
   ./scripts/restore-db.sh \
     --backup-file /var/backups/astro-db/astro_backup_YYYYMMDD_HHMMSS.sql.gz
   ```

4. **Option B: Restore specific table** (to minimize data loss)
   ```bash
   # Extract specific table from backup
   pg_restore \
     -h localhost \
     -p 5432 \
     -U astro_user \
     -d astro \
     --table=users \
     --data-only \
     /var/backups/astro-db/astro_backup_YYYYMMDD_HHMMSS.sql.gz
   ```

5. **Validate restored data**
   ```bash
   docker exec astro-db-1 psql -U astro_user -d astro -c \
     "SELECT * FROM users WHERE created_at >= 'YYYY-MM-DD'"
   ```

6. **Merge recent changes** (if Option B used)
   - Manually reconcile data created after backup
   - Check audit logs for changes
   - Communicate with users about potential data loss

**Expected Recovery Time:** 30 minutes - 1 hour

---

### Scenario 4: Rollback Failed Migration

**Symptoms:**
- Application fails to start after migration
- "Column does not exist" errors
- Migration errors in logs
- Database schema mismatch

**Recovery Steps:**

1. **Attempt Alembic downgrade first**
   ```bash
   cd apps/api
   alembic downgrade -1  # Rollback last migration
   ```

2. **If downgrade fails, restore pre-migration backup**
   ```bash
   # Pre-migration backups are created automatically if using best practices
   ./scripts/restore-db.sh \
     --backup-file /var/backups/astro-db/pre_migration_YYYYMMDD_HHMMSS.sql.gz
   ```

3. **Fix migration script**
   - Review migration file in `apps/api/alembic/versions/`
   - Fix SQL errors or logic issues
   - Test in development environment first

4. **Re-run migration**
   ```bash
   alembic upgrade head
   ```

5. **Restart services**
   ```bash
   docker-compose restart api celery_worker
   ```

**Best Practice:** Always create a manual backup before migrations:
```bash
BACKUP_NAME="pre_migration_$(date +%Y%m%d_%H%M%S)" ./scripts/backup-db.sh
```

**Expected Recovery Time:** 15-30 minutes

---

### Scenario 5: Qdrant Vector Database Recovery

**Symptoms:**
- RAG (Retrieval-Augmented Generation) not working
- AI interpretations returning generic/no results
- "Collection not found" errors
- Empty search results from vector queries
- Qdrant service unresponsive

**Recovery Steps:**

1. **Check Qdrant health**
   ```bash
   curl http://localhost:6333/healthz
   # Also check collections
   curl http://localhost:6333/collections
   ```

2. **Stop dependent services**
   ```bash
   docker-compose stop api celery_worker
   ```

3. **Option A: Restore from snapshot** (preferred)
   ```bash
   # Find latest snapshot
   ls -lh /var/backups/qdrant/

   # Delete corrupted collection (if exists)
   curl -X DELETE "http://localhost:6333/collections/astrology_knowledge"

   # Wait for deletion
   sleep 2

   # Restore from snapshot
   curl -X POST "http://localhost:6333/collections/astrology_knowledge/snapshots/upload?priority=snapshot" \
       -H "Content-Type: multipart/form-data" \
       -F "snapshot=@/var/backups/qdrant/qdrant_snapshot_YYYYMMDD.snapshot"
   ```

4. **Option B: Download from S3** (if local backup unavailable)
   ```bash
   # Download from S3
   aws s3 cp s3://your-bucket/backups/qdrant/qdrant_snapshot_YYYYMMDD.snapshot \
       /tmp/qdrant_restore.snapshot

   # Restore
   curl -X POST "http://localhost:6333/collections/astrology_knowledge/snapshots/upload?priority=snapshot" \
       -H "Content-Type: multipart/form-data" \
       -F "snapshot=@/tmp/qdrant_restore.snapshot"
   ```

5. **Option C: Regenerate from source** (if no backup available)
   ```bash
   # Re-run the knowledge base ingestion
   cd apps/api
   uv run python scripts/ingest_astrology_knowledge.py
   ```
   Note: This may take significant time depending on document size.

6. **Validate restore**
   ```bash
   # Check collection exists and has vectors
   curl "http://localhost:6333/collections/astrology_knowledge" | jq '.result.points_count'

   # Test a sample search
   curl -X POST "http://localhost:6333/collections/astrology_knowledge/points/search" \
       -H "Content-Type: application/json" \
       -d '{
           "vector": [0.1, 0.2, 0.3, 0.4],
           "limit": 1
       }'
   ```

7. **Restart services**
   ```bash
   docker-compose start api celery_worker
   ```

8. **Verify AI interpretations work**
   - Create a test chart in the application
   - Request AI interpretation
   - Verify results are contextually relevant

**Notes:**
- Qdrant data can be regenerated from source documents if needed
- RAG functionality will be degraded until restore completes
- Snapshots are stored alongside PostgreSQL backups

**Expected Recovery Time:** 15-30 minutes (snapshot restore), 1-4 hours (regeneration)

---

## Testing & Validation

### Automated Restore Tests

Run automated restore tests monthly to verify backup integrity:

```bash
./scripts/test-restore.sh
```

**What the test does:**

**PostgreSQL:**
1. Creates isolated test database
2. Inserts test data
3. Creates backup
4. Modifies data
5. Restores backup
6. Validates data integrity
7. Cleans up test environment

**Qdrant (if available):**
1. Creates test collection with sample vectors
2. Inserts test vectors with payloads
3. Creates snapshot
4. Modifies data (delete/add vectors)
5. Restores from snapshot
6. Validates restored vectors
7. Cleans up test collection

**Expected output:**
```
==========================================
  RESTORE TEST PASSED ✓
==========================================
All tests completed successfully!

Summary - PostgreSQL:
  - Test database created ✓
  - Test data inserted ✓
  - Backup created ✓
  - Data modified ✓
  - Backup restored ✓
  - Data validation passed ✓
  - Cleanup completed ✓

Summary - Qdrant:
  - Test collection created ✓
  - Test vectors inserted ✓
  - Snapshot created ✓
  - Data modified ✓
  - Snapshot restored ✓
  - Data validation passed ✓
  - Cleanup completed ✓
```

### Manual Disaster Recovery Drill

Perform full DR drill quarterly (every 3 months):

1. **Schedule downtime** (or use staging environment)
2. **Simulate complete failure:**
   ```bash
   docker-compose down -v  # Destroy all data
   ```

3. **Follow recovery procedures** for complete server failure

4. **Document:**
   - Actual recovery time
   - Issues encountered
   - Lessons learned
   - Process improvements

5. **Update this document** with findings

### Validation Checklist

After any restore operation, verify:

**PostgreSQL:**
- [ ] Database is accessible
- [ ] All tables exist and have data
- [ ] User authentication works
- [ ] Charts can be created and viewed
- [ ] API endpoints respond correctly
- [ ] Frontend loads properly
- [ ] No errors in application logs
- [ ] Audit logs are intact
- [ ] Background jobs (Celery) are running

**Qdrant:**
- [ ] Qdrant healthcheck passes (`/healthz`)
- [ ] Collections exist and have vectors
- [ ] AI interpretations return relevant results
- [ ] RAG queries complete without timeout
- [ ] No Qdrant-related errors in logs

---

## Emergency Contacts

### On-Call Rotation

| Role | Primary | Backup | Phone | Email |
|------|---------|--------|-------|-------|
| DevOps Lead | [Name] | [Name] | [Phone] | [Email] |
| Backend Lead | [Name] | [Name] | [Phone] | [Email] |
| DBA | [Name] | [Name] | [Phone] | [Email] |
| Security | [Name] | [Name] | [Phone] | [Email] |

### External Vendors

| Vendor | Service | Support Contact | SLA |
|--------|---------|-----------------|-----|
| AWS | Cloud Infrastructure | aws-support@amazon.com | 1-hour response |
| [Hosting Provider] | Server Hosting | support@provider.com | 2-hour response |
| [SSL Provider] | SSL Certificates | support@ssl.com | 24-hour response |

### Escalation Path

1. **Incident Detected** → On-call DevOps engineer
2. **15 minutes** → Escalate to DevOps Lead
3. **30 minutes** → Escalate to CTO
4. **1 hour** → Activate full incident response team

---

## Post-Recovery Checklist

After completing recovery procedures:

### Immediate (0-1 hour)

- [ ] Verify all services are running
- [ ] Run health checks on all endpoints
- [ ] Check application logs for errors
- [ ] Verify user authentication works
- [ ] Test critical user journeys (login, create chart, view chart)
- [ ] Monitor system resources (CPU, memory, disk)
- [ ] Send "all clear" notification to stakeholders

### Short-term (1-24 hours)

- [ ] Monitor error rates in production
- [ ] Review Sentry for new errors
- [ ] Check background job queues
- [ ] Verify email sending works
- [ ] Test OAuth providers (Google, GitHub, Facebook)
- [ ] Run full API test suite
- [ ] Review user complaints/support tickets
- [ ] Document incident timeline

### Long-term (1-7 days)

- [ ] Conduct post-mortem meeting
- [ ] Document root cause analysis
- [ ] Identify process improvements
- [ ] Update this DR document
- [ ] Create tasks for preventive measures
- [ ] Review and update monitoring/alerting
- [ ] Test backup integrity
- [ ] Validate disaster recovery metrics (RTO, RPO)

### Post-Mortem Template

```markdown
# Incident Post-Mortem: [Date]

## Summary
- **Incident:** [Brief description]
- **Impact:** [Users affected, downtime duration]
- **Root Cause:** [What caused the incident]
- **Resolution:** [How it was fixed]

## Timeline
- HH:MM - Incident detected
- HH:MM - Recovery started
- HH:MM - Services restored
- HH:MM - Verification complete

## What Went Well
- [List successes]

## What Went Wrong
- [List failures]

## Action Items
- [ ] [Task 1 - Owner - Deadline]
- [ ] [Task 2 - Owner - Deadline]

## Lessons Learned
- [Key takeaways]
```

---

## Backup Verification Schedule

| Activity | Frequency | Responsible | Last Completed |
|----------|-----------|-------------|----------------|
| Automated restore test | Monthly | CI/CD | [Date] |
| Manual DR drill | Quarterly | DevOps Team | [Date] |
| Backup integrity check | Weekly | DevOps Engineer | [Date] |
| Off-site backup verification | Monthly | DevOps Lead | [Date] |
| DR plan review | Quarterly | DevOps Team | [Date] |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.1.0 | 2025-12-26 | DevOps Team | Added Qdrant backup/restore procedures and testing |
| 1.0.0 | 2025-11-25 | DevOps Team | Initial disaster recovery plan |

---

## References

- Backup Script: `scripts/backup-db.sh`
- Restore Script: `scripts/restore-db.sh`
- Test Script: `scripts/test-restore.sh`
- PostgreSQL Backup Docs: https://www.postgresql.org/docs/16/backup-dump.html
- Qdrant Snapshots: https://qdrant.tech/documentation/concepts/snapshots/
- Issue #7 (Backup Automation): Completed
- Issue #87 (This document): Current
- Issue #208 (Qdrant Testing): Completed

---

## Next Steps

1. **Review this plan** with the team
2. **Schedule first DR drill** (within 30 days)
3. **Set up monitoring alerts** for backup failures
4. **Configure S3 offsite backups** (if not already)
5. **Add DR drill to quarterly calendar**
6. **Train new team members** on DR procedures

---

*This document is a living document and should be updated after each DR drill or significant infrastructure change.*
