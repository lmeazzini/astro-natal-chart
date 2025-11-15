# Production Deployment Checklist

Complete guide for deploying Astro Natal Chart API to production with HTTPS.

## Pre-Deployment Checklist

### 1. Server Requirements

- [ ] Server with Docker and Docker Compose installed
- [ ] Domain name configured and DNS pointing to server IP
- [ ] Ports 80 (HTTP) and 443 (HTTPS) open in firewall
- [ ] At least 2GB RAM and 20GB storage
- [ ] SSH access to server

### 2. Environment Configuration

- [ ] Copy `.env.prod.example` to `.env.prod`
- [ ] Update domain in `.env.prod`: `DOMAIN=yourdomain.com`
- [ ] Generate strong passwords for PostgreSQL and Redis
- [ ] Copy `apps/api/.env.production.example` to `apps/api/.env`
- [ ] Update all secrets in `apps/api/.env`:
  - SECRET_KEY (use `openssl rand -hex 32`)
  - POSTGRES_PASSWORD
  - REDIS_PASSWORD
  - OPENAI_API_KEY
  - OAuth2 credentials (if using)
- [ ] Update ALLOWED_ORIGINS with your domain
- [ ] Set COOKIE_SECURE=true
- [ ] Set COOKIE_DOMAIN=yourdomain.com

### 3. Code Preparation

- [ ] All tests passing: `npm run test`
- [ ] No linting errors: `npm run lint`
- [ ] Build frontend: `cd apps/web && npm run build`
- [ ] Verify production Dockerfile exists: `apps/api/Dockerfile` (target: production)

## Deployment Steps

### Step 1: Upload to Server

```bash
# From local machine
rsync -avz --exclude 'node_modules' --exclude '.git' \
  . user@yourserver:/opt/astro-natal-chart/
```

### Step 2: Setup SSL Certificates

```bash
# On server
cd /opt/astro-natal-chart

# Run SSL setup (this will obtain Let's Encrypt certificates)
./scripts/setup-ssl.sh yourdomain.com admin@yourdomain.com
```

Expected output:
- ✅ Nginx started
- ✅ SSL certificate obtained
- ✅ HTTPS enabled
- ✅ Renewal test passed

### Step 3: Start Production Stack

```bash
# Build and start all services
docker compose -f docker-compose.prod.yml up -d --build

# Check all containers are running
docker compose -f docker-compose.prod.yml ps
```

Expected containers:
- astro-db-prod (postgres:16-alpine)
- astro-redis-prod (redis:7-alpine)
- astro-api-prod (custom build)
- astro-celery-prod (custom build)
- astro-nginx-prod (nginx:alpine)
- astro-certbot (certbot/certbot)

### Step 4: Run Database Migrations

```bash
# Apply migrations
docker compose -f docker-compose.prod.yml exec api alembic upgrade head

# Verify database
docker compose -f docker-compose.prod.yml exec api python -c "from app.core.database import engine; print('DB OK')"
```

### Step 5: Verify Deployment

#### 5.1 Test HTTPS

```bash
# Should redirect to HTTPS
curl -I http://yourdomain.com

# Should return 200 OK
curl -I https://yourdomain.com

# Check API health
curl https://yourdomain.com/api/v1/health
```

Expected:
```json
{
  "status": "healthy",
  "environment": "production"
}
```

#### 5.2 Test Security Headers

```bash
curl -I https://yourdomain.com | grep -E "(Strict-Transport|X-Frame|Content-Security)"
```

Expected headers:
- ✅ Strict-Transport-Security
- ✅ X-Frame-Options
- ✅ X-Content-Type-Options
- ✅ Content-Security-Policy

#### 5.3 Test API Endpoints

```bash
# API documentation should be accessible
curl https://yourdomain.com/docs

# Test CORS (from your frontend domain)
curl -X OPTIONS https://yourdomain.com/api/v1/health \
  -H "Origin: https://yourdomain.com" \
  -H "Access-Control-Request-Method: GET"
```

### Step 6: Security Validation

Run external security tests:

