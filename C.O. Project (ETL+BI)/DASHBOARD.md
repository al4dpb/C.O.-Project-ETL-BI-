# Container Offices BI Dashboard

## Quick Start

```bash
# 1. Ensure pipeline has run at least once
make run

# 2. Launch the dashboard
make dashboard
```

The dashboard will open at **http://127.0.0.1:8050**

## Features

### 📊 KPI Summary Cards
- **Occupancy Rate** - Current occupancy % with leased/total sqft
- **Monthly Revenue** - Latest month revenue with collection rate
- **Price per SF/Year** - Average rental rate
- **Suite Status** - Total suites, vacant count, own-use count

### 📈 Interactive Charts

1. **Revenue Trends**
   - Rent base vs collected over time
   - Visual fill showing collection performance
   - Hover for exact values

2. **Occupancy Trend**
   - Historical occupancy percentage
   - Target line at 85%
   - Month-by-month changes

3. **Building A vs B Comparison**
   - Side-by-side comparison of occupied vs total sqft
   - Latest month data
   - Grouped bar chart

4. **Collection Rate**
   - Monthly collection percentage
   - Target line at 100%
   - Track payment efficiency

### 📋 Suite Details Table
- Complete list of all suites
- Columns: Suite ID, Building, Tenant, SqFt, Rents, Status
- **Interactive Features**:
  - ✅ Sort by any column
  - ✅ Filter/search suites
  - ✅ Color-coded status (Vacant = yellow, Own-Use = blue)
  - ✅ Paginated (10 per page)

## Data Sources

The dashboard connects directly to your **DuckDB warehouse** (`data/warehouse.duckdb`) and displays:
- Property-level KPIs from `prop_kpi_monthly`
- Building-level metrics from `building_kpi_monthly`
- Suite details from `stg_lease_rate`

## Updating Data

To refresh dashboard data:

```bash
# Update Excel file, then run:
make run

# Dashboard auto-reloads on page refresh
```

## Customization

### Colors
Edit `dashboard/app.py` → `COLORS` dictionary:
```python
COLORS = {
    'primary': '#2E86AB',    # Main color
    'success': '#06A77D',    # Success/positive
    'warning': '#F18F01',    # Warning/attention
    ...
}
```

### Charts
Each chart has a callback function in `dashboard/app.py`:
- `update_revenue_chart()`
- `update_occupancy_chart()`
- `update_building_comparison()`
- `update_collection_chart()`

Modify these to add new metrics or change visualizations.

### New Metrics
Add queries to `dashboard/data_loader.py`:
```python
def get_my_metric(self) -> pd.DataFrame:
    query = "SELECT ... FROM my_table"
    return self.conn.execute(query).df()
```

## Troubleshooting

**"No files found" error**
→ Run `make run` first to build the warehouse

**Dashboard won't start**
→ Ensure plotly/dash installed: `pip install plotly dash`

**Port 8050 already in use**
→ Stop other dashboard or change port in `run_dashboard.py`

**Charts empty**
→ Check that `make run` completed successfully and warehouse has data

## Architecture

```
Dashboard Flow:
  DuckDB Warehouse
      ↓
  DataLoader (data_loader.py)
      ↓
  Dash App (app.py)
      ↓
  Web Browser (http://127.0.0.1:8050)
```

## Dependencies

- **Dash** - Web framework
- **Plotly** - Interactive charts
- **Pandas** - Data manipulation
- **DuckDB** - Database connection

All installed via `make init` or `pip install plotly dash`.
