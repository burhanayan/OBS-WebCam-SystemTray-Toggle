#!/bin/bash
# Build script for macOS executable

# Store current directory and change to script directory
ORIGINAL_DIR=$(pwd)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "===================================================="
echo "Building OBS VirtualCam Tray Controller for macOS"
echo "===================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Install it using: brew install python3"
    exit 1
fi

echo "Using Python:"
python3 --version

# Create build environment
echo "Creating build environment..."
if [ -d "build_env" ]; then
    echo "Removing existing build environment..."
    rm -rf build_env
fi

python3 -m venv build_env
if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source build_env/bin/activate

# Install build requirements
echo "Installing build requirements..."
pip install --upgrade pip
pip install -r ../config/requirements-build.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install requirements"
    exit 1
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf ../build ../dist

# Build executable
echo "Building executable..."
cd ..
pyinstaller config/obs-tray.spec --clean
cd scripts
if [ $? -ne 0 ]; then
    echo "Error: Build failed"
    exit 1
fi

# Create distribution folder
echo "Creating distribution package..."
mkdir -p ../dist/macos

# Copy app bundle
cp -r "dist/OBS VirtualCam Tray Controller.app" ../dist/macos/

# Create DMG installer (if create-dmg is available)
if command -v create-dmg &> /dev/null; then
    echo "Creating DMG installer..."
    create-dmg \
        --volname "OBS VirtualCam Tray Controller" \
        --window-pos 200 120 \
        --window-size 600 400 \
        --icon-size 100 \
        --icon "OBS VirtualCam Tray Controller.app" 175 120 \
        --hide-extension "OBS VirtualCam Tray Controller.app" \
        --app-drop-link 425 120 \
        "../dist/macos/OBS-VirtualCam-Tray-Controller.dmg" \
        "../dist/macos/OBS VirtualCam Tray Controller.app"
else
    echo "Note: Install create-dmg for automatic DMG creation:"
    echo "brew install create-dmg"
fi

# Create README
cat > ../dist/macos/README.txt << EOF
OBS VirtualCam Tray Controller for macOS

Installation:
1. Drag "OBS VirtualCam Tray Controller.app" to your Applications folder
2. On first run, you may need to right-click and select "Open" due to Gatekeeper

Running:
- Launch from Applications folder
- The app will appear in your menu bar (system tray)

Requirements:
- OBS Studio 28+ with WebSocket enabled
- macOS 10.14 or later
- May require accessibility permissions for global hotkeys

Permissions:
If hotkeys don't work, grant accessibility permissions:
System Preferences > Security & Privacy > Privacy > Accessibility

Uninstall:
Simply drag the app from Applications to Trash
EOF

# Deactivate virtual environment
deactivate

echo "===================================================="
echo "Build complete!"
echo "Application location: ../dist/macos/OBS VirtualCam Tray Controller.app"
if [ -f "../dist/macos/OBS-VirtualCam-Tray-Controller.dmg" ]; then
    echo "DMG installer: ../dist/macos/OBS-VirtualCam-Tray-Controller.dmg"
fi
echo "===================================================="

# Return to original directory
cd "$ORIGINAL_DIR"