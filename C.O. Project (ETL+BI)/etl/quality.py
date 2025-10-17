"""Data quality validation with Pandera schemas - V2 with partition support."""
import pandas as pd
import pandera as pa
from pandera import Column, Check, DataFrameSchema
from pathlib import Path
from datetime import datetime

from etl.config import BRONZE_DIR, BRONZE_PARTITIONS
from etl.utils import logger


# Bronze schema: raw_dashboard_monthly (V2 with audit columns)
schema_dashboard_monthly = DataFrameSchema(
    {
        "as_of_month": Column(pa.String, nullable=False),
        "month": Column(pa.DateTime, nullable=False, coerce=True),
        "rent_base": Column(pa.Float, Check.ge(0), nullable=True),
        "collected": Column(pa.Float, Check.ge(0), nullable=True),
        "uncollected": Column(pa.Float, nullable=True),  # Can be negative if prepayment
        "leased_sqft": Column(pa.Float, Check.ge(0), nullable=True),
        "price_per_sf_yr": Column(pa.Float, Check.ge(0), nullable=True),
        "_file_md5": Column(pa.String, nullable=False),
        "_ingested_at": Column(pa.String, nullable=False),
    },
    strict=False,  # Allow extra columns
    coerce=True,
)


# Bronze schema: raw_expenses_monthly (V2 - updated for Dashboard extraction)
schema_expenses_monthly = DataFrameSchema(
    {
        "as_of_month": Column(pa.String, nullable=False),
        "month": Column(pa.DateTime, nullable=False, coerce=True),
        "item": Column(pa.String, nullable=False),
        "actual": Column(pa.Float, Check.ge(0), nullable=True),
        "expense_category": Column(pa.String, Check.isin(["fixed", "variable", "other"]), nullable=False),
        "_file_md5": Column(pa.String, nullable=False),
        "_ingested_at": Column(pa.String, nullable=False),
    },
    strict=False,
    coerce=True,
)


# Bronze schema: raw_lease_rate_snapshot (V2 with audit columns)
schema_lease_rate = DataFrameSchema(
    {
        "as_of_month": Column(pa.String, nullable=False),
        "suite_id": Column(pa.String, nullable=False),
        "building": Column(pa.String, Check.isin(["A", "B"]), nullable=True),
        "tenant": Column(pa.String, nullable=False),
        "sqft": Column(pa.Float, Check.ge(0), nullable=True),
        "rent_monthly": Column(pa.Float, Check.ge(0), nullable=True),
        "rent_annual": Column(pa.Float, Check.ge(0), nullable=True),
        "rent_psf_yr": Column(pa.Float, Check.ge(0), nullable=True),
        "is_vacant": Column(pa.Bool, nullable=False),
        "is_own_use": Column(pa.Bool, nullable=False),
        "_file_md5": Column(pa.String, nullable=False),
        "_ingested_at": Column(pa.String, nullable=False),
    },
    strict=False,
    coerce=True,
)


