#!/bin/bash
# =============================================================================
# Terraform Backend Initialization Script
# =============================================================================
# This script loads AWS credentials from .env and exports them for Terraform.
#
# Usage:
#   source scripts/init-backend.sh
#   terraform init
#   terraform plan
# =============================================================================

set -e

# Find the iac directory (works from any subdirectory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IAC_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$IAC_DIR/.env"

# Check if .env exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env file not found at $ENV_FILE"
    echo ""
    echo "Create it from the example:"
    echo "  cp $IAC_DIR/.env.example $ENV_FILE"
    echo "  # Edit $ENV_FILE with your AWS credentials"
    return 1 2>/dev/null || exit 1
fi

# Load environment variables
echo "Loading AWS credentials from $ENV_FILE..."
set -a
source "$ENV_FILE"
set +a

# Validate required variables
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ "$AWS_ACCESS_KEY_ID" = "your-access-key-id" ]; then
    echo "Error: AWS_ACCESS_KEY_ID is not set or still has placeholder value"
    return 1 2>/dev/null || exit 1
fi

if [ -z "$AWS_SECRET_ACCESS_KEY" ] || [ "$AWS_SECRET_ACCESS_KEY" = "your-secret-access-key" ]; then
    echo "Error: AWS_SECRET_ACCESS_KEY is not set or still has placeholder value"
    return 1 2>/dev/null || exit 1
fi

# Export for Terraform
export AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY
export AWS_REGION="${AWS_REGION:-us-east-1}"

echo "AWS credentials loaded successfully!"
echo "  Region: $AWS_REGION"
echo "  Access Key: ${AWS_ACCESS_KEY_ID:0:4}...${AWS_ACCESS_KEY_ID: -4}"
echo ""
echo "You can now run Terraform commands:"
echo "  terraform init"
echo "  terraform plan"
echo "  terraform apply"
