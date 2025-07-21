#!/usr/bin/env python3
"""
Simple build script for creating executable on current platform
"""

import sys
import subprocess
import platform
import shutil
import os
from pathlib import Path

def main():
    print("=" * 60)
    print(f"Building OBS VirtualCam Tray Controller for {platform.system()}")
    print("=" * 60)
    
    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Install build requirements
    print("\nInstalling build requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "config/requirements-build.txt"])
    
    # Clean previous builds
    print("\nCleaning previous builds...")
    for dir_name in ["build", "dist"]:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
    
    # Build executable
    print("\nBuilding executable...")
    subprocess.check_call([sys.executable, "-m", "PyInstaller", "config/obs-tray.spec", "--clean"])
    
    # Report results
    print("\n" + "=" * 60)
    print("Build complete!")
    
    if platform.system() == "Windows":
        exe_path = Path("dist/OBS-VirtualCam-Tray-Controller.exe")
        if exe_path.exists():
            print(f"Executable: {exe_path.absolute()}")
            print(f"Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
    elif platform.system() == "Darwin":
        app_path = Path("dist/OBS VirtualCam Tray Controller.app")
        if app_path.exists():
            print(f"Application: {app_path.absolute()}")
    else:  # Linux
        exe_path = Path("dist/obs-virtualcam-tray-controller")
        if exe_path.exists():
            print(f"Executable: {exe_path.absolute()}")
            print(f"Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
    
    print("=" * 60)

if __name__ == "__main__":
    main()