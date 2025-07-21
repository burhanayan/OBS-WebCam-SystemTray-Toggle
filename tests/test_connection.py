#!/usr/bin/env python3
"""
OBS WebSocket Connection Test Script

This script tests the connection to OBS Studio via WebSocket and verifies
that the configured scene and source exist and are accessible.
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path to access src module
sys.path.append(str(Path(__file__).parent.parent))

from src.settings_manager import SettingsManager
import obsws_python as obs


def main():
    """Test OBS WebSocket connection."""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    logger.info("OBS WebSocket Connection Test")
    logger.info("=" * 40)
    
    # Load settings
    settings_manager = SettingsManager()
    settings = settings_manager.settings
    
    logger.info(f"Testing connection to: {settings.obs_host}:{settings.obs_port}")
    logger.info(f"Target scene: '{settings.scene_name}'")
    logger.info(f"Target source: '{settings.source_name}'")
    logger.info("-" * 40)
    
    try:
        # Connect to OBS
        logger.info("Connecting to OBS WebSocket...")
        client = obs.ReqClient(
            host=settings.obs_host,
            port=settings.obs_port,
            password=settings.obs_password,
            timeout=10
        )
        
        # Test basic connection
        version_info = client.get_version()
        logger.info("✅ Successfully connected to OBS!")
        logger.info(f"   OBS Version: {version_info.obs_version}")
        logger.info(f"   WebSocket Version: {version_info.obs_web_socket_version}")
        logger.info(f"   Available Requests: {version_info.available_requests}")
        
        # Test scene existence
        logger.info(f"\nChecking if scene '{settings.scene_name}' exists...")
        scenes = client.get_scene_list()
        scene_names = [scene['sceneName'] for scene in scenes.scenes]
        
        if settings.scene_name in scene_names:
            logger.info(f"✅ Scene '{settings.scene_name}' found!")
        else:
            logger.error(f"❌ Scene '{settings.scene_name}' not found!")
            logger.info(f"   Available scenes: {scene_names}")
            return False
            
        # Test source existence in scene
        logger.info(f"\nChecking if source '{settings.source_name}' exists in scene...")
        scene_items = client.get_scene_item_list(settings.scene_name)
        source_names = [item['sourceName'] for item in scene_items.scene_items]
        
        if settings.source_name in source_names:
            logger.info(f"✅ Source '{settings.source_name}' found in scene!")
            
            # Find the source and get its current state
            source_item_id = None
            for item in scene_items.scene_items:
                if item['sourceName'] == settings.source_name:
                    source_item_id = item['sceneItemId']
                    break
            
            if source_item_id is not None:
                # Get current visibility state
                item_enabled = client.get_scene_item_enabled(settings.scene_name, source_item_id)
                state = "visible" if item_enabled.scene_item_enabled else "hidden"
                logger.info(f"   Current state: {state}")
                
                # Test toggle functionality
                logger.info(f"\nTesting visibility toggle...")
                
                # Toggle off
                client.set_scene_item_enabled(settings.scene_name, source_item_id, False)
                logger.info("✅ Source hidden successfully")
                
                # Toggle on
                client.set_scene_item_enabled(settings.scene_name, source_item_id, True)
                logger.info("✅ Source shown successfully")
                
                # Restore original state
                client.set_scene_item_enabled(settings.scene_name, source_item_id, item_enabled.scene_item_enabled)
                logger.info("✅ Original state restored")
                
        else:
            logger.error(f"❌ Source '{settings.source_name}' not found in scene!")
            logger.info(f"   Available sources: {source_names}")
            return False
        
        logger.info("\n" + "=" * 40)
        logger.info("🎉 All tests passed! OBS connection is working correctly.")
        logger.info("\nYour configuration:")
        logger.info(f"   Host: {settings.obs_host}")
        logger.info(f"   Port: {settings.obs_port}")
        logger.info(f"   Scene: {settings.scene_name}")
        logger.info(f"   Source: {settings.source_name}")
        logger.info("\nYou can now run the main application!")
        return True
        
    except ConnectionError as e:
        logger.error(f"❌ Connection failed: {e}")
        logger.error("\nTroubleshooting tips:")
        logger.error("1. Make sure OBS Studio is running")
        logger.error("2. Enable WebSocket server in OBS (Tools → WebSocket Server Settings)")
        logger.error("3. Check that the host and port are correct")
        logger.error("4. Verify the WebSocket password in settings")
        return False
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 