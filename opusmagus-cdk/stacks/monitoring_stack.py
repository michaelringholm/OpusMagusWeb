"""Monitoring Stack for OpusMagus CDK Infrastructure."""

from typing import Optional
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    aws_sns as sns,
    aws_logs as logs,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    Duration,
    RemovalPolicy,
)
from constructs import Construct


class MonitoringStack(Stack):
    """Stack for CloudWatch monitoring, dashboards, and alarms."""

    def __init__(
        self,
        scope: Construct,
        id: str,
        cloudfront_distribution: Optional[cloudfront.Distribution] = None,
        s3_bucket: Optional[s3.Bucket] = None,
        **kwargs
    ) -> None:
        """Initialize the MonitoringStack."""
        super().__init__(scope, id, **kwargs)

        # Create SNS topic for notifications
        self.alarm_topic = sns.Topic(
            self,
            "AlarmTopic",
            display_name="OpusMagus Alarms",
            topic_name="opusmagus-alarms",
        )

        # Create CloudWatch dashboard
        self.dashboard = cloudwatch.Dashboard(
            self,
            "OpusMagusDashboard",
            dashboard_name="opusmagus-website",
        )

        # Add sample widgets if distribution available
        if cloudfront_distribution:
            dist_id = cloudfront_distribution.distribution_id
            self.dashboard.add_widgets(
                cloudwatch.GraphWidget(
                    title="CloudFront Requests",
                    left=[
                        cloudwatch.Metric(
                            namespace="AWS/CloudFront",
                            metric_name="Requests",
                            dimensions_map={"DistributionId": dist_id},
                            statistic="Sum",
                            period=Duration.minutes(5),
                        )
                    ],
                ),
                cloudwatch.GraphWidget(
                    title="4XX Errors",
                    left=[
                        cloudwatch.Metric(
                            namespace="AWS/CloudFront",
                            metric_name="4XXError",
                            dimensions_map={"DistributionId": dist_id},
                            statistic="Sum",
                            period=Duration.minutes(5),
                        )
                    ],
                ),
            )

        # Create log group
        self.log_group = logs.LogGroup(
            self,
            "AccessLogs",
            log_group_name="/aws/opusmagus/access-logs",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.DESTROY,
        )
