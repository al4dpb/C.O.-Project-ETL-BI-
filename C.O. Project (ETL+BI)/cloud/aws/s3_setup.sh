#!/bin/bash
# AWS S3 Data Lake Setup for Container Offices BI
# Region: us-east-1
# Profile: co-pipeline

set -e

AWS_PROFILE="co-pipeline"
AWS_REGION="us-east-1"
DEV_BUCKET="co-data-dev"
PROD_BUCKET="co-data-prod"

echo "=== Container Offices S3 Data Lake Setup ==="
echo "Profile: $AWS_PROFILE"
echo "Region: $AWS_REGION"
echo ""

# Create development bucket
echo "Creating development bucket: $DEV_BUCKET"
aws s3 mb "s3://$DEV_BUCKET" \
    --region "$AWS_REGION" \
    --profile "$AWS_PROFILE" || echo "Bucket $DEV_BUCKET may already exist"

# Create production bucket
echo "Creating production bucket: $PROD_BUCKET"
aws s3 mb "s3://$PROD_BUCKET" \
    --region "$AWS_REGION" \
    --profile "$AWS_PROFILE" || echo "Bucket $PROD_BUCKET may already exist"

# Enable versioning on both buckets
echo ""
echo "Enabling versioning..."
aws s3api put-bucket-versioning \
    --bucket "$DEV_BUCKET" \
    --versioning-configuration Status=Enabled \
    --profile "$AWS_PROFILE"

aws s3api put-bucket-versioning \
    --bucket "$PROD_BUCKET" \
    --versioning-configuration Status=Enabled \
    --profile "$AWS_PROFILE"

# Create folder structure in dev bucket
echo ""
echo "Creating folder structure in $DEV_BUCKET..."
aws s3api put-object \
    --bucket "$DEV_BUCKET" \
    --key "bronze/raw_dashboard_monthly/" \
    --profile "$AWS_PROFILE"

aws s3api put-object \
    --bucket "$DEV_BUCKET" \
    --key "bronze/raw_expenses_monthly/" \
    --profile "$AWS_PROFILE"

aws s3api put-object \
    --bucket "$DEV_BUCKET" \
    --key "bronze/raw_lease_rate_snapshot/" \
    --profile "$AWS_PROFILE"

aws s3api put-object \
    --bucket "$DEV_BUCKET" \
    --key "gold/" \
    --profile "$AWS_PROFILE"

# Create folder structure in prod bucket
echo ""
echo "Creating folder structure in $PROD_BUCKET..."
aws s3api put-object \
    --bucket "$PROD_BUCKET" \
    --key "bronze/raw_dashboard_monthly/" \
    --profile "$AWS_PROFILE"

aws s3api put-object \
    --bucket "$PROD_BUCKET" \
    --key "bronze/raw_expenses_monthly/" \
    --profile "$AWS_PROFILE"

aws s3api put-object \
    --bucket "$PROD_BUCKET" \
    --key "bronze/raw_lease_rate_snapshot/" \
    --profile "$AWS_PROFILE"

aws s3api put-object \
    --bucket "$PROD_BUCKET" \
    --key "gold/" \
    --profile "$AWS_PROFILE"

# Set lifecycle policy for dev bucket (30 day retention)
echo ""
echo "Setting lifecycle policy for $DEV_BUCKET..."
cat > /tmp/lifecycle-dev.json <<EOF
{
    "Rules": [
        {
            "Id": "DeleteOldVersions",
            "Status": "Enabled",
            "NoncurrentVersionExpiration": {
                "NoncurrentDays": 30
            }
        }
    ]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
    --bucket "$DEV_BUCKET" \
    --lifecycle-configuration file:///tmp/lifecycle-dev.json \
    --profile "$AWS_PROFILE"

echo ""
echo "✓ S3 Data Lake setup complete!"
echo ""
echo "Buckets created:"
echo "  - s3://$DEV_BUCKET (development)"
echo "  - s3://$PROD_BUCKET (production)"
echo ""
echo "Folder structure:"
echo "  /bronze/raw_dashboard_monthly/"
echo "  /bronze/raw_expenses_monthly/"
echo "  /bronze/raw_lease_rate_snapshot/"
echo "  /gold/"
