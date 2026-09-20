# OpusMagus Marketing Website - Operations Runbook

## Daily Checks

```bash
# Check CloudFront health
aws cloudfront get-distribution --id DISTRIBUTION_ID

# Monitor error rates
aws cloudwatch get-metric-statistics --namespace AWS/CloudFront \
  --metric-name 4XXError --dimensions Name=DistributionId,Value=DIST_ID \
  --start-time 2026-01-01T00:00:00Z --end-time 2026-01-02T00:00:00Z --period 3600 --statistics Sum

# Check S3 bucket
aws s3 ls s3://opusmagus-com-prod/ --recursive --human-readable
```

## Weekly Maintenance

- Review CloudWatch alarms
- Check CloudFront cache hit ratio
- Validate SSL certificate renewal status
- Review access logs for anomalies

## Monthly Tasks

- Update service cards / portfolio
- Review analytics / conversion metrics
- Test DNS failover
- Backup S3 bucket versions

## Emergency Response

### Website Down
1. Check CloudFront distribution status
2. Verify S3 bucket is accessible
3. Check security group / WAF rules
4. Review CloudWatch logs

### SSL Certificate Issues
1. Check ACM console for status
2. Verify Route53 DNS validation records
3. Contact AWS Support if needed

### DDoS Attack
1. WAF automatically blocks suspicious traffic
2. Review WAF logs in CloudWatch
3. Escalate to AWS Shield if needed

## Disaster Recovery

```bash
# Full infrastructure rebuild
cdk destroy --force
cdk deploy --all

# Website content restore from S3 versions
# (S3 versioning enabled - can restore previous versions)
```

## Performance Monitoring

Key metrics to track:
- **LCP** (Largest Contentful Paint): Target < 2.5s
- **FID** (First Input Delay): Target < 100ms
- **CLS** (Cumulative Layout Shift): Target < 0.1
- **Cache Hit Ratio**: Target > 85%
- **Error Rate**: Target < 0.1%

Monitor via:
- Google PageSpeed Insights
- AWS CloudFront dashboards
- AWS CloudWatch metrics
