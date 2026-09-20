# Requirements Document: OpusMagus Professional Marketing Website

## Introduction

OpusMagus is building a professional, conversion-focused marketing website that showcases the brand through a dark-themed interface with purple and gold color scheme, featuring a wizard mascot and glowing effects. The website will be deployed to AWS PROD using Python CDK infrastructure-as-code, served via S3 and CloudFront with SSL/TLS enabled for the primary domain (opusmagus.com) and www subdomain. The site consists of static HTML, CSS, and JavaScript with no backend services. The MVP scope includes a hero section, service cards, featured work showcase, and footer, optimized for marketing effectiveness and conversion.

## Glossary

- **OpusMagus_Website**: The static HTML/CSS/JavaScript marketing website for OpusMagus
- **Hero_Section**: The landing section at the top of the homepage featuring the primary value proposition, wizard mascot, and call-to-action
- **Service_Cards**: Modular UI components displaying OpusMagus services with descriptions and visual elements
- **Featured_Work_Showcase**: A gallery section highlighting completed projects or case studies
- **S3_Bucket**: Amazon Simple Storage Service bucket hosting the static website assets
- **CloudFront**: Amazon CloudFront content delivery network distribution serving the website to users globally
- **SSL_Certificate**: AWS Certificate Manager certificate enabling HTTPS encryption for opusmagus.com and www.opusmagus.com
- **Python_CDK**: AWS Cloud Development Kit infrastructure-as-code framework using Python
- **PROD_Account**: AWS production account with ID 742xxxxx
- **Virtual_Environment**: Python virtual environment (.venv) for isolated package management on developer machines
- **Domain_Alias**: CNAME record mapping www.opusmagus.com to the primary opusmagus.com domain
- **Marketing_Effectiveness**: The ability to engage users, communicate value, and drive desired actions (contact, signup, etc.)
- **Conversion**: A user action indicating commercial intent (form submission, demo request, etc.)

## Requirements

### Requirement 1: Hero Section Implementation

**User Story:** As a site visitor, I want to immediately understand OpusMagus's value proposition through a compelling hero section, so that I am engaged and motivated to explore the site.

#### Acceptance Criteria

1. WHEN the OpusMagus_Website loads, THE Hero_Section SHALL display at the top of the viewport without requiring scroll
2. THE Hero_Section SHALL contain the OpusMagus brand logo, wizard mascot illustration, and primary headline
3. THE Hero_Section SHALL include a descriptive subheading (under 20 words) communicating the core value proposition
4. THE Hero_Section SHALL feature a primary call-to-action button (e.g., "Get Started", "Learn More") with contrasting color and visible focus state for keyboard navigation
5. THE Hero_Section background SHALL use the dark theme with purple and gold accent colors as defined in the brand style guide
6. THE Hero_Section SHALL include glowing effects applied to the wizard mascot and accent elements using CSS animations

### Requirement 2: Service Cards Component

**User Story:** As a site visitor, I want to understand the services OpusMagus offers through organized, visually distinct cards, so that I can quickly evaluate if those services match my needs.

#### Acceptance Criteria

1. WHEN the OpusMagus_Website displays the Service_Cards section, THE cards SHALL be arranged in a responsive grid (3 columns on desktop, 1 column on mobile)
2. EACH Service_Card SHALL display a service icon, title, description (under 50 words), and a "Learn More" link
3. WHILE hovering over a Service_Card on desktop, THE card SHALL display subtle visual feedback (shadow, scale, or color change)
4. THE Service_Cards SHALL use the dark theme with gold accent highlights on hover or focus states
5. THE Service_Cards layout SHALL maintain alignment and consistent spacing across all viewport sizes
6. THE Service_Cards SHALL be keyboard accessible with visible focus indicators for tab navigation

### Requirement 3: Featured Work Showcase

**User Story:** As a prospect evaluating OpusMagus, I want to see examples of completed work or case studies, so that I can assess the quality and relevance of their services.

#### Acceptance Criteria

