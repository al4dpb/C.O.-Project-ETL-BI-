# 🚀 Release Checklist - Container Offices BI Stack

Use this checklist to deploy the BI stack to production today.

---

## Pre-Deployment Checklist

### 1. Code & Repository
- [ ] All code committed and pushed to `main` branch
- [ ] No secrets in Git history (run `git log --all -p | grep -i "motherduck\|AKIA"`)
- [ ] `.gitignore` includes all secret files (.env, .env.*, *.csv)
- [ ] Pre-commit hooks installed (`pre-commit install`)
- [ ] All tests passing locally

### 2. Environment Variables Prepared
- [ ] AWS credentials ready (Access Key ID & Secret Access Key)
- [ ] MotherDuck token obtained from [motherduck.com](https://motherduck.com)
- [ ] S3 buckets created (`co-data-dev`, `co-data-prod`)
- [ ] AWS CLI configured with `co-pipeline` profile

### 3. Local Testing Complete
- [ ] API runs locally with `docker compose up`
- [ ] Frontend runs locally with `npm run dev`
- [ ] Upload flow tested end-to-end
- [ ] dbt runs successfully against MotherDuck
- [ ] All queries return data

---

## Deployment Steps

### Step 1: AWS Infrastructure (30 minutes)

**1.1 S3 CORS Configuration**
```bash
# ⏱️ 5 minutes
aws s3api put-bucket-cors --bucket co-data-prod --cors-configuration '{
  "CORSRules": [{
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["PUT", "GET", "HEAD"],
    "AllowedOrigins": ["https://*.vercel.app", "http://localhost:3000"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }]
}' --profile co-pipeline
```

- [ ] CORS configured on `co-data-prod`
- [ ] CORS configured on `co-data-dev` (optional)
- [ ] Versioning enabled on both buckets

**1.2 Lambda IAM Role**
```bash
# ⏱️ 10 minutes
# Create role (see PRODUCTION_DEPLOY.md Part 2.1)
```

- [ ] IAM role `co-lambda-excel-processor` created
- [ ] S3 access policy attached
- [ ] Lambda execution policy attached
- [ ] Role ARN saved: `_______________________________________`

**1.3 Lambda Deployment**
```bash
# ⏱️ 10 minutes
cd lambda
./deploy.sh
```

- [ ] Lambda function `co-excel-to-parquet` deployed
- [ ] Environment variables set (S3_BUCKET, AWS_REGION)
- [ ] S3 invoke permission added
- [ ] Lambda ARN saved: `_______________________________________`

**1.4 S3 Bucket Notification**
```bash
# ⏱️ 5 minutes
# Configure notification (see PRODUCTION_DEPLOY.md Part 2.3)
```

- [ ] S3 notification configured for `.xlsx` files in `raw/` prefix
- [ ] Notification verified with `aws s3api get-bucket-notification-configuration`

---

### Step 2: Backend API Deployment (20 minutes)

**2.1 Render.com Setup**

- [ ] Render.com account created
- [ ] GitHub repository connected
- [ ] Web Service created with name: `container-offices-api`

**2.2 Render Configuration**

| Setting | Value | Done |
|---------|-------|------|
| Environment | Docker | [ ] |
| Dockerfile Path | `services/bi_api/Dockerfile` | [ ] |
| Docker Context | `.` (root) | [ ] |
| Health Check Path | `/v1/health` | [ ] |

**2.3 Environment Variables**

Set in Render Dashboard → Environment:

| Variable | Value | Done |
|----------|-------|------|
| `AWS_REGION` | `us-east-1` | [ ] |
| `S3_BUCKET` | `co-data-prod` | [ ] |
| `AWS_ACCESS_KEY_ID` | `<YOUR_KEY>` | [ ] |
| `AWS_SECRET_ACCESS_KEY` | `<YOUR_SECRET>` | [ ] |
| `MOTHERDUCK_TOKEN` | `<YOUR_TOKEN>` | [ ] |

- [ ] All environment variables set
- [ ] Service deployed successfully
- [ ] Render URL saved: `https://_____________________________.onrender.com`

**2.4 API Health Check**

```bash
curl https://<YOUR_RENDER_URL>.onrender.com/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "motherduck",
  "version": "1.0.0"
}
```

- [ ] Health check returns `"status": "healthy"`
- [ ] Database shows `"motherduck"`

---

### Step 3: Frontend Deployment (15 minutes)

**3.1 Vercel Project Setup**

```bash
cd apps/web
vercel login
vercel
```

- [ ] Vercel account created/logged in
- [ ] Project created: `container-offices-ui`
- [ ] Initial deployment successful
- [ ] Vercel URL saved: `https://_____________________________.vercel.app`

**3.2 Environment Variables**

Set in Vercel Dashboard → Settings → Environment Variables:

| Variable | Value | Environments | Done |
|----------|-------|--------------|------|
| `BI_API_URL` | `https://<RENDER_URL>.onrender.com` | Production, Preview | [ ] |
| `NEXT_PUBLIC_BASE_URL` | `https://<VERCEL_URL>.vercel.app` | Production | [ ] |

- [ ] Both variables set
- [ ] Redeployed with `vercel --prod`

**3.3 Update S3 CORS with Actual Vercel Domain**

```bash
# Now that you have the Vercel domain, update CORS
aws s3api put-bucket-cors --bucket co-data-prod --cors-configuration '{
  "CORSRules": [{
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["PUT", "GET", "HEAD"],
    "AllowedOrigins": ["https://<YOUR_ACTUAL_VERCEL_DOMAIN>.vercel.app"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }]
}' --profile co-pipeline
```

- [ ] CORS updated with actual Vercel domain
- [ ] CORS verified

---

### Step 4: End-to-End Smoke Tests (15 minutes)

**4.1 API Tests**

```bash
# Query list
curl https://<RENDER_URL>/v1/queries

# Execute query
curl -X POST https://<RENDER_URL>/v1/query/01_property_overview \
  -H "Content-Type: application/json" -d '{}'
```

- [ ] `/v1/queries` returns list of queries
- [ ] `/v1/query/01_property_overview` returns data
- [ ] No errors in Render logs

**4.2 Frontend Tests**

Open in browser: `https://<VERCEL_URL>/dashboard`

- [ ] Dashboard page loads without errors
- [ ] Summary cards show data (not "N/A")
- [ ] Property overview table populated
- [ ] Revenue trends table populated
- [ ] No console errors in browser DevTools

**4.3 Upload Flow Test**

1. Go to: `https://<VERCEL_URL>/dashboard/upload`
2. Enter org_id: `test`
3. Enter building_id: `b1`
4. Select Excel file
5. Click "Upload File"

- [ ] Upload completes without error
- [ ] Success message appears
- [ ] S3 file visible in console: `aws s3 ls s3://co-data-prod/raw/test/b1/`

**4.4 Lambda Processing Test**

Wait 1-2 minutes after upload, then:

```bash
# Check bronze folder for Parquet files
aws s3 ls s3://co-data-prod/bronze/test/b1/ --recursive

# Check Lambda logs
aws logs tail /aws/lambda/co-excel-to-parquet --follow
```

- [ ] Parquet files created in `bronze/` folder
- [ ] Lambda logs show successful processing
- [ ] No errors in CloudWatch logs

**4.5 Data Refresh Test**

```bash
# Query should now include new data
curl -X POST https://<RENDER_URL>/v1/query/01_property_overview \
  -H "Content-Type: application/json" -d '{}' | jq '.row_count'
```

- [ ] Row count increased or data updated
- [ ] Dashboard reflects new data (refresh page)

---

## Post-Deployment Checklist

### 5. Monitoring & Alerts (10 minutes)

**5.1 CloudWatch Alarms**

```bash
# Lambda errors alarm (see PRODUCTION_DEPLOY.md Part 7.1)
```

- [ ] Lambda error alarm created
- [ ] SNS topic configured for notifications (optional)

**5.2 Render Alerts**

- [ ] Health check failed alert enabled
- [ ] Deployment failed alert enabled
- [ ] Email notifications configured

**5.3 Vercel Monitoring**

- [ ] Web Analytics enabled
- [ ] Core Web Vitals monitoring active

### 6. Documentation (5 minutes)

- [ ] Render URL documented for team
- [ ] Vercel URL documented for team
- [ ] Upload instructions shared with users
- [ ] Support contact information provided

### 7. Security Review (10 minutes)

- [ ] No secrets in Git history: `git log --all -p | grep -i "secret\|token\|akia"`
- [ ] All `.env` files gitignored
- [ ] AWS credentials rotated (if previously shared)
- [ ] MotherDuck token is unique (not reused from other projects)
- [ ] S3 CORS allows only production domain
- [ ] Render environment variables use "Secret" type

---

## Final Verification (5 minutes)

### Production URLs

| Service | URL | Status |
|---------|-----|--------|
| Frontend | `https://<VERCEL_URL>` | [ ] ✅ Live |
| API | `https://<RENDER_URL>` | [ ] ✅ Live |
| API Health | `https://<RENDER_URL>/v1/health` | [ ] ✅ Healthy |
| API Docs | `https://<RENDER_URL>/docs` | [ ] ✅ Accessible |

### Key Metrics

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| Dashboard Load Time | <3s | ___s | [ ] |
| API Response Time | <500ms | ___ms | [ ] |
| Upload Success Rate | 100% | ___% | [ ] |
| Lambda Execution Time | <30s | ___s | [ ] |

---

## Rollback Plan (If Needed)

If something goes wrong:

**Frontend Rollback**
```bash
vercel ls
vercel rollback <previous-deployment-url>
```

**Backend Rollback**
- Render Dashboard → Deploys → Click "Rollback" on previous version

**Lambda Rollback**
```bash
aws lambda list-versions-by-function --function-name co-excel-to-parquet
aws lambda update-alias --function-name co-excel-to-parquet --name PROD --function-version <previous>
```

---

## Client Handoff Checklist

### Deliverables

- [ ] Production dashboard URL shared
- [ ] Upload page URL shared
- [ ] User guide provided (how to upload Excel files)
- [ ] Data update frequency documented (real-time after upload)
- [ ] Support contact information provided
- [ ] Admin credentials shared (if authentication added)

### Training

- [ ] Demo of upload process
- [ ] Walkthrough of dashboard features
- [ ] Explanation of data refresh mechanism
- [ ] Troubleshooting guide provided

### Maintenance

- [ ] Weekly backup schedule documented
- [ ] Monthly cost review scheduled
- [ ] Quarterly security audit planned
- [ ] Annual credential rotation scheduled

---

## 🎉 Go-Live Sign-Off

**Deployed by:** `_______________________`

**Date:** `_______________________`

**Time:** `_______________________`

**Production URLs:**
- Dashboard: `_______________________`
- API: `_______________________`

**Sign-off:**
- [ ] Technical lead approved
- [ ] Client approved
- [ ] All tests passing
- [ ] Monitoring active
- [ ] Documentation complete

---

## Emergency Contacts

| Role | Contact | Phone/Email |
|------|---------|-------------|
| Developer | Your Name | your.email@example.com |
| AWS Support | - | [console.aws.amazon.com/support](https://console.aws.amazon.com/support) |
| Vercel Support | - | [vercel.com/support](https://vercel.com/support) |
| Render Support | - | [render.com/support](https://render.com/support) |

---

## Total Deployment Time Estimate

| Phase | Duration |
|-------|----------|
| AWS Infrastructure | 30 min |
| Backend Deployment | 20 min |
| Frontend Deployment | 15 min |
| Smoke Tests | 15 min |
| Monitoring Setup | 10 min |
| Security Review | 10 min |
| **Total** | **~100 minutes (1h 40m)** |

**🚀 Ready to ship!**
