# Design Document: OpusMagus Professional Marketing Website

## Design Overview

The OpusMagus marketing website is a static, high-performance web application deployed to AWS using Python CDK. The design emphasizes marketing effectiveness, conversion optimization, and accessibility while maintaining a cohesive dark-themed brand identity with purple and gold accents.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     End Users                               │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Route53 DNS                              │
│    (opusmagus.com A record, www CNAME)                      │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  CloudFront CDN                             │
│   • SSL/TLS Termination (ACM Certificate)                   │
│   • Edge Caching (HTML, CSS, JS, Images)                    │
│   • Compression (gzip, brotli)                              │
│   • Security Headers (HSTS, CSP, X-Frame-Options)           │
│   • AWS WAF (Web Application Firewall)                       │
│   • Logging to CloudWatch/S3                                │
└────────────────────────────┬────────────────────────────────┘
                             │ Origin Access Control
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              S3 Bucket (opusmagus-com-prod)                 │
│   • Static website hosting                                  │
│   • Versioning enabled                                      │
│   • Encryption (SSE-S3)                                     │
│   • Public access blocked (OAC only)                        │
│   • Access logging                                          │
└─────────────────────────────────────────────────────────────┘
```

### CDK Stack Structure

The infrastructure is organized into three logical CDK stacks:

1. **StorageStack**
   - S3 bucket for website assets
   - Versioning and encryption configuration
   - Access logging configuration

2. **DistributionStack**
   - CloudFront distribution
   - Origin Access Control for S3
   - Cache behaviors and TTLs
   - Security headers
   - Error page handling

3. **DNSStack** (Optional - if Route53 managed)
   - Route53 hosted zone records
   - A record for opusmagus.com
   - CNAME/A record for www.opusmagus.com

4. **SecurityStack**
   - AWS Certificate Manager SSL/TLS certificate
   - WAF rules and associations
   - Security group configurations

## Frontend Components

### Page Structure

```
index.html (Homepage)
├── Hero Section
│   ├── OpusMagus Logo
│   ├── Wizard Mascot (SVG/Image with glow effect)
│   ├── Headline (max 10 words)
│   ├── Subheading (under 20 words)
│   └── Primary CTA Button
├── Service Cards Section
│   ├── Section Title
│   └── 3+ Service Card Components
│       ├── Service Icon
│       ├── Title
│       ├── Description (under 50 words)
│       └── Learn More Link
├── Featured Work Showcase
│   ├── Section Title
│   ├── Featured Project Cards (min 3)
│   │   ├── Project Thumbnail (WebP + JPEG fallback)
│   │   ├── Project Title
│   │   ├── Project Description
│   │   └── Outcome/CTA Link
│   └── View All Portfolio Link
└── Footer
    ├── Contact Information
    ├── Social Media Links (LinkedIn, GitHub, Twitter)
    ├── Secondary Navigation
    ├── Copyright Notice
    └── Privacy Policy / Terms of Service Links
