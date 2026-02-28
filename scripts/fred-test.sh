#!/usr/bin/env bash

set -e

# If working directory is scripts/, move up to project root
if [ "$(basename "$PWD")" = "scripts" ]; then
    cd ..
    echo "Working directory changed to project root: $PWD"
fi

# Check if Python 3.14 is installed
if ! command -v python3.14 &> /dev/null; then
    echo "Error: Python 3.14 is required but not installed."
    echo "Please install Python 3.14 to continue."
    exit 1
fi

echo "Python 3.14 found: $(python3.14 --version)"

# Check if virtual environment directory exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment with Python 3.14..."
    python3.14 -m venv .venv
    echo "Virtual environment created."
fi

# Activate the virtual environment if not already activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
    echo "Virtual environment activated."
else
    echo "Virtual environment already activated."
fi

# Check if pyproject.toml exists
if [ ! -f "pyproject.toml" ]; then
    echo "Error: pyproject.toml not found in the project root."
    echo "Please ensure pyproject.toml exists before running tests."
    exit 1
fi

# Install tox in the virtual environment
echo "Installing tox..."
pip install --upgrade pip
pip install tox

# Run tests using tox with pyproject.toml
echo "Running tox..."
tox "$@"
