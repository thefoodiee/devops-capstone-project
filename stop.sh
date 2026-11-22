#!/usr/bin/env bash
# Script to stop all Docker services for Cloud Notes
set -e

COMPOSE_CMD="docker compose"
if ! docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
fi

echo "Stopping Cloud-Native Notes Application stack..."
$COMPOSE_CMD down "$@"
echo "All services stopped."