def log_validation_errors(
    table_name: str,
    partition: str,
    errors: pa.errors.SchemaErrors,
    df: pd.DataFrame
) -> None:
    """
    Log validation errors to error directory.

    Args:
        table_name: Name of bronze table
        partition: Partition path (e.g., as_of_month=2025-01)
        errors: Pandera schema errors
        df: DataFrame with errors
    """
    error_dir = BRONZE_DIR / "_errors" / table_name / partition
    error_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save error details
    error_file = error_dir / f"errors_{timestamp}.txt"
    with open(error_file, "w") as f:
        f.write(f"Validation errors for {table_name}/{partition}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write("=" * 80 + "\n\n")
        f.write(str(errors))

    logger.error(f"Validation errors logged to {error_file}")

    # Save sample of offending rows
    if hasattr(errors, "failure_cases") and errors.failure_cases is not None:
        failure_df = errors.failure_cases
        sample_file = error_dir / f"sample_failures_{timestamp}.csv"
        failure_df.to_csv(sample_file, index=False)
        logger.error(f"Sample failures saved to {sample_file}")


def validate_partition(
    table_name: str,
    partition_path: Path,
    schema: DataFrameSchema,
    hard_fail: bool = True
) -> bool:
    """
    Validate all Parquet files in a partition.

    Args:
        table_name: Name of bronze table
        partition_path: Path to partition (e.g., .../as_of_month=2025-01/)
        schema: Pandera DataFrameSchema
        hard_fail: If True, raise exception on validation failure

    Returns:
        True if validation passes

    Raises:
        pa.errors.SchemaError if validation fails and hard_fail=True
    """
    parquet_files = list(partition_path.glob("*.parquet"))

    if not parquet_files:
        logger.warning(f"No parquet files found in {partition_path}")
        return True

    partition_name = partition_path.name
    logger.info(f"Validating {len(parquet_files)} file(s) in {table_name}/{partition_name}...")

    all_valid = True

    for parquet_file in parquet_files:
        try:
            df = pd.read_parquet(parquet_file)
            logger.info(f"  - Loaded {len(df)} rows from {parquet_file.name}")

            # Validate with lazy=True to collect all errors
            schema.validate(df, lazy=True)
            logger.info(f"  ✓ Validation passed for {parquet_file.name}")

        except pa.errors.SchemaErrors as e:
            logger.error(f"  ✗ Validation failed for {parquet_file.name}")
            all_valid = False

            # Log errors
            log_validation_errors(table_name, partition_name, e, df)

            if hard_fail:
                raise

        except pa.errors.SchemaError as e:
            logger.error(f"  ✗ Validation failed for {parquet_file.name}")
            logger.error(str(e))
            all_valid = False

            if hard_fail:
                raise

    return all_valid


def validate_bronze_table(
    table_name: str,
    schema: DataFrameSchema,
    hard_fail: bool = True
) -> bool:
    """
    Validate all partitions of a bronze table.

    Args:
        table_name: Key in BRONZE_PARTITIONS
        schema: Pandera DataFrameSchema
        hard_fail: If True, raise exception on first failure

    Returns:
        True if all partitions pass validation
    """
    table_path = BRONZE_PARTITIONS[table_name]

    if not table_path.exists():
        logger.warning(f"Bronze table path does not exist: {table_path}")
        return True

    logger.info(f"Validating bronze table: {table_name}")

    # Find all partitions (as_of_month=*)
    partitions = sorted([p for p in table_path.iterdir() if p.is_dir() and p.name.startswith("as_of_month=")])

    if not partitions:
        logger.warning(f"No partitions found for {table_name}")
        return True

    logger.info(f"Found {len(partitions)} partition(s) for {table_name}")

    all_valid = True
    for partition in partitions:
        try:
            valid = validate_partition(table_name, partition, schema, hard_fail)
            if not valid:
                all_valid = False
        except Exception as e:
            logger.error(f"Partition validation failed: {partition.name}")
            if hard_fail:
                raise
            all_valid = False

    return all_valid


def main():
    """Validate all Bronze tables."""
    logger.info("=" * 60)
    logger.info("Starting Bronze validation (V2 - partitioned)")
    logger.info("=" * 60)

    validations = [
        ("dashboard", schema_dashboard_monthly),
        ("expenses", schema_expenses_monthly),
        ("lease_rate", schema_lease_rate),
    ]

    all_passed = True
    for table_name, schema in validations:
        try:
            logger.info("")
            passed = validate_bronze_table(table_name, schema, hard_fail=True)
            if not passed:
                all_passed = False
        except Exception as e:
            logger.error(f"Validation failed for {table_name}: {e}")
            all_passed = False
            # Continue with other tables instead of exiting immediately

    logger.info("")
    logger.info("=" * 60)
    if all_passed:
        logger.info("✓ All Bronze validations passed")
    else:
        logger.error("✗ Some Bronze validations failed")
        logger.error("Check data/bronze/_errors/ for details")
        exit(1)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
