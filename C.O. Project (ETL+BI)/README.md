# Container Offices ETL+BI Pipeline **V2**

Complete data pipeline with **history tracking, forecasting, and advanced BI** for Container Offices.

**Excel → Bronze (Partitioned) → Warehouse (SCD2) → Gold KPIs → Forecasts → Interactive Dashboard V2**

## 🚀 Quick Start

```bash
# 1. Setup environment (first time only)
make init
source .venv/bin/activate

# 2. Run the full V2 pipeline
make run
# This runs: ingest → quality → dbt → snapshots → forecasting → export

# 3. Launch interactive dashboard V2
make dashboard
```

**Dashboard V2 opens at: http://127.0.0.1:8050** 🎉

## ✨ What's New in V2

- ✅ **Append-Only History**: Monthly partitions preserve all data
- ✅ **SCD2 Snapshots**: Track lease changes over time
- ✅ **Rolling Windows**: 3/6/9/12-month KPI aggregations
- ✅ **Predictive Analytics**: SARIMAX forecasts (12 months ahead, P10/P50/P90)
- ✅ **NOI Calculation**: Net Operating Income tracking
- ✅ **Expense Tracking**: Budget vs Actual with categorization
- ✅ **Own-Use Toggle**: Exclude owner-occupied suites from metrics
- ✅ **Interactive Dashboard V2**: Window selection, forecast visualization

## 📊 Dashboard V2 Features

The **interactive BI dashboard V2** provides:

- ✅ **Time Window Selector** - View 3m/6m/9m/12m/YTD/All time periods
- ✅ **Own-Use Toggle** - Exclude owner-occupied suites from calculations
- ✅ **Forecast Visualization** - Toggle to show 12-month predictions with P10/P50/P90 bands
- ✅ **KPI Cards** - Occupancy, Revenue, NOI, Suite Status (updates with filters)
- ✅ **Revenue Trends** - Base vs Collected with optional forecasts
- ✅ **Occupancy Chart** - Historical + predicted trends
- ✅ **NOI Tracking** - Net Operating Income with forecasts
- ✅ **Building A vs B** - Comparative analysis
- ✅ **Collection Rate** - Payment efficiency
- ✅ **Expense Analysis** - Actual vs Budget by category
- ✅ **Suite Details Table** - Filterable, sortable lease data

See [DASHBOARD.md](DASHBOARD.md) for full dashboard documentation.

## 🏗️ Architecture V2

- **Bronze**: Raw Excel → **Partitioned Parquet** (by `as_of_month`, with MD5 deduplication)
- **Warehouse**: DuckDB with dbt
  - **Staging**: Incremental models reading from partitions
  - **Snapshots**: SCD2 for lease change history
  - **Marts**: Dimensions + Fact tables (rent, expenses)
  - **Gold**: Property & Building KPIs with NOI
- **Windows**: Rolling 3/6/9/12-month KPI aggregations
- **Forecasting**: SARIMAX predictions (Occupancy%, Revenue, NOI)
- **Exports**: CSV files for all gold tables + forecasts
- **Dashboard V2**: Interactive Dash app with filters & forecasts

## 📈 Pipeline Steps (V2)

1. **Ingest**: Excel → Bronze Partitions (`as_of_month=YYYY-MM/`)
   - Auto-detect as_of_month from Excel or filename
   - MD5 deduplication (skip if already ingested)
   - Extract: Dashboard, Expenses (NEW), Lease/Rate
2. **Validate**: Pandera quality checks (all partitions)
   - Hard-fail on violations
   - Log errors to `data/bronze/_errors/`
3. **Transform**: dbt models
   - **Staging**: Incremental, partition-aware
   - **Snapshots**: SCD2 for lease changes
   - **Marts**: fact_rent, fact_expense, dims
   - **Gold**: prop_kpi (with NOI), building_kpi, kpi_windows
4. **Forecast**: SARIMAX predictions
   - Occupancy%, Collected, NOI
   - 12 months ahead (P10/P50/P90)
5. **Export**: Gold tables + forecasts → CSV/Parquet
6. **Visualize**: Dashboard V2 with interactive controls

