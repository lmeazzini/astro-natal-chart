# =============================================================================
# VPC Module - Main Resources
# =============================================================================
# Creates VPC, subnets, Internet Gateway, and route tables.
# Single AZ architecture for cost optimization.
#
# Architecture:
#   ┌─────────────────────────────────────────────────────────────┐
#   │                        VPC (10.0.0.0/16)                    │
#   │                                                             │
#   │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
#   │  │  Public Subnet  │  │ Private Subnet  │  │  Database   │ │
#   │  │  10.0.1.0/24    │  │  10.0.11.0/24   │  │ 10.0.21.0/24│ │
#   │  │                 │  │                 │  │             │ │
#   │  │  - ALB          │  │  - ECS Tasks    │  │  - RDS      │ │
#   │  │  - NAT Gateway  │  │                 │  │  - Redis    │ │
#   │  └────────┬────────┘  └────────┬────────┘  └─────────────┘ │
#   │           │                    │                            │
#   │           ▼                    ▼                            │
#   │     Internet GW           NAT Gateway                       │
#   │           │                    │                            │
#   └───────────┼────────────────────┼────────────────────────────┘
#               │                    │
#               ▼                    │
#           Internet ◄───────────────┘
# =============================================================================

# -----------------------------------------------------------------------------
# Local Variables
# -----------------------------------------------------------------------------

locals {
  name_prefix = "astro-${var.environment}"

  common_tags = merge(var.tags, {
    Module = "vpc"
  })
}

# -----------------------------------------------------------------------------
# VPC
# -----------------------------------------------------------------------------

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = var.enable_dns_hostnames
  enable_dns_support   = var.enable_dns_support

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-vpc"
  })
}

# -----------------------------------------------------------------------------
# Internet Gateway
# -----------------------------------------------------------------------------

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-igw"
  })
}

# -----------------------------------------------------------------------------
# Subnets
# -----------------------------------------------------------------------------

# Public Subnet - For ALB and NAT Gateway (Primary AZ)
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidr
  availability_zone       = var.availability_zone
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-public-subnet"
    Tier = "public"
  })
}

# Public Subnet Secondary - Required by ALB (Secondary AZ)
resource "aws_subnet" "public_secondary" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidr_secondary
  availability_zone       = var.availability_zone_secondary
  map_public_ip_on_launch = true

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-public-subnet-secondary"
    Tier = "public"
  })
}

# Private Subnet - For ECS Tasks
resource "aws_subnet" "private" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.private_subnet_cidr
  availability_zone       = var.availability_zone
  map_public_ip_on_launch = false

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-private-subnet"
    Tier = "private"
  })
}

# Database Subnet - For RDS and ElastiCache (Primary AZ)
resource "aws_subnet" "database" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.database_subnet_cidr
  availability_zone       = var.availability_zone
  map_public_ip_on_launch = false

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-database-subnet"
    Tier = "database"
  })
}

# Database Subnet Secondary - Required by RDS for subnet group (Secondary AZ)
resource "aws_subnet" "database_secondary" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.database_subnet_cidr_secondary
  availability_zone       = var.availability_zone_secondary
  map_public_ip_on_launch = false

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-database-subnet-secondary"
    Tier = "database"
  })
}

# -----------------------------------------------------------------------------
# Route Tables
# -----------------------------------------------------------------------------

# Public Route Table - Routes to Internet Gateway
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-public-rt"
  })
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_secondary" {
  subnet_id      = aws_subnet.public_secondary.id
  route_table_id = aws_route_table.public.id
}

# Private Route Table - Routes to NAT Gateway (if enabled)
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-private-rt"
  })
}

resource "aws_route_table_association" "private" {
  subnet_id      = aws_subnet.private.id
  route_table_id = aws_route_table.private.id
}

# Database Route Table - Local only (no internet access)
resource "aws_route_table" "database" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-database-rt"
  })
}

resource "aws_route_table_association" "database" {
  subnet_id      = aws_subnet.database.id
  route_table_id = aws_route_table.database.id
}

resource "aws_route_table_association" "database_secondary" {
  subnet_id      = aws_subnet.database_secondary.id
  route_table_id = aws_route_table.database.id
}

# -----------------------------------------------------------------------------
# DB Subnet Group (for RDS)
# -----------------------------------------------------------------------------
# Note: RDS requires at least 2 subnets in different AZs.
# We use the primary AZ for actual resources but include secondary for compliance.

resource "aws_db_subnet_group" "main" {
  name        = "${local.name_prefix}-db-subnet-group"
  description = "Database subnet group for ${var.environment}"
  subnet_ids  = [aws_subnet.database.id, aws_subnet.database_secondary.id]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db-subnet-group"
  })
}

# -----------------------------------------------------------------------------
# ElastiCache Subnet Group (for Redis)
# -----------------------------------------------------------------------------

resource "aws_elasticache_subnet_group" "main" {
  name        = "${local.name_prefix}-redis-subnet-group"
  description = "ElastiCache subnet group for ${var.environment}"
  subnet_ids  = [aws_subnet.database.id]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-redis-subnet-group"
  })
}
