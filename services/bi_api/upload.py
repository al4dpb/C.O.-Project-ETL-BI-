"""
S3 Presigned Upload URL Generator
Generates secure URLs for browser-based file uploads to S3
"""
import os
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import boto3
from botocore.exceptions import ClientError

router = APIRouter()

S3_BUCKET = os.getenv("S3_BUCKET", "co-data-prod")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


class UploadRequest(BaseModel):
    """Request model for presigned upload URL"""
    org_id: str
    building_id: str
    filename: str
    content_type: str


class UploadResponse(BaseModel):
    """Response with presigned URL and object key"""
    uploadUrl: str
    objectKey: str
    expiresIn: int


@router.post("/v1/upload-url", response_model=UploadResponse)
def generate_upload_url(req: UploadRequest):
    """
    Generate a presigned S3 upload URL for browser-based uploads

    Args:
        req: Upload request with org_id, building_id, filename, content_type

    Returns:
        Presigned URL valid for 15 minutes and the S3 object key
    """
    # Generate S3 key with timestamp and organizational structure
    timestamp = int(time.time())
    date_path = time.strftime('%Y/%m/%d')
    key = f"raw/{req.org_id}/{req.building_id}/{date_path}/{timestamp}-{req.filename}"

    try:
        # Create S3 client
        s3_client = boto3.client("s3", region_name=AWS_REGION)

        # Generate presigned URL (15 minute expiry)
        expires_in = 900  # seconds

        presigned_url = s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": S3_BUCKET,
                "Key": key,
                "ContentType": req.content_type
            },
            ExpiresIn=expires_in
        )

        return UploadResponse(
            uploadUrl=presigned_url,
            objectKey=key,
            expiresIn=expires_in
        )

    except ClientError as e:
        raise HTTPException(
            status_code=500,
            detail=f"S3 error: {e.response['Error']['Message']}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate upload URL: {str(e)}"
        )


@router.post("/v1/upload-complete")
def mark_upload_complete(object_key: str):
    """
    Optional: Mark upload as complete and trigger processing

    Args:
        object_key: S3 object key that was uploaded
    """
    # TODO: Trigger ETL pipeline or add to processing queue
    return {
        "status": "acknowledged",
        "objectKey": object_key,
        "message": "Upload recorded. Processing will begin shortly."
    }
