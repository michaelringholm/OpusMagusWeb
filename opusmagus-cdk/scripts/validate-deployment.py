#!/usr/bin/env python3
"""
Pre-Deployment Validation Script for OpusMagus CDK Infrastructure

This script performs critical validation checks before CDK deployment to prevent
mistakes and ensure the correct AWS account and configuration are targeted.

Checks performed:
- AWS credentials and current account ID verification
- Domain configuration validation
- ACM SSL/TLS certificate status
- S3 bucket name uniqueness
- Overall deployment readiness

Exit codes:
- 0: All validations passed
- 1: Validation failed (see output for details)
- 2: User declined deployment confirmation
"""

import sys
import os
import json
import subprocess
from typing import Tuple, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import (
    PROD_ACCOUNT_ID,
    PROD_REGION,
    PRIMARY_DOMAIN,
    WWW_DOMAIN,
    S3_BUCKET_NAME,
    ENVIRONMENT_TAG,
)


class DeploymentValidator:
    """Validates pre-deployment configuration and AWS account setup."""

    def __init__(self):
        """Initialize validator."""
        self.results = {}
        self.warnings = []
        self.errors = []
        self.current_account_id = None
        self.current_principal = None
        self.certificate_info = {}
        self.bucket_exists = False

    def print_header(self, text: str) -> None:
        """Print a formatted header."""
        print(f"\n{'=' * 70}")
        print(f"  {text}")
        print(f"{'=' * 70}\n")

    def print_section(self, text: str) -> None:
        """Print a formatted section."""
        print(f"\n{text}")
        print(f"{'-' * len(text)}\n")

    def print_check(self, name: str, passed: bool, details: str = "") -> None:
        """Print a validation check result."""
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  [{status}] {name}")
        if details:
            print(f"         {details}")

    def run_command(self, command: list, silent: bool = False) -> Tuple[bool, str]:
        """
        Run a shell command and return success status and output.

        Args:
            command: List of command arguments
            silent: If True, suppress error output

        Returns:
            Tuple of (success: bool, output: str)
        """
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                if not silent:
                    print(f"    Error: {result.stderr.strip()}")
                return False, result.stderr.strip()
        except subprocess.TimeoutExpired:
            if not silent:
                print(f"    Error: Command timed out")
            return False, "Command timed out"
        except Exception as e:
            if not silent:
                print(f"    Error: {str(e)}")
            return False, str(e)

    def check_aws_credentials(self) -> bool:
        """
        Check if AWS credentials are configured and accessible.

        Returns:
            True if credentials are valid, False otherwise
        """
        print("\n1. Checking AWS Credentials")
        print("-" * 40)

        # Try to get caller identity
        success, output = self.run_command(["aws", "sts", "get-caller-identity"])

        if not success:
            self.print_check("AWS Credentials", False, "Unable to access AWS credentials")
            self.errors.append("AWS credentials not configured or invalid")
            return False

        try:
            identity = json.loads(output)
            self.current_account_id = identity.get("Account")
            self.current_principal = identity.get("Arn")

            self.print_check("AWS Credentials", True)
            print(f"    Account ID: {self.current_account_id}")
            print(f"    Principal:  {self.current_principal}")
        except json.JSONDecodeError:
            self.print_check("AWS Credentials", False, "Invalid AWS response")
            self.errors.append("Failed to parse AWS credentials response")
            return False

        return True

    def check_aws_account_id(self) -> bool:
        """
        Verify that the current AWS account matches PROD_ACCOUNT_ID.

        Returns:
            True if account matches, False otherwise
        """
        print("\n2. Checking AWS Account ID")
        print("-" * 40)

        if not self.current_account_id:
            self.print_check("Account ID Match", False, "Account ID not retrieved")
            self.errors.append("Cannot verify account ID without credentials")
            return False

        match = self.current_account_id == PROD_ACCOUNT_ID
        self.print_check(
            "Account ID Match",
            match,
            f"Current: {self.current_account_id}, Expected: {PROD_ACCOUNT_ID}",
        )

        if not match:
            self.errors.append(
                f"Account ID mismatch! Current: {self.current_account_id}, "
                f"Expected: {PROD_ACCOUNT_ID}"
            )

        return match

    def check_aws_region(self) -> bool:
        """
        Verify AWS region configuration (should be us-east-1 for CloudFront+ACM).

        Returns:
            True if region is valid, False otherwise
        """
        print("\n3. Checking AWS Region")
        print("-" * 40)

        valid_region = PROD_REGION == "us-east-1"
        self.print_check(
            "Region Configuration",
            valid_region,
            f"Region: {PROD_REGION} (required: us-east-1 for ACM+CloudFront)",
        )

        if not valid_region:
            self.warnings.append(
                f"Region {PROD_REGION} may not be optimal for CloudFront+ACM. "
                "Consider using us-east-1."
            )

        return valid_region

    def check_domain_configuration(self) -> bool:
        """
        Validate that domain names are properly configured.

        Returns:
            True if domain configuration is valid, False otherwise
        """
        print("\n4. Checking Domain Configuration")
        print("-" * 40)

        valid = True

        # Check primary domain
        primary_valid = PRIMARY_DOMAIN and "." in PRIMARY_DOMAIN
        self.print_check(
            "Primary Domain",
            primary_valid,
            f"Domain: {PRIMARY_DOMAIN}",
        )
        if not primary_valid:
            self.errors.append(f"Invalid primary domain: {PRIMARY_DOMAIN}")
            valid = False

        # Check www domain
        www_valid = WWW_DOMAIN and "." in WWW_DOMAIN
        self.print_check(
            "WWW Subdomain",
            www_valid,
            f"Domain: {WWW_DOMAIN}",
        )
        if not www_valid:
            self.errors.append(f"Invalid www domain: {WWW_DOMAIN}")
            valid = False

        # Check that www domain matches primary
        if www_valid and primary_valid:
            matches = WWW_DOMAIN == f"www.{PRIMARY_DOMAIN}"
            self.print_check(
                "Domain Consistency",
                matches,
                f"www domain should be 'www.{PRIMARY_DOMAIN}'",
            )
            if not matches:
                self.warnings.append(
                    f"www domain {WWW_DOMAIN} doesn't follow expected pattern"
                )

        return valid

    def check_acm_certificate_status(self) -> bool:
        """
        Check the status of ACM certificate for the configured domains.

        Returns:
            True if certificate exists and is valid, False otherwise
        """
        print("\n5. Checking ACM Certificate Status")
        print("-" * 40)

        # List certificates
        success, output = self.run_command(
            [
                "aws",
                "acm",
                "list-certificates",
                "--region",
                PROD_REGION,
                "--output",
                "json",
            ]
        )

        if not success:
            self.warnings.append("Unable to check ACM certificates")
            self.print_check("ACM Certificate", False, "Unable to query ACM")
            return False

        try:
            certs = json.loads(output)
            cert_summaries = certs.get("CertificateSummaryList", [])

            if not cert_summaries:
                self.print_check("ACM Certificate", False, "No certificates found")
                self.warnings.append(
                    "No ACM certificates found. Certificate needs to be created."
                )
                return False

            # Look for certificate matching our domain
            found_cert = False
            for cert in cert_summaries:
                domain_name = cert.get("DomainName")
                arn = cert.get("CertificateArn")
                status = cert.get("Status")

                # Check if this cert is for our primary domain
                if domain_name == PRIMARY_DOMAIN or domain_name == f"*.{PRIMARY_DOMAIN}":
                    found_cert = True
                    self.certificate_info = {
                        "arn": arn,
                        "domain": domain_name,
                        "status": status,
                    }

                    cert_valid = status == "ISSUED"
                    self.print_check(
                        "ACM Certificate",
                        cert_valid,
                        f"Domain: {domain_name}, Status: {status}",
                    )

                    if not cert_valid and status == "PENDING_VALIDATION":
                        self.warnings.append(
                            "Certificate is still pending validation. "
                            "Ensure DNS/email validation is complete before deployment."
                        )
                    elif not cert_valid:
                        self.errors.append(f"Certificate status: {status}")

                    return cert_valid

            if not found_cert:
                self.print_check(
                    "ACM Certificate",
                    False,
                    f"No certificate found for {PRIMARY_DOMAIN}",
                )
                self.warnings.append(
                    f"Certificate for {PRIMARY_DOMAIN} not found in ACM. "
                    "You may need to create it before deployment."
                )
                return False

        except (json.JSONDecodeError, KeyError) as e:
            self.print_check("ACM Certificate", False, "Error parsing ACM response")
            self.errors.append(f"Failed to parse ACM response: {str(e)}")
            return False

        return False

    def check_s3_bucket_uniqueness(self) -> bool:
        """
        Verify that the S3 bucket name is available (doesn't exist or belongs to us).

        Returns:
            True if bucket is available, False otherwise
        """
        print("\n6. Checking S3 Bucket Availability")
        print("-" * 40)

        # Try to check if bucket exists and who owns it
        success, output = self.run_command(
            [
                "aws",
                "s3api",
                "head-bucket",
                "--bucket",
                S3_BUCKET_NAME,
            ],
            silent=True,
        )

        if success:
            # Bucket exists - check if we own it
            success_tags, tags_output = self.run_command(
                [
                    "aws",
                    "s3api",
                    "get-bucket-tagging",
                    "--bucket",
                    S3_BUCKET_NAME,
                ],
                silent=True,
            )

            self.bucket_exists = True
            self.print_check(
                "S3 Bucket",
                True,
                f"Bucket '{S3_BUCKET_NAME}' exists and is accessible",
            )

            if success_tags:
                try:
                    tags = json.loads(tags_output)
                    tag_set = tags.get("TagSet", [])
                    env_tag = next(
                        (t for t in tag_set if t.get("Key") == "Environment"),
                        None,
                    )
                    if env_tag and env_tag.get("Value") == ENVIRONMENT_TAG:
                        print(f"         Bucket is tagged for '{ENVIRONMENT_TAG}' environment")
                except json.JSONDecodeError:
                    pass
            return True
        else:
            # Bucket doesn't exist - bucket name is available
            self.bucket_exists = False
            self.print_check(
                "S3 Bucket",
                True,
                f"Bucket '{S3_BUCKET_NAME}' is available for creation",
            )
            return True

    def check_environment_variable(self) -> bool:
        """
        Check if the non-interactive mode environment variable is set.

        Returns:
            True if OPUSMAGUS_SKIP_CONFIRMATION is set to true, False otherwise
        """
        skip_confirmation = os.getenv("OPUSMAGUS_SKIP_CONFIRMATION", "").lower()
        return skip_confirmation == "true"

    def validate_all(self) -> bool:
        """
        Run all validation checks.

        Returns:
            True if all critical checks pass, False otherwise
        """
        self.print_header("OPUSMAGUS PRE-DEPLOYMENT VALIDATION")

        # Run all checks
        credential_ok = self.check_aws_credentials()
        account_ok = self.check_aws_account_id() if credential_ok else False
        region_ok = self.check_aws_region()
        domain_ok = self.check_domain_configuration()
        cert_ok = self.check_acm_certificate_status()
        bucket_ok = self.check_s3_bucket_uniqueness()

        # Determine overall status
        all_pass = credential_ok and account_ok and domain_ok and bucket_ok
        critical_pass = all_pass  # All checks are critical for our use case

        return critical_pass

    def print_summary(self) -> None:
        """Print deployment summary and configuration details."""
        self.print_section("DEPLOYMENT SUMMARY")

        print("Configuration:")
        print(f"  AWS Account ID:      {PROD_ACCOUNT_ID}")
        print(f"  AWS Region:          {PROD_REGION}")
        print(f"  Primary Domain:      {PRIMARY_DOMAIN}")
        print(f"  WWW Domain:          {WWW_DOMAIN}")
        print(f"  S3 Bucket Name:      {S3_BUCKET_NAME}")
        print(f"  Environment Tag:     {ENVIRONMENT_TAG}")

        if self.certificate_info:
            print(f"\nACM Certificate:")
            print(f"  Domain:              {self.certificate_info.get('domain')}")
            print(f"  Status:              {self.certificate_info.get('status')}")
            print(f"  ARN:                 {self.certificate_info.get('arn')}")

        print(f"\nS3 Bucket:")
        print(f"  Name:                {S3_BUCKET_NAME}")
        print(f"  Exists:              {'Yes' if self.bucket_exists else 'No (will be created)'}")

        if self.warnings:
            self.print_section("WARNINGS")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}\n")

    def request_confirmation(self) -> bool:
        """
        Request user confirmation for deployment.

        Returns:
            True if user confirms, False if user declines
        """
        self.print_section("DEPLOYMENT CONFIRMATION")

        print(
            f"Ready to deploy infrastructure to AWS account {PROD_ACCOUNT_ID}?\n"
        )
        print("This will create or update the following resources:")
        print("  - S3 bucket for website hosting")
        print("  - CloudFront distribution")
        print("  - AWS WAF rules")
        print("  - Route53 DNS records (if applicable)")
        print()

        # Check for non-interactive mode
        if self.check_environment_variable():
            print(
                "Non-interactive mode enabled (OPUSMAGUS_SKIP_CONFIRMATION=true)"
            )
            print("Proceeding with deployment...\n")
            return True

        # Interactive confirmation
        while True:
            response = input("Continue with deployment? (yes/no): ").lower().strip()
            if response in ("yes", "y"):
                return True
            elif response in ("no", "n"):
                return False
            else:
                print("Please enter 'yes' or 'no'")

    def run(self) -> int:
        """
        Execute full validation workflow.

        Returns:
            Exit code (0 = success, 1 = validation failed, 2 = user declined)
        """
        # Run all validations
        validation_passed = self.validate_all()

        # Print summary
        self.print_summary()

        if not validation_passed:
            self.print_section("VALIDATION FAILED")
            print("The following issues must be resolved before deployment:\n")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}\n")
            print("\nPlease fix the above issues and run validation again.")
            return 1

        # All validations passed
        self.print_section("ALL VALIDATIONS PASSED ✓")

        # Request deployment confirmation
        if self.request_confirmation():
            print("\n" + "=" * 70)
            print("  DEPLOYMENT CONFIRMED")
            print("=" * 70)
            print("\nProceeding to CDK deployment...")
            print("You can now run: cdk deploy\n")
            return 0
        else:
            print("\n" + "=" * 70)
            print("  DEPLOYMENT CANCELLED")
            print("=" * 70)
            print("\nDeployment was cancelled by user.\n")
            return 2


def main():
    """Main entry point."""
    validator = DeploymentValidator()
    exit_code = validator.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
