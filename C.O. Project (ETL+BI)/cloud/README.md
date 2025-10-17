# Container Offices Cloud BI Stack

Production-ready cloud infrastructure for Container Offices analytics.

## 🏗️ Architecture

```
┌─────────────────┐
│  Excel Source   │
│  (Local/S3)     │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  ETL Pipeline   │
│  (Python/dbt)   │
└────────┬────────┘
         │
         v
┌─────────────────┐       ┌──────────────────┐
│   AWS S3 Lake   │──────>│   MotherDuck     │
│  (Bronze Data)  │       │   (Warehouse)    │
└─────────────────┘       └────────┬─────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    v                             v
          ┌──────────────────┐         ┌──────────────────┐
          │   FastAPI API    │         │   Next.js UI     │
          │  (Data Service)  │<────────│   (Vercel)       │
          └──────────────────┘         └──────────────────┘
```

## 📦 Components

### 1. **AWS S3 Data Lake**
- **Buckets**: `co-data-dev`, `co-data-prod`
- **Structure**: `/bronze/`, `/gold/`
- **Format**: Partitioned Parquet
- **Versioning**: Enabled

### 2. **MotherDuck Warehouse**
- **Database**: `co_warehouse`
- **Connection**: Serverless DuckDB
- **Features**: S3 integration, dbt support

### 3. **FastAPI Backend**
- **Purpose**: REST API for data queries
- **Authentication**: JWT (planned)
- **Endpoints**: KPIs, expenses, forecasts

### 4. **Next.js Frontend**
- **Deployment**: Vercel
- **UI**: v0 generated components
- **Features**: Interactive dashboards

## 🚀 Quick Start

### Prerequisites

```bash
# Install dependencies
pip install boto3 duckdb python-dotenv

# Configure AWS CLI
aws configure --profile co-pipeline
# Enter: Access Key, Secret Key, Region (us-east-1)
```

### Step 1: Configure Environment

```bash
cd cloud/
cp .env.template .env
# Edit .env with your credentials
```

### Step 2: Set Up S3 Data Lake

```bash
chmod +x aws/s3_setup.sh
./aws/s3_setup.sh
```

### Step 3: Initialize MotherDuck

1. Get MotherDuck token: https://motherduck.com/
2. Add to `.env`: `MOTHERDUCK_TOKEN=your_token`
3. Run setup SQL:

```bash
duckdb "md:co_warehouse?motherduck_token=<TOKEN>" < motherduck/setup.sql
```

### Step 4: Upload Data to Cloud

```bash
# Dry run first
python etl_cloud.py upload --dry-run

# Actual upload
python etl_cloud.py upload

# Verify
python etl_cloud.py verify
```

### Step 5: Sync to MotherDuck

```bash
# Sync warehouse tables
python etl_cloud.py sync

# Or run full pipeline
python etl_cloud.py full
```

## 📊 Data Flow

### Local to Cloud

1. **Run local ETL** (existing pipeline):
   ```bash
   cd ..
   make run
   ```

2. **Upload bronze to S3**:
   ```bash
   python cloud/etl_cloud.py upload
   ```

3. **Sync warehouse to MotherDuck**:
   ```bash
   python cloud/etl_cloud.py sync
   ```

### Cloud-Native (Future)

1. **Ingest directly to S3**
2. **Run dbt against MotherDuck + S3**
3. **FastAPI queries MotherDuck**
4. **Next.js fetches from FastAPI**

## 🔐 Security

- **AWS Credentials**: Via AWS CLI profile (never hardcoded)
- **MotherDuck Token**: Environment variable only
- **API Keys**: Stored in Vercel environment
- **Secrets**: Use AWS Secrets Manager (future)

## 📁 File Structure

```
cloud/
├── README.md                    # This file
├── .env.template                # Environment template
├── .env                         # Your config (gitignored)
├── etl_cloud.py                 # Cloud ETL orchestrator
├── dbt_cloud_profiles.yml       # dbt MotherDuck config
├── aws/
│   └── s3_setup.sh              # S3 bucket creation
├── motherduck/
│   └── setup.sql                # Warehouse initialization
├── api/
│   └── (FastAPI backend - TBD)
└── frontend/
    └── (Next.js app - TBD)
```

## 🛠️ Commands Reference

### AWS S3

```bash
# List bronze data
aws s3 ls s3://co-data-dev/bronze/ --profile co-pipeline --recursive

# Copy local to S3
aws s3 sync ../data/bronze/ s3://co-data-dev/bronze/ --profile co-pipeline

# Download from S3
aws s3 sync s3://co-data-dev/bronze/ ../data/bronze/ --profile co-pipeline
```

### MotherDuck

```bash
# Connect to MotherDuck
duckdb "md:co_warehouse?motherduck_token=<TOKEN>"

# Query from S3 via MotherDuck
SELECT * FROM read_parquet('s3://co-data-dev/bronze/raw_dashboard_monthly/**/*.parquet', hive_partitioning=1);

# Run dbt against MotherDuck
cd ../warehouse/dbt
dbt run --profiles-dir ../../cloud --profile container_offices --target dev
```

### Pipeline Operations

```bash
# Full cloud deployment
python etl_cloud.py full

# Upload only
python etl_cloud.py upload

# Sync warehouse only
python etl_cloud.py sync

# Verify cloud data
python etl_cloud.py verify
```

## 🐛 Troubleshooting

### Issue: AWS credentials not found
```bash
# Check profile
aws sts get-caller-identity --profile co-pipeline

# Reconfigure
aws configure --profile co-pipeline
```

### Issue: MotherDuck connection failed
```bash
# Test token
duckdb "md:?motherduck_token=<TOKEN>" -c "SELECT 1"

# Check database exists
duckdb "md:?motherduck_token=<TOKEN>" -c "SHOW DATABASES"
```

### Issue: S3 access denied
```bash
# Check bucket policy
aws s3api get-bucket-policy --bucket co-data-dev --profile co-pipeline

# Test write access
echo "test" | aws s3 cp - s3://co-data-dev/test.txt --profile co-pipeline
```

## 📈 Next Steps

1. ✅ Set up S3 data lake
2. ✅ Initialize MotherDuck warehouse
3. ✅ Upload existing data to cloud
4. 🔲 Build FastAPI backend
5. 🔲 Create Next.js frontend with v0
6. 🔲 Deploy to Vercel
7. 🔲 Set up CI/CD (GitHub Actions)
8. 🔲 Add monitoring (Sentry, CloudWatch)

## 📞 Support

For issues or questions:
1. Check this README
2. Review error logs
3. Verify credentials and environment variables
4. Test each component independently
