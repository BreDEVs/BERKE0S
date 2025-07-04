"""
Notification system for BERKE0S
"""

import tkinter as tk
import datetime
import logging
from typing import List, Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)

class NotificationSystem:
    """Advanced notification system"""
    
    def __init__(self, window_manager):
        self.wm = window_manager
        self.notifications: List[Dict[str, Any]] = []
        self.notification_id = 0
        self.notification_history: List[Dict[str, Any]] = []
        self.max_history = 100
    
    def send(self, title: str, message: str, timeout: int = 5000, 
             notification_type: str = "info", actions: Optional[List[Dict]] = None, 
             icon: Optional[str] = None) -> None:
        """Send a notification"""
        try:
            if not hasattr(self.wm, 'root') or not self.wm.root:
                return
            
            self.notification_id += 1
            
            # Store in history
            notification_data = {
                "id": self.notification_id,
                "title": title,
                "message": message,
                "type": notification_type,
                "timestamp": datetime.datetime.now(),
                "actions": actions or []
            }
            self.notification_history.append(notification_data)
            
            # Limit history size
            if len(self.notification_history) > self.max_history:
                self.notification_history.pop(0)
            
            # Create notification window
            notif = tk.Toplevel(self.wm.root)
            notif.withdraw()
            notif.overrideredirect(True)
            notif.attributes('-topmost', True)
            notif.configure(bg='#1a1a1a')
            
            # Position notification
            self._position_notification(notif)
            
            # Create notification content
            self._create_notification_content(notif, title, message, notification_type, actions, icon)
            
            # Store notification
            notification_data["window"] = notif
            self.notifications.append(notification_data)
            
            # Show with animation
            self._animate_notification(notif, "show")
            
            # Auto close
            if timeout > 0:
                self.wm.root.after(timeout, lambda: self._close_notification(notification_data))
            
        except Exception as e:
            logger.error(f"Notification error: {e}")
    
    def _position_notification(self, notif: tk.Toplevel) -> None:
        """Position notification window"""
        try:
            screen_width = self.wm.root.winfo_screenwidth()
            screen_height = self.wm.root.winfo_screenheight()
            
            notif_width = 350
            notif_height = 100
            
            # Position in top-right corner
            x = screen_width - notif_width - 20
            y = 20 + len(self.notifications) * (notif_height + 10)
            
            notif.geometry(f"{notif_width}x{notif_height}+{x}+{y}")
            
        except Exception as e:
            logger.error(f"Notification positioning error: {e}")
    
    def _create_notification_content(self, notif: tk.Toplevel, title: str, 
                                   message: str, notif_type: str, 
                                   actions: Optional[List[Dict]], icon: Optional[str]) -> None:
        """Create notification content"""
        try:
            # Color scheme based on type
            colors = {
                "info": {"icon": "ℹ️", "color": "#4a9eff", "text_color": "white"},
                "success": {"icon": "✅", "color": "#00ff88", "text_color": "black"},
                "warning": {"icon": "⚠️", "color": "#ffb347", "text_color": "black"},
                "error": {"icon": "❌", "color": "#ff6b6b", "text_color": "white"},
            }
            
            config = colors.get(notif_type, colors["info"])
            
            # Main container
            main_frame = tk.Frame(notif, bg='#2a2a2a', relief=tk.RAISED, bd=2)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
            
            # Header with colored stripe
            header_frame = tk.Frame(main_frame, bg=config["color"], height=30)
            header_frame.pack(fill=tk.X)
            header_frame.pack_propagate(False)
            
            # Icon and title
            title_frame = tk.Frame(header_frame, bg=config["color"])
            title_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Icon
            icon_text = icon if icon else config["icon"]
            tk.Label(title_frame, text=icon_text, bg=config["color"], 
                    fg=config["text_color"], font=('Arial', 12)).pack(side=tk.LEFT)
            
            # Title
            tk.Label(title_frame, text=title, bg=config["color"], 
                    fg=config["text_color"], font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(10, 0))
            
            # Close button
            close_btn = tk.Label(title_frame, text="✕", bg=config["color"], 
                               fg=config["text_color"], font=('Arial', 8), cursor='hand2')
            close_btn.pack(side=tk.RIGHT)
            close_btn.bind('<Button-1>', lambda e: self._close_notification_by_window(notif))
            
            # Message content
            content_frame = tk.Frame(main_frame, bg='#3a3a3a')
            content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Message text
            msg_label = tk.Label(content_frame, text=message, bg='#3a3a3a', fg='white', 
                               font=('Arial', 9), wraplength=320, justify=tk.LEFT, anchor='nw')
            msg_label.pack(fill=tk.X, pady=(0, 5))
            
        except Exception as e:
            logger.error(f"Notification content creation error: {e}")
    
    def _animate_notification(self, notif: tk.Toplevel, action: str) -> None:
        """Animate notification appearance/disappearance"""
        try:
            if action == "show":
                notif.deiconify()
                notif.attributes('-alpha', 0)
                
                def fade_in(alpha: float = 0) -> None:
                    if alpha <= 0.95:
                        notif.attributes('-alpha', alpha)
                        self.wm.root.after(20, lambda: fade_in(alpha + 0.1))
                
                fade_in()
                
            elif action == "hide":
                def fade_out(alpha: float = 0.95) -> None:
                    if alpha >= 0:
                        notif.attributes('-alpha', alpha)
                        self.wm.root.after(20, lambda: fade_out(alpha - 0.1))
                    else:
                        notif.destroy()
                
                fade_out()
                
        except Exception as e:
            logger.error(f"Animation error: {e}")
            if action == "hide":
                notif.destroy()
    
    def _close_notification(self, notification: Dict[str, Any]) -> None:
        """Close a specific notification"""
        try:
            if notification in self.notifications:
                self.notifications.remove(notification)
                if "window" in notification:
                    self._animate_notification(notification["window"], "hide")
                self._reposition_notifications()
        except Exception as e:
            logger.error(f"Close notification error: {e}")
    
    def _close_notification_by_window(self, notif_window: tk.Toplevel) -> None:
        """Close notification by window reference"""
        for notification in self.notifications:
            if notification.get("window") == notif_window:
                self._close_notification(notification)
                break
    
    def _reposition_notifications(self) -> None:
        """Reposition remaining notifications"""
        try:
            screen_width = self.wm.root.winfo_screenwidth()
            
            for i, notification in enumerate(self.notifications):
                if "window" in notification:
                    notif = notification["window"]
                    width, height = 350, 100
                    
                    x = screen_width - width - 20
                    y = 20 + i * (height + 10)
                    
                    notif.geometry(f"{width}x{height}+{x}+{y}")
                    
        except Exception as e:
            logger.error(f"Reposition error: {e}")