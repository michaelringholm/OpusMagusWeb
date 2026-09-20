# Task Plan: OpusMagus Professional Marketing Website

## Overview

This task plan breaks down the OpusMagus marketing website project into actionable, sequenced work items organized by phase. Each task includes success criteria, deliverables, and dependencies.

---

## Phase 1: Foundation & Infrastructure Setup

### 1.1 Initialize Python CDK Project Structure

**Description:** Set up the base CDK project with correct directory layout, dependencies, and configuration files.

**Tasks:**
- Create project directory: `opusmagus-cdk/`
- Initialize CDK app structure with `cdk init app --language python`
- Create `/stacks` directory for stack definitions
- Create `/config` directory for environment configurations
- Add `requirements.txt` with AWS CDK dependencies:
  - aws-cdk-lib (v2.x)
  - constructs
  - python-dotenv (for environment variables)

**Deliverables:**
- `opusmagus-cdk/` directory with CDK app scaffolding
- `opusmagus-cdk/stacks/` directory structure
- `requirements.txt` with all dependencies pinned

**Success Criteria:**
- `cdk list` outputs available stacks without errors
- All dependencies installable via `pip install -r requirements.txt`

---

### 1.2 Set Up Local Python Virtual Environment

**Description:** Document and automate the virtual environment setup process for developers.

**Tasks:**
- Create `setup.sh` (or `.bat` for Windows) script that:
  - Creates Python 3.10+ virtual environment
  - Activates virtual environment
  - Installs dependencies from `requirements.txt`
- Update `.gitignore` to exclude `.venv/`, `*.pyc`, `__pycache__/`
- Create `SETUP.md` with manual setup steps for reference

**Deliverables:**
- `setup.sh` / `setup.bat` automation scripts
- Updated `.gitignore`
- `SETUP.md` documentation

**Success Criteria:**
- New developer can run setup script once and have working environment
- Virtual environment properly isolated from system Python
- `pip list` shows all CDK dependencies installed

---

### 1.3 Create CDK Configuration Management

**Description:** Set up configuration system to manage environment-specific values (AWS account ID, regions, domain names).

**Tasks:**
- Create `config/config.py` with configuration class:
  - PROD_ACCOUNT_ID = "742xxxxx"
  - PROD_REGION = "us-east-1" (required for CloudFront + ACM)
  - PRIMARY_DOMAIN = "opusmagus.com"
  - WWW_DOMAIN = "www.opusmagus.com"
  - S3_BUCKET_NAME = "opusmagus-com-prod"
  - ENVIRONMENT_TAG = "prod"
- Create `.env.example` showing required environment variables
- Create `config/config.py` loader to read from `.env` file or environment variables

**Deliverables:**
- `config/config.py` configuration module
- `.env.example` template file

**Success Criteria:**
- Configuration values are easily accessible and not hardcoded in stack files
- Developers can override values via `.env` file
- Missing configuration values produce clear error messages

---

### 1.4 Create AWS Credentials & Account Setup Documentation

**Description:** Document AWS account setup and credential configuration for developers.

**Tasks:**
- Create `AWS_SETUP.md` documentation including:
  - AWS account creation requirements
  - IAM user/role setup for CDK deployment (required permissions)
  - AWS CLI installation and configuration
  - Profile setup for PROD_ACCOUNT (742xxxxx)
  - MFA setup requirements (if applicable)
- Create `iam-policy.json` with minimal required permissions for CDK deployment

**Deliverables:**
- `AWS_SETUP.md` documentation
- `iam-policy.json` with CDK deployment permissions

**Success Criteria:**
- Developers can configure AWS credentials without external guidance
- IAM policy follows least-privilege principle
- `aws sts get-caller-identity` returns correct account ID

---

## Phase 2: Infrastructure Stacks (CDK)

### 2.1 Create StorageStack (S3 Bucket)

**Description:** Define CDK stack for S3 bucket configuration.

**Tasks:**
- Create `/stacks/storage_stack.py` with StorageStack class
- Configure S3 bucket properties:
  - Bucket name: `opusmagus-com-prod`
  - Block public access: ALL settings enabled
  - Versioning: enabled
  - Encryption: SSE-S3
  - Access logging: to dedicated logging bucket or CloudWatch
  - Lifecycle rules: no automatic deletion (manual content management)
- Add bucket policy that denies direct public access
- Create Origin Access Control (OAC) construct for CloudFront
- Add CloudWatch alarms for bucket metrics

**Deliverables:**
- `/stacks/storage_stack.py` with S3 bucket and OAC
- CloudWatch logging configuration

