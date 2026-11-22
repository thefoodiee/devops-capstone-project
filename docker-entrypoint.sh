#!/usr/bin/env bash
set -e

echo "=== [Cloud Notes] Starting Application Entrypoint ==="

# Wait for PostgreSQL to be ready if configured with Postgres
if [ "$USE_SQLITE" != "true" ] && [ -n "$DB_HOST" ]; then
    echo "[Entrypoint] Checking database availability at ${DB_HOST}:${DB_PORT:-5432}..."
    max_retries=30
    count=0
    until python3 -c "
import os, sys, psycopg2
try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres'),
        dbname=os.getenv('DB_NAME', 'notes_db')
    )
    conn.close()
    sys.exit(0)
except Exception as e:
    sys.exit(1)
" 2>/dev/null; do
        count=$((count+1))
        if [ $count -gt $max_retries ]; then
            echo "[Entrypoint] Database connection timed out. Proceeding..."
            break
        fi
        echo "[Entrypoint] Waiting for database (${count}/${max_retries})..."
        sleep 2
    done
fi

# Run database table initialization and demo seeding
echo "[Entrypoint] Initializing database tables & seed data..."
python3 scripts/init_db.py

# Launch application with Gunicorn
PORT="${PORT:-5000}"
WORKERS="${GUNICORN_WORKERS:-3}"
echo "[Entrypoint] Starting Gunicorn server on 0.0.0.0:${PORT} with ${WORKERS} workers..."
exec gunicorn --bind "0.0.0.0:${PORT}" \
    --workers "${WORKERS}" \
    --access-logfile - \
    --error-logfile - \
    "app:create_app()"
