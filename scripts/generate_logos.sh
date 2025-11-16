#!/bin/bash
#
# Generate all logo sizes for web, PWA, and favicon
#
# This script:
# 1. Generates different PNG sizes from logo-transparent.png
# 2. Creates favicon.ico with multiple sizes
# 3. Copies files to apps/web/public/
#
# Requirements:
#   - ImageMagick (brew install imagemagick or apt install imagemagick)
#
# Usage:
#   bash scripts/generate_logos.sh

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0;no color'

# Paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOGO_DIR="$PROJECT_ROOT/ux/figures"
PUBLIC_DIR="$PROJECT_ROOT/apps/web/public"
LOGO_TRANSPARENT="$LOGO_DIR/logo-transparent.png"

# Check if ImageMagick is installed
if ! command -v convert &> /dev/null; then
    echo -e "${RED}❌ Error: ImageMagick not found${NC}"
    echo "Please install: brew install imagemagick (Mac) or apt install imagemagick (Linux)"
    exit 1
fi

# Check if transparent logo exists
if [ ! -f "$LOGO_TRANSPARENT" ]; then
    echo -e "${RED}❌ Error: logo-transparent.png not found${NC}"
    echo "Run 'python scripts/remove_bg.py' first"
    exit 1
fi

echo -e "${BLUE}📦 Generating logo sizes...${NC}"

# Create public directory if it doesn't exist
mkdir -p "$PUBLIC_DIR"

# Generate 32x32 favicon (for .ico generation)
echo "  → Generating 32x32 favicon..."
convert "$LOGO_TRANSPARENT" -resize 32x32 -background none -gravity center -extent 32x32 "$LOGO_DIR/logo-favicon.png"

# Generate 192x192 for PWA
echo "  → Generating 192x192 PWA icon..."
convert "$LOGO_TRANSPARENT" -resize 192x192 -background none -gravity center -extent 192x192 "$LOGO_DIR/logo-192.png"

# Generate 512x512 for PWA splash
echo "  → Generating 512x512 PWA splash..."
convert "$LOGO_TRANSPARENT" -resize 512x512 -background none -gravity center -extent 512x512 "$LOGO_DIR/logo-512.png"

# Generate favicon.ico with multiple sizes (16x16, 32x32)
echo "  → Generating favicon.ico (multi-size)..."
convert "$LOGO_TRANSPARENT" \
    \( -clone 0 -resize 16x16 \) \
    \( -clone 0 -resize 32x32 \) \
    -delete 0 \
    -colors 256 \
    "$LOGO_DIR/favicon.ico"

echo -e "${GREEN}✅ Logo sizes generated successfully!${NC}"
echo ""

# Copy to public directory
echo -e "${BLUE}📋 Copying to apps/web/public/...${NC}"

cp "$LOGO_DIR/favicon.ico" "$PUBLIC_DIR/favicon.ico"
echo "  ✓ favicon.ico"

cp "$LOGO_DIR/logo-192.png" "$PUBLIC_DIR/logo192.png"
echo "  ✓ logo192.png"

cp "$LOGO_DIR/logo-512.png" "$PUBLIC_DIR/logo512.png"
echo "  ✓ logo512.png"

echo -e "${GREEN}✅ Files copied to public directory!${NC}"
echo ""

# Summary
echo -e "${BLUE}📊 Summary:${NC}"
echo "  Generated files in ux/figures/:"
ls -lh "$LOGO_DIR"/logo-*.png "$LOGO_DIR"/favicon.ico 2>/dev/null | awk '{print "    " $9, "(" $5 ")"}'
echo ""
echo "  Copied to apps/web/public/:"
ls -lh "$PUBLIC_DIR"/{favicon.ico,logo*.png} 2>/dev/null | awk '{print "    " $9, "(" $5 ")"}'
echo ""
echo -e "${GREEN}🎉 All done!${NC}"
