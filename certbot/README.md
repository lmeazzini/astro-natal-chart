# Certbot - SSL Certificates

This directory stores SSL/TLS certificates obtained from Let's Encrypt via Certbot.

## Directory Structure

```
certbot/
├── conf/           # Let's Encrypt configuration and certificates
│   └── live/       # Symbolic links to current certificates
│       └── yourdomain.com/
│           ├── fullchain.pem  # Full certificate chain
│           ├── privkey.pem    # Private key
│           └── chain.pem      # Intermediate certificates
└── www/            # ACME challenge files (for domain verification)
    └── .well-known/acme-challenge/
```

## Security Note

**⚠️ IMPORTANT**: The contents of this directory contain sensitive cryptographic material:
- Private keys
- SSL certificates
- Let's Encrypt account information

These files are automatically ignored by git (see `.gitignore`) and should **NEVER** be committed to version control.

## Obtaining Certificates

To obtain SSL certificates, run the setup script:

```bash
./scripts/setup-ssl.sh yourdomain.com admin@yourdomain.com
```

For testing (staging certificates):
```bash
./scripts/setup-ssl.sh yourdomain.com admin@yourdomain.com staging
```

## Certificate Renewal

Certificates are automatically renewed every 12 hours by the `certbot` Docker container.

To manually renew:
```bash
./scripts/renew-ssl.sh
```

To test renewal (dry-run):
```bash
./scripts/renew-ssl.sh --dry-run
```

## Checking Certificate Status

View certificate details:
```bash
docker compose -f docker-compose.prod.yml run --rm certbot certificates
```

## Certificate Expiration

- Let's Encrypt certificates are valid for **90 days**
- Auto-renewal happens when **< 30 days** remaining
- Certbot runs renewal check every **12 hours**

## Troubleshooting

If certificates fail to renew:

1. Check certbot logs:
   ```bash
   docker compose -f docker-compose.prod.yml logs certbot
   ```

2. Verify domain DNS points to your server
3. Ensure ports 80 and 443 are accessible
4. Check nginx is serving ACME challenge correctly:
   ```bash
   curl http://yourdomain.com/.well-known/acme-challenge/test
   ```

## References

- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Certbot Documentation](https://certbot.eff.org/docs/)
