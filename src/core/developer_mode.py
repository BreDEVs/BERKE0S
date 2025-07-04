"""
BERKE0S Ultimate - Geliştirici Modu
Ctrl+Fn+B ile etkinleştirilen gelişmiş geliştirici araçları
"""

import os
import sys
import json
import time
import hashlib
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading

class DeveloperMode:
    """Geliştirici Modu Yöneticisi"""
    
    def __init__(self):
        self.enabled = False
        self.authenticated = False
        self.password_hash = "a4d4c8b5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3"  # 4997
        self.access_level = 0  # 0: Normal, 1: Developer, 2: System Admin
        self.session_start = None
        self.tools_window = None
        
    def authenticate(self):
        """Geliştirici modu kimlik doğrulaması"""
        try:
            auth_window = tk.Toplevel()
            auth_window.title("🔐 Geliştirici Modu - Kimlik Doğrulama")
            auth_window.geometry("400x300")
            auth_window.configure(bg='#0a0a0f')
            auth_window.resizable(False, False)
            auth_window.grab_set()
            
            # Center window
            auth_window.update_idletasks()
            x = (auth_window.winfo_screenwidth() // 2) - (400 // 2)
            y = (auth_window.winfo_screenheight() // 2) - (300 // 2)
            auth_window.geometry(f"400x300+{x}+{y}")
            
            # Header
            header = tk.Label(auth_window, text="🔐 Geliştirici Modu",
                            font=('Arial', 18, 'bold'),
                            fg='#ff6b6b', bg='#0a0a0f')
            header.pack(pady=(30, 20))
            
            # Warning
            warning = tk.Label(auth_window, 
                             text="⚠️ UYARI: Bu mod sistem dosyalarına\ntam erişim sağlar. Dikkatli kullanın!",
                             font=('Arial', 10),
                             fg='#ffb347', bg='#0a0a0f')
            warning.pack(pady=(0, 30))
            
            # Password frame
            pass_frame = tk.Frame(auth_window, bg='#0a0a0f')
            pass_frame.pack(pady=20)
            
            tk.Label(pass_frame, text="Geliştirici Şifresi:",
                    font=('Arial', 12), fg='white', bg='#0a0a0f').pack()
            
            password_var = tk.StringVar()
            password_entry = tk.Entry(pass_frame, textvariable=password_var,
                                    show='*', font=('Arial', 14), width=20,
                                    bg='#1a1a1a', fg='white', justify='center')
            password_entry.pack(pady=10)
            password_entry.focus_set()
            
            # Result
            result = {"authenticated": False}
            
            def check_password():
                entered = password_var.get()
                entered_hash = hashlib.sha256(entered.encode()).hexdigest()
                
                if entered_hash == self.password_hash:
                    result["authenticated"] = True
                    self.authenticated = True
                    self.session_start = time.time()
                    auth_window.destroy()
                else:
                    messagebox.showerror("Hata", "Yanlış şifre!", parent=auth_window)
                    password_var.set("")
            
            def cancel():
                auth_window.destroy()
            
            # Buttons
            btn_frame = tk.Frame(auth_window, bg='#0a0a0f')
            btn_frame.pack(pady=30)
            
            tk.Button(btn_frame, text="🔓 Giriş", command=check_password,
                     bg='#00ff88', fg='black', font=('Arial', 12, 'bold'),
                     relief=tk.FLAT, padx=20, pady=5).pack(side=tk.LEFT, padx=10)
            
            tk.Button(btn_frame, text="❌ İptal", command=cancel,
                     bg='#ff6b6b', fg='white', font=('Arial', 12),
                     relief=tk.FLAT, padx=20, pady=5).pack(side=tk.LEFT, padx=10)
            
            password_entry.bind('<Return>', lambda e: check_password())
            
            auth_window.wait_window()
            return result["authenticated"]
            
        except Exception as e:
            print(f"Kimlik doğrulama hatası: {e}")
            return False
    
    def enable(self):
        """Geliştirici modunu etkinleştir"""
        if not self.authenticated:
            return False
            
        self.enabled = True
        self.access_level = 2  # System Admin
        self.show_developer_tools()
        return True
    
    def disable(self):
        """Geliştirici modunu devre dışı bırak"""
        self.enabled = False
        self.access_level = 0
        if self.tools_window:
            self.tools_window.destroy()
            self.tools_window = None
    
    def is_enabled(self):
        """Geliştirici modu etkin mi?"""
        return self.enabled
    
    def show_developer_tools(self):
        """Geliştirici araçları penceresini göster"""
        try:
            if self.tools_window:
                self.tools_window.lift()
                return
                
            self.tools_window = tk.Toplevel()
            self.tools_window.title("🛠️ BERKE0S Geliştirici Araçları")
            self.tools_window.geometry("1000x700")
            self.tools_window.configure(bg='#0a0a0f')
            
            # Protocol for closing
            self.tools_window.protocol("WM_DELETE_WINDOW", self.close_tools)
            
            # Create notebook for different tools
            notebook = ttk.Notebook(self.tools_window)
            notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # System Inspector
            self.create_system_inspector_tab(notebook)
            
            # Code Editor
            self.create_code_editor_tab(notebook)
            
            # File System Browser
            self.create_filesystem_browser_tab(notebook)
            
            # Process Manager
            self.create_process_manager_tab(notebook)
            
            # Network Tools
            self.create_network_tools_tab(notebook)
            
            # Database Manager
            self.create_database_manager_tab(notebook)
            
            # Log Viewer
            self.create_log_viewer_tab(notebook)
            
            # System Configuration
            self.create_system_config_tab(notebook)
            
        except Exception as e:
            print(f"Geliştirici araçları hatası: {e}")
    
    def create_system_inspector_tab(self, notebook):
        """Sistem denetleyici sekmesi"""
        frame = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(frame, text="🔍 Sistem Denetleyici")
        
        # System info display
        self.system_info_text = scrolledtext.ScrolledText(
            frame, bg='#0a0a0f', fg='#00ff88', font=('Courier', 10)
        )
        self.system_info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Refresh button
        refresh_btn = tk.Button(frame, text="🔄 Yenile", 
                               command=self.refresh_system_info,
                               bg='#00ff88', fg='black', font=('Arial', 10, 'bold'))
        refresh_btn.pack(pady=5)
        
        # Load initial info
        self.refresh_system_info()
    
    def create_code_editor_tab(self, notebook):
        """Kod editörü sekmesi"""
        frame = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(frame, text="💻 Kod Editörü")
        
        # File selection
        file_frame = tk.Frame(frame, bg='#1a1a1a')
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(file_frame, text="Dosya:", bg='#1a1a1a', fg='white').pack(side=tk.LEFT)
        
        self.file_var = tk.StringVar()
        file_entry = tk.Entry(file_frame, textvariable=self.file_var,
                             bg='#0a0a0f', fg='white', width=60)
        file_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(file_frame, text="📁 Aç", command=self.open_file_for_edit,
                 bg='#4a9eff', fg='white').pack(side=tk.LEFT, padx=5)
        
        tk.Button(file_frame, text="💾 Kaydet", command=self.save_file,
                 bg='#00ff88', fg='black').pack(side=tk.LEFT, padx=5)
        
        # Code editor
        self.code_editor = scrolledtext.ScrolledText(
            frame, bg='#0a0a0f', fg='white', font=('Courier', 11),
            insertbackground='white'
        )
        self.code_editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_filesystem_browser_tab(self, notebook):
        """Dosya sistemi tarayıcısı sekmesi"""
        frame = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(frame, text="📁 Dosya Sistemi")
        
        # Path entry
        path_frame = tk.Frame(frame, bg='#1a1a1a')
        path_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(path_frame, text="Yol:", bg='#1a1a1a', fg='white').pack(side=tk.LEFT)
        
        self.path_var = tk.StringVar(value="/")
        path_entry = tk.Entry(path_frame, textvariable=self.path_var,
                             bg='#0a0a0f', fg='white', width=60)
        path_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(path_frame, text="🔍 Git", command=self.browse_filesystem,
                 bg='#4a9eff', fg='white').pack(side=tk.LEFT, padx=5)
        
        # File tree
        self.file_tree = ttk.Treeview(frame, columns=('Size', 'Modified'), show='tree headings')
        self.file_tree.heading('#0', text='Dosya/Klasör')
        self.file_tree.heading('Size', text='Boyut')
        self.file_tree.heading('Modified', text='Değiştirilme')
        self.file_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load root directory
        self.browse_filesystem()
    
    def create_process_manager_tab(self, notebook):
        """Süreç yöneticisi sekmesi"""
        frame = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(frame, text="⚙️ Süreç Yöneticisi")
        
        # Process list
        self.process_tree = ttk.Treeview(frame, columns=('PID', 'CPU', 'Memory', 'Status'), show='tree headings')
        self.process_tree.heading('#0', text='Süreç Adı')
        self.process_tree.heading('PID', text='PID')
        self.process_tree.heading('CPU', text='CPU %')
        self.process_tree.heading('Memory', text='Bellek %')
        self.process_tree.heading('Status', text='Durum')
        self.process_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control buttons
        btn_frame = tk.Frame(frame, bg='#1a1a1a')
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(btn_frame, text="🔄 Yenile", command=self.refresh_processes,
                 bg='#00ff88', fg='black').pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="⏹️ Sonlandır", command=self.kill_process,
                 bg='#ff6b6b', fg='white').pack(side=tk.LEFT, padx=5)
        
        # Load processes
        self.refresh_processes()
    
    def create_network_tools_tab(self, notebook):
        """Ağ araçları sekmesi"""
        frame = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(frame, text="🌐 Ağ Araçları")
        
        # Network commands
        cmd_frame = tk.Frame(frame, bg='#1a1a1a')
        cmd_frame.pack(fill=tk.X, padx=10, pady=5)
        
        commands = [
            ("📡 Ping", self.ping_test),
            ("🔍 Nslookup", self.nslookup_test),
            ("📊 Netstat", self.netstat_info),
            ("🌐 İfconfig", self.ifconfig_info)
        ]
        
        for text, command in commands:
            tk.Button(cmd_frame, text=text, command=command,
                     bg='#4a9eff', fg='white', width=12).pack(side=tk.LEFT, padx=5)
        
        # Output area
        self.network_output = scrolledtext.ScrolledText(
            frame, bg='#0a0a0f', fg='#00ff88', font=('Courier', 10)
        )
        self.network_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_database_manager_tab(self, notebook):
        """Veritabanı yöneticisi sekmesi"""
        frame = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(frame, text="🗄️ Veritabanı")
        
        # SQL query area
        query_frame = tk.LabelFrame(frame, text="SQL Sorgusu", bg='#1a1a1a', fg='white')
        query_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.sql_query = tk.Text(query_frame, height=5, bg='#0a0a0f', fg='white',
                                font=('Courier', 10))
        self.sql_query.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(query_frame, text="▶️ Çalıştır", command=self.execute_sql,
                 bg='#00ff88', fg='black').pack(pady=5)
        
        # Results area
        results_frame = tk.LabelFrame(frame, text="Sonuçlar", bg='#1a1a1a', fg='white')
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.sql_results = scrolledtext.ScrolledText(
            results_frame, bg='#0a0a0f', fg='#00ff88', font=('Courier', 9)
        )
        self.sql_results.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_log_viewer_tab(self, notebook):
        """Log görüntüleyici sekmesi"""
        frame = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(frame, text="📋 Log Görüntüleyici")
        
        # Log file selection
        log_frame = tk.Frame(frame, bg='#1a1a1a')
        log_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(log_frame, text="Log Dosyası:", bg='#1a1a1a', fg='white').pack(side=tk.LEFT)
        
        self.log_file_var = tk.StringVar()
        log_combo = ttk.Combobox(log_frame, textvariable=self.log_file_var,
                                values=self.get_log_files(), width=50)
        log_combo.pack(side=tk.LEFT, padx=5)
        
        tk.Button(log_frame, text="📖 Yükle", command=self.load_log_file,
                 bg='#4a9eff', fg='white').pack(side=tk.LEFT, padx=5)
        
        tk.Button(log_frame, text="🔄 Yenile", command=self.refresh_log,
                 bg='#00ff88', fg='black').pack(side=tk.LEFT, padx=5)
        
        # Log content
        self.log_content = scrolledtext.ScrolledText(
            frame, bg='#0a0a0f', fg='#00ff88', font=('Courier', 9)
        )
        self.log_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_system_config_tab(self, notebook):
        """Sistem konfigürasyonu sekmesi"""
        frame = tk.Frame(notebook, bg='#1a1a1a')
        notebook.add(frame, text="⚙️ Sistem Yapılandırması")
        
        # Config tree
        self.config_tree = ttk.Treeview(frame, columns=('Value',), show='tree headings')
        self.config_tree.heading('#0', text='Ayar')
        self.config_tree.heading('Value', text='Değer')
        self.config_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control buttons
        config_btn_frame = tk.Frame(frame, bg='#1a1a1a')
        config_btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(config_btn_frame, text="🔄 Yenile", command=self.refresh_config,
                 bg='#00ff88', fg='black').pack(side=tk.LEFT, padx=5)
        
        tk.Button(config_btn_frame, text="✏️ Düzenle", command=self.edit_config,
                 bg='#4a9eff', fg='white').pack(side=tk.LEFT, padx=5)
        
        tk.Button(config_btn_frame, text="💾 Kaydet", command=self.save_config,
                 bg='#ffb347', fg='black').pack(side=tk.LEFT, padx=5)
        
        # Load config
        self.refresh_config()
    
    # Implementation methods for developer tools
    
    def refresh_system_info(self):
        """Sistem bilgilerini yenile"""
        try:
            import psutil
            import platform
            
            info = f"""
BERKE0S Ultimate - Sistem Bilgileri
{'='*50}

İşletim Sistemi: {platform.system()} {platform.release()}
Mimari: {platform.machine()}
Python Sürümü: {sys.version}
Çalışma Süresi: {time.time() - (time.time() - psutil.boot_time()):.2f} saniye

CPU Bilgileri:
  Çekirdek Sayısı: {psutil.cpu_count()}
  Kullanım: {psutil.cpu_percent()}%
  Frekans: {psutil.cpu_freq().current:.2f} MHz

Bellek Bilgileri:
  Toplam: {psutil.virtual_memory().total / (1024**3):.2f} GB
  Kullanılan: {psutil.virtual_memory().used / (1024**3):.2f} GB
  Kullanım: {psutil.virtual_memory().percent}%

Disk Bilgileri:
  Toplam: {psutil.disk_usage('/').total / (1024**3):.2f} GB
  Kullanılan: {psutil.disk_usage('/').used / (1024**3):.2f} GB
  Boş: {psutil.disk_usage('/').free / (1024**3):.2f} GB

Ağ Bilgileri:
  Gönderilen: {psutil.net_io_counters().bytes_sent / (1024**2):.2f} MB
  Alınan: {psutil.net_io_counters().bytes_recv / (1024**2):.2f} MB

Süreç Sayısı: {len(psutil.pids())}
            """
            
            self.system_info_text.delete('1.0', tk.END)
            self.system_info_text.insert('1.0', info)
            
        except Exception as e:
            self.system_info_text.delete('1.0', tk.END)
            self.system_info_text.insert('1.0', f"Sistem bilgisi alınamadı: {e}")
    
    def open_file_for_edit(self):
        """Dosya aç ve düzenle"""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Düzenlenecek dosyayı seçin",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.file_var.set(file_path)
                self.code_editor.delete('1.0', tk.END)
                self.code_editor.insert('1.0', content)
                
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya açılamadı: {e}")
    
    def save_file(self):
        """Dosyayı kaydet"""
        file_path = self.file_var.get()
        if not file_path:
            messagebox.showwarning("Uyarı", "Önce bir dosya seçin")
            return
        
        try:
            content = self.code_editor.get('1.0', tk.END)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            messagebox.showinfo("Başarılı", "Dosya kaydedildi")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya kaydedilemedi: {e}")
    
    def browse_filesystem(self):
        """Dosya sistemini tara"""
        try:
            path = self.path_var.get()
            
            # Clear existing items
            for item in self.file_tree.get_children():
                self.file_tree.delete(item)
            
            # List directory contents
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                try:
                    stat = os.stat(item_path)
                    size = stat.st_size if os.path.isfile(item_path) else ""
                    modified = time.strftime("%Y-%m-%d %H:%M", time.localtime(stat.st_mtime))
                    
                    self.file_tree.insert("", "end", text=item, 
                                         values=(size, modified))
                except:
                    self.file_tree.insert("", "end", text=item, 
                                         values=("", ""))
                    
        except Exception as e:
            messagebox.showerror("Hata", f"Dizin okunamadı: {e}")
    
    def refresh_processes(self):
        """Süreçleri yenile"""
        try:
            import psutil
            
            # Clear existing items
            for item in self.process_tree.get_children():
                self.process_tree.delete(item)
            
            # List processes
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    info = proc.info
                    self.process_tree.insert("", "end", text=info['name'],
                                           values=(info['pid'], 
                                                  f"{info['cpu_percent']:.1f}",
                                                  f"{info['memory_percent']:.1f}",
                                                  info['status']))
                except:
                    pass
                    
        except Exception as e:
            messagebox.showerror("Hata", f"Süreçler listelenemedi: {e}")
    
    def kill_process(self):
        """Seçili süreci sonlandır"""
        selection = self.process_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Bir süreç seçin")
            return
        
        try:
            import psutil
            
            item = self.process_tree.item(selection[0])
            pid = int(item['values'][0])
            
            result = messagebox.askyesno("Onay", f"PID {pid} sürecini sonlandırmak istediğinizden emin misiniz?")
            if result:
                proc = psutil.Process(pid)
                proc.terminate()
                self.refresh_processes()
                
        except Exception as e:
            messagebox.showerror("Hata", f"Süreç sonlandırılamadı: {e}")
    
    def ping_test(self):
        """Ping testi"""
        host = tk.simpledialog.askstring("Ping Test", "Host adresini girin:")
        if host:
            try:
                result = subprocess.run(['ping', '-c', '4', host], 
                                      capture_output=True, text=True)
                self.network_output.delete('1.0', tk.END)
                self.network_output.insert('1.0', result.stdout)
            except Exception as e:
                self.network_output.delete('1.0', tk.END)
                self.network_output.insert('1.0', f"Ping hatası: {e}")
    
    def get_log_files(self):
        """Log dosyalarını listele"""
        log_files = []
        log_dirs = [
            os.path.expanduser("~/.berke0s"),
            "/var/log",
            "/tmp"
        ]
        
        for log_dir in log_dirs:
            if os.path.exists(log_dir):
                for file in os.listdir(log_dir):
                    if file.endswith('.log'):
                        log_files.append(os.path.join(log_dir, file))
        
        return log_files
    
    def load_log_file(self):
        """Log dosyasını yükle"""
        log_file = self.log_file_var.get()
        if not log_file:
            return
        
        try:
            with open(log_file, 'r') as f:
                content = f.read()
            
            self.log_content.delete('1.0', tk.END)
            self.log_content.insert('1.0', content)
            
        except Exception as e:
            self.log_content.delete('1.0', tk.END)
            self.log_content.insert('1.0', f"Log dosyası okunamadı: {e}")
    
    def refresh_config(self):
        """Konfigürasyonu yenile"""
        # Implementation for config refresh
        pass
    
    def close_tools(self):
        """Geliştirici araçlarını kapat"""
        self.tools_window.destroy()
        self.tools_window = None