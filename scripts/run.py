#!/usr/bin/env python3
"""
Convenient run script for OBS VirtualCam Tray Controller.
Ensures proper path setup and runs the main application.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import and run main application
from main import main

if __name__ == "__main__":
    main() 