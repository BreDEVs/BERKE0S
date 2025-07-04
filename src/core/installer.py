"""
Installation wizard for BERKE0S
"""

import os
import sys
import json
import hashlib
import datetime
import logging
import sqlite3
from typing import Dict, Any

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

logger = logging.getLogger(__name__)

class InstallationWizard:
    """Installation wizard for BERKE0S"""
    
    def __init__(self):
        self.config = {}
        self.gui_mode = GUI_AVAILABLE
        
    def start_installation(self) -> bool:
        """Start installation process"""
        try:
            logger.info("Starting BERKE0S installation...")
            
            if self.gui_mode:
                return self._gui_installation()
            else:
                return self._console_installation()
                
        except Exception as e:
            logger.error(f"Installation error: {e}")
            return False
    
    def _gui_installation(self) -> bool:
        """GUI installation process"""
        try:
            root = tk.Tk()
            root.title("BERKE0S Installation")
            root.geometry("800x600")
            
            # Installation content
            frame = tk.Frame(root)
            frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Header
            header = tk.Label(frame, text="BERKE0S Ultimate Desktop Environment V2",
                            font=("Arial", 16, "bold"))
            header.pack(pady=(0, 20))
            
            # Progress
            self.progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(frame, variable=self.progress_var, maximum=100)
            progress_bar.pack(fill=tk.X, pady=(0, 20))
            
            # Status
            self.status_var = tk.StringVar(value="Preparing installation...")
            status_label = tk.Label(frame, textvariable=self.status_var)
            status_label.pack(pady=(0, 20))
            
            # Start installation
            root.after(100, lambda: self._perform_installation(root))
            root.mainloop()
            
            return True
            
        except Exception as e:
            logger.error(f"GUI installation error: {e}")
            return self._console_installation()
    
    def _console_installation(self) -> bool:
        """Console installation process"""
        try:
            print("\n" + "="*60)
            print("  BERKE0S Ultimate Desktop Environment V2")
            print("  Enhanced Display Management")
            print("="*60)
            print("\nStarting installation...\n")
            
            # Basic configuration
            self.config = {
                "version": "3.0-v2",
                "installed": True,
                "language": "tr_TR",
                "theme": "berke_dark",
                "first_boot": False,
                "installation_date": datetime.datetime.now().isoformat()
            }
            
            # Save configuration
            config_dir = os.path.expanduser("~/.berke0s")
            os.makedirs(config_dir, exist_ok=True)
            
            config_file = os.path.join(config_dir, "config.json")
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            
            # Create install flag
            install_flag = os.path.join(config_dir, ".installed")
            with open(install_flag, 'w') as f:
                f.write("installed")
            
            # Initialize database
            self._init_database(config_dir)
            
            print("✓ Installation completed successfully!")
            print(f"Configuration saved to: {config_dir}")
            
            return True
            
        except Exception as e:
            logger.error(f"Console installation error: {e}")
            print(f"✗ Installation failed: {e}")
            return False
    
    def _perform_installation(self, root):
        """Perform actual installation steps"""
        try:
            steps = [
                ("Initializing...", self._init_step),
                ("Creating directories...", self._create_directories),
                ("Setting up database...", self._setup_database),
                ("Configuring display...", self._configure_display),
                ("Installing themes...", self._install_themes),
                ("Finalizing...", self._finalize)
            ]
            
            total_steps = len(steps)
            
            for i, (description, step_func) in enumerate(steps):
                self.status_var.set(description)
                progress = (i / total_steps) * 100
                self.progress_var.set(progress)
                root.update()
                
                step_func()
                
            self.progress_var.set(100)
            self.status_var.set("Installation completed!")
            root.update()
            
            # Show completion message
            messagebox.showinfo("Installation Complete", 
                              "BERKE0S has been installed successfully!")
            
            root.destroy()
            
        except Exception as e:
            logger.error(f"Installation step error: {e}")
            messagebox.showerror("Installation Error", f"Installation failed: {str(e)}")
            root.destroy()
    
    def _init_step(self):
        """Initialize installation"""
        self.config = {
            "version": "3.0-v2",
            "installed": True,
            "language": "tr_TR",
            "theme": "berke_dark",
            "first_boot": False,
            "installation_date": datetime.datetime.now().isoformat()
        }
    
    def _create_directories(self):
        """Create necessary directories"""
        config_dir = os.path.expanduser("~/.berke0s")
        directories = [
            config_dir,
            os.path.join(config_dir, "themes"),
            os.path.join(config_dir, "plugins"),
            os.path.join(config_dir, "wallpapers"),
            os.path.join(config_dir, "applications"),
            os.path.join(config_dir, "backups")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def _setup_database(self):
        """Setup system database"""
        config_dir = os.path.expanduser("~/.berke0s")
        self._init_database(config_dir)
    
    def _configure_display(self):
        """Configure display settings"""
        # Set default display configuration
        self.config["display"] = {
            "auto_detect": True,
            "force_x11": True,
            "display_server": "auto",
            "resolution": "auto",
            "refresh_rate": 60
        }
    
    def _install_themes(self):
        """Install default themes"""
        # Default themes configuration would be set here
        pass
    
    def _finalize(self):
        """Finalize installation"""
        config_dir = os.path.expanduser("~/.berke0s")
        
        # Save configuration
        config_file = os.path.join(config_dir, "config.json")
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
        
        # Create install flag
        install_flag = os.path.join(config_dir, ".installed")
        with open(install_flag, 'w') as f:
            f.write("installed")
    
    def _init_database(self, config_dir: str):
        """Initialize SQLite database"""
        try:
            db_file = os.path.join(config_dir, "berke0s.db")
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    fullname TEXT,
                    password_hash TEXT,
                    is_admin INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Applications table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    command TEXT,
                    icon TEXT,
                    category TEXT,
                    description TEXT,
                    installed INTEGER DEFAULT 1
                )
            ''')
            
            # Display logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS display_logs (
                    id INTEGER PRIMARY KEY,
                    event_type TEXT,
                    display_id TEXT,
                    message TEXT,
                    success INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert default applications
            default_apps = [
                ("File Manager", "berke0s_filemanager", "📁", "System", "File management"),
                ("Text Editor", "berke0s_texteditor", "📝", "Office", "Text editing"),
                ("Calculator", "berke0s_calculator", "🧮", "Utility", "Calculator"),
                ("Terminal", "berke0s_terminal", "💻", "System", "Terminal"),
                ("Settings", "berke0s_settings", "⚙️", "System", "System settings"),
                ("Display Settings", "berke0s_display", "🖥️", "System", "Display configuration")
            ]
            
            for app in default_apps:
                cursor.execute(
                    "INSERT OR REPLACE INTO applications (name, command, icon, category, description) VALUES (?, ?, ?, ?, ?)",
                    app
                )
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise