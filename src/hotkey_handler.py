"""
Global hotkey handler for OBS VirtualCam Tray Controller.
Manages keyboard shortcuts for webcam control.
"""

import logging
import threading
from typing import Optional, Callable, Dict, Any
from pynput import keyboard
from pynput.keyboard import Key, GlobalHotKeys

from .settings_manager import SettingsManager


class HotkeyHandler:
    """Handles global keyboard shortcuts for webcam control."""
    
    def __init__(self, settings_manager: SettingsManager):
        """
        Initialize hotkey handler.
        
        Args:
            settings_manager: Settings manager instance
        """
        self.settings_manager = settings_manager
        self.logger = logging.getLogger(__name__)
        
        # Callbacks for hotkey actions
        self.webcam_on_callback: Optional[Callable[[], None]] = None
        self.webcam_off_callback: Optional[Callable[[], None]] = None
        
        # Global hotkeys listener
        self.global_hotkeys: Optional[GlobalHotKeys] = None
        self.is_running = False
        
    def set_callbacks(self, webcam_on_callback: Optional[Callable[[], None]] = None,
                     webcam_off_callback: Optional[Callable[[], None]] = None):
        """
        Set callback functions for hotkey actions.
        
        Args:
            webcam_on_callback: Function to call when webcam on hotkey is pressed
            webcam_off_callback: Function to call when webcam off hotkey is pressed
        """
        if webcam_on_callback:
            self.webcam_on_callback = webcam_on_callback
        if webcam_off_callback:
            self.webcam_off_callback = webcam_off_callback
    
    def _parse_hotkey_string(self, hotkey_str: str) -> str:
        """
        Parse hotkey string from settings format to pynput format.
        
        Args:
            hotkey_str: Hotkey string like "<ctrl>+<alt>+1"
            
        Returns:
            str: Parsed hotkey string for pynput
        """
        # Convert from settings format to pynput format
        # Settings format: "<ctrl>+<alt>+1"
        # pynput format: "<ctrl>+<alt>+1"
        return hotkey_str.replace("<ctrl>", "<cmd>") if "darwin" in str(self.settings_manager.config_dir) else hotkey_str
    
    def _create_hotkeys_dict(self) -> Dict[str, Callable[[], None]]:
        """
        Create a dictionary of hotkey strings to callbacks.
        
        Returns:
            Dict mapping hotkey strings to callback functions
        """
        hotkeys_dict = {}
        settings = self.settings_manager.settings
        
        if not settings.enable_hotkeys:
            return hotkeys_dict
        
        # Add webcam on hotkey
        if settings.hotkey_webcam_on:
            parsed_on = self._parse_hotkey_string(settings.hotkey_webcam_on)
            hotkeys_dict[parsed_on] = self._on_webcam_on_hotkey
            self.logger.info(f"Webcam ON hotkey: {parsed_on}")
        
        # Add webcam off hotkey
        if settings.hotkey_webcam_off:
            parsed_off = self._parse_hotkey_string(settings.hotkey_webcam_off)
            hotkeys_dict[parsed_off] = self._on_webcam_off_hotkey
            self.logger.info(f"Webcam OFF hotkey: {parsed_off}")
        
        return hotkeys_dict
    
    def _on_webcam_on_hotkey(self):
        """Handle webcam on hotkey press."""
        try:
            self.logger.info("Webcam ON hotkey pressed")
            if self.webcam_on_callback:
                self.webcam_on_callback()
        except Exception as e:
            self.logger.error(f"Error handling webcam on hotkey: {e}")
    
    def _on_webcam_off_hotkey(self):
        """Handle webcam off hotkey press."""
        try:
            self.logger.info("Webcam OFF hotkey pressed")
            if self.webcam_off_callback:
                self.webcam_off_callback()
        except Exception as e:
            self.logger.error(f"Error handling webcam off hotkey: {e}")
    
    
    def start(self) -> bool:
        """
        Start the global hotkey listener.
        
        Returns:
            bool: True if started successfully
        """
        if self.is_running:
            self.logger.warning("Hotkey handler is already running")
            return True
        
        try:
            # Create hotkeys dictionary
            hotkeys_dict = self._create_hotkeys_dict()
            
            if not hotkeys_dict:
                self.logger.info("No hotkeys configured, skipping hotkey listener")
                return True
            
            # Create and start GlobalHotKeys listener
            self.global_hotkeys = GlobalHotKeys(hotkeys_dict)
            self.global_hotkeys.start()
            
            self.is_running = True
            self.logger.info(f"Hotkey handler started successfully with {len(hotkeys_dict)} hotkeys")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start hotkey handler: {e}")
            return False
    
    def stop(self):
        """Stop the global hotkey listener."""
        if not self.is_running:
            return
        
        try:
            self.is_running = False
            
            # Stop the global hotkeys listener
            if self.global_hotkeys:
                self.global_hotkeys.stop()
                self.global_hotkeys = None
            
            self.logger.info("Hotkey handler stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping hotkey handler: {e}")
    
    def reload_hotkeys(self):
        """Reload hotkeys from current settings."""
        if self.is_running:
            self.logger.info("Reloading hotkeys...")
            self.stop()
            self.start()
    
    def is_hotkey_valid(self, hotkey_str: str) -> bool:
        """
        Check if a hotkey string is valid.
        
        Args:
            hotkey_str: Hotkey string to validate
            
        Returns:
            bool: True if valid
        """
        try:
            # Try to create a temporary GlobalHotKeys to validate
            temp_hotkeys = GlobalHotKeys({self._parse_hotkey_string(hotkey_str): lambda: None})
            return True
        except Exception:
            return False 