1. WHEN the OpusMagus_Website displays the Featured_Work_Showcase section, THE showcase SHALL contain at least 3 featured projects or case studies (MVP minimum)
2. EACH featured work item SHALL display a project image/thumbnail, project title, brief description, and outcome or result
3. WHERE additional work items are available, THE Featured_Work_Showcase SHALL include a link to a portfolio or full work gallery
4. THE Featured_Work_Showcase layout SHALL adapt to a single-column layout on mobile devices while maintaining readability
5. THE Featured_Work_Showcase images SHALL use optimized formats (WebP with JPEG fallback) and lazy-loading to improve page performance
6. EACH featured work item SHALL include a link or button to view project details if a detail page exists

### Requirement 4: Footer Section

**User Story:** As a site visitor, I want to easily find contact information, social links, and additional navigation from anywhere on the site, so that I can connect with OpusMagus or explore other pages.

#### Acceptance Criteria

1. THE Footer section SHALL appear at the bottom of every page and include contact information (email, phone, physical address where applicable)
2. THE Footer SHALL include links to OpusMagus social media profiles (LinkedIn, GitHub, Twitter, etc.)
3. THE Footer SHALL contain secondary navigation links (e.g., About, Services, Portfolio, Blog, Privacy Policy)
4. THE Footer SHALL display a copyright notice with the current year
5. WHERE required by law or policy, THE Footer SHALL include Privacy Policy and Terms of Service links
6. THE Footer SHALL use the dark theme with gold accents, maintaining visual consistency with the rest of the site

### Requirement 5: Responsive Design and Mobile Optimization

**User Story:** As a mobile user, I want the OpusMagus website to display correctly and function smoothly on my smartphone, so that I can access information and engage with the brand regardless of device.

#### Acceptance Criteria

1. THE OpusMagus_Website SHALL support desktop (1920px and above), tablet (768px to 1024px), and mobile (375px to 767px) viewports
2. WHEN the viewport width changes, THE layout SHALL reflow without horizontal scrolling on all supported devices
3. WHILE interacting with touch inputs on mobile or tablet, THE buttons, links, and interactive elements SHALL have a minimum touch target size of 44x44 pixels
4. THE OpusMagus_Website typography SHALL be readable without zooming, with base font size at least 16px on mobile devices
5. THE OpusMagus_Website images SHALL scale proportionally and display correctly across all viewport sizes
6. WHEN testing on mobile devices, THE site SHALL load and render within 3 seconds (Core Web Vitals target)

### Requirement 6: Visual Design and Branding

**User Story:** As an OpusMagus stakeholder, I want the website to consistently reflect the brand identity through cohesive design elements, so that visitors perceive a professional and unified brand.

#### Acceptance Criteria

1. THE OpusMagus_Website color palette SHALL use dark background colors (near-black or dark gray) as the primary base
2. THE OpusMagus_Website accent colors SHALL include purple and gold, applied to highlights, links, buttons, and hover states
3. THE wizard mascot illustration SHALL appear prominently in the hero section and may be incorporated into other sections with glowing effects
4. THE OpusMagus_Website glowing effects (applied to mascot, text, or elements) SHALL use CSS animations and shadow properties, avoiding JavaScript-based animations where possible
5. THE OpusMagus_Website typography SHALL use a modern, readable font family with clear hierarchy (headline, subheading, body, caption styles)
6. ALL visual elements SHALL maintain consistency with the brand style guide provided in project documentation

### Requirement 7: Accessibility Compliance

**User Story:** As a user with accessibility needs, I want the OpusMagus website to be usable with assistive technologies (screen readers, keyboard navigation), so that I can access all content and functionality.

#### Acceptance Criteria

1. THE OpusMagus_Website HTML markup SHALL follow semantic HTML5 standards (proper heading hierarchy, form labels, alt text for images)
2. ALL images SHALL include descriptive alt text that communicates the image's purpose and content
3. THE OpusMagus_Website SHALL be fully keyboard navigable with visible focus indicators on all interactive elements
4. THE OpusMagus_Website color contrast SHALL meet WCAG AA standard (at least 4.5:1 for text, 3:1 for graphics)
5. WHEN screen readers access the OpusMagus_Website, THE page structure SHALL be logical and all content SHALL be announced correctly
6. THE OpusMagus_Website forms (where present) SHALL include proper labels, error messages, and validation announcements