## 📂 Data Flow V2

```
CFO Excel Files (Monthly)
  ├─ Dashboard → raw_dashboard_monthly/as_of_month=2025-01/*.parquet
  ├─ Expenses  → raw_expenses_monthly/as_of_month=2025-01/*.parquet
  └─ Lease Rate → raw_lease_rate_snapshot/as_of_month=2025-01/*.parquet
        ↓
    Bronze (partitioned, validated with Pandera)
        ↓
    Warehouse (DuckDB + dbt)
      ├─ Staging (incremental): stg_dashboard, stg_expenses, stg_lease_rate
      ├─ Snapshots (SCD2): snap_lease_rate_scd2
      ├─ Marts: fact_rent, fact_expense, dim_suite, dim_tenant
      └─ Gold: prop_kpi, building_kpi, kpi_windows
        ↓
    Forecasting (SARIMAX)
      └─ prop_kpi_forecast.csv (12 months, P10/P50/P90)
        ↓
    CSV/Parquet Exports + Dashboard V2
```

## 🎯 Key Metrics (V2)

- **Occupancy %**: `leased_sqft / 9,917` (with/without own-use toggle)
- **$/SF/Year**: Revenue per square foot
- **Collection Rate**: % of rent collected
- **AR**: Accounts receivable (uncollected rent)
- **NOI (Proto)**: `collected - (fixed + variable expenses)`
- **NOI Margin %**: `(NOI / collected) * 100`
- **Building A vs B**: Performance breakdown (respects own-use toggle)
- **Rolling Windows**: 3/6/9/12-month averages
- **Forecasts**: 12-month predictions with confidence intervals

## 🛠️ Development (V2 Commands)

```bash
make run                    # Full pipeline (ingest → quality → dbt → forecast → export)
make ingest                 # Ingest Excel (default from .env)
make ingest-file FILE=...   # Ingest specific file
make quality                # Run Pandera validation
make dbt                    # Run dbt seed + run + test
make snapshot               # Run dbt snapshots (SCD2)
make dbt-full               # Run dbt seed + run + snapshot + test
make dbt-refresh            # Rebuild all dbt models from scratch
make forecast               # Generate SARIMAX forecasts
make forecast-excl-own-use  # Forecast excluding own-use
make export                 # Export gold tables to CSV
make dashboard              # Launch Dashboard V2
make test                   # Run pytest
make format                 # Format code
make clean                  # Remove data artifacts
make clean-all              # Remove everything including venv
make help                   # Show all commands
```

## 📚 Documentation

- [QUICKSTART.md](QUICKSTART.md) - Detailed setup and usage
- [DASHBOARD.md](DASHBOARD.md) - Dashboard features and customization

## ✨ What's Included (V2)

✅ **Append-only history** with monthly partitions
✅ **MD5 deduplication** (prevents duplicate ingestion)
✅ **Auto as_of_month detection** (from Excel or filename)
✅ **Expense tracking** (actual vs budget)
✅ **Quality validation** with Pandera (all partitions)
✅ **SCD2 snapshots** (lease change history)
✅ **Dimensional warehouse** (DuckDB + dbt)
✅ **NOI calculation** (collected - expenses)
✅ **Rolling windows** (3/6/9/12 months)
✅ **SARIMAX forecasting** (12 months, P10/P50/P90)
✅ **Interactive Dashboard V2** (filters, forecasts, toggles)
✅ **Own-use toggle** (exclude owner suites)
✅ **Comprehensive exports** (CSVs + Parquet)
✅ **Unit + dbt tests**
✅ **CI/CD ready** (GitHub Actions)
✅ **Fully documented**

## 🔄 V2 Upgrade Benefits

**From V1 → V2:**
- Monthly files create new partitions (no overwrites)
- Track full lease history via SCD2 snapshots
- Filter dashboards by time windows (3m/6m/9m/12m/YTD)
- Predict future performance (Occupancy, Revenue, NOI)
- Calculate true NOI with expense tracking
- Toggle to exclude own-use suites from all metrics
- View forecast confidence intervals (P10/P90)
- Analyze expenses vs budget by category
