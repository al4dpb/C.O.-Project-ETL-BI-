#!/usr/bin/env bash
set -euo pipefail

# Lambda Deployment Script
# Packages handler.py with dependencies and deploys to AWS Lambda

FUNCTION_NAME="co-excel-to-parquet"
RUNTIME="python3.11"
HANDLER="handler.lambda_handler"
ROLE_ARN="<YOUR_LAMBDA_EXECUTION_ROLE_ARN>"  # Replace with actual ARN
S3_BUCKET_NOTIF="co-data-prod"  # Bucket to attach notification

echo "=== Lambda Deployment ==="
echo ""

# Step 1: Install dependencies
echo "Step 1: Installing dependencies..."
mkdir -p package
pip install -r requirements.txt -t package/ --platform manylinux2014_x86_64 --only-binary=:all:
echo "✓ Dependencies installed"
echo ""

# Step 2: Package Lambda
echo "Step 2: Packaging Lambda function..."
cd package
zip -r9 ../lambda-deployment.zip .
cd ..
zip -g lambda-deployment.zip handler.py
echo "✓ Lambda packaged: lambda-deployment.zip"
echo ""

# Step 3: Create/Update Lambda function
echo "Step 3: Deploying to AWS Lambda..."

# Check if function exists
if aws lambda get-function --function-name $FUNCTION_NAME 2>/dev/null; then
    echo "Updating existing function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://lambda-deployment.zip
else
    echo "Creating new function..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime $RUNTIME \
        --role $ROLE_ARN \
        --handler $HANDLER \
        --zip-file fileb://lambda-deployment.zip \
        --timeout 300 \
        --memory-size 512 \
        --environment "Variables={S3_BUCKET=$S3_BUCKET_NOTIF,AWS_REGION=us-east-1}"
fi

echo "✓ Lambda deployed"
echo ""

# Step 4: Add S3 trigger permission
echo "Step 4: Adding S3 invoke permission..."
aws lambda add-permission \
    --function-name $FUNCTION_NAME \
    --statement-id s3-trigger-permission \
    --action lambda:InvokeFunction \
    --principal s3.amazonaws.com \
    --source-arn "arn:aws:s3:::$S3_BUCKET_NOTIF" \
    2>/dev/null || echo "(Permission may already exist)"

echo "✓ Permission added"
echo ""

# Step 5: Get Lambda ARN for S3 notification config
LAMBDA_ARN=$(aws lambda get-function --function-name $FUNCTION_NAME --query 'Configuration.FunctionArn' --output text)
echo "Lambda ARN: $LAMBDA_ARN"
echo ""

echo "=== Next Steps ==="
echo "1. Configure S3 bucket notification using:"
echo "   ./configure_s3_notification.sh $LAMBDA_ARN"
echo ""
echo "2. Set Lambda environment variables in AWS Console:"
echo "   - S3_BUCKET: $S3_BUCKET_NOTIF"
echo "   - AWS_REGION: us-east-1"
echo "   - DBT_CLOUD_JOB_WEBHOOK: <your_dbt_webhook_url> (optional)"
echo ""

# Cleanup
rm -rf package lambda-deployment.zip

echo "✓ Deployment complete!"
