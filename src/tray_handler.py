"""
System tray handler module.
Manages the system tray icon, menu, and user interactions.
"""

import logging
import threading
import webbrowser
from typing import Optional, Callable
from PIL import Image, ImageDraw
import pystray

from .obs_client import OBSClient
from .settings_manager import SettingsManager
from .settings_dialog import SettingsDialog
from .hotkey_handler import HotkeyHandler


class TrayHandler:
    """Handles system tray icon and user interactions."""
    
    def __init__(self, obs_client: OBSClient, settings_manager: SettingsManager):
        """
        Initialize tray handler.
        
        Args:
            obs_client: OBS client instance
            settings_manager: Settings manager instance
        """
        self.obs_client = obs_client
        self.settings_manager = settings_manager
        self.icon: Optional[pystray.Icon] = None
        self.settings_dialog: Optional[SettingsDialog] = None
        
        # Initialize hotkey handler
        self.hotkey_handler = HotkeyHandler(settings_manager)
        self.hotkey_handler.set_callbacks(
            webcam_on_callback=self._hotkey_webcam_on,
            webcam_off_callback=self._hotkey_webcam_off
        )
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Current state tracking
        self.current_connection_state = False
        self.current_webcam_state = None  # None = unknown, True = on, False = off
        
        # Load static icons from assets
        self._load_icons()
        
        # Settings update callback
        self.settings_update_callback: Optional[Callable] = None
        
    def set_settings_update_callback(self, callback: Callable):
        """Set callback for when settings are updated."""
        self.settings_update_callback = callback
        
    def _load_icons(self):
        """
        Load static icon files from assets directory.
        Falls back to creating dynamic icons if files are not found.
        """
        import os
        from pathlib import Path
        
        # Get the directory where the script is located
        base_dir = Path(__file__).parent.parent
        assets_dir = base_dir / 'assets'
        
        try:
            # Load disconnected icon
            disconnected_path = assets_dir / 'OBS-WebCam-Tray-Logo_Disconnected.png'
            if disconnected_path.exists():
                self.disconnected_icon = Image.open(disconnected_path)
                self.logger.info(f"Loaded disconnected icon from {disconnected_path}")
            else:
                self.logger.warning(f"Disconnected icon not found at {disconnected_path}, creating default")
                self.disconnected_icon = self._create_default_icon('disconnected')
            
            # Load camera off icon
            camera_off_path = assets_dir / 'OBS-WebCam-Tray-Logo_Webcam_Turned_Off.png'
            if camera_off_path.exists():
                self.camera_off_icon = Image.open(camera_off_path)
                self.logger.info(f"Loaded camera off icon from {camera_off_path}")
            else:
                self.logger.warning(f"Camera off icon not found at {camera_off_path}, creating default")
                self.camera_off_icon = self._create_default_icon('off')
            
            # Load camera on icon
            camera_on_path = assets_dir / 'OBS-WebCam-Tray-Logo_Webcam_Turned_On.png'
            if camera_on_path.exists():
                self.camera_on_icon = Image.open(camera_on_path)
                self.logger.info(f"Loaded camera on icon from {camera_on_path}")
            else:
                self.logger.warning(f"Camera on icon not found at {camera_on_path}, creating default")
                self.camera_on_icon = self._create_default_icon('on')
                
        except Exception as e:
            self.logger.error(f"Error loading icons: {e}")
            # Fall back to creating default icons
            self.disconnected_icon = self._create_default_icon('disconnected')
            self.camera_off_icon = self._create_default_icon('off')
            self.camera_on_icon = self._create_default_icon('on')
    
    def _create_default_icon(self, state: str) -> Image.Image:
        """
        Create a simple default icon as fallback.
        
        Args:
            state: 'on', 'off', or 'disconnected'
            
        Returns:
            PIL Image for the icon
        """
        img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Simple circle with different colors for different states
        if state == 'on':
            color = '#00FF00'  # Green
        elif state == 'off':
            color = '#FF0000'  # Red
        else:  # disconnected
            color = '#888888'  # Gray
        
        # Draw a simple circle
        draw.ellipse([4, 4, 28, 28], fill=color, outline='black', width=2)
        
        # Add a simple indicator
        if state == 'disconnected':
            # Draw X for disconnected
            draw.line([10, 10, 22, 22], fill='white', width=2)
            draw.line([10, 22, 22, 10], fill='white', width=2)
        elif state == 'on':
            # Draw checkmark for on
            draw.line([10, 16, 14, 20], fill='white', width=2)
            draw.line([14, 20, 22, 12], fill='white', width=2)
        else:  # off
            # Draw dash for off
            draw.line([10, 16, 22, 16], fill='white', width=3)
        
        return img
    
    # Connection menu actions
    def _on_connect(self, icon, item):
        """Handle connect to OBS action."""
        self.logger.info("User requested connection to OBS")
        if self.obs_client.connect():
            self.current_connection_state = True
            self._update_icon()
            self._update_menus()
        else:
            self.logger.error("Failed to connect to OBS")
    
    def _on_disconnect(self, icon, item):
        """Handle disconnect from OBS action."""
        self.logger.info("User requested disconnection from OBS")
        self.obs_client.disconnect()
        self.current_connection_state = False
        self.current_webcam_state = None
        self._update_icon()
        self._update_menus()
    
    # Webcam control actions
    def _on_webcam_on(self, icon, item):
        """Handle turn webcam on action."""
        self.logger.info("User requested to turn webcam ON")
        if self.obs_client.set_source_visibility(True) is not None:
            self.current_webcam_state = True
            self._update_icon()
            self._update_menus()
    
    def _on_webcam_off(self, icon, item):
        """Handle turn webcam off action."""
        self.logger.info("User requested to turn webcam OFF")
        if self.obs_client.set_source_visibility(False) is not None:
            self.current_webcam_state = False
            self._update_icon()
            self._update_menus()
    
    def _refresh_webcam_state(self, icon, item):
        """Refresh webcam state from OBS."""
        if self.current_connection_state:
            self.current_webcam_state = self.obs_client.is_source_visible()
            self._update_icon()
            self._update_menus()
            
    # Settings menu actions
    def _on_settings(self, icon, item):
        """Handle settings menu action."""
        self.logger.info("Settings dialog requested")
        
        try:
            # Create and show settings dialog
            dialog = SettingsDialog(
                settings_manager=self.settings_manager,
                on_settings_changed=self._on_settings_changed
            )
            
            # Show dialog (this will block until closed)
            if dialog.show():
                self.logger.info("Settings were updated by user")
            else:
                self.logger.info("Settings dialog was cancelled")
                
        except Exception as e:
            self.logger.error(f"Error showing settings dialog: {e}")
            # Fallback to simple message
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error", f"Failed to open settings dialog: {e}")
            root.destroy()
    
    def _on_settings_changed(self):
        """Called when settings are changed via the dialog."""
        self.logger.info("Settings were changed, updating application")
        
        # Reload icons in case they changed
        self._load_icons()
        
        # Update current icon
        self._update_icon()
        
        # Reload hotkeys with new settings
        self.reload_hotkeys()
        
        # Notify main app if callback is set
        if self.settings_update_callback:
            self.settings_update_callback()
    
    def _on_test_connection(self, icon, item):
        """Test OBS connection."""
        import subprocess
        import sys
        
        try:
            # Run test connection script
            subprocess.Popen([sys.executable, "test_connection.py"], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE if hasattr(subprocess, 'CREATE_NEW_CONSOLE') else 0)
        except Exception as e:
            self.logger.error(f"Error running connection test: {e}")
    
    def _on_about(self, icon, item):
        """Show about dialog."""
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        
        about_text = """OBS VirtualCam Tray Controller v1.0

A professional system tray application for controlling OBS source visibility via WebSocket.

Features:
• Connect/disconnect to OBS WebSocket
• Toggle webcam source visibility
• Persistent settings storage
• Auto-reconnection support
• Cross-platform compatibility

GitHub: https://github.com/your-username/OBS-WebCam-SystemTray-Toggle"""
        
        messagebox.showinfo("About", about_text)
        root.destroy()
    
    def _on_github(self, icon, item):
        """Open GitHub repository."""
        webbrowser.open("https://github.com/your-username/OBS-WebCam-SystemTray-Toggle")
    
    def _on_exit(self, icon, item):
        """Handle exit menu item click."""
        self.logger.info("Exit requested from tray menu")
        self.stop()
    
    def _create_main_menu(self) -> pystray.Menu:
        """Create the main menu (left-click menu)."""
        settings = self.settings_manager.settings
        
        # Connection section
        if self.current_connection_state:
            connection_item = pystray.MenuItem("✅ Disconnect from OBS", self._on_disconnect)
        else:
            connection_item = pystray.MenuItem("🔌 Connect to OBS", self._on_connect)
        
        # Webcam control section
        if not self.current_connection_state:
            # Not connected - show disabled webcam controls
            webcam_on_item = pystray.MenuItem("Turn On Webcam", self._on_webcam_on, enabled=False)
            webcam_off_item = pystray.MenuItem("Turn Off Webcam", self._on_webcam_off, enabled=False)
            status_item = pystray.MenuItem("❌ Not connected to OBS", None, enabled=False)
        else:
            # Connected - show appropriate controls
            if self.current_webcam_state is None:
                # State unknown
                webcam_on_item = pystray.MenuItem("Turn On Webcam", self._on_webcam_on, enabled=True)
                webcam_off_item = pystray.MenuItem("Turn Off Webcam", self._on_webcam_off, enabled=True)
                status_item = pystray.MenuItem("❓ Webcam state unknown", self._refresh_webcam_state)
            elif self.current_webcam_state:
                # Webcam is on
                webcam_on_item = pystray.MenuItem("✅ Turn On Webcam", self._on_webcam_on, enabled=False)
                webcam_off_item = pystray.MenuItem("Turn Off Webcam", self._on_webcam_off, enabled=True)
                status_item = pystray.MenuItem(f"🎥 {settings.source_name}: ON", None, enabled=False)
            else:
                # Webcam is off
                webcam_on_item = pystray.MenuItem("Turn On Webcam", self._on_webcam_on, enabled=True)
                webcam_off_item = pystray.MenuItem("❌ Turn Off Webcam", self._on_webcam_off, enabled=False)
                status_item = pystray.MenuItem(f"📴 {settings.source_name}: OFF", None, enabled=False)
        
        return pystray.Menu(
            connection_item,
            pystray.Menu.SEPARATOR,
            status_item,
            webcam_on_item,
            webcam_off_item,
            pystray.MenuItem("🔄 Refresh State", self._refresh_webcam_state, enabled=self.current_connection_state),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self._on_exit)
        )
    
    def _create_settings_menu(self) -> pystray.Menu:
        """Create the settings menu (right-click menu)."""
        return pystray.Menu(
            pystray.MenuItem("⚙️ Settings", self._on_settings),
            pystray.MenuItem("🔧 Test Connection", self._on_test_connection),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("ℹ️ About", self._on_about),
            pystray.MenuItem("🌐 GitHub", self._on_github),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self._on_exit)
        )
    
    def _show_main_menu(self, icon, item):
        """Show main menu - called on left click."""
        pass  # Menu is already set as default
    
    def _show_settings_menu(self, icon, item):
        """Show settings menu - called on right click."""
        # Update the menu to settings menu temporarily
        if self.icon:
            self.icon.menu = self._create_settings_menu()
    
    def _update_icon(self):
        """Update the tray icon based on connection and webcam state."""
        if self.icon is None:
            return
            
        try:
            if not self.current_connection_state:
                self.icon.icon = self.disconnected_icon
                self.icon.title = "OBS VirtualCam Tray Controller - Disconnected"
                self.logger.debug("Updated tray icon to disconnected state")
            elif self.current_webcam_state is True:
                self.icon.icon = self.camera_on_icon
                self.icon.title = "OBS VirtualCam Tray Controller - Webcam ON"
                self.logger.debug("Updated tray icon to camera ON state")
            elif self.current_webcam_state is False:
                self.icon.icon = self.camera_off_icon  
                self.icon.title = "OBS VirtualCam Tray Controller - Webcam OFF"
                self.logger.debug("Updated tray icon to camera OFF state")
            else:
                self.icon.icon = self.disconnected_icon
                self.icon.title = "OBS VirtualCam Tray Controller - Connected (State Unknown)"
                self.logger.debug("Updated tray icon to connected but unknown state")
                
        except Exception as e:
            self.logger.error(f"Error updating tray icon: {e}")
    
    def _update_menus(self):
        """Update menu items based on current state."""
        if self.icon is None:
            return
            
        try:
            # Update the combined menu
            self.icon.menu = self._create_combined_menu()
            self.logger.debug("Updated tray menus")
            
        except Exception as e:
            self.logger.error(f"Error updating menus: {e}")
    
    def update_connection_state(self, connected: bool):
        """
        Update connection state from external source.
        
        Args:
            connected: True if connected to OBS, False otherwise
        """
        if self.current_connection_state != connected:
            self.current_connection_state = connected
            if not connected:
                self.current_webcam_state = None
            self._update_icon()
            self._update_menus()
    
    def update_webcam_state(self, webcam_state: Optional[bool]):
        """
        Update webcam state from external source.
        
        Args:
            webcam_state: True if webcam on, False if off, None if unknown
        """
        if self.current_webcam_state != webcam_state:
            self.current_webcam_state = webcam_state
            self._update_icon()
            self._update_menus()
    
    def start(self):
        """Start the system tray icon."""
        try:
            # Start the hotkey handler
            self.hotkey_handler.start()
            
            # Create icon with initial state
            self.icon = pystray.Icon(
                "OBS VirtualCam Tray Controller",
                self.disconnected_icon,
                "OBS VirtualCam Tray Controller - Starting...",
                menu=self._create_combined_menu()
            )
            
            # Set left-click to show main menu (default behavior)
            self.icon.default_action = None
            
            # Start the icon (this blocks until icon.stop() is called)
            self.logger.info("Starting system tray icon")
            self.icon.run()
            
        except Exception as e:
            self.logger.error(f"Error running tray icon: {e}")
    
    def _create_combined_menu(self) -> pystray.Menu:
        """Create a combined menu with all options."""
        settings = self.settings_manager.settings
        
        # Connection section
        if self.current_connection_state:
            connection_item = pystray.MenuItem("✅ Disconnect from OBS", self._on_disconnect)
        else:
            connection_item = pystray.MenuItem("🔌 Connect to OBS", self._on_connect)
        
        # Webcam control section
        if not self.current_connection_state:
            # Not connected - show disabled webcam controls
            webcam_on_item = pystray.MenuItem("Turn On Webcam", self._on_webcam_on, enabled=False)
            webcam_off_item = pystray.MenuItem("Turn Off Webcam", self._on_webcam_off, enabled=False)
            status_item = pystray.MenuItem("❌ Not connected to OBS", None, enabled=False)
        else:
            # Connected - show appropriate controls
            if self.current_webcam_state is None:
                # State unknown
                webcam_on_item = pystray.MenuItem("Turn On Webcam", self._on_webcam_on, enabled=True)
                webcam_off_item = pystray.MenuItem("Turn Off Webcam", self._on_webcam_off, enabled=True)
                status_item = pystray.MenuItem("❓ Webcam state unknown", self._refresh_webcam_state)
            elif self.current_webcam_state:
                # Webcam is on
                webcam_on_item = pystray.MenuItem("✅ Turn On Webcam", self._on_webcam_on, enabled=False)
                webcam_off_item = pystray.MenuItem("Turn Off Webcam", self._on_webcam_off, enabled=True)
                status_item = pystray.MenuItem(f"🎥 {settings.source_name}: ON", None, enabled=False)
            else:
                # Webcam is off
                webcam_on_item = pystray.MenuItem("Turn On Webcam", self._on_webcam_on, enabled=True)
                webcam_off_item = pystray.MenuItem("❌ Turn Off Webcam", self._on_webcam_off, enabled=False)
                status_item = pystray.MenuItem(f"📴 {settings.source_name}: OFF", None, enabled=False)
        
        # Create the combined menu
        return pystray.Menu(
            # Connection section
            connection_item,
            pystray.Menu.SEPARATOR,
            
            # Webcam controls section
            status_item,
            webcam_on_item,
            webcam_off_item,
            pystray.MenuItem("🔄 Refresh State", self._refresh_webcam_state, enabled=self.current_connection_state),
            
            pystray.Menu.SEPARATOR,
            
            # Settings and tools section
            pystray.MenuItem("⚙️ Settings", self._on_settings),
            pystray.MenuItem("🔧 Test Connection", self._on_test_connection),
            
            pystray.Menu.SEPARATOR,
            
            # About and links section
            pystray.MenuItem("ℹ️ About", self._on_about),
            pystray.MenuItem("🌐 GitHub", self._on_github),
            
            pystray.Menu.SEPARATOR,
            
            # Exit
            pystray.MenuItem("Exit", self._on_exit)
        )
    
    def stop(self):
        """Stop the system tray icon."""
        try:
            # Stop the hotkey handler
            self.hotkey_handler.stop()
            
            if self.icon:
                self.icon.stop()
                self.icon = None
                
            self.logger.info("Tray icon stopped")
        except Exception as e:
            self.logger.error(f"Error stopping tray icon: {e}")
    
    def is_running(self) -> bool:
        """Check if the tray icon is running."""
        return self.icon is not None and hasattr(self.icon, '_running') and self.icon._running 
    
    def _hotkey_webcam_on(self):
        """Handle webcam on hotkey activation."""
        self.logger.info("Global hotkey: Turn webcam ON")
        self._on_webcam_on(None, None)
    
    def _hotkey_webcam_off(self):
        """Handle webcam off hotkey activation."""
        self.logger.info("Global hotkey: Turn webcam OFF")
        self._on_webcam_off(None, None)
    
    def reload_hotkeys(self):
        """Reload hotkeys after settings change."""
        self.hotkey_handler.reload_hotkeys() 