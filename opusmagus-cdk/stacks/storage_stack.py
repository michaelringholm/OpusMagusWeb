"""Storage Stack for OpusMagus CDK Infrastructure.

This stack creates and manages S3 buckets and related storage resources for
the OpusMagus marketing website. It implements security best practices including
versioning, encryption, access logging, and public access restrictions.
"""

from typing import Optional

import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudwatch as cloudwatch,
    aws_logs as logs,
    aws_iam as iam,
)
from constructs import Construct

from config import S3_BUCKET_NAME, ENVIRONMENT_TAG


class StorageStack(Stack):
    """Stack for managing S3 buckets and storage infrastructure.

    This stack creates a secured S3 bucket for static website hosting with:
    - Versioning enabled for rollback capability
    - Server-side encryption (SSE-S3)
    - All public access blocked (BlockPublicAcls, BlockPublicPolicy, etc.)
    - Access logging to CloudWatch Logs
    - Lifecycle configuration
    - CloudWatch alarms for monitoring
    - Origin Access Control (OAC) for CloudFront-only access
    """

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        """Initialize the StorageStack.

        Args:
            scope: The scope (typically the app)
            id: The stack ID
            **kwargs: Additional stack properties
        """
        super().__init__(scope, id, **kwargs)

        # Create CloudWatch Log Group for access logging
        log_group = self._create_log_group()

        # Create the main S3 bucket
        bucket = self._create_s3_bucket(log_group)

        # Create Origin Access Control for CloudFront
        oac = self._create_origin_access_control()

        # Export the bucket and OAC for use by other stacks
        self.bucket = bucket
        self.website_bucket = bucket  # Alias for clarity
        self.bucket_name = bucket.bucket_name
        self.bucket_arn = bucket.bucket_arn
        self.bucket_domain_name = bucket.bucket_domain_name
        self.origin_access_control = oac

        # Create alarms for monitoring
        self._create_cloudwatch_alarms(bucket)

    def _create_log_group(self) -> logs.LogGroup:
        """Create CloudWatch Log Group for S3 access logging.

        Returns:
            CloudWatch LogGroup for S3 access logs
        """
        log_group = logs.LogGroup(
            self,
            "S3AccessLogs",
            log_group_name="/aws/s3/opusmagus-access-logs",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        return log_group

    def _create_origin_access_control(
        self,
    ) -> cloudfront.S3OriginAccessControl:
        """Create Origin Access Control for CloudFront.

        OAC provides a secure way for CloudFront to access S3 buckets
        without exposing the bucket publicly or using legacy OAI.

        Returns:
            CloudFront S3OriginAccessControl instance
        """
        oac = cloudfront.S3OriginAccessControl(
            self,
            "CloudFrontOAC",
            name="OpusMagus-CloudFront-OAC",
        )

        return oac

    def _create_s3_bucket(
        self, log_group: logs.LogGroup
    ) -> s3.Bucket:
        """Create the main S3 bucket with security configurations.

        This bucket is configured for static website hosting with:
        - Versioning for rollback capability
        - SSE-S3 encryption at rest
        - Public access completely blocked
        - Access logging to CloudWatch Logs
        - Lifecycle rules for cost optimization

        Args:
            log_group: CloudWatch LogGroup for access logging

        Returns:
            Configured S3 Bucket instance
        """
        bucket = s3.Bucket(
            self,
            "WebsiteBucket",
            bucket_name=S3_BUCKET_NAME,
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=True,
                block_public_policy=True,
                ignore_public_acls=True,
                restrict_public_buckets=True,
            ),
            access_log=s3.LogFileFormat.PARQUET.with_log_group(log_group),
            lifecycle_rules=[
                s3.LifecycleRule(
                    noncurrent_version_expiration=cdk.Duration.days(90),
                    noncurrent_version_transitions=[
                        s3.NoncurrentVersionTransition(
                            storage_class=s3.StorageClass.INTELLIGENT_TIERING,
                            transition_after=cdk.Duration.days(30),
                        ),
                    ],
                ),
                s3.LifecycleRule(
                    abort_incomplete_multipart_upload_after=cdk.Duration.days(7),
                ),
            ],
            public_read_access=False,
            removal_policy=cdk.RemovalPolicy.RETAIN,
        )

        # Add explicit deny policy for direct public access
        # This ensures only CloudFront OAC can access the bucket
        bucket.add_to_resource_policy(
            iam.PolicyStatement(
                sid="DenyDirectPublicAccess",
                effect=iam.Effect.DENY,
                principals=[iam.AnyPrincipal()],
                actions=["s3:GetObject", "s3:GetObjectVersion"],
                resources=[bucket.arn_for_objects("*")],
                conditions={
                    "StringNotEquals": {
                        "aws:SourceArn": [
                            f"arn:aws:cloudfront::{self.account}:distribution/*"
                        ]
                    }
                },
            )
        )

        # Add bucket policy to allow CloudFront with OAC
        bucket.add_to_resource_policy(
            iam.PolicyStatement(
                sid="AllowCloudFrontWithOAC",
                effect=iam.Effect.ALLOW,
                principals=[iam.ServicePrincipal("cloudfront.amazonaws.com")],
                actions=["s3:GetObject"],
                resources=[bucket.arn_for_objects("*")],
            )
        )

        # Add tags for resource identification
        cdk.Tags.of(bucket).add("Name", "OpusMagus-Website-Bucket")
        cdk.Tags.of(bucket).add("Environment", ENVIRONMENT_TAG)
        cdk.Tags.of(bucket).add("Purpose", "Static Website Hosting")

        return bucket

    def _create_cloudwatch_alarms(self, bucket: s3.Bucket) -> None:
        """Create CloudWatch alarms for S3 bucket monitoring.

        Creates alarms for:
        - Bucket size threshold
        - Client errors (4xx)
        - Server errors (5xx)
        - Replication failures

        Args:
            bucket: The S3 bucket to monitor
        """
        # Alarm for bucket size (warn if exceeds 500MB)
        cloudwatch.Alarm(
            self,
            "BucketSizeAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/S3",
                metric_name="BucketSizeBytes",
                dimensions_map={"BucketName": bucket.bucket_name},
                statistic="Average",
                period=cdk.Duration.hours(1),
            ),
            threshold=500 * 1024 * 1024,  # 500MB
            evaluation_periods=1,
            alarm_description="Alert when S3 bucket size exceeds 500MB",
            alarm_name=f"{bucket.bucket_name}-size-alert",
        )

        # Alarm for 4xx errors (client errors)
        cloudwatch.Alarm(
            self,
            "BucketClientErrorsAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/S3",
                metric_name="4xxErrors",
                dimensions_map={"BucketName": bucket.bucket_name},
                statistic="Sum",
                period=cdk.Duration.minutes(5),
            ),
            threshold=10,
            evaluation_periods=1,
            alarm_description="Alert when S3 bucket experiences high 4xx error rate",
            alarm_name=f"{bucket.bucket_name}-4xx-errors",
        )

        # Alarm for 5xx errors (server errors)
        cloudwatch.Alarm(
            self,
            "BucketServerErrorsAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/S3",
                metric_name="5xxErrors",
                dimensions_map={"BucketName": bucket.bucket_name},
                statistic="Sum",
                period=cdk.Duration.minutes(5),
            ),
            threshold=5,
            evaluation_periods=1,
            alarm_description="Alert when S3 bucket experiences server errors",
            alarm_name=f"{bucket.bucket_name}-5xx-errors",
        )

        # Alarm for replication failures (if replication configured)
        cloudwatch.Alarm(
            self,
            "ReplicationFailureAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/S3",
                metric_name="OperationsFailed",
                dimensions_map={"BucketName": bucket.bucket_name},
                statistic="Sum",
                period=cdk.Duration.hours(1),
            ),
            threshold=1,
            evaluation_periods=1,
            alarm_description="Alert on any S3 bucket operation failures",
            alarm_name=f"{bucket.bucket_name}-operation-failures",
        )
