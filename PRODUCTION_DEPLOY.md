# 🚀 Production Deployment Guide - Container Offices BI Stack

Complete step-by-step guide to deploy the BI stack to production.

---

## Architecture Overview

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Next.js   │─────▶│   FastAPI    │─────▶│ MotherDuck  │
│   (Vercel)  │      │  (Render.com)│      │  (Warehouse)│
└──────┬──────┘      └──────┬───────┘      └─────────────┘
       │                    │
       │                    │
       ▼                    ▼
┌─────────────┐      ┌─────────────┐
│  S3 Upload  │─────▶│   Lambda    │
│  (Browser)  │      │ Excel→Parquet│
└─────────────┘      └──────┬──────┘
                            │
                            ▼
                     ┌─────────────┐
                     │   dbt Cloud │
                     │  (Optional) │
                     └─────────────┘
```

---

## Prerequisites

Before starting, ensure you have:

- [x] AWS Account with CLI configured
- [x] MotherDuck account with token
- [x] Vercel account
- [x] Render.com account (or Fly.io)
- [x] GitHub repository with code pushed
- [x] Domain name (optional, but recommended)

---

## Part 1: AWS S3 Setup

### 1.1 Configure S3 CORS for Browser Uploads

```bash
# Set CORS policy on production bucket
aws s3api put-bucket-cors \
  --bucket co-data-prod \
  --cors-configuration '{
    "CORSRules": [{
      "AllowedHeaders": ["*"],
      "AllowedMethods": ["PUT", "GET", "HEAD"],
      "AllowedOrigins": [
        "https://<YOUR_VERCEL_DOMAIN>.vercel.app",
        "https://yourdomain.com",
        "http://localhost:3000"
      ],
      "ExposeHeaders": ["ETag"],
      "MaxAgeSeconds": 3000
    }]
  }' \
  --profile co-pipeline

# Verify CORS configuration
aws s3api get-bucket-cors --bucket co-data-prod --profile co-pipeline
```

**Replace:**
- `<YOUR_VERCEL_DOMAIN>` with your actual Vercel project domain
- `yourdomain.com` with your custom domain (if any)

### 1.2 Verify Bucket Versioning

```bash
# Enable versioning (should already be enabled)
aws s3api put-bucket-versioning \
  --bucket co-data-prod \
  --versioning-configuration Status=Enabled \
  --profile co-pipeline

# Verify
aws s3api get-bucket-versioning --bucket co-data-prod --profile co-pipeline
```

---

## Part 2: Lambda Deployment (Auto-Refresh)

### 2.1 Create IAM Role for Lambda

```bash
# Create trust policy file
cat > lambda-trust-policy.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

# Create role
aws iam create-role \
  --role-name co-lambda-excel-processor \
  --assume-role-policy-document file://lambda-trust-policy.json \
  --profile co-pipeline

# Attach basic Lambda execution policy
aws iam attach-role-policy \
  --role-name co-lambda-excel-processor \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
  --profile co-pipeline

# Create and attach S3 access policy
cat > lambda-s3-policy.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "s3:GetObject",
      "s3:PutObject",
      "s3:ListBucket"
    ],
    "Resource": [
      "arn:aws:s3:::co-data-dev",
      "arn:aws:s3:::co-data-dev/*",
      "arn:aws:s3:::co-data-prod",
      "arn:aws:s3:::co-data-prod/*"
    ]
  }]
}
EOF

aws iam put-role-policy \
  --role-name co-lambda-excel-processor \
  --policy-name S3Access \
  --policy-document file://lambda-s3-policy.json \
  --profile co-pipeline

# Get the role ARN (save this!)
aws iam get-role \
  --role-name co-lambda-excel-processor \
  --query 'Role.Arn' \
  --output text \
  --profile co-pipeline
```

**Save the Role ARN** - you'll need it for the next step.

### 2.2 Deploy Lambda Function

**Option A: Using deploy script (Recommended)**

```bash
cd lambda

# Edit deploy.sh and replace <YOUR_LAMBDA_EXECUTION_ROLE_ARN> with the ARN from step 2.1
nano deploy.sh

# Run deployment
./deploy.sh
```

**Option B: Manual deployment**

```bash
cd lambda

# Install dependencies
pip install -r requirements.txt -t package/ --platform manylinux2014_x86_64 --only-binary=:all:

# Package Lambda
cd package && zip -r9 ../lambda-deployment.zip . && cd ..
zip -g lambda-deployment.zip handler.py

