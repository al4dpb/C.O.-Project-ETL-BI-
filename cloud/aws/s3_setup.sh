#!/usr/bin/env bash
set -euo pipefail

REGION=us-east-1
PROFILE=co-pipeline
DEV_BUCKET=co-data-dev
PROD_BUCKET=co-data-prod

echo "=== S3 Data Lake Setup ==="
echo "Profile: $PROFILE"
echo "Region: $REGION"
echo ""

# Create dev bucket
echo "Creating dev bucket: $DEV_BUCKET"
aws s3api create-bucket --bucket $DEV_BUCKET --region $REGION \
  --create-bucket-configuration LocationConstraint=$REGION --profile $PROFILE 2>/dev/null || echo "  (bucket may already exist)"

# Create prod bucket
echo "Creating prod bucket: $PROD_BUCKET"
aws s3api create-bucket --bucket $PROD_BUCKET --region $REGION \
  --create-bucket-configuration LocationConstraint=$REGION --profile $PROFILE 2>/dev/null || echo "  (bucket may already exist)"

# Enable versioning
echo ""
echo "Enabling versioning..."
aws s3api put-bucket-versioning --bucket $DEV_BUCKET \
  --versioning-configuration Status=Enabled --profile $PROFILE

aws s3api put-bucket-versioning --bucket $PROD_BUCKET \
  --versioning-configuration Status=Enabled --profile $PROFILE

# Set CORS for browser uploads (edit the domain)
echo ""
echo "Setting CORS policy for $PROD_BUCKET..."
aws s3api put-bucket-cors --bucket $PROD_BUCKET --cors-configuration '{
  "CORSRules": [{
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["PUT", "GET", "HEAD"],
    "AllowedOrigins": ["https://YOUR-FRONTEND-DOMAIN.com", "http://localhost:3000"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }]
}' --profile $PROFILE

echo ""
echo "✓ S3 setup complete!"
echo ""
echo "Buckets:"
echo "  - s3://$DEV_BUCKET"
echo "  - s3://$PROD_BUCKET"
echo ""
echo "Next: Update CORS origin in this script with your actual frontend domain"
