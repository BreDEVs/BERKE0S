"""
BERKE0S Ultimate - Minecraft Launcher (Berke Launcher)
BERKE0S'e özel Minecraft başlatıcısı
"""

import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import threading
import urllib.request
import urllib.parse
import zipfile
import shutil
import time

class BerkeLauncher:
    """BERKE0S Minecraft Launcher"""
    
    def __init__(self, berke_os):
        self.berke_os = berke_os
        self.window = None
        self.minecraft_dir = os.path.join(os.path.expanduser("~/.berke0s"), "Minecraft")
        self.versions_dir = os.path.join(self.minecraft_dir, "versions")
        self.mods_dir = os.path.join(self.minecraft_dir, "mods")
        self.saves_dir = os.path.join(self.minecraft_dir, "saves")
        self.profiles_file = os.path.join(self.minecraft_dir, "profiles.json")
        
        # Launcher settings
        self.settings = {
            "java_path": self.find_java(),
            "memory_allocation": "2G",
            "window_width": 854,
            "window_height": 480,
            "fullscreen": False,
            "auto_update": True,
            "show_snapshots": False,
            "custom_resolution": False
        }
        
        # Available versions
        self.versions = {}
        self.profiles = self.load_profiles()
        self.current_profile = "default"
        
        # Download progress
        self.download_progress = 0
        self.downloading = False
        
        self.setup_directories()
    
    def setup_directories(self):
        """Gerekli dizinleri oluştur"""
        directories = [
            self.minecraft_dir,
            self.versions_dir,
            self.mods_dir,
            self.saves_dir,
            os.path.join(self.minecraft_dir, "assets"),
            os.path.join(self.minecraft_dir, "libraries"),
            os.path.join(self.minecraft_dir, "resourcepacks"),
            os.path.join(self.minecraft_dir, "shaderpacks")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def find_java(self):
        """Java yolunu bul"""
        java_paths = [
            "/usr/bin/java",
            "/usr/lib/jvm/default-java/bin/java",
            "/usr/lib/jvm/java-17-openjdk/bin/java",
            "/usr/lib/jvm/java-11-openjdk/bin/java",
            "/usr/lib/jvm/java-8-openjdk/bin/java"
        ]
        
        for path in java_paths:
            if os.path.exists(path):
                return path
        
        # Try to find java in PATH
        try:
            result = subprocess.run(['which', 'java'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return "java"  # Fallback
    
    def show(self):
        """Launcher'ı göster"""
        try:
            self.window = tk.Toplevel()
            self.window.title("🎮 Berke Launcher - Minecraft")
            self.window.geometry("900x600")
            self.window.configure(bg='#2b2b2b')
            
            self.create_launcher_interface()
            self.load_versions()
            
        except Exception as e:
            print(f"Minecraft Launcher hatası: {e}")
    
    def create_launcher_interface(self):
        """Launcher arayüzünü oluştur"""
        # Header
        self.create_header()
        
        # Main content
        self.create_main_content()
        
        # Footer
        self.create_footer()
    
    def create_header(self):
        """Header oluştur"""
        header_frame = tk.Frame(self.window, bg='#1e1e1e', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Logo and title
        title_frame = tk.Frame(header_frame, bg='#1e1e1e')
        title_frame.pack(expand=True)
        
        # Minecraft logo (text-based)
        logo_label = tk.Label(title_frame, text="⛏️", font=('Arial', 32),
                             bg='#1e1e1e', fg='#4CAF50')
        logo_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Title and subtitle
        text_frame = tk.Frame(title_frame, bg='#1e1e1e')
        text_frame.pack(side=tk.LEFT, padx=10)
        
        title_label = tk.Label(text_frame, text="Berke Launcher",
                              font=('Arial', 20, 'bold'),
                              bg='#1e1e1e', fg='white')
        title_label.pack(anchor='w')
        
        subtitle_label = tk.Label(text_frame, text="BERKE0S Minecraft Launcher",
                                 font=('Arial', 12),
                                 bg='#1e1e1e', fg='#888888')
        subtitle_label.pack(anchor='w')
        
        # User info
        user_frame = tk.Frame(header_frame, bg='#1e1e1e')
        user_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        user_label = tk.Label(user_frame, text="👤 Oyuncu",
                             font=('Arial', 12),
                             bg='#1e1e1e', fg='white')
        user_label.pack()
    
    def create_main_content(self):
        """Ana içerik alanını oluştur"""
        main_frame = tk.Frame(self.window, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left panel - Version and Profile selection
        left_panel = tk.Frame(main_frame, bg='#3a3a3a', width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        self.create_left_panel(left_panel)
        
        # Right panel - News and updates
        right_panel = tk.Frame(main_frame, bg='#3a3a3a')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_right_panel(right_panel)
    
    def create_left_panel(self, parent):
        """Sol panel oluştur"""
        # Profile selection
        profile_frame = tk.LabelFrame(parent, text="Profil", 
                                     bg='#3a3a3a', fg='white',
                                     font=('Arial', 12, 'bold'))
        profile_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.profile_var = tk.StringVar(value=self.current_profile)
        profile_combo = ttk.Combobox(profile_frame, textvariable=self.profile_var,
                                    values=list(self.profiles.keys()),
                                    state='readonly')
        profile_combo.pack(fill=tk.X, padx=10, pady=10)
        profile_combo.bind('<<ComboboxSelected>>', self.on_profile_change)
        
        # Profile management buttons
        profile_btn_frame = tk.Frame(profile_frame, bg='#3a3a3a')
        profile_btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(profile_btn_frame, text="➕ Yeni", command=self.new_profile,
                 bg='#4CAF50', fg='white', width=8).pack(side=tk.LEFT, padx=2)
        
        tk.Button(profile_btn_frame, text="✏️ Düzenle", command=self.edit_profile,
                 bg='#2196F3', fg='white', width=8).pack(side=tk.LEFT, padx=2)
        
        tk.Button(profile_btn_frame, text="🗑️ Sil", command=self.delete_profile,
                 bg='#f44336', fg='white', width=8).pack(side=tk.LEFT, padx=2)
        
        # Version selection
        version_frame = tk.LabelFrame(parent, text="Sürüm", 
                                     bg='#3a3a3a', fg='white',
                                     font=('Arial', 12, 'bold'))
        version_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.version_var = tk.StringVar()
        self.version_listbox = tk.Listbox(version_frame, height=8,
                                         bg='#2b2b2b', fg='white',
                                         selectbackground='#4CAF50')
        self.version_listbox.pack(fill=tk.X, padx=10, pady=10)
        
        # Version management buttons
        version_btn_frame = tk.Frame(version_frame, bg='#3a3a3a')
        version_btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(version_btn_frame, text="⬇️ İndir", command=self.download_version,
                 bg='#4CAF50', fg='white', width=10).pack(side=tk.LEFT, padx=2)
        
        tk.Button(version_btn_frame, text="🔄 Yenile", command=self.refresh_versions,
                 bg='#2196F3', fg='white', width=10).pack(side=tk.LEFT, padx=2)
        
        # Game settings
        settings_frame = tk.LabelFrame(parent, text="Oyun Ayarları", 
                                      bg='#3a3a3a', fg='white',
                                      font=('Arial', 12, 'bold'))
        settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Memory allocation
        tk.Label(settings_frame, text="RAM:", bg='#3a3a3a', fg='white').pack(anchor='w', padx=10)
        self.memory_var = tk.StringVar(value=self.settings["memory_allocation"])
        memory_combo = ttk.Combobox(settings_frame, textvariable=self.memory_var,
                                   values=["1G", "2G", "4G", "6G", "8G", "12G", "16G"],
                                   width=10)
        memory_combo.pack(anchor='w', padx=10, pady=5)
        
        # Resolution
        resolution_frame = tk.Frame(settings_frame, bg='#3a3a3a')
        resolution_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.custom_res_var = tk.BooleanVar(value=self.settings["custom_resolution"])
        tk.Checkbutton(resolution_frame, text="Özel Çözünürlük",
                      variable=self.custom_res_var,
                      bg='#3a3a3a', fg='white', selectcolor='#4CAF50',
                      command=self.toggle_custom_resolution).pack(anchor='w')
        
        res_input_frame = tk.Frame(settings_frame, bg='#3a3a3a')
        res_input_frame.pack(fill=tk.X, padx=10, pady=2)
        
        self.width_var = tk.StringVar(value=str(self.settings["window_width"]))
        self.height_var = tk.StringVar(value=str(self.settings["window_height"]))
        
        tk.Entry(res_input_frame, textvariable=self.width_var, width=8).pack(side=tk.LEFT)
        tk.Label(res_input_frame, text="x", bg='#3a3a3a', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Entry(res_input_frame, textvariable=self.height_var, width=8).pack(side=tk.LEFT)
        
        # Fullscreen
        self.fullscreen_var = tk.BooleanVar(value=self.settings["fullscreen"])
        tk.Checkbutton(settings_frame, text="Tam Ekran",
                      variable=self.fullscreen_var,
                      bg='#3a3a3a', fg='white', selectcolor='#4CAF50').pack(anchor='w', padx=10, pady=5)
    
    def create_right_panel(self, parent):
        """Sağ panel oluştur"""
        # News and updates
        news_frame = tk.LabelFrame(parent, text="Haberler ve Güncellemeler", 
                                  bg='#3a3a3a', fg='white',
                                  font=('Arial', 12, 'bold'))
        news_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # News content
        news_text = tk.Text(news_frame, bg='#2b2b2b', fg='white',
                           font=('Arial', 10), wrap=tk.WORD)
        news_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sample news content
        news_content = """
🎮 Berke Launcher v1.0 Yayınlandı!

BERKE0S Ultimate için özel olarak geliştirilmiş Minecraft launcher'ı artık hazır!

✨ Özellikler:
• Tüm Minecraft sürümlerini destekler
• Mod yönetimi
• Profil sistemi
• Otomatik güncelleme
• BERKE0S entegrasyonu

📦 Son Minecraft Güncellemeleri:
• 1.20.4 - Bug düzeltmeleri
• 1.20.3 - Yeni özellikler
• 1.20.2 - Performans iyileştirmeleri

🔧 Mod Desteği:
• Forge
• Fabric
• Quilt
• OptiFine

🎯 Yakında Gelecek Özellikler:
• Shader pack yöneticisi
• Kaynak paketi yöneticisi
• Sunucu listesi
• Arkadaş sistemi
• Başarım takibi

📊 İstatistikler:
• Toplam oyun süresi: 0 saat
• En çok oynanan sürüm: -
• Kurulan mod sayısı: 0

🌟 BERKE0S özel özellikleri:
• Sistem entegrasyonu
• Performans optimizasyonu
• Gelişmiş hata ayıklama
• Otomatik yedekleme

Minecraft oynamaya başlamak için sol panelden bir profil seçin ve "Oyunu Başlat" butonuna tıklayın!
        """
        
        news_text.insert('1.0', news_content)
        news_text.config(state='disabled')
        
        # Mod management
        mod_frame = tk.LabelFrame(parent, text="Mod Yönetimi", 
                                 bg='#3a3a3a', fg='white',
                                 font=('Arial', 12, 'bold'))
        mod_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        mod_btn_frame = tk.Frame(mod_frame, bg='#3a3a3a')
        mod_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(mod_btn_frame, text="📁 Mod Klasörü", command=self.open_mods_folder,
                 bg='#FF9800', fg='white', width=12).pack(side=tk.LEFT, padx=5)
        
        tk.Button(mod_btn_frame, text="⬇️ Mod İndir", command=self.download_mods,
                 bg='#9C27B0', fg='white', width=12).pack(side=tk.LEFT, padx=5)
        
        tk.Button(mod_btn_frame, text="⚙️ Mod Ayarları", command=self.mod_settings,
                 bg='#607D8B', fg='white', width=12).pack(side=tk.LEFT, padx=5)
    
    def create_footer(self):
        """Footer oluştur"""
        footer_frame = tk.Frame(self.window, bg='#1e1e1e', height=60)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)
        
        # Progress bar (initially hidden)
        self.progress_frame = tk.Frame(footer_frame, bg='#1e1e1e')
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, 
                                           variable=self.progress_var,
                                           maximum=100, length=400)
        self.progress_bar.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.progress_label = tk.Label(self.progress_frame, text="",
                                      bg='#1e1e1e', fg='white')
        self.progress_label.pack(side=tk.LEFT, padx=10)
        
        # Main buttons
        button_frame = tk.Frame(footer_frame, bg='#1e1e1e')
        button_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Settings button
        tk.Button(button_frame, text="⚙️ Ayarlar", command=self.show_settings,
                 bg='#607D8B', fg='white', font=('Arial', 10),
                 width=10, height=2).pack(side=tk.LEFT, padx=5)
        
        # Launch button
        self.launch_button = tk.Button(button_frame, text="🚀 Oyunu Başlat", 
                                      command=self.launch_game,
                                      bg='#4CAF50', fg='white', 
                                      font=('Arial', 12, 'bold'),
                                      width=15, height=2)
        self.launch_button.pack(side=tk.LEFT, padx=5)
    
    def load_profiles(self):
        """Profilleri yükle"""
        default_profiles = {
            "default": {
                "name": "Varsayılan",
                "version": "latest-release",
                "java_args": "-Xmx2G",
                "game_dir": self.minecraft_dir,
                "mods_enabled": True
            }
        }
        
        try:
            if os.path.exists(self.profiles_file):
                with open(self.profiles_file, 'r') as f:
                    return json.load(f)
            else:
                self.save_profiles(default_profiles)
                return default_profiles
        except:
            return default_profiles
    
    def save_profiles(self, profiles=None):
        """Profilleri kaydet"""
        if profiles is None:
            profiles = self.profiles
            
        try:
            with open(self.profiles_file, 'w') as f:
                json.dump(profiles, f, indent=4)
        except Exception as e:
            print(f"Profiller kaydedilemedi: {e}")
    
    def load_versions(self):
        """Mevcut sürümleri yükle"""
        # Sample versions (in real implementation, this would fetch from Mojang API)
        sample_versions = [
            "1.20.4 (Latest)",
            "1.20.3",
            "1.20.2",
            "1.20.1",
            "1.19.4",
            "1.19.3",
            "1.19.2",
            "1.18.2",
            "1.17.1",
            "1.16.5",
            "1.12.2",
            "1.8.9"
        ]
        
        self.version_listbox.delete(0, tk.END)
        for version in sample_versions:
            self.version_listbox.insert(tk.END, version)
        
        # Select first version by default
        if sample_versions:
            self.version_listbox.selection_set(0)
    
    def on_profile_change(self, event=None):
        """Profil değiştiğinde"""
        self.current_profile = self.profile_var.get()
        # Update UI based on selected profile
        
    def new_profile(self):
        """Yeni profil oluştur"""
        profile_window = tk.Toplevel(self.window)
        profile_window.title("Yeni Profil")
        profile_window.geometry("400x300")
        profile_window.configure(bg='#2b2b2b')
        
        # Profile name
        tk.Label(profile_window, text="Profil Adı:", bg='#2b2b2b', fg='white').pack(pady=5)
        name_var = tk.StringVar()
        tk.Entry(profile_window, textvariable=name_var, width=30).pack(pady=5)
        
        # Version selection
        tk.Label(profile_window, text="Sürüm:", bg='#2b2b2b', fg='white').pack(pady=5)
        version_var = tk.StringVar()
        version_combo = ttk.Combobox(profile_window, textvariable=version_var,
                                    values=["latest-release", "latest-snapshot", "1.20.4", "1.19.4"])
        version_combo.pack(pady=5)
        
        # Game directory
        tk.Label(profile_window, text="Oyun Dizini:", bg='#2b2b2b', fg='white').pack(pady=5)
        dir_frame = tk.Frame(profile_window, bg='#2b2b2b')
        dir_frame.pack(pady=5)
        
        dir_var = tk.StringVar(value=self.minecraft_dir)
        tk.Entry(dir_frame, textvariable=dir_var, width=25).pack(side=tk.LEFT)
        tk.Button(dir_frame, text="...", command=lambda: self.browse_directory(dir_var)).pack(side=tk.LEFT)
        
        # Buttons
        btn_frame = tk.Frame(profile_window, bg='#2b2b2b')
        btn_frame.pack(pady=20)
        
        def save_profile():
            name = name_var.get().strip()
            if name and name not in self.profiles:
                self.profiles[name] = {
                    "name": name,
                    "version": version_var.get() or "latest-release",
                    "java_args": "-Xmx2G",
                    "game_dir": dir_var.get(),
                    "mods_enabled": True
                }
                self.save_profiles()
                self.update_profile_combo()
                profile_window.destroy()
                messagebox.showinfo("Başarılı", "Profil oluşturuldu!")
            else:
                messagebox.showerror("Hata", "Geçersiz profil adı!")
        
        tk.Button(btn_frame, text="Kaydet", command=save_profile,
                 bg='#4CAF50', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="İptal", command=profile_window.destroy,
                 bg='#f44336', fg='white').pack(side=tk.LEFT, padx=5)
    
    def edit_profile(self):
        """Profil düzenle"""
        if self.current_profile in self.profiles:
            # Implementation for profile editing
            messagebox.showinfo("Bilgi", "Profil düzenleme özelliği yakında eklenecek!")
    
    def delete_profile(self):
        """Profil sil"""
        if self.current_profile != "default" and self.current_profile in self.profiles:
            result = messagebox.askyesno("Onay", f"'{self.current_profile}' profilini silmek istediğinizden emin misiniz?")
            if result:
                del self.profiles[self.current_profile]
                self.save_profiles()
                self.current_profile = "default"
                self.update_profile_combo()
                messagebox.showinfo("Başarılı", "Profil silindi!")
    
    def update_profile_combo(self):
        """Profil combo'sunu güncelle"""
        # Update the combobox values
        pass
    
    def download_version(self):
        """Seçili sürümü indir"""
        selection = self.version_listbox.curselection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen bir sürüm seçin!")
            return
        
        version = self.version_listbox.get(selection[0])
        
        # Show progress
        self.show_progress("İndiriliyor", f"Minecraft {version} indiriliyor...")
        
        # Simulate download
        def download_thread():
            for i in range(101):
                self.progress_var.set(i)
                self.progress_label.config(text=f"İndiriliyor... %{i}")
                time.sleep(0.05)
            
            self.hide_progress()
            messagebox.showinfo("Başarılı", f"Minecraft {version} başarıyla indirildi!")
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def refresh_versions(self):
        """Sürüm listesini yenile"""
        self.load_versions()
        messagebox.showinfo("Bilgi", "Sürüm listesi yenilendi!")
    
    def toggle_custom_resolution(self):
        """Özel çözünürlük toggle"""
        # Enable/disable resolution inputs
        pass
    
    def show_progress(self, title, message):
        """Progress bar göster"""
        self.progress_frame.pack(side=tk.LEFT, padx=20, pady=10)
        self.progress_label.config(text=message)
        self.progress_var.set(0)
        self.downloading = True
    
    def hide_progress(self):
        """Progress bar gizle"""
        self.progress_frame.pack_forget()
        self.downloading = False
    
    def launch_game(self):
        """Minecraft'ı başlat"""
        try:
            # Get selected version
            selection = self.version_listbox.curselection()
            if not selection:
                messagebox.showwarning("Uyarı", "Lütfen bir sürüm seçin!")
                return
            
            version = self.version_listbox.get(selection[0])
            
            # Show launching message
            self.launch_button.config(text="Başlatılıyor...", state='disabled')
            
            # Simulate game launch
            def launch_thread():
                time.sleep(2)  # Simulate launch time
                
                # In real implementation, this would launch Minecraft
                messagebox.showinfo("Oyun Başlatıldı", 
                                   f"Minecraft {version} başlatıldı!\n\n"
                                   "Gerçek uygulamada, burada Minecraft oyunu açılacaktır.")
                
                self.launch_button.config(text="🚀 Oyunu Başlat", state='normal')
            
            threading.Thread(target=launch_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Oyun başlatılamadı: {str(e)}")
            self.launch_button.config(text="🚀 Oyunu Başlat", state='normal')
    
    def open_mods_folder(self):
        """Mod klasörünü aç"""
        try:
            if os.path.exists(self.mods_dir):
                subprocess.run(['xdg-open', self.mods_dir])
            else:
                os.makedirs(self.mods_dir, exist_ok=True)
                subprocess.run(['xdg-open', self.mods_dir])
        except Exception as e:
            messagebox.showerror("Hata", f"Mod klasörü açılamadı: {str(e)}")
    
    def download_mods(self):
        """Mod indirme sayfası"""
        mod_window = tk.Toplevel(self.window)
        mod_window.title("Mod İndirme")
        mod_window.geometry("600x400")
        mod_window.configure(bg='#2b2b2b')
        
        # Popular mods list
        tk.Label(mod_window, text="Popüler Modlar", 
                font=('Arial', 14, 'bold'),
                bg='#2b2b2b', fg='white').pack(pady=10)
        
        mods_frame = tk.Frame(mod_window, bg='#2b2b2b')
        mods_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        popular_mods = [
            "OptiFine - Performans ve grafik iyileştirmeleri",
            "JEI (Just Enough Items) - Eşya listesi ve tarifler",
            "Biomes O' Plenty - Yeni biome'lar",
            "Tinkers' Construct - Gelişmiş araç sistemi",
            "Applied Energistics 2 - Gelişmiş depolama",
            "Thermal Expansion - Makineler ve enerji",
            "Iron Chests - Gelişmiş sandıklar",
            "Waystones - Hızlı seyahat",
            "JourneyMap - Harita modu",
            "Inventory Tweaks - Envanter düzenleme"
        ]
        
        for mod in popular_mods:
            mod_frame = tk.Frame(mods_frame, bg='#3a3a3a', relief=tk.RAISED, bd=1)
            mod_frame.pack(fill=tk.X, pady=2)
            
            tk.Label(mod_frame, text=mod, bg='#3a3a3a', fg='white',
                    font=('Arial', 10)).pack(side=tk.LEFT, padx=10, pady=5)
            
            tk.Button(mod_frame, text="İndir", 
                     command=lambda m=mod: self.download_mod(m),
                     bg='#4CAF50', fg='white').pack(side=tk.RIGHT, padx=10, pady=2)
    
    def download_mod(self, mod_name):
        """Mod indir"""
        messagebox.showinfo("Mod İndirme", f"{mod_name} indiriliyor...\n\nGerçek uygulamada mod dosyası indirilecektir.")
    
    def mod_settings(self):
        """Mod ayarları"""
        messagebox.showinfo("Mod Ayarları", "Mod ayarları özelliği yakında eklenecek!")
    
    def show_settings(self):
        """Launcher ayarları"""
        settings_window = tk.Toplevel(self.window)
        settings_window.title("Launcher Ayarları")
        settings_window.geometry("500x400")
        settings_window.configure(bg='#2b2b2b')
        
        # Java settings
        java_frame = tk.LabelFrame(settings_window, text="Java Ayarları",
                                  bg='#2b2b2b', fg='white')
        java_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(java_frame, text="Java Yolu:", bg='#2b2b2b', fg='white').pack(anchor='w', padx=10)
        java_var = tk.StringVar(value=self.settings["java_path"])
        java_entry = tk.Entry(java_frame, textvariable=java_var, width=50)
        java_entry.pack(padx=10, pady=5)
        
        tk.Button(java_frame, text="Java'yı Bul", 
                 command=lambda: java_var.set(self.find_java())).pack(pady=5)
        
        # Memory settings
        memory_frame = tk.LabelFrame(settings_window, text="Bellek Ayarları",
                                    bg='#2b2b2b', fg='white')
        memory_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(memory_frame, text="Maksimum RAM:", bg='#2b2b2b', fg='white').pack(anchor='w', padx=10)
        memory_var = tk.StringVar(value=self.settings["memory_allocation"])
        memory_combo = ttk.Combobox(memory_frame, textvariable=memory_var,
                                   values=["1G", "2G", "4G", "6G", "8G", "12G", "16G"])
        memory_combo.pack(padx=10, pady=5)
        
        # Save button
        def save_settings():
            self.settings.update({
                "java_path": java_var.get(),
                "memory_allocation": memory_var.get()
            })
            messagebox.showinfo("Başarılı", "Ayarlar kaydedildi!")
            settings_window.destroy()
        
        tk.Button(settings_window, text="Kaydet", command=save_settings,
                 bg='#4CAF50', fg='white', font=('Arial', 12, 'bold')).pack(pady=20)
    
    def browse_directory(self, var):
        """Dizin seç"""
        directory = filedialog.askdirectory()
        if directory:
            var.set(directory)
    
    def close(self):
        """Launcher'ı kapat"""
        if self.window:
            self.window.destroy()