# Create Lambda function
aws lambda create-function \
  --function-name co-excel-to-parquet \
  --runtime python3.11 \
  --role <YOUR_LAMBDA_EXECUTION_ROLE_ARN> \
  --handler handler.lambda_handler \
  --zip-file fileb://lambda-deployment.zip \
  --timeout 300 \
  --memory-size 512 \
  --environment "Variables={S3_BUCKET=co-data-prod,AWS_REGION=us-east-1}" \
  --profile co-pipeline

# Add S3 invoke permission
aws lambda add-permission \
  --function-name co-excel-to-parquet \
  --statement-id s3-trigger-permission \
  --action lambda:InvokeFunction \
  --principal s3.amazonaws.com \
  --source-arn arn:aws:s3:::co-data-prod \
  --profile co-pipeline

# Get Lambda ARN (save this!)
aws lambda get-function \
  --function-name co-excel-to-parquet \
  --query 'Configuration.FunctionArn' \
  --output text \
  --profile co-pipeline
```

### 2.3 Configure S3 Bucket Notification

```bash
# Create notification configuration
cat > s3-notification-config.json <<'EOF'
{
  "LambdaFunctionConfigurations": [{
    "Id": "ExcelUploadTrigger",
    "LambdaFunctionArn": "<YOUR_LAMBDA_ARN>",
    "Events": ["s3:ObjectCreated:*"],
    "Filter": {
      "Key": {
        "FilterRules": [
          {"Name": "prefix", "Value": "raw/"},
          {"Name": "suffix", "Value": ".xlsx"}
        ]
      }
    }
  }]
}
EOF

# Replace <YOUR_LAMBDA_ARN> with your actual Lambda ARN from step 2.2
# Then apply the configuration:
aws s3api put-bucket-notification-configuration \
  --bucket co-data-prod \
  --notification-configuration file://s3-notification-config.json \
  --profile co-pipeline

# Verify
aws s3api get-bucket-notification-configuration \
  --bucket co-data-prod \
  --profile co-pipeline
```

### 2.4 Set Lambda Environment Variables

Go to AWS Lambda Console or use CLI:

```bash
aws lambda update-function-configuration \
  --function-name co-excel-to-parquet \
  --environment "Variables={S3_BUCKET=co-data-prod,AWS_REGION=us-east-1,DBT_CLOUD_JOB_WEBHOOK=<YOUR_DBT_WEBHOOK>}" \
  --profile co-pipeline
```

**Optional:** Set `DBT_CLOUD_JOB_WEBHOOK` if using dbt Cloud.

---

## Part 3: FastAPI Backend Deployment (Render.com)

### 3.1 Render.com Web Service Setup

**Via Render Dashboard:**

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `container-offices-api` |
| **Environment** | `Docker` |
| **Region** | `US East (Ohio)` or closest to your users |
| **Branch** | `main` |
| **Dockerfile Path** | `services/bi_api/Dockerfile` |
| **Docker Context Directory** | `.` (project root) |

5. Click **"Advanced"** and set environment variables:

```bash
AWS_REGION=us-east-1
S3_BUCKET=co-data-prod
AWS_ACCESS_KEY_ID=<YOUR_AWS_ACCESS_KEY>
AWS_SECRET_ACCESS_KEY=<YOUR_AWS_SECRET_KEY>
MOTHERDUCK_TOKEN=<YOUR_MOTHERDUCK_TOKEN>
```

**⚠️ SECURITY:** Use Render's **Secret Files** feature or environment variable encryption for credentials.

6. Set Health Check:
   - **Health Check Path**: `/v1/health`
   - **Health Check Timeout**: `30s`

7. Click **"Create Web Service"**

8. Wait for deployment (5-10 minutes)

9. **Save your Render URL**: `https://container-offices-api.onrender.com`

### 3.2 Verify API Deployment

```bash
# Health check
curl https://container-offices-api.onrender.com/v1/health

# Should return:
# {
#   "status": "healthy",
#   "database": "motherduck",
#   "version": "1.0.0"
# }
```

---

## Part 4: Frontend Deployment (Vercel)

### 4.1 Prepare Vercel Project

```bash
cd apps/web

# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login
```

### 4.2 Deploy to Vercel

**Option A: Via CLI**

```bash
# First deployment (creates project)
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? (select your account)
# - Link to existing project? No
# - Project name: container-offices-ui
# - Directory: ./apps/web
# - Override settings? No

# Production deployment
vercel --prod
```

**Option B: Via Vercel Dashboard**

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `apps/web`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### 4.3 Set Vercel Environment Variables

In Vercel Dashboard → Project Settings → Environment Variables:

