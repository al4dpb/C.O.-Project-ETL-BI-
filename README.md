# Container Offices - BI Stack

Production-ready Business Intelligence stack for property management with automatic data refresh and cloud deployment.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                       User Interface                          │
│  Next.js (Vercel) - Dashboard, Analytics, Upload             │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│                      API Layer                                │
│  FastAPI (Render/Fly) - Query Proxy, S3 Presigned URLs      │
└────────────┬─────────────────────────────────────────────────┘
             │
    ┌────────┴────────┐
    ▼                 ▼
┌─────────┐    ┌──────────────┐
│   S3    │───▶│  MotherDuck  │
│  Lake   │    │  Warehouse   │
└────┬────┘    └──────────────┘
     │
     ▼
┌─────────┐    ┌──────────┐
│ Lambda  │───▶│   dbt    │
│ Excel→  │    │  Cloud   │
│ Parquet │    │(Optional)│
└─────────┘    └──────────┘
```

---

## 🚀 Quick Links

| Document | Purpose | Time |
|----------|---------|------|
| **[QUICKSTART_PRODUCTION.md](QUICKSTART_PRODUCTION.md)** | Deploy to production in 30 min | 30 min |
| **[RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md)** | Complete deployment checklist | 100 min |
| **[PRODUCTION_DEPLOY.md](PRODUCTION_DEPLOY.md)** | Full deployment guide with all details | Reference |
| **[SECURITY.md](SECURITY.md)** | Security guidelines & best practices | Reference |
| **[CLOUD_SETUP.md](CLOUD_SETUP.md)** | Cloud infrastructure setup | Reference |

---

## ⚡ Features

### Frontend (Next.js)
- 📊 **Interactive Dashboards** - Real-time property analytics
- 📈 **Revenue Trends** - Historical and forecasted metrics
- 🏢 **Property Overview** - Occupancy, revenue, and suite details
- 📤 **Upload Interface** - Browser-based Excel file uploads
- ⚡ **Real-time Updates** - Auto-refresh after data uploads
- 🎨 **Modern UI** - Built with Tailwind CSS and Radix UI

### Backend (FastAPI)
- 🔌 **REST API** - Query execution and data access
- 🔐 **S3 Presigned URLs** - Secure browser uploads
- 📊 **MotherDuck Integration** - Serverless DuckDB warehouse
- 🔄 **Query Proxy** - Server-side query execution
- 📝 **Auto Documentation** - OpenAPI/Swagger docs at `/docs`
- 🚀 **Docker Deployment** - Containerized for easy deployment

### Data Pipeline
- 📥 **Excel Ingestion** - Automatic Excel to Parquet conversion
- 🔄 **Lambda Triggers** - S3 event-driven processing
- 🏗️ **dbt Transformations** - Data modeling and quality checks
- 📊 **Bronze/Silver/Gold** - Medallion architecture
- ✅ **Data Validation** - Pandera schemas for quality
- 📈 **Time Series** - Revenue forecasting with SARIMAX

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 14 (App Router) | React framework with SSR |
| **UI** | Tailwind CSS, Radix UI | Styling and components |
| **Backend** | FastAPI | Python REST API |
| **Warehouse** | MotherDuck (DuckDB) | Serverless analytical database |
| **Lake** | AWS S3 | Object storage for raw/bronze/gold |
| **Transforms** | dbt | SQL transformations |
| **Auto-refresh** | AWS Lambda | Serverless Excel processing |
| **Validation** | Pandera | Data quality checks |
| **Deployment** | Vercel, Render, AWS | Cloud hosting |

---

## 📂 Project Structure

```
.
├── apps/
│   └── web/                    # Next.js frontend
│       ├── app/
│       │   ├── dashboard/      # Dashboard pages
│       │   │   ├── page.tsx    # Main dashboard
│       │   │   ├── upload/     # Upload interface
│       │   │   ├── loading.tsx # Loading skeleton
│       │   │   └── error.tsx   # Error boundary
│       │   └── api/bi/         # API proxy routes
│       ├── lib/bi.ts           # BI client library
│       └── package.json
│
├── services/
│   └── bi_api/                 # FastAPI backend
│       ├── main.py             # Main API app
│       ├── upload.py           # S3 upload handler
│       ├── Dockerfile
│       └── requirements.txt
│
├── lambda/
│   ├── handler.py              # Excel → Parquet processor
│   ├── requirements.txt
│   └── deploy.sh               # Deployment script
│
├── C.O. Project (ETL+BI)/      # Local ETL pipeline
│   ├── etl/                    # Python ETL modules
│   ├── warehouse/dbt/          # dbt project
│   ├── dashboard/              # Plotly Dash (legacy)
│   └── sql_queries/            # Analytical queries
│
├── cloud/
│   ├── aws/s3_setup.sh         # S3 bucket setup
│   └── dbt_cloud_profiles.yml  # dbt Cloud config
│
├── scripts/
│   ├── local_smoke_test.sh     # Local testing
│   ├── smoke_test.sh           # Full smoke test
│   └── print_runtime_env.sh    # Env variable checker
│
├── docker-compose.yml          # Local development
├── .gitignore                  # Secret files ignored
├── .pre-commit-config.yaml     # Secret detection hooks
├── SECURITY.md                 # Security guidelines
├── PRODUCTION_DEPLOY.md        # Full deployment guide
├── RELEASE_CHECKLIST.md        # Go-live checklist
└── QUICKSTART_PRODUCTION.md    # 30-min quick start
```

---

## 🚀 Getting Started

### Local Development

```bash
# 1. Clone repository
git clone <your-repo-url>
cd C.O.-Project-ETL-BI--main