1. **SSL Labs Test**
   - Visit: https://www.ssllabs.com/ssltest/analyze.html?d=yourdomain.com
   - Target: A or A+ rating

2. **Security Headers Test**
   - Visit: https://securityheaders.com/?q=https://yourdomain.com
   - Target: A rating

3. **Mozilla Observatory**
   - Visit: https://observatory.mozilla.org/analyze/yourdomain.com
   - Target: 80+ score

## Post-Deployment

### Monitoring

Set up monitoring for:
- [ ] SSL certificate expiration (auto-renewed at < 30 days)
- [ ] Server resources (CPU, RAM, disk)
- [ ] Application logs
- [ ] Error rates

### Logging

```bash
# View all logs
docker compose -f docker-compose.prod.yml logs -f

# View API logs only
docker compose -f docker-compose.prod.yml logs -f api

# View nginx logs
docker compose -f docker-compose.prod.yml logs -f nginx

# View certbot logs (renewal)
docker compose -f docker-compose.prod.yml logs certbot
```

### Certificate Renewal

Certificates are auto-renewed every 12 hours. To manually renew:

```bash
# Dry run (test)
./scripts/renew-ssl.sh --dry-run

# Actual renewal
./scripts/renew-ssl.sh
```

### Backup Strategy

- [ ] Database backups: Daily exports of PostgreSQL
- [ ] Code backups: Git repository
- [ ] SSL certificates: Backed up in certbot/conf (git-ignored)
- [ ] Environment files: Secure storage (NOT in git)

### Updates and Maintenance

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker compose -f docker-compose.prod.yml up -d --build

# Run new migrations
docker compose -f docker-compose.prod.yml exec api alembic upgrade head
```

## Troubleshooting

### Issue: SSL Certificate Not Obtained

**Symptoms**: setup-ssl.sh fails with certificate error

**Solutions**:
1. Verify DNS is pointing to server: `dig yourdomain.com`
2. Check ports 80 and 443 are open: `netstat -tlnp | grep -E ':(80|443)'`
3. Try staging mode first: `./scripts/setup-ssl.sh yourdomain.com email staging`
4. Check certbot logs: `docker compose logs certbot`

### Issue: 502 Bad Gateway

**Symptoms**: Nginx returns 502 error

**Solutions**:
1. Check API is running: `docker compose ps api`
2. Check API logs: `docker compose logs api`
3. Verify database connection: Check DATABASE_URL
4. Restart API: `docker compose restart api`

### Issue: CORS Errors

**Symptoms**: Frontend can't connect to API

**Solutions**:
1. Verify ALLOWED_ORIGINS in apps/api/.env
2. Check frontend domain is in the list
3. Restart API: `docker compose restart api`

### Issue: Database Connection Failed

**Symptoms**: API can't connect to database

**Solutions**:
1. Check PostgreSQL is running: `docker compose ps db`
2. Verify DATABASE_URL format: `postgresql+asyncpg://user:pass@db:5432/dbname`
3. Check credentials match .env.prod
4. View database logs: `docker compose logs db`

## Security Best Practices

- [ ] Change all default passwords
- [ ] Enable firewall (ufw) and allow only 22, 80, 443
- [ ] Set up fail2ban for SSH protection
- [ ] Regular security updates: `apt update && apt upgrade`
- [ ] Monitor access logs for suspicious activity
- [ ] Use environment-specific secrets (never reuse dev secrets)
- [ ] Rotate secrets periodically (every 90 days)

## Rollback Procedure

If deployment fails:

```bash
# Stop new version
docker compose -f docker-compose.prod.yml down

# Revert to previous git commit
git checkout <previous-commit>

# Restart
docker compose -f docker-compose.prod.yml up -d
```

## Support Resources

- FastAPI Documentation: https://fastapi.tiangolo.com/
- Nginx Documentation: https://nginx.org/en/docs/
- Let's Encrypt Documentation: https://letsencrypt.org/docs/
- Docker Compose Documentation: https://docs.docker.com/compose/

---

**Last Updated**: 2025-11-15
**Deployment Status**: ⏳ Pending first production deployment
