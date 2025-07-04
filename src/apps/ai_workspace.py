"""
BERKE0S Ultimate - AI Workspace
Ollama entegrasyonu ile yerel AI asistan ve geliştirme ortamı
"""

import os
import sys
import json
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import subprocess
import threading
import requests
import time
import re

class AIWorkspace:
    """BERKE0S AI Workspace - Yerel AI Asistan"""
    
    def __init__(self, berke_os):
        self.berke_os = berke_os
        self.window = None
        self.ollama_running = False
        self.current_model = None
        self.chat_history = []
        self.available_models = []
        self.workspace_dir = os.path.join(os.path.expanduser("~/.berke0s"), "AI_Workspace")
        
        # AI settings
        self.settings = {
            "ollama_host": "http://localhost:11434",
            "default_model": "llama2",
            "temperature": 0.7,
            "max_tokens": 2048,
            "auto_save_chat": True,
            "code_highlighting": True,
            "voice_enabled": False
        }
        
        self.setup_workspace()
    
    def setup_workspace(self):
        """AI workspace dizinlerini oluştur"""
        directories = [
            self.workspace_dir,
            os.path.join(self.workspace_dir, "chats"),
            os.path.join(self.workspace_dir, "projects"),
            os.path.join(self.workspace_dir, "models"),
            os.path.join(self.workspace_dir, "exports")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def show(self):
        """AI Workspace'i göster"""
        try:
            self.window = tk.Toplevel()
            self.window.title("🤖 BERKE0S AI Workspace")
            self.window.geometry("1200x800")
            self.window.configure(bg='#1a1a1a')
            
            self.create_ai_interface()
            self.check_ollama_status()
            
        except Exception as e:
            print(f"AI Workspace hatası: {e}")
    
    def create_ai_interface(self):
        """AI arayüzünü oluştur"""
        # Menu bar
        self.create_menu_bar()
        
        # Toolbar
        self.create_toolbar()
        
        # Main content
        self.create_main_content()
        
        # Status bar
        self.create_status_bar()
    
    def create_menu_bar(self):
        """Menü çubuğunu oluştur"""
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Dosya", menu=file_menu)
        file_menu.add_command(label="Yeni Sohbet", command=self.new_chat, accelerator="Ctrl+N")
        file_menu.add_command(label="Sohbet Aç", command=self.open_chat, accelerator="Ctrl+O")
        file_menu.add_command(label="Sohbet Kaydet", command=self.save_chat, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Dışa Aktar", command=self.export_chat)
        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", command=self.window.destroy)
        
        # Models menu
        models_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Modeller", menu=models_menu)
        models_menu.add_command(label="Model İndir", command=self.download_model)
        models_menu.add_command(label="Model Yönetimi", command=self.manage_models)
        models_menu.add_command(label="Model Bilgileri", command=self.model_info)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Araçlar", menu=tools_menu)
        tools_menu.add_command(label="Kod Analizi", command=self.code_analysis)
        tools_menu.add_command(label="Proje Oluşturucu", command=self.project_generator)
        tools_menu.add_command(label="Dokümantasyon", command=self.generate_docs)
        tools_menu.add_separator()
        tools_menu.add_command(label="Ollama Ayarları", command=self.ollama_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Yardım", menu=help_menu)
        help_menu.add_command(label="AI Komutları", command=self.show_commands)
        help_menu.add_command(label="Hakkında", command=self.show_about)
    
    def create_toolbar(self):
        """Araç çubuğunu oluştur"""
        toolbar = tk.Frame(self.window, bg='#2a2a2a', height=50)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)
        
        # Model selection
        model_frame = tk.Frame(toolbar, bg='#2a2a2a')
        model_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Label(model_frame, text="Model:", bg='#2a2a2a', fg='white',
                font=('Arial', 10)).pack(side=tk.LEFT)
        
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(model_frame, textvariable=self.model_var,
                                       values=self.available_models, width=20)
        self.model_combo.pack(side=tk.LEFT, padx=5)
        self.model_combo.bind('<<ComboboxSelected>>', self.on_model_change)
        
        # Status indicator
        status_frame = tk.Frame(toolbar, bg='#2a2a2a')
        status_frame.pack(side=tk.LEFT, padx=20)
        
        self.status_indicator = tk.Label(status_frame, text="●", 
                                        font=('Arial', 16), bg='#2a2a2a', fg='red')
        self.status_indicator.pack(side=tk.LEFT)
        
        self.status_text = tk.Label(status_frame, text="Ollama Bağlantısı Yok",
                                   bg='#2a2a2a', fg='white', font=('Arial', 10))
        self.status_text.pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        action_frame = tk.Frame(toolbar, bg='#2a2a2a')
        action_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        tk.Button(action_frame, text="🔄 Yenile", command=self.refresh_models,
                 bg='#4CAF50', fg='white', relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=2)
        
        tk.Button(action_frame, text="⚙️ Ayarlar", command=self.show_settings,
                 bg='#2196F3', fg='white', relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=2)
        
        tk.Button(action_frame, text="🚀 Ollama Başlat", command=self.start_ollama,
                 bg='#FF9800', fg='white', relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=2)
    
    def create_main_content(self):
        """Ana içerik alanını oluştur"""
        main_frame = tk.Frame(self.window, bg='#1a1a1a')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Chat history and tools
        left_panel = tk.Frame(main_frame, bg='#2a2a2a', width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        left_panel.pack_propagate(False)
        
        self.create_left_panel(left_panel)
        
        # Main chat area
        chat_frame = tk.Frame(main_frame, bg='#1a1a1a')
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        self.create_chat_area(chat_frame)
        
        # Right panel - Code and tools
        right_panel = tk.Frame(main_frame, bg='#2a2a2a', width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)
        
        self.create_right_panel(right_panel)
    
    def create_left_panel(self, parent):
        """Sol panel oluştur"""
        # Chat history
        history_frame = tk.LabelFrame(parent, text="Sohbet Geçmişi",
                                     bg='#2a2a2a', fg='white',
                                     font=('Arial', 10, 'bold'))
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.chat_list = tk.Listbox(history_frame, bg='#1a1a1a', fg='white',
                                   selectbackground='#4CAF50', height=10)
        self.chat_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Quick actions
        actions_frame = tk.LabelFrame(parent, text="Hızlı Eylemler",
                                     bg='#2a2a2a', fg='white',
                                     font=('Arial', 10, 'bold'))
        actions_frame.pack(fill=tk.X, padx=5, pady=5)
        
        quick_actions = [
            ("💡 Kod Açıkla", self.explain_code),
            ("🔧 Kod Düzelt", self.fix_code),
            ("📝 Dokümantasyon", self.generate_docs),
            ("🧪 Test Yaz", self.generate_tests),
            ("🎨 UI Tasarla", self.design_ui),
            ("📊 Veri Analizi", self.analyze_data)
        ]
        
        for text, command in quick_actions:
            tk.Button(actions_frame, text=text, command=command,
                     bg='#3a3a3a', fg='white', relief=tk.FLAT,
                     width=20, anchor='w').pack(fill=tk.X, padx=5, pady=2)
        
        # AI Templates
        templates_frame = tk.LabelFrame(parent, text="AI Şablonları",
                                       bg='#2a2a2a', fg='white',
                                       font=('Arial', 10, 'bold'))
        templates_frame.pack(fill=tk.X, padx=5, pady=5)
        
        templates = [
            "Python Geliştirici",
            "Web Tasarımcısı", 
            "Veri Analisti",
            "DevOps Uzmanı",
            "UI/UX Tasarımcı",
            "Sistem Yöneticisi"
        ]
        
        self.template_var = tk.StringVar()
        template_combo = ttk.Combobox(templates_frame, textvariable=self.template_var,
                                     values=templates, width=18)
        template_combo.pack(padx=5, pady=5)
        
        tk.Button(templates_frame, text="Şablonu Uygula",
                 command=self.apply_template,
                 bg='#9C27B0', fg='white', relief=tk.FLAT).pack(pady=5)
    
    def create_chat_area(self, parent):
        """Sohbet alanını oluştur"""
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            parent, bg='#1a1a1a', fg='white', font=('Arial', 11),
            wrap=tk.WORD, state='disabled'
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Configure text tags for styling
        self.chat_display.tag_configure("user", foreground="#4CAF50", font=('Arial', 11, 'bold'))
        self.chat_display.tag_configure("ai", foreground="#2196F3", font=('Arial', 11, 'bold'))
        self.chat_display.tag_configure("code", background="#2a2a2a", foreground="#FFD700", font=('Courier', 10))
        self.chat_display.tag_configure("error", foreground="#f44336")
        
        # Input area
        input_frame = tk.Frame(parent, bg='#1a1a1a')
        input_frame.pack(fill=tk.X)
        
        # Input text area
        self.input_text = tk.Text(input_frame, height=4, bg='#2a2a2a', fg='white',
                                 font=('Arial', 11), wrap=tk.WORD)
        self.input_text.pack(fill=tk.X, pady=(0, 10))
        
        # Input controls
        controls_frame = tk.Frame(input_frame, bg='#1a1a1a')
        controls_frame.pack(fill=tk.X)
        
        # Send button
        self.send_button = tk.Button(controls_frame, text="📤 Gönder",
                                    command=self.send_message,
                                    bg='#4CAF50', fg='white', font=('Arial', 11, 'bold'),
                                    relief=tk.FLAT, padx=20)
        self.send_button.pack(side=tk.RIGHT, padx=5)
        
        # Clear button
        tk.Button(controls_frame, text="🗑️ Temizle", command=self.clear_chat,
                 bg='#f44336', fg='white', relief=tk.FLAT, padx=15).pack(side=tk.RIGHT, padx=5)
        
        # File upload button
        tk.Button(controls_frame, text="📎 Dosya", command=self.upload_file,
                 bg='#FF9800', fg='white', relief=tk.FLAT, padx=15).pack(side=tk.LEFT, padx=5)
        
        # Voice input button (if enabled)
        if self.settings["voice_enabled"]:
            tk.Button(controls_frame, text="🎤 Ses", command=self.voice_input,
                     bg='#9C27B0', fg='white', relief=tk.FLAT, padx=15).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        self.input_text.bind('<Control-Return>', lambda e: self.send_message())
    
    def create_right_panel(self, parent):
        """Sağ panel oluştur"""
        # Code editor
        code_frame = tk.LabelFrame(parent, text="Kod Editörü",
                                  bg='#2a2a2a', fg='white',
                                  font=('Arial', 10, 'bold'))
        code_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.code_editor = scrolledtext.ScrolledText(
            code_frame, bg='#1a1a1a', fg='white', font=('Courier', 10),
            wrap=tk.NONE
        )
        self.code_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Code controls
        code_controls = tk.Frame(code_frame, bg='#2a2a2a')
        code_controls.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(code_controls, text="▶️ Çalıştır", command=self.run_code,
                 bg='#4CAF50', fg='white', relief=tk.FLAT, width=8).pack(side=tk.LEFT, padx=2)
        
        tk.Button(code_controls, text="💾 Kaydet", command=self.save_code,
                 bg='#2196F3', fg='white', relief=tk.FLAT, width=8).pack(side=tk.LEFT, padx=2)
        
        tk.Button(code_controls, text="📋 Kopyala", command=self.copy_code,
                 bg='#FF9800', fg='white', relief=tk.FLAT, width=8).pack(side=tk.LEFT, padx=2)
        
        # Project explorer
        project_frame = tk.LabelFrame(parent, text="Proje Gezgini",
                                     bg='#2a2a2a', fg='white',
                                     font=('Arial', 10, 'bold'))
        project_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.project_tree = ttk.Treeview(project_frame, height=8)
        self.project_tree.pack(fill=tk.X, padx=5, pady=5)
        
        # Load project structure
        self.load_project_structure()
    
    def create_status_bar(self):
        """Durum çubuğunu oluştur"""
        status_frame = tk.Frame(self.window, bg='#2a2a2a', height=25)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="Hazır", bg='#2a2a2a', fg='white',
                                    font=('Arial', 9), anchor='w')
        self.status_label.pack(side=tk.LEFT, padx=10, pady=3)
        
        # Token count
        self.token_label = tk.Label(status_frame, text="Tokens: 0", bg='#2a2a2a', fg='white',
                                   font=('Arial', 9))
        self.token_label.pack(side=tk.RIGHT, padx=10, pady=3)
    
    def check_ollama_status(self):
        """Ollama durumunu kontrol et"""
        def check():
            try:
                response = requests.get(f"{self.settings['ollama_host']}/api/tags", timeout=5)
                if response.status_code == 200:
                    self.ollama_running = True
                    self.status_indicator.config(fg='green')
                    self.status_text.config(text="Ollama Bağlı")
                    
                    # Load available models
                    models_data = response.json()
                    self.available_models = [model['name'] for model in models_data.get('models', [])]
                    self.model_combo['values'] = self.available_models
                    
                    if self.available_models and not self.current_model:
                        self.current_model = self.available_models[0]
                        self.model_var.set(self.current_model)
                else:
                    self.ollama_running = False
                    self.status_indicator.config(fg='red')
                    self.status_text.config(text="Ollama Bağlantı Hatası")
                    
            except requests.exceptions.RequestException:
                self.ollama_running = False
                self.status_indicator.config(fg='red')
                self.status_text.config(text="Ollama Çalışmıyor")
        
        threading.Thread(target=check, daemon=True).start()
    
    def start_ollama(self):
        """Ollama'yı başlat"""
        def start():
            try:
                self.status_label.config(text="Ollama başlatılıyor...")
                
                # Try to start Ollama
                process = subprocess.Popen(['ollama', 'serve'], 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE)
                
                # Wait a moment for startup
                time.sleep(3)
                
                # Check if it's running
                self.check_ollama_status()
                
                if self.ollama_running:
                    self.status_label.config(text="Ollama başarıyla başlatıldı")
                else:
                    self.status_label.config(text="Ollama başlatılamadı")
                    
            except FileNotFoundError:
                self.status_label.config(text="Ollama bulunamadı - Kurulum gerekli")
                self.install_ollama()
            except Exception as e:
                self.status_label.config(text=f"Hata: {str(e)}")
        
        threading.Thread(target=start, daemon=True).start()
    
    def install_ollama(self):
        """Ollama kurulumunu başlat"""
        result = messagebox.askyesno("Ollama Kurulumu", 
                                    "Ollama kurulu değil. Şimdi kurmak ister misiniz?")
        
        if result:
            def install():
                try:
                    self.status_label.config(text="Ollama kuruluyor...")
                    
                    # Download and install Ollama
                    subprocess.run(['curl', '-fsSL', 'https://ollama.ai/install.sh'], 
                                 capture_output=True, check=True)
                    
                    self.status_label.config(text="Ollama kurulumu tamamlandı")
                    
                    # Try to start after installation
                    self.start_ollama()
                    
                except Exception as e:
                    self.status_label.config(text=f"Kurulum hatası: {str(e)}")
            
            threading.Thread(target=install, daemon=True).start()
    
    def send_message(self):
        """Mesaj gönder"""
        message = self.input_text.get('1.0', tk.END).strip()
        if not message:
            return
        
        if not self.ollama_running:
            messagebox.showwarning("Uyarı", "Ollama çalışmıyor. Lütfen önce Ollama'yı başlatın.")
            return
        
        if not self.current_model:
            messagebox.showwarning("Uyarı", "Lütfen bir model seçin.")
            return
        
        # Add user message to chat
        self.add_message("Kullanıcı", message, "user")
        
        # Clear input
        self.input_text.delete('1.0', tk.END)
        
        # Send to AI
        self.send_to_ai(message)
    
    def add_message(self, sender, message, tag):
        """Sohbete mesaj ekle"""
        self.chat_display.config(state='normal')
        
        # Add timestamp
        timestamp = time.strftime("%H:%M")
        
        # Add sender and message
        self.chat_display.insert(tk.END, f"\n[{timestamp}] {sender}:\n", tag)
        
        # Process message for code blocks
        if "```" in message:
            parts = message.split("```")
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    # Regular text
                    self.chat_display.insert(tk.END, part)
                else:
                    # Code block
                    self.chat_display.insert(tk.END, part, "code")
        else:
            self.chat_display.insert(tk.END, message)
        
        self.chat_display.insert(tk.END, "\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)
        
        # Add to history
        self.chat_history.append({
            "sender": sender,
            "message": message,
            "timestamp": time.time()
        })
    
    def send_to_ai(self, message):
        """AI'ya mesaj gönder"""
        def ai_request():
            try:
                self.send_button.config(state='disabled', text="🤔 Düşünüyor...")
                self.status_label.config(text="AI yanıt oluşturuyor...")
                
                # Prepare request
                data = {
                    "model": self.current_model,
                    "prompt": message,
                    "stream": False,
                    "options": {
                        "temperature": self.settings["temperature"],
                        "num_predict": self.settings["max_tokens"]
                    }
                }
                
                # Send request to Ollama
                response = requests.post(
                    f"{self.settings['ollama_host']}/api/generate",
                    json=data,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result.get('response', 'Yanıt alınamadı')
                    
                    # Add AI response to chat
                    self.add_message("AI", ai_response, "ai")
                    
                    # Extract code if present
                    self.extract_code_from_response(ai_response)
                    
                    self.status_label.config(text="Yanıt alındı")
                else:
                    self.add_message("Sistem", f"Hata: {response.status_code}", "error")
                    self.status_label.config(text="AI yanıt hatası")
                
            except requests.exceptions.Timeout:
                self.add_message("Sistem", "Zaman aşımı - AI yanıt veremedi", "error")
                self.status_label.config(text="Zaman aşımı")
            except Exception as e:
                self.add_message("Sistem", f"Hata: {str(e)}", "error")
                self.status_label.config(text="Bağlantı hatası")
            finally:
                self.send_button.config(state='normal', text="📤 Gönder")
        
        threading.Thread(target=ai_request, daemon=True).start()
    
    def extract_code_from_response(self, response):
        """AI yanıtından kodu çıkar ve editöre ekle"""
        code_blocks = re.findall(r'```(?:\w+)?\n(.*?)\n```', response, re.DOTALL)
        
        if code_blocks:
            # Add the first code block to the editor
            code = code_blocks[0].strip()
            self.code_editor.delete('1.0', tk.END)
            self.code_editor.insert('1.0', code)
    
    def on_model_change(self, event=None):
        """Model değiştiğinde"""
        self.current_model = self.model_var.get()
        self.status_label.config(text=f"Model değiştirildi: {self.current_model}")
    
    def refresh_models(self):
        """Model listesini yenile"""
        self.check_ollama_status()
    
    def new_chat(self):
        """Yeni sohbet başlat"""
        if self.chat_history:
            result = messagebox.askyesno("Yeni Sohbet", "Mevcut sohbeti kaydetmek ister misiniz?")
            if result:
                self.save_chat()
        
        self.clear_chat()
        self.status_label.config(text="Yeni sohbet başlatıldı")
    
    def clear_chat(self):
        """Sohbeti temizle"""
        self.chat_display.config(state='normal')
        self.chat_display.delete('1.0', tk.END)
        self.chat_display.config(state='disabled')
        self.chat_history.clear()
    
    def save_chat(self):
        """Sohbeti kaydet"""
        if not self.chat_history:
            messagebox.showinfo("Bilgi", "Kaydedilecek sohbet yok.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=os.path.join(self.workspace_dir, "chats")
        )
        
        if filename:
            try:
                chat_data = {
                    "model": self.current_model,
                    "timestamp": time.time(),
                    "history": self.chat_history
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(chat_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Başarılı", "Sohbet kaydedildi!")
                
            except Exception as e:
                messagebox.showerror("Hata", f"Sohbet kaydedilemedi: {str(e)}")
    
    def open_chat(self):
        """Sohbet aç"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=os.path.join(self.workspace_dir, "chats")
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    chat_data = json.load(f)
                
                self.clear_chat()
                self.chat_history = chat_data.get('history', [])
                
                # Restore chat display
                for item in self.chat_history:
                    tag = "user" if item['sender'] == "Kullanıcı" else "ai"
                    self.add_message(item['sender'], item['message'], tag)
                
                messagebox.showinfo("Başarılı", "Sohbet yüklendi!")
                
            except Exception as e:
                messagebox.showerror("Hata", f"Sohbet açılamadı: {str(e)}")
    
    def run_code(self):
        """Kod editöründeki kodu çalıştır"""
        code = self.code_editor.get('1.0', tk.END).strip()
        if not code:
            messagebox.showinfo("Bilgi", "Çalıştırılacak kod yok.")
            return
        
        # Determine language and run accordingly
        if code.startswith('#!/usr/bin/env python') or 'import ' in code or 'def ' in code:
            self.run_python_code(code)
        elif 'function ' in code or 'console.log' in code:
            self.run_javascript_code(code)
        else:
            # Default to Python
            self.run_python_code(code)
    
    def run_python_code(self, code):
        """Python kodunu çalıştır"""
        def run():
            try:
                # Create temporary file
                temp_file = os.path.join(self.workspace_dir, "temp_code.py")
                with open(temp_file, 'w') as f:
                    f.write(code)
                
                # Run the code
                result = subprocess.run([sys.executable, temp_file], 
                                      capture_output=True, text=True, timeout=30)
                
                # Show result
                if result.stdout:
                    self.add_message("Çıktı", result.stdout, "ai")
                if result.stderr:
                    self.add_message("Hata", result.stderr, "error")
                
                # Clean up
                os.remove(temp_file)
                
            except subprocess.TimeoutExpired:
                self.add_message("Sistem", "Kod çalıştırma zaman aşımına uğradı", "error")
            except Exception as e:
                self.add_message("Sistem", f"Kod çalıştırma hatası: {str(e)}", "error")
        
        threading.Thread(target=run, daemon=True).start()
    
    def run_javascript_code(self, code):
        """JavaScript kodunu çalıştır"""
        try:
            # Create temporary HTML file with the JavaScript
            temp_file = os.path.join(self.workspace_dir, "temp_code.html")
            html_content = f"""
<!DOCTYPE html>
<html>
<head><title>JavaScript Test</title></head>
<body>
<script>
{code}
</script>
</body>
</html>
"""
            with open(temp_file, 'w') as f:
                f.write(html_content)
            
            # Open in browser
            subprocess.run(['xdg-open', temp_file])
            
            self.add_message("Sistem", "JavaScript kodu tarayıcıda açıldı", "ai")
            
        except Exception as e:
            self.add_message("Sistem", f"JavaScript çalıştırma hatası: {str(e)}", "error")
    
    def save_code(self):
        """Kodu dosyaya kaydet"""
        code = self.code_editor.get('1.0', tk.END).strip()
        if not code:
            messagebox.showinfo("Bilgi", "Kaydedilecek kod yok.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[
                ("Python files", "*.py"),
                ("JavaScript files", "*.js"),
                ("HTML files", "*.html"),
                ("All files", "*.*")
            ],
            initialdir=os.path.join(self.workspace_dir, "projects")
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                messagebox.showinfo("Başarılı", "Kod kaydedildi!")
                self.load_project_structure()
                
            except Exception as e:
                messagebox.showerror("Hata", f"Kod kaydedilemedi: {str(e)}")
    
    def copy_code(self):
        """Kodu panoya kopyala"""
        code = self.code_editor.get('1.0', tk.END).strip()
        if code:
            self.window.clipboard_clear()
            self.window.clipboard_append(code)
            self.status_label.config(text="Kod panoya kopyalandı")
    
    def load_project_structure(self):
        """Proje yapısını yükle"""
        # Clear existing items
        for item in self.project_tree.get_children():
            self.project_tree.delete(item)
        
        # Load project files
        projects_dir = os.path.join(self.workspace_dir, "projects")
        if os.path.exists(projects_dir):
            for item in os.listdir(projects_dir):
                item_path = os.path.join(projects_dir, item)
                if os.path.isfile(item_path):
                    self.project_tree.insert("", "end", text=item, values=(item_path,))
    
    # Quick action methods
    def explain_code(self):
        """Kod açıklama şablonu"""
        self.input_text.delete('1.0', tk.END)
        self.input_text.insert('1.0', "Lütfen aşağıdaki kodu açıkla:\n\n[Kodunuzu buraya yapıştırın]")
    
    def fix_code(self):
        """Kod düzeltme şablonu"""
        self.input_text.delete('1.0', tk.END)
        self.input_text.insert('1.0', "Bu kodda hata var, düzeltir misin?\n\n[Hatalı kodunuzu buraya yapıştırın]")
    
    def generate_docs(self):
        """Dokümantasyon oluşturma şablonu"""
        self.input_text.delete('1.0', tk.END)
        self.input_text.insert('1.0', "Bu kod için dokümantasyon oluştur:\n\n[Kodunuzu buraya yapıştırın]")
    
    def generate_tests(self):
        """Test oluşturma şablonu"""
        self.input_text.delete('1.0', tk.END)
        self.input_text.insert('1.0', "Bu fonksiyon için unit test yaz:\n\n[Fonksiyonunuzu buraya yapıştırın]")
    
    def design_ui(self):
        """UI tasarım şablonu"""
        self.input_text.delete('1.0', tk.END)
        self.input_text.insert('1.0', "Şu özelliklere sahip bir web sayfası tasarla:\n\n[Özelliklerinizi buraya yazın]")
    
    def analyze_data(self):
        """Veri analizi şablonu"""
        self.input_text.delete('1.0', tk.END)
        self.input_text.insert('1.0', "Bu veriyi analiz et ve görselleştir:\n\n[Verinizi buraya yapıştırın]")
    
    def apply_template(self):
        """AI şablonu uygula"""
        template = self.template_var.get()
        if not template:
            return
        
        templates = {
            "Python Geliştirici": "Sen deneyimli bir Python geliştiricisisin. Python kodu yazma, hata ayıklama ve optimizasyon konularında uzmanısın.",
            "Web Tasarımcısı": "Sen kreatif bir web tasarımcısısın. HTML, CSS, JavaScript ve modern web teknolojilerinde uzmanısın.",
            "Veri Analisti": "Sen veri analizi uzmanısın. Python, pandas, numpy ve veri görselleştirme konularında uzmanısın.",
            "DevOps Uzmanı": "Sen DevOps uzmanısın. Docker, Kubernetes, CI/CD ve bulut teknolojilerinde uzmanısın.",
            "UI/UX Tasarımcı": "Sen kullanıcı deneyimi uzmanısın. Kullanıcı arayüzü tasarımı ve kullanılabilirlik konularında uzmanısın.",
            "Sistem Yöneticisi": "Sen sistem yöneticisisin. Linux, ağ yönetimi ve sistem güvenliği konularında uzmanısın."
        }
        
        template_text = templates.get(template, "")
        if template_text:
            self.input_text.delete('1.0', tk.END)
            self.input_text.insert('1.0', template_text + "\n\nNasıl yardımcı olabilirim?")
    
    def show_settings(self):
        """AI ayarlarını göster"""
        settings_window = tk.Toplevel(self.window)
        settings_window.title("AI Workspace Ayarları")
        settings_window.geometry("500x400")
        settings_window.configure(bg='#2a2a2a')
        
        # Ollama settings
        ollama_frame = tk.LabelFrame(settings_window, text="Ollama Ayarları",
                                    bg='#2a2a2a', fg='white')
        ollama_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(ollama_frame, text="Host:", bg='#2a2a2a', fg='white').pack(anchor='w', padx=10)
        host_var = tk.StringVar(value=self.settings["ollama_host"])
        tk.Entry(ollama_frame, textvariable=host_var, width=40).pack(padx=10, pady=5)
        
        # AI parameters
        params_frame = tk.LabelFrame(settings_window, text="AI Parametreleri",
                                    bg='#2a2a2a', fg='white')
        params_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(params_frame, text="Temperature:", bg='#2a2a2a', fg='white').pack(anchor='w', padx=10)
        temp_var = tk.DoubleVar(value=self.settings["temperature"])
        tk.Scale(params_frame, from_=0.0, to=2.0, resolution=0.1, orient=tk.HORIZONTAL,
                variable=temp_var, bg='#2a2a2a', fg='white').pack(fill=tk.X, padx=10)
        
        tk.Label(params_frame, text="Max Tokens:", bg='#2a2a2a', fg='white').pack(anchor='w', padx=10)
        tokens_var = tk.IntVar(value=self.settings["max_tokens"])
        tk.Scale(params_frame, from_=512, to=8192, resolution=256, orient=tk.HORIZONTAL,
                variable=tokens_var, bg='#2a2a2a', fg='white').pack(fill=tk.X, padx=10)
        
        # Save button
        def save_settings():
            self.settings.update({
                "ollama_host": host_var.get(),
                "temperature": temp_var.get(),
                "max_tokens": tokens_var.get()
            })
            messagebox.showinfo("Başarılı", "Ayarlar kaydedildi!")
            settings_window.destroy()
        
        tk.Button(settings_window, text="Kaydet", command=save_settings,
                 bg='#4CAF50', fg='white', font=('Arial', 12, 'bold')).pack(pady=20)
    
    def close(self):
        """AI Workspace'i kapat"""
        if self.window:
            self.window.destroy()