# 2. Set up environment
cp .env.compose.example .env.compose
nano .env.compose  # Add your credentials

# 3. Run smoke test
./scripts/local_smoke_test.sh

# 4. Start frontend
cd apps/web
npm install
npm run dev

# 5. Open dashboard
open http://localhost:3000/dashboard
```

### Production Deployment

See **[QUICKSTART_PRODUCTION.md](QUICKSTART_PRODUCTION.md)** for 30-minute deployment guide.

---

## 📊 Data Flow

### Upload Flow

```
1. User uploads Excel via browser
   ↓
2. Frontend requests presigned URL from API
   ↓
3. API generates S3 presigned URL
   ↓
4. Browser uploads directly to S3 (raw/)
   ↓
5. S3 triggers Lambda function
   ↓
6. Lambda converts Excel → Parquet (bronze/)
   ↓
7. Lambda triggers dbt Cloud job (optional)
   ↓
8. dbt runs transformations (MotherDuck)
   ↓
9. Dashboard queries updated data
```

### Query Flow

```
1. Dashboard loads
   ↓
2. Frontend calls /api/bi/01_property_overview
   ↓
3. Next.js proxy forwards to FastAPI
   ↓
4. FastAPI reads SQL from file
   ↓
5. FastAPI queries MotherDuck
   ↓
6. Results returned to frontend
   ↓
7. UI renders charts and tables
```

---

## 🔐 Security

### Credentials Management

All credentials are stored in environment variables:

| Environment | File | Gitignored |
|-------------|------|------------|
| Local Dev | `.env.compose` | ✅ Yes |
| Frontend | `apps/web/.env.local` | ✅ Yes |
| Render | Dashboard UI | ✅ Encrypted |
| Vercel | Dashboard UI | ✅ Encrypted |
| Lambda | AWS Console | ✅ Encrypted |

### Pre-commit Hooks

```bash
# Install secret detection
pip install pre-commit
pre-commit install

# Scan for secrets
pre-commit run --all-files
```

See **[SECURITY.md](SECURITY.md)** for full security guidelines.

---

## 📈 Monitoring

### Health Checks

| Endpoint | Purpose | Expected |
|----------|---------|----------|
| `GET /v1/health` | API health | `{"status": "healthy"}` |
| `GET /v1/queries` | Available queries | List of query names |
| `GET /v1/tables` | Warehouse tables | List of tables |

### Logs

```bash
# API logs (Render)
# View in Render Dashboard → Logs

# Lambda logs (AWS)
aws logs tail /aws/lambda/co-excel-to-parquet --follow

# Frontend logs (Vercel)
# View in Vercel Dashboard → Logs
```

---

## 🧪 Testing

### Local Testing

```bash
# Full local smoke test
./scripts/local_smoke_test.sh

# Backend only
docker compose up -d bi_api
curl http://localhost:8080/v1/health

# Frontend only
cd apps/web && npm run dev
```

### Production Testing

```bash
# Health check
curl https://YOUR_API_URL/v1/health

# Query test
curl -X POST https://YOUR_API_URL/v1/query/01_property_overview \
  -H "Content-Type: application/json" -d '{}'

