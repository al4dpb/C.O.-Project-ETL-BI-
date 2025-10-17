# PyCharm Database Tools Setup

## Quick Setup: DuckDB in PyCharm

### Step 1: Open Database Tool Window

1. In PyCharm, go to **View → Tool Windows → Database** (or press `⌘+1` then select Database)
2. Click the **+** button → **Data Source** → **DuckDB**

### Step 2: Configure DuckDB Connection

**Connection Details:**
- **Name**: `Container Offices Warehouse`
- **Driver**: DuckDB (PyCharm will download driver if needed)
- **Database**:
  ```
  /Users/alejandrodelpalacio/Desktop/codex/C.O. Project (ETL+BI)/data/warehouse.duckdb
  ```
  Or use the project-relative path: `$PROJECT_DIR$/data/warehouse.duckdb`

**Driver Setup (if needed):**
1. Click "Download missing driver files"
2. PyCharm will automatically download DuckDB JDBC driver

### Step 3: Test Connection

1. Click **Test Connection**
2. Should see: ✅ "Connection successful"
3. Click **OK** to save

### Step 4: Explore Your Data

Once connected, you'll see:

```
Container Offices Warehouse
├── main (schema)
│   ├── 📊 building_kpi_monthly (24 rows)
│   ├── 📊 dim_suite (18 rows)
│   ├── 📊 dim_tenant (18 rows)
│   ├── 📊 fact_rent_monthly (12 rows)
│   ├── 📊 prop_kpi_monthly (12 rows)
│   ├── 👁️ stg_dashboard_monthly (view)
│   └── 👁️ stg_lease_rate (view)
```

## 📊 Database Schema

### Tables Overview

#### 1. **prop_kpi_monthly** - Property-Level KPIs
```sql
month                    DATE           -- Report month
occupancy_pct           DOUBLE         -- Occupancy percentage
leased_sqft             INTEGER        -- Square feet leased
collected               DECIMAL(12,2)  -- Revenue collected
rent_base               DECIMAL(12,2)  -- Base rent
collection_rate_pct     DOUBLE         -- Collection rate %
price_per_sf_yr         DECIMAL(10,2)  -- Price per SF/year
accounts_receivable     DECIMAL(12,2)  -- AR (uncollected)
revenue_sqft            HUGEINT        -- Revenue-generating sqft
```

#### 2. **building_kpi_monthly** - Building A vs B
```sql
month                    DATE           -- Report month
building                VARCHAR        -- 'A' or 'B'
total_sqft              HUGEINT        -- Total sqft in building
occupied_sqft           HUGEINT        -- Occupied sqft
occupancy_pct           DOUBLE         -- Occupancy %
suite_count             BIGINT         -- Number of suites
vacant_count            HUGEINT        -- Vacant suites
own_use_count           HUGEINT        -- Own-use suites
```

#### 3. **fact_rent_monthly** - Rent Collection Facts
```sql
month                    DATE           -- Report month
rent_base               DECIMAL(12,2)  -- Base rent
collected               DECIMAL(12,2)  -- Collected amount
uncollected             DECIMAL(12,2)  -- Uncollected amount
collection_rate_pct     DOUBLE         -- Collection %
total_billed            DECIMAL(13,2)  -- Total billed
```

#### 4. **dim_suite** - Suite Dimension
```sql
suite_id                VARCHAR        -- Suite identifier
building                VARCHAR        -- 'A' or 'B'
sqft                    INTEGER        -- Square footage
```

#### 5. **dim_tenant** - Tenant Dimension
```sql
tenant_id               VARCHAR        -- Tenant hash ID
tenant_name             VARCHAR        -- Tenant name
is_own_use              BOOLEAN        -- Own-use flag
```

## 🔍 Ready-to-Use SQL Queries

All queries are in the `sql_queries/` folder. Just **open and run** in PyCharm:

### Quick Access in PyCharm

1. **Right-click** on `sql_queries/` folder
2. Select **Attach Directory** → **Container Offices Warehouse**
3. Now you can run any query with `⌘+Enter`

### Available Queries

