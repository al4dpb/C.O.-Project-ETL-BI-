"""Time series forecasting with SARIMAX for Container Offices KPIs."""
import argparse
import warnings
from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta

import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib

try:
    from pmdarima import auto_arima
    HAS_PMDARIMA = True
except ImportError:
    HAS_PMDARIMA = False
    warnings.warn("pmdarima not installed, using manual SARIMA order selection")

from etl.config import DATA_DIR, GOLD_DIR
from etl.utils import logger

warnings.filterwarnings('ignore', category=FutureWarning)


class KPIForecaster:
    """Forecaster for property KPIs using SARIMAX."""

    def __init__(self, metric_name: str, periods_ahead: list = [3, 6, 9, 12]):
        """
        Initialize forecaster.

        Args:
            metric_name: Name of metric to forecast
            periods_ahead: List of forecast horizons in months
        """
        self.metric_name = metric_name
        self.periods_ahead = periods_ahead
        self.model = None
        self.order = None
        self.seasonal_order = None

    def auto_select_order(self, series: pd.Series) -> tuple:
        """
        Auto-select SARIMA order using pmdarima or heuristics.

        Args:
            series: Time series data

        Returns:
            (order, seasonal_order) tuples
        """
        if HAS_PMDARIMA and len(series) >= 24:
            try:
                logger.info(f"Using pmdarima auto_arima for {self.metric_name}...")
                model = auto_arima(
                    series,
                    start_p=0, start_q=0, max_p=3, max_q=3,
                    seasonal=True, m=12,
                    start_P=0, start_Q=0, max_P=2, max_Q=2,
                    trace=False,
                    error_action='ignore',
                    suppress_warnings=True,
                    stepwise=True
                )
                order = model.order
                seasonal_order = model.seasonal_order
                logger.info(f"  Selected order: {order}, seasonal: {seasonal_order}")
                return order, seasonal_order
            except Exception as e:
                logger.warning(f"  pmdarima failed: {e}, using defaults")

        # Fallback: simple heuristic (pmdarima not available)
        if len(series) >= 24:
            order = (1, 1, 1)
            seasonal_order = (1, 1, 1, 12)
            logger.info("Using default order with seasonality (pmdarima not available)")
        else:
            order = (1, 0, 1)
            seasonal_order = (0, 0, 0, 0)
            logger.info("Using simple default order (pmdarima not available)")

        logger.info(f"Order: {order}, seasonal: {seasonal_order}")
        return order, seasonal_order

    def fit(self, df: pd.DataFrame, date_col: str = 'month', value_col: str = None):
        """
        Fit SARIMAX model on historical data.

        Args:
            df: DataFrame with date and value columns
            date_col: Name of date column
            value_col: Name of value column (defaults to metric_name)
        """
        value_col = value_col or self.metric_name

        # Prepare time series
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(date_col)
        series = df.set_index(date_col)[value_col].dropna()

        if len(series) < 3:
            logger.warning(f"Insufficient data for {self.metric_name} ({len(series)} points)")
            return None

        logger.info(f"Fitting SARIMAX for {self.metric_name} ({len(series)} observations)...")

        # Auto-select order
        self.order, self.seasonal_order = self.auto_select_order(series)

        # Fit model
        try:
            self.model = SARIMAX(
                series,
                order=self.order,
                seasonal_order=self.seasonal_order,
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            self.fitted_model = self.model.fit(disp=False, maxiter=200)
            logger.info(f"  ✓ Model fitted (AIC: {self.fitted_model.aic:.2f})")
            return self.fitted_model
        except Exception as e:
            logger.error(f"  ✗ Model fitting failed: {e}")
            return None

    def forecast(self, steps: int = 12, alpha: float = 0.1) -> pd.DataFrame:
        """
        Generate forecasts with prediction intervals.

        Args:
            steps: Number of steps ahead to forecast
            alpha: Significance level for prediction intervals (default 0.1 for 90% CI)

        Returns:
            DataFrame with forecast, lower, and upper bounds
        """
        if self.fitted_model is None:
            logger.error("Model not fitted. Call fit() first.")
            return None

        try:
            forecast_result = self.fitted_model.get_forecast(steps=steps)
            forecast_df = forecast_result.summary_frame(alpha=alpha)

            # Rename columns
            forecast_df = forecast_df.rename(columns={
                'mean': f'{self.metric_name}_p50',
                'mean_ci_lower': f'{self.metric_name}_p10',
                'mean_ci_upper': f'{self.metric_name}_p90',
            })

            # Add metadata
            forecast_df['metric'] = self.metric_name
            forecast_df['forecast_date'] = datetime.now().isoformat()

            return forecast_df[[
                'metric',
                f'{self.metric_name}_p10',
                f'{self.metric_name}_p50',
                f'{self.metric_name}_p90',
                'forecast_date'
            ]]
        except Exception as e:
            logger.error(f"Forecasting failed: {e}")
            return None

    def save_model(self, path: Path):
        """Save fitted model to disk."""
        if self.fitted_model is not None:
            joblib.dump(self.fitted_model, path)
            logger.info(f"Model saved to {path}")

    def load_model(self, path: Path):
        """Load fitted model from disk."""
        self.fitted_model = joblib.load(path)
        logger.info(f"Model loaded from {path}")


def load_historical_kpis() -> pd.DataFrame:
    """Load historical KPIs from gold layer."""
    gold_path = GOLD_DIR / "prop_kpi_monthly.csv"

    if not gold_path.exists():
        # Try loading from warehouse
        warehouse_path = DATA_DIR / "warehouse.duckdb"
        if warehouse_path.exists():
            import duckdb
            con = duckdb.connect(str(warehouse_path))
            df = con.execute("SELECT * FROM prop_kpi_monthly ORDER BY as_of_month, month").df()
            con.close()
            return df
        else:
            raise FileNotFoundError(f"No KPI data found at {gold_path} or in warehouse")

    return pd.read_csv(gold_path)


def main(exclude_own_use: bool = False, save_models: bool = True):
    """
    Run forecasting pipeline for all key metrics.

    Args:
        exclude_own_use: If True, use metrics excluding own-use suites
        save_models: If True, save fitted models to disk
    """
    logger.info("=" * 60)
    logger.info("Starting KPI Forecasting")
    logger.info("=" * 60)

    # Load historical data
    df_kpis = load_historical_kpis()
    logger.info(f"Loaded {len(df_kpis)} monthly KPI records")

    # Define metrics to forecast
    metrics = {
        'occupancy_pct': 'occupancy_pct_excl_own_use' if exclude_own_use else 'occupancy_pct',
        'collected': 'collected',
        'noi_proto': 'noi_proto',
    }

    all_forecasts = []

    for metric_label, metric_col in metrics.items():
        logger.info("")
        logger.info(f"Forecasting: {metric_label}")
        logger.info("-" * 40)

        # Initialize forecaster
        forecaster = KPIForecaster(metric_label, periods_ahead=[3, 6, 9, 12])

        # Fit model
        result = forecaster.fit(df_kpis, date_col='month', value_col=metric_col)

        if result is None:
            logger.warning(f"Skipping {metric_label} due to fitting failure")
            continue

        # Generate forecasts for max horizon
        max_horizon = max(forecaster.periods_ahead)
        forecast_df = forecaster.forecast(steps=max_horizon, alpha=0.2)  # 80% CI (P10-P90)

        if forecast_df is not None:
            all_forecasts.append(forecast_df)

            # Save model
            if save_models:
                model_dir = DATA_DIR / "models"
                model_dir.mkdir(exist_ok=True)
                model_path = model_dir / f"{metric_label}_sarimax.pkl"
                forecaster.save_model(model_path)

    if all_forecasts:
        # Combine all forecasts
        combined_df = pd.concat(all_forecasts, axis=0, ignore_index=True)

        # Add month labels
        latest_month = pd.to_datetime(df_kpis['month'].max())
        forecast_months = [latest_month + relativedelta(months=i+1) for i in range(12)]

        # Pivot to wide format for easier consumption
        output_rows = []
        for i, month in enumerate(forecast_months):
            row = {
                'forecast_month': month.strftime('%Y-%m'),
                'horizon': i + 1,
            }
            for forecast in all_forecasts:
                metric = forecast['metric'].iloc[0]
                if i < len(forecast):
                    row[f'{metric}_p10'] = forecast[f'{metric}_p10'].iloc[i]
                    row[f'{metric}_p50'] = forecast[f'{metric}_p50'].iloc[i]
                    row[f'{metric}_p90'] = forecast[f'{metric}_p90'].iloc[i]
            output_rows.append(row)

        output_df = pd.DataFrame(output_rows)

        # Save to gold
        forecast_path = GOLD_DIR / "prop_kpi_forecast.csv"
        forecast_path.parent.mkdir(parents=True, exist_ok=True)
        output_df.to_csv(forecast_path, index=False)
        logger.info("")
        logger.info(f"✓ Forecasts saved to {forecast_path}")

        # Also save parquet
        parquet_path = GOLD_DIR / "prop_kpi_forecast.parquet"
        output_df.to_parquet(parquet_path, index=False)
        logger.info(f"✓ Forecasts saved to {parquet_path}")

    logger.info("=" * 60)
    logger.info("✓ Forecasting completed")
    logger.info("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Forecast Container Offices KPIs")
    parser.add_argument(
        "--exclude-own-use",
        action="store_true",
        help="Exclude own-use suites from occupancy forecasts"
    )
    parser.add_argument(
        "--no-save-models",
        action="store_true",
        help="Don't save fitted models to disk"
    )
    args = parser.parse_args()

    main(exclude_own_use=args.exclude_own_use, save_models=not args.no_save_models)
