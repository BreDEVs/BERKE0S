"""
Taskbar interface for BERKE0S
"""

import tkinter as tk
import datetime
import logging

logger = logging.getLogger(__name__)

class Taskbar:
    """Taskbar manager class"""
    
    def __init__(self, window_manager):
        self.wm = window_manager
        self.frame = None
        self.clock_label = None
        self.setup_taskbar()
    
    def setup_taskbar(self):
        """Setup taskbar frame and components"""
        try:
            # Create taskbar frame
            self.frame = tk.Frame(
                self.wm.root,
                bg=self.wm.get_theme_color("taskbar"),
                height=45
            )
            self.frame.pack(side=tk.BOTTOM, fill=tk.X)
            self.frame.pack_propagate(False)
            
            # Create components
            self.create_start_button()
            self.create_clock()
            
            logger.info("Taskbar setup completed")
            
        except Exception as e:
            logger.error(f"Taskbar setup error: {e}")
    
    def create_start_button(self):
        """Create start menu button"""
        try:
            start_btn = tk.Button(
                self.frame,
                text="🏠 BERKE0S",
                bg=self.wm.get_theme_color("accent"),
                fg="white",
                font=('Arial', 11, 'bold'),
                relief=tk.FLAT,
                padx=20,
                command=self.show_start_menu
            )
            start_btn.pack(side=tk.LEFT, padx=5, pady=5)
            
        except Exception as e:
            logger.error(f"Start button creation error: {e}")
    
    def create_clock(self):
        """Create clock display"""
        try:
            self.clock_label = tk.Label(
                self.frame,
                bg=self.wm.get_theme_color("taskbar"),
                fg=self.wm.get_theme_color("fg"),
                font=('Arial', 10, 'bold')
            )
            self.clock_label.pack(side=tk.RIGHT, padx=10, pady=5)
            
            # Update clock
            self.update_clock()
            
        except Exception as e:
            logger.error(f"Clock creation error: {e}")
    
    def update_clock(self):
        """Update clock display"""
        try:
            now = datetime.datetime.now()
            time_str = now.strftime("%H:%M")
            date_str = now.strftime("%a %d/%m")
            
            self.clock_label.config(text=f"{time_str}\n{date_str}")
            
            # Schedule next update
            self.wm.root.after(1000, self.update_clock)
            
        except Exception as e:
            logger.error(f"Clock update error: {e}")
            # Retry in 5 seconds on error
            self.wm.root.after(5000, self.update_clock)
    
    def show_start_menu(self):
        """Show start menu"""
        try:
            # Create simple start menu
            menu = tk.Toplevel(self.wm.root)
            menu.title("Start Menu")
            menu.geometry("300x400")
            menu.configure(bg=self.wm.get_theme_color("window"))
            
            # Position menu
            menu.geometry("+50+100")
            
            # Menu items
            items = [
                ("📁 File Manager", self.launch_file_manager),
                ("💻 Terminal", self.launch_terminal),
                ("📝 Text Editor", self.launch_text_editor),
                ("🧮 Calculator", self.launch_calculator),
                ("⚙️ Settings", self.launch_settings),
                ("🖥️ Display Settings", self.launch_display_settings),
                ("📊 System Monitor", self.launch_system_monitor)
            ]
            
            for text, command in items:
                btn = tk.Button(
                    menu,
                    text=text,
                    command=lambda cmd=command: self.execute_and_close(cmd, menu),
                    bg=self.wm.get_theme_color("window"),
                    fg=self.wm.get_theme_color("fg"),
                    font=('Arial', 11),
                    relief=tk.FLAT,
                    anchor='w',
                    padx=20,
                    pady=8
                )
                btn.pack(fill=tk.X, padx=10, pady=2)
                
                # Hover effects
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.wm.get_theme_color("hover")))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.wm.get_theme_color("window")))
            
        except Exception as e:
            logger.error(f"Start menu error: {e}")
    
    def execute_and_close(self, command, menu):
        """Execute command and close menu"""
        try:
            menu.destroy()
            command()
        except Exception as e:
            logger.error(f"Command execution error: {e}")
    
    # Application launchers (placeholders)
    def launch_file_manager(self):
        """Launch file manager"""
        logger.info("Launching file manager...")
    
    def launch_terminal(self):
        """Launch terminal"""
        logger.info("Launching terminal...")
    
    def launch_text_editor(self):
        """Launch text editor"""
        logger.info("Launching text editor...")
    
    def launch_calculator(self):
        """Launch calculator"""
        logger.info("Launching calculator...")
    
    def launch_settings(self):
        """Launch settings"""
        logger.info("Launching settings...")
    
    def launch_display_settings(self):
        """Launch display settings"""
        logger.info("Launching display settings...")
    
    def launch_system_monitor(self):
        """Launch system monitor"""
        logger.info("Launching system monitor...")