```

### Styling Strategy

**Color Palette:**
- Primary Background: #0a0a0a (near-black)
- Secondary Background: #1a1a2e (dark navy)
- Accent 1: #7c3aed (purple)
- Accent 2: #d4af37 (gold)
- Text Primary: #ffffff (white)
- Text Secondary: #b0b0b0 (light gray)

**Typography:**
- Headlines (H1, H2): Inter Bold, 2.5rem–4rem
- Subheadings (H3, H4): Inter SemiBold, 1.5rem–2rem
- Body Text: Inter Regular, 1rem
- Caption/Meta: Inter Light, 0.875rem

**Layout Strategy:**
- 12-column responsive grid (CSS Grid / Bootstrap-like)
- Max-width container: 1280px
- Mobile-first responsive breakpoints:
  - Mobile: 375px–767px (1 column)
  - Tablet: 768px–1024px (2 columns for cards)
  - Desktop: 1025px+ (3+ columns for cards)

### Interactive Elements & Effects

**Glowing Effects:**
- CSS `box-shadow` with purple/gold glow on wizard mascot
- CSS `filter: drop-shadow()` for animated glow
- `@keyframes` animation for subtle pulsing effect
- No JavaScript animation required

**Hover States:**
- Service cards: subtle scale (1.02) + shadow elevation
- Links: color transition to gold (#d4af37)
- CTA buttons: brightness increase + shadow

**Focus States (Accessibility):**
- Visible focus ring: 2px solid gold
- All interactive elements keyboard-navigable
- Focus trap avoided; standard tab order

## Performance Specifications

### Core Web Vitals Targets

- **LCP (Largest Contentful Paint):** < 2.5s
  - Achieved via CloudFront edge caching
  - Hero image as LCP element (critical path)
  
- **FID (First Input Delay):** < 100ms
  - Minimal JavaScript (static site)
  - No render-blocking resources

- **CLS (Cumulative Layout Shift):** < 0.1
  - Fixed dimensions for images
  - No dynamic content shifts
  - Proper font-display strategy (font-display: swap)

### Asset Optimization

- **HTML:** Minified, cache TTL: 0 (serve fresh)
- **CSS/JavaScript:** Minified, cache TTL: 31536000 (1 year) with content hash in filename
- **Images:**
  - Format: WebP (with JPEG fallback for older browsers)
  - Sizes: 320px, 768px, 1024px, 1920px variants
  - Lazy-loading for below-the-fold images
  - Maximum uncompressed: 100KB per image
- **Fonts:** System fonts or web-safe fonts (avoid heavy custom fonts)
- **Total Page Load:** < 3MB including all assets

### CloudFront Cache Configuration

| Content Type | TTL | Purpose |
|---|---|---|
| HTML | 0 seconds | Fresh content on every request |
| CSS/JS | 31536000 (1 year) | Immutable via content hash |
| Images | 86400 (1 day) | Balanced freshness/efficiency |
| SVGs | 86400 | Reusable graphics |

## Security Architecture

### Transport Security
- **TLS 1.2+** minimum (enforced via CloudFront)
- **HSTS:** max-age=31536000; includeSubDomains; preload
- **Automatic HTTP → HTTPS redirect** via CloudFront behavior

### Access Control
- **S3 Public Access Block:** All settings enabled (deny all)
- **Origin Access Control (OAC):** CloudFront-only access to S3
- **No public S3 URLs** exposed in responses

### Content Security
- **Content-Security-Policy:** 
  - default-src 'self'
  - script-src 'self' (no inline scripts)
  - style-src 'self' (no inline styles, only linked CSS)
  - img-src 'self' data: (allow data URIs for small images)
- **X-Content-Type-Options:** nosniff
- **X-Frame-Options:** DENY (prevent clickjacking)
- **Referrer-Policy:** strict-origin-when-cross-origin

### Data Encryption
- **S3 Encryption:** SSE-S3 (server-side encryption)
- **Access Logs:** Encrypted storage
- **No sensitive data** in static files (no API keys, credentials)

### Application Security
- **No third-party scripts** (analytics, ads, trackers) without explicit review
- **No forms or backend processing** (MVP scope)
- **Input validation:** N/A (static content only)
- **Rate limiting:** Handled by AWS WAF

### AWS WAF Configuration
- **Rate-based rules:** 2000 requests/5 minutes from single IP
- **SQL Injection rules:** AWS managed rule group
- **XSS rules:** AWS managed rule group
- **Bot Control:** Optional (if traffic monitoring required)

## Accessibility Design

### Semantic HTML
- Proper heading hierarchy: H1 (one per page) → H2 → H3
- `<nav>`, `<main>`, `<footer>` semantic elements
- `<section>` for logical content groupings
- Form labels associated with inputs (future feature)

### Color Contrast
- Text on background: 4.5:1 minimum (WCAG AA)
- Graphical elements: 3:1 minimum
- Tested via WCAG Color Contrast Checker

### Keyboard Navigation
- Tab order follows visual flow (left-to-right, top-to-bottom)
- Focus indicators: 2px solid gold (#d4af37)
- Skip-to-main-content link at page top
- No keyboard traps

### Screen Reader Support
- Alt text for all images (descriptive, under 125 characters)
- ARIA labels for icon-only buttons
- `role="region"` for major sections (optional)
- Proper list markup (`<ul>`, `<ol>`, `<li>`)

### Mobile/Touch Accessibility
- Minimum touch target size: 44x44 pixels
- No hover-only content (hover is desktop-only)
- Responsive text size: minimum 16px on mobile
- Readable without pinch-zoom (viewport meta tag)

## Deployment & Operations

### CDK Deployment Process

1. **Local Development Environment**
   - Python 3.10+ virtual environment
   - AWS CDK CLI installed globally
   - AWS credentials configured (AWS CLI profile or environment variables)

2. **Synthesis & Validation**
   - `cdk synth` → generates CloudFormation template
   - `cdk diff` → shows resource changes before deployment
   - Manual review of security and resource changes

3. **Deployment to PROD**
   - `cdk deploy` → applies changes to AWS account 742xxxxx
   - CloudFormation creates/updates resources
   - Requires interactive approval before proceeding

4. **Post-Deployment Verification**
   - S3 bucket created and accessible
   - CloudFront distribution deployed and healthy
   - CloudFront domain name noted (e.g., d111.cloudfront.net)
   - SSL certificate issued and validated
   - DNS records updated (manual step outside CDK)

### Asset Deployment Process

1. **Build/Preparation**
   - Minify HTML, CSS, JavaScript
   - Optimize and convert images to WebP + JPEG
   - Generate content hashes for CSS/JS files

2. **Upload to S3**
   - Sync static files to S3 bucket
   - Set Cache-Control headers per asset type
   - Set Content-Type MIME types correctly

3. **Cache Invalidation**
   - Invalidate `/index.html` path in CloudFront (instant update)
   - Optionally invalidate all (`/*`) if major changes
   - Monitor invalidation status

4. **Verification**
   - Test website via CloudFront domain
   - Verify custom domain resolves (opusmagus.com)
   - Check performance via WebPageTest or Lighthouse

## Risk Mitigation

### High-Risk Areas

1. **DNS Configuration**
   - Risk: Incorrect DNS records break website availability
   - Mitigation: DNS records validated before update; rollback plan (previous DNS values documented)

2. **SSL Certificate Issues**
   - Risk: Certificate renewal fails, HTTPS breaks
   - Mitigation: ACM automatic renewal; SNS notifications configured for expiration warnings

3. **S3 Access Control Misconfiguration**
   - Risk: Bucket becomes publicly accessible, data exposure
   - Mitigation: Public access block enabled; OAC enforced; regular audits via AWS Config

4. **Cache TTL Misconfiguration**
   - Risk: Stale content served; or excessive origin requests
   - Mitigation: HTML cached with TTL=0; CloudFront invalidation for urgent updates

5. **Performance Degradation**
   - Risk: Large assets cause slow load times
   - Mitigation: Strict asset limits (3MB total); lazy-loading for images; compression enabled

### Rollback Strategy

- **S3 Asset Rollback:** Previous versions accessible via S3 versioning; revert to prior version if needed
- **Infrastructure Rollback:** CDK state file backed up; CloudFormation can roll back stack changes
- **DNS Rollback:** Old DNS values documented; quickly revert if issues arise

## Monitoring & Observability

### CloudWatch Metrics

- CloudFront requests per second
- Cache hit ratio (%)
- 4xx errors (404, 403, 400)
- 5xx errors (500, 502, 503)
- Origin latency (milliseconds)
- Bandwidth consumption (GB)

### CloudWatch Logs

- CloudFront access logs (queryable via Athena)
- S3 access logs (who accessed what, when)
- Application errors (if any)

### Alarms

- **High 4xx Rate:** Trigger if > 5% of requests → investigate 404s
- **High 5xx Rate:** Trigger if > 1% of requests → check origin health
- **Cache Hit Ratio Low:** Trigger if < 80% → review cache settings
- **High Latency:** Trigger if P95 > 500ms → investigate origin or CloudFront

### Dashboard

- CloudFront distribution health
- S3 bucket metrics
- Top requested paths
- Geographic distribution of traffic
- Cache performance

## Documentation Structure

```
README.md
├── Project Overview
├── Technology Stack
├── Prerequisites
├── Local Setup
│   ├── Clone Repository
│   ├── Create Virtual Environment
│   ├── Install Dependencies
│   └── Configure AWS Credentials
├── Deployment
│   ├── CDK Synthesis
│   ├── CDK Deployment
│   └── Asset Upload
├── Configuration
│   ├── Domain Names
│   ├── AWS Account ID
│   └── Region
└── Support & Troubleshooting

DEPLOYMENT_RUNBOOK.md
├── Initial Deployment Steps
├── Asset Deployment Process
├── Cache Invalidation
├── Emergency Rollback
└── Common Issues & Solutions

CONTENT_UPDATES.md
├── Directory Structure
├── HTML File Editing
├── Image Optimization
└── Deployment After Changes
```

---

## Design Verification Checklist

- [ ] All 20 requirements addressed in design
- [ ] Performance targets (CWV, 3MB limit) achievable with design
- [ ] Security hardening measures specified (HTTPS, WAF, CSP)
- [ ] Accessibility standards (WCAG AA) incorporated
- [ ] Scalability via CloudFront edge locations confirmed
- [ ] Cost-effective: static hosting minimizes compute costs
- [ ] Monitoring and logging strategy documented
- [ ] Rollback and disaster recovery paths defined

