# 🚀 Container Offices Dashboard - Launch Guide

## For the Boss: 3 Commands to Success

### Step 1: First-Time Setup (5 minutes)
```bash
cd "/Users/alejandrodelpalacio/Desktop/codex/C.O. Project (ETL+BI)"
make init
source .venv/bin/activate
```

This installs all dependencies (pandas, duckdb, dbt, plotly, dash).

### Step 2: Build the Data Warehouse (30 seconds)
```bash
make run
```

This:
- ✅ Reads TCO Excel.xlsx
- ✅ Creates validated Bronze files
- ✅ Builds DuckDB warehouse
- ✅ Generates Gold KPIs
- ✅ Exports CSVs

You'll see:
```
✓ Saved 12 rows to raw_dashboard_monthly.parquet
✓ Saved 19 rows to raw_lease_rate_snapshot.parquet
✓ All Bronze validations passed
✓ dbt run completed (7 models)
✓ Gold exports completed
```

### Step 3: Launch the Dashboard (instant)
```bash
make dashboard
```

Opens at: **http://127.0.0.1:8050**

## 📊 What You'll See

### Top Row - KPI Cards
```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ Occupancy Rate  │ Monthly Revenue │ Price per SF/Yr │ Suite Status    │
│   88.9%         │   $19,030       │   $25.89        │   19 Total      │
│ 8,820/9,917 sqft│ Collection: 100%│ Annual average  │ Vacant: 3       │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

### Charts Section

**Revenue Trends**
- Line chart showing Rent Base vs Collected
- Filled area shows collection efficiency
- Hover to see exact amounts

**Occupancy Trend**
- Historical occupancy % over time
- Dashed line at 85% target
- See month-by-month changes

**Building A vs B**
- Side-by-side bar chart
- Occupied vs Total sqft per building
- Latest month snapshot

**Collection Rate**
- Bar chart of monthly collection %
- Target line at 100%
- Track payment performance

### Suite Details Table
```
Suite | Building | Tenant              | SqFt | Monthly | Annual  | $/SF/Yr | Status
------|----------|---------------------|------|---------|---------|---------|--------
201A  | A        | MPACT Group         | 218  | $400    | $4,800  | $22.02  | Leased
300B  | B        | Carlee Williams     | 1800 | $3,500  | $42,000 | $23.33  | Leased
101B  | B        | Budde Offices       | 285  | $650    | $7,800  | $27.37  | Own-Use
...
```

**Interactive Features:**
- 🔍 Search/filter any column
- ⬆️⬇️ Sort by clicking headers
- 🎨 Color-coded: Yellow=Vacant, Blue=Own-Use
- 📄 Pagination (10 per page)

## 🔄 Daily Workflow

### Update Data (when Excel changes)
```bash
# 1. Update the Excel file
# 2. Re-run pipeline
make run

# 3. Refresh browser (F5)
# Dashboard automatically shows new data
```

### Quick Checks
```bash
# See data files
ls -lh data/bronze/
ls -lh data/gold/

# View CSV exports
cat data/gold/prop_kpi_monthly.csv

# Run tests
make test
```

## 🎯 Use Cases

### Monthly Performance Review
1. Open dashboard
2. Check KPI cards (occupancy, revenue)
3. Review revenue trend chart
4. Compare to previous months

### Vacancy Management
1. Go to Suite Details table
2. Filter status column → "Vacant"
3. See which suites need leasing
4. Note sqft and building

### Building Comparison
1. Look at Building A vs B chart
2. Check occupancy% for each
3. Review suite table filtered by building
4. Identify optimization opportunities

### Collection Tracking
1. Check Collection Rate chart
2. Verify 100% target
3. Look at Accounts Receivable in KPI card
4. Review uncollected amounts if any

## 🛠️ Troubleshooting

**Dashboard won't start**
```bash
# Reinstall dependencies
pip install plotly dash pandas duckdb
```

**No data in charts**
```bash
# Rebuild warehouse
make run
```

**Port 8050 in use**
```bash
# Kill existing dashboard
pkill -f "run_dashboard"
```

**Excel not found**
```bash
# Check path
ls data/raw/TCO\ Excel.xlsx
```

## 📈 Advanced: Customization

### Change Colors
Edit `dashboard/app.py` line 20:
```python
COLORS = {
    'primary': '#2E86AB',    # Change to your brand color
    'success': '#06A77D',
    ...
}
```

### Add New Chart
1. Add query in `dashboard/data_loader.py`
2. Create callback in `dashboard/app.py`
3. Add to layout

See [DASHBOARD.md](DASHBOARD.md) for details.

## ✨ Summary

**One-time:**
```bash
make init && source .venv/bin/activate
```

**Daily use:**
```bash
make run        # Update data
make dashboard  # View insights
```

**That's it!** Your Container Offices business intelligence is now at your fingertips. 🎉

---

*Questions? Check README.md, QUICKSTART.md, or DASHBOARD.md*
