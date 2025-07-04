#!/usr/bin/env python3
"""
BERKE0S Ultimate Operating System V4.0
Tam özellikli işletim sistemi deneyimi
"""

import sys
import os
import json
import logging
import argparse
import threading
import time
from pathlib import Path

# Sistem yollarını ayarla
BERKE0S_HOME = os.environ.get('BERKE0S_HOME', '/opt/berke0s')
BERKE0S_USER = os.environ.get('BERKE0S_USER', os.path.expanduser('~/.berke0s'))

sys.path.insert(0, os.path.join(BERKE0S_HOME, 'System32', 'BERKE0S', 'src'))

# Core modülleri import et
from core.config import ConfigManager
from core.logger import setup_logging
from core.window_manager import UltimateWindowManager
from core.installer import InstallationWizard
from core.developer_mode import DeveloperMode
from core.recovery_system import RecoverySystem

# Sistem uygulamaları
from apps.file_manager import UltimateFileManager
from apps.web_browser import BerkeWebBrowser
from apps.ide import BerkeIDE
from apps.control_panel import ControlPanel
from apps.minecraft_launcher import BerkeLauncher
from apps.ai_workspace import AIWorkspace
from apps.office_suite import BerkeOffice
from apps.media_center import MediaCenter
from apps.terminal import UltimateTerminal
from apps.disk_manager import DiskManager

