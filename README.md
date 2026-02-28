# FRED Data Extractor

![Build Status](https://img.shields.io/github/actions/workflow/status/benforleo/fred-data-extractor/tests.yaml?branch=main)
[![Coverage Status](https://coveralls.io/repos/github/benforleo/fred-data-extractor/badge.svg?branch=main&kill_cache=1)](https://coveralls.io/github/benforleo/fred-data-extractor?branch=main)

Greetings! 

The fred data extractor is a work in progress and is under active development. 

This simple batch processing application will pull data from the Federal Reserve of St. Louis FRED API
on a daily schedule and store the data in an S3 bucket. 

The purpose is simply to demonstrate that I know how to use AWS and can deploy AWS infrastructure through code, 
specifically, the AWS CDK.


Please consider hiring me :slightly_smiling_face:

Obviously, this is only the E in a potential ETL pipeline. A real ETL pipeline would have:
- Separate, decoupled load and transform processes
- Idempotent tasks, whenever possible
- Error handling, retry logic, and failure notifications

![architecture](img/fred-data-extractor.png)


# To build and deploy locally:

## Prerequisites

1. **Python 3.14** - Required for running the application
2. **Node.js >= 22.14.0** - Required for AWS CDK
3. **Docker** - Required for building CDK asset bundles
4. **AWS CDK** - Will be installed automatically by the deploy script if not present
5. **AWS Credentials** - Configure at `$HOME/.aws/credentials` or via environment variables

## Quick Start with the Fred Extractor

The easiest way to deploy is using the provided deploy script:

```bash
# Option 1: Pass credentials as arguments
./scripts/fred.sh -a 123456789012 -b my-fred-bucket-name

# Option 2: Use environment variables
export AWS_ACCOUNT_ID="123456789012"
export FRED_BUCKET_NAME="my-fred-bucket-name"
./scripts/fred.sh

# View all options
./scripts/fred.sh --help
```

The fred script will automatically:
- Verify Python 3.14 is installed
- Verify Node.js >= 22.14.0 is installed
- Install AWS CDK if not present
- Create and activate a virtual environment
- Install Python dependencies
- Deploy the CDK stack

### Other Deploy Script Commands

```bash
# Synthesize CloudFormation template
./scripts/fred.sh -s

# View stack differences
./scripts/fred.sh -c diff -b my-fred-bucket-name

# Destroy the stack
./scripts/fred.sh -d
```
