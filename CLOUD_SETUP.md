# Cloud BI Stack - Setup & Run Commands

## Prerequisites ✓

```bash
# 1. AWS CLI configured with co-pipeline profile
aws configure --profile co-pipeline
# Enter: Access Key, Secret Key, Region (us-east-1)

# Verify
aws sts get-caller-identity --profile co-pipeline
```

## Setup Commands

### 1. S3 Bootstrap (Run Once)

```bash
# Make executable and run
chmod +x cloud/aws/s3_setup.sh
cloud/aws/s3_setup.sh
```

**Expected Output:**
```
=== S3 Data Lake Setup ===
Profile: co-pipeline
Region: us-east-1

Creating dev bucket: co-data-dev
Creating prod bucket: co-data-prod
...
✓ S3 setup complete!
```

### 2. Fill Local Environment Variables

```bash
# Edit .env.compose with your actual values
nano .env.compose
```

**Fill these placeholders:**
```bash
AWS_REGION=us-east-1                    # ✓ Already set
S3_BUCKET=co-data-dev                   # ✓ Already set
AWS_PROFILE=co-pipeline                 # ✓ Already set
MOTHERDUCK_TOKEN=<PASTE_TOKEN_HERE>     # ← Get from https://motherduck.com/
```

### 3. Build & Run API Container

```bash
# Build and start in detached mode
docker compose --env-file .env.compose up -d --build bi_api

# View logs
docker compose logs -f bi_api
```

**Expected Output:**
```
[+] Building 45.2s (12/12) FINISHED
...
✔ Container co-bi-api  Started
```

### 4. Verify API Health

```bash
# Test health endpoint
curl -s http://localhost:8080/v1/health | jq
```

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "motherduck",
  "version": "1.0.0"
}
```

### 5. Test Presigned Upload URL

```bash
# Generate presigned S3 upload URL
curl -s -X POST "http://localhost:8080/v1/upload-url" \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": "acme",
    "building_id": "b1",
    "filename": "test.xlsx",
    "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
  }' | jq
```

**Expected Response:**
```json
{
  "uploadUrl": "https://co-data-dev.s3.amazonaws.com/raw/acme/b1/2025/01/14/1736870400-test.xlsx?...",
  "objectKey": "raw/acme/b1/2025/01/14/1736870400-test.xlsx",
  "expiresIn": 900
}
```

### 6. Test Query Endpoint

```bash
# List available queries
curl -s http://localhost:8080/v1/queries | jq

# Execute a query (example: property overview)
curl -s -X POST http://localhost:8080/v1/query/01_property_overview \
  -H "Content-Type: application/json" \
  -d '{}' | jq
```

### 7. Setup Next.js Environment

```bash
cd apps/web
cp .env.local.template .env.local

# Edit .env.local
nano .env.local
```

**Set:**
```bash
BI_API_URL=http://localhost:8080
```

### 8. Run dbt Against MotherDuck

```bash
cd "C.O. Project (ETL+BI)/warehouse/dbt"

# Set MotherDuck token
export MOTHERDUCK_TOKEN="your_token_here"

# Run dbt with cloud profile
dbt run --profiles-dir ../../../cloud --profile co_profile --target dev

# Test
dbt test --profiles-dir ../../../cloud --profile co_profile --target dev
```

## Verification Checklist

### ✓ **1. AWS Profile Configured**
```bash
aws sts get-caller-identity --profile co-pipeline
# Should show: Account, UserId, Arn
```

### ✓ **2. S3 Buckets Exist**
```bash
aws s3 ls --profile co-pipeline
# Should show: co-data-dev, co-data-prod
```

### ✓ **3. Environment File Filled**
```bash
cat .env.compose | grep -v "^#" | grep -v "^$"
# Should show all 4 variables with real values (no <PLACEHOLDERS>)
```

### ✓ **4. Docker Container Running**
```bash
docker ps | grep co-bi-api
# Should show: co-bi-api running on 0.0.0.0:8080
```

### ✓ **5. Health Check Passes**
```bash
curl -s http://localhost:8080/v1/health | jq -r .status
# Should output: healthy
```

### ✓ **6. Presigned Upload Works**
```bash
# Run the presigned URL test (above)
# Should return: uploadUrl, objectKey, expiresIn
```

### ✓ **7. dbt Connects to MotherDuck**
```bash
cd "C.O. Project (ETL+BI)/warehouse/dbt"
dbt debug --profiles-dir ../../../cloud --profile co_profile --target dev
# Should show: All checks passed!
```

### ✓ **8. Next.js Proxy Works**
```bash
cd apps/web
npm run dev

# In another terminal:
curl -s http://localhost:3000/api/bi/01_property_overview \
  -X POST -H "Content-Type: application/json" -d '{}' | jq
# Should return query results
```

## Common Issues & Fixes

### Issue 1: Docker build fails with "COPY failed"

**Cause:** Missing directories or files in COPY paths

**Fix:**
```bash
# Verify directories exist
ls -la services/bi_api/
ls -la "C.O. Project (ETL+BI)/sql_queries/"

# If sql_queries missing, create it
mkdir -p "C.O. Project (ETL+BI)/sql_queries"
touch "C.O. Project (ETL+BI)/sql_queries/.gitkeep"
```

### Issue 2: Health check returns "unhealthy" or connection error

**Cause:** MOTHERDUCK_TOKEN not set or invalid

**Fix:**
```bash
# 1. Verify token in .env.compose
cat .env.compose | grep MOTHERDUCK_TOKEN

# 2. Test token directly
duckdb "md:?motherduck_token=YOUR_TOKEN" -c "SELECT 1"

# 3. Restart container with new env
docker compose --env-file .env.compose down
docker compose --env-file .env.compose up -d --build bi_api
```

### Issue 3: S3 upload URL generation fails with "Access Denied"

**Cause:** AWS credentials not mounted or profile not found

**Fix:**
```bash
# 1. Verify AWS credentials exist
cat ~/.aws/credentials | grep co-pipeline

# 2. Verify volume mount in docker-compose.yml
cat docker-compose.yml | grep "~/.aws"

# 3. Restart container
docker compose --env-file .env.compose restart bi_api
```

## Quick Commands Reference

```bash
# Start API
docker compose --env-file .env.compose up -d bi_api

# Stop API
docker compose down

# View logs
docker compose logs -f bi_api

# Rebuild after code changes
docker compose --env-file .env.compose up -d --build bi_api

# Run dbt
cd "C.O. Project (ETL+BI)/warehouse/dbt"
dbt run --profiles-dir ../../../cloud --profile co_profile --target dev

# Test API endpoints
curl http://localhost:8080/v1/health
curl http://localhost:8080/v1/queries
curl http://localhost:8080/v1/tables
```

## Next Steps

Once all checks pass:

1. **Deploy to production:**
   - Push Docker image to registry (ECR, Docker Hub)
   - Deploy to ECS/Fargate or similar
   - Update Next.js `BI_API_URL` to production endpoint

2. **Add authentication:**
   - Implement JWT/API keys in FastAPI
   - Add middleware to Next.js proxy

3. **Monitor:**
   - Add Sentry for error tracking
   - Set up CloudWatch logs
   - Create health check alarms

4. **Optimize:**
   - Add Redis caching layer
   - Implement query result caching
   - Set up CDN for static assets