**Success Criteria:**
- Stack synthesizes without errors: `cdk synth`
- `cdk diff` shows expected S3 resources (bucket, versioning, encryption)
- Public access block settings correctly configured

---

### 2.2 Create DistributionStack (CloudFront)

**Description:** Define CDK stack for CloudFront distribution and caching behavior.

**Tasks:**
- Create `/stacks/distribution_stack.py` with DistributionStack class
- Configure CloudFront distribution:
  - Origin: S3 bucket with OAC (not public access)
  - Default root object: `index.html`
  - Behaviors:
    - HTML files: TTL 0 (no cache), compress
    - CSS/JS: TTL 31536000 (1 year), compress
    - Images: TTL 86400 (1 day), compress
  - HTTP to HTTPS redirect
  - Error responses: 404 → `/404.html` (or index.html)
  - Logging to CloudWatch or S3
- Add security headers via Lambda@Edge or CloudFront headers:
  - Strict-Transport-Security
  - Content-Security-Policy
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
- Add cache invalidation capability (path parameter for `cdk deploy`)

**Deliverables:**
- `/stacks/distribution_stack.py` with CloudFront distribution
- Lambda@Edge function (if headers via Lambda)
- CloudWatch logging configuration

**Success Criteria:**
- Stack synthesizes without errors
- CloudFront domain generated and accessible
- Cache behaviors correctly configured per asset type
- Security headers present in HTTP responses

---

### 2.3 Create SecurityStack (SSL/TLS Certificate & WAF)

**Description:** Define CDK stack for ACM certificate and AWS WAF rules.

**Tasks:**
- Create `/stacks/security_stack.py` with SecurityStack class
- Configure AWS Certificate Manager (ACM):
  - Certificate for: opusmagus.com, www.opusmagus.com
  - Validation method: DNS (Route53 or manual)
  - Auto-renewal: enabled
  - Add SNS notifications for renewal/expiration
- Configure AWS WAF Web ACL:
  - Rate-based rule: 2000 requests/5 min per IP
  - AWS Managed Rules:
    - AWSManagedRulesCommonRuleSet
    - AWSManagedRulesAmazonIpReputationList
  - CloudFront association
- Add CloudWatch alarms for WAF blocked requests

**Deliverables:**
- `/stacks/security_stack.py` with ACM certificate and WAF
- SNS topic for certificate notifications
- CloudWatch alarms

**Success Criteria:**
- Certificate requested successfully
- Certificate domain validation visible in ACM console
- WAF Web ACL created and associated with CloudFront
- WAF rules block malicious requests (tested)

---

### 2.4 Create DNSStack (Route53 - Optional/Conditional)

**Description:** Define CDK stack for Route53 DNS records (if Route53 is used for DNS management).

**Tasks:**
- Create `/stacks/dns_stack.py` with DNSStack class (optional, conditionally deployed)
- Configure Route53 hosted zone (if not already created):
  - Hosted zone: opusmagus.com
- Configure DNS records:
  - A record: opusmagus.com → CloudFront distribution
  - CNAME record: www.opusmagus.com → CloudFront distribution (or A record)
  - TTL: 300 seconds
- Add CloudWatch alarms for DNS query health (optional)

**Deliverables:**
- `/stacks/dns_stack.py` with Route53 records (optional)
- CloudWatch alarms for DNS health

**Success Criteria:**
- Route53 records created and visible in AWS console
- DNS resolution working: `nslookup opusmagus.com` returns CloudFront IP
- TTL correctly set to 300 seconds

---

### 2.5 Create Main CDK App Entry Point

**Description:** Create the main CDK app file that orchestrates all stacks.

**Tasks:**
- Create `app.py` (or `opusmagus_app.py`) as CDK app entry point
- Import all stack classes (StorageStack, DistributionStack, SecurityStack, DNSStack)
- Instantiate stacks with proper dependencies:
  - SecurityStack (ACM cert) → DistributionStack (uses cert)
  - StorageStack → DistributionStack (S3 as origin)
  - DNSStack (optional) → DistributionStack (uses CloudFront domain)
- Add environment context for PROD_ACCOUNT and region
- Add stack naming convention: `{StackName}-opusmagus-prod`
- Add tags to all stacks: `Environment: prod`, `Project: opusmagus`

**Deliverables:**
- `app.py` with full stack orchestration
- Proper dependency and output handling between stacks

**Success Criteria:**
- `cdk synth` generates CloudFormation template without errors
- `cdk ls` shows all stacks in correct order
- Stack names follow naming convention

---

### 2.6 Add Pre-Deployment Validation

