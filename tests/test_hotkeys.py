#!/usr/bin/env python3
"""
Test script for global hotkey functionality.
This tests the hotkey system without requiring OBS to be running.
"""

import sys
import logging
from pathlib import Path
import time

# Add parent directory to path to access src module
sys.path.append(str(Path(__file__).parent.parent))

from src.settings_manager import SettingsManager
from src.hotkey_handler import HotkeyHandler


def main():
    """Test the hotkey functionality."""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    logger.info("🎹 OBS Tray Controller - Hotkey Test")
    logger.info("=" * 50)
    
    # Load settings
    settings_manager = SettingsManager()
    settings = settings_manager.settings
    
    logger.info(f"Hotkeys enabled: {settings.enable_hotkeys}")
    logger.info(f"Webcam ON hotkey: {settings.hotkey_webcam_on}")
    logger.info(f"Webcam OFF hotkey: {settings.hotkey_webcam_off}")
    logger.info("-" * 50)
    
    if not settings.enable_hotkeys:
        logger.warning("⚠️  Hotkeys are disabled in settings!")
        logger.info("Enable them in the settings dialog to test.")
        return
    
    # Create test callbacks
    def on_webcam_on():
        logger.info("🟢 HOTKEY ACTIVATED: Webcam ON")
        print("💡 This would turn your webcam ON in the real app!")
    
    def on_webcam_off():
        logger.info("🔴 HOTKEY ACTIVATED: Webcam OFF")
        print("💡 This would turn your webcam OFF in the real app!")
    
    # Create hotkey handler
    hotkey_handler = HotkeyHandler(settings_manager)
    hotkey_handler.set_callbacks(
        webcam_on_callback=on_webcam_on,
        webcam_off_callback=on_webcam_off
    )
    
    # Start the hotkey handler
    logger.info("🚀 Starting hotkey listener...")
    if hotkey_handler.start():
        logger.info("✅ Hotkey listener started successfully!")
        logger.info("")
        logger.info("🎯 TEST YOUR HOTKEYS NOW:")
        logger.info(f"   Press {settings.hotkey_webcam_on} to trigger 'Webcam ON'")
        logger.info(f"   Press {settings.hotkey_webcam_off} to trigger 'Webcam OFF'")
        logger.info("")
        logger.info("Press Ctrl+C to stop the test")
        logger.info("-" * 50)
        
        try:
            # Keep the program running
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Test stopped by user")
            
    else:
        logger.error("❌ Failed to start hotkey listener!")
        return
    
    # Clean up
    hotkey_handler.stop()
    logger.info("🏁 Hotkey test completed")


if __name__ == "__main__":
    main() 