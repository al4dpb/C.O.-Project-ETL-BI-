"""
AWS Lambda handler for S3 Excel → Parquet conversion with dbt trigger
Triggered by S3 ObjectCreated events for *.xlsx files in raw/ prefix
"""
import os
import json
import boto3
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from io import BytesIO
from urllib.parse import unquote_plus
import requests
from datetime import datetime

# Environment variables
S3_BUCKET = os.getenv("S3_BUCKET", "co-data-prod")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DBT_CLOUD_JOB_WEBHOOK = os.getenv("DBT_CLOUD_JOB_WEBHOOK")  # Optional

# Initialize S3 client
s3_client = boto3.client("s3", region_name=AWS_REGION)


def lambda_handler(event, context):
    """
    Main Lambda handler

    Args:
        event: S3 event notification
        context: Lambda context

    Returns:
        dict: Response with status and message
    """
    print(f"Received event: {json.dumps(event)}")

    try:
        # Parse S3 event
        for record in event.get("Records", []):
            if record.get("eventName", "").startswith("ObjectCreated"):
                process_s3_object(record)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Processing complete"})
        }

    except Exception as e:
        print(f"Error processing event: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }


def process_s3_object(record):
    """
    Process a single S3 object: Excel → Parquet conversion

    Args:
        record: S3 event record
    """
    # Extract S3 object details
    s3_info = record["s3"]
    bucket = s3_info["bucket"]["name"]
    key = unquote_plus(s3_info["object"]["key"])

    print(f"Processing s3://{bucket}/{key}")

    # Validate file is Excel and in raw/ prefix
    if not key.startswith("raw/") or not key.endswith((".xlsx", ".xls")):
        print(f"Skipping non-Excel file or file outside raw/: {key}")
        return

    try:
        # Download Excel file from S3
        excel_obj = s3_client.get_object(Bucket=bucket, Key=key)
        excel_bytes = excel_obj["Body"].read()
        print(f"Downloaded {len(excel_bytes)} bytes from S3")

        # Read Excel sheets to DataFrames
        excel_file = BytesIO(excel_bytes)
        sheets = pd.read_excel(excel_file, sheet_name=None)  # Read all sheets
        print(f"Found {len(sheets)} sheets: {list(sheets.keys())}")

        # Convert each sheet to Parquet
        for sheet_name, df in sheets.items():
            if df.empty:
                print(f"Skipping empty sheet: {sheet_name}")
                continue

            # Generate Parquet output key
            # Example: raw/org/building/2025/01/15/file.xlsx → bronze/org/building/2025/01/15/file_SheetName.parquet
            parquet_key = generate_parquet_key(key, sheet_name)

            # Write DataFrame to Parquet
            write_parquet_to_s3(df, bucket, parquet_key)
            print(f"Wrote Parquet: s3://{bucket}/{parquet_key}")

        # Trigger dbt Cloud job if webhook configured
        if DBT_CLOUD_JOB_WEBHOOK:
            trigger_dbt_job(key)

        print(f"Successfully processed {key}")

    except Exception as e:
        print(f"Error processing {key}: {str(e)}")
        raise


def generate_parquet_key(excel_key: str, sheet_name: str) -> str:
    """
    Generate Parquet S3 key from Excel key

    Args:
        excel_key: Original Excel file S3 key (e.g., raw/org/building/2025/01/15/file.xlsx)
        sheet_name: Excel sheet name

    Returns:
        str: Parquet S3 key (e.g., bronze/org/building/2025/01/15/file_Dashboard.parquet)
    """
    # Replace raw/ prefix with bronze/
    parquet_key = excel_key.replace("raw/", "bronze/", 1)

    # Replace .xlsx with _SheetName.parquet
    base_key = parquet_key.rsplit(".", 1)[0]  # Remove extension
    sheet_safe = sheet_name.replace(" ", "_").replace("/", "_")  # Sanitize sheet name
    parquet_key = f"{base_key}_{sheet_safe}.parquet"

    return parquet_key


def write_parquet_to_s3(df: pd.DataFrame, bucket: str, key: str):
    """
    Write DataFrame to S3 as Parquet

    Args:
        df: pandas DataFrame
        bucket: S3 bucket name
        key: S3 object key
    """
    # Convert DataFrame to PyArrow Table
    table = pa.Table.from_pandas(df)

    # Write to in-memory buffer
    buffer = BytesIO()
    pq.write_table(
        table,
        buffer,
        compression="snappy",
        use_dictionary=True,
        write_statistics=True
    )

    # Upload to S3
    buffer.seek(0)
    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=buffer.getvalue(),
        ContentType="application/octet-stream",
        Metadata={
            "source_format": "excel",
            "converted_at": datetime.utcnow().isoformat(),
            "rows": str(len(df)),
            "columns": str(len(df.columns))
        }
    )


def trigger_dbt_job(source_key: str):
    """
    Trigger dbt Cloud job via webhook

    Args:
        source_key: S3 key of source file that triggered the job
    """
    try:
        payload = {
            "cause": f"S3 upload: {source_key}",
            "git_sha": None,
            "schema_override": None,
            "steps_override": None
        }

        response = requests.post(
            DBT_CLOUD_JOB_WEBHOOK,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        if response.status_code == 200:
            print(f"dbt job triggered successfully for {source_key}")
        else:
            print(f"dbt job trigger failed: {response.status_code} {response.text}")

    except Exception as e:
        # Log but don't fail - dbt trigger is optional
        print(f"Error triggering dbt job: {str(e)}")


# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        "Records": [
            {
                "eventName": "ObjectCreated:Put",
                "s3": {
                    "bucket": {"name": "co-data-dev"},
                    "object": {"key": "raw/acme/b1/2025/01/15/test.xlsx"}
                }
            }
        ]
    }

    result = lambda_handler(test_event, None)
    print(f"Result: {result}")