**Description:** Create validation script to check configuration before deployment.

**Tasks:**
- Create `scripts/validate-deployment.py` script that:
  - Checks AWS credentials and account ID (must match PROD_ACCOUNT)
  - Validates domain configuration
  - Checks ACM certificate status
  - Validates S3 bucket name uniqueness (optional, if bucket doesn't exist)
  - Outputs deployment summary for review
- Add deployment confirmation prompt (interactive or via environment variable)
- Script runs automatically before `cdk deploy` (via git hook or manual reminder)

**Deliverables:**
- `scripts/validate-deployment.py` validation script
- Integration instructions in README

**Success Criteria:**
- Script identifies misconfiguration before deployment (wrong account, etc.)
- Script produces clear pass/fail output
- Non-interactive option available for CI/CD pipelines

---

## Phase 3: Frontend Assets

### 3.1 Create HTML File Structure

**Description:** Create static HTML files for all pages and components.

**Tasks:**
- Create `/website/index.html` (homepage) with:
  - DOCTYPE, HTML5 semantic structure
  - Meta tags (viewport, charset, description, og:)
  - Link to main.css stylesheet
  - Hero section with placeholder content
  - Service cards section with 3+ cards (semantic structure)
  - Featured work showcase section (min 3 projects)
  - Footer with contact info, social links, legal links
- Create `/website/pages/services/index.html` (services detail page - optional)
- Create `/website/pages/portfolio/index.html` (portfolio gallery - optional)
- Create `/website/404.html` (custom 404 error page)
- Ensure all pages have proper heading hierarchy (H1 → H2 → H3)
- Add skip-to-main-content link at top of each page

**Deliverables:**
- `/website/index.html` homepage
- `/website/404.html` error page
- Optional detail pages
- All files with valid HTML5 markup and semantic elements

**Success Criteria:**
- W3C HTML validation passes (no critical errors)
- Heading hierarchy correct (single H1 per page)
- Meta tags present
- All pages keyboard navigable

---

### 3.2 Create Main Stylesheet (CSS)

**Description:** Create CSS file with responsive design and styling.

**Tasks:**
- Create `/website/css/main.css` with:
  - CSS custom properties (variables) for colors, fonts, breakpoints
  - Reset/normalize styles (margins, padding, box-sizing)
  - Typography styles (H1-H6, p, span, etc.)
  - Layout system:
    - 12-column responsive grid
    - Container max-width: 1280px
    - Flexbox utilities for alignment
  - Component styles:
    - Hero section (background image, text overlay, button)
    - Service cards (grid, hover effects, shadows)
    - Featured work cards (image containers, text overlay)
    - Footer (multi-column layout, link styles)
  - Responsive breakpoints (mobile: 375px, tablet: 768px, desktop: 1025px)
  - Hover and focus states for accessibility
  - Glowing effects (box-shadow, filter: drop-shadow())
  - Animations (@keyframes for pulsing glow)
- Minify CSS for production

**Deliverables:**
- `/website/css/main.css` stylesheet (minified)
- CSS organized with clear sections and comments

**Success Criteria:**
- All components styled per design specification
- Responsive design works on 375px, 768px, 1024px, 1920px viewports
- Color contrast meets WCAG AA (4.5:1 for text)
- CSS file size optimized (target < 50KB)

---

### 3.3 Create JavaScript for Interactivity (Minimal)

**Description:** Create minimal JavaScript for progressive enhancement (optional).

**Tasks:**
- Create `/website/js/main.js` with:
  - Smooth scrolling (if link anchors used)
  - Mobile menu toggle (if hamburger menu added)
  - Lazy-loading image observer (for below-the-fold images)
  - Optional: Form submission handling (contact form - if added)
- Ensure JavaScript is non-blocking (defer attribute in script tag)
- Minify JavaScript for production
- Keep JavaScript minimal; CSS handles most interactions

**Deliverables:**
- `/website/js/main.js` JavaScript file (minified)
- Optional feature flags for advanced functionality

**Success Criteria:**
- Page fully functional without JavaScript (progressive enhancement)
- Lazy-loading correctly defers non-critical images
- No console errors when JS disabled

---

### 3.4 Optimize and Create Image Assets

**Description:** Create and optimize images for the website.

**Tasks:**
- Create `/website/images/` directory structure:
  - `/hero/` (hero background, mascot illustration)
  - `/icons/` (service icons, social icons)
  - `/portfolio/` (project thumbnails)
  - `/branding/` (logo, watermarks)
- For each image:
  - Create WebP format (primary) and JPEG fallback
  - Generate responsive sizes: 320px, 768px, 1024px, 1920px widths
  - Compress to optimize file size (target < 100KB per image)
  - Add SVG versions for icons (preferred for icons)
- Add srcset and sizes attributes to `<img>` tags in HTML
- Add lazy-loading via `loading="lazy"` attribute

**Deliverables:**
- `/website/images/` directory with all optimized images
- SVG icons for services and social media
- Image optimization scripts (optional, for automation)

**Success Criteria:**
- WebP images 20-30% smaller than JPEG equivalents
- Image total size < 100KB per image
- srcset properly configured for responsive sizes
- Lazy-loading functional (verified via DevTools Network tab)

---

### 3.5 Create Favicon and Meta Assets

**Description:** Create favicon and social media preview assets.

**Tasks:**
- Create favicon files:
  - `/website/favicon.ico` (32x32px)
  - `/website/apple-touch-icon.png` (180x180px)
  - `/website/site.webmanifest` (PWA manifest - optional)
- Create social preview image:
  - `/website/images/og-image.png` (1200x630px)
- Add meta tags to `<head>`:
  - `<link rel="icon" href="/favicon.ico">`
  - `<link rel="apple-touch-icon" href="/apple-touch-icon.png">`
  - `<meta property="og:image" content="/images/og-image.png">`

**Deliverables:**
- `/website/favicon.ico`
- `/website/apple-touch-icon.png`
- `/website/images/og-image.png`
- Meta tags in HTML head

**Success Criteria:**
- Favicon displays in browser tabs
- Apple devices show custom icon
- Social media preview renders correctly (tested in sharing debuggers)

---

## Phase 4: Deployment & Validation

### 4.1 Create Asset Deployment Script

**Description:** Create script to deploy website files to S3 and invalidate CloudFront cache.

**Tasks:**
- Create `scripts/deploy-assets.py` script that:
  - Validates S3 bucket exists and is accessible
  - Syncs `/website/` directory to S3 bucket
  - Sets Cache-Control headers:
    - HTML: `Cache-Control: max-age=0, must-revalidate`
    - CSS/JS: `Cache-Control: max-age=31536000, immutable`
    - Images: `Cache-Control: max-age=86400`
  - Sets correct Content-Type MIME types
  - Invalidates `/index.html` in CloudFront
  - Outputs deployment summary
- Script should support dry-run mode (`--dry-run` flag)

**Deliverables:**
- `scripts/deploy-assets.py` deployment script
- Usage documentation in README

**Success Criteria:**
- Script uploads files to S3 with correct headers
- CloudFront cache invalidation initiated
- Dry-run mode shows what would be deployed without making changes

---

### 4.2 Create CDK Deployment Instructions & Checklist

**Description:** Document step-by-step CDK deployment process.

**Tasks:**
- Create `DEPLOYMENT.md` with:
  - Prerequisites checklist (AWS account, credentials, domain, CDK installed)
  - Step-by-step deployment:
    1. `pip install -r requirements.txt`
    2. `cdk synth` (generate CloudFormation)
    3. `cdk diff` (review changes)
    4. `cdk deploy` (deploy infrastructure)
    5. Validation steps (check CloudFront, S3, ACM)
  - Deployment confirmation prompts (built into scripts)
  - Post-deployment configuration (Route53 DNS, if applicable)
  - Expected outputs and CloudFront domain name
  - Rollback procedures (CloudFormation stack deletion)
- Create pre-deployment checklist:
  - AWS credentials configured correctly
  - Account ID matches PROD_ACCOUNT
  - Domain name configured correctly
  - No other deployments in progress

**Deliverables:**
- `DEPLOYMENT.md` comprehensive deployment guide
- Checklist embedded in scripts

**Success Criteria:**
- New DevOps engineer can follow instructions without additional guidance
- All steps explicitly listed with expected outputs
- Rollback procedures clearly documented

---

### 4.3 Deploy Infrastructure (CDK)

**Description:** Deploy CDK stacks to AWS PROD account.

**Tasks:**
- Execute `cdk synth` to validate CloudFormation generation
- Execute `cdk diff` to review changes (confirm S3, CloudFront, ACM, WAF resources)
- Execute `cdk deploy` with approval
- Verify CloudFormation stack creation in AWS console
- Collect CloudFront domain name (e.g., d111.cloudfront.net)
- Verify S3 bucket created and public access blocked
- Verify ACM certificate status (pending validation or issued)
- Verify CloudFront distribution healthy and active
- Verify WAF Web ACL associated with CloudFront

**Deliverables:**
- CloudFormation stacks deployed to AWS PROD account (742xxxxx)
- CloudFront distribution active and domain noted
- S3 bucket ready for asset upload
- ACM certificate issued (or pending DNS validation)

**Success Criteria:**
- All stacks show CREATE_COMPLETE or UPDATE_COMPLETE in CloudFormation
- S3 bucket accessible only via CloudFront (no public access)
- CloudFront distribution returns healthy status
- ACM certificate issued and valid for both domains

---

### 4.4 Deploy Website Assets to S3

**Description:** Upload website files to S3 bucket.

**Tasks:**
- Run `scripts/deploy-assets.py` to upload `/website/` directory to S3
- Verify assets uploaded:
  - `index.html` present in bucket root
  - CSS, JavaScript, images present
  - Cache-Control headers correctly set
- Test S3 bucket via CloudFront domain:
  - Access https://d111.cloudfront.net/ (CloudFront domain)
  - Verify homepage loads without errors
  - Verify CSS styling applied (colors, layout)
  - Verify images display correctly

**Deliverables:**
- Website files uploaded to S3 bucket
- Cache-Control headers correctly configured
- Website accessible via CloudFront domain

**Success Criteria:**
- Homepage loads without 403/404 errors
- CSS and images render correctly
- Page load time < 3s
- Core Web Vitals in acceptable range (LCP < 2.5s)

---

### 4.5 Configure DNS Records

**Description:** Update DNS to point to CloudFront distribution.

**Tasks:**
- Identify current DNS provider (Route53, external provider, etc.)
- If Route53 managed (via DNSStack):
  - Route53 records auto-created by CDK
  - Verify A/CNAME records resolve to CloudFront domain
  - Test DNS resolution: `nslookup opusmagus.com`
- If external DNS provider:
  - Manually create/update DNS records:
    - A record for opusmagus.com → CloudFront IP (or use ALIAS if supported)
    - CNAME for www.opusmagus.com → CloudFront domain
  - Verify TTL set to 300 seconds
  - Wait for DNS propagation (up to 24-48 hours, typically minutes)
- Test domain resolution:
  - `nslookup opusmagus.com` returns CloudFront IP
  - `curl -I https://opusmagus.com` returns 200 OK
  - Browser access to opusmagus.com works

**Deliverables:**
- DNS records updated and verified
- Domain resolution working
- Website accessible via opusmagus.com

**Success Criteria:**
- Domain resolves to CloudFront distribution
- HTTPS connection secure (no certificate warnings)
- Website loads correctly via opusmagus.com
- www.opusmagus.com redirects or serves same content

---

### 4.6 Validate SSL/TLS Certificate

**Description:** Verify SSL/TLS certificate is issued and correctly configured.

**Tasks:**
- Check ACM console for certificate status:
  - Certificate for opusmagus.com and www.opusmagus.com
  - Status: "Issued" (not Pending or Failed)
  - Validation method: DNS or Email
  - Auto-renewal enabled
- Verify certificate in browser:
  - Navigate to https://opusmagus.com
  - Click lock icon → Certificate details
  - Verify domains listed (opusmagus.com, www.opusmagus.com)
  - Verify certificate issuer is AWS Certificate Manager
- Check CloudFront SSL settings:
  - Minimum TLS version: 1.2 or higher
  - Certificate associated with distribution
  - HTTPS redirect configured (HTTP → HTTPS)

**Deliverables:**
- ACM certificate verified as issued
- Certificate installed and active in CloudFront
- HTTPS working for all domains

**Success Criteria:**
- Certificate status "Issued" in ACM console
- No certificate warnings in browser
- All domains (opusmagus.com, www.opusmagus.com) covered
- HSTS header present (checked via curl or DevTools)

---

### 4.7 Performance Validation (Lighthouse & Core Web Vitals)

**Description:** Validate website performance against requirements.

**Tasks:**
- Run Lighthouse audit:
  - Google Lighthouse (DevTools or via CLI)
  - Target: Performance score > 90
  - Check LCP < 2.5s, FID < 100ms, CLS < 0.1
- Check page size and assets:
  - Total page load size < 3MB
  - Individual images < 100KB
  - HTML minified
  - CSS/JS minified and gzipped
- Test on multiple devices/networks:
  - Desktop (Chrome, Firefox, Safari)
  - Mobile (iOS Safari, Android Chrome)
  - Slow 3G network (DevTools throttling)
- Verify caching:
  - Repeat page load faster (cached resources)
  - Check Network tab for cache hits

**Deliverables:**
- Lighthouse report saved (screenshot or PDF)
- Performance metrics documented
- Issues (if any) logged for remediation

**Success Criteria:**
- LCP < 2.5s
- FID < 100ms
- CLS < 0.1
- Total page size < 3MB
- Lighthouse Performance score > 90

---

### 4.8 Accessibility Validation (WCAG AA)

**Description:** Validate website meets WCAG AA accessibility standards.

**Tasks:**
- Run automated accessibility tools:
  - axe DevTools (browser extension)
  - WAVE (WebAIM)
  - Lighthouse accessibility audit
- Manual testing:
  - Keyboard navigation: Tab through all interactive elements
  - Check focus indicators visible (2px gold ring)
  - Screen reader (NVDA or JAWS on Windows; VoiceOver on Mac)
  - Zoom to 200% and verify layout intact
  - Disable CSS and verify content readable
- Color contrast validation:
  - WebAIM Color Contrast Checker
  - Text on background: 4.5:1 minimum
  - Graphical elements: 3:1 minimum
- Alt text validation:
  - All images have descriptive alt text
  - Alt text describes image content (not "image" or "picture")

**Deliverables:**
- Automated accessibility audit report
- Manual testing notes
- Issues (if any) logged for remediation

**Success Criteria:**
- No critical or major accessibility issues
- All interactive elements keyboard accessible
- Focus indicators visible and clear
- Color contrast WCAG AA compliant
- Alt text present and descriptive
- Screen reader usable (content announced correctly)

---

### 4.9 Security Validation

**Description:** Validate security hardening and best practices.

**Tasks:**
- Verify AWS security configuration:
  - S3 bucket public access blocked (all settings enabled)
  - CloudFront uses OAC/OAI for S3 access
  - WAF Web ACL active on CloudFront
  - ACM certificate issued and valid
- Check HTTP security headers:
  - Curl test: `curl -I https://opusmagus.com`
  - Verify headers present:
    - Strict-Transport-Security (HSTS)
    - Content-Security-Policy (CSP)
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
- Test WAF effectiveness:
  - Simulate malicious requests (SQL injection, XSS payloads)
  - Verify WAF blocks requests (403 Forbidden)
  - Check CloudWatch logs for blocked requests
- SSL/TLS validation:
  - Use SSL Labs or similar tool to check certificate and ciphers
  - Minimum TLS 1.2
  - No weak ciphers
- Check for common vulnerabilities:
  - No exposed secrets or API keys in HTML/JS
  - No third-party scripts without CSP approval
  - No unsafe-inline styles or scripts

**Deliverables:**
- Security audit report
- SSL Labs test result
- WAF testing confirmation
- Issues (if any) logged for remediation

**Success Criteria:**
- S3 bucket not publicly accessible
- Security headers present and correct
- WAF actively blocking malicious requests
- SSL/TLS configuration strong (A+ rating on SSL Labs)
- No critical security issues

---

### 4.10 Monitoring & Alerting Setup Verification

**Description:** Verify monitoring and alerting are configured and functional.

**Tasks:**
- Verify CloudWatch logs enabled:
  - CloudFront access logs stored (S3 or CloudWatch)
  - S3 bucket access logs stored
  - Logs queryable and accessible
- Verify CloudWatch alarms configured:
  - High 4xx error rate alarm
  - High 5xx error rate alarm
  - Low cache hit ratio alarm (optional)
  - High latency alarm (optional)
- Test alarm functionality:
  - Trigger alarm by simulating traffic spike or error
  - Verify SNS notification received (if configured)
  - Check CloudWatch dashboard displays metrics
- Verify CloudFront metrics:
  - Requests per second visible
  - Cache hit ratio visible
  - Bandwidth consumption visible
  - Geographic distribution visible

**Deliverables:**
- CloudWatch logs verified and accessible
- Alarms configured and tested
- Dashboard created and displaying metrics
- SNS topics and notifications verified (if applicable)

**Success Criteria:**
- Monitoring data flowing to CloudWatch
- Alarms triggering correctly
- Dashboard accessible and useful
- Team can identify issues via logs and metrics

---

## Phase 5: Documentation & Handoff

### 5.1 Create Comprehensive README

**Description:** Document project overview, setup, and deployment.

**Tasks:**
- Create `README.md` with sections:
  - Project Overview (OpusMagus marketing website)
  - Technology Stack (CDK, CloudFront, S3, etc.)
  - Architecture Diagram (text or image)
  - Prerequisites (AWS account, Python 3.10+, AWS CLI)
  - Local Setup Instructions (clone, .venv, requirements.txt)
  - Deployment Instructions (summarized, link to DEPLOYMENT.md)
  - Project Structure (directory layout explanation)
  - File Structure (`/website/`, `/stacks/`, `/config/`, etc.)
  - Configuration (environment variables, domain names)
  - Common Tasks (updating content, invalidating cache, rollback)
  - Troubleshooting (common issues and solutions)
  - Support and Contact

**Deliverables:**
- `README.md` comprehensive documentation

**Success Criteria:**
- New team member can clone repo and understand project without external help
- All setup and deployment steps explicit
- Common questions answered

---

### 5.2 Create Content Update Runbook

**Description:** Document process for non-developers to update website content.

**Tasks:**
- Create `CONTENT_UPDATES.md` with:
  - File structure overview (`/website/` directory)
  - How to edit HTML content:
    - Open index.html in text editor
    - Locate section (Hero, Services, Portfolio, Footer)
    - Edit text, links, or images
    - Save file
  - How to add/update images:
    - Prepare image (optimize, convert to WebP)
    - Place image in `/website/images/` directory
    - Reference in HTML via `<img>` tag or CSS
  - How to update service cards:
    - Locate service card HTML
    - Edit title, description, icon
    - Save and deploy
  - How to add portfolio items:
    - Add project images to `/website/images/portfolio/`
    - Add HTML structure for new project card
    - Test locally (optional)
  - Deployment process:
    - Run `python scripts/deploy-assets.py`
    - Verify files uploaded to S3
    - Monitor CloudFront for content updates
  - Troubleshooting:
    - Old content still showing: CloudFront cache issue (manual invalidation needed)
    - Images not displaying: Check file path and MIME type
    - Formatting broken: HTML structure corrupted (restore from version control)

**Deliverables:**
- `CONTENT_UPDATES.md` content management guide

**Success Criteria:**
- Non-technical team member can update content with minimal training
- Clear step-by-step instructions
- Common issues and solutions documented

---

### 5.3 Create Troubleshooting Guide

**Description:** Document solutions for common issues.

**Tasks:**
- Create `TROUBLESHOOTING.md` with solutions for:
  - 403 Forbidden errors
    - Cause: S3 public access issue or OAC misconfigured
    - Solution: Verify S3 bucket public access blocked, OAC configured
  - 404 Not Found
    - Cause: File not in S3 bucket or incorrect path
    - Solution: Verify file deployed, check file path in HTML
  - Stale content serving
    - Cause: CloudFront cache not invalidated
    - Solution: Manual cache invalidation via AWS console or script
  - Slow page load
    - Cause: Large images, missing compression
    - Solution: Optimize images, verify gzip enabled in CloudFront
  - HTTPS certificate errors
    - Cause: Certificate not issued, domain mismatch
    - Solution: Check ACM console, verify DNS configured, wait for validation
  - DNS not resolving
    - Cause: DNS records not updated or TTL not expired
    - Solution: Verify Route53 records, check TTL, use `nslookup` to test
  - CSS not loading
    - Cause: Incorrect file path or cache issue
    - Solution: Check file exists in S3, invalidate cache
  - Images not displaying
    - Cause: Incorrect path, wrong MIME type, or performance issue
    - Solution: Verify file in S3, check `Content-Type` header, lazy-loading delay

**Deliverables:**
- `TROUBLESHOOTING.md` troubleshooting guide

**Success Criteria:**
- Common issues documented with solutions
- Team can resolve issues without external help

---

### 5.4 Create Operations Runbook

**Description:** Document operational procedures and disaster recovery.

**Tasks:**
- Create `OPERATIONS.md` with:
  - Daily/Weekly checks:
    - CloudFront metrics healthy (low error rate, good cache ratio)
    - No alarms triggered
    - Website responsive (spot check)
  - Monthly maintenance:
    - Review CloudWatch logs for anomalies
    - Update dependencies (if applicable)
    - Backup CDK state and S3 versioning
  - Emergency procedures:
    - Website down: Check CloudFront status, check S3 bucket, check DNS
    - Performance degradation: Check image sizes, CloudFront metrics, origin latency
    - Security incident: Check WAF logs, revoke compromised credentials, audit access
  - Rollback procedures:
    - Infrastructure rollback: CloudFormation stack delete and redeploy
    - Asset rollback: S3 versioning to restore previous content
    - DNS rollback: Revert Route53 records to previous values
  - Disaster recovery:
    - Complete infrastructure loss: Re-deploy from CDK code
    - Data loss: Recover from S3 versioning
    - Credential compromise: Rotate AWS keys, update CDK code

**Deliverables:**
- `OPERATIONS.md` operations and disaster recovery guide

**Success Criteria:**
- Team has clear procedures for common scenarios
- Disaster recovery procedures documented

---

### 5.5 Create Architecture & Configuration Documentation

**Description:** Document technical architecture for future reference and maintenance.

**Tasks:**
- Create `ARCHITECTURE.md` with:
  - System diagram (ASCII art or image)
  - Component descriptions (S3, CloudFront, Route53, ACM)
  - Data flow (user → CloudFront → S3)
  - Caching strategy (TTLs, invalidation)
  - Security measures (WAF, HTTPS, OAC)
  - Monitoring strategy (CloudWatch logs, alarms)
  - Scalability considerations
- Create `CONFIG_REFERENCE.md` with:
  - All configurable parameters (domain names, account ID, region, bucket name)
  - How to change each parameter
  - Impact of each change
  - Default values and recommendations

**Deliverables:**
- `ARCHITECTURE.md` technical architecture documentation
- `CONFIG_REFERENCE.md` configuration reference

**Success Criteria:**
- Future team member can understand system from documentation
- Configuration parameters clearly documented

---

### 5.6 Final Testing & Sign-Off

**Description:** Final comprehensive testing before handoff.

**Tasks:**
- Perform end-to-end testing:
  - Access website via all domains (opusmagus.com, www.opusmagus.com)
  - All pages load correctly
  - All links functional
  - Forms (if any) working
  - Images display correctly
  - CSS styling applied correctly
  - Responsive on mobile/tablet/desktop
  - Performance acceptable (LCP, FID, CLS within targets)
- Security validation:
  - SSL/TLS certificate valid
  - HTTPS enforced
  - Security headers present
  - WAF blocking malicious traffic
- Monitoring validation:
  - CloudWatch logs collecting data
  - Alarms configured and tested
  - Dashboard displaying metrics
- Documentation review:
  - README complete and accurate
  - Deployment steps verified by test deployment
  - Runbooks tested and validated
  - Troubleshooting guide comprehensive
- Team training:
  - Handoff meeting with operations team
  - Content update training for marketing team
  - Emergency procedures reviewed

**Deliverables:**
- Sign-off document confirming all systems operational
- Training completion records

**Success Criteria:**
- All functionality working correctly
- All documentation accurate and complete
- Team confident in managing website
- No critical issues remaining

---

## Summary of Deliverables

### Infrastructure (CDK)
- [x] Python CDK project structure and stacks
- [ ] S3 bucket with security configurations
- [ ] CloudFront distribution with caching and security headers
- [ ] AWS Certificate Manager SSL/TLS certificate
- [ ] AWS WAF Web ACL and rules
- [ ] Route53 DNS records (if managed by CDK)
- [ ] CloudWatch logging and alarms
- [ ] Pre-deployment validation scripts

### Frontend
- [ ] HTML pages (homepage, 404, optional detail pages)
- [ ] CSS stylesheet with responsive design
- [ ] JavaScript for interactivity (minimal, progressive enhancement)
- [ ] Optimized images (WebP + JPEG fallbacks, responsive sizes)
- [ ] Favicon and social media preview assets

### Deployment
- [ ] Asset deployment script
- [ ] Deployed infrastructure in AWS PROD account
- [ ] Website files in S3 bucket
- [ ] DNS records configured and resolving
- [ ] SSL/TLS certificate issued and active

### Documentation
- [ ] README.md with project overview and setup
- [ ] DEPLOYMENT.md with step-by-step deployment instructions
- [ ] CONTENT_UPDATES.md for content management
- [ ] TROUBLESHOOTING.md with common issues and solutions
- [ ] OPERATIONS.md with operational procedures
- [ ] ARCHITECTURE.md with technical architecture
- [ ] CONFIG_REFERENCE.md with configuration parameters

---

## Success Criteria Summary

The project is considered complete when:

1. **Infrastructure is deployed** to AWS PROD account (742xxxxx) without errors
2. **Website is accessible** via opusmagus.com and www.opusmagus.com over HTTPS
3. **Performance meets targets** (LCP < 2.5s, FID < 100ms, CLS < 0.1, page size < 3MB)
4. **Accessibility compliant** (WCAG AA standards met, keyboard navigable, screen reader compatible)
5. **Security hardened** (HTTPS enforced, WAF active, no public S3 access, security headers present)
6. **Monitoring operational** (CloudWatch logs, alarms, dashboard functional)
7. **Documentation complete** (README, deployment, operations, troubleshooting guides)
8. **Team trained** (operations team can manage infrastructure, marketing team can update content)
9. **No critical issues** remain (all functional, performance, security, and accessibility tests passing)

