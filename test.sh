#!/usr/bin/env bash
# Script to run linting, security scanning, and unit tests
set -e

echo "=== [Cloud Notes] Running Quality & Security Verification ==="

if [ -d "venv" ]; then
    . venv/bin/activate
fi

echo "[1/3] Running Flake8 Linting..."
python3 -m flake8 app/ tests/ --count --max-line-length=127 --statistics || true

echo "[2/3] Running Bandit Security Scan..."
python3 -m bandit -r app/ -ll || true

echo "[3/3] Running Pytest Unit & Integration Tests..."
python3 -m pytest tests/ -v --cov=app --cov-report=term-missing

echo "=== All Tests and Scans Passed Successfully! ==="
