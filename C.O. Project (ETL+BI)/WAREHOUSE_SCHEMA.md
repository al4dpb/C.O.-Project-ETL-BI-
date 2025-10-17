# Container Offices Data Warehouse Schema

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        GOLD LAYER (KPIs)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────┐         ┌──────────────────────┐    │
│  │ prop_kpi_monthly     │         │ building_kpi_monthly │    │
│  │ ──────────────────── │         │ ──────────────────── │    │
│  │ • occupancy_pct      │         │ • building (A/B)     │    │
│  │ • collected          │         │ • occupancy_pct      │    │
│  │ • price_per_sf_yr    │         │ • occupied_sqft      │    │
│  │ • accounts_receivable│         │ • vacant_count       │    │
│  └──────────────────────┘         └──────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────────┐
│                       MARTS LAYER (Facts/Dims)                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ fact_rent_monthly│  │  dim_suite   │  │   dim_tenant    │  │
│  │ ──────────────── │  │ ──────────── │  │ ─────────────── │  │
│  │ • rent_base      │  │ • suite_id   │  │ • tenant_id     │  │
│  │ • collected      │  │ • building   │  │ • tenant_name   │  │
│  │ • uncollected    │  │ • sqft       │  │ • is_own_use    │  │
│  │ • collection_%   │  └──────────────┘  └─────────────────┘  │
│  └──────────────────┘                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    STAGING LAYER (Cleaned Views)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────┐         ┌──────────────────────┐    │
│  │ stg_dashboard_monthly│         │   stg_lease_rate     │    │
│  │ ──────────────────── │         │ ──────────────────── │    │
│  │ • month              │         │ • suite_id           │    │
│  │ • rent_base          │         │ • building           │    │
│  │ • collected          │         │ • tenant             │    │
│  │ • leased_sqft        │         │ • sqft               │    │
│  └──────────────────────┘         │ • rent_monthly       │    │
│                                    │ • is_vacant          │    │
│                                    │ • is_own_use         │    │
│                                    └──────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     BRONZE LAYER (Validated)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  raw_dashboard_monthly.parquet                                  │
│  raw_lease_rate_snapshot.parquet                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
                     TCO Excel.xlsx
```

## 🗂️ Table Catalog

### GOLD LAYER

#### `prop_kpi_monthly`
**Purpose**: Property-level monthly KPIs for executive reporting

| Column | Type | Description |
|--------|------|-------------|
| month | DATE | Report month |
| occupancy_pct | DOUBLE | Occupancy % (leased/total sqft) |
| leased_sqft | INTEGER | Total leased square feet |
| total_property_sqft | INTEGER | Total property sqft (9,917) |
| collected | DECIMAL(12,2) | Revenue collected |
| rent_base | DECIMAL(12,2) | Base rent amount |
| collection_rate_pct | DOUBLE | Collection efficiency % |
| price_per_sf_yr | DECIMAL(10,2) | Average $/SF/year |
| accounts_receivable | DECIMAL(12,2) | Uncollected rent (AR) |
| revenue_sqft | HUGEINT | Revenue-generating sqft |
| revenue | DECIMAL(12,2) | Total revenue |
| noi_proto | DECIMAL(12,2) | Proto net operating income |

**Rows**: 12 (one per month)
**Primary Use**: Dashboard KPI cards, trend analysis

---

#### `building_kpi_monthly`
**Purpose**: Building-level comparison (A vs B)

| Column | Type | Description |
|--------|------|-------------|
| month | DATE | Report month |
| building | VARCHAR | Building identifier (A or B) |
| total_sqft | HUGEINT | Total sqft in building |
| occupied_sqft | HUGEINT | Occupied sqft |
| revenue_sqft | HUGEINT | Revenue-generating sqft |
| occupancy_pct | DOUBLE | Building occupancy % |
| suite_count | BIGINT | Total suites in building |
| vacant_count | HUGEINT | Number of vacant suites |
| own_use_count | HUGEINT | Number of own-use suites |

**Rows**: 24 (12 months × 2 buildings)
**Primary Use**: Building comparison charts

---

### MARTS LAYER

#### `fact_rent_monthly`
**Purpose**: Monthly rent collection facts

| Column | Type | Description |
|--------|------|-------------|
| month | DATE | Report month |
| rent_base | DECIMAL(12,2) | Base rent amount |
| collected | DECIMAL(12,2) | Amount collected |
| uncollected | DECIMAL(12,2) | Amount uncollected |
| collection_rate_pct | DOUBLE | Collection % |
| total_billed | DECIMAL(13,2) | Total billed amount |
| leased_sqft | INTEGER | Leased square feet |
| price_per_sf_yr | DECIMAL(10,2) | Price per SF/year |

**Rows**: 12
**Primary Use**: Revenue analysis, collection tracking

---

#### `dim_suite`
**Purpose**: Suite dimension (slowly changing)

| Column | Type | Description |
|--------|------|-------------|
| suite_id | VARCHAR | Unique suite identifier |
| building | VARCHAR | Building (A or B) |
| sqft | INTEGER | Suite square footage |

**Rows**: 18
**Primary Use**: Suite analysis, capacity planning

---

#### `dim_tenant`
**Purpose**: Tenant dimension

| Column | Type | Description |
|--------|------|-------------|
| tenant_id | VARCHAR | MD5 hash of tenant name |
| tenant_name | VARCHAR | Tenant business name |
| is_own_use | BOOLEAN | Internal/owner use flag |

**Rows**: 18
**Primary Use**: Tenant analysis, roster reporting

---

### STAGING LAYER

#### `stg_dashboard_monthly`
**Purpose**: Cleaned dashboard data (view)

Reads from: `raw_dashboard_monthly.parquet`

| Column | Type |
|--------|------|
| month | DATE |
| rent_base | DECIMAL(12,2) |
| collected | DECIMAL(12,2) |
| uncollected | DECIMAL(12,2) |
| leased_sqft | INTEGER |
| price_per_sf_yr | DECIMAL(10,2) |

---

#### `stg_lease_rate`
**Purpose**: Cleaned lease/rate data (view)

Reads from: `raw_lease_rate_snapshot.parquet`

| Column | Type |
|--------|------|
| suite_id | VARCHAR |
| building | VARCHAR |
| tenant | VARCHAR |
| sqft | INTEGER |
| rent_monthly | DECIMAL(12,2) |
| rent_annual | DECIMAL(12,2) |
| rent_psf_yr | DECIMAL(10,2) |
| is_vacant | BOOLEAN |
| is_own_use | BOOLEAN |

---

## 🔗 Relationships

```
prop_kpi_monthly.month ──┐
building_kpi_monthly.month─┴─→ fact_rent_monthly.month

