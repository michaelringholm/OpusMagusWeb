# OpusMagus Website - Deployment Guide

## Quick Start (3 Steps)

### 1. Set Up Local Environment
```bash
cd opusmagus-cdk
./setup.sh          # macOS/Linux
# or
setup.bat           # Windows
```

### 2. Configure AWS Credentials
```bash
aws configure --profile opusmagus-prod
# Enter: AWS Access Key ID, Secret Access Key, Region (us-east-1), Output format (json)
```

### 3. Deploy Infrastructure to PROD
```bash
cdk deploy --all --profile opusmagus-prod
# Review changes, type 'y' to proceed
```

## After Deployment

```bash
# Upload website assets to S3
python scripts/deploy-assets.py

# Verify website is live
curl https://opusmagus.com
```

## Stack Details

- **StorageStack**: S3 bucket (opusmagus-com-prod) with versioning, encryption, public access blocked
- **SecurityStack**: ACM certificate (opusmagus.com + www.opusmagus.com), AWS WAF with managed rules
- **DistributionStack**: CloudFront CDN with caching, security headers, HTTP→HTTPS redirect
- **DNSStack**: Route53 A/CNAME records pointing to CloudFront
- **MonitoringStack**: CloudWatch logs, dashboards, alarms for all services

## Configuration

Edit `.env` before deployment:
```bash
PROD_ACCOUNT_ID=742197632521
PROD_REGION=us-east-1
PRIMARY_DOMAIN=opusmagus.com
WWW_DOMAIN=www.opusmagus.com
S3_BUCKET_NAME=opusmagus-com-prod
ENVIRONMENT_TAG=prod
```

## Troubleshooting

**Certificate pending validation?**
- Check Route53 CNAME record created by ACM
- Wait up to 5 minutes for AWS to validate ownership

**Stale content serving?**
```bash
aws cloudfront create-invalidation --distribution-id E1234ABCD --paths "/*" --profile opusmagus-prod
```

**S3 bucket not accessible?**
- Verify OAC (Origin Access Control) is configured in CloudFront
- Check S3 bucket policy allows CloudFront access only

**Build or deployment errors?**
```bash
# Clear CDK cache
rm -rf cdk.out
rm *.context.json

# Reinstall dependencies
pip install --upgrade aws-cdk-lib constructs
```

## Support

- AWS CDK Docs: https://docs.aws.amazon.com/cdk/v2/
- OpusMagus Email: hello@opusmagus.com
