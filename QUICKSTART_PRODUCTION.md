# ⚡ Production Quick Start - 30 Minute Deploy

Deploy your Container Offices BI Stack to production in 30 minutes.

---

## 🎯 What You'll Deploy

- ✅ **Frontend**: Next.js dashboard on Vercel (free tier)
- ✅ **Backend**: FastAPI on Render.com ($7/month)
- ✅ **Storage**: S3 data lake (AWS)
- ✅ **Warehouse**: MotherDuck (free tier up to 10GB)
- ✅ **Auto-refresh**: Lambda function for Excel → Parquet conversion

---

## 📋 Prerequisites (5 minutes)

Have these ready before starting:

1. **AWS Account**
   - Access Key ID
   - Secret Access Key
   - S3 buckets created: `co-data-dev`, `co-data-prod`

2. **MotherDuck Token**
   - Sign up at [motherduck.com](https://motherduck.com)
   - Get token from dashboard

3. **GitHub Repository**
   - Code pushed to `main` branch

4. **Accounts Created**
   - [Vercel](https://vercel.com) (free)
   - [Render.com](https://render.com) (free trial)

---

## 🚀 30-Minute Deployment

### Step 1: Deploy Backend API (10 minutes)

**1.1 Go to Render.com**
- Click "New +" → "Web Service"
- Connect your GitHub repo

**1.2 Configure Service**
```
Name: container-offices-api
Environment: Docker
Dockerfile Path: services/bi_api/Dockerfile
Docker Context: .
```

**1.3 Set Environment Variables**
```bash
AWS_REGION=us-east-1
S3_BUCKET=co-data-prod
AWS_ACCESS_KEY_ID=<YOUR_AWS_KEY>
AWS_SECRET_ACCESS_KEY=<YOUR_AWS_SECRET>
MOTHERDUCK_TOKEN=<YOUR_MOTHERDUCK_TOKEN>
```

**1.4 Set Health Check**
```
Health Check Path: /v1/health
```

**1.5 Deploy**
- Click "Create Web Service"
- Wait 5-7 minutes for build
- Copy your Render URL: `https://container-offices-api-XXXX.onrender.com`

**1.6 Verify**
```bash
curl https://YOUR_RENDER_URL/v1/health
# Should return: {"status": "healthy", "database": "motherduck"}
```

---

### Step 2: Deploy Frontend (10 minutes)

**2.1 Install Vercel CLI**
```bash
npm i -g vercel
vercel login
```

**2.2 Deploy**
```bash
cd apps/web
vercel
```

Follow prompts:
- Project name: `container-offices-ui`
- Directory: `./apps/web`
- Copy your Vercel URL: `https://container-offices-ui-XXXX.vercel.app`

**2.3 Set Environment Variables**

Go to Vercel Dashboard → Project → Settings → Environment Variables:

```bash
BI_API_URL=https://YOUR_RENDER_URL.onrender.com
NEXT_PUBLIC_BASE_URL=https://YOUR_VERCEL_URL.vercel.app
```

**2.4 Redeploy**
```bash
vercel --prod
```

**2.5 Verify**
Open in browser: `https://YOUR_VERCEL_URL.vercel.app/dashboard`

---

### Step 3: Configure S3 & Lambda (10 minutes)

**3.1 Set S3 CORS**
```bash
aws s3api put-bucket-cors \
  --bucket co-data-prod \
  --cors-configuration '{
    "CORSRules": [{
      "AllowedHeaders": ["*"],
      "AllowedMethods": ["PUT", "GET", "HEAD"],
      "AllowedOrigins": ["https://YOUR_VERCEL_URL.vercel.app"],
      "ExposeHeaders": ["ETag"],
      "MaxAgeSeconds": 3000
    }]
  }' \
  --profile co-pipeline
```

**3.2 Deploy Lambda (Quick Method)**

```bash
cd lambda

# Edit deploy.sh - set your Lambda IAM role ARN (see PRODUCTION_DEPLOY.md)
nano deploy.sh

# Deploy
./deploy.sh
```

**3.3 Configure S3 Trigger**

See `PRODUCTION_DEPLOY.md` Part 2.3 for full S3 notification setup.

---

## ✅ Verification (5 minutes)

### Test 1: API Health
```bash
curl https://YOUR_RENDER_URL/v1/health | jq
```
Expected: `{"status": "healthy"}`

### Test 2: Frontend Loads
```
https://YOUR_VERCEL_URL/dashboard
```
Should show dashboard with data.

### Test 3: Upload Flow
1. Go to `https://YOUR_VERCEL_URL/dashboard/upload`
2. Upload an Excel file
3. Check S3: `aws s3 ls s3://co-data-prod/raw/`
4. Wait 1 min, check bronze: `aws s3 ls s3://co-data-prod/bronze/`

---

## 🎉 You're Live!

Your production BI stack is now deployed!

**Access Points:**
- 📊 Dashboard: `https://YOUR_VERCEL_URL/dashboard`
- 🔧 API: `https://YOUR_RENDER_URL`
- 📚 API Docs: `https://YOUR_RENDER_URL/docs`

---

## 🔧 Troubleshooting

### Dashboard shows "No data"
1. Check API health: `curl YOUR_RENDER_URL/v1/health`
2. Verify env vars in Vercel match Render URL
3. Check Render logs for errors

### Upload fails with CORS error
1. Verify S3 CORS includes your Vercel domain
2. Check browser console for exact error
3. Ensure Vercel URL is correct in CORS config

### Lambda not processing files
1. Check S3 notification: `aws s3api get-bucket-notification-configuration --bucket co-data-prod`
2. View Lambda logs: `aws logs tail /aws/lambda/co-excel-to-parquet --follow`
3. Verify Lambda has S3 permissions

---

## 📚 Next Steps

1. **Add authentication** - Implement NextAuth.js
2. **Custom domain** - Configure in Vercel settings
3. **Monitoring** - Set up Sentry and CloudWatch alarms
4. **Documentation** - Share user guide with client

---

## 💰 Monthly Costs

| Service | Cost |
|---------|------|
| Vercel | $0 (free tier) |
| Render | $7 (starter) |
| AWS S3 | ~$2 |
| AWS Lambda | $0 (free tier) |
| MotherDuck | $0 (free tier) |
| **Total** | **~$9/month** |

---

## 🆘 Need Help?

- **Full deployment guide**: See `PRODUCTION_DEPLOY.md`
- **Release checklist**: See `RELEASE_CHECKLIST.md`
- **Security guide**: See `SECURITY.md`
- **Local testing**: Run `./scripts/local_smoke_test.sh`

---

**🚀 Ship it!**
