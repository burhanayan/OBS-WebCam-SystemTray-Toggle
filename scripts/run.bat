@echo off
REM OBS VirtualCam Tray Controller - Windows Run Script
REM This script runs the OBS tray application on Windows

REM Store current directory and change to script directory
set "ORIGINAL_DIR=%CD%"
cd /d "%~dp0"

echo Starting OBS VirtualCam Tray Controller...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if src directory exists
if not exist "..\src\" (
    echo Error: src/ directory not found
    echo Please make sure the project structure is intact
    pause
    exit /b 1
)

REM Install/update dependencies
echo Checking dependencies...
echo Note: We've updated to simpleobsws for OBS WebSocket 5.x support
python -m pip install -r ..\requirements.txt --user >nul 2>&1
if errorlevel 1 (
    echo Warning: Could not automatically install dependencies
    echo Please run: python -m pip install -r ..\requirements.txt --user
    echo If you get permission errors, try the --user flag above
    pause
)

REM Run the application
cd ..
python main.py

REM Return to original directory
cd /d "%ORIGINAL_DIR%"

pause 