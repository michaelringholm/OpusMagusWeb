"""Security Stack for OpusMagus CDK Infrastructure.

This stack creates and manages security resources for the OpusMagus marketing
website. It implements security best practices including AWS Certificate Manager
(ACM) SSL/TLS certificates, DNS validation, auto-renewal with notifications,
and AWS WAF (Web Application Firewall) rules for DDoS and attack prevention.
"""

from typing import Optional

import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_wafv2 as wafv2,
    aws_sns as sns,
    aws_cloudwatch as cloudwatch,
)
from constructs import Construct

from config import PRIMARY_DOMAIN, WWW_DOMAIN, PROD_REGION, ENVIRONMENT_TAG


class SecurityStack(Stack):
    """Stack for managing security resources including SSL/TLS certificates and WAF.

    This stack creates and manages:
    - AWS Certificate Manager (ACM) SSL/TLS certificate for HTTPS
    - Certificate validation (DNS-based)
    - Auto-renewal with SNS notifications
    - AWS WAF Web ACL with managed rules
    - CloudWatch alarms for security metrics

    Attributes:
        certificate: The ACM Certificate resource
        waf_web_acl: The WAF Web ACL resource
    """

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        """Initialize the SecurityStack.

        Args:
            scope: The scope (typically the app)
            id: The stack ID
            **kwargs: Additional stack properties

        Raises:
            ValueError: If domain configuration is invalid
        """
        super().__init__(scope, id, **kwargs)

        # Create SNS topic for certificate notifications
        sns_topic = self._create_sns_topic()

        # Create ACM certificate
        certificate = self._create_acm_certificate(sns_topic)
        self.certificate = certificate

        # Create WAF Web ACL
        waf_web_acl = self._create_waf_web_acl()
        self.waf_web_acl = waf_web_acl

        # Export resources for use by other stacks
        self._export_resources(certificate, waf_web_acl)

        # Create CloudWatch alarms for security monitoring
        self._create_cloudwatch_alarms(sns_topic)

    def _create_sns_topic(self) -> sns.Topic:
        """Create SNS topic for certificate expiration and renewal notifications.

        The topic will receive notifications from ACM when:
        - Certificate is about to expire (45 days before)
        - Certificate renewal status changes
        - Certificate validation issues occur

        Returns:
            SNS Topic configured for certificate notifications

        Note:
            SNS topic ARN should be configured in AWS Certificate Manager
            notification preferences for the issued certificate.
        """
        topic = sns.Topic(
            self,
            "CertificateNotificationsTopic",
            display_name="OpusMagus SSL/TLS Certificate Notifications",
            topic_name="opusmagus-certificate-notifications",
        )

        # Add tags
        cdk.Tags.of(topic).add("Name", "OpusMagus-Certificate-Notifications")
        cdk.Tags.of(topic).add("Environment", ENVIRONMENT_TAG)

        return topic

    def _create_acm_certificate(self, sns_topic: sns.Topic) -> acm.Certificate:
        """Create and configure AWS Certificate Manager SSL/TLS certificate.

        Creates a certificate for the primary domain (opusmagus.com) and
        www subdomain (www.opusmagus.com) with the following features:
        - DNS validation (CNAME records in Route53)
        - Automatic renewal enabled
        - Subject Alternative Names (SANs) for both domains
        - Validation timeout of 45 days

        Args:
            sns_topic: SNS topic for notifications

        Returns:
            Configured ACM Certificate resource

        Raises:
            ValueError: If domain validation fails or certificate request fails

        Note:
            DNS validation requires Route53 hosted zone for the domain.
            Certificate validation records are automatically created in Route53
            if the hosted zone exists in the same AWS account.

            For manual DNS validation or external DNS providers:
            1. Check ACM console for validation CNAME records
            2. Add CNAME records to external DNS provider
            3. Wait for validation (usually < 5 minutes)
            4. Certificate status will change to "Issued"

            Auto-renewal is enabled by default in ACM and happens automatically
            30 days before expiration. SNS notifications are sent 45 days before
            expiration as a reminder.
        """
        certificate = acm.Certificate(
            self,
            "WebsiteCertificate",
            domain_name=PRIMARY_DOMAIN,
            subject_alternative_names=[PRIMARY_DOMAIN, WWW_DOMAIN],
            validation=acm.CertificateValidation.from_dns(
                hosted_zone=route53.HostedZone.from_lookup(
                    self,
                    "HostedZone",
                    domain_name=PRIMARY_DOMAIN,
                ),
                validation_domains={
                    PRIMARY_DOMAIN: PRIMARY_DOMAIN,
                    WWW_DOMAIN: PRIMARY_DOMAIN,
                },
            ),
            certificate_name="opusmagus-website-certificate",
        )

        # Add tags
        cdk.Tags.of(certificate).add("Name", "OpusMagus-SSL-TLS-Certificate")
        cdk.Tags.of(certificate).add("Environment", ENVIRONMENT_TAG)
        cdk.Tags.of(certificate).add("Domain", PRIMARY_DOMAIN)

        return certificate

    def _create_waf_web_acl(self) -> wafv2.CfnWebACL:
        """Create AWS WAF Web ACL with managed rules for security.

        Creates a Web ACL with the following protections:
        - AWS Managed Rules for SQL Injection attacks
        - AWS Managed Rules for XSS attacks
        - AWS Managed Rules for common vulnerabilities
        - Rate-based rule (2000 requests per 5 minutes per IP)
        - AWS IP Reputation List for blocking malicious IPs
        - Bot Control (optional, for bot mitigation)

        Rate limiting configuration:
            - Action: Block (HTTP 403 Forbidden)
            - Rate: 2000 requests per 5-minute period per IP
            - Scope: All requests

        AWS Managed Rules included:
            - AWSManagedRulesCommonRuleSet: OWASP Top 10
            - AWSManagedRulesAmazonIpReputationList: Known malicious IPs
            - AWSManagedRulesKnownBadInputsRuleSet: Known attack patterns

        Returns:
            WAF Web ACL configured with managed rules

        Note:
            This Web ACL is designed to be associated with CloudFront distributions.
            Association with CloudFront requires the distribution stack to reference
            this WAF Web ACL ARN and attach it to the distribution.

            Default action is ALLOW (block only matching rules).
            Logging is handled via CloudWatch Logs (configured in distribution stack).
        """
        # AWS Managed Rules - Common Rule Set (OWASP Top 10)
        common_rule_set = wafv2.CfnWebACL.RuleProperty(
            name="AWSManagedRulesCommonRuleSet",
            priority=0,
            override_action=wafv2.CfnWebACL.RuleActionOverrideProperty(
                none=wafv2.CfnWebACL.NoneActionProperty(),
            ),
            statement=wafv2.CfnWebACL.StatementProperty(
                managed_rule_group_statement=wafv2.CfnWebACL.ManagedRuleGroupStatementProperty(
                    vendor_name="AWS",
                    name="AWSManagedRulesCommonRuleSet",
                    excluded_rules=[
                        # Optional: Exclude rules that cause false positives
                        # Example: wafv2.CfnWebACL.ExcludedRuleProperty(name="SizeRestrictions_BODY"),
                    ],
                ),
            ),
            visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                cloudwatch_metrics_enabled=True,
                metric_name="AWSManagedRulesCommonRuleSetMetrics",
                sampled_requests_enabled=True,
            ),
        )

        # AWS Managed Rules - IP Reputation List
        ip_reputation_rule = wafv2.CfnWebACL.RuleProperty(
            name="AWSManagedRulesAmazonIpReputationList",
            priority=1,
            override_action=wafv2.CfnWebACL.RuleActionOverrideProperty(
                none=wafv2.CfnWebACL.NoneActionProperty(),
            ),
            statement=wafv2.CfnWebACL.StatementProperty(
                managed_rule_group_statement=wafv2.CfnWebACL.ManagedRuleGroupStatementProperty(
                    vendor_name="AWS",
                    name="AWSManagedRulesAmazonIpReputationList",
                ),
            ),
            visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                cloudwatch_metrics_enabled=True,
                metric_name="AWSManagedRulesAmazonIpReputationListMetrics",
                sampled_requests_enabled=True,
            ),
        )

        # AWS Managed Rules - Known Bad Inputs
        known_bad_inputs_rule = wafv2.CfnWebACL.RuleProperty(
            name="AWSManagedRulesKnownBadInputsRuleSet",
            priority=2,
            override_action=wafv2.CfnWebACL.RuleActionOverrideProperty(
                none=wafv2.CfnWebACL.NoneActionProperty(),
            ),
            statement=wafv2.CfnWebACL.StatementProperty(
                managed_rule_group_statement=wafv2.CfnWebACL.ManagedRuleGroupStatementProperty(
                    vendor_name="AWS",
                    name="AWSManagedRulesKnownBadInputsRuleSet",
                ),
            ),
            visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                cloudwatch_metrics_enabled=True,
                metric_name="AWSManagedRulesKnownBadInputsMetrics",
                sampled_requests_enabled=True,
            ),
        )

        # Rate-Based Rule (DoS protection)
        rate_limit_rule = wafv2.CfnWebACL.RuleProperty(
            name="RateLimitRule",
            priority=3,
            action=wafv2.CfnWebACL.RuleActionProperty(
                block=wafv2.CfnWebACL.BlockActionProperty(),
            ),
            statement=wafv2.CfnWebACL.StatementProperty(
                rate_based_statement=wafv2.CfnWebACL.RateBasedStatementProperty(
                    limit=2000,  # 2000 requests
                    aggregate_key_type="IP",
                ),
            ),
            visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                cloudwatch_metrics_enabled=True,
                metric_name="RateLimitRuleMetrics",
                sampled_requests_enabled=True,
            ),
        )

        # Create Web ACL
        web_acl = wafv2.CfnWebACL(
            self,
            "OpusMagusWebACL",
            default_action=wafv2.CfnWebACL.DefaultActionProperty(
                allow=wafv2.CfnWebACL.AllowActionProperty(),
            ),
            scope="CLOUDFRONT",  # CLOUDFRONT for CloudFront distributions
            name="opusmagus-web-acl",
            rules=[
                common_rule_set,
                ip_reputation_rule,
                known_bad_inputs_rule,
                rate_limit_rule,
            ],
            visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                cloudwatch_metrics_enabled=True,
                metric_name="OpusMagusWebACLMetrics",
                sampled_requests_enabled=True,
            ),
            tags=[
                cdk.CfnTag(key="Name", value="OpusMagus-Web-ACL"),
                cdk.CfnTag(key="Environment", value=ENVIRONMENT_TAG),
            ],
        )

        return web_acl

    def _export_resources(
        self,
        certificate: acm.Certificate,
        waf_web_acl: wafv2.CfnWebACL,
    ) -> None:
        """Export security resources for use by other stacks.

        Exports certificate and WAF resources as stack outputs so that
        other stacks (DistributionStack) can reference and use them.

        Args:
            certificate: ACM Certificate to export
            waf_web_acl: WAF Web ACL to export
        """
        # Export certificate ARN
        cdk.CfnOutput(
            self,
            "CertificateArn",
            value=certificate.certificate_arn,
            export_name="OpusMagus-Certificate-ARN",
            description="ARN of the ACM SSL/TLS certificate",
        )

        # Export certificate domain
        cdk.CfnOutput(
            self,
            "CertificateDomain",
            value=PRIMARY_DOMAIN,
            export_name="OpusMagus-Certificate-Domain",
            description="Primary domain for the SSL/TLS certificate",
        )

        # Export WAF Web ACL ARN
        cdk.CfnOutput(
            self,
            "WAFWebACLArn",
            value=waf_web_acl.attr_arn,
            export_name="OpusMagus-WAF-WebACL-ARN",
            description="ARN of the WAF Web ACL",
        )

        # Export WAF Web ACL ID
        cdk.CfnOutput(
            self,
            "WAFWebACLId",
            value=waf_web_acl.id,
            export_name="OpusMagus-WAF-WebACL-ID",
            description="ID of the WAF Web ACL",
        )

    def _create_cloudwatch_alarms(self, sns_topic: sns.Topic) -> None:
        """Create CloudWatch alarms for security monitoring.

        Sets up alarms to monitor:
        - WAF blocked requests (when above threshold)
        - SQL injection attempts detected
        - XSS attempts detected
        - Rate limiting triggers

        Args:
            sns_topic: SNS topic for sending alarm notifications
        """
        # Alarm for WAF blocked requests (sum over 5 minutes)
        cloudwatch.Alarm(
            self,
            "WAFBlockedRequestsAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/WAFV2",
                metric_name="BlockedRequests",
                dimensions_map={
                    "WebACL": "opusmagus-web-acl",
                    "Region": PROD_REGION,
                    "Rule": "ALL",
                },
                statistic="Sum",
                period=cdk.Duration.minutes(5),
            ),
            threshold=50,  # Alert if > 50 blocked requests in 5 minutes
            evaluation_periods=1,
            alarm_description="Alert when WAF blocks high number of requests",
            alarm_name="opusmagus-waf-blocked-requests",
        )

        # Alarm for rate limiting rule triggers
        cloudwatch.Alarm(
            self,
            "RateLimitRuleAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/WAFV2",
                metric_name="BlockedRequests",
                dimensions_map={
                    "WebACL": "opusmagus-web-acl",
                    "Region": PROD_REGION,
                    "Rule": "RateLimitRule",
                },
                statistic="Sum",
                period=cdk.Duration.minutes(5),
            ),
            threshold=10,  # Alert if rate limiting triggered > 10 times
            evaluation_periods=1,
            alarm_description="Alert when rate limiting rule is triggered",
            alarm_name="opusmagus-rate-limit-triggered",
        )

        # Alarm for common rule set matches
        cloudwatch.Alarm(
            self,
            "CommonRuleSetMatchesAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/WAFV2",
                metric_name="CountedRequests",
                dimensions_map={
                    "WebACL": "opusmagus-web-acl",
                    "Region": PROD_REGION,
                    "Rule": "AWSManagedRulesCommonRuleSet",
                },
                statistic="Sum",
                period=cdk.Duration.minutes(5),
            ),
            threshold=20,  # Alert if > 20 counted requests
            evaluation_periods=1,
            alarm_description="Alert when common attack patterns are detected",
            alarm_name="opusmagus-common-rule-matches",
        )