# Upload test
# See PRODUCTION_DEPLOY.md Part 5
```

---

## 📚 API Documentation

### Interactive Docs

Access OpenAPI documentation:
- **Local**: http://localhost:8080/docs
- **Production**: https://YOUR_API_URL/docs

### Key Endpoints

```http
GET  /v1/health              # Health check
GET  /v1/queries             # List available queries
GET  /v1/tables              # List warehouse tables
POST /v1/query/{name}        # Execute named query
POST /v1/upload-url          # Get presigned S3 upload URL
POST /v1/sql                 # Execute arbitrary SQL (read-only)
```

---

## 🔧 Configuration

### Environment Variables

**Required for all environments:**

```bash
# AWS
AWS_REGION=us-east-1
S3_BUCKET=co-data-prod
AWS_ACCESS_KEY_ID=<YOUR_KEY>
AWS_SECRET_ACCESS_KEY=<YOUR_SECRET>

# MotherDuck
MOTHERDUCK_TOKEN=<YOUR_TOKEN>

# Frontend (additional)
BI_API_URL=https://YOUR_API_URL
NEXT_PUBLIC_BASE_URL=https://YOUR_FRONTEND_URL
```

**Optional:**

```bash
# dbt Cloud webhook for auto-refresh
DBT_CLOUD_JOB_WEBHOOK=<WEBHOOK_URL>

# Local warehouse path (dev only)
WAREHOUSE_PATH=data/warehouse.duckdb
```

---

## 💰 Cost Breakdown

### Monthly Costs (Production)

| Service | Tier | Cost |
|---------|------|------|
| Vercel | Hobby | $0 |
| Render | Starter (512MB) | $7 |
| AWS S3 | <50GB storage | ~$2 |
| AWS Lambda | <10k invocations | $0 (free tier) |
| MotherDuck | <10GB | $0 (free tier) |
| **Total** | | **~$9/month** |

### Scaling Costs

| Users | API Tier | S3 Storage | MotherDuck | Monthly Cost |
|-------|----------|------------|------------|--------------|
| <100 | Starter | <50GB | <10GB | ~$10 |
| 100-1000 | Standard | <200GB | <50GB | ~$50 |
| 1000+ | Pro | <1TB | <200GB | ~$200 |

---

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes
3. Run tests: `./scripts/local_smoke_test.sh`
4. Run pre-commit: `pre-commit run --all-files`
5. Commit: `git commit -m "feat: add my feature"`
6. Push: `git push origin feature/my-feature`
7. Create Pull Request

---

## 📝 License

Proprietary - Container Offices Internal Use Only

---

## 🆘 Support

### Documentation

- 📚 **Full Deployment**: [PRODUCTION_DEPLOY.md](PRODUCTION_DEPLOY.md)
- ✅ **Go-Live Checklist**: [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md)
- ⚡ **Quick Start**: [QUICKSTART_PRODUCTION.md](QUICKSTART_PRODUCTION.md)
- 🔐 **Security**: [SECURITY.md](SECURITY.md)

### Troubleshooting

Common issues and solutions:

1. **CORS errors on upload**
   - Verify S3 CORS includes your frontend domain
   - Check browser console for exact error

2. **API returns 500 errors**
   - Check Render logs for stack trace
   - Verify environment variables are set
   - Test MotherDuck connection

3. **Dashboard shows no data**
   - Verify API health: `/v1/health`
   - Check if data exists in MotherDuck
   - Review browser console for errors

4. **Lambda not processing files**
   - Check S3 notification configuration
   - Review CloudWatch logs
   - Verify Lambda has S3 permissions

---

## 🚀 Deployment Status

| Environment | Status | URL |
|-------------|--------|-----|
| **Production** | 🟢 Live | `https://YOUR_DOMAIN` |
| **Staging** | 🟡 Preview | `https://staging.YOUR_DOMAIN` |
| **Development** | 🟢 Running | `http://localhost:3000` |

---

## 📊 Project Stats

- **Lines of Code**: ~5,000
- **API Endpoints**: 8
- **SQL Queries**: 10
- **dbt Models**: 15
- **Test Coverage**: Core features
- **Deployment Time**: 30 minutes
- **Monthly Cost**: ~$9

---

## 🎯 Roadmap

### Q1 2025
- [x] Cloud deployment
- [x] Auto-refresh pipeline
- [ ] Authentication (NextAuth.js)
- [ ] Custom domain setup

### Q2 2025
- [ ] Multi-tenant support
- [ ] Advanced analytics (forecasting)
- [ ] Email notifications
- [ ] Mobile responsive design

### Q3 2025
- [ ] API rate limiting
- [ ] Caching layer (Redis)
- [ ] Advanced permissions
- [ ] Audit logging

---

**Built with ❤️ for Container Offices**

🚀 **Ready to ship!**
