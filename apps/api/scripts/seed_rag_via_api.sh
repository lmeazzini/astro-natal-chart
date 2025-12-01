#!/bin/bash

# Script to seed RAG via API endpoint
# Usage: ./scripts/seed_rag_via_api.sh

set -e

# Get auth token (use an existing user or create one)
API_URL="http://localhost:8000"
TOKEN="${RAG_SEED_TOKEN:-}"

if [ -z "$TOKEN" ]; then
    echo "Error: RAG_SEED_TOKEN environment variable not set"
    echo "Please set it with a valid JWT token:"
    echo "  export RAG_SEED_TOKEN='your_jwt_token_here'"
    exit 1
fi

echo "========================================"
echo "Seeding RAG System via API"
echo "========================================"
echo "API URL: $API_URL"
echo ""

# Document 1: Fundamentos da Astrologia Tradicional
echo "[1/5] Ingesting: Fundamentos da Astrologia Tradicional"
curl -s -X POST "$API_URL/api/v1/rag/ingest/text" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
  "title": "Fundamentos da Astrologia Tradicional",
  "content": "# Fundamentos da Astrologia Tradicional\n\nA astrologia tradicional é um sistema antigo de interpretação que remonta à Babilônia, Grécia e Roma...",
  "document_type": "astrology_fundamentals",
  "metadata": {"category": "traditional_astrology", "language": "pt-BR"}
}' | python3 -m json.tool

echo ""
echo "========================================"
echo "Seeding completed!"
echo "========================================"
