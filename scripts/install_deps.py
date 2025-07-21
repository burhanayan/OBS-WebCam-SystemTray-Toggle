#!/usr/bin/env python3
"""
Dependency installer for OBS VirtualCam Tray Controller

This script installs the required dependencies, handling the externally managed
environment issue by using a temporary override flag.
"""

import subprocess
import sys
import os

def main():
    """Install dependencies."""
    print("🔧 Installing OBS Tray Controller Dependencies")
    print("=" * 50)
    
    print("Installing required packages...")
    print("This may show a warning about externally-managed-environment.")
    print("We're using --break-system-packages to install user packages.")
    print()
    
    # Install dependencies with system package override
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "--break-system-packages", "--user",
            "-r", "requirements.txt"
        ], check=True, capture_output=True, text=True)
        
        print("✅ Dependencies installed successfully!")
        print()
        print("Installed packages:")
        print("- obsws-python==1.7.0 (OBS WebSocket client)")
        print("- pystray==0.19.5 (System tray support)")
        print("- Pillow==10.1.0 (Image processing)")
        print("- pynput==1.7.6 (Global hotkey support)")
        print()
        print("🎉 Ready to run the application!")
        print()
        print("Next steps:")
        print("1. Make sure OBS Studio is running with WebSocket enabled")
        print("2. Test the connection: python test_connection.py")
        print("3. Run the app: python main.py")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        print()
        print("Error output:")
        print(e.stderr)
        print()
        print("Alternative installation methods:")
        print("1. Use pipx: pipx install obsws-python pystray Pillow")
        print("2. Create a virtual environment manually")
        print("3. Use the system package manager if available")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 