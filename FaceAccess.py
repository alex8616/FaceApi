import tkinter as tk
from tkinter import ttk, Menu, messagebox
import sqlite3
import pickle
import numpy as np
from datetime import datetime
from PIL import Image, ImageTk
import cv2

from face_engine import FaceEngine
from utils import registrar_asistencia
from database import init_db

# =========================
# IMPORTAR VENTANAS DESDE LA CARPETA WINDOWS
# =========================
from windows.usuarios_window import UsuariosWindow
from windows.reportes_window import ReportesWindow
from windows.config_window import ConfigWindow
from windows.about_window import AboutWindow
from windows.asistencia_window import AsistenciaWindow

# =========================
# CONFIGURACIÓN DE ESTILOS
# =========================
COLOR_PRIMARY = "#003049"      # Azul oscuro elegante
COLOR_SUCCESS = "#A1DD70"      # Verde suave
COLOR_DANGER = "#FF5555"       # Rojo vibrante
COLOR_TEXT = "#FFFFFF"         # Blanco
COLOR_BG = "#003049"           # Fondo principal azul oscuro
COLOR_SURFACE = "#FFFFFF"      # Superficies blancas
COLOR_ROW_PAR = "#F8F9FA"      # Color fila par (gris muy claro)
COLOR_ROW_IMPAR = "#FFFFFF"    # Color fila impar (blanco)
COLOR_TEXT_SECONDARY = "#003049"  # Texto secundario azul oscuro
COLOR_TITLE_BAR = "#002238"    # Color de la barra de título
COLOR_MENU_HOVER = "#004466"   # Color hover del menú

engine = FaceEngine()
CAMERA_INDEX = 2

class Toast:
    def __init__(self, parent):
        self.parent = parent
        
    def show(self, texto, tipo="info"):
        toast = tk.Toplevel(self.parent)
        toast.attributes("-fullscreen", True)
        toast.configure(bg=COLOR_BG)
        toast.attributes("-alpha", 0.95)
        
        colors = {
            "success": COLOR_SUCCESS,
            "error": COLOR_DANGER,
            "warning": "#FFB347",
            "info": COLOR_PRIMARY
        }
        
        frame = tk.Frame(toast, bg=COLOR_BG)
        frame.pack(expand=True)
        
        iconos = {
            "success": "✓",
            "error": "✗",
            "warning": "⚠",
            "info": "ℹ"
        }
        
        content_frame = tk.Frame(frame, bg=COLOR_SURFACE, padx=40, pady=30)
        content_frame.pack()
        
        tk.Label(
            content_frame,
            text=iconos.get(tipo, "ℹ"),
            font=("Segoe UI", 60, "bold"),
            fg=colors.get(tipo, COLOR_PRIMARY),
            bg=COLOR_SURFACE
        ).pack(pady=(0, 20))
        
        tk.Label(
            content_frame,
            text=texto,
            font=("Segoe UI", 28, "bold"),
            fg=COLOR_PRIMARY,
            bg=COLOR_SURFACE,
            wraplength=min(800, toast.winfo_screenwidth() - 200)
        ).pack()
        
        toast.after(2500, toast.destroy)

