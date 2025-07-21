"""
Settings manager for OBS VirtualCam Tray Controller.
Handles persistent storage and configuration management.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class Settings:
    """Application settings dataclass."""
    # OBS WebSocket Configuration
    obs_host: str = "localhost"
    obs_port: int = 4455
    obs_password: Optional[str] = None
    
    # OBS Scene and Source Configuration
    scene_name: str = "ZoomInWebCam"
    source_name: str = "Video Capture Device 2"
    
    # Application Configuration
    reconnect_delay: float = 3.0
    auto_connect: bool = False
    start_minimized: bool = True
    
    # Icon Configuration
    camera_on_color: str = "#4CAF50"
    camera_off_color: str = "#F44336"
    
    # Keyboard shortcuts
    hotkey_webcam_on: str = "<ctrl>+<alt>+1"
    hotkey_webcam_off: str = "<ctrl>+<alt>+2"
    enable_hotkeys: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Settings':
        """Create settings from dictionary."""
        # Filter out unknown keys to handle version compatibility
        known_fields = {field.name for field in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered_data)


class SettingsManager:
    """Manages application settings with persistent storage."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize settings manager.
        
        Args:
            config_dir: Optional custom configuration directory
        """
        self.logger = logging.getLogger(__name__)
        
        # Determine config directory
        if config_dir:
            self.config_dir = config_dir
        else:
            # Use platform-appropriate config directory
            home = Path.home()
            if Path.home().joinpath("AppData").exists():  # Windows
                self.config_dir = home / "AppData" / "Roaming" / "OBSTrayController"
            elif Path.home().joinpath(".config").exists():  # Linux
                self.config_dir = home / ".config" / "obs-tray-controller"
            else:  # macOS or fallback
                self.config_dir = home / ".obs-tray-controller"
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "settings.json"
        
        # Load or create default settings
        self._settings = self._load_settings()
    
    def _load_settings(self) -> Settings:
        """Load settings from file or create defaults."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    settings = Settings.from_dict(data)
                    self.logger.info(f"Loaded settings from {self.config_file}")
                    return settings
            else:
                self.logger.info("No settings file found, using defaults")
                return Settings()
                
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}, using defaults")
            return Settings()
    
    def _save_settings(self) -> bool:
        """Save current settings to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings.to_dict(), f, indent=2)
            self.logger.info(f"Settings saved to {self.config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            return False
    
    @property
    def settings(self) -> Settings:
        """Get current settings."""
        return self._settings
    
    def update_setting(self, key: str, value: Any) -> bool:
        """
        Update a single setting.
        
        Args:
            key: Setting key name
            value: New value
            
        Returns:
            bool: True if successful
        """
        try:
            if hasattr(self._settings, key):
                setattr(self._settings, key, value)
                return self._save_settings()
            else:
                self.logger.error(f"Unknown setting key: {key}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating setting {key}: {e}")
            return False
    
    def update_settings(self, **kwargs) -> bool:
        """
        Update multiple settings at once.
        
        Args:
            **kwargs: Settings to update
            
        Returns:
            bool: True if successful
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self._settings, key):
                    setattr(self._settings, key, value)
                else:
                    self.logger.warning(f"Ignoring unknown setting: {key}")
            
            return self._save_settings()
            
        except Exception as e:
            self.logger.error(f"Error updating settings: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to defaults."""
        try:
            self._settings = Settings()
            return self._save_settings()
            
        except Exception as e:
            self.logger.error(f"Error resetting settings: {e}")
            return False
    
    def export_settings(self, file_path: Path) -> bool:
        """Export settings to a file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._settings.to_dict(), f, indent=2)
            self.logger.info(f"Settings exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting settings: {e}")
            return False
    
    def import_settings(self, file_path: Path) -> bool:
        """Import settings from a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._settings = Settings.from_dict(data)
            
            success = self._save_settings()
            if success:
                self.logger.info(f"Settings imported from {file_path}")
            return success
            
        except Exception as e:
            self.logger.error(f"Error importing settings: {e}")
            return False 