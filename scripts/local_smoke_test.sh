#!/usr/bin/env bash
set -euo pipefail

echo "=== Local Development Smoke Test ==="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env.compose exists
if [ ! -f .env.compose ]; then
    echo -e "${RED}❌ ERROR: .env.compose not found${NC}"
    echo "Create .env.compose with your credentials first"
    exit 1
fi

# Load environment
export $(cat .env.compose | grep -v '^#' | xargs)

echo "Step 1: Show environment variables (redacted)"
./scripts/print_runtime_env.sh || {
    echo -e "${RED}❌ Failed to show environment${NC}"
    exit 1
}
echo ""

echo "Step 2: Start API container"
docker compose --env-file .env.compose down
docker compose --env-file .env.compose up -d --build bi_api
echo -e "${GREEN}✓ Container started${NC}"
echo ""

echo "Waiting for API to be ready (10s)..."
sleep 10

echo "Step 3: Health check"
HEALTH_RESPONSE=$(curl -s http://localhost:8080/v1/health)
echo "$HEALTH_RESPONSE" | jq . || {
    echo -e "${RED}❌ Health check failed${NC}"
    docker compose logs bi_api
    exit 1
}

HEALTH_STATUS=$(echo "$HEALTH_RESPONSE" | jq -r .status)
if [ "$HEALTH_STATUS" = "healthy" ]; then
    echo -e "${GREEN}✓ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed: status=$HEALTH_STATUS${NC}"
    exit 1
fi
echo ""

echo "Step 4: List available queries"
curl -s http://localhost:8080/v1/queries | jq .queries || {
    echo -e "${RED}❌ Failed to list queries${NC}"
    exit 1
}
echo -e "${GREEN}✓ Queries listed${NC}"
echo ""

echo "Step 5: Test query execution"
QUERY_RESPONSE=$(curl -s -X POST http://localhost:8080/v1/query/01_property_overview \
  -H "Content-Type: application/json" -d '{}')

ROW_COUNT=$(echo "$QUERY_RESPONSE" | jq -r .row_count)
if [ "$ROW_COUNT" != "null" ] && [ "$ROW_COUNT" != "0" ]; then
    echo -e "${GREEN}✓ Query executed successfully (returned $ROW_COUNT rows)${NC}"
else
    echo -e "${RED}❌ Query failed or returned no data${NC}"
    echo "$QUERY_RESPONSE" | jq .
    exit 1
fi
echo ""

echo "Step 6: Test upload URL generation"
UPLOAD_RESPONSE=$(curl -s -X POST "http://localhost:8080/v1/upload-url" \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": "test",
    "building_id": "b1",
    "filename": "test.xlsx",
    "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
  }')

UPLOAD_URL=$(echo "$UPLOAD_RESPONSE" | jq -r .uploadUrl)
if [ "$UPLOAD_URL" != "null" ] && [ -n "$UPLOAD_URL" ]; then
    echo -e "${GREEN}✓ Upload URL generated${NC}"
    echo "  URL (redacted): ${UPLOAD_URL:0:50}..."
else
    echo -e "${RED}❌ Failed to generate upload URL${NC}"
    echo "$UPLOAD_RESPONSE" | jq .
    exit 1
fi
echo ""

echo "Step 7: Test MotherDuck connection (if configured)"
if [ -n "${MOTHERDUCK_TOKEN:-}" ]; then
    duckdb "md:?motherduck_token=$MOTHERDUCK_TOKEN" -c "SELECT 1 as test" > /dev/null 2>&1 && {
        echo -e "${GREEN}✓ MotherDuck connection successful${NC}"
    } || {
        echo -e "${RED}❌ MotherDuck connection failed${NC}"
        echo "Check your MOTHERDUCK_TOKEN"
    }
else
    echo "⚠️  MOTHERDUCK_TOKEN not set, skipping MotherDuck test"
fi
echo ""

echo "Step 8: Frontend setup check"
cd apps/web

if [ ! -f .env.local ]; then
    echo "Creating .env.local from template..."
    cp .env.local.example .env.local
    echo -e "${GREEN}✓ .env.local created${NC}"
    echo "⚠️  Edit apps/web/.env.local with your values"
else
    echo -e "${GREEN}✓ .env.local exists${NC}"
fi

if [ ! -d node_modules ]; then
    echo "Installing npm dependencies..."
    npm install
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Dependencies already installed${NC}"
fi

cd ../..
echo ""

echo "=== Local Smoke Test Summary ==="
echo -e "${GREEN}✓ All checks passed!${NC}"
echo ""
echo "Next steps:"
echo "  1. Start frontend: cd apps/web && npm run dev"
echo "  2. Open: http://localhost:3000/dashboard"
echo "  3. Test upload: http://localhost:3000/dashboard/upload"
echo ""
echo "API is running at: http://localhost:8080"
echo "API docs: http://localhost:8080/docs"
echo ""
echo "To stop API: docker compose down"
