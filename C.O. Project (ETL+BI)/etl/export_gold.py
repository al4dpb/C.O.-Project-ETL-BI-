"""Export Gold tables from DuckDB to CSV for BI visualization - V2."""
import duckdb
from pathlib import Path

from etl.config import WAREHOUSE_PATH, GOLD_DIR
from etl.utils import logger


def export_table_to_csv(conn: duckdb.DuckDBPyConnection, table_name: str, output_filename: str):
    """
    Export a table from DuckDB to CSV.

    Args:
        conn: DuckDB connection
        table_name: Name of table to export
        output_filename: Output CSV filename
    """
    output_path = Path(GOLD_DIR) / output_filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Exporting {table_name} to {output_path}...")

    # Export to CSV
    query = f"""
        COPY (SELECT * FROM {table_name})
        TO '{output_path}'
        (HEADER, DELIMITER ',')
    """

    conn.execute(query)

    # Count rows
    count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    logger.info(f"✓ Exported {count} rows to {output_filename}")


def main():
    """Export all Gold tables to CSV."""
    logger.info("=" * 60)
    logger.info("Starting Gold table exports (V2)")
    logger.info("=" * 60)

    # Connect to warehouse
    if not Path(WAREHOUSE_PATH).exists():
        logger.error(f"Warehouse not found: {WAREHOUSE_PATH}")
        logger.error("Run 'make dbt' first to build the warehouse")
        exit(1)

    conn = duckdb.connect(str(WAREHOUSE_PATH), read_only=True)

    # Export tables
    exports = [
        ("prop_kpi_monthly", "prop_kpi_monthly.csv"),
        ("building_kpi_monthly", "building_kpi_monthly.csv"),
        ("kpi_windows", "kpi_windows.csv"),
        ("fact_expense_monthly", "fact_expense_monthly.csv"),
    ]

    for table_name, filename in exports:
        try:
            export_table_to_csv(conn, table_name, filename)
        except Exception as e:
            logger.warning(f"Failed to export {table_name}: {e}")
            # Continue with other exports

    conn.close()

    logger.info("")
    logger.info("✓ Gold exports completed successfully")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
