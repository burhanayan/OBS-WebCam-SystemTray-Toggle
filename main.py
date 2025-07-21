#!/usr/bin/env python3
"""
OBS VirtualCam Tray Controller - Main Application

Entry point for the OBS WebSocket tray controller application.
Coordinates OBS client connection and system tray interface with persistent settings.
"""

import sys
import signal
import logging
import threading
import time
from typing import Optional

from src.settings_manager import SettingsManager
from src.obs_client import OBSClient
from src.tray_handler import TrayHandler


class OBSTrayApp:
    """Main application class that coordinates OBS client and tray handler."""
    
    def __init__(self):
        """Initialize the application."""
        self.settings_manager: Optional[SettingsManager] = None
        self.obs_client: Optional[OBSClient] = None
        self.tray_handler: Optional[TrayHandler] = None
        self.update_thread: Optional[threading.Thread] = None
        self.running = False
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup application logging."""
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                # Uncomment to also log to file:
                # logging.FileHandler('obs_tray.log')
            ]
        )
        
        # Reduce noise from some libraries
        logging.getLogger('PIL').setLevel(logging.WARNING)
        logging.getLogger('pystray').setLevel(logging.WARNING)
        
        return logging.getLogger(__name__)
        
    def _on_obs_connection_change(self, connected: bool):
        """
        Callback for OBS connection status changes.
        
        Args:
            connected: True if connected to OBS, False otherwise
        """
        if self.tray_handler:
            self.tray_handler.update_connection_state(connected)
            
            if connected:
                self.logger.info("Connected to OBS - checking initial source state")
                # Check initial source state
                initial_state = self.obs_client.is_source_visible()
                self.tray_handler.update_webcam_state(initial_state)
            else:
                self.logger.warning("Disconnected from OBS")
                self.tray_handler.update_webcam_state(None)
                
    def _update_loop(self):
        """Background thread that periodically updates the tray icon state."""
        self.logger.info("Started update loop thread")
        
        while self.running:
            try:
                if (self.obs_client and self.obs_client.connected and 
                    self.tray_handler and self.tray_handler.current_connection_state):
                    
                    # Check current source state periodically
                    current_state = self.obs_client.is_source_visible()
                    self.tray_handler.update_webcam_state(current_state)
                    
            except Exception as e:
                self.logger.error(f"Error in update loop: {e}")
                
            # Sleep for a bit before next update (every 5 seconds)
            for _ in range(50):  # Check every 5 seconds (50 * 0.1s)
                if not self.running:
                    break
                time.sleep(0.1)
                
        self.logger.info("Update loop thread stopped")
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.shutdown()
        
    def start(self):
        """Start the application."""
        try:
            # Initialize settings manager
            self.settings_manager = SettingsManager()
            settings = self.settings_manager.settings
            
            self.logger.info(f"Starting OBS VirtualCam Tray Controller")
            self.logger.info(f"Settings loaded from: {self.settings_manager.config_file}")
            self.logger.info(f"Auto-connect: {settings.auto_connect}")
            
            # Setup signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            # Initialize OBS client
            self.obs_client = OBSClient(
                settings_manager=self.settings_manager,
                status_callback=self._on_obs_connection_change
            )
            
            # Initialize tray handler
            self.tray_handler = TrayHandler(
                obs_client=self.obs_client,
                settings_manager=self.settings_manager
            )
            
            # Start the application components
            self.running = True
            
            # Auto-connect to OBS if enabled in settings
            if settings.auto_connect:
                self.logger.info("Auto-connect enabled, attempting to connect to OBS...")
                if self.obs_client.connect():
                    self.logger.info("Auto-connected to OBS successfully")
                    # Start reconnect loop for auto-connection
                    self.obs_client.start_reconnect_loop()
                else:
                    self.logger.warning("Auto-connect to OBS failed, will remain disconnected")
            else:
                self.logger.info("Auto-connect disabled, waiting for manual connection")
            
            # Start update loop thread
            self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self.update_thread.start()
            
            # Start tray icon (this blocks until exit)
            self.logger.info("Starting system tray interface")
            self.tray_handler.start()
            
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        except Exception as e:
            self.logger.error(f"Application error: {e}")
            raise
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Shutdown the application gracefully."""
        if not self.running:
            return
            
        self.logger.info("Shutting down application...")
        self.running = False
        
        # Stop tray handler
        if self.tray_handler:
            self.tray_handler.stop()
            
        # Disconnect OBS client and stop reconnection
        if self.obs_client:
            self.obs_client.stop_reconnect_loop()
            self.obs_client.disconnect()
            
        # Wait for update thread to finish
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=2.0)
            
        self.logger.info("Application shutdown complete")


def main():
    """Main entry point."""
    try:
        app = OBSTrayApp()
        app.start()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 