### Requirement 8: S3 Bucket Configuration

**User Story:** As a DevOps engineer deploying the OpusMagus website, I want the S3 bucket to be properly configured for static website hosting, so that assets are stored securely and served efficiently.

#### Acceptance Criteria

1. THE S3_Bucket in the PROD_Account SHALL be configured for static website hosting
2. THE S3_Bucket name SHALL be consistent with the domain naming convention (e.g., opusmagus-com-prod)
3. THE S3_Bucket SHALL have public read access restricted to CloudFront only using Origin Access Identity (OAI) or Origin Access Control (OAC)
4. THE S3_Bucket versioning SHALL be enabled to maintain rollback capability
5. THE S3_Bucket SHALL have logging enabled to CloudWatch or a dedicated logging bucket
6. THE S3_Bucket public access block settings SHALL deny all public ACLs and public bucket policies

### Requirement 9: CloudFront Distribution Configuration

**User Story:** As an OpusMagus stakeholder, I want the website served globally with low latency and high availability, so that users experience fast, reliable access.

#### Acceptance Criteria

1. THE CloudFront distribution SHALL use the S3_Bucket as its origin
2. THE CloudFront distribution origin SHALL be configured to use Origin Access Identity (OAI) or OAC for secure S3 access
3. THE CloudFront distribution cache behavior SHALL cache static assets (HTML, CSS, JS, images) with appropriate TTLs (HTML: 0 or short; assets: long-lived)
4. THE CloudFront distribution SHALL be configured to compress static assets using gzip and brotli compression
5. THE CloudFront distribution SHALL serve index.html for root path requests and directory paths (e.g., /services/ → /services/index.html)
6. THE CloudFront distribution error responses SHALL return the custom error page for 404 and 403 errors where applicable

### Requirement 10: SSL/TLS Certificate and HTTPS

**User Story:** As a security-conscious visitor, I want all communication with the OpusMagus website encrypted, so that my data is protected in transit.

#### Acceptance Criteria

1. WHEN a user visits opusmagus.com, THE OpusMagus_Website SHALL respond over HTTPS with a valid SSL_Certificate
2. WHEN a user visits www.opusmagus.com, THE OpusMagus_Website SHALL respond over HTTPS with the same SSL_Certificate
3. THE SSL_Certificate SHALL be issued by AWS Certificate Manager for opusmagus.com and www.opusmagus.com (wildcard or SAN)
4. THE SSL_Certificate SHALL be configured in the CloudFront distribution with minimum TLS version 1.2
5. WHEN a user accesses http:// (non-HTTPS) URLs, THE CloudFront distribution SHALL redirect to https://
6. THE SSL_Certificate renewal process SHALL be automatic through AWS Certificate Manager

### Requirement 11: Domain Configuration and DNS

**User Story:** As the OpusMagus infrastructure owner, I want DNS records properly configured so that users can access the site via the primary domain and www subdomain.

#### Acceptance Criteria

1. THE primary domain opusmagus.com SHALL have an A record pointing to the CloudFront distribution
2. THE www subdomain (www.opusmagus.com) SHALL have a CNAME record or A record pointing to the CloudFront distribution
3. WHEN users access www.opusmagus.com, THE request SHALL be served the same content as opusmagus.com without redirect (or redirect via CloudFront behavior)
4. THE DNS records SHALL be managed via Route53 (AWS DNS service) or external DNS provider as determined by OpusMagus infrastructure team
5. THE DNS records TTL SHALL be set to 300 seconds to allow rapid updates during troubleshooting or migration
6. WHERE a Domain_Alias is used, THE alias configuration SHALL resolve without additional HTTP redirects

### Requirement 12: Python CDK Infrastructure-as-Code

**User Story:** As a DevOps engineer, I want the infrastructure defined in Python CDK code, so that the deployment is reproducible, version-controlled, and follows infrastructure-as-code best practices.

