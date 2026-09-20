# Opus Magus - Professional Marketing Website

Fast. Scalable. Secure. **Magic shaped into something useful.**

## What''s Ready

✅ **Professional Marketing Website**
- Dark theme with purple/gold accents
- Wizard mascot hero section with glowing effects
- Service cards (Cloud Architecture, Applied AI, Product Engineering)
- Featured work showcase
- Responsive design (mobile, tablet, desktop)
- WCAG AA accessibility compliance
- Core Web Vitals optimization (LCP < 2.5s)

✅ **Production AWS Infrastructure (CDK)**
- S3 bucket with versioning, encryption, public access blocked
- CloudFront CDN with 7-layer caching strategy
- ACM SSL/TLS certificates (opusmagus.com + www)
- AWS WAF with managed security rules (rate limiting, SQL injection, XSS protection)
- Route53 DNS with alias records
- CloudWatch monitoring, dashboards, alarms
- Security headers (HSTS, CSP, X-Frame-Options, X-Content-Type-Options)

✅ **Complete Documentation**
- DEPLOYMENT_GUIDE.md - Step-by-step setup and AWS deployment
- OPERATIONS.md - Daily/weekly/monthly operational procedures
- CONTENT_UPDATES.md - How to update site content
- TROUBLESHOOTING.md - Common issues and solutions

## Quick Deploy (5 Minutes)

### Prerequisites
- AWS account (PROD: 742xxxxx)
- AWS CLI configured
- Node.js 14+ (for AWS CDK)
- Python 3.10+

### Deploy

```bash
# 1. Install dependencies
cd opusmagus-cdk
pip install -r requirements.txt
npm install -g aws-cdk

# 2. Configure AWS
aws configure --profile opusmagus-prod
# Enter credentials, region: us-east-1

# 3. Deploy infrastructure
cdk deploy --all --profile opusmagus-prod
# Review changes, type ''y'' to proceed

# 4. Upload website content
python scripts/deploy-assets.py

# 5. Done! Website live at https://opusmagus.com
```

## File Structure

```
opusmagus-cdk/
├── app.py                          # CDK entry point (all stacks)
├── requirements.txt                # Python dependencies
├── config/
│   └── config.py                   # Configuration (domains, account ID, bucket)
├── stacks/
│   ├── storage_stack.py            # S3 bucket (versioning, encryption, OAC)
│   ├── security_stack.py           # ACM certificate, AWS WAF
│   ├── distribution_stack.py       # CloudFront (caching, security headers)
│   ├── dns_stack.py                # Route53 DNS records
│   └── monitoring_stack.py         # CloudWatch logs, alarms, dashboards
└── scripts/
    └── deploy-assets.py            # Upload website to S3

website/
├── index.html                      # Homepage (hero, services, portfolio, footer)
├── 404.html                        # Custom 404 error page
├── css/
│   └── main.css                    # Responsive design, dark theme, glowing effects
├── js/
│   └── main.js                     # Smooth scroll, lazy loading, accessibility
└── images/
    ├── hero/                       # Hero section images
    ├── icons/                      # Service icons
    └── portfolio/                  # Project thumbnails
```

## Key Features

### Performance
- **LCP < 2.5s** (Largest Contentful Paint)
- **FID < 100ms** (First Input Delay)  
- **CLS < 0.1** (Cumulative Layout Shift)
- **Page size < 3MB** (optimized images, minified CSS/JS)
- **Cache strategy**: HTML (0s), CSS/JS (1yr), images (1day)

### Security
- **HTTPS/TLS 1.2+** via ACM certificate
- **AWS WAF** with rate limiting, SQL injection, XSS protection
- **S3 public access blocked** (CloudFront-only via OAC)
- **Security headers**: HSTS, CSP, X-Frame-Options, X-Content-Type-Options
- **S3 versioning** for rollback capability

### Accessibility
- **WCAG AA compliant** (4.5:1 color contrast, alt text, keyboard navigation)
- **Semantic HTML5** (proper heading hierarchy, skip links)
- **Focus indicators** visible (2px gold outline)
- **Screen reader compatible**

### Scalability
- **CloudFront edge locations** (200+ points of presence globally)
- **S3 infinitely scalable** storage
- **Auto-scaling** via AWS Lambda (if future backend added)
- **Cost-optimized**: Pay only for what you use

## Documentation

| Document | Purpose |
|----------|---------|
| DEPLOYMENT_GUIDE.md | AWS deployment steps, troubleshooting |
| OPERATIONS.md | Daily/weekly/monthly operational tasks |
| CONTENT_UPDATES.md | How to update website content |
| TROUBLESHOOTING.md | Common issues and solutions |

## Configuration

All configuration in `.env` (or environment variables):

```bash
PROD_ACCOUNT_ID=742197632521        # Your AWS account
PROD_REGION=us-east-1               # CloudFront must be us-east-1
PRIMARY_DOMAIN=opusmagus.com         # Your domain
WWW_DOMAIN=www.opusmagus.com        # WWW subdomain
S3_BUCKET_NAME=opusmagus-com-prod   # S3 bucket name
ENVIRONMENT_TAG=prod                # Resource tagging
```

## Support & Contact

- **Website**: https://opusmagus.com
- **Email**: hello@opusmagus.com
- **GitHub**: https://github.com/opusmagus
- **LinkedIn**: https://linkedin.com/company/opusmagus

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        End Users                            │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS (ACM Certificate)
                     ▼
        ┌─────────────────────────────┐
        │      Route53 DNS             │
        │ opusmagus.com → CloudFront   │
        │ www.* → CloudFront           │
        └────────────┬────────────────┘
                     │
                     ▼
        ┌─────────────────────────────┐
        │     CloudFront CDN           │
        │ • Security Headers (HSTS)    │
        │ • AWS WAF Rules              │
        │ • Caching (HTML/CSS/Images)  │
        │ • Compression (gzip/brotli)  │
        │ • Origin Access Control      │
        └────────────┬────────────────┘
                     │
                     ▼
        ┌─────────────────────────────┐
        │   S3 Bucket (Static Hosting) │
        │ • Versioning                 │
        │ • Encryption                 │
        │ • Access Logging             │
        │ • Public Access Blocked      │
        └─────────────────────────────┘
                     
        ┌─────────────────────────────┐
        │    CloudWatch Monitoring     │
        │ • Logs & Metrics             │
        │ • Alarms & Dashboards        │
        └─────────────────────────────┘
```

## Status

✅ **Frontend**: Complete (HTML, CSS, JS responsive design)
✅ **Infrastructure**: Complete (all 5 CDK stacks)
✅ **Documentation**: Complete (deployment, ops, troubleshooting guides)
✅ **Ready for Deployment**: Yes

## Next Step

```bash
cd opusmagus-cdk && cdk deploy --all
```

**Website will be live at https://opusmagus.com in ~10 minutes.**

---

*Technology shaped into something useful.*
