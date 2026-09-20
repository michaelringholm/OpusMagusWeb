# OpusMagus CDK Infrastructure

AWS CDK infrastructure-as-code for the OpusMagus project. This project manages cloud infrastructure including S3 storage, CloudFront distribution, security resources, and Route53 DNS.

## Prerequisites

- Python 3.10 or later
- Node.js 14.x or later (required for AWS CDK CLI)
- AWS CDK CLI (installed via npm)
- AWS credentials configured locally

## Quick Start

### 1. Install AWS CDK CLI

```bash
npm install -g aws-cdk
cdk --version
```

### 2. Set Up Local Environment

#### On Linux/macOS:
```bash
chmod +x setup.sh
./setup.sh
```

#### On Windows:
```cmd
setup.bat
```

### 3. Review Configuration

Edit `.env` with your AWS account details:
```bash
# Copy from .env.example if .env doesn't exist
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use your preferred editor
```

### 4. Verify Setup

```bash
# Activate virtual environment (if not already active)
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# List available stacks
cdk list

# Synthesize CloudFormation template (dry run)
cdk synth
```

## Project Structure

```
opusmagus-cdk/
├── app.py                 # CDK application entry point
├── requirements.txt       # Python dependencies
├── .env.example          # Configuration template
├── .gitignore            # Git ignore rules
├── setup.sh              # Linux/macOS setup script
├── setup.bat             # Windows setup script
├── config/
│   ├── __init__.py       # Config module initialization
│   └── config.py         # Configuration constants
└── stacks/
    ├── __init__.py       # Stacks module initialization
    ├── storage_stack.py  # S3 and storage resources
    ├── distribution_stack.py  # CloudFront distribution
    ├── security_stack.py # WAF and security resources
    └── dns_stack.py      # Route53 DNS records
```

## CDK Stack Details

### StorageStack
Manages S3 buckets for website content:
- Primary S3 bucket with versioning
- Encryption at rest
- Public access blocking
- Lifecycle policies

### SecurityStack
Manages security resources:
- AWS WAF rules
- SSL/TLS certificates (ACM)
- Security group configurations
- Access logging

### DistributionStack
Manages CloudFront distribution:
- Origin configuration
- Caching behaviors
- Security headers
- HTTPS enforcement

### DNSStack
Manages Route53 DNS:
- Hosted zone configuration
- A records for domains
- CloudFront aliases
- Health checks

## Configuration

Configuration is managed through environment variables in `.env`:

- `PROD_ACCOUNT_ID`: AWS Account ID for production deployment
- `PROD_REGION`: AWS region (default: us-east-1)
- `PRIMARY_DOMAIN`: Primary domain name (default: opusmagus.com)
- `WWW_DOMAIN`: www subdomain (default: www.opusmagus.com)
- `S3_BUCKET_NAME`: S3 bucket name (default: opusmagus-com-prod)
- `ENVIRONMENT_TAG`: Environment tag for resources (default: prod)

## Common Commands

```bash
# List all stacks
cdk list

# Synthesize CloudFormation template
cdk synth

# View differences between local and deployed resources
cdk diff

# Deploy to AWS
cdk deploy

# Deploy specific stack
cdk deploy OpusMagus-StorageStack

# Destroy resources
cdk destroy
```

## Development

### Adding a New Stack

1. Create a new file in `stacks/` (e.g., `stacks/my_stack.py`)
2. Import and instantiate in `app.py`
3. Add to stacks module `__init__.py`

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov
```

## Deployment Safety

The PROD account deployment includes safeguards:
- Requires explicit confirmation before deployment
- Uses dedicated PROD_ACCOUNT_ID environment variable
- All resources tagged with environment and project information
- Stack dependencies prevent premature deletions

## Troubleshooting

### Virtual Environment Issues
```bash
# If virtual environment is corrupted, recreate it
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### AWS Credentials
```bash
# Configure AWS credentials
aws configure

# Verify credentials
aws sts get-caller-identity
```

### CDK Issues
```bash
# Clear CDK cache
rm -rf cdk.out
rm *.context.json

# Reinstall dependencies
pip install --upgrade aws-cdk-lib constructs
```

## References

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/v2/guide/)
- [AWS CDK Python Reference](https://docs.aws.amazon.com/cdk/api/v2/python/)
- [AWS CloudFormation](https://docs.aws.amazon.com/cloudformation/)