#### Acceptance Criteria

1. THE infrastructure code SHALL be written in Python using AWS CDK v2 or compatible version
2. THE CDK code SHALL define stacks for S3_Bucket, CloudFront distribution, SSL_Certificate, and Route53 DNS records (if managed via Route53)
3. THE CDK code SHALL be organized into logical constructs (e.g., StorageStack, DistributionStack, DNSStack)
4. THE CDK code SHALL use configuration files or environment variables to specify domain names, certificate details, and account IDs
5. THE CDK code SHALL include comments and docstrings explaining the purpose of each construct and configuration
6. THE CDK code deployment process SHALL be idempotent (running it multiple times produces the same result)

### Requirement 13: Local Virtual Environment Setup

**User Story:** As a developer, I want to set up the CDK project locally using a Python virtual environment, so that dependencies are isolated and the project is reproducible across machines.

#### Acceptance Criteria

1. THE Python project SHALL include a requirements.txt file listing all Python dependencies (aws-cdk-lib, constructs, etc.)
2. THE Virtual_Environment (.venv directory) SHALL be created locally and not committed to version control (listed in .gitignore)
3. WHEN a developer runs setup instructions, THE process SHALL activate the Virtual_Environment and install dependencies from requirements.txt
4. THE Virtual_Environment Python version SHALL be compatible with AWS CDK requirements (Python 3.8 or higher, typically 3.10+)
5. THE project README SHALL include step-by-step instructions for local environment setup and CDK deployment
6. THE project structure SHALL follow Python and CDK conventions (source code in dedicated directories, configs in root or config/ folder)

### Requirement 14: Deployment to PROD Account

**User Story:** As a DevOps engineer, I want to deploy the infrastructure and website to the AWS PROD account (742xxxxx) with confidence that the correct account is targeted.

#### Acceptance Criteria

1. THE CDK code SHALL be configured to deploy to the PROD_Account (AWS account 742xxxxx)
2. THE deployment process SHALL include safeguards to prevent accidental deployment to non-PROD accounts (e.g., environment variable checks, stack naming conventions)
3. WHEN running CDK deploy, THE command SHALL require explicit confirmation before applying changes
4. THE CDK code SHALL use the correct AWS region (us-east-1, us-west-2, or as specified by OpusMagus)
5. AFTER deployment, THE CloudFront distribution and S3 bucket SHALL be visible in the PROD_Account AWS console
6. THE deployment process SHALL be documented with exact commands required (cdk synth, cdk deploy, etc.)

### Requirement 15: Website Asset Deployment

**User Story:** As a developer, I want to deploy the static website assets (HTML, CSS, JavaScript, images) to the S3 bucket, so that the website content is accessible via CloudFront.

#### Acceptance Criteria

1. THE static website files (index.html, service cards page, portfolio page, CSS, JavaScript, images) SHALL be organized in a project directory structure
2. WHEN deploying assets, THE build or deployment process SHALL copy all static files to the S3_Bucket with appropriate content types
3. THE S3 objects (files) SHALL have Cache-Control headers set according to asset type (HTML: short cache, CSS/JS/images: long cache)
4. WHERE image assets are used, THE images SHALL be optimized for web (compressed, appropriately sized) before deployment
5. AFTER asset deployment, THE website content SHALL be immediately accessible via the CloudFront distribution (respecting cache invalidation if needed)
6. THE deployment process SHALL include a rollback mechanism (e.g., reverting to previous S3 versions) for quick recovery from errors

### Requirement 16: Performance Optimization

**User Story:** As an OpusMagus stakeholder, I want the website to load quickly and efficiently, so that users have a positive experience and the site ranks well in search engines.

#### Acceptance Criteria

1. THE OpusMagus_Website Core Web Vitals SHALL meet Google's performance thresholds: LCP (Largest Contentful Paint) under 2.5s, FID (First Input Delay) under 100ms, CLS (Cumulative Layout Shift) under 0.1
2. THE OpusMagus_Website initial page load size SHALL not exceed 3 MB (including all assets)
3. THE HTML, CSS, and JavaScript files SHALL be minified to reduce file size
4. THE OpusMagus_Website images SHALL use modern formats (WebP) with fallbacks and be appropriately sized for different viewports
5. THE CloudFront distribution SHALL enable compression for text-based assets (HTML, CSS, JavaScript, JSON)
6. THE OpusMagus_Website SHALL use lazy-loading for below-the-fold images to defer non-critical image requests

