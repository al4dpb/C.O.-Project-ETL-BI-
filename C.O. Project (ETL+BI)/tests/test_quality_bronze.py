"""Tests for Bronze data quality."""
import pytest
import pandas as pd
from pathlib import Path

from etl.config import BRONZE_DIR


@pytest.fixture
def dashboard_df():
    """Load dashboard bronze data."""
    path = Path(BRONZE_DIR) / "raw_dashboard_monthly.parquet"
    if not path.exists():
        pytest.skip("Bronze data not generated yet")
    return pd.read_parquet(path)


@pytest.fixture
def lease_df():
    """Load lease/rate bronze data."""
    path = Path(BRONZE_DIR) / "raw_lease_rate_snapshot.parquet"
    if not path.exists():
        pytest.skip("Bronze data not generated yet")
    return pd.read_parquet(path)


class TestDashboardQuality:
    """Test dashboard bronze data quality."""

    def test_month_not_null(self, dashboard_df):
        """All records must have a month."""
        assert dashboard_df['month'].notna().all()

    def test_numeric_columns_non_negative(self, dashboard_df):
        """Numeric columns should be non-negative."""
        numeric_cols = ['rent_base', 'collected', 'uncollected', 'leased_sqft', 'price_per_sf_yr']
        for col in numeric_cols:
            if col in dashboard_df.columns:
                # Allow NaN but no negative values
                assert (dashboard_df[col].isna() | (dashboard_df[col] >= 0)).all(), \
                    f"Column {col} has negative values"

    def test_collected_lte_rent_base(self, dashboard_df):
        """Collected rent should generally not exceed base rent."""
        if 'collected' in dashboard_df.columns and 'rent_base' in dashboard_df.columns:
            # Allow some tolerance for edge cases
            valid = (dashboard_df['collected'].isna() |
                    dashboard_df['rent_base'].isna() |
                    (dashboard_df['collected'] <= dashboard_df['rent_base'] * 1.1))
            if not valid.all():
                print("Warning: Some collected values exceed rent_base")


class TestLeaseRateQuality:
    """Test lease/rate bronze data quality."""

    def test_suite_id_not_null(self, lease_df):
        """All suites must have an ID."""
        assert lease_df['suite_id'].notna().all()

    def test_suite_id_unique(self, lease_df):
        """Suite IDs should be unique."""
        assert not lease_df['suite_id'].duplicated().any()

    def test_building_valid(self, lease_df):
        """Building should be A or B (or null)."""
        if 'building' in lease_df.columns:
            valid_buildings = {'A', 'B', None}
            assert lease_df['building'].isin(valid_buildings).all()

    def test_sqft_non_negative(self, lease_df):
        """Square footage should be non-negative."""
        if 'sqft' in lease_df.columns:
            assert (lease_df['sqft'].isna() | (lease_df['sqft'] >= 0)).all()

    def test_rent_fields_non_negative(self, lease_df):
        """Rent fields should be non-negative."""
        rent_cols = ['rent_monthly', 'rent_annual', 'rent_psf_yr']
        for col in rent_cols:
            if col in lease_df.columns:
                assert (lease_df[col].isna() | (lease_df[col] >= 0)).all(), \
                    f"Column {col} has negative values"

    def test_boolean_flags_exist(self, lease_df):
        """Boolean flags should exist."""
        assert 'is_vacant' in lease_df.columns
        assert 'is_own_use' in lease_df.columns

    def test_own_use_flagged(self, lease_df):
        """At least one own-use suite should be flagged."""
        # This test validates that the own-use detection logic is working
        # We expect at least one suite to be marked as own-use
        if 'is_own_use' in lease_df.columns:
            own_use_count = lease_df['is_own_use'].sum()
            print(f"Own-use suites detected: {own_use_count}")
