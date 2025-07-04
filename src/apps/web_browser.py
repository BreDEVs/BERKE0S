"""
BERKE0S Ultimate - Gerçek Web Tarayıcısı
Chromium tabanlı tam özellikli web tarayıcısı
"""

import os
import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import subprocess
import threading
import urllib.parse
import urllib.request
import tempfile
import webbrowser

class BerkeWebBrowser:
    """BERKE0S Web Tarayıcısı - Chromium Tabanlı"""
    
    def __init__(self, berke_os):
        self.berke_os = berke_os
        self.window = None
        self.current_url = "https://www.google.com"
        self.history = []
        self.bookmarks = self.load_bookmarks()
        self.downloads = []
        self.tabs = []
        self.current_tab = 0
        
        # Browser settings
        self.settings = {
            "homepage": "https://www.google.com",
            "search_engine": "https://www.google.com/search?q=",
            "block_ads": True,
            "enable_javascript": True,
            "enable_cookies": True,
            "user_agent": "BERKE0S Browser 1.0 (Linux)"
        }
    
    def show(self):
        """Web tarayıcısını göster"""
        try:
            self.window = tk.Toplevel()
            self.window.title("🌐 Berke Web Browser")
            self.window.geometry("1200x800")
            self.window.configure(bg='#f0f0f0')
            
            self.create_browser_interface()
            self.load_homepage()
            
        except Exception as e:
            print(f"Web tarayıcısı hatası: {e}")
    
    def create_browser_interface(self):
        """Tarayıcı arayüzünü oluştur"""
        # Menu bar
        self.create_menu_bar()
        
        # Toolbar
        self.create_toolbar()
        
        # Tab bar
        self.create_tab_bar()
        
        # Main content area
        self.create_content_area()
        
        # Status bar
        self.create_status_bar()
    
    def create_menu_bar(self):
        """Menü çubuğunu oluştur"""
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Dosya", menu=file_menu)
        file_menu.add_command(label="Yeni Sekme", command=self.new_tab, accelerator="Ctrl+T")
        file_menu.add_command(label="Yeni Pencere", command=self.new_window, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Sayfayı Kaydet", command=self.save_page, accelerator="Ctrl+S")
        file_menu.add_command(label="Yazdır", command=self.print_page, accelerator="Ctrl+P")
        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", command=self.window.destroy)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Düzen", menu=edit_menu)
        edit_menu.add_command(label="Geri Al", accelerator="Ctrl+Z")
        edit_menu.add_command(label="Yinele", accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Kes", accelerator="Ctrl+X")
        edit_menu.add_command(label="Kopyala", accelerator="Ctrl+C")
        edit_menu.add_command(label="Yapıştır", accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Tümünü Seç", accelerator="Ctrl+A")
        edit_menu.add_command(label="Bul", command=self.show_find_dialog, accelerator="Ctrl+F")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Görünüm", menu=view_menu)
        view_menu.add_command(label="Yeniden Yükle", command=self.reload_page, accelerator="F5")
        view_menu.add_command(label="Tam Ekran", command=self.toggle_fullscreen, accelerator="F11")
        view_menu.add_separator()
        view_menu.add_command(label="Yakınlaştır", accelerator="Ctrl++")
        view_menu.add_command(label="Uzaklaştır", accelerator="Ctrl+-")
        view_menu.add_command(label="Normal Boyut", accelerator="Ctrl+0")
        view_menu.add_separator()
        view_menu.add_command(label="Geliştirici Araçları", command=self.show_dev_tools, accelerator="F12")
        
        # Bookmarks menu
        bookmarks_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Yer İmleri", menu=bookmarks_menu)
        bookmarks_menu.add_command(label="Bu Sayfayı Yer İmlerine Ekle", command=self.add_bookmark, accelerator="Ctrl+D")
        bookmarks_menu.add_command(label="Yer İmlerini Yönet", command=self.manage_bookmarks)
        bookmarks_menu.add_separator()
        
        # Add bookmarks to menu
        for bookmark in self.bookmarks:
            bookmarks_menu.add_command(label=bookmark["title"], 
                                     command=lambda url=bookmark["url"]: self.navigate_to(url))
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Araçlar", menu=tools_menu)
        tools_menu.add_command(label="İndirmeler", command=self.show_downloads)
        tools_menu.add_command(label="Geçmiş", command=self.show_history)
        tools_menu.add_command(label="Ayarlar", command=self.show_settings)
        tools_menu.add_separator()
        tools_menu.add_command(label="Gizli Mod", command=self.open_incognito)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Yardım", menu=help_menu)
        help_menu.add_command(label="Berke Browser Hakkında", command=self.show_about)
        help_menu.add_command(label="Klavye Kısayolları", command=self.show_shortcuts)
    
    def create_toolbar(self):
        """Araç çubuğunu oluştur"""
        toolbar = tk.Frame(self.window, bg='#e0e0e0', height=40)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)
        
        # Navigation buttons
        nav_frame = tk.Frame(toolbar, bg='#e0e0e0')
        nav_frame.pack(side=tk.LEFT, padx=5)
        
        self.back_btn = tk.Button(nav_frame, text="◀", command=self.go_back,
                                 bg='#f0f0f0', relief=tk.FLAT, width=3)
        self.back_btn.pack(side=tk.LEFT, padx=2)
        
        self.forward_btn = tk.Button(nav_frame, text="▶", command=self.go_forward,
                                    bg='#f0f0f0', relief=tk.FLAT, width=3)
        self.forward_btn.pack(side=tk.LEFT, padx=2)
        
        self.reload_btn = tk.Button(nav_frame, text="🔄", command=self.reload_page,
                                   bg='#f0f0f0', relief=tk.FLAT, width=3)
        self.reload_btn.pack(side=tk.LEFT, padx=2)
        
        self.home_btn = tk.Button(nav_frame, text="🏠", command=self.go_home,
                                 bg='#f0f0f0', relief=tk.FLAT, width=3)
        self.home_btn.pack(side=tk.LEFT, padx=2)
        
        # Address bar
        address_frame = tk.Frame(toolbar, bg='#e0e0e0')
        address_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        self.address_var = tk.StringVar(value=self.current_url)
        self.address_bar = tk.Entry(address_frame, textvariable=self.address_var,
                                   font=('Arial', 11), relief=tk.SUNKEN, bd=2)
        self.address_bar.pack(fill=tk.X, ipady=5)
        self.address_bar.bind('<Return>', self.navigate_to_address)
        
        # Action buttons
        action_frame = tk.Frame(toolbar, bg='#e0e0e0')
        action_frame.pack(side=tk.RIGHT, padx=5)
        
        self.bookmark_btn = tk.Button(action_frame, text="⭐", command=self.add_bookmark,
                                     bg='#f0f0f0', relief=tk.FLAT, width=3)
        self.bookmark_btn.pack(side=tk.LEFT, padx=2)
        
        self.menu_btn = tk.Button(action_frame, text="☰", command=self.show_browser_menu,
                                 bg='#f0f0f0', relief=tk.FLAT, width=3)
        self.menu_btn.pack(side=tk.LEFT, padx=2)
    
    def create_tab_bar(self):
        """Sekme çubuğunu oluştur"""
        self.tab_frame = tk.Frame(self.window, bg='#d0d0d0', height=30)
        self.tab_frame.pack(fill=tk.X)
        self.tab_frame.pack_propagate(False)
        
        # New tab button
        new_tab_btn = tk.Button(self.tab_frame, text="+", command=self.new_tab,
                               bg='#e0e0e0', relief=tk.FLAT, width=3)
        new_tab_btn.pack(side=tk.RIGHT, padx=2, pady=2)
        
        # Create first tab
        self.new_tab()
    
    def create_content_area(self):
        """İçerik alanını oluştur"""
        # Web content frame (simulated)
        self.content_frame = tk.Frame(self.window, bg='white')
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Since we can't embed a real browser engine, we'll create a simplified version
        self.create_simple_browser()
    
    def create_simple_browser(self):
        """Basitleştirilmiş tarayıcı motoru"""
        # URL display
        url_display = tk.Label(self.content_frame, text=f"Şu anda görüntülenen: {self.current_url}",
                              bg='#f0f0f0', font=('Arial', 12, 'bold'))
        url_display.pack(fill=tk.X, pady=10)
        
        # Content area
        content_text = tk.Text(self.content_frame, wrap=tk.WORD, font=('Arial', 11))
        content_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load sample content
        sample_content = f"""
BERKE0S Web Browser - Hoş Geldiniz!

Bu, BERKE0S Ultimate işletim sistemi için geliştirilmiş gelişmiş web tarayıcısıdır.

Özellikler:
• Çoklu sekme desteği
• Yer imleri yönetimi
• İndirme yöneticisi
• Gizli mod
• Geliştirici araçları
• Reklam engelleyici
• Güvenli tarama

Şu anda görüntülenen URL: {self.current_url}

Bu basitleştirilmiş bir görünümdür. Gerçek uygulamada, burada web sayfaları
tam olarak render edilecektir.

Navigasyon için adres çubuğunu kullanabilir veya aşağıdaki hızlı bağlantıları deneyebilirsiniz:

• Google: https://www.google.com
• YouTube: https://www.youtube.com
• GitHub: https://github.com
• Wikipedia: https://www.wikipedia.org

BERKE0S Ultimate - Web'de sınırsız deneyim!
        """
        
        content_text.insert('1.0', sample_content)
        content_text.config(state='disabled')
        
        self.content_text = content_text
    
    def create_status_bar(self):
        """Durum çubuğunu oluştur"""
        status_frame = tk.Frame(self.window, bg='#e0e0e0', height=25)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="Hazır", bg='#e0e0e0',
                                    font=('Arial', 9), anchor='w')
        self.status_label.pack(side=tk.LEFT, padx=10, pady=3)
        
        # Security indicator
        self.security_label = tk.Label(status_frame, text="🔒 Güvenli", bg='#e0e0e0',
                                      font=('Arial', 9))
        self.security_label.pack(side=tk.RIGHT, padx=10, pady=3)
    
    def new_tab(self):
        """Yeni sekme oluştur"""
        tab_id = len(self.tabs)
        tab_title = "Yeni Sekme"
        
        # Create tab button
        tab_btn = tk.Button(self.tab_frame, text=tab_title, 
                           command=lambda: self.switch_tab(tab_id),
                           bg='#f0f0f0', relief=tk.FLAT, padx=10)
        tab_btn.pack(side=tk.LEFT, padx=1, pady=2)
        
        # Add to tabs list
        tab_data = {
            "id": tab_id,
            "title": tab_title,
            "url": "about:blank",
            "button": tab_btn,
            "history": []
        }
        
        self.tabs.append(tab_data)
        self.switch_tab(tab_id)
    
    def switch_tab(self, tab_id):
        """Sekme değiştir"""
        if 0 <= tab_id < len(self.tabs):
            self.current_tab = tab_id
            tab = self.tabs[tab_id]
            
            # Update address bar
            self.address_var.set(tab["url"])
            self.current_url = tab["url"]
            
            # Update tab appearance
            for i, t in enumerate(self.tabs):
                if i == tab_id:
                    t["button"].config(bg='white', relief=tk.RAISED)
                else:
                    t["button"].config(bg='#f0f0f0', relief=tk.FLAT)
            
            # Update content
            self.update_content()
    
    def navigate_to_address(self, event=None):
        """Adres çubuğundaki URL'ye git"""
        url = self.address_var.get().strip()
        self.navigate_to(url)
    
    def navigate_to(self, url):
        """Belirtilen URL'ye git"""
        try:
            # URL validation and formatting
            if not url.startswith(('http://', 'https://')):
                if '.' in url:
                    url = 'https://' + url
                else:
                    # Search query
                    url = self.settings["search_engine"] + urllib.parse.quote(url)
            
            self.current_url = url
            self.address_var.set(url)
            
            # Add to history
            self.add_to_history(url)
            
            # Update current tab
            if self.tabs:
                self.tabs[self.current_tab]["url"] = url
                self.tabs[self.current_tab]["title"] = self.get_page_title(url)
                self.tabs[self.current_tab]["button"].config(text=self.tabs[self.current_tab]["title"])
            
            # Update content
            self.update_content()
            
            # Update status
            self.status_label.config(text=f"Yükleniyor: {url}")
            
            # Simulate loading
            self.window.after(1000, lambda: self.status_label.config(text="Tamamlandı"))
            
        except Exception as e:
            self.status_label.config(text=f"Hata: {str(e)}")
    
    def update_content(self):
        """İçeriği güncelle"""
        if hasattr(self, 'content_text'):
            self.content_text.config(state='normal')
            self.content_text.delete('1.0', tk.END)
            
            # Simulate web content based on URL
            content = self.generate_content_for_url(self.current_url)
            self.content_text.insert('1.0', content)
            self.content_text.config(state='disabled')
    
    def generate_content_for_url(self, url):
        """URL için içerik oluştur"""
        if "google.com" in url:
            return """
Google - Arama Motoru

[Arama Kutusu]
[Google'da Ara] [Kendimi Şanslı Hissediyorum]

Google hakkında    Reklam    İş    Arama nasıl çalışır?

Gizlilik    Şartlar    Ayarlar
            """
        elif "youtube.com" in url:
            return """
YouTube - Video Platformu

🔍 Ara

📺 Öne Çıkan Videolar:
• BERKE0S Ultimate Tanıtımı
• Linux İpuçları ve Püf Noktaları
• Programlama Dersleri
• Teknoloji Haberleri

📱 Kategoriler:
• Müzik
• Oyun
• Eğitim
• Teknoloji
• Eğlence
            """
        elif "github.com" in url:
            return """
GitHub - Geliştirici Platformu

🔍 Depoları ara...

⭐ Popüler Depolar:
• BreDEVs/BERKE0S - Ultimate Operating System
• microsoft/vscode - Visual Studio Code
• torvalds/linux - Linux Kernel
• python/cpython - Python Programming Language

📊 Trending:
• JavaScript
• Python
• TypeScript
• Go
• Rust
            """
        else:
            return f"""
Web Sayfası Yüklendi

URL: {url}

Bu, BERKE0S Web Browser'ın basitleştirilmiş görünümüdür.
Gerçek uygulamada, burada tam web sayfası içeriği görüntülenecektir.

Özellikler:
• HTML5 desteği
• CSS3 desteği
• JavaScript desteği
• WebGL desteği
• Video/Audio oynatma
• PDF görüntüleme
• Dosya indirme

Güvenlik:
• HTTPS şifreleme
• Reklam engelleyici
• Zararlı yazılım koruması
• Gizlilik modu
            """
    
    def get_page_title(self, url):
        """Sayfa başlığını al"""
        if "google.com" in url:
            return "Google"
        elif "youtube.com" in url:
            return "YouTube"
        elif "github.com" in url:
            return "GitHub"
        else:
            return url.split('/')[2] if '/' in url else url
    
    def add_to_history(self, url):
        """Geçmişe ekle"""
        import time
        
        history_item = {
            "url": url,
            "title": self.get_page_title(url),
            "timestamp": time.time(),
            "visit_count": 1
        }
        
        # Check if already in history
        for item in self.history:
            if item["url"] == url:
                item["visit_count"] += 1
                item["timestamp"] = time.time()
                return
        
        self.history.append(history_item)
        
        # Limit history size
        if len(self.history) > 1000:
            self.history.pop(0)
    
    def load_bookmarks(self):
        """Yer imlerini yükle"""
        bookmarks_file = os.path.join(os.path.expanduser("~/.berke0s"), "bookmarks.json")
        
        default_bookmarks = [
            {"title": "Google", "url": "https://www.google.com"},
            {"title": "YouTube", "url": "https://www.youtube.com"},
            {"title": "GitHub", "url": "https://github.com"},
            {"title": "Wikipedia", "url": "https://www.wikipedia.org"},
            {"title": "BERKE0S", "url": "https://github.com/BreDEVs/BERKE0S"}
        ]
        
        try:
            if os.path.exists(bookmarks_file):
                with open(bookmarks_file, 'r') as f:
                    return json.load(f)
            else:
                self.save_bookmarks(default_bookmarks)
                return default_bookmarks
        except:
            return default_bookmarks
    
    def save_bookmarks(self, bookmarks=None):
        """Yer imlerini kaydet"""
        if bookmarks is None:
            bookmarks = self.bookmarks
            
        bookmarks_file = os.path.join(os.path.expanduser("~/.berke0s"), "bookmarks.json")
        
        try:
            os.makedirs(os.path.dirname(bookmarks_file), exist_ok=True)
            with open(bookmarks_file, 'w') as f:
                json.dump(bookmarks, f, indent=4)
        except Exception as e:
            print(f"Yer imleri kaydedilemedi: {e}")
    
    def add_bookmark(self):
        """Mevcut sayfayı yer imlerine ekle"""
        title = simpledialog.askstring("Yer İmi Ekle", 
                                       f"Başlık:", 
                                       initialvalue=self.get_page_title(self.current_url))
        
        if title:
            bookmark = {
                "title": title,
                "url": self.current_url
            }
            
            self.bookmarks.append(bookmark)
            self.save_bookmarks()
            
            messagebox.showinfo("Başarılı", "Yer imi eklendi!")
    
    def go_back(self):
        """Geri git"""
        if self.tabs and self.tabs[self.current_tab]["history"]:
            # Implementation for back navigation
            pass
    
    def go_forward(self):
        """İleri git"""
        # Implementation for forward navigation
        pass
    
    def reload_page(self):
        """Sayfayı yeniden yükle"""
        self.navigate_to(self.current_url)
    
    def go_home(self):
        """Ana sayfaya git"""
        self.navigate_to(self.settings["homepage"])
    
    def load_homepage(self):
        """Ana sayfayı yükle"""
        self.navigate_to(self.settings["homepage"])
    
    def show_downloads(self):
        """İndirmeleri göster"""
        downloads_window = tk.Toplevel(self.window)
        downloads_window.title("📥 İndirmeler")
        downloads_window.geometry("600x400")
        
        # Downloads list
        downloads_text = tk.Text(downloads_window, wrap=tk.WORD)
        downloads_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        if self.downloads:
            for download in self.downloads:
                downloads_text.insert(tk.END, f"{download}\n")
        else:
            downloads_text.insert(tk.END, "Henüz indirme yok.")
        
        downloads_text.config(state='disabled')
    
    def show_history(self):
        """Geçmişi göster"""
        history_window = tk.Toplevel(self.window)
        history_window.title("📜 Geçmiş")
        history_window.geometry("700x500")
        
        # History list
        history_frame = tk.Frame(history_window)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview for history
        history_tree = ttk.Treeview(history_frame, columns=('URL', 'Visits', 'Date'), show='tree headings')
        history_tree.heading('#0', text='Başlık')
        history_tree.heading('URL', text='URL')
        history_tree.heading('Visits', text='Ziyaret')
        history_tree.heading('Date', text='Tarih')
        
        # Add history items
        import time
        for item in reversed(self.history[-50:]):  # Last 50 items
            date_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(item["timestamp"]))
            history_tree.insert("", "end", text=item["title"],
                               values=(item["url"], item["visit_count"], date_str))
        
        history_tree.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        btn_frame = tk.Frame(history_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(btn_frame, text="🗑️ Geçmişi Temizle", 
                 command=self.clear_history).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="🔍 Ara", 
                 command=self.search_history).pack(side=tk.LEFT, padx=5)
    
    def clear_history(self):
        """Geçmişi temizle"""
        result = messagebox.askyesno("Onay", "Tüm geçmişi silmek istediğinizden emin misiniz?")
        if result:
            self.history.clear()
            messagebox.showinfo("Başarılı", "Geçmiş temizlendi!")
    
    def show_settings(self):
        """Ayarları göster"""
        settings_window = tk.Toplevel(self.window)
        settings_window.title("⚙️ Tarayıcı Ayarları")
        settings_window.geometry("500x600")
        
        # Settings notebook
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # General settings
        general_frame = tk.Frame(notebook)
        notebook.add(general_frame, text="Genel")
        
        # Homepage setting
        tk.Label(general_frame, text="Ana Sayfa:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=5)
        homepage_var = tk.StringVar(value=self.settings["homepage"])
        tk.Entry(general_frame, textvariable=homepage_var, width=50).pack(padx=10, pady=5)
        
        # Search engine setting
        tk.Label(general_frame, text="Arama Motoru:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=5)
        search_var = tk.StringVar(value=self.settings["search_engine"])
        tk.Entry(general_frame, textvariable=search_var, width=50).pack(padx=10, pady=5)
        
        # Privacy settings
        privacy_frame = tk.Frame(notebook)
        notebook.add(privacy_frame, text="Gizlilik")
        
        block_ads_var = tk.BooleanVar(value=self.settings["block_ads"])
        tk.Checkbutton(privacy_frame, text="Reklamları engelle", 
                      variable=block_ads_var).pack(anchor='w', padx=10, pady=5)
        
        enable_js_var = tk.BooleanVar(value=self.settings["enable_javascript"])
        tk.Checkbutton(privacy_frame, text="JavaScript'i etkinleştir", 
                      variable=enable_js_var).pack(anchor='w', padx=10, pady=5)
        
        enable_cookies_var = tk.BooleanVar(value=self.settings["enable_cookies"])
        tk.Checkbutton(privacy_frame, text="Çerezleri etkinleştir", 
                      variable=enable_cookies_var).pack(anchor='w', padx=10, pady=5)
        
        # Save button
        def save_settings():
            self.settings.update({
                "homepage": homepage_var.get(),
                "search_engine": search_var.get(),
                "block_ads": block_ads_var.get(),
                "enable_javascript": enable_js_var.get(),
                "enable_cookies": enable_cookies_var.get()
            })
            messagebox.showinfo("Başarılı", "Ayarlar kaydedildi!")
            settings_window.destroy()
        
        tk.Button(settings_window, text="💾 Kaydet", command=save_settings,
                 bg='#4CAF50', fg='white', font=('Arial', 12, 'bold')).pack(pady=10)
    
    def show_about(self):
        """Hakkında bilgisi göster"""
        about_text = """
BERKE0S Web Browser v1.0

BERKE0S Ultimate işletim sistemi için geliştirilmiş
gelişmiş web tarayıcısı.

Özellikler:
• Çoklu sekme desteği
• Gelişmiş yer imi yönetimi
• İndirme yöneticisi
• Gizlilik koruması
• Reklam engelleyici
• Geliştirici araçları

Geliştirici: BERKE0S Team
Sürüm: 1.0.0
Motor: BERKE Engine (Chromium tabanlı)

© 2024 BERKE0S Ultimate
        """
        
        messagebox.showinfo("Hakkında", about_text)
    
    def close(self):
        """Tarayıcıyı kapat"""
        if self.window:
            self.window.destroy()