### Requirement 17: Security Hardening

**User Story:** As a security stakeholder, I want the OpusMagus website infrastructure to follow security best practices, so that the site and user data are protected from common threats.

#### Acceptance Criteria

1. THE S3_Bucket public access block settings SHALL deny all public ACLs, public bucket policies, and require CloudFront for all access
2. THE CloudFront distribution SHALL have AWS WAF (Web Application Firewall) enabled with rules to block common attacks (SQL injection, XSS, etc.)
3. THE CloudFront distribution security headers SHALL include: Strict-Transport-Security (HSTS), Content-Security-Policy (CSP), X-Content-Type-Options, X-Frame-Options
4. THE S3_Bucket encryption SHALL be enabled using SSE-S3 or SSE-KMS
5. THE CDK code SHALL not include hardcoded secrets or credentials (use AWS Secrets Manager or environment variables)
6. THE OpusMagus_Website HTML pages SHALL not include external third-party scripts without security review and Content-Security-Policy approval

### Requirement 18: Monitoring and Logging

**User Story:** As an OpusMagus operations team member, I want visibility into website performance and issues, so that problems can be detected and resolved quickly.

#### Acceptance Criteria

1. THE CloudFront distribution logging SHALL be enabled to capture request and error data
2. THE S3_Bucket access logs SHALL be sent to a dedicated logging bucket or CloudWatch Logs
3. THE CDK code SHALL include CloudWatch dashboards or alarms for key metrics (4xx errors, 5xx errors, high latency)
4. WHEN an error occurs (e.g., missing asset, misconfiguration), THE logs SHALL contain sufficient detail to diagnose the issue
5. THE monitoring configuration SHALL track cache hit ratio, requests per second, and geographic distribution of users
6. WHERE critical issues are detected, THE alarms SHALL send notifications to OpusMagus operations team

### Requirement 19: Documentation and Runbooks

**User Story:** As a DevOps engineer or team member, I want comprehensive documentation covering setup, deployment, troubleshooting, and maintenance, so that anyone can manage the infrastructure.

#### Acceptance Criteria

1. THE project README SHALL include project overview, technology stack, and prerequisites
2. THE documentation SHALL include step-by-step local setup instructions (cloning repo, creating .venv, installing dependencies)
3. THE documentation SHALL include deployment instructions with exact CDK commands and expected outputs
4. THE documentation SHALL include runbooks for common tasks (updating content, invalidating CloudFront cache, scaling, rolling back)
5. THE documentation SHALL include troubleshooting guide for common issues (403 errors, cache invalidation, SSL certificate issues)
6. THE documentation SHALL be written in Markdown and maintained in the project repository

### Requirement 20: Content Management and Updates

**User Story:** As a marketing team member, I want an easy process to update website content (services, portfolio, text), so that I can keep the site current without requiring developer intervention.

#### Acceptance Criteria

1. THE static website content (HTML files) SHALL be organized in clearly labeled directories (index.html, services/index.html, portfolio/index.html)
2. THE website file structure SHALL allow non-developers to update text and links using a text editor or IDE
3. WHERE content changes are made, THE deployment process SHALL copy updated files to S3 with minimal manual steps
4. THE website content management process SHALL not require rebuilding or compiling (static files only)
5. THE documentation SHALL include instructions for common content updates (adding service cards, updating portfolio items, changing contact info)
6. AFTER content deployment to S3, THE CloudFront cache SHALL be invalidated to ensure updated content is served immediately (or automatic invalidation configured)

---

## End of Requirements Document

**Next Phase:** Design specifications will be generated in the next workflow phase. This requirements document establishes the foundation for translating the OpusMagus marketing website vision into concrete design and implementation tasks.
