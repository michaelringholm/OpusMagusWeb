"""Distribution Stack for OpusMagus CDK Infrastructure.

This stack creates and manages CloudFront distributions and CDN configuration
for the OpusMagus marketing website. Implements Requirement 9 (CloudFront
Distribution Configuration), Requirement 16 (Performance Optimization) and
Requirement 17 (Security Hardening).

Key Features:
    - CloudFront distribution with S3 origin via Origin Access Control (OAC)
    - Tiered cache behaviors with TTL-specific policies:
        * HTML: TTL 0 (no caching, always fresh)
        * CSS/JS: TTL 31536000 (1 year, immutable assets)
        * Images: TTL 86400 (1 day)
    - Compression: gzip and brotli for all compressible assets
    - HTTP → HTTPS redirect
    - Custom error pages (404 and 403 → /404.html)
    - CloudWatch logging for monitoring and debugging
    - Security headers (HSTS, CSP, X-Content-Type-Options, X-Frame-Options)
    - Default root object: index.html for directory requests
    - AWS WAF Web ACL integration for DDoS and attack prevention
"""

from typing import Optional

from aws_cdk import (
    Stack,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_s3 as s3,
    aws_certificatemanager as acm,
    aws_wafv2 as wafv2,
    aws_logs as logs,
    Duration,
    RemovalPolicy,
    Tags,
)
from constructs import Construct

from config import PRIMARY_DOMAIN, WWW_DOMAIN, ENVIRONMENT_TAG


