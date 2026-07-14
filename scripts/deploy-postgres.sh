#!/usr/bin/env bash
set -Eeuo pipefail

SOURCE_DIR="/opt/aios-src/docker/postgres"
RUNTIME_DIR="/opt/aios/docker/postgres"

echo "[1/5] Checking source..."
test -f "$SOURCE_DIR/compose.yml"

echo "[2/5] Checking runtime..."
test -f "$RUNTIME_DIR/.env"

echo "[3/5] Copy compose.yml..."
install -m 0644 "$SOURCE_DIR/compose.yml" "$RUNTIME_DIR/compose.yml"

echo "[4/5] Validate compose..."
docker compose --project-directory "$RUNTIME_DIR" config --quiet

echo "[5/5] Starting PostgreSQL..."
docker compose --project-directory "$RUNTIME_DIR" up -d

echo
docker compose --project-directory "$RUNTIME_DIR" ps
