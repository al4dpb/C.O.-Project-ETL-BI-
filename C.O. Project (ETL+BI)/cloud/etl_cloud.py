"""
Cloud ETL Pipeline for Container Offices
Uploads bronze data to S3 and syncs with MotherDuck warehouse
"""
import os
import boto3
from pathlib import Path
from datetime import datetime
import duckdb
from dotenv import load_dotenv

# Load environment variables
load_dotenv('cloud/.env')

AWS_PROFILE = os.getenv('AWS_PROFILE', 'co-pipeline')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')
S3_BUCKET = os.getenv(f'AWS_S3_BUCKET_{ENVIRONMENT.upper()}')
MOTHERDUCK_TOKEN = os.getenv('MOTHERDUCK_TOKEN')
MOTHERDUCK_DATABASE = os.getenv('MOTHERDUCK_DATABASE', 'co_warehouse')

# Local paths
LOCAL_BRONZE_DIR = Path('data/bronze')
LOCAL_WAREHOUSE = Path('data/warehouse.duckdb')


class CloudPipeline:
    """Manages cloud ETL operations"""

    def __init__(self):
        """Initialize AWS and MotherDuck connections"""
        # AWS S3 client
        session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
        self.s3 = session.client('s3')

        # MotherDuck connection
        if not MOTHERDUCK_TOKEN:
            raise ValueError("MOTHERDUCK_TOKEN not set in environment")

        self.md_connection_string = f"md:{MOTHERDUCK_DATABASE}?motherduck_token={MOTHERDUCK_TOKEN}"

        print(f"✓ Initialized CloudPipeline")
        print(f"  Environment: {ENVIRONMENT}")
        print(f"  S3 Bucket: {S3_BUCKET}")
        print(f"  MotherDuck DB: {MOTHERDUCK_DATABASE}")

    def upload_bronze_to_s3(self, dry_run=False):
        """
        Upload local bronze parquet files to S3 data lake

        Args:
            dry_run: If True, only show what would be uploaded
        """
        print(f"\n{'DRY RUN: ' if dry_run else ''}Uploading bronze data to S3...")

        uploaded_count = 0

        for bronze_table in ['raw_dashboard_monthly', 'raw_expenses_monthly', 'raw_lease_rate_snapshot']:
            local_path = LOCAL_BRONZE_DIR / bronze_table

            if not local_path.exists():
                print(f"  ⚠ Skipping {bronze_table} (not found locally)")
                continue

            # Find all parquet files in partitions
            parquet_files = list(local_path.rglob('*.parquet'))

            for parquet_file in parquet_files:
                # Construct S3 key maintaining partition structure
                relative_path = parquet_file.relative_to(LOCAL_BRONZE_DIR)
                s3_key = f"bronze/{relative_path}"

                if dry_run:
                    print(f"  [DRY RUN] Would upload: {parquet_file} -> s3://{S3_BUCKET}/{s3_key}")
                else:
                    try:
                        self.s3.upload_file(
                            str(parquet_file),
                            S3_BUCKET,
                            s3_key,
                            ExtraArgs={
                                'Metadata': {
                                    'uploaded_at': datetime.now().isoformat(),
                                    'environment': ENVIRONMENT
                                }
                            }
                        )
                        print(f"  ✓ Uploaded: {s3_key}")
                        uploaded_count += 1
                    except Exception as e:
                        print(f"  ✗ Failed to upload {parquet_file}: {e}")

        print(f"\n{'DRY RUN: ' if dry_run else ''}Upload complete: {uploaded_count} files")
        return uploaded_count

    def sync_to_motherduck(self, tables=None):
        """
        Sync data from local DuckDB to MotherDuck

        Args:
            tables: List of table names to sync (None = all tables)
        """
        print(f"\nSyncing to MotherDuck ({MOTHERDUCK_DATABASE})...")

        if not LOCAL_WAREHOUSE.exists():
            print(f"  ✗ Local warehouse not found: {LOCAL_WAREHOUSE}")
            print(f"    Run 'make run' first to generate local warehouse")
            return

        # Connect to both databases
        local_con = duckdb.connect(str(LOCAL_WAREHOUSE))
        md_con = duckdb.connect(self.md_connection_string)

        # Get list of tables to sync
        if tables is None:
            # Get all tables from main schema
            tables_query = "SELECT table_name FROM information_schema.tables WHERE table_schema='main'"
            tables = [row[0] for row in local_con.execute(tables_query).fetchall()]

        print(f"  Tables to sync: {', '.join(tables)}")

        synced_count = 0
        for table in tables:
            try:
                # Read from local
                df = local_con.execute(f"SELECT * FROM {table}").df()

                # Write to MotherDuck (CREATE OR REPLACE)
                md_con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM df")

                row_count = len(df)
                print(f"  ✓ Synced {table}: {row_count} rows")
                synced_count += 1

            except Exception as e:
                print(f"  ✗ Failed to sync {table}: {e}")

        local_con.close()
        md_con.close()

        print(f"\nSync complete: {synced_count}/{len(tables)} tables")
        return synced_count

    def verify_s3_data(self):
        """Verify bronze data exists in S3"""
        print(f"\nVerifying S3 data in {S3_BUCKET}...")

        for prefix in ['bronze/raw_dashboard_monthly/',
                       'bronze/raw_expenses_monthly/',
                       'bronze/raw_lease_rate_snapshot/']:

            response = self.s3.list_objects_v2(
                Bucket=S3_BUCKET,
                Prefix=prefix,
                MaxKeys=10
            )

            if 'Contents' in response:
                count = response['KeyCount']
                print(f"  ✓ {prefix}: {count} files")
            else:
                print(f"  ⚠ {prefix}: No files found")

    def verify_motherduck_data(self):
        """Verify data exists in MotherDuck"""
        print(f"\nVerifying MotherDuck data in {MOTHERDUCK_DATABASE}...")

        md_con = duckdb.connect(self.md_connection_string)

        # Check key tables
        tables_to_check = [
            'prop_kpi_monthly',
            'building_kpi_monthly',
            'fact_expense_monthly',
            'dim_suite',
            'dim_tenant'
        ]

        for table in tables_to_check:
            try:
                result = md_con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                count = result[0]
                print(f"  ✓ {table}: {count} rows")
            except Exception as e:
                print(f"  ✗ {table}: Not found or error - {e}")

        md_con.close()


def main():
    """Run cloud pipeline"""
    import argparse

    parser = argparse.ArgumentParser(description='Container Offices Cloud ETL Pipeline')
    parser.add_argument('action', choices=['upload', 'sync', 'verify', 'full'],
                       help='Action to perform')
    parser.add_argument('--dry-run', action='store_true',
                       help='Dry run mode (show what would happen)')

    args = parser.parse_args()

    pipeline = CloudPipeline()

    if args.action == 'upload':
        pipeline.upload_bronze_to_s3(dry_run=args.dry_run)
        pipeline.verify_s3_data()

    elif args.action == 'sync':
        pipeline.sync_to_motherduck()
        pipeline.verify_motherduck_data()

    elif args.action == 'verify':
        pipeline.verify_s3_data()
        pipeline.verify_motherduck_data()

    elif args.action == 'full':
        # Full cloud deployment
        print("=== Full Cloud Pipeline ===\n")
        pipeline.upload_bronze_to_s3(dry_run=args.dry_run)
        if not args.dry_run:
            pipeline.sync_to_motherduck()
            pipeline.verify_s3_data()
            pipeline.verify_motherduck_data()


if __name__ == '__main__':
    main()
