#!/usr/bin/env bash
set -euo pipefail

if [ ! -f .env.compose ]; then
    echo "ERROR: .env.compose not found in repo root"
    echo "Create it with your credentials first"
    exit 1
fi

echo "Starting BI API container..."
docker compose --env-file .env.compose down
docker compose --env-file .env.compose up -d --build bi_api

echo ""
echo "Waiting for API to be ready (5s)..."
sleep 5

echo ""
echo "Health check:"
curl -s http://localhost:8080/v1/health | python3 -m json.tool || curl -s http://localhost:8080/v1/health

echo ""
echo ""
echo "API running at http://localhost:8080"
echo "API docs: http://localhost:8080/docs"
