"""
Main window manager for BERKE0S
"""

import os
import sys
import logging
import tkinter as tk
from typing import Optional

from core.config import ConfigManager
from display.manager import DisplayManager
from ui.desktop import Desktop
from ui.taskbar import Taskbar
from ui.notifications import NotificationSystem

logger = logging.getLogger(__name__)

class WindowManager:
    """Main window manager class"""
    
    def __init__(self, config_manager: ConfigManager, headless: bool = False):
        self.config_manager = config_manager
        self.headless = headless
        self.root: Optional[tk.Tk] = None
        self.display_manager = DisplayManager()
        self.desktop: Optional[Desktop] = None
        self.taskbar: Optional[Taskbar] = None
        self.notifications: Optional[NotificationSystem] = None
        self.running = False
        
    def run(self) -> int:
        """Run the window manager"""
        try:
            logger.info("Starting BERKE0S window manager...")
            
            # Setup display
            if not self.headless:
                success = self.display_manager.setup_display_environment()
                if not success:
                    logger.warning("Display setup failed, running in headless mode")
                    self.headless = True
            
            if self.headless:
                return self._run_headless()
            else:
                return self._run_gui()
                
        except Exception as e:
            logger.error(f"Window manager error: {e}")
            return 1
    
    def _run_gui(self) -> int:
        """Run with GUI"""
        try:
            # Create main window
            self.root = tk.Tk()
            self.root.title("BERKE0S Desktop Environment V2")
            
            # Configure window
            try:
                self.root.attributes('-fullscreen', True)
            except:
                self.root.geometry("1024x768")
            
            self.root.configure(bg='#1a1a1a')
            
            # Setup components
            self._setup_components()
            
            # Start main loop
            self.running = True
            logger.info("Starting GUI main loop...")
            self.root.mainloop()
            
            return 0
            
        except Exception as e:
            logger.error(f"GUI run error: {e}")
            return 1
        finally:
            self._cleanup()
    
    def _run_headless(self) -> int:
        """Run in headless mode"""
        try:
            logger.info("Running in headless mode...")
            
            # Create minimal root for services
            self.root = tk.Tk()
            self.root.withdraw()
            
            # Setup notifications only
            self.notifications = NotificationSystem(self)
            
            # Keep running
            self.running = True
            self.root.mainloop()
            
            return 0
            
        except Exception as e:
            logger.error(f"Headless run error: {e}")
            return 1
        finally:
            self._cleanup()
    
    def _setup_components(self):
        """Setup UI components"""
        try:
            # Notification system
            self.notifications = NotificationSystem(self)
            
            # Desktop
            self.desktop = Desktop(self)
            
            # Taskbar
            self.taskbar = Taskbar(self)
            
            # Bind events
            self.root.protocol("WM_DELETE_WINDOW", self.shutdown)
            
            # Show welcome notification
            if self.notifications:
                self.notifications.send(
                    "BERKE0S V2 Ready",
                    "Enhanced Desktop Environment loaded successfully!",
                    notification_type="success"
                )
                
        except Exception as e:
            logger.error(f"Component setup error: {e}")
            raise
    
    def get_config(self, key: str, default=None):
        """Get configuration value"""
        return self.config_manager.get(key, default)
    
    def set_config(self, key: str, value):
        """Set configuration value"""
        self.config_manager.set(key, value)
        self.config_manager.save_config()
    
    def get_theme_color(self, color_name: str) -> str:
        """Get theme color"""
        # Default colors
        colors = {
            "bg": "#1a1a1a",
            "fg": "#ffffff", 
            "accent": "#00ff88",
            "secondary": "#4a9eff",
            "window": "#2a2a2a",
            "input": "#333333",
            "error": "#ff6b6b",
            "warning": "#ffb347",
            "success": "#00ff88"
        }
        
        return colors.get(color_name, "#000000")
    
    def shutdown(self):
        """Shutdown the window manager"""
        try:
            logger.info("Shutting down BERKE0S...")
            
            self.running = False
            
            if self.root:
                self.root.quit()
                
        except Exception as e:
            logger.error(f"Shutdown error: {e}")
    
    def _cleanup(self):
        """Cleanup resources"""
        try:
            logger.info("Cleaning up resources...")
            
            if self.display_manager:
                self.display_manager.shutdown_display()
                
        except Exception as e:
            logger.error(f"Cleanup error: {e}")