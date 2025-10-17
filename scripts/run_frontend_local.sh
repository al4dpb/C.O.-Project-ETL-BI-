#!/usr/bin/env bash
set -euo pipefail

cd apps/web

if [ ! -f .env.local ]; then
    echo "Creating .env.local from template..."
    cp .env.local.example .env.local
    echo ".env.local created - using defaults"
fi

if [ ! -d node_modules ]; then
    echo "Installing dependencies..."
    npm install
fi

echo ""
echo "Starting Next.js dev server..."
npm run dev