| Name | Value | Environments |
|------|-------|--------------|
| `BI_API_URL` | `https://container-offices-api.onrender.com` | Production, Preview, Development |
| `NEXT_PUBLIC_BASE_URL` | `https://<YOUR_VERCEL_DOMAIN>.vercel.app` | Production |
| `NEXT_PUBLIC_BASE_URL` | `https://<YOUR_PREVIEW>.vercel.app` | Preview |
| `NEXT_PUBLIC_BASE_URL` | `http://localhost:3000` | Development |

**Replace** `<YOUR_VERCEL_DOMAIN>` with your actual Vercel domain.

### 4.4 Redeploy with Environment Variables

```bash
# Trigger new deployment with env vars
vercel --prod
```

### 4.5 Update S3 CORS with Vercel Domain

Now that you have your Vercel domain, update S3 CORS:

```bash
aws s3api put-bucket-cors \
  --bucket co-data-prod \
  --cors-configuration '{
    "CORSRules": [{
      "AllowedHeaders": ["*"],
      "AllowedMethods": ["PUT", "GET", "HEAD"],
      "AllowedOrigins": [
        "https://<YOUR_ACTUAL_VERCEL_DOMAIN>.vercel.app"
      ],
      "ExposeHeaders": ["ETag"],
      "MaxAgeSeconds": 3000
    }]
  }' \
  --profile co-pipeline
```

---

## Part 5: Smoke Tests

### 5.1 Production Health Checks

```bash
# API Health
curl https://container-offices-api.onrender.com/v1/health | jq

# List available queries
curl https://container-offices-api.onrender.com/v1/queries | jq

# Test query execution
curl -X POST https://container-offices-api.onrender.com/v1/query/01_property_overview \
  -H "Content-Type: application/json" \
  -d '{}' | jq '.row_count'
```

### 5.2 Frontend Access Test

```bash
# Open in browser
open https://<YOUR_VERCEL_DOMAIN>.vercel.app/dashboard
```

**Verify:**
- [ ] Dashboard loads without errors
- [ ] Cards show data (not "N/A" or empty)
- [ ] Tables populate with real data
- [ ] No console errors in browser DevTools

### 5.3 Upload Flow Test

1. Go to `https://<YOUR_VERCEL_DOMAIN>.vercel.app/dashboard/upload`
2. Select an Excel file
3. Click "Upload File"
4. Verify success message appears
5. Check S3 bucket:

```bash
aws s3 ls s3://co-data-prod/raw/ --recursive --profile co-pipeline
```

6. Wait 1-2 minutes, check bronze folder:

```bash
aws s3 ls s3://co-data-prod/bronze/ --recursive --profile co-pipeline
```

7. Check Lambda logs:

```bash
aws logs tail /aws/lambda/co-excel-to-parquet --follow --profile co-pipeline
```

### 5.4 End-to-End Test

```bash
# 1. Upload test file via API
curl -X POST "https://container-offices-api.onrender.com/v1/upload-url" \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": "test",
    "building_id": "b1",
    "filename": "test.xlsx",
    "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
  }' > upload_response.json

# Extract upload URL
UPLOAD_URL=$(cat upload_response.json | jq -r .uploadUrl)

# 2. Upload file
curl -X PUT "$UPLOAD_URL" \
  -H "Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" \
  --data-binary "@path/to/your/test.xlsx"

# 3. Wait for Lambda processing (30-60 seconds)
sleep 60

# 4. Verify Parquet files created
aws s3 ls s3://co-data-prod/bronze/test/b1/ --recursive --profile co-pipeline

# 5. Query updated data
curl -X POST "https://container-offices-api.onrender.com/v1/query/01_property_overview" \
  -H "Content-Type: application/json" \
  -d '{}' | jq
```

---

## Part 6: dbt Cloud Integration (Optional)

If using dbt Cloud for transformations:

### 6.1 Create dbt Cloud Account

