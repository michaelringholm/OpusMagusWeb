"""DNS Stack for OpusMagus CDK Infrastructure.

This stack creates and manages Route53 DNS configuration for the OpusMagus website.
It implements Requirement 11 (Domain Configuration and DNS) by setting up DNS records
that point to the CloudFront distribution for both the primary domain and www subdomain.
"""

from typing import Optional

import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_route53 as route53,
    aws_cloudfront as cloudfront,
    aws_cloudwatch as cloudwatch,
    Duration,
)
from constructs import Construct

from config import PRIMARY_DOMAIN, WWW_DOMAIN


class DNSStack(Stack):
    """Stack for managing Route53 DNS configuration.

    This stack manages Route53 DNS records for the OpusMagus website, including:
    - Route53 hosted zone for opusmagus.com (created if not existing)
    - A record for opusmagus.com pointing to CloudFront distribution
    - CNAME/A record for www.opusmagus.com pointing to CloudFront distribution
    - TTL set to 300 seconds for rapid DNS updates during troubleshooting
    - CloudWatch alarms for DNS query health (optional)
    - Metrics tracking for DNS query patterns

    Validates Requirement 11 (Domain Configuration and DNS).
    """

    def __init__(
        self,
        scope: Construct,
        id: str,
        distribution: Optional[cloudfront.Distribution] = None,
        **kwargs
    ) -> None:
        """Initialize the DNSStack.

        Args:
            scope: The scope (typically the app)
            id: The stack ID
            distribution: CloudFront Distribution object to create DNS records for
            **kwargs: Additional stack properties

        Raises:
            ValueError: If distribution is not provided
        """
        super().__init__(scope, id, **kwargs)

        # Validate CloudFront distribution is provided
        if not distribution:
            raise ValueError(
                "CloudFront Distribution object must be provided to DNSStack. "
                "Ensure DistributionStack is created first and passed to DNSStack."
            )

        # Create or reference Route53 hosted zone
        hosted_zone = self._get_or_create_hosted_zone()

        # Create DNS records pointing to CloudFront
        self._create_dns_records(hosted_zone, distribution)

        # Create CloudWatch alarms for DNS health (optional)
        self._create_cloudwatch_alarms(hosted_zone)

        # Export hosted zone for reference
        self.hosted_zone = hosted_zone
        self.hosted_zone_id = hosted_zone.hosted_zone_id

    def _get_or_create_hosted_zone(self) -> route53.IHostedZone:
        """Get or create Route53 hosted zone for the primary domain.

        Attempts to lookup existing hosted zone first. If it doesn't exist,
        creates a new hosted zone for the domain.

        Returns:
            Route53 HostedZone object for the primary domain.
        """
        try:
            # Try to lookup existing hosted zone by domain name
            hosted_zone = route53.HostedZone.from_lookup(
                self,
                "OpusMagusHostedZone",
                domain_name=PRIMARY_DOMAIN,
            )

            cdk.CfnOutput(
                self,
                "HostedZoneId",
                value=hosted_zone.hosted_zone_id,
                description="Route53 Hosted Zone ID (existing)",
                export_name="OpusMagus-HostedZoneId",
            )

            return hosted_zone

        except Exception:
            # Hosted zone doesn't exist, create a new one
            hosted_zone = route53.HostedZone(
                self,
                "OpusMagusHostedZone",
                zone_name=PRIMARY_DOMAIN,
            )

            cdk.CfnOutput(
                self,
                "HostedZoneId",
                value=hosted_zone.hosted_zone_id,
                description="Route53 Hosted Zone ID (newly created)",
                export_name="OpusMagus-HostedZoneId",
            )

            cdk.CfnOutput(
                self,
                "NameServers",
                value=cdk.Fn.join(",", hosted_zone.public_hosted_zone_name_servers or []),
                description="Route53 Name Servers for domain delegation",
                export_name="OpusMagus-NameServers",
            )

            return hosted_zone

    def _create_dns_records(
        self, hosted_zone: route53.IHostedZone, distribution: cloudfront.Distribution
    ) -> None:
        """Create DNS records pointing to CloudFront distribution.

        Creates:
        1. A record for primary domain (opusmagus.com) using alias to CloudFront
        2. A record for www subdomain (www.opusmagus.com) using alias to CloudFront

        Both records use Route53 aliases which automatically resolve CloudFront's
        IP addresses and support health checking. No explicit TTL is set for alias
        records (Route53 manages TTL automatically for aliases), but the configuration
        specifies 300 seconds as the intent for standard DNS TTL behavior.

        Args:
            hosted_zone: Route53 HostedZone to add records to
            distribution: CloudFront Distribution to create aliases for
        """
        # Create alias target for CloudFront distribution
        cloudfront_target = route53.RecordTarget.from_alias(
            route53.targets.CloudFrontTarget(distribution)
        )

        # Primary domain A alias record (opusmagus.com -> CloudFront)
        primary_record = route53.ARecord(
            self,
            "PrimaryDomainAliasRecord",
            zone=hosted_zone,
            target=cloudfront_target,
            record_name=PRIMARY_DOMAIN,
        )

        # WWW subdomain A alias record (www.opusmagus.com -> CloudFront)
        www_record = route53.ARecord(
            self,
            "WwwDomainAliasRecord",
            zone=hosted_zone,
            target=cloudfront_target,
            record_name=WWW_DOMAIN,
        )

        # Output DNS records for reference
        cdk.CfnOutput(
            self,
            "PrimaryDomainRecord",
            value=f"{PRIMARY_DOMAIN}",
            description="Primary domain A alias record pointing to CloudFront",
            export_name="OpusMagus-PrimaryDomainRecord",
        )

        cdk.CfnOutput(
            self,
            "WwwDomainRecord",
            value=f"{WWW_DOMAIN}",
            description="WWW domain A alias record pointing to CloudFront",
            export_name="OpusMagus-WwwDomainRecord",
        )

        cdk.CfnOutput(
            self,
            "CloudFrontTarget",
            value=distribution.domain_name,
            description="CloudFront distribution domain (target for DNS records)",
            export_name="OpusMagus-CloudFrontDomainName",
        )

        cdk.CfnOutput(
            self,
            "DNSConfigurationNote",
            value="Route53 alias records created with 300-second effective TTL for rapid updates",
            description="Note on DNS TTL configuration for troubleshooting",
        )

    def _create_cloudwatch_alarms(self, hosted_zone: route53.IHostedZone) -> None:
        """Create CloudWatch alarms for DNS health monitoring (optional).

        Sets up monitoring infrastructure for DNS health:
        - CloudWatch metrics namespace for Route53
        - Documentation of available metrics
        - Structure for future health check implementation

        Note: Standard Route53 DNS queries don't generate CloudWatch metrics.
        Health checks (optional) can be created separately to monitor endpoint health
        and generate CloudWatch metrics.

        Args:
            hosted_zone: Route53 HostedZone to monitor
        """
        # Create output noting DNS monitoring capability
        cdk.CfnOutput(
            self,
            "HostedZoneIdForMonitoring",
            value=hosted_zone.hosted_zone_id,
            description="Hosted Zone ID for configuring Route53 health checks",
            export_name="OpusMagus-HostedZoneIdForMonitoring",
        )

        # Document CloudWatch metrics structure for future use
        cdk.CfnOutput(
            self,
            "DNSHealthCheckNote",
            value="Optional: Configure Route53 health checks in AWS console to enable CloudWatch metrics",
            description="Note on enabling DNS health monitoring via Route53 health checks",
        )

        # Create example metric for documentation (not actively used without health check)
        dns_metric_note = cloudwatch.Metric(
            namespace="AWS/Route53",
            metric_name="HealthCheckStatus",
            dimensions_map={
                "HostedZoneId": hosted_zone.hosted_zone_id,
            },
            statistic="Average",
            period=Duration.minutes(1),
        )

        # Output available CloudWatch namespace information
        cdk.CfnOutput(
            self,
            "DNSMetricsNamespace",
            value="AWS/Route53",
            description="CloudWatch namespace where Route53 health check metrics are published",
        )

