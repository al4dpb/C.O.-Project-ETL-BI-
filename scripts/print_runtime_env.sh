#!/usr/bin/env bash
set -euo pipefail

echo "=== Runtime Environment Variables (Redacted) ==="
echo ""
echo "AWS Configuration:"
echo "  AWS_REGION=${AWS_REGION:-<NOT_SET>}"
echo "  S3_BUCKET=${S3_BUCKET:-<NOT_SET>}"
echo "  AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:0:4}********"
echo "  AWS_SECRET_ACCESS_KEY=********"
echo ""
echo "MotherDuck:"
echo "  MOTHERDUCK_TOKEN=${MOTHERDUCK_TOKEN:0:6}********"
echo ""
echo "Application:"
echo "  WAREHOUSE_PATH=${WAREHOUSE_PATH:-<NOT_SET>}"
echo ""
echo "=== End Runtime Environment ==="
