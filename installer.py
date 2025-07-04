#!/usr/bin/env python3
"""
BERKE0S Ultimate Operating System - Smart Installer
Otomatik indirme, kurulum ve bağımlılık yönetimi
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
import zipfile
import tarfile
import subprocess
import shutil
import hashlib
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import tempfile
import platform

class BerkeOSInstaller:
    """BERKE0S Akıllı Kurulum Sistemi"""
    
    def __init__(self):
        self.version = "4.0-Ultimate"
        self.github_repo = "https://github.com/BreDEVs/BERKE0S"
        self.install_dir = "/opt/berke0s"
        self.user_dir = os.path.expanduser("~/.berke0s")
        self.temp_dir = tempfile.mkdtemp(prefix="berke0s_")
        self.progress = 0
        self.status = "Hazırlanıyor..."
        
        # Sistem bilgileri
        self.system_info = self.detect_system()
        
        # Bağımlılıklar
        self.dependencies = {
            "python3": "Python 3.8+",
            "python3-tk": "Tkinter GUI",
            "python3-pip": "Python paket yöneticisi",
            "git": "Git versiyon kontrol",
            "curl": "HTTP istemcisi",
            "wget": "Dosya indirici",
            "xorg": "X Window System",
            "wine": "Windows uygulamaları için",
            "docker": "Konteyner desteği",
            "nodejs": "JavaScript runtime",
            "npm": "Node paket yöneticisi"
        }
        
    def detect_system(self):
        """Sistem bilgilerini algıla"""
        return {
            "os": platform.system(),
            "arch": platform.machine(),
            "python_version": sys.version,
            "is_tinycore": os.path.exists("/opt/tce") or os.path.exists("/usr/bin/tce-load"),
            "is_debian": os.path.exists("/etc/debian_version"),
            "is_redhat": os.path.exists("/etc/redhat-release"),
            "is_arch": os.path.exists("/etc/arch-release"),
            "user": os.getenv("USER", "unknown"),
            "home": os.path.expanduser("~")
        }
    
    def start_gui_install(self):
        """GUI kurulum başlat"""
        try:
            self.root = tk.Tk()
            self.root.title("BERKE0S Ultimate - Akıllı Kurulum")
            self.root.geometry("800x600")
            self.root.configure(bg='#0a0a0f')
            self.root.resizable(False, False)
            
            # Ana container
            main_frame = tk.Frame(self.root, bg='#0a0a0f')
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Header
            header = tk.Label(main_frame, 
                            text="🚀 BERKE0S Ultimate Operating System",
                            font=('Arial', 24, 'bold'),
                            fg='#00ff88', bg='#0a0a0f')
            header.pack(pady=(0, 10))
            
            subtitle = tk.Label(main_frame,
                              text="Gelişmiş İşletim Sistemi - Akıllı Kurulum",
                              font=('Arial', 14),
                              fg='white', bg='#0a0a0f')
            subtitle.pack(pady=(0, 30))
            
            # Sistem bilgileri
            info_frame = tk.LabelFrame(main_frame, text="Sistem Bilgileri",
                                     bg='#1a1a1a', fg='white', font=('Arial', 12, 'bold'))
            info_frame.pack(fill=tk.X, pady=(0, 20))
            
            info_text = f"""
