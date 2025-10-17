# Quick Start Guide

## Setup (First Time)

```bash
# 1. Create virtual environment and install dependencies
make init

# 2. Activate virtual environment
source .venv/bin/activate
```

## Running the Pipeline

```bash
# Run complete pipeline: Excel → Bronze → Warehouse → Gold → CSV
make run
```

This will:
1. ✅ Extract data from `data/raw/TCO Excel.xlsx`
2. ✅ Create Bronze Parquet files (validated)
3. ✅ Build DuckDB warehouse with dbt
4. ✅ Generate Gold KPI tables
5. ✅ Export CSVs to `data/gold/`

## Outputs

### Bronze (Parquet)
- `data/bronze/raw_dashboard_monthly.parquet` - 12 monthly records
- `data/bronze/raw_lease_rate_snapshot.parquet` - 19 suite leases

### Warehouse (DuckDB)
- `data/warehouse.duckdb` - Full dimensional model

### Gold (CSV for BI)
- `data/gold/prop_kpi_monthly.csv` - Property-level KPIs
- `data/gold/building_kpi_monthly.csv` - Building A vs B metrics

## Key Metrics Available

**Property KPIs** (`prop_kpi_monthly.csv`):
- `occupancy_pct` - Occupancy percentage (leased/9,917 sqft)
- `price_per_sf_yr` - Revenue per square foot annually
- `accounts_receivable` - Uncollected rent (AR)
- `collection_rate_pct` - % of rent collected
- `noi_proto` - Proto net operating income

**Building KPIs** (`building_kpi_monthly.csv`):
- Split all metrics by Building A vs B
- `occupied_sqft`, `revenue_sqft` per building
- `vacant_count`, `own_use_count`

## Data Quality

Bronze data is validated with Pandera schemas:
- Non-negative amounts
- Valid building codes (A/B)
- No null required fields

## BI Visualization (Next Steps)

### Option 1: Apache Superset
```bash
# Install Superset
pip install apache-superset

# Connect to data/gold/*.csv or data/warehouse.duckdb
```

### Option 2: Python Dashboards
```bash
pip install plotly dash pandas

# Read data/gold/prop_kpi_monthly.csv
# Create interactive charts
```

### Option 3: Excel/Power BI
Import `data/gold/*.csv` directly into your BI tool.

## Development

```bash
# Run just dbt models
make dbt

# Run tests
make test

# Format code
make format

# Clean generated data
make clean
```

## Troubleshooting

**"No module named etl"**
→ Make sure you're in the project root and venv is activated

**"Excel file not found"**
→ Ensure `data/raw/TCO Excel.xlsx` exists

**"dbt tests failing"**
→ Some months may have null data (future months), this is expected
→ Pipeline will still generate gold exports

## Project Structure

```
├── data/
│   ├── raw/              # TCO Excel.xlsx
│   ├── bronze/           # Validated Parquet
│   ├── gold/             # BI-ready CSVs
│   └── warehouse.duckdb  # DuckDB database
├── etl/
│   ├── ingest_excel.py   # Excel → Bronze
│   ├── quality.py        # Validation
│   └── export_gold.py    # Gold → CSV
├── warehouse/dbt/
│   └── models/           # SQL transformations
│       ├── staging/      # Clean views
│       ├── marts/        # Facts/dims
│       └── gold/         # KPI tables
└── tests/                # Pytest tests
```
