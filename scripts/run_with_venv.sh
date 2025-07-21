#!/bin/bash
# OBS VirtualCam Tray Controller - Virtual Environment Run Script
# This script handles virtual environment setup and runs the application

echo "OBS VirtualCam Tray Controller - Virtual Environment Setup"
echo "==========================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed or not in PATH"
    echo "Please install Python 3.8+ from your package manager"
    exit 1
fi

echo "Using Python: $(python3 --version)"

# Check if src directory exists
if [ ! -d "src" ]; then
    echo "Error: src/ directory not found"
    echo "Please make sure you're running this from the project directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        echo "Make sure you have python3-venv installed: sudo apt install python3-venv"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Checking dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies in virtual environment"
    exit 1
fi

# Run the application
echo "Starting OBS Tray Controller..."
python main.py

# Deactivate virtual environment when done
deactivate 