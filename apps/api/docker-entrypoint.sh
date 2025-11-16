#!/bin/sh
set -e

# Install/sync dependencies if needed
if [ ! -d ".venv" ] || [ ! -f ".venv/bin/python" ]; then
    echo "Virtual environment not found, creating with UV..."
    /root/.local/bin/uv sync --frozen
fi

# Execute command
exec "$@"
