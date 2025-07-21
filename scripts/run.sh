#!/bin/bash
# OBS VirtualCam Tray Controller - Unix/Linux Run Script
# This script runs the OBS tray application on Unix/Linux/macOS

# Store current directory and change to script directory
ORIGINAL_DIR=$(pwd)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting OBS VirtualCam Tray Controller..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "Error: Python is not installed or not in PATH"
        echo "Please install Python 3.8+ from your package manager or https://python.org"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Using Python: $($PYTHON_CMD --version)"

# Check if src directory exists
if [ ! -d "../src" ]; then
    echo "Error: src/ directory not found"
    echo "Please make sure the project structure is intact"
    exit 1
fi

# Check if dependencies are installed
echo "Checking dependencies..."
if ! $PYTHON_CMD -c "import simpleobsws, pystray, PIL" 2>/dev/null; then
    echo "Installing dependencies..."
    echo "Note: We've updated to simpleobsws for OBS WebSocket 5.x support"
    $PYTHON_CMD -m pip install -r ../requirements.txt --user
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies"
        echo "Please run: $PYTHON_CMD -m pip install -r ../requirements.txt --user"
        echo "If you get externally-managed-environment error, use --user flag or create a virtual environment"
        exit 1
    fi
fi

# Run the application
echo "Starting application..."
cd ..
$PYTHON_CMD main.py

# Return to original directory
cd "$ORIGINAL_DIR" 