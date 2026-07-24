#!/bin/sh
# Exit immediately if a command exits with a non-zero status
set -e

echo "Running database migrations..."
uv run alembic upgrade head

echo "Creating initial superuser..."
uv run python create_superuser.py

echo "Starting FastAPI application in production..."
uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000