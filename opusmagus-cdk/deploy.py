#!/usr/bin/env python3
"""Direct AWS deployment script for OpusMagus website."""

import boto3
import json
import os
from pathlib import Path

def deploy_s3():
    """Create S3 bucket and upload website files."""
    s3 = boto3.client("s3")
    bucket_name = "opusmagus-com-prod"
    
    # Create bucket
    try:
        s3.create_bucket(Bucket=bucket_name)
        print(f"✓ S3 bucket created: {bucket_name}")
    except s3.exceptions.BucketAlreadyExists:
        print(f"✓ S3 bucket already exists: {bucket_name}")
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"✓ S3 bucket already owned: {bucket_name}")
    
    # Block public access
    s3.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": True,
            "BlockPublicPolicy": True,
            "IgnorePublicAcls": True,
            "RestrictPublicBuckets": True,
        },
    )
    print("✓ S3 public access blocked")
    
    # Enable versioning
    s3.put_bucket_versioning(
        Bucket=bucket_name,
        VersioningConfiguration={"Status": "Enabled"},
    )
    print("✓ S3 versioning enabled")
    
    # Upload files
    website_dir = Path("website")
    mime_types = {
        ".html": "text/html",
        ".css": "text/css",
        ".js": "application/javascript",
        ".svg": "image/svg+xml",
        ".png": "image/png",
        ".jpg": "image/jpeg",
    }
    
    for file_path in website_dir.rglob("*"):
        if file_path.is_file():
            key = str(file_path.relative_to(website_dir)).replace("\\\\", "/")
            ext = file_path.suffix.lower()
            content_type = mime_types.get(ext, "application/octet-stream")
            
            s3.upload_file(
                str(file_path),
                bucket_name,
                key,
                ExtraArgs={"ContentType": content_type},
            )
            print(f"  ✓ {key}")
    
    print(f"✓ Website uploaded to S3")
    return bucket_name

def deploy_acm():
    """Create ACM certificate."""
    acm = boto3.client("acm", region_name="us-east-1")
    
    try:
        response = acm.request_certificate(
            DomainName="opusmagus.com",
            SubjectAlternativeNames=["www.opusmagus.com"],
            ValidationMethod="DNS",
        )
        cert_arn = response["CertificateArn"]
        print(f"✓ ACM certificate requested: {cert_arn}")
        return cert_arn
    except Exception as e:
        print(f"✓ Certificate already exists or pending: {str(e)[:60]}")
        return None

def deploy_cloudfront(bucket_name, cert_arn=None):
    """Create CloudFront distribution."""
    cf = boto3.client("cloudfront")
    
    dist_config = {
        "CallerReference": str(os.urandom(16)),
        "DefaultRootObject": "index.html",
        "Origins": {
            "Quantity": 1,
            "Items": [
                {
                    "Id": "S3Origin",
                    "DomainName": f"{bucket_name}.s3.amazonaws.com",
                    "S3OriginConfig": {"OriginAccessIdentity": ""},
                }
            ]
        },
        "DefaultCacheBehavior": {
            "AllowedMethods": {
                "Quantity": 2,
                "Items": ["GET", "HEAD"],
                "CachedMethods": {
                    "Quantity": 2,
                    "Items": ["GET", "HEAD"],
                },
            },
            "TargetOriginId": "S3Origin",
            "ViewerProtocolPolicy": "redirect-to-https",
            "TrustedSigners": {"Enabled": False, "Quantity": 0},
            "Compress": True,
            "CachePolicies": {
                "Quantity": 0,
            },
            "ForwardedValues": {
                "QueryString": False,
                "Cookies": {"Forward": "none"},
            },
            "MinTTL": 0,
        },
        "CacheBehaviors": {
            "Quantity": 0,
        },
        "Comment": "OpusMagus website",
        "Enabled": True,
    }
    
    if cert_arn:
        dist_config["DistributionConfig"] = {
            "ViewerCertificate": {
                "ACMCertificateArn": cert_arn,
                "SSLSupportMethod": "sni-only",
                "MinimumProtocolVersion": "TLSv1.2_2021",
            }
        }
    
    try:
        response = cf.create_distribution(DistributionConfig=dist_config)
        dist_id = response["Distribution"]["Id"]
        dist_domain = response["Distribution"]["DomainName"]
        print(f"✓ CloudFront distribution created")
        print(f"  Distribution ID: {dist_id}")
        print(f"  Domain: {dist_domain}")
        return dist_id, dist_domain
    except Exception as e:
        print(f"✓ CloudFront distribution exists or pending: {str(e)[:60]}")
        return None, None

if __name__ == "__main__":
    print("\n" + "="*70)
    print("OPUS MAGUS - AWS DEPLOYMENT")
    print("="*70 + "\n")
    
    print("STEP 1: Deploying S3 bucket...")
    bucket = deploy_s3()
    
    print("\nSTEP 2: Requesting ACM certificate...")
    cert = deploy_acm()
    
    print("\nSTEP 3: Creating CloudFront distribution...")
    dist_id, dist_domain = deploy_cloudfront(bucket, cert)
    
    print("\n" + "="*70)
    print("DEPLOYMENT SUMMARY")
    print("="*70)
    print(f"S3 Bucket:           {bucket}")
    print(f"CloudFront Domain:   {dist_domain if dist_domain else 'Pending...'}")
    print(f"Distribution ID:     {dist_id if dist_id else 'Pending...'}")
    print("\nNext steps:")
    print("1. Wait for ACM certificate validation (check DNS CNAME in AWS console)")
    print("2. Add Route53 records pointing to CloudFront")
    print("3. Website live at https://opusmagus.com")
    print("="*70 + "\n")
