@echo off
REM Build script for Windows executable

REM Store current directory and change to script directory
set "ORIGINAL_DIR=%CD%"
cd /d "%~dp0"

echo ====================================================
echo Building OBS VirtualCam Tray Controller for Windows
echo ====================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    cd /d "%ORIGINAL_DIR%"
    pause
    exit /b 1
)

REM Create build environment
echo Creating build environment...
if exist "build_env\" (
    echo Removing existing build environment...
    rmdir /s /q build_env
)

python -m venv build_env
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    cd /d "%ORIGINAL_DIR%"
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call build_env\Scripts\activate.bat

REM Install build requirements
echo Installing build requirements...
pip install --upgrade pip
pip install -r ..\config\requirements-build.txt
if errorlevel 1 (
    echo Error: Failed to install requirements
    cd /d "%ORIGINAL_DIR%"
    pause
    exit /b 1
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "..\build\" rmdir /s /q ..\build
if exist "..\dist\" rmdir /s /q ..\dist

REM Build executable
echo Building executable...
cd ..
pyinstaller config\obs-tray.spec --clean
cd scripts
if errorlevel 1 (
    echo Error: Build failed
    cd /d "%ORIGINAL_DIR%"
    pause
    exit /b 1
)

REM Create distribution folder
echo Creating distribution package...
if not exist "..\dist\windows\" mkdir ..\dist\windows

REM Copy executable
copy ..\dist\OBS-VirtualCam-Tray-Controller.exe ..\dist\windows\

REM Create README for distribution
echo OBS VirtualCam Tray Controller for Windows > ..\dist\windows\README.txt
echo. >> ..\dist\windows\README.txt
echo Simply run OBS-VirtualCam-Tray-Controller.exe to start the application. >> ..\dist\windows\README.txt
echo The application will appear in your system tray. >> ..\dist\windows\README.txt
echo. >> ..\dist\windows\README.txt
echo Requirements: >> ..\dist\windows\README.txt
echo - OBS Studio 28+ with WebSocket enabled >> ..\dist\windows\README.txt
echo - Windows 10 or later >> ..\dist\windows\README.txt

REM Deactivate virtual environment
deactivate

echo ====================================================
echo Build complete!
echo Executable location: ..\dist\windows\OBS-VirtualCam-Tray-Controller.exe
echo ====================================================

REM Return to original directory
cd /d "%ORIGINAL_DIR%"

pause