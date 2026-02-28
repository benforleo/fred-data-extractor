# Scripts Documentation

## fred.sh

Automated deployment script for the FRED Data Extractor CDK application.

### Prerequisites

The script automatically checks for:
- Python 3.14
- Node.js >= 22.14.0
- Docker (and Docker daemon running)
- AWS CDK (installs if missing)
- Valid AWS credentials

### Usage

```bash
./scripts/fred.sh [options]
```

### Options

| Option | Description | Example |
|--------|-------------|---------|
| `-a, --account-id ID` | AWS Account ID (can use env var) | `-a 123456789012` |
| `-b, --bucket-name NAME` | FRED bucket name (can use env var) | `-b my-bucket` |
| `-c, --command COMMAND` | CDK command to run | `-c diff` |
| `-r, --require-approval` | Require approval mode | `-r broadening` |
| `-d, --destroy` | Shortcut for destroy | `-d` |
| `-s, --synth` | Shortcut for synth | `-s` |
| `-h, --help` | Show help message | `-h` |

### Examples

**Deploy with arguments:**
```bash
./scripts/fred.sh -a 123456789012 -b my-fred-bucket
```

**Deploy with environment variables:**
```bash
export AWS_ACCOUNT_ID="123456789012"
export FRED_BUCKET_NAME="my-fred-bucket"
./scripts/fred.sh
```

**Synthesize CloudFormation template:**
```bash
./scripts/fred.sh -s
```

**View differences:**
```bash
./scripts/fred.sh -c diff -b my-fred-bucket
```

**Destroy stack:**
```bash
./scripts/fred.sh -d
```

**Deploy with manual approval:**
```bash
./scripts/fred.sh -a 123456789012 -b my-bucket -r broadening
```

### What the Script Does

1. **Validates working directory** - Moves to project root if in scripts/
2. **Checks Python 3.14** - Exits if not installed
3. **Checks Node.js version** - Verifies >= 22.14.0
4. **Checks Docker** - Verifies installed and daemon is running
5. **Checks/Installs AWS CDK** - Installs latest if missing
6. **Validates AWS credentials** - Confirms access via STS
7. **Creates virtual environment** - If .venv doesn't exist
8. **Installs dependencies** - Pip installs from requirements.txt
9. **Runs CDK command** - Executes deploy/destroy/synth/etc.

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FRED_BUCKET_NAME` | Yes (for deploy) | Name of S3 bucket for FRED data |
| `AWS_ACCOUNT_ID` | No | AWS account ID (optional) |
| `AWS_PROFILE` | No | AWS profile to use |
| `AWS_REGION` | No | AWS region (defaults to credentials) |

---

## run-tests.sh

Automated test runner using tox and pyproject.toml configuration.

### Usage

```bash
./scripts/fred-tests.sh [tox-options]
```

### Examples

**Run all tests:**
```bash
./scripts/fred-tests.sh
```

**Run specific environment:**
```bash
./scripts/fred-tests.sh -e py314
```

**List environments:**
```bash
./scripts/fred-tests.sh -l
```

### What the Script Does

1. Validates working directory
2. Checks Python 3.14 is installed
3. Creates/activates virtual environment
4. Validates pyproject.toml exists
5. Installs tox
6. Runs tests via tox