class DistributionStack(Stack):
    """Stack for managing CloudFront distributions and content delivery.
    
    This stack configures a high-performance, secure CloudFront CDN for the
    OpusMagus website with industry-leading best practices including:
    
    - **Origin Access Control (OAC)**: Restricts S3 bucket access to CloudFront
      only, preventing direct public access to bucket URLs.
    - **Tiered Caching**: Different TTLs for different content types to balance
      freshness and performance.
    - **Compression**: Gzip and Brotli compression reduce bandwidth and improve
      load times, supporting Core Web Vitals targets.
    - **HTTP → HTTPS Redirect**: All traffic forced to encrypted connections.
    - **Error Handling**: Custom error pages provide better UX.
    - **CloudWatch Logging**: Detailed logs for monitoring, debugging, and
      compliance auditing.
    - **Security Headers**: Protects against common web vulnerabilities
      (XSS, clickjacking, MIME-type sniffing).
    - **AWS WAF Integration**: Web Application Firewall with managed rules and
      rate-based protection for DDoS and attack prevention.
    - **Default Root Object**: Serves index.html for root and directory paths.
    
    Validates Requirements 9 (CloudFront Config), 16 (Performance), 17 (Security).
    """

    def __init__(
        self,
        scope: Construct,
        id: str,
        s3_bucket: Optional[s3.Bucket] = None,
        certificate: Optional[acm.Certificate] = None,
        waf_web_acl: Optional[wafv2.CfnWebACL] = None,
        **kwargs
    ) -> None:
        """Initialize the DistributionStack.

        Args:
            scope: The scope (typically the app).
            id: The stack ID.
            s3_bucket: S3 bucket to use as CloudFront origin. Required.
            certificate: ACM certificate for HTTPS. If None, CloudFront will use
                default certificate (*.cloudfront.net).
            waf_web_acl: AWS WAF Web ACL to associate with CloudFront distribution.
                Provides DDoS and attack protection.
            **kwargs: Additional stack properties passed to parent Stack.
            
        Raises:
            ValueError: If s3_bucket is not provided.
        """
        super().__init__(scope, id, **kwargs)

        # Validate required parameters
        if s3_bucket is None:
            raise ValueError("S3 bucket must be provided to DistributionStack")

        # Create CloudFront Origin Access Control for secure S3 access
        # OAC restricts bucket access to CloudFront only, no direct public URLs
        oac = self._create_origin_access_control()

        # Create S3 origin with OAC
        s3_origin = origins.S3Origin(s3_bucket, origin_access_control=oac)

        # Create CloudWatch log group for CloudFront access logs
        cf_log_group = self._create_cloudwatch_log_group()

        # Create response headers policy with security headers
        security_headers_policy = self._create_security_headers_policy()

        # Create cache behavior policies for different content types
        html_cache_policy = self._create_cache_policy(
            "HTMLCachePolicy",
            comment="Cache policy for HTML files - no caching (TTL 0)",
            default_ttl=Duration.seconds(0),
            max_ttl=Duration.seconds(0),
            min_ttl=Duration.seconds(0),
        )

        asset_cache_policy = self._create_cache_policy(
            "AssetCachePolicy",
            comment="Cache policy for CSS/JS - 1 year TTL (immutable assets)",
            default_ttl=Duration.days(365),
            max_ttl=Duration.days(365),
            min_ttl=Duration.days(365),
        )

        image_cache_policy = self._create_cache_policy(
            "ImageCachePolicy",
            comment="Cache policy for images - 1 day TTL",
            default_ttl=Duration.days(1),
            max_ttl=Duration.days(1),
            min_ttl=Duration.days(1),
        )

        # Define cache behaviors for different content types
        cache_behaviors = self._create_cache_behaviors(
            s3_origin,
            html_cache_policy,
            asset_cache_policy,
            image_cache_policy,
            security_headers_policy,
        )

        # Create the CloudFront distribution
        distribution_props = {
            "default_behavior": cloudfront.BehaviorOptions(
                origin=s3_origin,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                cache_policy=html_cache_policy,
                compress=True,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                response_headers_policy=security_headers_policy,
            ),
            "additional_behaviors": cache_behaviors,
            "default_root_object": "index.html",
            "domain_names": [PRIMARY_DOMAIN, WWW_DOMAIN],
            "enable_logging": True,
            "log_bucket": None,  # Use CloudWatch logs instead of S3
            "error_responses": [
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_page_path="/404.html",
                    response_http_status=404,
                    ttl=Duration.minutes(5),
                ),
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_page_path="/404.html",
                    response_http_status=404,
                    ttl=Duration.minutes(5),
                ),
            ],
            "comment": "CloudFront distribution for OpusMagus website",
            "price_class": cloudfront.PriceClass.PRICE_CLASS_100,
        }

        # Add certificate if provided
        if certificate is not None:
            distribution_props["certificate"] = certificate

        # Add WAF Web ACL if provided
        if waf_web_acl is not None:
            distribution_props["web_acl"] = waf_web_acl

        distribution = cloudfront.Distribution(
            self,
            "OpusMagusDistribution",
            **distribution_props
        )

        # Add tags to the distribution
        Tags.of(distribution).add("Name", "OpusMagus-Distribution")
        Tags.of(distribution).add("Environment", ENVIRONMENT_TAG)

        # Export distribution domain name and reference for other stacks
        self.distribution_domain_name = distribution.domain_name
        self.distribution = distribution

    def _create_origin_access_control(self) -> "cloudfront.S3OriginAccessControl":
        """Create Origin Access Control for CloudFront to S3 access.
        
        S3OriginAccessControl is the newer, more secure alternative to OAI
        (Origin Access Identity). It restricts S3 bucket access to CloudFront only,
        preventing direct public access via bucket URLs.
        
        Returns:
            S3OriginAccessControl construct configured for S3 access.
        """
        return cloudfront.S3OriginAccessControl(
            self,
            "OpusMagusOAC",
        )

    def _create_cloudwatch_log_group(self) -> logs.LogGroup:
        """Create CloudWatch Log Group for CloudFront access logs.
        
        CloudFront logs are stored in CloudWatch Logs for queryable access logs,
        monitoring, and debugging. Logs are retained for one month then deleted.
        
        Returns:
            CloudWatch LogGroup for CloudFront access logs.
        """
        return logs.LogGroup(
            self,
            "OpusMagusCFLogs",
            log_group_name="/aws/cloudfront/opusmagus",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.DESTROY,
        )

    def _create_cache_policy(
        self,
        id: str,
        comment: str,
        default_ttl: Duration,
        max_ttl: Duration,
        min_ttl: Duration,
    ) -> cloudfront.CachePolicy:
        """Create a cache policy with specified TTL and compression settings.
        
        Cache policies control how CloudFront caches content from the origin.
        TTL values determine cache freshness: HTML uses TTL 0 (no caching), while
        immutable assets (CSS/JS with content hashes) use TTL 1 year.
        
        Args:
            id: Construct ID for this cache policy.
            comment: Human-readable description of cache behavior.
            default_ttl: Default time-to-live (how long objects cached).
            max_ttl: Maximum TTL (CloudFront won't cache beyond this).
            min_ttl: Minimum TTL (CloudFront won't cache below this).
            
        Returns:
            Configured CachePolicy with gzip and brotli compression enabled.
        """
        return cloudfront.CachePolicy(
            self,
            id,
            comment=comment,
            default_ttl=default_ttl,
            max_ttl=max_ttl,
            min_ttl=min_ttl,
            enable_accept_encoding_gzip=True,
            enable_accept_encoding_brotli=True,
        )

    def _create_security_headers_policy(
        self,
    ) -> cloudfront.ResponseHeadersPolicy:
        """Create response headers policy with comprehensive security headers.
        
        Security headers protect against common web vulnerabilities:
        - HSTS: Forces HTTPS, prevents downgrade attacks
        - CSP: Restricts resource loading, prevents XSS
        - X-Content-Type-Options: Prevents MIME-type sniffing
        - X-Frame-Options: Prevents clickjacking
        - Referrer-Policy: Controls what referrer info is sent
        
        Returns:
            ResponseHeadersPolicy with security headers configured.
        """
        return cloudfront.ResponseHeadersPolicy(
            self,
            "SecurityHeadersPolicy",
            comment="Security headers for OpusMagus website",
            security_headers_policy=cloudfront.SecurityHeadersPolicy(
                override=False,
                strict_transport_security=cloudfront.StrictTransportSecurityProperty(
                    override=False,
                    access_control_max_age=Duration.seconds(31536000),  # 1 year
                    include_subdomains=True,
                    preload=True,
                ),
                content_type_options=cloudfront.ContentTypeOptions(override=False),
                frame_options=cloudfront.FrameOptions(
                    frame_option=cloudfront.HeadersFrameOption.DENY,
                    override=False,
                ),
                xss_protection=cloudfront.XSSProtection(
                    override=False,
                    protection=True,
                    mode_block=True,
                ),
            ),
            custom_headers_policy=cloudfront.CustomHeadersPolicy(
                custom_headers=[
                    cloudfront.CustomHeader(
                        header="Content-Security-Policy",
                        value="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self';",
                        override=False,
                    ),
                    cloudfront.CustomHeader(
                        header="Referrer-Policy",
                        value="strict-origin-when-cross-origin",
                        override=False,
                    ),
                ]
            ),
        )

    def _create_cache_behaviors(
        self,
        origin: origins.S3Origin,
        html_policy: cloudfront.CachePolicy,
        asset_policy: cloudfront.CachePolicy,
        image_policy: cloudfront.CachePolicy,
        security_headers_policy: cloudfront.ResponseHeadersPolicy,
    ) -> list:
        """Create cache behaviors for different content types.
        
        Cache behaviors route different file types to appropriate cache policies:
        - HTML: No caching (TTL 0) - always fresh content
        - CSS/JS: Long cache (TTL 1 year) - immutable assets with content hashes
        - Images: Medium cache (TTL 1 day) - balance between freshness and efficiency
        
        Each behavior enables compression (gzip/brotli) for smaller file transfer
        and faster load times.
        
        Args:
            origin: S3 origin for the behaviors.
            html_policy: Cache policy for HTML files (TTL 0).
            asset_policy: Cache policy for CSS/JS files (TTL 1 year).
            image_policy: Cache policy for image files (TTL 1 day).
            security_headers_policy: Security headers policy to apply.
            
        Returns:
            List of CacheBehavior configurations for additional_behaviors.
        """
        return [
            # HTML files - no caching, always fresh
            cloudfront.CacheBehavior(
                path_pattern="*.html",
                origin=origin,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                cache_policy=html_policy,
                compress=True,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                response_headers_policy=security_headers_policy,
            ),
            # CSS - cache for 1 year (immutable)
            cloudfront.CacheBehavior(
                path_pattern="*.css",
                origin=origin,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                cache_policy=asset_policy,
                compress=True,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            # JavaScript - cache for 1 year (immutable)
            cloudfront.CacheBehavior(
                path_pattern="*.js",
                origin=origin,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                cache_policy=asset_policy,
                compress=True,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            # PNG images - cache for 1 day
            cloudfront.CacheBehavior(
                path_pattern="*.png",
                origin=origin,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                cache_policy=image_policy,
                compress=True,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            # JPEG images - cache for 1 day
            cloudfront.CacheBehavior(
                path_pattern="*.jpg",
                origin=origin,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                cache_policy=image_policy,
                compress=True,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            # JPEG alternative extension - cache for 1 day
            cloudfront.CacheBehavior(
                path_pattern="*.jpeg",
                origin=origin,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                cache_policy=image_policy,
                compress=True,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            # WebP images - cache for 1 day
            cloudfront.CacheBehavior(
                path_pattern="*.webp",
                origin=origin,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                cache_policy=image_policy,
                compress=True,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            # SVG images - cache for 1 day
            cloudfront.CacheBehavior(
                path_pattern="*.svg",
                origin=origin,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                cache_policy=image_policy,
                compress=True,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            # GIF images - cache for 1 day
            cloudfront.CacheBehavior(
                path_pattern="*.gif",
                origin=origin,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                cache_policy=image_policy,
                compress=True,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
        ]