class HorasExtraModal:
    """Modal para agregar horas extra en las salidas"""
    def __init__(self, parent, registro_id, nombre, fecha, hora, refresh_callback):
        self.parent = parent
        self.registro_id = registro_id
        self.nombre = nombre
        self.fecha = fecha
        self.hora = hora
        self.refresh_callback = refresh_callback
        self.window = None
        self.toast = Toast(parent)

    def show(self):
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = tk.Toplevel(self.parent)
        self.window.title("Registro de Horas Extra")
        self.window.configure(bg=COLOR_BG)
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Hacer el modal responsivo
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Tamaño proporcional
        width = int(screen_width * 0.4)
        height = int(screen_height * 0.5)
        
        # Centrar
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        self.window.minsize(500, 450)

        # Configurar grid principal
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # Frame principal con padding
        main = tk.Frame(self.window, bg=COLOR_BG)
        main.grid(row=0, column=0, sticky="nsew", padx=40, pady=30)
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        # TÍTULO
        title_frame = tk.Frame(main, bg=COLOR_BG)
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        tk.Label(
            title_frame,
            text="⏰ REGISTRO DE HORAS EXTRA",
            font=("Segoe UI", 20, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_BG
        ).pack()

        # Información del registro
        info_frame = tk.Frame(main, bg=COLOR_BG)
        info_frame.grid(row=1, column=0, sticky="ew", pady=10)
        
        info_text = f"Empleado: {self.nombre}\nFecha: {self.fecha}\nHora de salida: {self.hora}"
        tk.Label(
            info_frame,
            text=info_text,
            font=("Segoe UI", 12),
            fg=COLOR_TEXT,
            bg=COLOR_BG,
            justify="left"
        ).pack(anchor="w", pady=5)

        # Área de texto para descripción
        desc_frame = tk.Frame(main, bg=COLOR_BG)
        desc_frame.grid(row=2, column=0, sticky="nsew", pady=20)
        desc_frame.grid_rowconfigure(1, weight=1)
        desc_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(
            desc_frame,
            text="Descripción de horas extra:",
            font=("Segoe UI", 13, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_BG
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Text area con scrollbar
        text_frame = tk.Frame(desc_frame, bg=COLOR_SURFACE, relief="solid", bd=1)
        text_frame.grid(row=1, column=0, sticky="nsew")
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        self.descripcion_text = tk.Text(
            text_frame,
            font=("Segoe UI", 11),
            wrap=tk.WORD,
            padx=10,
            pady=10,
            relief="flat"
        )
        self.descripcion_text.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(text_frame, command=self.descripcion_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.descripcion_text.config(yscrollcommand=scrollbar.set)
        
        # Placeholder
        self.descripcion_text.insert("1.0", "Ejemplo: Horas extra por reunión de proyecto, trabajo en mantenimiento, etc.")
        self.descripcion_text.config(fg="gray")
        self.descripcion_text.bind("<FocusIn>", self.on_focus_in)
        self.descripcion_text.bind("<FocusOut>", self.on_focus_out)

        # Botones de acción
        buttons_frame = tk.Frame(main, bg=COLOR_BG)
        buttons_frame.grid(row=3, column=0, sticky="ew", pady=20)
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)

        self.btn_guardar = tk.Button(
            buttons_frame,
            text="💾 GUARDAR HORAS EXTRA",
            font=("Segoe UI", 14, "bold"),
            bg=COLOR_SUCCESS,
            fg="#003049",
            relief="flat",
            cursor="hand2",
            height=2,
            command=self.guardar_horas_extra
        )
        self.btn_guardar.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        self.btn_cancelar = tk.Button(
            buttons_frame,
            text="✕ CANCELAR",
            font=("Segoe UI", 14, "bold"),
            bg=COLOR_DANGER,
            fg=COLOR_TEXT,
            relief="flat",
            cursor="hand2",
            height=2,
            command=self.close
        )
        self.btn_cancelar.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        
        # Atajos de teclado
        self.window.bind("<Escape>", lambda e: self.close())
        self.descripcion_text.bind("<Control-Return>", lambda e: self.guardar_horas_extra())

    def on_focus_in(self, event):
        if self.descripcion_text.get("1.0", "end-1c") == "Ejemplo: Horas extra por reunión de proyecto, trabajo en mantenimiento, etc.":
            self.descripcion_text.delete("1.0", tk.END)
            self.descripcion_text.config(fg="black")

    def on_focus_out(self, event):
        if not self.descripcion_text.get("1.0", "end-1c").strip():
            self.descripcion_text.insert("1.0", "Ejemplo: Horas extra por reunión de proyecto, trabajo en mantenimiento, etc.")
            self.descripcion_text.config(fg="gray")

    def guardar_horas_extra(self):
        descripcion = self.descripcion_text.get("1.0", tk.END).strip()
        
        # Verificar si es el placeholder
        if descripcion == "Ejemplo: Horas extra por reunión de proyecto, trabajo en mantenimiento, etc.":
            descripcion = ""
        
        if not descripcion:
            messagebox.showwarning("Advertencia", "Por favor, ingrese una descripción de las horas extra")
            return
        
        try:
            conn = sqlite3.connect("personas.db")
            cursor = conn.cursor()
            
            # Verificar si la columna horas_extra existe
            try:
                cursor.execute("ALTER TABLE asistencias ADD COLUMN horas_extra TEXT")
                conn.commit()
            except sqlite3.OperationalError:
                pass  # La columna ya existe
            
            # Actualizar el registro con las horas extra
            cursor.execute("""
                UPDATE asistencias 
                SET horas_extra = ? 
                WHERE id = ?
            """, (descripcion, self.registro_id))
            
            conn.commit()
            conn.close()
            
            self.toast.show(f"✅ Horas extra registradas para {self.nombre}", "success")
            self.refresh_callback()  # Refrescar la tabla
            self.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar horas extra: {str(e)}")

    def close(self):
        if self.window and self.window.winfo_exists():
            self.window.destroy()
            self.window = None

class ModernButton(tk.Button):
    def __init__(self, parent, text="", bg_color=COLOR_PRIMARY, **kwargs):
        super().__init__(parent, text=text, **kwargs)
        self.bg_color = bg_color
        self.configure(
            bg=bg_color,
            fg=COLOR_TEXT,
            font=("Segoe UI", 14, "bold"),
            relief="flat",
            cursor="hand2",
            borderwidth=0,
            padx=30,
            pady=12
        )
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
    def on_enter(self, e):
        if self.bg_color == COLOR_PRIMARY:
            self.configure(bg="#004466")
        elif self.bg_color == COLOR_SUCCESS:
            self.configure(bg="#B8FF88")
        elif self.bg_color == COLOR_DANGER:
            self.configure(bg="#FF6666")
            
    def on_leave(self, e):
        self.configure(bg=self.bg_color)

# =========================
# BARRA DE TÍTULO PERSONALIZADA CON MENÚ
# =========================
class TitleBar:
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        
        # Frame de la barra de título
        self.title_bar = tk.Frame(parent, bg=COLOR_TITLE_BAR, height=40)
        self.title_bar.pack(fill="x", side="top")
        self.title_bar.pack_propagate(False)
        
        # Frame para el menú y título
        left_frame = tk.Frame(self.title_bar, bg=COLOR_TITLE_BAR)
        left_frame.pack(side="left", fill="y")
        
        # Botón de menú (hamburguesa)
        self.menu_button = tk.Button(
            left_frame,
            text="☰",
            font=("Segoe UI", 14, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_TITLE_BAR,
            relief="flat",
            cursor="hand2",
            width=3,
            command=self.show_menu
        )
        self.menu_button.pack(side="left", padx=(10, 5))
        self.menu_button.bind("<Enter>", lambda e: self.menu_button.configure(bg=COLOR_MENU_HOVER))
        self.menu_button.bind("<Leave>", lambda e: self.menu_button.configure(bg=COLOR_TITLE_BAR))
        
        # Título
        self.title_label = tk.Label(
            left_frame,
            text="Registro Biometrico",
            font=("Segoe UI", 12, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_TITLE_BAR
        )
        self.title_label.pack(side="left", padx=5)
        
        # Frame para botones de control
        button_frame = tk.Frame(self.title_bar, bg=COLOR_TITLE_BAR)
        button_frame.pack(side="right", padx=5)
        
        # Botón minimizar
        self.btn_minimize = tk.Button(
            button_frame,
            text="─",
            font=("Segoe UI", 12, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_TITLE_BAR,
            relief="flat",
            cursor="hand2",
            width=3,
            command=self.minimize_window
        )
        self.btn_minimize.pack(side="left", padx=2)
        self.btn_minimize.bind("<Enter>", lambda e: self.btn_minimize.configure(bg=COLOR_MENU_HOVER))
        self.btn_minimize.bind("<Leave>", lambda e: self.btn_minimize.configure(bg=COLOR_TITLE_BAR))
        
        # Botón cerrar
        self.btn_close = tk.Button(
            button_frame,
            text="✕",
            font=("Segoe UI", 12, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_TITLE_BAR,
            relief="flat",
            cursor="hand2",
            width=3,
            command=self.close_window
        )
        self.btn_close.pack(side="left", padx=2)
        self.btn_close.bind("<Enter>", lambda e: self.btn_close.configure(bg=COLOR_DANGER))
        self.btn_close.bind("<Leave>", lambda e: self.btn_close.configure(bg=COLOR_TITLE_BAR))
        
        # Crear menú contextual
        self.menu = Menu(self.title_bar, tearoff=0, bg=COLOR_TITLE_BAR, fg=COLOR_TEXT, font=("Segoe UI", 10))
        self.menu.add_command(label="👥 Usuarios", command=self.open_usuarios)
        self.menu.add_separator()
        self.menu.add_command(label="📊 Reportes", command=self.open_reportes)
        self.menu.add_separator()
        self.menu.add_command(label="⚙️ Configuración", command=self.open_config)
        self.menu.add_separator()
        self.menu.add_command(label="ℹ️ Acerca De", command=self.open_about)
        self.menu.add_separator()
        self.menu.add_command(label="🔄 Refrescar", command=self.refresh_data)
        self.menu.add_separator()
        self.menu.add_command(label="📋 Asistencia", command=self.open_asistencia)

        # Permitir mover la ventana
        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.on_move)
        self.title_label.bind("<Button-1>", self.start_move)
        self.title_label.bind("<B1-Motion>", self.on_move)
        
        self.x = None
        self.y = None
    
    def show_menu(self):
        """Muestra el menú desplegable"""
        self.menu.post(self.menu_button.winfo_rootx(), 
                       self.menu_button.winfo_rooty() + self.menu_button.winfo_height())
    
    def open_usuarios(self):
        """Abre la ventana de gestión de usuarios"""
        usuarios = UsuariosWindow(self.parent, self.app.refrescar_lista)
        usuarios.show()
    
    def open_reportes(self):
        """Abre la ventana de reportes"""
        reportes = ReportesWindow(self.parent)
        reportes.show()
    
    def open_config(self):
        """Abre la ventana de configuración"""
        config = ConfigWindow(self.parent)
        config.show()
    
    def open_about(self):
        """Abre la ventana de acerca de"""
        about = AboutWindow(self.parent)
        about.show()
    
    def refresh_data(self):
        """Refresca los datos de la tabla principal"""
        self.app.refrescar_lista()
        if hasattr(self.app, 'toast'):
            self.app.toast.show("✅ Datos actualizados", "success")
    
    def start_move(self, event):
        self.x = event.x_root - self.parent.winfo_x()
        self.y = event.y_root - self.parent.winfo_y()
    
    def on_move(self, event):
        x = event.x_root - self.x
        y = event.y_root - self.y
        self.parent.geometry(f"+{x}+{y}")
    
    def minimize_window(self):
        self.parent.iconify()
    
    def close_window(self):
        if hasattr(self.parent, 'on_closing'):
            self.parent.on_closing()
        else:
            self.parent.destroy()

    def open_asistencia(self):
        asistencia = AsistenciaWindow(self.parent)
        asistencia.show()

# =========================
# PIN PANEL MODAL
# =========================
class PinModal:
    def __init__(self, parent, usuarios_db, refresh_callback):
        self.parent = parent
        self.usuarios_db = usuarios_db
        self.refresh_callback = refresh_callback
        self.window = None
        self.toast = Toast(parent)

    def show(self):
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = tk.Toplevel(self.parent)
        self.window.title("Acceso PIN")
        self.window.configure(bg=COLOR_BG)
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Hacer el modal responsivo
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Tamaño proporcional
        width = int(screen_width * 0.35)
        height = int(screen_height * 0.5)
        
        # Centrar
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        self.window.minsize(500, 500)

        # Configurar grid principal
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # Frame principal con padding
        main = tk.Frame(self.window, bg=COLOR_BG)
        main.grid(row=0, column=0, sticky="nsew", padx=50, pady=40)
        main.grid_rowconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=2)
        main.grid_rowconfigure(2, weight=1)
        main.grid_rowconfigure(3, weight=2)
        main.grid_rowconfigure(4, weight=2)
        main.grid_columnconfigure(0, weight=1)

        # TÍTULO
        title_frame = tk.Frame(main, bg=COLOR_BG)
        title_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        
        tk.Label(
            title_frame,
            text="🔐 ACCESO PIN",
            font=("Segoe UI", 24, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_BG
        ).pack()

        # TIPO DE ACCESO
        tipo_frame = tk.Frame(main, bg=COLOR_BG)
        tipo_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        tipo_frame.grid_columnconfigure(0, weight=1)
        tipo_frame.grid_columnconfigure(1, weight=1)
        
        tk.Label(
            tipo_frame,
            text="Seleccione tipo de acceso:",
            font=("Segoe UI", 14),
            fg=COLOR_TEXT,
            bg=COLOR_BG
        ).grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky="n")
        
        self.tipo_var = tk.StringVar(value="")

        def set_tipo(t):
            self.tipo_var.set(t)
            if t == "INGRESO":
                btn_ing.config(bg=COLOR_SUCCESS, fg=COLOR_TEXT)
                btn_sal.config(bg=COLOR_PRIMARY, fg=COLOR_TEXT)
            elif t == "SALIDA":
                btn_ing.config(bg=COLOR_PRIMARY, fg=COLOR_TEXT)
                btn_sal.config(bg=COLOR_DANGER, fg=COLOR_TEXT)

        btn_ing = tk.Button(
            tipo_frame,
            text="🚪 INGRESO",
            font=("Segoe UI", 16, "bold"),
            bg=COLOR_PRIMARY,
            fg=COLOR_TEXT,
            relief="flat",
            cursor="hand2",
            height=2,
            command=lambda: set_tipo("INGRESO")
        )
        btn_ing.grid(row=1, column=0, padx=10, sticky="nsew")

        btn_sal = tk.Button(
            tipo_frame,
            text="🏃 SALIDA",
            font=("Segoe UI", 16, "bold"),
            bg=COLOR_PRIMARY,
            fg=COLOR_TEXT,
            relief="flat",
            cursor="hand2",
            height=2,
            command=lambda: set_tipo("SALIDA")
        )
        btn_sal.grid(row=1, column=1, padx=10, sticky="nsew")

        # INPUT PIN
        pin_frame = tk.Frame(main, bg=COLOR_BG)
        pin_frame.grid(row=2, column=0, sticky="nsew", pady=20)
        
        tk.Label(
            pin_frame,
            text="Ingrese su PIN:",
            font=("Segoe UI", 14),
            fg=COLOR_TEXT,
            bg=COLOR_BG
        ).pack(pady=(0, 10))
        
        self.pin_entry = tk.Entry(
            pin_frame,
            font=("Segoe UI", 22, "bold"),
            justify="center",
            show="•",
            relief="solid",
            bd=2
        )
        self.pin_entry.pack(fill="x", ipady=12, padx=20)
        self.pin_entry.focus()

        # BOTONES DE ACCIÓN
        buttons_frame = tk.Frame(main, bg=COLOR_BG)
        buttons_frame.grid(row=3, column=0, sticky="nsew", pady=20)
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)

        self.btn_confirmar = tk.Button(
            buttons_frame,
            text="✓ CONFIRMAR",
            font=("Segoe UI", 16, "bold"),
            bg=COLOR_SUCCESS,
            fg="#003049",
            relief="flat",
            cursor="hand2",
            height=2,
            command=self.verify_pin
        )
        self.btn_confirmar.grid(row=0, column=0, padx=10, sticky="nsew")

        self.btn_cancelar = tk.Button(
            buttons_frame,
            text="✕ CANCELAR",
            font=("Segoe UI", 16, "bold"),
            bg=COLOR_DANGER,
            fg=COLOR_TEXT,
            relief="flat",
            cursor="hand2",
            height=2,
            command=self.close
        )
        self.btn_cancelar.grid(row=0, column=1, padx=10, sticky="nsew")
        
        # Atajos de teclado
        self.window.bind("<Escape>", lambda e: self.close())
        self.pin_entry.bind("<Return>", lambda e: self.verify_pin())

    def verify_pin(self):
        pin = self.pin_entry.get().strip()
        tipo = self.tipo_var.get()

        if not pin:
            self.toast.show("❌ Ingrese un PIN", "warning")
            self.pin_entry.delete(0, tk.END)
            self.pin_entry.focus()
            return

        if not tipo:
            self.toast.show("⚠️ Seleccione INGRESO o SALIDA", "warning")
            return

        # Debug: mostrar qué usuarios están disponibles
        print(f"🔍 Buscando PIN: {pin}")
        print(f"📋 Usuarios activos disponibles: {len(self.usuarios_db)}")
        for u in self.usuarios_db:
            print(f"   - {u['nombre']}: PIN={u['pin']} | Estado={u.get('estado')}")

        usuario = next((u for u in self.usuarios_db if u["pin"] == pin), None)

        if not usuario:
            print(f"❌ PIN {pin} no encontrado")
            self.toast.show("❌ PIN incorrecto", "error")
            self.pin_entry.delete(0, tk.END)
            self.pin_entry.focus()
            return

        # VERIFICAR QUE EL USUARIO ESTÉ ACTIVO
        if usuario.get("estado") != "true":
            print(f"❌ Usuario {usuario['nombre']} está INACTIVO (estado={usuario.get('estado')})")
            self.toast.show(f"❌ Usuario {usuario['nombre']} está INACTIVO\nContacte al administrador", "error")
            self.close()
            return

        print(f"✅ Usuario activo encontrado: {usuario['nombre']}")
        ok, msg = registrar_asistencia(usuario["nombre"], tipo)

        if ok:
            self.toast.show(f"✅ {usuario['nombre']}\n{tipo} registrado", "success")
            # 🔥 ELIMINADO: Ya no pregunta por horas extra en salidas
            self.refresh_callback()
            self.close()
        else:
            self.toast.show(f"❌ {msg}", "error")
            self.close()

    def close(self):
        if self.window and self.window.winfo_exists():
            self.window.destroy()
            self.window = None

# =========================
# VENTANA PRINCIPAL
# =========================
class SmartFaceKiosk:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Registro Biometrico")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg=COLOR_BG)
        
        # Cargar configuración guardada
        self.cargar_configuracion()
        
        # Crear barra de título personalizada con referencia a la app
        self.title_bar = TitleBar(self.root, self)
        
        # Frame principal con grid responsivo
        self.main_frame = tk.Frame(self.root, bg=COLOR_BG)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        
        self.setup_ui()
        self.setup_variables()
        self.setup_callbacks()
        
        # Inicializar datos
        self.cargar_usuarios()
        self.refrescar_lista()
        
        # Bind para salir de pantalla completa con ESC
        self.root.bind("<Escape>", lambda e: self.exit_fullscreen())
        
        # Bind para manejar cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.toast = Toast(self.root)
    
    def cargar_configuracion(self):
        global CAMERA_INDEX
        try:
            with open('config.pkl', 'rb') as f:
                config = pickle.load(f)
                CAMERA_INDEX = config.get('camera_index', 2)
        except:
            pass
    
    def exit_fullscreen(self):
        """Salir del modo pantalla completa"""
        self.root.attributes("-fullscreen", False)
        self.root.geometry("1400x800")
        # Centrar la ventana
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
    
    def setup_variables(self):
        self.usuarios_db = []
        self.cam_active = False
        self.cap = None
        self.confirmado = None
        self.contador = 0
        self.ya_registrado = False
        self.tipo_actual = None
        self.bloqueo_sistema = False
        self.loop_id = None
        self.current_row_index = 0  # Para el color de filas
    
    def setup_ui(self):
        # ==================== COLUMNA IZQUIERDA ====================
        self.left_column = tk.Frame(self.main_frame, bg=COLOR_BG)
        self.left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.left_column.grid_rowconfigure(1, weight=3)
        self.left_column.grid_rowconfigure(0, weight=0)
        self.left_column.grid_rowconfigure(2, weight=0)
        self.left_column.grid_rowconfigure(3, weight=0)
        self.left_column.grid_columnconfigure(0, weight=1)

        # Título Control de Acceso
        tk.Label(
            self.left_column,
            text="CONTROL DE ACCESO",
            font=("Segoe UI", 24, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_BG
        ).grid(row=0, column=0, pady=(0, 20), sticky="n")

        # Contenedor de la cámara
        self.cam_container = tk.Frame(self.left_column, bg=COLOR_SURFACE, relief="flat", bd=2)
        self.cam_container.grid(row=1, column=0, sticky="nsew", pady=(0, 20))
        self.cam_container.grid_rowconfigure(0, weight=1)
        self.cam_container.grid_columnconfigure(0, weight=1)

        self.cam_label = tk.Label(self.cam_container, bg=COLOR_SURFACE)
        self.cam_label.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        self.black_frame = ImageTk.PhotoImage(Image.new("RGB", (800, 600), COLOR_SURFACE))
        self.cam_label.configure(image=self.black_frame)
        self.cam_label.image = self.black_frame

        # Botones debajo de la cámara
        self.buttons_frame = tk.Frame(self.left_column, bg=COLOR_BG)
        self.buttons_frame.grid(row=2, column=0, sticky="ew", pady=10)
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        self.buttons_frame.grid_columnconfigure(1, weight=1)

        self.btn_ingreso = ModernButton(self.buttons_frame, text="🚪 INGRESO", bg_color=COLOR_SUCCESS)
        self.btn_ingreso.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.btn_salida = ModernButton(self.buttons_frame, text="🏃 SALIDA", bg_color=COLOR_DANGER)
        self.btn_salida.grid(row=0, column=1, sticky="ew", padx=(10, 0))

        # Botón PIN debajo
        self.btn_pin = ModernButton(self.left_column, text="🔢 MODO PIN", bg_color=COLOR_PRIMARY)
        self.btn_pin.grid(row=3, column=0, sticky="ew", pady=10)

        # ==================== COLUMNA DERECHA ====================
        self.right_column = tk.Frame(self.main_frame, bg=COLOR_BG)
        self.right_column.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.right_column.grid_rowconfigure(1, weight=1)
        self.right_column.grid_rowconfigure(0, weight=0)
        self.right_column.grid_rowconfigure(2, weight=0)
        self.right_column.grid_columnconfigure(0, weight=1)

        # Título Registros de Hoy
        tk.Label(
            self.right_column,
            text="REGISTROS DE HOY",
            font=("Segoe UI", 24, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_BG
        ).grid(row=0, column=0, pady=(0, 20), sticky="n")

        # Contenedor de la tabla
        self.table_container = tk.Frame(self.right_column, bg=COLOR_SURFACE, relief="flat", bd=2)
        self.table_container.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        self.table_container.grid_rowconfigure(0, weight=1)
        self.table_container.grid_columnconfigure(0, weight=1)

        # Treeview estilizado
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                        background=COLOR_SURFACE,
                        foreground=COLOR_PRIMARY,
                        fieldbackground=COLOR_SURFACE,
                        borderwidth=0,
                        font=("Segoe UI", 11),
                        rowheight=35)
        style.configure("Custom.Treeview.Heading",
                        background=COLOR_PRIMARY,
                        foreground=COLOR_TEXT,
                        font=("Segoe UI", 12, "bold"),
                        borderwidth=0)
        style.map("Custom.Treeview", 
                  background=[('selected', COLOR_SUCCESS)],
                  foreground=[('selected', COLOR_PRIMARY)])

        self.tree_frame = tk.Frame(self.table_container, bg=COLOR_SURFACE)
        self.tree_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(self.tree_frame, style="Custom.Treeview")
        self.tree["columns"] = ("id", "hora", "nombre", "tipo", "horas_extra")
        self.tree.column("#0", width=0, stretch=False)
        self.tree.column("id", width=0, stretch=False)  # Oculto
        self.tree.column("hora", width=120, anchor="center")
        self.tree.column("nombre", width=250, anchor="w")
        self.tree.column("tipo", width=100, anchor="center")
        self.tree.column("horas_extra", width=150, anchor="center")

        self.tree.heading("hora", text="HORA")
        self.tree.heading("nombre", text="NOMBRE")
        self.tree.heading("tipo", text="TIPO")
        self.tree.heading("horas_extra", text="📝 HORAS EXTRA")

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Grid para tree y scrollbar
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Bind doble clic para abrir modal de horas extra (solo en salidas)
        self.tree.bind("<Double-1>", self.abrir_modal_horas_extra)

        # Botón refrescar debajo de la tabla
        self.btn_refresh = ModernButton(self.right_column, text="🔄 REFRESCAR", bg_color=COLOR_SUCCESS)
        self.btn_refresh.grid(row=2, column=0, sticky="ew", pady=10)
    
    def aplicar_colores_filas(self):
        """Aplica colores intercalados a las filas de la tabla"""
        items = self.tree.get_children()
        for i, item in enumerate(items):
            # Determinar el color según la paridad
            if i % 2 == 0:
                bg_color = COLOR_ROW_PAR
            else:
                bg_color = COLOR_ROW_IMPAR
            
            # Aplicar el color a la fila completa
            self.tree.tag_configure(f'row_{i}', background=bg_color)
            self.tree.item(item, tags=(f'row_{i}',))
    
    def abrir_modal_horas_extra(self, event):
        """Abre el modal de horas extra solo para registros de tipo SALIDA"""
        item = self.tree.selection()
        if not item:
            return
        
        values = self.tree.item(item, "values")
        if not values or len(values) < 5:
            return
        
        registro_id = values[0]
        hora = values[1]
        nombre = values[2]
        tipo = values[3]
        
        # Solo permitir horas extra en SALIDAS
        if tipo != "SALIDA":
            self.toast.show("⚠️ Solo se pueden registrar horas extra en salidas", "warning")
            return
        
        # Obtener la fecha del registro
        conn = sqlite3.connect("personas.db")
        cursor = conn.cursor()
        cursor.execute("SELECT fecha FROM asistencias WHERE id = ?", (registro_id,))
        result = cursor.fetchone()
        conn.close()
        
        fecha_registro = result[0] if result else datetime.now().strftime("%Y-%m-%d")
        
        # Abrir modal
        modal = HorasExtraModal(self.root, registro_id, nombre, fecha_registro, hora, self.refrescar_lista)
        modal.show()
    
    def setup_callbacks(self):
        self.btn_ingreso.configure(command=lambda: self.start_camera("INGRESO"))
        self.btn_salida.configure(command=lambda: self.start_camera("SALIDA"))
        self.btn_pin.configure(command=self.abrir_pin_modal)
        self.btn_refresh.configure(command=self.refrescar_lista)
    
    def abrir_pin_modal(self):
        """Abre el modal de PIN"""
        pin_modal = PinModal(self.root, self.usuarios_db, self.refrescar_lista)
        pin_modal.show()
    
    def cargar_usuarios(self):
        """Carga SOLO usuarios con estado = 'true'"""
        conn = sqlite3.connect("personas.db")
        cursor = conn.cursor()
        # SOLO usuarios ACTIVOS (estado = "true")
        cursor.execute("SELECT id, Nombre_Completo, Pin, descriptores, estado FROM personas WHERE estado = 'true'")
        data = cursor.fetchall()
        conn.close()
        
        self.usuarios_db = []
        for pid, nombre, pin, emb_blob, estado in data:
            # Cargar embeddings si existen
            embeddings = []
            if emb_blob is not None and len(emb_blob) > 0:
                try:
                    emb_list = pickle.loads(emb_blob)
                    if emb_list:
                        # Normalizar cada embedding
                        for emb in emb_list:
                            if isinstance(emb, np.ndarray):
                                embeddings.append(emb / np.linalg.norm(emb))
                            else:
                                embeddings.append(emb)
                    print(f"   📸 {nombre}: {len(embeddings)} embeddings cargados")
                except Exception as e:
                    print(f"   ⚠️ Error cargando embeddings de {nombre}: {e}")
                    embeddings = []
            
            self.usuarios_db.append({
                "id": pid,
                "nombre": nombre,
                "pin": pin,
                "embeddings": embeddings,
                "estado": estado
            })
        
        # Debug: mostrar usuarios cargados
        print(f"📋 Usuarios ACTIVOS cargados: {len(self.usuarios_db)}")
        for u in self.usuarios_db:
            tiene_rostro = "✅" if u['embeddings'] else "❌"
            print(f"   👤 {u['nombre']} | PIN: {u['pin']} | Rostro: {tiene_rostro} | Estado: {u['estado']}")
    
    def obtener_asistencias(self):
        conn = sqlite3.connect("personas.db")
        cursor = conn.cursor()
        
        # Verificar si la columna horas_extra existe
        try:
            cursor.execute("SELECT horas_extra FROM asistencias LIMIT 1")
        except sqlite3.OperationalError:
            # Crear la columna si no existe
            cursor.execute("ALTER TABLE asistencias ADD COLUMN horas_extra TEXT")
            conn.commit()
        
        hoy = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT a.id, a.hora, p.Nombre_Completo, a.tipo, IFNULL(a.horas_extra, '')
            FROM asistencias a
            JOIN personas p ON p.id = a.persona_id
            WHERE DATE(a.fecha) = ?
            ORDER BY a.id DESC
        """, (hoy,))
        data = cursor.fetchall()
        conn.close()
        return data
    
    def refrescar_lista(self):
        # IMPORTANTE: Recargar usuarios primero
        self.cargar_usuarios()  # Esto actualiza self.usuarios_db
        
        # Limpiar la tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Cargar datos
        for registro_id, hora, nombre, tipo, horas_extra in self.obtener_asistencias():
            # Mostrar solo indicador si tiene horas extra
            if horas_extra and horas_extra.strip():
                horas_extra_display = "✨ + Horas Extra"
            else:
                horas_extra_display = ""
            
            self.tree.insert("", "end", values=(registro_id, hora, nombre, tipo, horas_extra_display))
        
        # Aplicar colores intercalados después de insertar todas las filas
        self.aplicar_colores_filas()
        
        # Debug: mostrar cuántos usuarios hay
        print(f"🔄 Refresh completado - Usuarios activos: {len(self.usuarios_db)}")
    
    def reconocer(self, frame):
        faces = engine.app.get(frame)
        if len(faces) == 0:
            return None, 999, frame
        
        best_user = None
        best_dist = 999
        
        for face in faces:
            emb = face.embedding / np.linalg.norm(face.embedding)
            for user in self.usuarios_db:
                for saved in user["embeddings"]:
                    dist = np.linalg.norm(saved - emb)
                    if dist < best_dist:
                        best_dist = dist
                        best_user = user
            
            box = face.bbox.astype(int)
            cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (161, 221, 112), 2)
        
        return best_user, best_dist, frame
    
    def stop_camera(self):
        self.cam_active = False
        self.bloqueo_sistema = True
        if self.loop_id:
            self.cam_label.after_cancel(self.loop_id)
            self.loop_id = None
        if self.cap:
            self.cap.release()
            self.cap = None
        self.cam_label.configure(image=self.black_frame)
        self.cam_label.image = self.black_frame
    
    def loop(self):
        if not self.cam_active or self.bloqueo_sistema:
            return
        
        if self.cap is None or not self.cap.isOpened():
            return
        
        ret, frame = self.cap.read()
        if not ret:
            return
        
        # Redimensionar manteniendo aspecto
        frame_height, frame_width = frame.shape[:2]
        container_width = self.cam_label.winfo_width()
        container_height = self.cam_label.winfo_height()
        
        if container_width > 1 and container_height > 1:
            ratio = min(container_width / frame_width, container_height / frame_height)
            new_width = int(frame_width * ratio)
            new_height = int(frame_height * ratio)
            frame = cv2.resize(frame, (new_width, new_height))
        else:
            frame = cv2.resize(frame, (800, 600))
        
        user, dist, frame = self.reconocer(frame)
        
        estado = "🔍 Buscando..."
        
        if user and dist < 0.8:
            nombre = user["nombre"]
            
            # VERIFICAR QUE EL USUARIO ESTÉ ACTIVO
            if user.get("estado") != "true":
                estado = "❌ Usuario Inactivo"
                self.bloqueo_sistema = True
                self.toast.show(f"❌ {nombre} está INACTIVO\nContacte al administrador", "error")
                self.stop_camera()
                return
            
            if self.confirmado == nombre:
                self.contador += 1
            else:
                self.confirmado = nombre
                self.contador = 1
            
            if self.contador >= 5 and not self.ya_registrado:
                ok, msg = registrar_asistencia(nombre, self.tipo_actual)
                self.bloqueo_sistema = True
                
                if ok:
                    self.ya_registrado = True
                    self.toast.show(f"✅ {nombre}\n{self.tipo_actual} registrado", "success")
                    # 🔥 ELIMINADO: Ya no pregunta por horas extra en salidas
                else:
                    self.toast.show(msg, "error")
                
                self.stop_camera()
                self.refrescar_lista()
                return
            
            estado = f"✓ {nombre} Identificado (Activo)"
        else:
            self.confirmado = None
            self.contador = 0
            self.ya_registrado = False
            estado = "❓ Desconocido o Inactivo"
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], 60), (0, 48, 73), -1)
        frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
        
        # Escalar tamaño de texto
        font_scale = min(container_width, container_height) / 600
        cv2.putText(frame, estado, (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, max(0.6, font_scale),
                    (161, 221, 112), 2)
        
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        
        self.cam_label.configure(image=imgtk)
        self.cam_label.image = imgtk
        
        self.loop_id = self.cam_label.after(10, self.loop)
    
    def start_camera(self, tipo):
        self.cam_active = True
        self.bloqueo_sistema = False
        self.tipo_actual = tipo
        self.confirmado = None
        self.contador = 0
        self.ya_registrado = False
        
        self.cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
        
        if not self.cap.isOpened():
            self.toast.show("❌ Error al acceder a la cámara", "error")
            self.cam_active = False
            return
        
        self.loop()
    
    def on_closing(self):
        # Detener la cámara si está activa
        self.stop_camera()
        # Cerrar la ventana
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()

# =========================
# EJECUTAR APLICACIÓN
# =========================
if __name__ == "__main__":
    init_db()  # CREA LAS TABLAS AUTOMÁTICAMENTE
    app = SmartFaceKiosk()
    app.run()