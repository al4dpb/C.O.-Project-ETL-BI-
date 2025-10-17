"""Data loader for Container Offices dashboard - V2."""
import pandas as pd
import duckdb
from pathlib import Path
from typing import Dict, Optional

# Paths
BASE_DIR = Path(__file__).parent.parent
WAREHOUSE_PATH = BASE_DIR / "data" / "warehouse.duckdb"
GOLD_DIR = BASE_DIR / "data" / "gold"


class DataLoader:
    """Load data from DuckDB warehouse for dashboard - V2 with windows & forecasts."""

    def __init__(self):
        """Initialize connection to warehouse."""
        if not WAREHOUSE_PATH.exists():
            raise FileNotFoundError(
                f"Warehouse not found: {WAREHOUSE_PATH}\n"
                "Run 'make run' first to build the warehouse."
            )
        self.conn = duckdb.connect(str(WAREHOUSE_PATH), read_only=True)

    def get_property_kpis(self, window: Optional[str] = None, exclude_own_use: bool = False) -> pd.DataFrame:
        """
        Get property-level monthly KPIs.

        Args:
            window: Optional window filter ('3m', '6m', '9m', '12m', 'ytd', or None for all)
            exclude_own_use: If True, use occupancy_pct_excl_own_use

        Returns:
            DataFrame with property KPIs
        """
        query = """
            SELECT
                as_of_month,
                month,
                rent_base,
                collected,
                uncollected,
                leased_sqft,
                price_per_sf_yr,
                collection_rate_pct,
                occupancy_pct,
                occupancy_pct_excl_own_use,
                accounts_receivable,
                noi_proto,
                noi_margin_pct,
                fixed_expenses,
                variable_expenses,
                total_expenses
            FROM prop_kpi_monthly
            WHERE month IS NOT NULL
            ORDER BY as_of_month DESC, month DESC
        """
        df = self.conn.execute(query).df()
        df['month'] = pd.to_datetime(df['month'])

        # Apply window filter
        if window and len(df) > 0:
            latest_month = df['month'].max()
            if window == 'ytd':
                year_start = pd.Timestamp(latest_month.year, 1, 1)
                df = df[df['month'] >= year_start]
            elif window in ['3m', '6m', '9m', '12m']:
                months = int(window[:-1])
                cutoff = latest_month - pd.DateOffset(months=months-1)
                df = df[df['month'] >= cutoff]

        return df

    def get_building_kpis(self, window: Optional[str] = None, exclude_own_use: bool = False) -> pd.DataFrame:
        """
        Get building-level (A vs B) monthly KPIs.

        Args:
            window: Optional window filter
            exclude_own_use: If True, use occupancy_pct_excl_own_use
        """
        query = """
            SELECT
                as_of_month,
                month,
                building,
                total_sqft,
                occupied_sqft,
                effective_occupied_sqft,
                vacant_sqft,
                own_use_sqft,
                occupancy_pct,
                occupancy_pct_excl_own_use,
                suite_count,
                vacant_count,
                own_use_count
            FROM building_kpi_monthly
            WHERE month IS NOT NULL AND building IS NOT NULL
            ORDER BY as_of_month DESC, month DESC, building
        """
        df = self.conn.execute(query).df()
        df['month'] = pd.to_datetime(df['month'])

        # Apply window filter
        if window and len(df) > 0:
            latest_month = df['month'].max()
            if window == 'ytd':
                year_start = pd.Timestamp(latest_month.year, 1, 1)
                df = df[df['month'] >= year_start]
            elif window in ['3m', '6m', '9m', '12m']:
                months = int(window[:-1])
                cutoff = latest_month - pd.DateOffset(months=months-1)
                df = df[df['month'] >= cutoff]

        return df

    def get_window_kpis(self) -> pd.DataFrame:
        """Get rolling window KPI aggregations."""
        query = """
            SELECT
                end_month,
                window_size,
                avg_occupancy_pct,
                avg_collection_rate_pct,
                avg_price_per_sf_yr,
                total_collected,
                total_rent_base,
                total_uncollected,
                avg_noi_proto,
                avg_noi_margin_pct
            FROM kpi_windows
            ORDER BY end_month DESC, window_size
        """
        df = self.conn.execute(query).df()
        return df

    def get_forecasts(self) -> Optional[pd.DataFrame]:
        """Get KPI forecasts (P10/P50/P90)."""
        forecast_path = GOLD_DIR / "prop_kpi_forecast.csv"

        if not forecast_path.exists():
            return None

        df = pd.read_csv(forecast_path)
        df['forecast_month'] = pd.to_datetime(df['forecast_month'] + '-01')
        return df

    def get_expense_facts(self) -> pd.DataFrame:
        """Get monthly expense facts."""
        query = """
            SELECT
                as_of_month,
                expense_category,
                total_actual,
                total_budget,
                total_variance,
                budget_adherence_pct
            FROM fact_expense_monthly
            ORDER BY as_of_month DESC, expense_category
        """
        df = self.conn.execute(query).df()
        return df

    def get_suite_details(self) -> pd.DataFrame:
        """Get suite-level lease details (latest snapshot)."""
        query = """
            SELECT
                suite_id,
                building,
                tenant,
                sqft,
                rent_monthly,
                rent_annual,
                rent_psf_yr,
                is_vacant,
                is_own_use
            FROM stg_lease_rate
            WHERE as_of_month = (SELECT MAX(as_of_month) FROM stg_lease_rate)
            ORDER BY building, suite_id
        """
        df = self.conn.execute(query).df()
        return df

    def get_summary_stats(self, exclude_own_use: bool = False) -> Dict:
        """
        Get summary statistics for KPI cards.

        Args:
            exclude_own_use: If True, use metrics excluding own-use suites
        """
        prop_kpis = self.get_property_kpis()
        suite_details = self.get_suite_details()

        # Latest month data
        latest = prop_kpis.iloc[0] if len(prop_kpis) > 0 else None

        if latest is not None:
            occupancy = (
                latest['occupancy_pct_excl_own_use']
                if exclude_own_use and 'occupancy_pct_excl_own_use' in latest
                else latest['occupancy_pct']
            )

            return {
                'occupancy': occupancy,
                'monthly_revenue': latest['collected'],
                'price_per_sf': latest['price_per_sf_yr'],
                'collection_rate': latest['collection_rate_pct'],
                'noi_proto': latest.get('noi_proto', 0),
                'noi_margin_pct': latest.get('noi_margin_pct', 0),
                'total_suites': len(suite_details),
                'vacant_suites': suite_details['is_vacant'].sum(),
                'own_use_suites': suite_details['is_own_use'].sum(),
                'total_sqft': 9917,
                'leased_sqft': latest['leased_sqft'],
            }
        else:
            return {
                'occupancy': 0,
                'monthly_revenue': 0,
                'price_per_sf': 0,
                'collection_rate': 0,
                'noi_proto': 0,
                'noi_margin_pct': 0,
                'total_suites': len(suite_details),
                'vacant_suites': suite_details['is_vacant'].sum(),
                'own_use_suites': suite_details['is_own_use'].sum(),
                'total_sqft': 9917,
                'leased_sqft': 0,
            }

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
