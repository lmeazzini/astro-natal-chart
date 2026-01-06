#!/bin/bash
# =============================================================================
# RDS Port Forwarding via AWS Session Manager
# =============================================================================
# Creates a secure tunnel to the production RDS database through an ECS task.
#
# Prerequisites:
#   1. AWS CLI v2 installed
#   2. Session Manager plugin installed (run: sudo bash scripts/setup-ssm-plugin.sh)
#   3. AWS credentials configured (or set AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY)
#
# Usage:
#   ./scripts/rds-tunnel.sh              # Uses default local port 5432
#   ./scripts/rds-tunnel.sh 15432        # Uses custom local port 15432
#
# After running, connect with:
#   psql -h localhost -p 5432 -U astro -d astro
# =============================================================================

set -e

# Configuration
LOCAL_PORT="${1:-5432}"
RDS_HOST="astro-prod-db.ctwuoia0imsd.us-east-2.rds.amazonaws.com"
RDS_PORT="5432"
CLUSTER="astro-prod-cluster"
SERVICE="astro-prod-api"
REGION="us-east-2"

# Load AWS credentials from iac/.env if not set
if [ -z "$AWS_ACCESS_KEY_ID" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    ENV_FILE="$SCRIPT_DIR/../iac/.env"
    if [ -f "$ENV_FILE" ]; then
        echo "Loading AWS credentials from iac/.env..."
        export $(grep -v '^#' "$ENV_FILE" | xargs)
    else
        echo "Error: AWS credentials not found. Set AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY or create iac/.env"
        exit 1
    fi
fi

# Check prerequisites
if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI not installed. Install from https://aws.amazon.com/cli/"
    exit 1
fi

if ! command -v session-manager-plugin &> /dev/null; then
    echo "Error: Session Manager plugin not installed."
    echo "Run: sudo bash scripts/setup-ssm-plugin.sh"
    exit 1
fi

echo "=============================================="
echo "  RDS Port Forwarding via Session Manager"
echo "=============================================="
echo ""
echo "RDS Endpoint: $RDS_HOST"
echo "Local Port:   $LOCAL_PORT"
echo ""

# Get the running task ID
echo "Finding running ECS task..."
TASK_ARN=$(aws ecs list-tasks \
    --cluster "$CLUSTER" \
    --service-name "$SERVICE" \
    --query 'taskArns[0]' \
    --output text \
    --region "$REGION")

if [ "$TASK_ARN" == "None" ] || [ -z "$TASK_ARN" ]; then
    echo "Error: No running tasks found in service $SERVICE"
    exit 1
fi

TASK_ID=$(echo "$TASK_ARN" | awk -F'/' '{print $NF}')
echo "Task ID: $TASK_ID"

# Get the runtime ID for the container
echo "Getting container runtime ID..."
TASK_DETAILS=$(aws ecs describe-tasks \
    --cluster "$CLUSTER" \
    --tasks "$TASK_ID" \
    --query 'tasks[0].containers[?name==`api`].runtimeId' \
    --output text \
    --region "$REGION")

if [ -z "$TASK_DETAILS" ] || [ "$TASK_DETAILS" == "None" ]; then
    echo "Error: Could not get container runtime ID"
    exit 1
fi

RUNTIME_ID="$TASK_DETAILS"
echo "Runtime ID: $RUNTIME_ID"

# Construct the SSM target
TARGET="ecs:${CLUSTER}_${TASK_ID}_${RUNTIME_ID}"
echo ""
echo "SSM Target: $TARGET"
echo ""
echo "=============================================="
echo "  Starting port forwarding..."
echo "  Press Ctrl+C to stop"
echo "=============================================="
echo ""
echo "Connect to the database with:"
echo "  psql -h localhost -p $LOCAL_PORT -U astro_admin -d astro"
echo ""
echo "Or use this connection string (get password from AWS Secrets Manager):"
echo "  postgresql://astro_admin:<password>@localhost:$LOCAL_PORT/astro"
echo ""
echo "To get the password, run:"
echo "  aws secretsmanager get-secret-value --secret-id 'astro/prod/database-url' --query 'SecretString' --output text --region us-east-2"
echo ""

# Start port forwarding
aws ssm start-session \
    --target "$TARGET" \
    --document-name AWS-StartPortForwardingSessionToRemoteHost \
    --parameters "{\"host\":[\"$RDS_HOST\"],\"portNumber\":[\"$RDS_PORT\"],\"localPortNumber\":[\"$LOCAL_PORT\"]}" \
    --region "$REGION"
