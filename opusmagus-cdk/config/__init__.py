"""Configuration module for OpusMagus CDK Infrastructure."""
from .config import (
    PROD_ACCOUNT_ID,
    PROD_REGION,
    PRIMARY_DOMAIN,
    WWW_DOMAIN,
    S3_BUCKET_NAME,
    ENVIRONMENT_TAG,
)

__all__ = [
    "PROD_ACCOUNT_ID",
    "PROD_REGION",
    "PRIMARY_DOMAIN",
    "WWW_DOMAIN",
    "S3_BUCKET_NAME",
    "ENVIRONMENT_TAG",
]