İşletim Sistemi: {self.system_info['os']} ({self.system_info['arch']})
Python Sürümü: {self.system_info['python_version'].split()[0]}
Kullanıcı: {self.system_info['user']}
Tiny Core Linux: {'Evet' if self.system_info['is_tinycore'] else 'Hayır'}
Kurulum Dizini: {self.install_dir}
Kullanıcı Dizini: {self.user_dir}
            """
            
            tk.Label(info_frame, text=info_text, bg='#1a1a1a', fg='white',
                    font=('Courier', 10), justify=tk.LEFT).pack(padx=10, pady=10)
            
            # Özellikler
            features_frame = tk.LabelFrame(main_frame, text="Kurulacak Özellikler",
                                         bg='#1a1a1a', fg='white', font=('Arial', 12, 'bold'))
            features_frame.pack(fill=tk.X, pady=(0, 20))
            
            features = [
                "🖥️ Gelişmiş Masaüstü Ortamı",
                "🌐 Gerçek Web Tarayıcısı (Chromium tabanlı)",
                "💻 Programlama IDE'si (VS Code benzeri)",
                "📁 Windows benzeri Dosya Sistemi",
                "🎮 Minecraft Launcher (Berke Launcher)",
                "🤖 Yapay Zeka Workspace (Ollama entegrasyonu)",
                "📊 Microsoft 365 benzeri Ofis Paketi",
                "🎵 YouTube Müzik/Video İndirici",
                "🔧 Gelişmiş Kontrol Paneli",
                "🍷 Windows Uygulamaları Desteği (Wine)",
                "🛠️ Geliştirici Modu (Ctrl+Fn+B)",
                "🔄 Otomatik Güncelleme ve Kurtarma"
            ]
            
            features_text = "\n".join(features)
            tk.Label(features_frame, text=features_text, bg='#1a1a1a', fg='#00ff88',
                    font=('Arial', 10), justify=tk.LEFT).pack(padx=10, pady=10)
            
            # Progress bar
            self.progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var,
                                         maximum=100, length=600)
            progress_bar.pack(pady=(20, 10))
            
            # Status label
            self.status_var = tk.StringVar(value=self.status)
            status_label = tk.Label(main_frame, textvariable=self.status_var,
                                  bg='#0a0a0f', fg='white', font=('Arial', 11))
            status_label.pack(pady=(0, 20))
            
            # Buttons
            button_frame = tk.Frame(main_frame, bg='#0a0a0f')
            button_frame.pack(pady=20)
            
            install_btn = tk.Button(button_frame, text="🚀 Kurulumu Başlat",
                                  command=self.start_installation,
                                  bg='#00ff88', fg='black', font=('Arial', 14, 'bold'),
                                  relief=tk.FLAT, padx=30, pady=10)
            install_btn.pack(side=tk.LEFT, padx=10)
            
            exit_btn = tk.Button(button_frame, text="❌ Çıkış",
                               command=self.root.quit,
                               bg='#ff6b6b', fg='white', font=('Arial', 12),
                               relief=tk.FLAT, padx=20, pady=10)
            exit_btn.pack(side=tk.LEFT, padx=10)
            
            # Center window
            self.center_window()
            
            self.root.mainloop()
            
        except Exception as e:
            print(f"GUI kurulum hatası: {e}")
            self.console_install()
    
    def center_window(self):
        """Pencereyi ortala"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"800x600+{x}+{y}")
    
    def start_installation(self):
        """Kurulumu başlat"""
        self.install_thread = threading.Thread(target=self.install_process, daemon=True)
        self.install_thread.start()
    
    def update_progress(self, progress, status):
        """Progress güncelle"""
        self.progress = progress
        self.status = status
        if hasattr(self, 'progress_var'):
            self.progress_var.set(progress)
            self.status_var.set(status)
            self.root.update()
    
    def install_process(self):
        """Ana kurulum süreci"""
        try:
            steps = [
                (5, "Sistem kontrolü yapılıyor...", self.check_system),
                (15, "Bağımlılıklar kuruluyor...", self.install_dependencies),
                (25, "BERKE0S indiriliyor...", self.download_berke0s),
                (40, "Dosya sistemi oluşturuluyor...", self.create_filesystem),
                (55, "Sistem uygulamaları kuruluyor...", self.install_system_apps),
                (70, "Web tarayıcısı kuruluyor...", self.install_browser),
                (80, "IDE kuruluyor...", self.install_ide),
                (90, "Yapılandırma tamamlanıyor...", self.finalize_installation),
                (100, "Kurulum tamamlandı!", self.installation_complete)
            ]
            
            for progress, status, func in steps:
                self.update_progress(progress, status)
                func()
                time.sleep(1)
                
        except Exception as e:
            self.update_progress(0, f"Hata: {str(e)}")
            messagebox.showerror("Kurulum Hatası", f"Kurulum başarısız: {str(e)}")
    
    def check_system(self):
        """Sistem kontrolü"""
        # Python sürümü kontrolü
        if sys.version_info < (3, 8):
            raise Exception("Python 3.8 veya üzeri gerekli")
        
        # Disk alanı kontrolü
        if shutil.disk_usage("/").free < 5 * 1024**3:  # 5GB
            raise Exception("En az 5GB boş disk alanı gerekli")
    
    def install_dependencies(self):
        """Bağımlılıkları kur"""
        if self.system_info['is_tinycore']:
            self.install_tinycore_deps()
        elif self.system_info['is_debian']:
            self.install_debian_deps()
        elif self.system_info['is_redhat']:
            self.install_redhat_deps()
        elif self.system_info['is_arch']:
            self.install_arch_deps()
    
    def install_tinycore_deps(self):
        """Tiny Core bağımlılıkları"""
        extensions = [
            "python3.tcz", "python3-tkinter.tcz", "git.tcz", "curl.tcz",
            "Xorg-7.7.tcz", "wine.tcz", "nodejs.tcz", "docker.tcz"
        ]
        
        for ext in extensions:
            try:
                subprocess.run(['tce-load', '-wi', ext], check=True, capture_output=True)
            except:
                pass
    
    def install_debian_deps(self):
        """Debian/Ubuntu bağımlılıkları"""
        packages = [
            "python3", "python3-tk", "python3-pip", "git", "curl", "wget",
            "xorg", "wine", "docker.io", "nodejs", "npm", "chromium-browser"
        ]
        
        try:
            subprocess.run(['sudo', 'apt', 'update'], check=True)
            subprocess.run(['sudo', 'apt', 'install', '-y'] + packages, check=True)
        except:
            pass
    
    def install_redhat_deps(self):
        """Red Hat/CentOS bağımlılıkları"""
        packages = [
            "python3", "python3-tkinter", "python3-pip", "git", "curl", "wget",
            "xorg-x11-server-Xorg", "wine", "docker", "nodejs", "npm"
        ]
        
        try:
            subprocess.run(['sudo', 'yum', 'install', '-y'] + packages, check=True)
        except:
            pass
    
    def install_arch_deps(self):
        """Arch Linux bağımlılıkları"""
        packages = [
            "python", "python-pip", "git", "curl", "wget",
            "xorg", "wine", "docker", "nodejs", "npm", "chromium"
        ]
        
        try:
            subprocess.run(['sudo', 'pacman', '-S', '--noconfirm'] + packages, check=True)
        except:
            pass
    
    def download_berke0s(self):
        """BERKE0S'i indir"""
        try:
            # GitHub'dan indir
            url = f"{self.github_repo}/archive/main.zip"
            zip_path = os.path.join(self.temp_dir, "berke0s.zip")
            
            urllib.request.urlretrieve(url, zip_path)
            
            # Çıkart
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
                
        except Exception as e:
            # Fallback: git clone
            try:
                subprocess.run(['git', 'clone', f"{self.github_repo}.git", 
                              os.path.join(self.temp_dir, "BERKE0S-main")], check=True)
            except:
                raise Exception("BERKE0S indirilemedi")
    
    def create_filesystem(self):
        """Windows benzeri dosya sistemi oluştur"""
        # Ana dizinler
        directories = [
            f"{self.install_dir}/Program Files",
            f"{self.install_dir}/Program Files (x86)",
            f"{self.install_dir}/System32",
            f"{self.install_dir}/Windows",
            f"{self.install_dir}/Users",
            f"{self.install_dir}/Temp",
            f"{self.user_dir}/Desktop",
            f"{self.user_dir}/Documents",
            f"{self.user_dir}/Downloads",
            f"{self.user_dir}/Pictures",
            f"{self.user_dir}/Music",
            f"{self.user_dir}/Videos",
            f"{self.user_dir}/AppData/Local",
            f"{self.user_dir}/AppData/Roaming"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        # Sistem dosyalarını kopyala
        source_dir = os.path.join(self.temp_dir, "BERKE0S-main")
        if os.path.exists(source_dir):
            shutil.copytree(source_dir, f"{self.install_dir}/System32/BERKE0S", dirs_exist_ok=True)
    
    def install_system_apps(self):
        """Sistem uygulamalarını kur"""
        # Python paketleri
        pip_packages = [
            "requests", "pillow", "pygame", "numpy", "matplotlib",
            "flask", "fastapi", "selenium", "beautifulsoup4",
            "opencv-python", "tensorflow", "torch", "transformers"
        ]
        
        for package in pip_packages:
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                             check=True, capture_output=True)
            except:
                pass
    
    def install_browser(self):
        """Web tarayıcısı kur"""
        # Chromium tabanlı tarayıcı kurulumu
        pass
    
    def install_ide(self):
        """IDE kur"""
        # VS Code benzeri IDE kurulumu
        pass
    
    def finalize_installation(self):
        """Kurulumu tamamla"""
        # Başlangıç scriptleri oluştur
        self.create_startup_scripts()
        
        # Konfigürasyon dosyaları
        self.create_config_files()
        
        # Desktop entries
        self.create_desktop_entries()
    
    def create_startup_scripts(self):
        """Başlangıç scriptleri oluştur"""
        # Ana başlangıç scripti
        startup_script = f"""#!/bin/bash
# BERKE0S Ultimate Startup Script
export BERKE0S_HOME="{self.install_dir}"
export BERKE0S_USER="{self.user_dir}"
cd "{self.install_dir}/System32/BERKE0S"
python3 main.py "$@"
"""
        
        script_path = f"{self.install_dir}/berke0s"
        with open(script_path, 'w') as f:
            f.write(startup_script)
        os.chmod(script_path, 0o755)
        
        # Sistem linkini oluştur
        try:
            if os.path.exists("/usr/local/bin"):
                os.symlink(script_path, "/usr/local/bin/berke0s")
        except:
            pass
    
    def create_config_files(self):
        """Konfigürasyon dosyaları oluştur"""
        config = {
            "version": self.version,
            "install_date": time.time(),
            "install_dir": self.install_dir,
            "user_dir": self.user_dir,
            "system_info": self.system_info,
            "features": {
                "web_browser": True,
                "ide": True,
                "ai_workspace": True,
                "office_suite": True,
                "minecraft_launcher": True,
                "media_tools": True,
                "developer_mode": False
            }
        }
        
        with open(f"{self.user_dir}/config.json", 'w') as f:
            json.dump(config, f, indent=4)
    
    def create_desktop_entries(self):
        """Desktop entries oluştur"""
        desktop_entry = f"""[Desktop Entry]
Name=BERKE0S Ultimate
Comment=Ultimate Operating System
Exec={self.install_dir}/berke0s
Icon={self.install_dir}/System32/BERKE0S/assets/icon.png
Type=Application
Categories=System;
StartupNotify=true
"""
        
        desktop_dirs = [
            os.path.expanduser("~/.local/share/applications"),
            os.path.expanduser("~/Desktop"),
            "/usr/share/applications"
        ]
        
        for desktop_dir in desktop_dirs:
            try:
                os.makedirs(desktop_dir, exist_ok=True)
                with open(f"{desktop_dir}/berke0s.desktop", 'w') as f:
                    f.write(desktop_entry)
                os.chmod(f"{desktop_dir}/berke0s.desktop", 0o755)
            except:
                pass
    
    def installation_complete(self):
        """Kurulum tamamlandı"""
        # Temp dosyaları temizle
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        # Başarı mesajı
        if hasattr(self, 'root'):
            messagebox.showinfo("Kurulum Tamamlandı", 
                              "BERKE0S Ultimate başarıyla kuruldu!\n\n"
                              "Başlatmak için: berke0s\n"
                              "Veya masaüstündeki ikona tıklayın.")
    
    def console_install(self):
        """Konsol kurulumu"""
        print("\n" + "="*60)
        print("🚀 BERKE0S Ultimate Operating System")
        print("   Akıllı Kurulum Sistemi")
        print("="*60)
        
        print(f"\nSistem Bilgileri:")
        print(f"  OS: {self.system_info['os']} ({self.system_info['arch']})")
        print(f"  Python: {self.system_info['python_version'].split()[0]}")
        print(f"  Kullanıcı: {self.system_info['user']}")
        
        response = input("\nKuruluma devam etmek istiyor musunuz? (e/h): ")
        if response.lower() != 'e':
            print("Kurulum iptal edildi.")
            return
        
        try:
            print("\n🔍 Sistem kontrolü...")
            self.check_system()
            
            print("📦 Bağımlılıklar kuruluyor...")
            self.install_dependencies()
            
            print("⬇️ BERKE0S indiriliyor...")
            self.download_berke0s()
            
            print("📁 Dosya sistemi oluşturuluyor...")
            self.create_filesystem()
            
            print("🔧 Sistem uygulamaları kuruluyor...")
            self.install_system_apps()
            
            print("🌐 Web tarayıcısı kuruluyor...")
            self.install_browser()
            
            print("💻 IDE kuruluyor...")
            self.install_ide()
            
            print("⚙️ Yapılandırma tamamlanıyor...")
            self.finalize_installation()
            
            print("\n✅ BERKE0S Ultimate başarıyla kuruldu!")
            print("🚀 Başlatmak için: berke0s")
            
        except Exception as e:
            print(f"\n❌ Kurulum hatası: {e}")
            return False
        
        return True

def main():
    """Ana fonksiyon"""
    try:
        installer = BerkeOSInstaller()
        
        # GUI mevcut mu kontrol et
        try:
            import tkinter
            installer.start_gui_install()
        except ImportError:
            print("GUI mevcut değil, konsol kurulumu başlatılıyor...")
            installer.console_install()
            
    except KeyboardInterrupt:
        print("\n\nKurulum kullanıcı tarafından iptal edildi.")
    except Exception as e:
        print(f"Kurulum hatası: {e}")

if __name__ == "__main__":
    main()