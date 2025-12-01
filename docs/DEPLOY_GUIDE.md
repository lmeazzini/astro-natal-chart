# Deployment Guide - Real Astrology

Complete guide for deploying the Real Astrology application to AWS EC2 with automatic CD pipeline.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Initial EC2 Setup](#initial-ec2-setup)
4. [Environment Configuration](#environment-configuration)
5. [SSL Certificate Setup](#ssl-certificate-setup)
6. [First Manual Deployment](#first-manual-deployment)
7. [GitHub Actions Configuration](#github-actions-configuration)
8. [Automatic Deployments](#automatic-deployments)
9. [Monitoring and Logs](#monitoring-and-logs)
10. [Rollback Procedures](#rollback-procedures)
11. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### Production Stack

```
┌─────────────────────────────────────────────────┐
│            AWS EC2 Instance (Ubuntu)            │
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │         Docker Compose Production         │ │
│  │                                           │ │
│  │  ┌─────────────┐  ┌──────────────────┐  │ │
│  │  │ PostgreSQL  │  │      Redis       │  │ │
│  │  │     16      │  │        7         │  │ │
│  │  └─────────────┘  └──────────────────┘  │ │
│  │                                           │ │
│  │  ┌─────────────┐  ┌──────────────────┐  │ │
│  │  │  FastAPI    │  │  Celery Worker   │  │ │
│  │  │  (4 workers)│  │  (2 concurrency) │  │ │
│  │  └─────────────┘  └──────────────────┘  │ │
│  │                                           │ │
│  │  ┌─────────────┐  ┌──────────────────┐  │ │
│  │  │   Qdrant    │  │   React/Vite     │  │ │
│  │  │    (RAG)    │  │   (Frontend)     │  │ │
│  │  └─────────────┘  └──────────────────┘  │ │
│  │                                           │ │
│  │  ┌──────────────────────────────────────┐│ │
│  │  │  Nginx (Reverse Proxy + SSL/TLS)    ││ │
│  │  │  + Certbot (Let's Encrypt)          ││ │
│  │  └──────────────────────────────────────┘│ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  Ports: 80 (HTTP), 443 (HTTPS), 22 (SSH)      │
└─────────────────────────────────────────────────┘
                      ▲
                      │
                      │ SSH Deploy
                      │
┌─────────────────────────────────────────────────┐
│          GitHub Actions (CI/CD)                 │
│                                                 │
│  Triggers:                                      │
│    - Push to main branch                        │
│    - Manual workflow dispatch                   │
│                                                 │
│  Steps:                                         │
│    1. SSH to EC2                                │
│    2. Run deployment script                     │
│    3. Health check validation                   │
│    4. Auto-rollback on failure                  │
└─────────────────────────────────────────────────┘
```

### Deployment Flow

```
┌──────────────┐
│ Developer    │
│ git push     │
│ origin main  │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│ GitHub Actions Triggered             │
│ (.github/workflows/deploy.yml)       │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ SSH to EC2 Instance                  │
│ Execute: scripts/deploy.sh           │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Deployment Script Steps:             │
│                                      │
│ 1. ✅ Pre-deployment checks          │
│    - Docker running?                 │
│    - .env files exist?               │
│    - Disk space >5GB?                │
│                                      │
│ 2. 🏷️  Tag current images            │
│    - astro-api-prod:rollback         │
│    - astro-web-prod:rollback         │
│                                      │
│ 3. 📦 Build new images               │
│    - git pull origin main            │
│    - docker compose build            │
│                                      │
│ 4. 🗄️  Run migrations                │
│    - Check for recent backup         │
│    - alembic upgrade head            │
│                                      │
│ 5. 🔄 Restart services               │
│    - docker compose up -d            │
│    - nginx reload                    │
│                                      │
│ 6. 🏥 Health check (30 retries)      │
│    - curl http://localhost/health    │
│                                      │
│ 7. ✅ Success OR ❌ Rollback          │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ If Success:                          │
│   - ✅ Cleanup old images            │
│   - ✅ Deployment complete           │
│                                      │
│ If Failure:                          │
│   - 🔄 Automatic rollback            │
│   - ❌ Deploy failed (exit 1)        │
└──────────────────────────────────────┘
```

---

## Prerequisites

### AWS Requirements

- ✅ EC2 instance running Ubuntu 22.04 LTS or newer
- ✅ Elastic IP allocated and associated with EC2
- ✅ Security Group configured:
  - Port 22 (SSH) - Your IP only
  - Port 80 (HTTP) - 0.0.0.0/0
  - Port 443 (HTTPS) - 0.0.0.0/0
- ✅ SSH key pair for instance access
- ✅ IAM credentials for S3 (backups and PDF storage)

### Domain Requirements

- ✅ Domain name registered (e.g., realastrology.ai)
- ✅ DNS configured:
  - A record: `@` → EC2 Elastic IP
  - A record: `www` → EC2 Elastic IP

### GitHub Requirements

- ✅ Repository with main branch
- ✅ GitHub Actions enabled
- ✅ SSH private key for EC2 access

---

## Initial EC2 Setup

### 1. Connect to EC2 Instance

```bash
# Using SSH key
ssh -i /path/to/your-key.pem ubuntu@<your-elastic-ip>

# Or if using key added to ssh-agent
ssh ubuntu@<your-elastic-ip>
```

### 2. Run Setup Script

```bash
# Download setup script
curl -fsSL https://raw.githubusercontent.com/lmeazzini/astro-natal-chart/main/scripts/setup-ec2.sh -o setup-ec2.sh

# Make executable
chmod +x setup-ec2.sh

# Run setup
bash setup-ec2.sh
```

The script will:
- ✅ Update system packages
- ✅ Install Docker and Docker Compose
- ✅ Install Git, Make, and utilities
- ✅ Create application directory at `/opt/astro-natal-chart`
- ✅ Clone repository
- ✅ Create required directories
- ✅ Set up environment file templates

### 3. Activate Docker Group

```bash
# Activate docker group without logout
newgrp docker

# Verify Docker works without sudo
docker ps
```

---

## Environment Configuration

### Backend Environment (`apps/api/.env`)

```bash
cd /opt/astro-natal-chart
nano apps/api/.env
```

**Critical variables to configure:**

```bash
# Domain
DOMAIN=realastrology.ai

# Security (NEVER use defaults in production!)
SECRET_KEY=<generate-with-openssl-rand-hex-32>
POSTGRES_PASSWORD=<strong-random-password>
REDIS_PASSWORD=<strong-random-password>

# Database
DATABASE_URL=postgresql+asyncpg://postgres:${POSTGRES_PASSWORD}@db:5432/astro_natal

# CORS
ALLOWED_ORIGINS=https://realastrology.ai,https://www.realastrology.ai

# AWS S3 (Backups and PDFs)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<your-aws-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret>
S3_BUCKET_NAME=<your-bucket-name>
S3_PREFIX=birth-charts

# OAuth2 Providers (optional but recommended)
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-secret>
GITHUB_CLIENT_ID=<your-github-client-id>
GITHUB_CLIENT_SECRET=<your-github-secret>
FACEBOOK_CLIENT_ID=<your-facebook-client-id>
FACEBOOK_CLIENT_SECRET=<your-facebook-secret>

# OpenAI (optional - for AI interpretations)
OPENAI_API_KEY=sk-proj-...

# Email (optional - for password reset, etc.)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=<your-gmail>
SMTP_PASSWORD=<app-specific-password>
SMTP_FROM=noreply@realastrology.ai

# Geocoding
OPENCAGE_API_KEY=<your-opencage-key>
```

**Generate secure passwords:**

```bash
# SECRET_KEY
openssl rand -hex 32

# PostgreSQL password
openssl rand -base64 32

# Redis password
openssl rand -base64 32
```

### Frontend Environment (`apps/web/.env`)

```bash
nano apps/web/.env
```

```bash
# API URL (production)
VITE_API_URL=https://realastrology.ai

# Google OAuth (if using)
VITE_GOOGLE_CLIENT_ID=<your-google-client-id>
```

---

## SSL Certificate Setup

### Option 1: Automated Setup (Recommended)

```bash
cd /opt/astro-natal-chart

# Run SSL setup script
bash scripts/setup-ssl.sh
```

### Option 2: Manual Setup

```bash
cd /opt/astro-natal-chart

# Start Nginx
docker compose -f docker-compose.prod.yml up -d nginx

# Request certificate
docker compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email \
  -d realastrology.ai \
  -d www.realastrology.ai

# Restart Nginx to load certificate
docker compose -f docker-compose.prod.yml restart nginx
```

### SSL Certificate Renewal

Certbot automatically renews certificates. Verify auto-renewal:

```bash
# Test renewal
docker compose -f docker-compose.prod.yml run --rm certbot renew --dry-run

# Renewal runs automatically via cron (configured in certbot container)
```

---

## First Manual Deployment

Before enabling automatic deployments, do a manual deployment to verify everything works.

### 1. Build Docker Images

```bash
cd /opt/astro-natal-chart

# Build images (first build takes 5-10 minutes)
docker compose -f docker-compose.prod.yml build
```

### 2. Start Services

```bash
# Start all services
docker compose -f docker-compose.prod.yml up -d

# Check status
docker compose -f docker-compose.prod.yml ps
```

Expected output:
```
NAME                    STATUS              PORTS
astro-db                Up 30 seconds       5432/tcp
astro-redis             Up 30 seconds       6379/tcp
astro-qdrant            Up 30 seconds       6333/tcp, 6334/tcp
astro-api               Up 20 seconds       8000/tcp
astro-celery-worker     Up 20 seconds
astro-web               Up 15 seconds       5173/tcp
astro-nginx             Up 10 seconds       0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
```

### 3. Run Database Migrations

```bash
# Apply all 27 migrations
docker compose -f docker-compose.prod.yml exec api uv run alembic upgrade head
```

### 4. Verify Deployment

```bash
# Check health endpoint
curl http://localhost/health

# Expected response:
# {"status":"ok","timestamp":"2025-01-20T15:30:45.123Z"}

# Check HTTPS
curl https://realastrology.ai/health
```

### 5. View Logs

```bash
# All services
docker compose -f docker-compose.prod.yml logs

# Specific service
docker compose -f docker-compose.prod.yml logs api
docker compose -f docker-compose.prod.yml logs nginx

# Follow logs
docker compose -f docker-compose.prod.yml logs -f api
```

---

## GitHub Actions Configuration

### 1. Add SSH Private Key to GitHub Secrets

```bash
# On your local machine, copy SSH private key
cat ~/.ssh/your-ec2-key.pem

# Copy the entire content (including BEGIN/END lines)
```

### 2. Configure GitHub Secrets

Go to GitHub Repository → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `EC2_HOST` | Your Elastic IP | `54.123.456.789` |
| `EC2_USER` | SSH username | `ubuntu` |
| `EC2_SSH_KEY` | Complete private key | `<paste entire content of your .pem file>` |
| `DOMAIN` | Your domain | `realastrology.ai` |

### 3. Verify Workflow File

The workflow file is already created at `.github/workflows/deploy.yml`. Verify it exists:

```bash
cat .github/workflows/deploy.yml
```

---

## Automatic Deployments

### How It Works

Once configured, deployments happen automatically:

1. **Developer pushes to main:**
   ```bash
   git push origin main
   ```

2. **GitHub Actions triggers** (within seconds)

3. **Deployment script runs** on EC2:
   - Pre-deployment checks
   - Tag current images (rollback point)
   - Pull latest code
   - Build new images
   - Run migrations
   - Restart services
   - Health check (30 retries, 2s interval)
   - Auto-rollback if health check fails

4. **Deployment completes** (5-10 minutes total)

### Manual Deployment Trigger

You can also trigger deployments manually:

1. Go to GitHub → Actions → Deploy to Production
2. Click "Run workflow"
3. Select branch: `main`
4. Click "Run workflow"

### Deployment Status

Monitor deployment status:

1. **GitHub Actions UI:**
   - Go to repository → Actions
   - Click on the running workflow
   - View real-time logs

2. **SSH to EC2:**
   ```bash
   ssh ubuntu@<elastic-ip>
   docker compose -f /opt/astro-natal-chart/docker-compose.prod.yml logs -f
   ```

---

## Monitoring and Logs

### Application Logs

```bash
cd /opt/astro-natal-chart

# All services
docker compose -f docker-compose.prod.yml logs

# Follow logs (live)
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker-compose.prod.yml logs api
docker compose -f docker-compose.prod.yml logs celery_worker
docker compose -f docker-compose.prod.yml logs nginx

# Last 100 lines
docker compose -f docker-compose.prod.yml logs --tail=100

# Search logs
docker compose -f docker-compose.prod.yml logs | grep ERROR
```

### Container Status

```bash
# List containers
docker compose -f docker-compose.prod.yml ps

# Resource usage
docker stats

# Inspect container
docker compose -f docker-compose.prod.yml exec api bash
```

### Database Access

```bash
# Connect to PostgreSQL
docker compose -f docker-compose.prod.yml exec db psql -U postgres -d astro_natal

# Common queries
\dt                                    # List tables
SELECT COUNT(*) FROM users;            # Count users
SELECT COUNT(*) FROM birth_charts;     # Count charts
\q                                     # Quit
```

### System Resources

```bash
# Disk usage
df -h

# Memory usage
free -h

# CPU and processes
htop
```

---

## Rollback Procedures

### Automatic Rollback

Automatic rollback happens if health check fails after deployment. No manual intervention needed.

### Manual Rollback

If you need to manually revert to a previous version:

```bash
cd /opt/astro-natal-chart

# Run rollback script
bash scripts/rollback.sh
```

The script will:
1. Show recent commits
2. Ask which commit to rollback to
3. Stop services
4. Checkout target commit
5. Rebuild images
6. Start services
7. Verify health

**Example rollback session:**

```
Recent commits (last 10):
a1b2c3d Fix critical bug in chart calculation
e4f5g6h Add new feature for aspects
...

Enter the commit hash to rollback to: e4f5g6h

Target commit: e4f5g6h - Add new feature for aspects

Are you absolutely sure? Type 'ROLLBACK' to continue: ROLLBACK

Starting Rollback Process...
✅ Rollback successful!
```

### Rollback from Specific Commit

```bash
# Rollback to previous commit
bash scripts/rollback.sh
# Press Enter when asked for commit (uses HEAD~1)

# Rollback to specific commit
bash scripts/rollback.sh
# Enter commit hash when prompted
```

---

## Troubleshooting

### Deployment Fails with "Health Check Failed"

**Symptoms:** Deployment fails, automatic rollback occurs

**Check:**
```bash
# View API logs
docker compose -f docker-compose.prod.yml logs api

# Common issues:
# - Database migration failed
# - Missing environment variables
# - Port conflicts
```

**Solution:**
```bash
# Fix the issue, then redeploy
git commit -m "fix: resolve health check issue"
git push origin main
```

### SSL Certificate Not Working

**Symptoms:** HTTPS not working, browser shows "Not Secure"

**Check:**
```bash
# Check certificate files
docker compose -f docker-compose.prod.yml exec nginx ls -la /etc/letsencrypt/live/realastrology.ai/

# Check Nginx logs
docker compose -f docker-compose.prod.yml logs nginx
```

**Solution:**
```bash
# Re-request certificate
docker compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@example.com \
  --agree-tos \
  --force-renewal \
  -d realastrology.ai \
  -d www.realastrology.ai

# Restart Nginx
docker compose -f docker-compose.prod.yml restart nginx
```

### Database Migration Failed

**Symptoms:** Deployment fails at migration step

**Check:**
```bash
# Check migration status
docker compose -f docker-compose.prod.yml exec api uv run alembic current

# Check migration logs
docker compose -f docker-compose.prod.yml logs api | grep alembic
```

**Solution:**
```bash
# Try manual migration with verbose output
docker compose -f docker-compose.prod.yml exec api uv run alembic upgrade head --verbose

# If migration is stuck, check database
docker compose -f docker-compose.prod.yml exec db psql -U postgres -d astro_natal -c "SELECT * FROM alembic_version;"
```

### Services Not Starting

**Symptoms:** Containers exit immediately or restart loop

**Check:**
```bash
# Check container status
docker compose -f docker-compose.prod.yml ps

# Check logs for specific service
docker compose -f docker-compose.prod.yml logs <service-name>

# Check resource usage
docker stats
df -h
```

**Solution:**
```bash
# Restart services
docker compose -f docker-compose.prod.yml restart

# Full reboot (stops and starts everything)
bash scripts/reboot.sh

# If persists, rebuild images
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

### GitHub Actions SSH Connection Failed

**Symptoms:** Deploy workflow fails at SSH step

**Check:**
- ✅ EC2_HOST secret is correct Elastic IP
- ✅ EC2_USER secret is `ubuntu`
- ✅ EC2_SSH_KEY secret contains complete private key (with newlines)
- ✅ Security Group allows SSH from GitHub Actions IPs

**Solution:**
```bash
# Verify secrets are correct
# Re-add EC2_SSH_KEY with proper formatting

# Test SSH manually from local machine
ssh -i your-key.pem ubuntu@<elastic-ip>
```

### Out of Disk Space

**Symptoms:** Deployment fails with "no space left on device"

**Check:**
```bash
df -h
docker system df
```

**Solution:**
```bash
# Clean up Docker resources
docker system prune -a --volumes

# Remove old images
docker image prune -a

# Remove old logs
sudo find /var/lib/docker/containers -name "*.log" -delete

# Increase EBS volume size (if needed)
```

### Database Connection Errors

**Symptoms:** API can't connect to database

**Check:**
```bash
# Check database container
docker compose -f docker-compose.prod.yml ps db

# Check database logs
docker compose -f docker-compose.prod.yml logs db

# Check DATABASE_URL in .env
cat apps/api/.env | grep DATABASE_URL
```

**Solution:**
```bash
# Restart database
docker compose -f docker-compose.prod.yml restart db

# Verify connection
docker compose -f docker-compose.prod.yml exec api python -c "from app.core.database import engine; import asyncio; asyncio.run(engine.connect())"
```

---

## Backup and Recovery

### Automated Backups

Backups run daily at 3 AM via cron (configured in docker-compose.prod.yml):

```bash
# Check backup status
ls -lh /opt/astro-natal-chart/backups/

# Manual backup
bash scripts/backup-db.sh
```

### Restore from Backup

```bash
# List backups
ls -lh backups/

# Restore specific backup
gunzip -c backups/backup-20250120-030000.sql.gz | \
  docker compose -f docker-compose.prod.yml exec -T db psql -U postgres -d astro_natal
```

### Disaster Recovery

See issue #87 for full disaster recovery procedures.

---

## Performance Tuning

### Database Optimization

```bash
# Vacuum database
docker compose -f docker-compose.prod.yml exec db psql -U postgres -d astro_natal -c "VACUUM ANALYZE;"

# Check database size
docker compose -f docker-compose.prod.yml exec db psql -U postgres -d astro_natal -c "
  SELECT pg_size_pretty(pg_database_size('astro_natal'));"
```

### Monitoring Resources

```bash
# Container resource limits (configured in docker-compose.prod.yml)
docker compose -f docker-compose.prod.yml config | grep -A5 resources

# Real-time monitoring
docker stats
```

---

## Security Checklist

- ✅ Strong passwords for PostgreSQL and Redis
- ✅ SECRET_KEY is cryptographically random (32+ bytes)
- ✅ CORS configured with specific origins (no wildcards)
- ✅ Firewall rules configured (only 22, 80, 443 open)
- ✅ SSH key-based authentication (no password login)
- ✅ SSL/TLS certificates configured
- ✅ .env files never committed to git
- ✅ Automated backups enabled
- ✅ Security Group restricts SSH to your IP only
- ✅ IAM credentials have minimal required permissions

---

## Additional Resources

- **Project Documentation:** `/docs/`
- **API Documentation:** `https://realastrology.ai/docs`
- **Issue Tracker:** GitHub Issues
- **CI/CD Configuration:** `.github/workflows/`

---

## Support and Maintenance

### Regular Maintenance Tasks

**Daily:**
- ✅ Automated backups (3 AM)
- ✅ Check application health

**Weekly:**
- ✅ Review error logs
- ✅ Check disk space
- ✅ Verify backup integrity

**Monthly:**
- ✅ Update system packages
- ✅ Review security updates
- ✅ Test rollback procedures
- ✅ Verify SSL certificate auto-renewal

### Updating Dependencies

```bash
# Backend (Python)
cd apps/api
uv lock --upgrade
git commit -m "chore: update Python dependencies"

# Frontend (Node.js)
cd apps/web
npm update
git commit -m "chore: update Node dependencies"

# Push to trigger deployment
git push origin main
```

---

## Summary

You now have a complete CD pipeline for automatic deployment to EC2! 🎉

**Key Features:**
- ✅ Automatic deployment on push to main
- ✅ Health check validation
- ✅ Automatic rollback on failure
- ✅ Manual rollback capability
- ✅ SSL/TLS with Let's Encrypt
- ✅ Comprehensive logging
- ✅ Automated backups

**Deployment Time:** 5-10 minutes
**Downtime:** 10-15 seconds (acceptable for Phase 1)

For questions or issues, refer to the troubleshooting section or check GitHub Issues.
