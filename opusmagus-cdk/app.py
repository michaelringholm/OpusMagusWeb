#!/usr/bin/env python3
"""OpusMagus CDK Infrastructure Application."""

import aws_cdk as cdk
from config import PROD_ACCOUNT_ID, PROD_REGION, ENVIRONMENT_TAG
from stacks import StorageStack, DistributionStack, SecurityStack, DNSStack, MonitoringStack


def create_app() -> cdk.App:
    """Create and configure the CDK application."""
    app = cdk.App()
    env = cdk.Environment(account=PROD_ACCOUNT_ID, region=PROD_REGION)

    # Storage Stack
    storage_stack = StorageStack(
        app,
        "OpusMagus-StorageStack",
        env=env,
    )
    cdk.Tags.of(storage_stack).add("Environment", ENVIRONMENT_TAG)
    cdk.Tags.of(storage_stack).add("Project", "OpusMagus")

    # Security Stack
    security_stack = SecurityStack(
        app,
        "OpusMagus-SecurityStack",
        env=env,
    )
    cdk.Tags.of(security_stack).add("Environment", ENVIRONMENT_TAG)
    cdk.Tags.of(security_stack).add("Project", "OpusMagus")

    # Distribution Stack
    distribution_stack = DistributionStack(
        app,
        "OpusMagus-DistributionStack",
        s3_bucket=storage_stack.website_bucket,
        certificate=security_stack.certificate,
        waf_web_acl=security_stack.web_acl,
        env=env,
    )
    distribution_stack.add_dependency(storage_stack)
    distribution_stack.add_dependency(security_stack)
    cdk.Tags.of(distribution_stack).add("Environment", ENVIRONMENT_TAG)
    cdk.Tags.of(distribution_stack).add("Project", "OpusMagus")

    # DNS Stack
    dns_stack = DNSStack(
        app,
        "OpusMagus-DNSStack",
        distribution=distribution_stack.distribution,
        env=env,
    )
    dns_stack.add_dependency(distribution_stack)
    cdk.Tags.of(dns_stack).add("Environment", ENVIRONMENT_TAG)
    cdk.Tags.of(dns_stack).add("Project", "OpusMagus")

    # Monitoring Stack
    monitoring_stack = MonitoringStack(
        app,
        "OpusMagus-MonitoringStack",
        cloudfront_distribution=distribution_stack.distribution,
        s3_bucket=storage_stack.website_bucket,
        env=env,
    )
    monitoring_stack.add_dependency(distribution_stack)
    monitoring_stack.add_dependency(storage_stack)
    cdk.Tags.of(monitoring_stack).add("Environment", ENVIRONMENT_TAG)
    cdk.Tags.of(monitoring_stack).add("Project", "OpusMagus")

    return app


if __name__ == "__main__":
    app = create_app()
    app.synth()