dim_suite.suite_id ──→ Source: stg_lease_rate
dim_tenant.tenant_id ──→ Source: stg_lease_rate (MD5 hash)
```

## 📈 Data Volumes

| Layer | Tables/Views | Total Rows | Size |
|-------|--------------|------------|------|
| Gold | 2 tables | 36 | ~10 KB |
| Marts | 3 tables | 48 | ~15 KB |
| Staging | 2 views | Dynamic | - |
| Bronze | 2 parquet | 31 | ~10 KB |

**Total Warehouse**: ~1 MB

## 🎯 Query Patterns

### Pattern 1: Latest Month KPIs
```sql
SELECT * FROM prop_kpi_monthly
WHERE month = (SELECT MAX(month) FROM prop_kpi_monthly)
```

### Pattern 2: Time-Series Analysis
```sql
SELECT month, occupancy_pct
FROM prop_kpi_monthly
WHERE month >= CURRENT_DATE - INTERVAL 6 MONTHS
ORDER BY month
```

### Pattern 3: Building Comparison
```sql
SELECT building, occupied_sqft, occupancy_pct
FROM building_kpi_monthly
WHERE month = (SELECT MAX(month) FROM building_kpi_monthly)
```

### Pattern 4: Tenant Roster
```sql
SELECT t.tenant_name, COUNT(DISTINCT s.suite_id) as suite_count
FROM dim_tenant t
JOIN stg_lease_rate s ON MD5(s.tenant) = t.tenant_id
GROUP BY t.tenant_name
```

## 🔄 Data Lineage

```
TCO Excel.xlsx
    ├─ Dashboard (2025) tab
    │   └─> raw_dashboard_monthly.parquet
    │       └─> stg_dashboard_monthly (view)
    │           ├─> fact_rent_monthly
    │           │   └─> prop_kpi_monthly
    │           └─> building_kpi_monthly
    │
    └─ Lease Rate tab
        └─> raw_lease_rate_snapshot.parquet
            └─> stg_lease_rate (view)
                ├─> dim_suite
                ├─> dim_tenant
                └─> building_kpi_monthly
```

## ⚙️ Maintenance

### Daily: Update Data
```bash
make run
```

### Weekly: Validate Quality
```bash
make test
```

### Monthly: Review Schema
```sql
-- Check data freshness
SELECT MAX(month) as latest_data FROM prop_kpi_monthly;

-- Verify row counts
SELECT 'prop_kpi_monthly' as table_name, COUNT(*) as rows FROM prop_kpi_monthly
UNION ALL
SELECT 'building_kpi_monthly', COUNT(*) FROM building_kpi_monthly
UNION ALL
SELECT 'dim_suite', COUNT(*) FROM dim_suite;
```

## 📚 Additional Documentation

- **SQL Queries**: See `sql_queries/` folder (10 ready-to-use queries)
- **PyCharm Setup**: See `PYCHARM_DATABASE.md`
- **Dashboard**: See `DASHBOARD.md`

---

*Schema Version: 1.0 | Last Updated: 2025-10-02*
