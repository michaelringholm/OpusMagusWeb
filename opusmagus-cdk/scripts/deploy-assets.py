#!/usr/bin/env python3
"""Deploy website assets to S3 bucket."""

import os
import sys
import boto3
from pathlib import Path

def deploy_assets(website_dir="website", bucket_name="opusmagus-com-prod"):
    """Deploy static assets to S3."""
    s3 = boto3.client("s3")
    
    # MIME types mapping
    mime_types = {
        ".html": "text/html",
        ".css": "text/css",
        ".js": "application/javascript",
        ".json": "application/json",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
        ".gif": "image/gif",
        ".ico": "image/x-icon",
    }
    
    # Cache control headers
    cache_control = {
        ".html": "max-age=0, must-revalidate",
        ".css": "max-age=31536000, immutable",
        ".js": "max-age=31536000, immutable",
        ".png": "max-age=86400",
        ".jpg": "max-age=86400",
        ".jpeg": "max-age=86400",
        ".webp": "max-age=86400",
        ".svg": "max-age=86400",
        ".gif": "max-age=86400",
        ".ico": "max-age=604800",
    }
    
    # Walk directory and upload files
    for root, dirs, files in os.walk(website_dir):
        for file in files:
            file_path = Path(root) / file
            relative_path = file_path.relative_to(website_dir)
            s3_key = str(relative_path).replace("\\\\", "/")
            
            ext = file_path.suffix.lower()
            mime_type = mime_types.get(ext, "application/octet-stream")
            cc = cache_control.get(ext, "max-age=3600")
            
            print(f"Uploading {s3_key}...")
            s3.upload_file(
                str(file_path),
                bucket_name,
                s3_key,
                ExtraArgs={
                    "ContentType": mime_type,
                    "CacheControl": cc,
                },
            )
    
    print(f"✓ Assets deployed to s3://{bucket_name}/")

if __name__ == "__main__":
    deploy_assets()
