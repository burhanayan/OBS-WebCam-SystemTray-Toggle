#!/bin/bash
# Build script for Linux executable

# Store current directory and change to script directory
ORIGINAL_DIR=$(pwd)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "===================================================="
echo "Building OBS VirtualCam Tray Controller for Linux"
echo "===================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
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
mkdir -p ../dist/linux

# Copy executable
cp ../dist/obs-virtualcam-tray-controller ../../dist/linux/

# Make it executable
chmod +x ../dist/linux/obs-virtualcam-tray-controller

# Create desktop entry
cat > ../dist/linux/obs-virtualcam-tray-controller.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=OBS VirtualCam Tray Controller
Comment=Control OBS virtualcam from system tray
Exec=/opt/obs-virtualcam-tray-controller/obs-virtualcam-tray-controller
Icon=/opt/obs-virtualcam-tray-controller/icon.png
Terminal=false
Categories=Utility;AudioVideo;
StartupNotify=false
EOF

# Create install script
cat > ../dist/linux/install.sh << 'EOF'
#!/bin/bash
echo "Installing OBS VirtualCam Tray Controller..."

# Create installation directory
sudo mkdir -p /opt/obs-virtualcam-tray-controller

# Copy files
sudo cp obs-virtualcam-tray-controller /opt/obs-virtualcam-tray-controller/
sudo chmod +x /opt/obs-virtualcam-tray-controller/obs-virtualcam-tray-controller

# Create symlink
sudo ln -sf /opt/obs-virtualcam-tray-controller/obs-virtualcam-tray-controller /usr/local/bin/obs-virtualcam-tray-controller

# Install desktop entry
sudo cp obs-virtualcam-tray-controller.desktop /usr/share/applications/

echo "Installation complete!"
echo "You can run the application by typing 'obs-virtualcam-tray-controller' in terminal"
echo "Or find it in your applications menu as 'OBS VirtualCam Tray Controller'"
EOF

chmod +x ../dist/linux/install.sh

# Create README
cat > ../dist/linux/README.txt << EOF
OBS VirtualCam Tray Controller for Linux

Installation:
1. Run: ./install.sh (requires sudo)
2. The application will be installed to /opt/obs-virtualcam-tray-controller/

Running:
- From terminal: obs-virtualcam-tray-controller
- From applications menu: Look for "OBS VirtualCam Tray Controller"

Requirements:
- OBS Studio 28+ with WebSocket enabled
- Linux with system tray support (GNOME, KDE, XFCE, etc.)

Uninstall:
sudo rm -rf /opt/obs-virtualcam-tray-controller
sudo rm /usr/local/bin/obs-virtualcam-tray-controller
sudo rm /usr/share/applications/obs-virtualcam-tray-controller.desktop
EOF

# Deactivate virtual environment
deactivate

echo "===================================================="
echo "Build complete!"
echo "Distribution location: ../dist/linux/"
echo "===================================================="

# Return to original directory
cd "$ORIGINAL_DIR"