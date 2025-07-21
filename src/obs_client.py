"""
OBS WebSocket client module.
Handles connection to OBS Studio and source visibility operations.
"""

import logging
import asyncio
import threading
from typing import Optional, Callable
import obsws_python as obs

from .settings_manager import SettingsManager


class OBSClient:
    """OBS WebSocket client for managing source visibility."""
    
    def __init__(self, settings_manager: SettingsManager, status_callback: Optional[Callable[[bool], None]] = None):
        """
        Initialize OBS client.
        
        Args:
            settings_manager: Settings manager instance
            status_callback: Callback function called when connection status changes
        """
        self.settings_manager = settings_manager
        self.ws: Optional[obs.ReqClient] = None
        self.connected = False
        self.status_callback = status_callback
        self.reconnect_thread: Optional[threading.Thread] = None
        self.should_reconnect = False
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def connect(self) -> bool:
        """
        Connect to OBS WebSocket.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            settings = self.settings_manager.settings
            self.logger.info(f"Connecting to OBS at {settings.obs_host}:{settings.obs_port}")
            
            # Create WebSocket client using obsws-python
            self.ws = obs.ReqClient(
                host=settings.obs_host,
                port=settings.obs_port,
                password=settings.obs_password,
                timeout=5
            )
            
            # Test connection with a simple request
            version_info = self.ws.get_version()
            self.logger.info(f"Connected to OBS WebSocket v{version_info.obs_web_socket_version}")
            
            self.connected = True
            
            if self.status_callback:
                self.status_callback(True)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to OBS: {e}")
            self.connected = False
            if self.status_callback:
                self.status_callback(False)
            return False
    
    def disconnect(self) -> bool:
        """
        Disconnect from OBS WebSocket.
        
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        try:
            self.should_reconnect = False
            
            if self.ws:
                # obsws-python handles disconnection automatically when object is destroyed
                self.ws = None
                self.logger.info("Disconnected from OBS WebSocket")
            
            self.connected = False
            
            if self.status_callback:
                self.status_callback(False)
                
            return True
        except Exception as e:
            self.logger.error(f"Error disconnecting from OBS: {e}")
            return False

    def is_source_visible(self) -> Optional[bool]:
        """
        Check if the configured source is visible in the scene.
        
        Returns:
            Optional[bool]: True if visible, False if hidden, None if error/not found
        """
        if not self.connected or not self.ws:
            self.logger.warning("Not connected to OBS")
            return None
            
        try:
            settings = self.settings_manager.settings
            
            # Get scene item ID for the source
            scene_items = self.ws.get_scene_item_list(settings.scene_name)
            
            source_item_id = None
            for item in scene_items.scene_items:
                if item['sourceName'] == settings.source_name:
                    source_item_id = item['sceneItemId']
                    break
            
            if source_item_id is None:
                self.logger.error(f"Source '{settings.source_name}' not found in scene '{settings.scene_name}'")
                return None
            
            # Check if the scene item is enabled (visible)
            item_enabled = self.ws.get_scene_item_enabled(settings.scene_name, source_item_id)
            return item_enabled.scene_item_enabled
            
        except Exception as e:
            self.logger.error(f"Error checking source visibility: {e}")
            return None

    def toggle_source_visibility(self) -> bool:
        """
        Toggle the visibility of the configured source.
        
        Returns:
            bool: True if toggle successful, False otherwise
        """
        if not self.connected or not self.ws:
            self.logger.warning("Not connected to OBS")
            return False
            
        try:
            settings = self.settings_manager.settings
            
            # Get current visibility state
            current_state = self.is_source_visible()
            if current_state is None:
                return False
            
            # Get scene item ID
            scene_items = self.ws.get_scene_item_list(settings.scene_name)
            
            source_item_id = None
            for item in scene_items.scene_items:
                if item['sourceName'] == settings.source_name:
                    source_item_id = item['sceneItemId']
                    break
            
            if source_item_id is None:
                self.logger.error(f"Source '{settings.source_name}' not found in scene '{settings.scene_name}'")
                return False
            
            # Toggle visibility
            new_state = not current_state
            self.ws.set_scene_item_enabled(settings.scene_name, source_item_id, new_state)
            
            action = "shown" if new_state else "hidden"
            self.logger.info(f"Source '{settings.source_name}' {action}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error toggling source visibility: {e}")
            return False

    def set_source_visibility(self, visible: bool) -> bool:
        """
        Set the visibility of the configured source.
        
        Args:
            visible: True to show the source, False to hide it
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connected or not self.ws:
            self.logger.warning("Not connected to OBS")
            return False
            
        try:
            settings = self.settings_manager.settings
            
            # Get scene item ID
            scene_items = self.ws.get_scene_item_list(settings.scene_name)
            
            source_item_id = None
            for item in scene_items.scene_items:
                if item['sourceName'] == settings.source_name:
                    source_item_id = item['sceneItemId']
                    break
            
            if source_item_id is None:
                self.logger.error(f"Source '{settings.source_name}' not found in scene '{settings.scene_name}'")
                return False
            
            # Set visibility
            self.ws.set_scene_item_enabled(settings.scene_name, source_item_id, visible)
            
            action = "shown" if visible else "hidden"
            self.logger.info(f"Source '{settings.source_name}' {action}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting source visibility: {e}")
            return False
    
    def start_reconnect_loop(self):
        """Start the reconnection loop in a background thread."""
        if self.reconnect_thread and self.reconnect_thread.is_alive():
            return
            
        self.should_reconnect = True
        self.reconnect_thread = threading.Thread(target=self._reconnect_loop, daemon=True)
        self.reconnect_thread.start()
    
    def stop_reconnect_loop(self):
        """Stop the reconnection loop."""
        self.should_reconnect = False
    
    def _reconnect_loop(self):
        """Background reconnection loop."""
        settings = self.settings_manager.settings
        
        while self.should_reconnect:
            if not self.connected:
                self.logger.info("Attempting to reconnect to OBS...")
                if self.connect():
                    continue
                    
            # Wait before next reconnect attempt
            delay_steps = int(settings.reconnect_delay * 10)
            for _ in range(delay_steps):  # Check should_reconnect every 0.1s
                if not self.should_reconnect:
                    return
                threading.Event().wait(0.1)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect() 