"""Tests for KPI calculation logic."""
import pytest
import pandas as pd
import duckdb
from pathlib import Path

from etl.config import WAREHOUSE_PATH, TOTAL_SQFT


@pytest.fixture
def warehouse_conn():
    """Connect to warehouse."""
    if not Path(WAREHOUSE_PATH).exists():
        pytest.skip("Warehouse not built yet")
    conn = duckdb.connect(str(WAREHOUSE_PATH), read_only=True)
    yield conn
    conn.close()


class TestOccupancyCalculation:
    """Test occupancy percentage calculations."""

    def test_occupancy_denominator(self, warehouse_conn):
        """Occupancy should use correct total sqft."""
        query = """
            SELECT
                occupancy_pct,
                leased_sqft,
                total_property_sqft
            FROM prop_kpi_monthly
            LIMIT 1
        """
        result = warehouse_conn.execute(query).fetchone()

        if result:
            _, leased_sqft, total_sqft = result
            assert total_sqft == TOTAL_SQFT, \
                f"Total sqft should be {TOTAL_SQFT}, got {total_sqft}"

    def test_occupancy_formula(self, warehouse_conn):
        """Occupancy % = (leased_sqft / total_sqft) * 100."""
        query = """
            SELECT
                occupancy_pct,
                leased_sqft,
                total_property_sqft
            FROM prop_kpi_monthly
            WHERE leased_sqft IS NOT NULL
        """
        results = warehouse_conn.execute(query).fetchall()

        for occ_pct, leased, total in results:
            if leased and total and total > 0:
                expected = (leased / total) * 100
                # Allow small floating point differences
                assert abs(occ_pct - expected) < 0.01, \
                    f"Occupancy mismatch: {occ_pct} vs {expected}"


class TestRevenueMetrics:
    """Test revenue metric calculations."""

    def test_accounts_receivable(self, warehouse_conn):
        """AR should equal uncollected rent."""
        query = """
            SELECT
                accounts_receivable,
                uncollected
            FROM prop_kpi_monthly
            WHERE uncollected IS NOT NULL
        """
        results = warehouse_conn.execute(query).fetchall()

        for ar, uncollected in results:
            assert ar == uncollected, \
                f"AR should equal uncollected: {ar} vs {uncollected}"

    def test_price_per_sf_valid(self, warehouse_conn):
        """Price per SF should be reasonable (if present)."""
        query = """
            SELECT price_per_sf_yr
            FROM prop_kpi_monthly
            WHERE price_per_sf_yr IS NOT NULL
        """
        results = warehouse_conn.execute(query).fetchall()

        for (price,) in results:
            # Sanity check: should be between $1 and $1000 per sf/yr
            assert 1 <= price <= 1000, \
                f"Price per SF seems unreasonable: ${price}"


class TestCollectionRate:
    """Test collection rate calculations."""

    def test_collection_rate_formula(self, warehouse_conn):
        """Collection rate = (collected / rent_base) * 100."""
        query = """
            SELECT
                collection_rate_pct,
                collected,
                rent_base
            FROM fact_rent_monthly
            WHERE rent_base > 0 AND collected IS NOT NULL
        """
        results = warehouse_conn.execute(query).fetchall()

        for rate, collected, base in results:
            if base and base > 0:
                expected = (collected / base) * 100
                assert abs(rate - expected) < 0.01, \
                    f"Collection rate mismatch: {rate} vs {expected}"

    def test_collection_rate_bounds(self, warehouse_conn):
        """Collection rate should be 0-100% (allow slight over for edge cases)."""
        query = """
            SELECT collection_rate_pct
            FROM fact_rent_monthly
            WHERE collection_rate_pct IS NOT NULL
        """
        results = warehouse_conn.execute(query).fetchall()

        for (rate,) in results:
            # Allow up to 110% for edge cases (prepayments, etc.)
            assert 0 <= rate <= 110, \
                f"Collection rate out of bounds: {rate}%"