1. **01_property_overview.sql** - Latest month KPIs
2. **02_revenue_trends.sql** - 6-month revenue history
3. **03_building_comparison.sql** - A vs B performance
4. **04_vacant_suites.sql** - Available suites
5. **05_tenant_roster.sql** - All current tenants
6. **06_occupancy_history.sql** - 12-month occupancy trend
7. **07_revenue_by_building.sql** - Revenue distribution
8. **08_kpi_summary.sql** - Executive dashboard (one query!)
9. **09_collection_analysis.sql** - Payment performance
10. **10_custom_analysis.sql** - Template for your queries

## 💡 How to Run Queries in PyCharm

### Method 1: From SQL File
1. Open any `.sql` file from `sql_queries/`
2. Press `⌘+Enter` (or click ▶️ button)
3. Results appear in bottom panel

### Method 2: Database Console
1. Right-click database → **Jump to Console**
2. Type your SQL
3. Press `⌘+Enter` to execute

### Method 3: Table Explorer
1. Double-click any table
2. Browse data in grid view
3. Sort, filter, export directly

## 📈 Common Tasks

### View Latest KPIs
```sql
-- Open: sql_queries/08_kpi_summary.sql
-- Press ⌘+Enter
```

### Find Vacant Suites
```sql
-- Open: sql_queries/04_vacant_suites.sql
-- Press ⌘+Enter
```

### Track Revenue Trends
```sql
-- Open: sql_queries/02_revenue_trends.sql
-- Press ⌘+Enter
```

### Compare Buildings
```sql
-- Open: sql_queries/03_building_comparison.sql
-- Press ⌘+Enter
```

## 🛠️ Advanced Features

### Export Query Results
1. Run any query
2. Right-click results → **Export Data**
3. Choose format: CSV, JSON, Excel, etc.

### Create Diagrams
1. Right-click database → **Diagrams** → **Show Visualization**
2. PyCharm will show table relationships

### Query History
- View → Tool Windows → Database Console
- Access all your previous queries
- Rerun with one click

### Data Editing
1. Double-click any table
2. Edit values directly in grid
3. Press `⌘+Enter` to commit changes

**⚠️ Note**: DuckDB warehouse is read-only in dashboard. To modify data, update Excel and run `make run`.

## 🔄 Updating Data

When you update the Excel file and run the pipeline:

```bash
make run
```

PyCharm will automatically see the new data. Just **refresh** the database view:
- Right-click database → **Refresh** (or press `⌘+F5`)

## 🎯 Pro Tips

### Tip 1: Pin Favorite Queries
- Right-click any SQL file → **Add to Favorites**
- Access from **Favorites** tool window

### Tip 2: Use Query Console
- Database tool window → **+** → **Query Console**
- Create scratch queries without saving files

### Tip 3: Compare Data
- Select two result sets
- Right-click → **Compare Tables**

### Tip 4: Auto-Complete
- PyCharm knows your schema
- Type `SELECT * FROM ` and get suggestions
- Column names auto-complete too

### Tip 5: Format SQL
- Select your SQL
- Press `⌘+⌥+L` to auto-format

## 📚 Additional Resources

### DuckDB Documentation
- [DuckDB SQL Reference](https://duckdb.org/docs/sql/introduction)
- Supports most PostgreSQL syntax
- Lightning-fast analytics queries

### PyCharm Database Tools
- [JetBrains Database Guide](https://www.jetbrains.com/help/pycharm/database-tool-window.html)

## 🆘 Troubleshooting

**"Can't find DuckDB driver"**
→ PyCharm → Preferences → Database → Drivers → DuckDB → Download

**"Database file locked"**
→ Close dashboard first (`Ctrl+C` in terminal)
→ DuckDB allows multiple readers, but check for writers

**"No tables showing"**
→ Run `make run` first to build warehouse
→ Refresh database view (`⌘+F5`)

**"Query returns no data"**
→ Check that pipeline has run successfully
→ Some months may have null values (future months)

## ✨ Summary

With PyCharm Database Tools, you can:

✅ **Browse** - Explore all tables and data visually
✅ **Query** - Run 10 pre-built SQL queries instantly
✅ **Analyze** - Export results to CSV/Excel
✅ **Monitor** - Track KPIs without leaving IDE
✅ **Debug** - Validate dbt transformations
✅ **Explore** - Create custom ad-hoc queries

**Everything is connected. Just open PyCharm and start exploring!** 🚀
