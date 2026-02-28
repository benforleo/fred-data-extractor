#!/usr/bin/env bash

set -e

# Parse command line arguments
AWS_ACCOUNT_ID=""
FRED_BUCKET_NAME=""
CDK_COMMAND="deploy"
REQUIRE_APPROVAL="never"

usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -a, --account-id ID       AWS Account ID (or set AWS_ACCOUNT_ID env var)"
    echo "  -b, --bucket-name NAME    FRED bucket name (or set FRED_BUCKET_NAME env var)"
    echo "  -c, --command COMMAND     CDK command to run (default: deploy)"
    echo "  -r, --require-approval    Require approval for deployment (default: never)"
    echo "  -d, --destroy             Shortcut for 'cdk destroy'"
    echo "  -s, --synth               Shortcut for 'cdk synth'"
    echo "  -h, --help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -a 123456789012 -b my-fred-bucket"
    echo "  $0 --account-id 123456789012 --bucket-name my-fred-bucket"
    echo "  $0 -d  # Destroy the stack"
    echo "  AWS_ACCOUNT_ID=123456789012 FRED_BUCKET_NAME=my-bucket $0"
    exit 1
}

# While count of arguments > 0
while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--account-id)
            AWS_ACCOUNT_ID="$2"
            shift 2
            ;;
        -b|--bucket-name)
            FRED_BUCKET_NAME="$2"
            shift 2
            ;;
        -c|--command)
            CDK_COMMAND="$2"
            shift 2
            ;;
        -r|--require-approval)
            REQUIRE_APPROVAL="$2"
            shift 2
            ;;
        -d|--destroy)
            CDK_COMMAND="destroy"
            shift
            ;;
        -s|--synth)
            CDK_COMMAND="synth"
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# If working directory is scripts/, move up to project root
if [ "$(basename "$PWD")" = "scripts" ]; then
    cd ..
    echo "Working directory changed to project root: $PWD"
fi

echo "========================================="
echo "FRED Data Extractor - CDK Deployment"
echo "========================================="

# Check if Python 3.14 is installed
if ! command -v python3.14 &> /dev/null; then
    echo "Error: Python 3.14 is required but not installed."
    echo "Please install Python 3.14 to continue."
    exit 1
fi

echo "✓ Python 3.14 found: $(python3.14 --version)"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is required but not installed."
    echo "Please install Node.js >= 22.14.0 to continue."
    exit 1
fi

NODE_VERSION=$(node --version | sed 's/v//')
REQUIRED_NODE_VERSION="22.14.0"

# Simple version comparison (works for semantic versioning)
version_compare() {
    if [[ "$(printf '%s\n' "$1" "$2" | sort -V | head -n1)" == "$2" ]]; then
        return 0  # version >= required
    else
        return 1  # version < required
    fi
}

if ! version_compare "$NODE_VERSION" "$REQUIRED_NODE_VERSION"; then
    echo "Error: Node.js version $NODE_VERSION is installed, but >= $REQUIRED_NODE_VERSION is required."
    echo "Please upgrade Node.js to continue."
    exit 1
fi

echo "✓ Node.js found: v$NODE_VERSION"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is required but not installed."
    echo "Docker is needed to build CDK asset bundles."
    echo "Please install Docker Desktop (macOS/Windows) or Docker Engine (Linux)."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "Error: Docker is installed but the Docker daemon is not running."
    echo "Please start Docker Desktop (macOS/Windows) or the Docker service (Linux)."
    exit 1
fi

DOCKER_VERSION=$(docker --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1)
echo "✓ Docker found: v$DOCKER_VERSION (daemon running)"

# Check if AWS CDK is installed
if ! command -v cdk &> /dev/null; then
    echo "Error: AWS CDK is not installed."
    echo "Installing AWS CDK..."
    npm install -g aws-cdk@latest
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install AWS CDK."
        exit 1
    fi
fi

CDK_VERSION=$(cdk --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n1)
echo "✓ AWS CDK found: $CDK_VERSION"

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "Error: AWS credentials are not configured or invalid."
    echo "Please configure AWS credentials using 'aws configure' or environment variables."
    exit 1
fi

AWS_CALLER_IDENTITY=$(aws sts get-caller-identity)
echo "✓ AWS credentials configured"
echo "  Account: $(echo "$AWS_CALLER_IDENTITY" | grep -oP '"Account": "\K[^"]*')"
echo "  User/Role: $(echo "$AWS_CALLER_IDENTITY" | grep -oP '"Arn": "\K[^"]*')"

# Get AWS_ACCOUNT_ID from environment if not provided as argument
if [ -z "$AWS_ACCOUNT_ID" ]; then
    AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-}"
fi

# Get FRED_BUCKET_NAME from environment if not provided as argument
if [ -z "$FRED_BUCKET_NAME" ]; then
    FRED_BUCKET_NAME="${FRED_BUCKET_NAME:-}"
fi

# Validate required parameters (only for deploy command)
if [ "$CDK_COMMAND" = "deploy" ]; then
    if [ -z "$FRED_BUCKET_NAME" ]; then
        echo "Error: FRED_BUCKET_NAME is required for deployment."
        echo "Provide it via --bucket-name argument or FRED_BUCKET_NAME environment variable."
        usage
    fi
    echo "✓ Bucket name: $FRED_BUCKET_NAME"
fi

# Check if virtual environment directory exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment with Python 3.14..."
    python3.14 -m venv .venv
    echo "✓ Virtual environment created."
fi

# Activate the virtual environment if not already activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
    echo "✓ Virtual environment activated."
else
    echo "✓ Virtual environment already activated."
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "✓ Python dependencies installed"

# Export environment variables for CDK
export FRED_BUCKET_NAME
if [ -n "$AWS_ACCOUNT_ID" ]; then
    export AWS_ACCOUNT_ID
fi

echo ""
echo "========================================="
echo "Running CDK Command: $CDK_COMMAND"
echo "========================================="

# Run CDK command
case $CDK_COMMAND in
    deploy)
        cdk deploy --require-approval "$REQUIRE_APPROVAL" --tags app=fred-data-extractor
        ;;
    destroy)
        cdk destroy --force
        ;;
    synth)
        cdk synth
        ;;
    diff)
        cdk diff
        ;;
    *)
        cdk "$CDK_COMMAND"
        ;;
esac

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "✓ CDK command completed successfully!"
    echo "========================================="
else
    echo ""
    echo "========================================="
    echo "✗ CDK command failed!"
    echo "========================================="
    exit 1
fi

