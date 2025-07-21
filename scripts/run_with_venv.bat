@echo off
REM OBS VirtualCam Tray Controller - Virtual Environment Run Script (Windows)
REM This script handles virtual environment setup and runs the application

echo OBS VirtualCam Tray Controller - Virtual Environment Setup
echo ===========================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Using Python: 
python --version

REM Check if src directory exists
if not exist "src\" (
    echo Error: src/ directory not found
    echo Please make sure you're running this from the project directory
    pause
    exit /b 1
)

REM Check if virtual environment exists with correct structure
if exist "venv\Scripts\activate.bat" (
    echo Virtual environment found.
) else (
    echo Creating virtual environment...
    if exist "venv\" (
        echo Removing incompatible virtual environment...
        rmdir /s /q venv
    )
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Checking dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo Error: Failed to install dependencies in virtual environment
    pause
    exit /b 1
)

REM Run the application
echo Starting OBS VirtualCam Tray Controller...
python main.py

pause 