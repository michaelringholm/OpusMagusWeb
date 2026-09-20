# Troubleshooting Guide

## Website Not Loading

### 403 Forbidden
- **Cause**: S3 bucket public access issue
- **Fix**: Verify CloudFront OAC is configured in DistributionStack

### 404 Not Found
- **Cause**: File missing from S3
- **Fix**: Re-run `python scripts/deploy-assets.py`

### Slow Load Times
- **Cause**: CloudFront cache not warmed
- **Fix**: First access is slow (cache build-up), subsequent loads are fast

## DNS Issues

### Domain not resolving
```bash
# Check DNS propagation
nslookup opusmagus.com
dig opusmagus.com

# Manual fix: Verify Route53 records
aws route53 list-resource-record-sets --hosted-zone-id ZONE_ID
```

### Stale content showing
```bash
# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id DIST_ID --paths "/*"

# Check cache status
aws cloudfront get-distribution-statistics --distribution-id DIST_ID
```

## Certificate Issues

### SSL certificate not issued
- ACM pending validation (wait 5-10 min)
- Route53 CNAME record not created
- Domain ownership not verified

### Certificate expired
- ACM auto-renewal failed
- Check SNS notifications for expiration warnings

## Deployment Errors

### "Stack already exists"
```bash
cdk deploy --all --force
```

### AWS credentials not found
```bash
# Configure AWS CLI
aws configure --profile opusmagus-prod

# Verify credentials
aws sts get-caller-identity --profile opusmagus-prod
```

### Out of memory during build
```bash
# Increase Node.js heap
export NODE_OPTIONS=--max-old-space-size=4096
cdk deploy
```

## Performance Check

```bash
# Page load time
curl -w "@curl-format.txt" https://opusmagus.com

# Check Core Web Vitals
# Use Google PageSpeed Insights: https://pagespeed.web.dev/

# CloudFront stats
aws cloudfront get-distribution-statistics --distribution-id DIST_ID
```

## Rollback

```bash
# Revert to previous S3 version
aws s3api list-object-versions --bucket opusmagus-com-prod

# Restore specific version
aws s3api get-object --bucket opusmagus-com-prod --key index.html --version-id VERSION_ID restored.html

# Delete failed CloudFormation stack
aws cloudformation delete-stack --stack-name OpusMagus-DistributionStack
```
