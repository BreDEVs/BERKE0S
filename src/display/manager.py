"""
Enhanced display management system for BERKE0S V2
Optimized for Tiny Core Linux with robust fallback methods
"""

import os
import sys
import time
import logging
import subprocess
import platform
import shutil
from typing import Dict, Any, List, Optional

logger = logging.getLogger('display')

class DisplayManager:
    """Advanced display management for Tiny Core Linux and other systems"""
    
    def __init__(self):
        self.display_info = {}
        self.x_process = None
        self.display_ready = False
        self.current_display = ":0"
        self.backup_displays = [":1", ":2", ":10"]
        self.x_server_attempts = 0
        self.max_attempts = 5
        
    def detect_environment(self) -> Dict[str, Any]:
        """Detect current environment and capabilities"""
        try:
            env_info = {
                "os_name": platform.system(),
                "distribution": self._get_distribution(),
                "is_tinycore": self._is_tiny_core_linux(),
                "desktop_session": os.environ.get("DESKTOP_SESSION", ""),
                "display": os.environ.get("DISPLAY", ""),
                "wayland_display": os.environ.get("WAYLAND_DISPLAY", ""),
                "x11_available": self._check_x11_availability(),
                "wayland_available": self._check_wayland_availability(),
                "graphics_driver": self._detect_graphics_driver(),
                "current_user": os.getenv("USER", "unknown"),
                "tty": self._get_current_tty(),
                "runlevel": self._get_runlevel()
            }
            
            logger.info(f"Environment detected: {env_info}")
            return env_info
            
        except Exception as e:
            logger.error(f"Environment detection error: {e}")
            return {"error": str(e)}
    
    def setup_display_environment(self) -> bool:
        """Setup comprehensive display environment"""
        try:
            logger.info("Starting enhanced display setup...")
            
            # Check if we already have a working display
            if self._test_existing_display():
                logger.info("Existing display working, using it")
                return True
            
            # Prepare environment
            self._prepare_display_environment()
            
            # Try different display methods
            env_info = self.detect_environment()
            if env_info.get("is_tinycore", False):
                success = self._setup_tinycore_display()
            else:
                success = self._setup_generic_display()
            
            if not success:
                success = self._try_fallback_display_methods()
            
            if success:
                success = self._verify_display_setup()
            
            if success:
                logger.info("Display setup completed successfully")
                self.display_ready = True
                return True
            else:
                logger.warning("All display setup methods failed")
                return False
                
        except Exception as e:
            logger.error(f"Display setup error: {e}")
            return False
    
    def get_display_info(self) -> Dict[str, Any]:
        """Get current display information"""
        try:
            if self.display_ready:
                try:
                    result = subprocess.run(
                        ['xdpyinfo', '-display', self.current_display],
                        capture_output=True, text=True, timeout=5
                    )
                    
                    if result.returncode == 0:
                        info = self._parse_xdpyinfo_output(result.stdout)
                        self.display_info = info
                        return info
                except:
                    pass
            
            return {
                "display": self.current_display,
                "mode": "headless" if not self.display_ready else "unknown",
                "width": 1024,
                "height": 768,
                "depth": 24
            }
            
        except Exception as e:
            logger.error(f"Get display info error: {e}")
            return {"error": str(e)}
    
    def is_display_ready(self) -> bool:
        """Check if display is ready for use"""
        return self.display_ready
    
    def get_current_display(self) -> str:
        """Get current display identifier"""
        return self.current_display
    
    def shutdown_display(self):
        """Shutdown display system"""
        try:
            logger.info("Shutting down display system...")
            
            if self.x_process and self.x_process.poll() is None:
                try:
                    self.x_process.terminate()
                    time.sleep(2)
                    if self.x_process.poll() is None:
                        self.x_process.kill()
                except:
                    pass
            
            self._cleanup_x_processes()
            self.display_ready = False
            
            logger.info("Display system shutdown completed")
            
        except Exception as e:
            logger.error(f"Display shutdown error: {e}")
    
    # Private methods
    
    def _is_tiny_core_linux(self) -> bool:
        """Check if running on Tiny Core Linux"""
        try:
            tc_indicators = [
                "/opt/tce",
                "/etc/init.d/tc-config", 
                "/usr/bin/tce-load",
                "/opt/bootlocal.sh"
            ]
            
            for indicator in tc_indicators:
                if os.path.exists(indicator):
                    return True
            
            version_files = ["/etc/tc-release", "/etc/tinycore-release"]
            for vfile in version_files:
                if os.path.exists(vfile):
                    return True
            
            try:
                result = subprocess.run(['uname', '-a'], capture_output=True, text=True, timeout=5)
                if 'tinycore' in result.stdout.lower():
                    return True
            except:
                pass
                
            return False
            
        except Exception as e:
            logger.error(f"Tiny Core detection error: {e}")
            return False
    
    def _get_distribution(self) -> str:
        """Get Linux distribution name"""
        try:
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release", 'r') as f:
                    content = f.read()
                    if 'tinycore' in content.lower():
                        return "TinyCore"
                    elif 'ubuntu' in content.lower():
                        return "Ubuntu"
                    elif 'debian' in content.lower():
                        return "Debian"
            
            return "Unknown"
            
        except Exception as e:
            logger.error(f"Distribution detection error: {e}")
            return "Unknown"
    
    def _check_x11_availability(self) -> Dict[str, Any]:
        """Check if X11 is available"""
        try:
            x11_binaries = ['X', 'Xorg', 'xinit', 'startx']
            available_binaries = []
            
            for binary in x11_binaries:
                if shutil.which(binary):
                    available_binaries.append(binary)
            
            x11_libs = ['/usr/lib/xorg', '/usr/lib/X11', '/usr/X11R6/lib']
            available_libs = [lib for lib in x11_libs if os.path.exists(lib)]
            
            return {
                "available": len(available_binaries) > 0,
                "binaries": available_binaries,
                "libraries": available_libs
            }
            
        except Exception as e:
            logger.error(f"X11 availability check error: {e}")
            return {"available": False, "error": str(e)}
    
    def _check_wayland_availability(self) -> Dict[str, Any]:
        """Check if Wayland is available"""
        try:
            wayland_binaries = ['wayland-scanner', 'weston']
            available_binaries = []
            
            for binary in wayland_binaries:
                if shutil.which(binary):
                    available_binaries.append(binary)
            
            return {
                "available": len(available_binaries) > 0,
                "binaries": available_binaries
            }
            
        except Exception as e:
            logger.error(f"Wayland availability check error: {e}")
            return {"available": False, "error": str(e)}
    
    def _detect_graphics_driver(self) -> List[str]:
        """Detect graphics driver"""
        try:
            drivers = []
            
            try:
                result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=10)
                lines = result.stdout.lower()
                
                if 'nvidia' in lines:
                    drivers.append('nvidia')
                if 'amd' in lines or 'ati' in lines:
                    drivers.append('amd')
                if 'intel' in lines:
                    drivers.append('intel')
                if 'vmware' in lines:
                    drivers.append('vmware')
                if 'virtualbox' in lines:
                    drivers.append('vbox')
            except:
                pass
            
            return list(set(drivers)) if drivers else ['generic']
            
        except Exception as e:
            logger.error(f"Graphics driver detection error: {e}")
            return ['unknown']
    
    def _get_current_tty(self) -> str:
        """Get current TTY"""
        try:
            result = subprocess.run(['tty'], capture_output=True, text=True, timeout=5)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def _get_runlevel(self) -> str:
        """Get current runlevel"""
        try:
            result = subprocess.run(['runlevel'], capture_output=True, text=True, timeout=5)
            return result.stdout.strip()
        except:
            return "unknown"
    
    def _test_existing_display(self) -> bool:
        """Test if there's already a working display"""
        try:
            current_display = os.environ.get('DISPLAY', '')
            if current_display:
                logger.info(f"Testing existing display: {current_display}")
                
                try:
                    result = subprocess.run(['xdpyinfo'], capture_output=True, timeout=5)
                    if result.returncode == 0:
                        logger.info("Existing display is working")
                        self.current_display = current_display
                        return True
                except:
                    pass
            
            return False
            
        except Exception as e:
            logger.error(f"Existing display test error: {e}")
            return False
    
    def _prepare_display_environment(self):
        """Prepare environment variables and settings"""
        try:
            logger.info("Preparing display environment...")
            
            os.environ['DISPLAY'] = self.current_display
            os.environ['XAUTHORITY'] = os.path.expanduser('~/.Xauthority')
            
            # Create necessary directories
            x_dirs = [
                '/tmp/.X11-unix',
                '/tmp/.ICE-unix',
                os.path.expanduser('~/.cache'),
                os.path.expanduser('~/.local/share')
            ]
            
            for directory in x_dirs:
                os.makedirs(directory, exist_ok=True)
                try:
                    if directory.startswith('/tmp'):
                        os.chmod(directory, 0o1777)
                    else:
                        os.chmod(directory, 0o755)
                except:
                    pass
            
            logger.info("Display environment prepared")
            
        except Exception as e:
            logger.error(f"Environment preparation error: {e}")
    
    def _setup_tinycore_display(self) -> bool:
        """Setup display specifically for Tiny Core Linux"""
        try:
            logger.info("Setting up display for Tiny Core Linux...")
            
            tc_methods = [
                self._start_tc_x_with_startx,
                self._start_tc_x_with_xinit,
                self._start_tc_x_direct
            ]
            
            for method in tc_methods:
                try:
                    logger.info(f"Trying method: {method.__name__}")
                    if method():
                        logger.info(f"Success with method: {method.__name__}")
                        return True
                    time.sleep(2)
                except Exception as e:
                    logger.warning(f"Method {method.__name__} failed: {e}")
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Tiny Core display setup error: {e}")
            return False
    
    def _start_tc_x_with_startx(self) -> bool:
        """Start X using startx (TC preferred method)"""
        try:
            if not shutil.which('startx'):
                return False
            
            self._cleanup_x_processes()
            
            xinitrc_path = os.path.expanduser('~/.xinitrc')
            if not os.path.exists(xinitrc_path):
                with open(xinitrc_path, 'w') as f:
                    f.write('#!/bin/sh\n')
                    f.write('xset -dpms\n')
                    f.write('xset s off\n')
                    f.write('exec flwm &\n')
                    f.write('wait\n')
                os.chmod(xinitrc_path, 0o755)
            
            cmd = ['startx', '--', self.current_display, '-nolisten', 'tcp']
            
            self.x_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )
            
            return self._wait_for_x_server()
            
        except Exception as e:
            logger.error(f"startx method error: {e}")
            return False
    
    def _start_tc_x_with_xinit(self) -> bool:
        """Start X using xinit"""
        try:
            if not shutil.which('xinit'):
                return False
            
            self._cleanup_x_processes()
            
            cmd = ['xinit', '--', f'/usr/bin/X', self.current_display, '-nolisten', 'tcp']
            
            self.x_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )
            
            return self._wait_for_x_server(timeout=10)
            
        except Exception as e:
            logger.error(f"xinit method error: {e}")
            return False
    
    def _start_tc_x_direct(self) -> bool:
        """Start X server directly"""
        try:
            x_binary = shutil.which('Xorg') or shutil.which('X')
            if not x_binary:
                return False
            
            self._cleanup_x_processes()
            
            cmd = [
                x_binary, self.current_display,
                '-nolisten', 'tcp', '-nolisten', 'local',
                '-noreset', '-auth', os.path.expanduser('~/.Xauthority')
            ]
            
            self.x_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )
            
            if self._wait_for_x_server():
                self._start_window_manager()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Direct X start error: {e}")
            return False
    
    def _setup_generic_display(self) -> bool:
        """Setup display for generic Linux distributions"""
        try:
            logger.info("Setting up display for generic Linux...")
            
            if shutil.which('startx'):
                self.x_process = subprocess.Popen(
                    ['startx', '--', self.current_display, '-nolisten', 'tcp'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                return self._wait_for_x_server()
            
            return False
            
        except Exception as e:
            logger.error(f"Generic display setup error: {e}")
            return False
    
    def _try_fallback_display_methods(self) -> bool:
        """Try various fallback display methods"""
        try:
            logger.info("Trying fallback display methods...")
            
            fallback_methods = [
                self._try_xvfb,
                self._try_different_displays
            ]
            
            for method in fallback_methods:
                try:
                    if method():
                        return True
                except Exception as e:
                    logger.warning(f"Fallback method failed: {e}")
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Fallback methods error: {e}")
            return False
    
    def _try_xvfb(self) -> bool:
        """Try Xvfb (Virtual Framebuffer)"""
        try:
            if not shutil.which('Xvfb'):
                return False
            
            self._cleanup_x_processes()
            
            cmd = [
                'Xvfb', self.current_display,
                '-screen', '0', '1024x768x24',
                '-pixdepths', '3', '8', '15', '16', '24', '32'
            ]
            
            self.x_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            
            if self._wait_for_x_server():
                self._start_window_manager()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Xvfb error: {e}")
            return False
    
    def _try_different_displays(self) -> bool:
        """Try different display numbers"""
        try:
            for display_num in self.backup_displays:
                try:
                    self.current_display = display_num
                    os.environ['DISPLAY'] = display_num
                    
                    x_binary = shutil.which('Xorg') or shutil.which('X')
                    if x_binary:
                        cmd = [x_binary, display_num, '-nolisten', 'tcp']
                        
                        self.x_process = subprocess.Popen(
                            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                        )
                        
                        if self._wait_for_x_server(timeout=10):
                            self._start_window_manager()
                            return True
                        
                        self._cleanup_x_processes()
                
                except Exception as e:
                    logger.warning(f"Display {display_num} failed: {e}")
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Different displays error: {e}")
            return False
    
    def _wait_for_x_server(self, timeout: int = 30) -> bool:
        """Wait for X server to become ready"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    result = subprocess.run(
                        ['xdpyinfo', '-display', self.current_display],
                        capture_output=True, timeout=3
                    )
                    if result.returncode == 0:
                        return True
                except:
                    pass
                
                if self.x_process and self.x_process.poll() is not None:
                    return False
                
                time.sleep(1)
            
            return False
            
        except Exception as e:
            logger.error(f"Wait for X server error: {e}")
            return False
    
    def _start_window_manager(self):
        """Start a window manager"""
        try:
            wm_list = ['flwm', 'jwm', 'openbox', 'icewm', 'twm']
            
            for wm in wm_list:
                if shutil.which(wm):
                    env = os.environ.copy()
                    env['DISPLAY'] = self.current_display
                    
                    subprocess.Popen(
                        [wm], env=env,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
                    
                    time.sleep(2)
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Window manager start error: {e}")
            return False
    
    def _cleanup_x_processes(self):
        """Clean up existing X processes"""
        try:
            x_processes = ['X', 'Xorg', 'Xvfb', 'Xnest']
            
            for proc_name in x_processes:
                try:
                    subprocess.run(['pkill', '-f', proc_name], 
                                 capture_output=True, timeout=5)
                except:
                    pass
            
            x_sockets = [f'/tmp/.X11-unix/X{i}' for i in range(0, 10)]
            for socket_path in x_sockets:
                try:
                    if os.path.exists(socket_path):
                        os.remove(socket_path)
                except:
                    pass
            
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"X processes cleanup error: {e}")
    
    def _verify_display_setup(self) -> bool:
        """Verify that display setup is working correctly"""
        try:
            result = subprocess.run(
                ['xdpyinfo', '-display', self.current_display],
                capture_output=True, timeout=5
            )
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Display verification error: {e}")
            return False
    
    def _parse_xdpyinfo_output(self, output: str) -> Dict[str, Any]:
        """Parse xdpyinfo output to extract display information"""
        try:
            info = {
                "display": self.current_display,
                "mode": "x11"
            }
            
            lines = output.split('\n')
            for line in lines:
                if 'dimensions:' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        resolution = parts[1]
                        if 'x' in resolution:
                            w, h = resolution.split('x')
                            info['width'] = int(w)
                            info['height'] = int(h.split()[0])
                
                elif 'depth of root window:' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        info['depth'] = int(parts[4])
                
                elif 'number of screens:' in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        info['screens'] = int(parts[3])
            
            return info
            
        except Exception as e:
            logger.error(f"Parse xdpyinfo error: {e}")
            return {"error": str(e)}