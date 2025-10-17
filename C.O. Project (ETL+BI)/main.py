"""
Container Offices ETL+BI Pipeline - Main Entry Point

This script runs the complete pipeline:
1. Ingest Excel → Bronze (Parquet)
2. Quality validation (Pandera)
3. dbt transformations (Staging → Marts → Gold)
4. SCD2 snapshots
5. Forecasting (SARIMAX)
6. Export to CSV

Usage:
    python main.py              # Run full pipeline
    python main.py --help       # Show options
"""
import argparse
import sys
from pathlib import Path

from etl.utils import logger


def run_ingest():
    """Run Excel ingestion."""
    logger.info("Step 1/6: Running ingestion...")
    from etl.ingest_excel import main as ingest_main
    ingest_main()


def run_quality():
    """Run quality validation."""
    logger.info("Step 2/6: Running quality validation...")
    from etl.quality import main as quality_main
    quality_main()


def run_dbt():
    """Run dbt models."""
    logger.info("Step 3/6: Running dbt transformations...")
    import subprocess

    dbt_dir = Path("warehouse/dbt")
    commands = [
        ["dbt", "seed"],
        ["dbt", "run"],
        ["dbt", "snapshot"],
        ["dbt", "test"],
    ]

    for cmd in commands:
        logger.info(f"  Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=dbt_dir, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"dbt command failed: {' '.join(cmd)}")
            logger.error(result.stderr)
            sys.exit(1)


def run_forecast():
    """Run forecasting."""
    logger.info("Step 4/6: Running forecasting...")
    from predict.forecast import main as forecast_main
    forecast_main(exclude_own_use=False, save_models=True)


def run_export():
    """Run gold exports."""
    logger.info("Step 5/6: Running gold exports...")
    from etl.export_gold import main as export_main
    export_main()


def main():
    """Run the complete pipeline."""
    parser = argparse.ArgumentParser(
        description="Container Offices ETL+BI Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run full pipeline
  python main.py --skip-forecast    # Skip forecasting step
  python main.py --skip-export      # Skip export step
        """
    )
    parser.add_argument(
        "--skip-ingest",
        action="store_true",
        help="Skip Excel ingestion (use existing bronze data)"
    )
    parser.add_argument(
        "--skip-quality",
        action="store_true",
        help="Skip quality validation"
    )
    parser.add_argument(
        "--skip-dbt",
        action="store_true",
        help="Skip dbt transformations"
    )
    parser.add_argument(
        "--skip-forecast",
        action="store_true",
        help="Skip forecasting"
    )
    parser.add_argument(
        "--skip-export",
        action="store_true",
        help="Skip CSV exports"
    )

    args = parser.parse_args()

    logger.info("=" * 70)
    logger.info("Container Offices ETL+BI Pipeline V2")
    logger.info("=" * 70)

    try:
        if not args.skip_ingest:
            run_ingest()

        if not args.skip_quality:
            run_quality()

        if not args.skip_dbt:
            run_dbt()

        if not args.skip_forecast:
            run_forecast()

        if not args.skip_export:
            run_export()

        logger.info("")
        logger.info("=" * 70)
        logger.info("✓ Pipeline completed successfully!")
        logger.info("=" * 70)
        logger.info("")
        logger.info("Next steps:")
        logger.info("  - Launch dashboard: make dashboard")
        logger.info("  - View gold CSVs: ls -lh data/gold/")
        logger.info("  - Query warehouse: duckdb data/warehouse.duckdb")

    except KeyboardInterrupt:
        logger.warning("\nPipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\nPipeline failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
