import os
import requests
import threading
import queue
import time
from urllib.parse import urljoin, urlparse, urldefrag
from bs4 import BeautifulSoup
import hashlib
import webbrowser
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import tkinter.font as tkfont
import sys
import json
import re
import shutil
from pathlib import Path

class WebDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌐 Web Cloner Pro - Sitios Funcionales")
        self.root.geometry("1200x800")
        
        # Tema moderno profesional
        self.bg_color = '#121212'
        self.fg_color = '#e0e0e0'
        self.accent_color = '#6200ee'
        self.secondary_color = '#1e1e1e'
        self.success_color = '#00c853'
        self.warning_color = '#ffab00'
        self.error_color = '#ff5252'
        self.highlight_color = '#bb86fc'
        
        self.root.configure(bg=self.bg_color)
        
        # Variables de estado
        self.is_downloading = False
        self.download_thread = None
        self.download_queue = queue.Queue()
        self.downloaded_files_tree = {}
        
        # Configuración por defecto
        self.download_mode = tk.StringVar(value="full")  # full, interactive, static
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Fuentes modernas
        self.title_font = tkfont.Font(family="Segoe UI", size=20, weight="bold")
        self.heading_font = tkfont.Font(family="Segoe UI", size=12, weight="bold")
        self.label_font = tkfont.Font(family="Segoe UI", size=10)
        self.button_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.mono_font = tkfont.Font(family="Consolas", size=9)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(header_frame, 
                              text="🌐 WEB CLONER PRO", 
                              font=self.title_font, 
                              bg=self.bg_color, 
                              fg=self.highlight_color)
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(header_frame, 
                                 text="Clona sitios web manteniendo funcionalidad",
                                 font=self.label_font, 
                                 bg=self.bg_color, 
                                 fg=self.fg_color)
        subtitle_label.pack(side=tk.LEFT, padx=(15, 0))
        
        # Frame de configuración principal
        main_config_frame = tk.Frame(main_frame, bg=self.secondary_color)
        main_config_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Sección de URL y modo
        url_frame = tk.Frame(main_config_frame, bg=self.secondary_color)
        url_frame.pack(fill=tk.X, padx=20, pady=15)
        
        # URL input
        tk.Label(url_frame, text="URL del sitio:", 
                font=self.heading_font, 
                bg=self.secondary_color, 
                fg=self.fg_color).pack(anchor=tk.W)
        
        url_input_frame = tk.Frame(url_frame, bg=self.secondary_color)
        url_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.url_entry = tk.Entry(url_input_frame, 
                                 font=self.label_font, 
                                 width=70,
                                 bg='#2d2d2d', 
                                 fg=self.fg_color,
                                 insertbackground=self.fg_color,
                                 relief=tk.FLAT)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.url_entry.insert(0, "https://ejemplo.com")
        
        # Botones de URL
        tk.Button(url_input_frame, text="📋 Pegar", 
                 command=self.paste_url,
                 bg=self.accent_color, 
                 fg='white',
                 font=self.button_font,
                 relief=tk.FLAT,
                 cursor="hand2",
                 padx=15).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(url_input_frame, text="🌐 Probar", 
                 command=self.test_url,
                 bg='#2196f3', 
                 fg='white',
                 font=self.button_font,
                 relief=tk.FLAT,
                 cursor="hand2",
                 padx=15).pack(side=tk.LEFT)
        
        # Modo de descarga
        mode_frame = tk.Frame(url_frame, bg=self.secondary_color)
        mode_frame.pack(fill=tk.X, pady=(15, 0))
        
        tk.Label(mode_frame, text="Modo de clonado:", 
                font=self.heading_font, 
                bg=self.secondary_color, 
                fg=self.fg_color).pack(anchor=tk.W)
        
        mode_options_frame = tk.Frame(mode_frame, bg=self.secondary_color)
        mode_options_frame.pack(fill=tk.X, pady=(5, 0))
        
        modes = [
            ("🎯 Completo (HTML+CSS+JS+Recursos)", "full"),
            ("🤖 Interactivo (Formularios, Botones)", "interactive"),
            ("📄 Estático (Solo HTML/CSS)", "static"),
            ("⚡ Rápido (HTML básico)", "fast")
        ]
        
        for text, mode in modes:
            rb = tk.Radiobutton(mode_options_frame, 
                               text=text,
                               variable=self.download_mode,
                               value=mode,
                               font=self.label_font,
                               bg=self.secondary_color,
                               fg=self.fg_color,
                               selectcolor=self.accent_color,
                               activebackground=self.secondary_color,
                               activeforeground=self.fg_color)
            rb.pack(side=tk.LEFT, padx=(0, 20))
        
        # Sección de opciones avanzadas
        options_frame = tk.Frame(main_config_frame, bg=self.secondary_color)
        options_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Grid de opciones
        options_grid = tk.Frame(options_frame, bg=self.secondary_color)
        options_grid.pack(fill=tk.X)
        
        # Columna izquierda
        left_col = tk.Frame(options_grid, bg=self.secondary_color)
        left_col.grid(row=0, column=0, sticky=tk.W, padx=(0, 50))
        
        # Profundidad
        tk.Label(left_col, text="Profundidad de navegación:", 
                font=self.label_font, 
                bg=self.secondary_color, 
                fg=self.fg_color).pack(anchor=tk.W)
        
        depth_frame = tk.Frame(left_col, bg=self.secondary_color)
        depth_frame.pack(fill=tk.X, pady=(5, 15))
        
        self.depth_var = tk.IntVar(value=2)
        depth_spin = tk.Spinbox(depth_frame, 
                               from_=1, to=5, 
                               textvariable=self.depth_var,
                               font=self.label_font, 
                               width=10,
                               bg='#2d2d2d', 
                               fg=self.fg_color,
                               buttonbackground=self.accent_color,
                               relief=tk.FLAT)
        depth_spin.pack(side=tk.LEFT)
        
        tk.Label(depth_frame, text=" niveles", 
                font=self.label_font, 
                bg=self.secondary_color, 
                fg='#888888').pack(side=tk.LEFT, padx=(5, 0))
        
        # Hilos
        tk.Label(left_col, text="Hilos simultáneos:", 
                font=self.label_font, 
                bg=self.secondary_color, 
                fg=self.fg_color).pack(anchor=tk.W)
        
        threads_frame = tk.Frame(left_col, bg=self.secondary_color)
        threads_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.threads_var = tk.IntVar(value=5)
        threads_spin = tk.Spinbox(threads_frame, 
                                 from_=1, to=20, 
                                 textvariable=self.threads_var,
                                 font=self.label_font, 
                                 width=10,
                                 bg='#2d2d2d', 
                                 fg=self.fg_color,
                                 buttonbackground=self.accent_color,
                                 relief=tk.FLAT)
        threads_spin.pack(side=tk.LEFT)
        
        # Columna derecha
        right_col = tk.Frame(options_grid, bg=self.secondary_color)
        right_col.grid(row=0, column=1, sticky=tk.W)
        
        # Checkboxes de funcionalidad
        self.js_var = tk.BooleanVar(value=True)
        js_check = tk.Checkbutton(right_col, 
                                 text="✅ Mantener JavaScript",
                                 variable=self.js_var,
                                 font=self.label_font, 
                                 bg=self.secondary_color, 
                                 fg=self.fg_color,
                                 selectcolor=self.accent_color,
                                 activebackground=self.secondary_color)
        js_check.pack(anchor=tk.W, pady=(0, 10))
        
        self.forms_var = tk.BooleanVar(value=True)
        forms_check = tk.Checkbutton(right_col, 
                                    text="✅ Mantener formularios activos",
                                    variable=self.forms_var,
                                    font=self.label_font, 
                                    bg=self.secondary_color, 
                                    fg=self.fg_color,
                                    selectcolor=self.accent_color,
                                    activebackground=self.secondary_color)
        forms_check.pack(anchor=tk.W, pady=(0, 10))
        
        self.ajax_var = tk.BooleanVar(value=False)
        ajax_check = tk.Checkbutton(right_col, 
                                   text="⚠️ Intentar mantener AJAX (Experimental)",
                                   variable=self.ajax_var,
                                   font=self.label_font, 
                                   bg=self.secondary_color, 
                                   fg=self.fg_color,
                                   selectcolor=self.accent_color,
                                   activebackground=self.secondary_color)
        ajax_check.pack(anchor=tk.W, pady=(0, 10))
        
        # Frame de destino y botones
        dest_button_frame = tk.Frame(main_config_frame, bg=self.secondary_color)
        dest_button_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Destino
        tk.Label(dest_button_frame, text="Carpeta destino:", 
                font=self.heading_font, 
                bg=self.secondary_color, 
                fg=self.fg_color).pack(anchor=tk.W)
        
        dest_input_frame = tk.Frame(dest_button_frame, bg=self.secondary_color)
        dest_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.folder_var = tk.StringVar()
        default_folder = os.path.join(os.path.expanduser("~"), "WebClones")
        self.folder_var.set(default_folder)
        
        self.folder_entry = tk.Entry(dest_input_frame, 
                                    textvariable=self.folder_var,
                                    font=self.label_font, 
                                    width=60,
                                    bg='#2d2d2d', 
                                    fg=self.fg_color,
                                    insertbackground=self.fg_color,
                                    relief=tk.FLAT)
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Button(dest_input_frame, text="📁 Explorar", 
                 command=self.browse_folder,
                 bg=self.accent_color, 
                 fg='white',
                 font=self.button_font,
                 relief=tk.FLAT,
                 cursor="hand2",
                 padx=15).pack(side=tk.LEFT, padx=(0, 10))
        
        # Botones de control principales
        control_frame = tk.Frame(main_frame, bg=self.bg_color)
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.start_button = tk.Button(control_frame, 
                                     text="🚀 INICIAR CLONADO", 
                                     command=self.start_download,
                                     bg=self.success_color, 
                                     fg='white',
                                     font=self.button_font,
                                     relief=tk.FLAT,
                                     cursor="hand2",
                                     padx=30, pady=12)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = tk.Button(control_frame, 
                                    text="⏹ DETENER", 
                                    command=self.stop_download,
                                    bg=self.error_color, 
                                    fg='white',
                                    font=self.button_font,
                                    relief=tk.FLAT,
                                    cursor="hand2",
                                    state=tk.DISABLED,
                                    padx=30, pady=12)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(control_frame, 
                 text="🔧 PREVIEW LOCAL", 
                 command=self.preview_local,
                 bg='#2196f3', 
                 fg='white',
                 font=self.button_font,
                 relief=tk.FLAT,
                 cursor="hand2",
                 padx=30, pady=12).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(control_frame, 
                 text="📊 REPORTE", 
                 command=self.generate_report,
                 bg=self.warning_color, 
                 fg='white',
                 font=self.button_font,
                 relief=tk.FLAT,
                 cursor="hand2",
                 padx=30, pady=12).pack(side=tk.LEFT)
        
        # Panel de progreso
        progress_frame = tk.Frame(main_frame, bg=self.secondary_color)
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Barra de progreso múltiple
        self.progress_bars = {}
        progress_types = [
            ("html", "📄 Páginas HTML", self.highlight_color),
            ("css", "🎨 Estilos CSS", "#2196f3"),
            ("js", "⚙️ Scripts JS", "#ff9800"),
            ("images", "🖼️ Imágenes", "#4caf50"),
            ("other", "📦 Otros recursos", "#9c27b0")
        ]
        
        for i, (key, label, color) in enumerate(progress_types):
            type_frame = tk.Frame(progress_frame, bg=self.secondary_color)
            type_frame.pack(fill=tk.X, padx=20, pady=(10 if i == 0 else 5))
            
            tk.Label(type_frame, text=label, 
                    font=self.label_font, 
                    bg=self.secondary_color, 
                    fg=color, width=15).pack(side=tk.LEFT)
            
            bar = ttk.Progressbar(type_frame, mode='determinate', length=400)
            bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
            self.progress_bars[key] = bar
            
            self.progress_bars[f"{key}_label"] = tk.Label(type_frame, text="0/0", 
                                                         font=self.mono_font, 
                                                         bg=self.secondary_color, 
                                                         fg='#888888', width=10)
            self.progress_bars[f"{key}_label"].pack(side=tk.LEFT, padx=(10, 0))
        
        # Información general
        info_frame = tk.Frame(progress_frame, bg=self.secondary_color)
        info_frame.pack(fill=tk.X, padx=20, pady=(5, 15))
        
        self.status_label = tk.Label(info_frame, 
                                    text="✅ Listo para clonar sitio web", 
                                    font=self.heading_font, 
                                    bg=self.secondary_color, 
                                    fg=self.success_color)
        self.status_label.pack(side=tk.LEFT)
        
        self.stats_label = tk.Label(info_frame, 
                                   text="", 
                                   font=self.mono_font, 
                                   bg=self.secondary_color, 
                                   fg='#888888')
        self.stats_label.pack(side=tk.RIGHT)
        
        # Panel principal dividido
        main_panel = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, 
                                   bg=self.bg_color, sashwidth=5)
        main_panel.pack(fill=tk.BOTH, expand=True)
        
        # Panel izquierdo - Logs
        log_frame = tk.Frame(main_panel, bg=self.secondary_color)
        main_panel.add(log_frame, width=500)
        
        log_title = tk.Label(log_frame, text="REGISTRO DE ACTIVIDAD", 
                            font=self.heading_font, 
                            bg=self.secondary_color, 
                            fg=self.highlight_color)
        log_title.pack(anchor=tk.W, padx=20, pady=(15, 10))
        
        # Log con pestañas
        log_notebook = ttk.Notebook(log_frame)
        log_notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Pestaña de logs
        log_tab = tk.Frame(log_notebook, bg='#2d2d2d')
        log_notebook.add(log_tab, text="📝 Logs")
        
        self.log_text = scrolledtext.ScrolledText(log_tab, 
                                                 bg='#2d2d2d', 
                                                 fg=self.fg_color,
                                                 font=self.mono_font,
                                                 insertbackground=self.fg_color,
                                                 relief=tk.FLAT)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Pestaña de errores
        error_tab = tk.Frame(log_notebook, bg='#2d2d2d')
        log_notebook.add(error_tab, text="⚠️ Errores")
        
        self.error_text = scrolledtext.ScrolledText(error_tab, 
                                                   bg='#2d2d2d', 
                                                   fg=self.error_color,
                                                   font=self.mono_font,
                                                   insertbackground=self.error_color,
                                                   relief=tk.FLAT)
        self.error_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Panel derecho - Vista y preview
        right_panel = tk.Frame(main_panel, bg=self.secondary_color)
        main_panel.add(right_panel, width=600)
        
        # Vista de estructura
        structure_frame = tk.Frame(right_panel, bg=self.secondary_color)
        structure_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        structure_title = tk.Label(structure_frame, 
                                  text="ESTRUCTURA DEL SITIO CLONADO", 
                                  font=self.heading_font, 
                                  bg=self.secondary_color, 
                                  fg=self.highlight_color)
        structure_title.pack(anchor=tk.W, pady=(0, 10))
        
        # Treeview con scroll
        tree_container = tk.Frame(structure_frame, bg='#2d2d2d')
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        # Configurar treeview
        self.tree = ttk.Treeview(tree_container, columns=('type', 'size', 'status'), 
                                selectmode='extended')
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_container, orient="vertical", 
                           command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_container, orient="horizontal", 
                           command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Layout
        self.tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)
        
        # Configurar columnas
        self.tree.heading('#0', text='Archivo/Carpeta', anchor=tk.W)
        self.tree.heading('type', text='Tipo', anchor=tk.W)
        self.tree.heading('size', text='Tamaño', anchor=tk.W)
        self.tree.heading('status', text='Estado', anchor=tk.W)
        
        self.tree.column('#0', width=300)
        self.tree.column('type', width=100)
        self.tree.column('size', width=100)
        self.tree.column('status', width=100)
        
        # Configurar estilos
        self.configure_styles()
        
        # Log inicial
        self.log("🚀 Web Cloner Pro iniciado")
        self.log("💡 Selecciona un modo de clonado y haz clic en INICIAR")
        self.log("⚠️ El modo 'Interactivo' intenta mantener formularios y botones funcionales")
        
        # Iniciar actualización de UI
        self.update_ui()
        
    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores para Treeview
        style.configure("Treeview",
                       background="#2d2d2d",
                       foreground=self.fg_color,
                       fieldbackground="#2d2d2d",
                       borderwidth=0,
                       font=self.mono_font)
        
        style.configure("Treeview.Heading",
                       background=self.accent_color,
                       foreground='white',
                       font=self.label_font,
                       relief=tk.FLAT)
        
        style.map("Treeview", 
                 background=[('selected', self.highlight_color)])
        
        # Configurar Progressbar
        for key in self.progress_bars:
            if isinstance(self.progress_bars[key], ttk.Progressbar):
                style.configure(f"{key}.Horizontal.TProgressbar",
                               background=self.highlight_color,
                               troughcolor='#2d2d2d',
                               bordercolor='#2d2d2d')
    
    def paste_url(self):
        try:
            clipboard_content = self.root.clipboard_get()
            if clipboard_content.startswith(('http://', 'https://')):
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, clipboard_content)
                self.log(f"📋 URL pegada: {clipboard_content}")
            else:
                self.error_log(f"⚠️ URL inválida en portapapeles")
        except:
            self.error_log(f"❌ Error al acceder al portapapeles")
    
    def test_url(self):
        url = self.url_entry.get().strip()
        if not url:
            self.error_log("⚠️ Ingresa una URL primero")
            return
        
        self.log(f"🔍 Probando conexión a: {url}")
        try:
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                self.log(f"✅ URL accesible (Status: {response.status_code})")
            else:
                self.log(f"⚠️ URL responde con status: {response.status_code}")
        except Exception as e:
            self.error_log(f"❌ Error al conectar: {str(e)}")
    
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Seleccionar carpeta de destino")
        if folder:
            self.folder_var.set(folder)
            self.log(f"📁 Carpeta destino: {folder}")
    
    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        
        # Auto-color basado en contenido
        if message.startswith("✅") or message.startswith("🚀"):
            self.log_text.tag_add("success", f"end-2c linestart", f"end-2c lineend")
        elif message.startswith("⚠️") or message.startswith("🔍"):
            self.log_text.tag_add("warning", f"end-2c linestart", f"end-2c lineend")
        elif message.startswith("❌"):
            self.log_text.tag_add("error", f"end-2c linestart", f"end-2c lineend")
        
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def error_log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.error_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.error_text.see(tk.END)
        self.log(message)  # También mostrar en log principal
    
    def start_download(self):
        if self.is_downloading:
            self.log("⚠️ Ya hay una descarga en progreso")
            return
        
        url = self.url_entry.get().strip()
        if not url or not url.startswith(('http://', 'https://')):
            messagebox.showerror("Error", "Ingresa una URL válida (http:// o https://)")
            return
        
        # Crear directorio
        download_folder = self.folder_var.get()
        try:
            os.makedirs(download_folder, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el directorio:\n{str(e)}")
            return
        
        # Iniciar descarga
        self.is_downloading = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Limpiar barras de progreso
        for key in self.progress_bars:
            if isinstance(self.progress_bars[key], ttk.Progressbar):
                self.progress_bars[key]['value'] = 0
        
        # Obtener configuración
        config = {
            'url': url,
            'folder': download_folder,
            'depth': self.depth_var.get(),
            'threads': self.threads_var.get(),
            'mode': self.download_mode.get(),
            'keep_js': self.js_var.get(),
            'keep_forms': self.forms_var.get(),
            'try_ajax': self.ajax_var.get()
        }
        
        self.log(f"🚀 Iniciando clonado en modo: {config['mode'].upper()}")
        self.log(f"📁 Destino: {download_folder}")
        
        # Iniciar thread
        self.download_thread = threading.Thread(
            target=self.download_website,
            args=(config,),
            daemon=True
        )
        self.download_thread.start()
    
    def download_website(self, config):
        try:
            downloader = FunctionalWebDownloader(
                url=config['url'],
                download_folder=config['folder'],
                max_depth=config['depth'],
                max_workers=config['threads'],
                mode=config['mode'],
                keep_js=config['keep_js'],
                keep_forms=config['keep_forms'],
                try_ajax=config['try_ajax'],
                update_callback=self.update_download_status,
                log_callback=self.log,
                error_callback=self.error_log,
                tree_callback=self.update_tree_view
            )
            
            downloader.download()
            
            if not self.is_downloading:
                self.log("⏹️ Clonado detenido por el usuario")
                self.download_queue.put(('status', 'stopped'))
            else:
                self.log("✅ Clonado completado exitosamente")
                self.download_queue.put(('status', 'completed'))
                
        except Exception as e:
            error_msg = f"❌ Error crítico: {str(e)}"
            self.error_log(error_msg)
            self.download_queue.put(('error', error_msg))
        finally:
            self.is_downloading = False
            self.download_queue.put(('finished', None))
    
    def update_download_status(self, stats, file_info=None):
        self.download_queue.put(('stats', stats))
        if file_info:
            self.download_queue.put(('file', file_info))
    
    def update_tree_view(self, filepath, file_type, size, status):
        self.download_queue.put(('tree', (filepath, file_type, size, status)))
    
    def update_ui(self):
        try:
            while True:
                msg_type, data = self.download_queue.get_nowait()
                
                if msg_type == 'stats':
                    self.update_progress(data)
                elif msg_type == 'file':
                    self.update_file_display(data)
                elif msg_type == 'tree':
                    filepath, file_type, size, status = data
                    self.add_to_tree(filepath, file_type, size, status)
                elif msg_type == 'status':
                    if data == 'completed':
                        self.status_label.config(text="✅ Clonado completado", fg=self.success_color)
                    elif data == 'stopped':
                        self.status_label.config(text="⏹️ Clonado detenido", fg=self.error_color)
                elif msg_type == 'error':
                    messagebox.showerror("Error", data)
                elif msg_type == 'finished':
                    self.start_button.config(state=tk.NORMAL)
                    self.stop_button.config(state=tk.DISABLED)
                
        except queue.Empty:
            pass
        
        if self.is_downloading:
            self.root.after(100, self.update_ui)
        else:
            self.root.after(100, self.update_ui)
    
    def update_progress(self, stats):
        for file_type in ['html', 'css', 'js', 'images', 'other']:
            total = stats.get(f'{file_type}_total', 0)
            downloaded = stats.get(f'{file_type}_downloaded', 0)
            
            if total > 0:
                progress = (downloaded / total) * 100
                self.progress_bars[file_type]['value'] = progress
                self.progress_bars[f'{file_type}_label'].config(text=f"{downloaded}/{total}")
        
        elapsed = stats.get('elapsed_time', 0)
        total_files = stats.get('total_files', 0)
        downloaded_files = stats.get('downloaded_files', 0)
        
        if elapsed > 0:
            time_str = f"{int(elapsed//60)}:{int(elapsed%60):02d}"
            self.stats_label.config(
                text=f"⏱ {time_str} | 📦 {downloaded_files}/{total_files} archivos"
            )
    
    def update_file_display(self, file_info):
        # Actualizar información específica del archivo si es necesario
        pass
    
    def add_to_tree(self, filepath, file_type, size, status):
        # Obtener nombre y ruta relativa
        rel_path = os.path.relpath(filepath, self.folder_var.get())
        parent = ''
        
        # Dividir ruta
        parts = rel_path.split(os.sep)
        
        # Construir jerarquía
        for i, part in enumerate(parts[:-1]):
            parent_path = os.sep.join(parts[:i+1])
            
            # Buscar si ya existe
            found = False
            for child in self.tree.get_children(parent):
                if self.tree.item(child)['text'] == part:
                    parent = child
                    found = True
                    break
            
            if not found:
                parent = self.tree.insert(parent, 'end', 
                                         text=part,
                                         values=('📁 Carpeta', '', ''),
                                         open=True)
        
        # Agregar archivo
        icon = {
            'html': '📄',
            'css': '🎨',
            'js': '⚙️',
            'image': '🖼️',
            'other': '📦'
        }.get(file_type, '📄')
        
        size_str = self.format_size(size)
        status_icon = '✅' if status == 'success' else '❌'
        
        self.tree.insert(parent, 'end',
                        text=parts[-1] if parts else filepath,
                        values=(f"{icon} {file_type}", size_str, status_icon))
    
    def format_size(self, size):
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f} KB"
        else:
            return f"{size/(1024*1024):.1f} MB"
    
    def stop_download(self):
        if self.is_downloading:
            self.is_downloading = False
            self.log("⏹️ Deteniendo clonado...")
            self.status_label.config(text="⏹️ Deteniendo...", fg=self.error_color)
    
    def preview_local(self):
        folder = self.folder_var.get()
        if not os.path.exists(folder) or not os.listdir(folder):
            messagebox.showinfo("Sin contenido", "La carpeta está vacía o no existe.\nClona un sitio primero.")
            return
        
        # Buscar archivo index.html
        index_files = ['index.html', 'index.htm', 'default.html']
        for index_file in index_files:
            index_path = os.path.join(folder, index_file)
            if os.path.exists(index_path):
                webbrowser.open(f"file://{index_path}")
                self.log(f"🌐 Abriendo preview local: {index_file}")
                return
        
        # Si no hay index, mostrar diálogo para seleccionar archivo
        file_path = filedialog.askopenfilename(
            initialdir=folder,
            title="Seleccionar archivo para preview",
            filetypes=[("HTML files", "*.html *.htm"), ("All files", "*.*")]
        )
        
        if file_path:
            webbrowser.open(f"file://{file_path}")
    
    def generate_report(self):
        folder = self.folder_var.get()
        if not os.path.exists(folder):
            messagebox.showinfo("Sin datos", "No hay datos para generar reporte.")
            return
        
        # Crear reporte simple
        report_path = os.path.join(folder, "clonado_report.txt")
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("=== REPORTE DE CLONADO WEB ===\n\n")
                f.write(f"Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"URL original: {self.url_entry.get()}\n")
                f.write(f"Carpeta destino: {folder}\n")
                f.write(f"Modo: {self.download_mode.get()}\n\n")
                
                # Contar archivos por tipo
                file_counts = {'html': 0, 'css': 0, 'js': 0, 'images': 0, 'other': 0}
                total_size = 0
                
                for root_dir, dirs, files in os.walk(folder):
                    for file in files:
                        filepath = os.path.join(root_dir, file)
                        size = os.path.getsize(filepath)
                        total_size += size
                        
                        ext = os.path.splitext(file)[1].lower()
                        if ext in ['.html', '.htm']:
                            file_counts['html'] += 1
                        elif ext == '.css':
                            file_counts['css'] += 1
                        elif ext == '.js':
                            file_counts['js'] += 1
                        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg']:
                            file_counts['images'] += 1
                        else:
                            file_counts['other'] += 1
                
                f.write("=== ESTADÍSTICAS ===\n")
                f.write(f"Total archivos: {sum(file_counts.values())}\n")
                f.write(f"Total tamaño: {self.format_size(total_size)}\n\n")
                
                f.write("Por tipo:\n")
                for file_type, count in file_counts.items():
                    f.write(f"  {file_type.upper()}: {count} archivos\n")
                
                f.write("\n=== ESTRUCTURA ===\n")
                self.write_tree_structure(f, folder, "")
            
            self.log(f"📊 Reporte generado: {report_path}")
            messagebox.showinfo("Reporte generado", f"Reporte guardado en:\n{report_path}")
            
        except Exception as e:
            self.error_log(f"❌ Error generando reporte: {str(e)}")
    
    def write_tree_structure(self, file, folder, prefix):
        """Escribe estructura tipo tree en el reporte"""
        items = os.listdir(folder)
        items.sort()
        
        for i, item in enumerate(items):
            path = os.path.join(folder, item)
            is_last = i == len(items) - 1
            
            if os.path.isdir(path):
                file.write(f"{prefix}{'└── ' if is_last else '├── '}{item}/\n")
                new_prefix = prefix + ("    " if is_last else "│   ")
                self.write_tree_structure(file, path, new_prefix)
            else:
                size = os.path.getsize(path)
                size_str = self.format_size(size)
                file.write(f"{prefix}{'└── ' if is_last else '├── '}{item} ({size_str})\n")
    
    def on_closing(self):
        if self.is_downloading:
            if messagebox.askyesno("Confirmar", 
                                  "⚠️ El clonado está en progreso.\n\n¿Deseas salir de todos modos?"):
                self.is_downloading = False
                if self.download_thread:
                    self.download_thread.join(timeout=2)
                self.root.destroy()
        else:
            self.root.destroy()

class FunctionalWebDownloader:
    def __init__(self, url, download_folder, max_depth=2, max_workers=5,
                 mode='full', keep_js=True, keep_forms=True, try_ajax=False,
                 update_callback=None, log_callback=None, error_callback=None,
                 tree_callback=None):
        
        self.base_url = url
        self.download_folder = download_folder
        self.max_depth = max_depth
        self.max_workers = max_workers
        self.mode = mode
        self.keep_js = keep_js
        self.keep_forms = keep_forms
        self.try_ajax = try_ajax
        
        self.update_callback = update_callback
        self.log_callback = log_callback
        self.error_callback = error_callback
        self.tree_callback = tree_callback
        
        self.parsed_base_url = urlparse(url)
        self.domain = self.parsed_base_url.netloc
        self.scheme = self.parsed_base_url.scheme or 'http'
        
        self.visited_urls = set()
        self.urls_to_visit = [url]
        self.downloaded_files = set()
        self.session = requests.Session()
        
        # Configurar headers para parecer navegador real
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        })
        
        # Estadísticas
        self.stats = {
            'html_total': 0,
            'html_downloaded': 0,
            'css_total': 0,
            'css_downloaded': 0,
            'js_total': 0,
            'js_downloaded': 0,
            'images_total': 0,
            'images_downloaded': 0,
            'other_total': 0,
            'other_downloaded': 0,
            'total_files': 0,
            'downloaded_files': 0,
            'errors': 0,
            'start_time': time.time(),
            'total_size': 0
        }
        
        self.is_running = True
        
        # Mapeo de extensiones a tipos
        self.file_types = {
            'html': {'.html', '.htm', '.php', '.asp', '.aspx', '.jsp'},
            'css': {'.css', '.scss', '.less'},
            'js': {'.js', '.mjs', '.cjs'},
            'images': {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico', '.bmp', '.webp', '.avif'},
            'fonts': {'.woff', '.woff2', '.ttf', '.otf', '.eot'},
            'documents': {'.pdf', '.doc', '.docx', '.xls', '.xlsx'},
            'media': {'.mp3', '.mp4', '.wav', '.avi', '.mov'},
            'archives': {'.zip', '.rar', '.tar', '.gz'}
        }
    
    def log(self, message):
        if self.log_callback:
            self.log_callback(message)
    
    def error_log(self, message):
        if self.error_callback:
            self.error_callback(message)
    
    def update_stats(self, file_type=None, increment_total=False):
        if self.update_callback:
            elapsed = time.time() - self.stats['start_time']
            stats_update = {
                'html_total': self.stats['html_total'],
                'html_downloaded': self.stats['html_downloaded'],
                'css_total': self.stats['css_total'],
                'css_downloaded': self.stats['css_downloaded'],
                'js_total': self.stats['js_total'],
                'js_downloaded': self.stats['js_downloaded'],
                'images_total': self.stats['images_total'],
                'images_downloaded': self.stats['images_downloaded'],
                'other_total': self.stats['other_total'],
                'other_downloaded': self.stats['other_downloaded'],
                'total_files': self.stats['total_files'],
                'downloaded_files': self.stats['downloaded_files'],
                'elapsed_time': elapsed
            }
            self.update_callback(stats_update)
    
    def get_file_type(self, filename):
        """Determina tipo de archivo por extensión"""
        ext = os.path.splitext(filename)[1].lower()
        
        for file_type, extensions in self.file_types.items():
            if ext in extensions:
                return file_type
        
        return 'other'
    
    def should_process_url(self, url):
        """Determina si procesar una URL"""
        if not url or url in self.visited_urls:
            return False
        
        # Filtrar URLs no HTTP/HTTPS
        if url.startswith(('javascript:', 'mailto:', 'tel:', '#', 'data:')):
            return False
        
        parsed = urlparse(url)
        if parsed.scheme and parsed.scheme not in ('http', 'https'):
            return False
        
        # Para modo interactivo, procesar más URLs
        if self.mode == 'interactive':
            return True
        
        # Para otros modos, solo mismo dominio
        if not parsed.netloc or parsed.netloc == self.domain:
            return True
        
        return False
    
    def download_file(self, url, depth=0):
        """Descarga y procesa un archivo"""
        if not self.is_running or url in self.downloaded_files:
            return []
        
        try:
            # Hacer URL absoluta
            if not urlparse(url).netloc:
                url = urljoin(self.base_url, url)
            
            self.log(f"📥 Descargando: {url}")
            
            # Descargar
            response = self.session.get(url, stream=True, timeout=15)
            response.raise_for_status()
            
            # Determinar nombre de archivo
            filename = self.get_filename_from_response(url, response)
            
            # Determinar ruta local
            local_path = self.get_local_path(url, filename)
            
            # Crear directorios
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # Guardar archivo
            file_size = 0
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        file_size += len(chunk)
            
            # Determinar tipo de archivo
            file_type = self.get_file_type(filename)
            
            # Actualizar estadísticas
            self.downloaded_files.add(url)
            self.stats[f'{file_type}_downloaded'] += 1
            self.stats['downloaded_files'] += 1
            self.stats['total_size'] += file_size
            
            # Notificar tree view
            if self.tree_callback:
                self.tree_callback(local_path, file_type, file_size, 'success')
            
            # Procesar según tipo
            links = []
            content_type = response.headers.get('content-type', '').lower()
            
            if 'html' in content_type or file_type == 'html':
                # Procesar HTML para mantener funcionalidad
                links = self.process_html_file(local_path, url, depth)
                self.stats['html_total'] += len(links)
                self.stats['total_files'] += len(links)
            
            elif 'css' in content_type or file_type == 'css':
                # Procesar CSS para reescribir URLs
                links = self.process_css_file(local_path, url)
                self.stats['css_total'] += len(links)
                self.stats['total_files'] += len(links)
            
            elif 'javascript' in content_type or file_type == 'js':
                # Procesar JS si está habilitado
                if self.keep_js:
                    links = self.process_js_file(local_path, url)
                    self.stats['js_total'] += len(links)
                    self.stats['total_files'] += len(links)
            
            self.update_stats()
            return links
            
        except Exception as e:
            self.stats['errors'] += 1
            error_msg = str(e)[:100]
            self.error_log(f"❌ Error descargando {url}: {error_msg}")
            
            # Notificar error en tree view
            if self.tree_callback:
                self.tree_callback(url, 'error', 0, 'error')
            
            return []
    
    def get_filename_from_response(self, url, response):
        """Obtiene nombre de archivo desde respuesta o URL"""
        # Intentar desde content-disposition
        content_disposition = response.headers.get('content-disposition')
        if content_disposition and 'filename=' in content_disposition:
            import re
            match = re.search(r'filename=["\']?(.+?)["\']?(?:;|$)', content_disposition)
            if match:
                return match.group(1)
        
        # Desde URL
        filename = os.path.basename(urlparse(url).path)
        if filename:
            return filename
        
        # Por defecto según content-type
        content_type = response.headers.get('content-type', '').split(';')[0]
        
        mime_map = {
            'text/html': 'index.html',
            'text/css': 'styles.css',
            'application/javascript': 'script.js',
            'image/jpeg': 'image.jpg',
            'image/png': 'image.png',
            'image/gif': 'image.gif',
            'image/svg+xml': 'image.svg'
        }
        
        return mime_map.get(content_type, 'file.bin')
    
    def get_local_path(self, url, filename):
        """Obtiene ruta local para archivo"""
        parsed = urlparse(url)
        
        # Para URLs del mismo dominio
        if not parsed.netloc or parsed.netloc == self.domain:
            path = parsed.path
            if not path or path == '/':
                path = '/index.html'
            
            clean_path = path.lstrip('/')
            if not clean_path:
                clean_path = 'index.html'
            
            # Reemplazar caracteres problemáticos
            clean_path = re.sub(r'[<>:"|?*]', '_', clean_path)
            
            return os.path.join(self.download_folder, clean_path)
        
        # Para recursos externos
        else:
            external_dir = os.path.join(self.download_folder, 'external', parsed.netloc)
            return os.path.join(external_dir, filename)
    
    def process_html_file(self, filepath, source_url, depth):
        """Procesa archivo HTML para mantener funcionalidad"""
        links = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # 1. Mantener formularios funcionales
            if self.keep_forms:
                self.preserve_forms(soup, source_url)
            
            # 2. Mantener JavaScript
            if self.keep_js:
                self.preserve_javascript(soup, source_url)
            else:
                # Remover scripts si no se mantienen
                for script in soup.find_all('script'):
                    script.decompose()
            
            # 3. Reescribir URLs para que funcionen localmente
            links = self.rewrite_html_urls(soup, source_url)
            
            # 4. Para modo interactivo, agregar polyfills si es necesario
            if self.mode == 'interactive':
                self.add_interactive_polyfills(soup)
            
            # 5. Guardar HTML procesado
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            
            self.log(f"✅ HTML procesado: {os.path.basename(filepath)}")
            
        except Exception as e:
            self.error_log(f"❌ Error procesando HTML {filepath}: {str(e)}")
        
        return links
    
    def preserve_forms(self, soup, source_url):
        """Intenta mantener formularios funcionales"""
        for form in soup.find_all('form'):
            action = form.get('action', '')
            
            if action:
                # Si la acción es relativa, hacerla absoluta
                if not urlparse(action).netloc:
                    absolute_action = urljoin(source_url, action)
                    form['action'] = absolute_action
                
                # Para formularios POST, podríamos necesitar procesar más
                method = form.get('method', 'get').lower()
                if method == 'post':
                    # Agregar nota sobre funcionalidad
                    if not form.find('div', {'class': 'form-note'}):
                        note = soup.new_tag('div')
                        note['class'] = 'form-note'
                        note['style'] = 'color: #666; font-size: 0.9em; margin: 10px 0;'
                        note.string = 'Nota: Este formulario puede requerir ajustes para funcionar localmente.'
                        form.insert_after(note)
            
            # Asegurar que todos los inputs tengan name
            for input_tag in form.find_all('input'):
                if not input_tag.get('name') and input_tag.get('type') not in ['submit', 'button', 'reset']:
                    input_tag['name'] = f"field_{hash(str(input_tag))[:8]}"
    
    def preserve_javascript(self, soup, source_url):
        """Procesa scripts para que funcionen localmente"""
        for script in soup.find_all('script'):
            src = script.get('src')
            
            if src:
                # Reescribir src para apuntar a archivo local
                if not urlparse(src).netloc:
                    absolute_src = urljoin(source_url, src)
                    script['data-original-src'] = src
                    
                    # Convertir a ruta relativa local
                    local_src = self.convert_to_local_path(absolute_src, source_url)
                    if local_src:
                        script['src'] = local_src
            
            # Para scripts inline, intentar reescribir URLs
            elif script.string:
                try:
                    # Buscar y reescribir URLs en scripts inline
                    script_content = script.string
                    
                    # Patrones comunes de URLs en JavaScript
                    url_patterns = [
                        r'["\'](https?://[^"\']+)["\']',
                        r'url\(["\']?([^"\')]+)["\']?\)',
                        r'src=["\']([^"\']+)["\']',
                        r'href=["\']([^"\']+)["\']'
                    ]
                    
                    for pattern in url_patterns:
                        matches = re.findall(pattern, script_content)
                        for match in matches:
                            if match and not urlparse(match).scheme:
                                absolute_url = urljoin(source_url, match)
                                local_url = self.convert_to_local_path(absolute_url, source_url)
                                if local_url:
                                    script_content = script_content.replace(match, local_url)
                    
                    script.string = script_content
                except:
                    pass  # Si falla, dejar script original
    
    def rewrite_html_urls(self, soup, source_url):
        """Reescribe URLs en HTML para que funcionen localmente"""
        links = []
        
        # Elementos con URLs
        url_attributes = [
            ('a', 'href'),
            ('link', 'href'),
            ('img', 'src'),
            ('script', 'src'),
            ('iframe', 'src'),
            ('source', 'src'),
            ('video', 'src'),
            ('audio', 'src'),
            ('form', 'action'),
            ('meta', 'content'),  # Para og:image, etc.
            ('object', 'data'),
            ('embed', 'src'),
            ('applet', 'code')
        ]
        
        for tag_name, attr in url_attributes:
            for tag in soup.find_all(tag_name, {attr: True}):
                url = tag[attr].strip()
                if not url:
                    continue
                
                # Eliminar fragmentos
                url, _ = urldefrag(url)
                
                # Convertir a URL absoluta
                absolute_url = urljoin(source_url, url)
                
                # Verificar si debemos procesarla
                if self.should_download(absolute_url):
                    links.append(absolute_url)
                    
                    # Reescribir a ruta local
                    local_path = self.convert_to_local_path(absolute_url, source_url)
                    if local_path:
                        tag[attr] = local_path
                    else:
                        # Mantener URL original si no se puede convertir
                        tag[attr] = absolute_url
                else:
                    # Para URLs externas o que no descargamos
                    tag[attr] = absolute_url
        
        # También procesar URLs en estilos inline
        for tag in soup.find_all(style=True):
            style_content = tag['style']
            urls = re.findall(r'url\(["\']?([^"\')]+)["\']?\)', style_content)
            
            for url in urls:
                absolute_url = urljoin(source_url, url)
                
                if self.should_download(absolute_url):
                    links.append(absolute_url)
                    local_path = self.convert_to_local_path(absolute_url, source_url)
                    if local_path:
                        style_content = style_content.replace(url, local_path)
            
            tag['style'] = style_content
        
        return list(set(links))  # Eliminar duplicados
    
    def convert_to_local_path(self, url, source_url):
        """Convierte URL a ruta local relativa"""
        try:
            parsed = urlparse(url)
            
            # Si es del mismo dominio
            if not parsed.netloc or parsed.netloc == self.domain:
                path = parsed.path
                if not path or path == '/':
                    path = '/index.html'
                
                clean_path = path.lstrip('/')
                if not clean_path:
                    clean_path = 'index.html'
                
                # Reemplazar caracteres problemáticos
                clean_path = re.sub(r'[<>:"|?*]', '_', clean_path)
                
                return clean_path
            
            # Si es externo, poner en subdirectorio external
            else:
                external_path = os.path.join('external', parsed.netloc, parsed.path.lstrip('/'))
                return external_path.replace('//', '/')
                
        except:
            return None
    
    def add_interactive_polyfills(self, soup):
        """Agrega polyfills para funcionalidad interactiva"""
        head = soup.find('head')
        if not head:
            head = soup.new_tag('head')
            soup.html.insert(0, head)
        
        # Agregar polyfill para fetch si no existe
        if not soup.find('script', string=lambda t: t and 'fetch' in t):
            polyfill_script = soup.new_tag('script')
            polyfill_script.string = '''
            // Polyfill para funcionalidad offline
            if (typeof window.fetch === 'undefined') {
                window.fetch = function(url, options) {
                    return new Promise(function(resolve, reject) {
                        console.log('Fetch polyfill llamado para:', url);
                        // Simular respuesta básica
                        resolve({
                            ok: true,
                            status: 200,
                            json: function() { return Promise.resolve({}); },
                            text: function() { return Promise.resolve(''); }
                        });
                    });
                };
            }
            '''
            head.append(polyfill_script)
    
    def process_css_file(self, filepath, source_url):
        """Procesa archivo CSS para reescribir URLs"""
        links = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Buscar todas las URLs en el CSS
            url_pattern = r'url\(["\']?([^"\')]+)["\']?\)'
            urls = re.findall(url_pattern, content)
            
            for url in urls:
                # Convertir a URL absoluta
                absolute_url = urljoin(source_url, url)
                
                if self.should_download(absolute_url):
                    links.append(absolute_url)
                    
                    # Reescribir a ruta local
                    local_path = self.convert_to_local_path(absolute_url, source_url)
                    if local_path:
                        content = content.replace(f'url("{url}")', f'url("{local_path}")')
                        content = content.replace(f"url('{url}')", f"url('{local_path}')")
                        content = content.replace(f'url({url})', f'url({local_path})')
            
            # Guardar CSS procesado
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log(f"✅ CSS procesado: {os.path.basename(filepath)}")
            
        except Exception as e:
            self.error_log(f"❌ Error procesando CSS {filepath}: {str(e)}")
        
        return links
    
    def process_js_file(self, filepath, source_url):
        """Procesa archivo JavaScript"""
        links = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Buscar URLs comunes en JS (puede ser complejo)
            # Patrones simples para URLs en strings
            url_patterns = [
                r'["\'](https?://[^"\']+)["\']',
                r'["\'](/[^"\']+)["\']',  # Rutas absolutas
            ]
            
            for pattern in url_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    # Convertir a URL absoluta
                    if match.startswith('http'):
                        absolute_url = match
                    else:
                        absolute_url = urljoin(source_url, match)
                    
                    if self.should_download(absolute_url):
                        links.append(absolute_url)
                        
                        # Reescribir a ruta local (opcional, puede romper JS)
                        # local_path = self.convert_to_local_path(absolute_url, source_url)
                        # if local_path:
                        #     content = content.replace(match, local_path)
            
            # Para modo interactivo, intentar hacer el JS más compatible
            if self.mode == 'interactive':
                content = self.make_js_compatible(content, source_url)
            
            # Guardar JS procesado
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log(f"✅ JS procesado: {os.path.basename(filepath)}")
            
        except Exception as e:
            self.error_log(f"❌ Error procesando JS {filepath}: {str(e)}")
        
        return links
    
    def make_js_compatible(self, content, source_url):
        """Intenta hacer JavaScript más compatible para funcionar localmente"""
        # Reemplazar referencias a servidores originales
        if self.domain in content:
            content = content.replace(f'https://{self.domain}', '')
            content = content.replace(f'http://{self.domain}', '')
        
        # Agregar polyfills para APIs comunes
        if 'XMLHttpRequest' in content or 'fetch' in content:
            polyfill = '''
            // Polyfill para entorno local
            if (window.location.protocol === 'file:') {
                console.log('Ejecutando en entorno local - algunas APIs pueden estar limitadas');
                if (!window.originalFetch) window.originalFetch = window.fetch;
                window.fetch = function(url, options) {
                    console.log('Fetch interceptado para:', url);
                    // Para URLs relativas, intentar cargar localmente
                    if (url.startsWith('/') || url.startsWith('./') || url.startsWith('../')) {
                        return window.originalFetch(url, options).catch(function(err) {
                            console.warn('Error en fetch local:', err);
                            return Promise.resolve({
                                ok: true,
                                status: 200,
                                json: function() { return Promise.resolve({success: false, error: 'offline'}); },
                                text: function() { return Promise.resolve(''); }
                            });
                        });
                    }
                    return window.originalFetch(url, options);
                };
            }
            '''
            content = polyfill + '\n' + content
        
        return content
    
    def should_download(self, url):
        """Determina si se debe descargar una URL"""
        if not self.is_running or url in self.downloaded_files:
            return False
        
        # Filtrar por tipo según modo
        parsed = urlparse(url)
        path = parsed.path.lower()
        ext = os.path.splitext(path)[1]
        
        # Según modo
        if self.mode == 'fast':
            # Solo HTML básico
            return ext in self.file_types['html']
        
        elif self.mode == 'static':
            # HTML y CSS
            return ext in self.file_types['html'] or ext in self.file_types['css']
        
        elif self.mode == 'full':
            # Todos los recursos
            return True
        
        elif self.mode == 'interactive':
            # Todos los recursos + intentar mantener funcionalidad
            return True
        
        return False
    
    def download(self):
        """Método principal de descarga"""
        self.log(f"🚀 Iniciando clonado en modo: {self.mode.upper()}")
        
        depth = 0
        while self.urls_to_visit and depth < self.max_depth and self.is_running:
            current_batch = len(self.urls_to_visit)
            self.log(f"📊 Profundidad {depth + 1}: {current_batch} URLs")
            
            current_urls = self.urls_to_visit.copy()
            self.urls_to_visit.clear()
            
            # Procesar en paralelo
            import concurrent.futures
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_url = {}
                
                for url in current_urls:
                    if self.should_process_url(url) and url not in self.visited_urls:
                        self.visited_urls.add(url)
                        future = executor.submit(self.download_file, url, depth)
                        future_to_url[future] = url
                
                # Procesar resultados
                for future in concurrent.futures.as_completed(future_to_url):
                    if not self.is_running:
                        break
                    
                    url = future_to_url[future]
                    try:
                        new_links = future.result(timeout=20)
                        
                        # Agregar nuevos enlaces
                        for link in new_links:
                            if (self.should_download(link) and 
                                link not in self.visited_urls and 
                                link not in self.urls_to_visit):
                                self.urls_to_visit.append(link)
                                
                    except concurrent.futures.TimeoutError:
                        self.error_log(f"⏱️ Timeout procesando: {url}")
                        self.stats['errors'] += 1
                    except Exception as e:
                        self.error_log(f"❌ Error procesando {url}: {str(e)}")
                        self.stats['errors'] += 1
            
            depth += 1
            self.update_stats()
        
        if self.is_running:
            self.log(f"\n✅ Clonado completado")
            self.log(f"📊 Archivos descargados: {self.stats['downloaded_files']}")
            self.log(f"📊 Tamaño total: {self.format_size(self.stats['total_size'])}")
            self.log(f"📊 Errores: {self.stats['errors']}")
            
            # Mostrar resumen por tipo
            self.log(f"\n📊 Resumen por tipo:")
            for file_type in ['html', 'css', 'js', 'images', 'other']:
                downloaded = self.stats[f'{file_type}_downloaded']
                total = self.stats[f'{file_type}_total']
                if total > 0:
                    self.log(f"  {file_type.upper()}: {downloaded}/{total}")
        else:
            self.log(f"\n⏹️ Clonado interrumpido")
            self.log(f"📊 Progreso: {self.stats['downloaded_files']} archivos descargados")
    
    def format_size(self, size):
        """Formatea tamaño en bytes a texto legible"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"

def main():
    # Verificar dependencias
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("Instalando dependencias...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4"])
        print("✅ Dependencias instaladas. Reinicia la aplicación.")
        return
    
    # Crear ventana
    root = tk.Tk()
    
    # Configurar icono si existe
    try:
        root.iconbitmap('web_cloner.ico')
    except:
        pass
    
    # Crear aplicación
    app = WebDownloaderApp(root)
    
    # Centrar ventana
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Iniciar
    root.mainloop()

if __name__ == "__main__":
    main()