class BerkeOSUltimate:
    """BERKE0S Ultimate Ana Sistem Sınıfı"""
    
    def __init__(self):
        self.version = "4.0-Ultimate"
        self.config_manager = ConfigManager()
        self.logger = setup_logging()
        self.window_manager = None
        self.developer_mode = DeveloperMode()
        self.recovery_system = RecoverySystem()
        self.running = False
        
        # Sistem durumu
        self.system_status = {
            "boot_time": time.time(),
            "uptime": 0,
            "memory_usage": 0,
            "cpu_usage": 0,
            "disk_usage": 0,
            "network_status": "disconnected",
            "active_apps": [],
            "background_services": []
        }
        
        # Uygulamalar registry
        self.applications = {}
        self.services = {}
        
        self.logger.info(f"BERKE0S Ultimate {self.version} başlatılıyor...")
    
    def parse_arguments(self):
        """Komut satırı argümanlarını parse et"""
        parser = argparse.ArgumentParser(
            description='BERKE0S Ultimate Operating System',
            prog='berke0s'
        )
        
        parser.add_argument('--version', action='version', 
                          version=f'BERKE0S Ultimate {self.version}')
        parser.add_argument('--debug', action='store_true', 
                          help='Debug modunda başlat')
        parser.add_argument('--safe-mode', action='store_true',
                          help='Güvenli modda başlat')
        parser.add_argument('--recovery', action='store_true',
                          help='Kurtarma modunda başlat')
        parser.add_argument('--install', action='store_true',
                          help='Kurulum sihirbazını başlat')
        parser.add_argument('--developer', action='store_true',
                          help='Geliştirici modunu etkinleştir')
        parser.add_argument('--headless', action='store_true',
                          help='Headless modda çalıştır')
        parser.add_argument('--config-dir', 
                          help='Özel config dizini')
        
        return parser.parse_args()
    
    def initialize_system(self, args):
        """Sistemi başlat"""
        try:
            self.logger.info("Sistem başlatılıyor...")
            
            # Konfigürasyon yükle
            if args.config_dir:
                self.config_manager.set_config_dir(args.config_dir)
            
            # Kurulum kontrolü
            if args.install or not self.config_manager.is_installed():
                self.logger.info("Kurulum sihirbazı başlatılıyor...")
                installer = InstallationWizard()
                if not installer.start_installation():
                    return False
            
            # Kurtarma modu
            if args.recovery:
                return self.recovery_system.start_recovery_mode()
            
            # Geliştirici modu
            if args.developer:
                if not self.developer_mode.authenticate():
                    self.logger.warning("Geliştirici modu kimlik doğrulaması başarısız")
                    return False
                self.developer_mode.enable()
            
            # Sistem servisleri başlat
            self.start_system_services()
            
            # Uygulamaları kaydet
            self.register_applications()
            
            # Window manager başlat
            if not args.headless:
                self.window_manager = UltimateWindowManager(self)
                
            self.running = True
            self.logger.info("BERKE0S Ultimate başarıyla başlatıldı")
            return True
            
        except Exception as e:
            self.logger.error(f"Sistem başlatma hatası: {e}")
            return False
    
    def start_system_services(self):
        """Sistem servislerini başlat"""
        services = [
            ("SystemMonitor", self.system_monitor_service),
            ("NetworkManager", self.network_manager_service),
            ("UpdateService", self.update_service),
            ("BackupService", self.backup_service),
            ("SecurityService", self.security_service),
            ("PerformanceOptimizer", self.performance_optimizer_service),
            ("AIAssistant", self.ai_assistant_service)
        ]
        
        for service_name, service_func in services:
            try:
                thread = threading.Thread(target=service_func, 
                                        daemon=True, name=service_name)
                thread.start()
                self.services[service_name] = thread
                self.logger.info(f"Servis başlatıldı: {service_name}")
            except Exception as e:
                self.logger.error(f"Servis başlatma hatası {service_name}: {e}")
    
    def register_applications(self):
        """Uygulamaları kaydet"""
        apps = {
            "file_manager": UltimateFileManager,
            "web_browser": BerkeWebBrowser,
            "ide": BerkeIDE,
            "control_panel": ControlPanel,
            "minecraft_launcher": BerkeLauncher,
            "ai_workspace": AIWorkspace,
            "office_suite": BerkeOffice,
            "media_center": MediaCenter,
            "terminal": UltimateTerminal,
            "disk_manager": DiskManager
        }
        
        for app_name, app_class in apps.items():
            self.applications[app_name] = app_class
            self.logger.debug(f"Uygulama kaydedildi: {app_name}")
    
    def launch_application(self, app_name, *args, **kwargs):
        """Uygulama başlat"""
        try:
            if app_name in self.applications:
                app_class = self.applications[app_name]
                app_instance = app_class(self, *args, **kwargs)
                app_instance.show()
                
                self.system_status["active_apps"].append({
                    "name": app_name,
                    "instance": app_instance,
                    "start_time": time.time()
                })
                
                self.logger.info(f"Uygulama başlatıldı: {app_name}")
                return app_instance
            else:
                self.logger.error(f"Bilinmeyen uygulama: {app_name}")
                return None
        except Exception as e:
            self.logger.error(f"Uygulama başlatma hatası {app_name}: {e}")
            return None
    
    def system_monitor_service(self):
        """Sistem izleme servisi"""
        import psutil
        
        while self.running:
            try:
                # Sistem metriklerini güncelle
                self.system_status.update({
                    "uptime": time.time() - self.system_status["boot_time"],
                    "memory_usage": psutil.virtual_memory().percent,
                    "cpu_usage": psutil.cpu_percent(interval=1),
                    "disk_usage": psutil.disk_usage('/').percent
                })
                
                # Kritik durumları kontrol et
                if self.system_status["memory_usage"] > 90:
                    self.logger.warning("Yüksek bellek kullanımı!")
                
                if self.system_status["cpu_usage"] > 95:
                    self.logger.warning("Yüksek CPU kullanımı!")
                
                time.sleep(5)
                
            except Exception as e:
                self.logger.error(f"Sistem izleme hatası: {e}")
                time.sleep(30)
    
    def network_manager_service(self):
        """Ağ yönetimi servisi"""
        import socket
        
        while self.running:
            try:
                # İnternet bağlantısını kontrol et
                socket.create_connection(("8.8.8.8", 53), timeout=5)
                self.system_status["network_status"] = "connected"
            except OSError:
                self.system_status["network_status"] = "disconnected"
            
            time.sleep(30)
    
    def update_service(self):
        """Güncelleme servisi"""
        while self.running:
            try:
                # Güncellemeleri kontrol et
                if self.config_manager.get("system.auto_updates", True):
                    self.check_for_updates()
                
                time.sleep(3600)  # Her saat kontrol et
                
            except Exception as e:
                self.logger.error(f"Güncelleme servisi hatası: {e}")
                time.sleep(3600)
    
    def backup_service(self):
        """Yedekleme servisi"""
        while self.running:
            try:
                if self.config_manager.get("system.auto_backup", True):
                    self.create_system_backup()
                
                time.sleep(86400)  # Günlük yedekleme
                
            except Exception as e:
                self.logger.error(f"Yedekleme servisi hatası: {e}")
                time.sleep(86400)
    
    def security_service(self):
        """Güvenlik servisi"""
        while self.running:
            try:
                # Güvenlik taraması yap
                self.perform_security_scan()
                
                time.sleep(1800)  # 30 dakikada bir
                
            except Exception as e:
                self.logger.error(f"Güvenlik servisi hatası: {e}")
                time.sleep(1800)
    
    def performance_optimizer_service(self):
        """Performans optimizasyon servisi"""
        while self.running:
            try:
                # Sistem performansını optimize et
                self.optimize_system_performance()
                
                time.sleep(300)  # 5 dakikada bir
                
            except Exception as e:
                self.logger.error(f"Performans optimizasyon hatası: {e}")
                time.sleep(300)
    
    def ai_assistant_service(self):
        """AI asistan servisi"""
        while self.running:
            try:
                # AI asistan görevlerini işle
                self.process_ai_tasks()
                
                time.sleep(60)  # Dakikada bir
                
            except Exception as e:
                self.logger.error(f"AI asistan hatası: {e}")
                time.sleep(60)
    
    def check_for_updates(self):
        """Güncellemeleri kontrol et"""
        try:
            # GitHub'dan son sürümü kontrol et
            import urllib.request
            import json
            
            url = "https://api.github.com/repos/BreDEVs/BERKE0S/releases/latest"
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read())
                latest_version = data["tag_name"]
                
                if latest_version != self.version:
                    self.logger.info(f"Yeni sürüm mevcut: {latest_version}")
                    # Güncelleme bildirimi gönder
                    
        except Exception as e:
            self.logger.error(f"Güncelleme kontrolü hatası: {e}")
    
    def create_system_backup(self):
        """Sistem yedeği oluştur"""
        try:
            backup_dir = os.path.join(BERKE0S_USER, "Backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"berke0s_backup_{timestamp}.tar.gz")
            
            # Önemli dosyaları yedekle
            import tarfile
            with tarfile.open(backup_file, "w:gz") as tar:
                tar.add(BERKE0S_USER, arcname="user_data")
                tar.add(os.path.join(BERKE0S_HOME, "System32", "BERKE0S", "config"), 
                       arcname="system_config")
            
            self.logger.info(f"Sistem yedeği oluşturuldu: {backup_file}")
            
        except Exception as e:
            self.logger.error(f"Yedekleme hatası: {e}")
    
    def perform_security_scan(self):
        """Güvenlik taraması yap"""
        try:
            # Şüpheli dosyaları tara
            # Ağ bağlantılarını kontrol et
            # Sistem bütünlüğünü doğrula
            pass
        except Exception as e:
            self.logger.error(f"Güvenlik taraması hatası: {e}")
    
    def optimize_system_performance(self):
        """Sistem performansını optimize et"""
        try:
            # Bellek temizliği
            import gc
            gc.collect()
            
            # Geçici dosyaları temizle
            temp_dirs = ["/tmp", os.path.join(BERKE0S_USER, "Temp")]
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    for file in os.listdir(temp_dir):
                        try:
                            file_path = os.path.join(temp_dir, file)
                            if os.path.isfile(file_path):
                                # 1 günden eski dosyaları sil
                                if time.time() - os.path.getmtime(file_path) > 86400:
                                    os.remove(file_path)
                        except:
                            pass
            
        except Exception as e:
            self.logger.error(f"Performans optimizasyonu hatası: {e}")
    
    def process_ai_tasks(self):
        """AI görevlerini işle"""
        try:
            # AI asistan görevleri
            # Kullanıcı davranışlarını analiz et
            # Sistem önerilerini hazırla
            pass
        except Exception as e:
            self.logger.error(f"AI görev işleme hatası: {e}")
    
    def handle_keyboard_shortcut(self, key_combination):
        """Klavye kısayollarını işle"""
        if key_combination == "Ctrl+Fn+B":
            # Geliştirici modu toggle
            if self.developer_mode.is_enabled():
                self.developer_mode.disable()
            else:
                if self.developer_mode.authenticate():
                    self.developer_mode.enable()
    
    def shutdown(self):
        """Sistemi kapat"""
        try:
            self.logger.info("BERKE0S Ultimate kapatılıyor...")
            
            # Çalışan uygulamaları kapat
            for app_info in self.system_status["active_apps"]:
                try:
                    app_info["instance"].close()
                except:
                    pass
            
            # Servisleri durdur
            self.running = False
            
            # Son yedekleme
            if self.config_manager.get("system.backup_on_shutdown", True):
                self.create_system_backup()
            
            # Konfigürasyonu kaydet
            self.config_manager.save_config()
            
            self.logger.info("BERKE0S Ultimate başarıyla kapatıldı")
            
        except Exception as e:
            self.logger.error(f"Kapatma hatası: {e}")
    
    def run(self):
        """Ana çalışma döngüsü"""
        try:
            if self.window_manager:
                # GUI modda çalıştır
                self.window_manager.run()
            else:
                # Headless modda çalıştır
                self.logger.info("Headless modda çalışıyor...")
                while self.running:
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            self.logger.info("Kullanıcı tarafından durduruldu")
        except Exception as e:
            self.logger.error(f"Çalışma döngüsü hatası: {e}")
        finally:
            self.shutdown()

def main():
    """Ana giriş noktası"""
    try:
        # BERKE0S Ultimate başlat
        berke_os = BerkeOSUltimate()
        
        # Argümanları parse et
        args = berke_os.parse_arguments()
        
        # Sistemi başlat
        if berke_os.initialize_system(args):
            # Ana döngüyü çalıştır
            berke_os.run()
            return 0
        else:
            print("BERKE0S Ultimate başlatılamadı")
            return 1
            
    except Exception as e:
        print(f"Kritik hata: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())