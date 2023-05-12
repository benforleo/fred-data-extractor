# FRED Data Extractor

![Build Status](https://img.shields.io/github/actions/workflow/status/benforleo/fred-data-extractor/tests.yaml?branch=main)
[![Coverage Status](https://coveralls.io/repos/github/benforleo/fred-data-extractor/badge.svg?branch=main&kill_cache=1)](https://coveralls.io/github/benforleo/fred-data-extractor?branch=main)

Greetings! 

The fred data extractor is a work in progress and is under active development. 

This super simple batch processing application will pull data from the Federal Reserve of St. Louis FRED API
on a daily schedule and store the data in an S3 bucket. 

The purpose is simply to demonstrate that I know how to use AWS and can deploy AWS infrastructure through code, 
specifically, the AWS CDK.


Please consider hiring me :)

Obviously, this is only the E in a potential ETL pipeline. A real ETL pipeline would have:
- Separate, decoupled transform and load processes (likely in separate code bases)
- Idempotent tasks, whenever possible
- Error handling, retry logic, and failure notifications

![architecture](img/fred-data-extractor.png)


# To build and deploy locally:

1. Install NodeJS version 16.20.0
2. Install the AWS CDK

```bash
npm install -g aws-cdk@2.73
```
4. Clone this repository
5. Create a Python 3.9 virtual environment at the project root and activate it

```bash
python3 -m venv venv
source venv/bin/activate 
```
6. Install python requirements

```bash
python3 -m pip install -r requirements.txt 
```
7. Optional: Install tox to run tests

```bash
python3 -m pip install tox
```
8. Optional: Run tests

```bash
tox
```
9. Be sure appropriate AWS profile and IAM credentials are set at $HOME/.aws/credentials
11. Set the appropriate environment variables

```bash
export AWS_ACCOUNT_ID="12345678"
export FRED_BUCKET_NAME="my-fred-bucket-name"
```
11. Deploy

```bash
cdk deploy
```
