"""Configuration for OpusMagus CDK Infrastructure.

This module contains environment-specific configuration for AWS CDK deployment.
All configuration is read from environment variables with sensible defaults.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AWS Account and Region Configuration
PROD_ACCOUNT_ID = os.getenv("PROD_ACCOUNT_ID", "742197632521")
PROD_REGION = os.getenv("PROD_REGION", "us-east-1")

# Domain Configuration
PRIMARY_DOMAIN = os.getenv("PRIMARY_DOMAIN", "opusmagus.com")
WWW_DOMAIN = os.getenv("WWW_DOMAIN", "www.opusmagus.com")

# Storage Configuration
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "opusmagus-com-prod")

# Environment Tag for resource identification
ENVIRONMENT_TAG = os.getenv("ENVIRONMENT_TAG", "prod")

# Stack Configuration
STACKS_CONFIG = {
    "storage_stack": {
        "stack_name": "OpusMagus-StorageStack",
        "description": "Storage resources including S3 buckets and configuration",
    },
    "distribution_stack": {
        "stack_name": "OpusMagus-DistributionStack",
        "description": "CloudFront distribution and CDN configuration",
    },
    "security_stack": {
        "stack_name": "OpusMagus-SecurityStack",
        "description": "Security resources including WAF and SSL certificates",
    },
    "dns_stack": {
        "stack_name": "OpusMagus-DNSStack",
        "description": "Route53 DNS configuration and records",
    },
}
