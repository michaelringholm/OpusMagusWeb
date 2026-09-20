# Project Structure Overview

## Directory Layout

```
opusmagus-cdk/
├── app.py                      # CDK application entry point
├── requirements.txt            # Python package dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore configuration
├── setup.sh                   # Linux/macOS setup script
├── setup.bat                  # Windows setup script
├── README.md                  # Project documentation
├── STRUCTURE.md              # This file
│
├── config/                    # Configuration module
│   ├── __init__.py           # Module initialization
│   └── config.py             # Configuration constants
│       ├── PROD_ACCOUNT_ID
│       ├── PROD_REGION
│       ├── PRIMARY_DOMAIN
│       ├── WWW_DOMAIN
│       ├── S3_BUCKET_NAME
│       ├── ENVIRONMENT_TAG
│       └── STACKS_CONFIG
│
└── stacks/                    # CDK Stack implementations
    ├── __init__.py           # Module initialization & exports
    ├── storage_stack.py      # StorageStack (S3 buckets)
    ├── distribution_stack.py # DistributionStack (CloudFront)
    ├── security_stack.py     # SecurityStack (WAF, SSL)
    └── dns_stack.py          # DNSStack (Route53)
```

## File Descriptions

### Core Application Files

- **app.py**: Entry point for CDK. Initializes the App, creates all stacks, adds dependencies and tags.
- **requirements.txt**: Python dependencies including aws-cdk-lib, constructs, and python-dotenv.
- **.env.example**: Template for environment configuration. Copy to .env and customize.
- **.gitignore**: Excludes .venv, __pycache__, .env, cdk.out, and other development artifacts.

### Setup Scripts

- **setup.sh**: Bash script for Linux/macOS environment setup
  - Creates Python virtual environment
  - Upgrades pip/setuptools
  - Installs dependencies
  - Creates .env from .env.example

- **setup.bat**: Batch script for Windows environment setup
  - Same functionality as setup.sh for Windows systems

### Configuration Module (`config/`)

- **config.py**: Centralized configuration using environment variables
  - Loads .env file using python-dotenv
  - Provides constants for all stacks
  - Stack configurations in STACKS_CONFIG dictionary

- **__init__.py**: Exports configuration values for easy importing

### Stack Implementations (`stacks/`)

Each stack is a separate class extending `aws_cdk.Stack`:

- **storage_stack.py**: StorageStack
  - S3 bucket creation and configuration
  - Versioning, encryption, lifecycle policies
  
- **security_stack.py**: SecurityStack
  - AWS WAF rules
  - SSL/TLS certificates
  - Security groups and access logging

- **distribution_stack.py**: DistributionStack
  - CloudFront distribution
  - Origin configuration
  - Caching and security headers

- **dns_stack.py**: DNSStack
  - Route53 hosted zone
  - DNS records and aliases
  - Health checks

- **__init__.py**: Exports all stack classes

## Configuration Values

From `config/config.py`:

```python
PROD_ACCOUNT_ID = "742197632521"        # Production AWS account
PROD_REGION = "us-east-1"               # Primary region
PRIMARY_DOMAIN = "opusmagus.com"        # Main domain
WWW_DOMAIN = "www.opusmagus.com"        # www subdomain
S3_BUCKET_NAME = "opusmagus-com-prod"   # S3 bucket name
ENVIRONMENT_TAG = "prod"                 # Environment tag
```

## Dependencies

- **aws-cdk-lib>=2.0.0**: AWS CDK core library
- **constructs>=10.0.0**: CDK constructs base classes
- **python-dotenv>=0.20.0**: Environment variable loading

## Virtual Environment (.venv)

Created by setup scripts:
- Python 3.10+ standard library
- Isolated from system Python
- Contains installed packages from requirements.txt

## Stack Dependencies

Defined in app.py:
```
StorageStack (no dependencies)
    ↓
SecurityStack (no dependencies)
    ↓
DistributionStack (depends on StorageStack)
    ↓
DNSStack (depends on DistributionStack)
```

This ensures resources are created in the correct order and CloudFormation respects dependencies.

## Deployment to PROD Account

Safeguards in place:
1. **Account ID**: PROD_ACCOUNT_ID set in .env
2. **Region Lock**: us-east-1 hardcoded for consistency
3. **Tagging**: All resources tagged with Environment and Project
4. **Dependencies**: Stack ordering prevents premature deletions
5. **Manual Confirmation**: CDK requires explicit approval for deployment

## Usage Examples

```bash
# Activate environment
source .venv/bin/activate

# List stacks
cdk list

# Preview changes (dry run)
cdk synth
cdk diff

# Deploy
cdk deploy

# Destroy
cdk destroy
```

## Next Steps

1. Run setup script to install dependencies
2. Update .env with actual AWS account ID and settings
3. Implement stack logic in each stack file
4. Test with `cdk synth` and `cdk diff`
5. Deploy with `cdk deploy`
