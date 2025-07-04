"""
Configuration management for BERKE0S
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "version": "3.0-v2",
    "first_boot": True,
    "language": "tr_TR",
    "timezone": "Europe/Istanbul",
    "theme": "berke_dark",
    "users": [],
    "wifi": {"ssid": "", "password": ""},
    "installed": False,
    "display": {
        "auto_detect": True,
        "force_x11": True,
        "display_server": "auto",
        "resolution": "auto",
        "refresh_rate": 60,
        "color_depth": 24,
        "multi_monitor": False,
        "primary_monitor": 0,
        "x_arguments": ["-nolisten", "tcp", "-nocursor"],
        "fallback_resolution": "1024x768",
        "virtual_display": False,
        "headless_mode": False
    },
    "desktop": {
        "wallpaper": "",
        "wallpaper_mode": "stretch",
        "icon_size": 48,
        "grid_snap": True,
        "effects": True,
        "transparency": 0.95,
        "blur_radius": 5,
        "shadow_offset": 3,
        "animation_speed": 300,
        "auto_arrange": False,
        "show_desktop_icons": True,
        "desktop_icons": [],
        "virtual_desktops": 4,
        "show_dock": False
    },
    "taskbar": {
        "position": "bottom",
        "auto_hide": False,
        "color": "#1a1a1a",
        "size": 45,
        "show_clock": True,
        "show_system_tray": True,
        "show_quick_launch": True,
        "transparency": 0.9
    },
    "notifications": {
        "enabled": True,
        "timeout": 5000,
        "position": "top-right",
        "sound_enabled": True,
        "show_previews": True
    },
    "power": {
        "sleep_timeout": 1800,
        "screen_off_timeout": 900,
        "hibernate_enabled": True,
        "cpu_scaling": "ondemand"
    },
    "accessibility": {
        "high_contrast": False,
        "screen_reader": False,
        "font_scale": 1.0,
        "magnifier": False,
        "keyboard_navigation": True
    },
    "security": {
        "auto_lock": True,
        "lock_timeout": 600,
        "require_password": True,
        "encryption_enabled": False
    },
    "network": {
        "auto_connect": True,
        "proxy_enabled": False,
        "proxy_host": "",
        "proxy_port": 8080,
        "firewall_enabled": True
    },
    "audio": {
        "master_volume": 75,
        "mute": False,
        "default_device": "auto",
        "sound_theme": "default"
    },
    "system": {
        "auto_updates": True,
        "crash_reporting": True,
        "telemetry": False,
        "performance_mode": "balanced",
        "auto_backup": False,
        "backup_interval": 24,
        "24_hour_format": True
    }
}

class ConfigManager:
    """Configuration management class"""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = config_dir or os.path.expanduser("~/.berke0s")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.install_flag = os.path.join(self.config_dir, ".installed")
        
        # Ensure directories exist
        os.makedirs(self.config_dir, exist_ok=True)
        
        self._config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                # Merge with defaults
                return self._merge_configs(DEFAULT_CONFIG.copy(), config)
            
            return DEFAULT_CONFIG.copy()
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return DEFAULT_CONFIG.copy()
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=4)
            logger.info("Configuration saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def is_installed(self) -> bool:
        """Check if BERKE0S is installed"""
        return os.path.exists(self.install_flag) and self.get("installed", False)
    
    def mark_installed(self) -> None:
        """Mark BERKE0S as installed"""
        self.set("installed", True)
        self.save_config()
        
        # Create install flag
        try:
            with open(self.install_flag, 'w') as f:
                f.write("installed")
        except Exception as e:
            logger.error(f"Error creating install flag: {e}")
    
    def get_config_dir(self) -> str:
        """Get configuration directory"""
        return self.config_dir
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Recursively merge configurations"""
        for key, value in default.items():
            if key not in loaded:
                loaded[key] = value
            elif isinstance(value, dict) and isinstance(loaded[key], dict):
                loaded[key] = self._merge_configs(value, loaded[key])
        
        return loaded