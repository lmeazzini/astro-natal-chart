#!/bin/bash
# =============================================================================
# Setup AWS Session Manager Plugin
# =============================================================================
# This script installs the AWS Session Manager plugin required for
# port forwarding to RDS via ECS tasks.
#
# Run with: sudo bash scripts/setup-ssm-plugin.sh
# =============================================================================

set -e

echo "Installing AWS Session Manager Plugin..."

# Detect OS
if [ -f /etc/debian_version ]; then
    # Debian/Ubuntu
    curl -s "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb" -o /tmp/session-manager-plugin.deb
    dpkg -i /tmp/session-manager-plugin.deb
    rm /tmp/session-manager-plugin.deb
elif [ -f /etc/redhat-release ]; then
    # RHEL/CentOS/Amazon Linux
    curl -s "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/linux_64bit/session-manager-plugin.rpm" -o /tmp/session-manager-plugin.rpm
    yum install -y /tmp/session-manager-plugin.rpm
    rm /tmp/session-manager-plugin.rpm
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    curl -s "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/mac/session-manager-plugin.pkg" -o /tmp/session-manager-plugin.pkg
    installer -pkg /tmp/session-manager-plugin.pkg -target /
    rm /tmp/session-manager-plugin.pkg
else
    echo "Unsupported OS. Please install manually from:"
    echo "https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html"
    exit 1
fi

echo ""
echo "Verifying installation..."
session-manager-plugin --version

echo ""
echo "Session Manager Plugin installed successfully!"
echo "You can now use: ./scripts/rds-tunnel.sh"
