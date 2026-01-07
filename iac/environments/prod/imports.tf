# =============================================================================
# Import Existing AWS Secrets Manager Secrets
# =============================================================================
# These secrets were created manually before Terraform management.
# Import blocks allow Terraform to adopt existing resources without destroying them.
# After successful import, these blocks can be removed.
# =============================================================================

import {
  to = module.secrets.aws_secretsmanager_secret.openai[0]
  id = "astro/prod/openai-api-key"
}

import {
  to = module.secrets.aws_secretsmanager_secret.stripe_secret_key[0]
  id = "astro/prod/stripe-secret-key"
}

import {
  to = module.secrets.aws_secretsmanager_secret.stripe_webhook_secret[0]
  id = "astro/prod/stripe-webhook-secret"
}
