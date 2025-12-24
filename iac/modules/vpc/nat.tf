# =============================================================================
# VPC Module - NAT Gateway
# =============================================================================
# Creates NAT Gateway and Elastic IP for private subnet internet access.
# Can be disabled to save ~$32/month in non-production environments.
#
# Cost breakdown:
#   - NAT Gateway: ~$32/month (hourly charge)
#   - Elastic IP:  ~$3.60/month (if NAT is disabled but EIP kept)
#   - Data processing: $0.045/GB
# =============================================================================

# -----------------------------------------------------------------------------
# Elastic IP for NAT Gateway
# -----------------------------------------------------------------------------

resource "aws_eip" "nat" {
  count  = var.enable_nat_gateway ? 1 : 0
  domain = "vpc"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-nat-eip"
  })

  depends_on = [aws_internet_gateway.main]
}

# -----------------------------------------------------------------------------
# NAT Gateway
# -----------------------------------------------------------------------------

resource "aws_nat_gateway" "main" {
  count             = var.enable_nat_gateway ? 1 : 0
  allocation_id     = aws_eip.nat[0].id
  subnet_id         = aws_subnet.public.id
  connectivity_type = "public"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-nat"
  })

  depends_on = [aws_internet_gateway.main]
}

# -----------------------------------------------------------------------------
# Private Route to NAT Gateway
# -----------------------------------------------------------------------------
# Add route to NAT Gateway in the private route table when NAT is enabled.
# This allows ECS tasks to pull images and access external APIs.

resource "aws_route" "private_nat" {
  count                  = var.enable_nat_gateway ? 1 : 0
  route_table_id         = aws_route_table.private.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.main[0].id
}
