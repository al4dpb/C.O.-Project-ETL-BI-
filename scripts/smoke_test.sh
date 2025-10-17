#!/usr/bin/env bash
set -euo pipefail

echo "=== Container Offices BI Stack - Smoke Test ==="
echo ""

# Load environment variables
if [ ! -f .env.compose ]; then
    echo "❌ ERROR: .env.compose not found. Please create it with your credentials."
    exit 1
fi

export $(cat .env.compose | grep -v '^#' | xargs)

# Step 1: Show redacted environment
echo "Step 1: Verifying environment variables (redacted)..."
./scripts/print_runtime_env.sh
echo ""

# Step 2: Rebuild and start container
echo "Step 2: Rebuilding and starting bi_api container..."
docker compose --env-file .env.compose down
docker compose --env-file .env.compose up -d --build bi_api
echo "✓ Container started"
echo ""

# Wait for container to be ready
echo "Waiting for API to start..."
sleep 5

# Step 3: Health check
echo "Step 3: Testing /v1/health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8080/v1/health)
echo "$HEALTH_RESPONSE" | jq .
HEALTH_STATUS=$(echo "$HEALTH_RESPONSE" | jq -r .status)

if [ "$HEALTH_STATUS" != "healthy" ]; then
    echo "❌ Health check failed!"
    docker compose logs bi_api
    exit 1
fi
echo "✓ Health check passed"
echo ""

# Step 4: MotherDuck sanity check
echo "Step 4: Testing MotherDuck connection..."
duckdb "md:?motherduck_token=$MOTHERDUCK_TOKEN" -c "SELECT 1 as test" || {
    echo "❌ MotherDuck connection failed!"
    exit 1
}
echo "✓ MotherDuck connection successful"
echo ""

# Step 5: Presigned upload URL test
echo "Step 5: Testing S3 presigned upload URL generation..."
UPLOAD_RESPONSE=$(curl -s -X POST "http://localhost:8080/v1/upload-url" \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": "test",
    "building_id": "b1",
    "filename": "smoke_test.xlsx",
    "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
  }')

echo "$UPLOAD_RESPONSE" | jq .
UPLOAD_URL=$(echo "$UPLOAD_RESPONSE" | jq -r .uploadUrl)

if [ -z "$UPLOAD_URL" ] || [ "$UPLOAD_URL" == "null" ]; then
    echo "❌ Presigned URL generation failed!"
    exit 1
fi
echo "✓ Presigned URL generated successfully"
echo ""

# Step 6: dbt debug and run against MotherDuck
echo "Step 6: Testing dbt against MotherDuck..."
cd "C.O. Project (ETL+BI)/warehouse/dbt"

echo "Running dbt debug..."
dbt debug --profiles-dir ../../../cloud --profile co_profile --target dev || {
    echo "❌ dbt debug failed!"
    exit 1
}
echo "✓ dbt debug passed"
echo ""

echo "Running dbt (seed, run, snapshot, test)..."
dbt seed --profiles-dir ../../../cloud --profile co_profile --target dev
dbt run --profiles-dir ../../../cloud --profile co_profile --target dev
dbt snapshot --profiles-dir ../../../cloud --profile co_profile --target dev
dbt test --profiles-dir ../../../cloud --profile co_profile --target dev
cd ../../..
echo "✓ dbt pipeline completed successfully"
echo ""

# Step 7: Query API test
echo "Step 7: Testing query endpoint..."
QUERY_RESPONSE=$(curl -s -X POST "http://localhost:8080/v1/query/01_property_overview" \
  -H "Content-Type: application/json" \
  -d '{}')

echo "$QUERY_RESPONSE" | jq '.row_count, .columns'
ROW_COUNT=$(echo "$QUERY_RESPONSE" | jq -r .row_count)

if [ -z "$ROW_COUNT" ] || [ "$ROW_COUNT" == "null" ]; then
    echo "❌ Query execution failed!"
    exit 1
fi
echo "✓ Query executed successfully (returned $ROW_COUNT rows)"
echo ""

# Summary
echo "=== Smoke Test Summary ==="
echo "✓ All checks passed!"
echo ""
echo "Services running:"
docker compose ps
echo ""
echo "View logs: docker compose logs -f bi_api"
echo "Stop services: docker compose down"