1. Sign up at [cloud.getdbt.com](https://cloud.getdbt.com)
2. Connect your GitHub repository
3. Set up project with MotherDuck connection

### 6.2 Configure dbt Cloud Credentials

In dbt Cloud → Project Settings → Credentials:

```yaml
type: duckdb
path: md:co_warehouse_prod?motherduck_token={{ env_var('MOTHERDUCK_TOKEN') }}
schema: co_gold
threads: 8
```

Set environment variable `MOTHERDUCK_TOKEN` in dbt Cloud.

### 6.3 Create Webhook for Lambda Trigger

1. dbt Cloud → Jobs → Create Job
2. Name: "Production Refresh"
3. Commands:
   ```
   dbt seed
   dbt run
   dbt snapshot
   dbt test
   ```
4. Generate webhook URL
5. Copy webhook URL and add to Lambda environment:

```bash
aws lambda update-function-configuration \
  --function-name co-excel-to-parquet \
  --environment "Variables={S3_BUCKET=co-data-prod,AWS_REGION=us-east-1,DBT_CLOUD_JOB_WEBHOOK=<YOUR_DBT_WEBHOOK>}" \
  --profile co-pipeline
```

---

## Part 7: Monitoring & Maintenance

### 7.1 Set Up CloudWatch Alarms

```bash
# Lambda error alarm
aws cloudwatch put-metric-alarm \
  --alarm-name co-lambda-errors \
  --alarm-description "Alert on Lambda errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=FunctionName,Value=co-excel-to-parquet \
  --profile co-pipeline
```

### 7.2 Enable Render Alerts

In Render Dashboard → Service → Alerts:
- Enable "Health Check Failed" notifications
- Enable "Deployment Failed" notifications

### 7.3 Vercel Analytics

In Vercel Dashboard → Project → Analytics:
- Enable Web Analytics
- Monitor Core Web Vitals

---

## Security Checklist

Before going live:

- [ ] All environment variables use secrets (no hardcoded values)
- [ ] S3 buckets have versioning enabled
- [ ] CORS policies restrict to production domains only
- [ ] Lambda has minimal IAM permissions
- [ ] API has rate limiting (consider adding Cloudflare)
- [ ] Pre-commit hooks prevent secret leaks
- [ ] `.env.compose` and all `.env*` files are gitignored
- [ ] AWS credentials rotated and stored securely
- [ ] MotherDuck token rotated

---

## Rollback Procedures

### Rollback Vercel Deployment

```bash
# List deployments
vercel ls

# Rollback to specific deployment
vercel rollback <deployment-url>
```

### Rollback Render Deployment

Render Dashboard → Service → Deploys → Click "Rollback" on previous working deployment

### Rollback Lambda

```bash
# List versions
aws lambda list-versions-by-function --function-name co-excel-to-parquet --profile co-pipeline

# Rollback by updating alias
aws lambda update-alias \
  --function-name co-excel-to-parquet \
  --name PROD \
  --function-version <previous-version> \
  --profile co-pipeline
```

---

## Cost Estimates (Monthly)

| Service | Usage | Estimated Cost |
|---------|-------|----------------|
| Vercel (Hobby) | <100GB bandwidth | **$0** |
| Render (Starter) | 1 instance, 512MB | **$7** |
| AWS S3 | <50GB storage | **$1-2** |
| AWS Lambda | <10k invocations | **$0** (free tier) |
| MotherDuck | Up to 10GB | **$0** (free tier) |
| **Total** | | **~$8-10/month** |

---

## Support & Troubleshooting

### Common Issues

**1. CORS Error on Upload**
- Verify Vercel domain in S3 CORS configuration
- Check browser console for exact error
- Ensure CORS allows PUT method

**2. API Returns 500 Error**
- Check Render logs: Dashboard → Service → Logs
- Verify all environment variables are set
- Test MotherDuck connection directly

**3. Lambda Not Triggering**
- Check S3 notification configuration
- Verify Lambda has permission to be invoked by S3
- Check CloudWatch logs for Lambda errors

**4. Dashboard Shows No Data**
- Verify API is healthy: `/v1/health`
- Check if data exists in MotherDuck
- Run dbt transformations manually

---

## Next Steps

After successful deployment:

1. **Set up custom domain** (optional)
   - Configure in Vercel: Settings → Domains
   - Update CORS and environment variables

2. **Enable authentication** (recommended for production)
   - Add NextAuth.js to frontend
   - Implement API key authentication on backend

3. **Set up CI/CD**
   - GitHub Actions for automated testing
   - Automatic deployments on merge to main

4. **Add monitoring**
   - Sentry for error tracking
   - LogRocket for session replay
   - Datadog for metrics

5. **Create user documentation**
   - Upload process guide
   - Dashboard user manual
   - FAQ page

---

## 🎉 Deployment Complete!

Your Container Offices BI Stack is now live in production!

**Access Points:**
- 📊 Dashboard: `https://<YOUR_VERCEL_DOMAIN>.vercel.app/dashboard`
- 🔧 API: `https://container-offices-api.onrender.com`
- ⚙️ API Docs: `https://container-offices-api.onrender.com/docs`

**Quick Links:**
- [Vercel Dashboard](https://vercel.com/dashboard)
- [Render Dashboard](https://dashboard.render.com/)
- [AWS Console](https://console.aws.amazon.com/)
- [MotherDuck Console](https://app.motherduck.com/)
