import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import pickle
import base64
import cv2
import numpy as np
from datetime import datetime
from face_engine import FaceEngine

# Colores
COLOR_PRIMARY = "#003049"
COLOR_SUCCESS = "#A1DD70"
COLOR_DANGER = "#FF5555"
COLOR_TEXT = "#FFFFFF"
COLOR_BG = "#003049"
COLOR_SURFACE = "#FFFFFF"
COLOR_TITLE_BAR = "#002238"

class UsuariosWindow:
    def __init__(self, parent, refresh_callback):
        self.parent = parent
        self.refresh_callback = refresh_callback
        self.window = None
        self.usuario_editando = None
        self.pin_original = None  # Para guardar el PIN original al editar
        self.engine = FaceEngine()
        self.cargar_configuracion_camara()  # Cargar configuración al inicio
        
    def cargar_configuracion_camara(self):
        """Carga la configuración desde config.pkl"""
        try:
            with open('config.pkl', 'rb') as f:
                config = pickle.load(f)
                self.camara_index = config.get('camera_index', 2)
                self.frames_confirmacion = config.get('frames_confirmacion', 5)
                self.umbral = config.get('umbral_reconocimiento', 0.8)
        except:
            self.camara_index = 2
            self.frames_confirmacion = 5
            self.umbral = 0.8
            print("⚠️ No se encontró config.pkl, usando valores por defecto")
        
    def show(self):
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
            
        self.window = tk.Toplevel(self.parent)
        self.window.title("Gestión de Usuarios")
        self.window.configure(bg=COLOR_BG)
        self.window.transient(self.parent)
        self.window.grab_set()
        
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        width = int(screen_width * 0.8)
        height = int(screen_height * 0.8)
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        self.window.minsize(900, 600)
        
        # Frame principal con dos columnas
        main = tk.Frame(self.window, bg=COLOR_BG, padx=20, pady=20)
        main.pack(fill="both", expand=True)
        
        # Título principal
        tk.Label(
            main,
            text="👥 GESTIÓN DE USUARIOS",
            font=("Segoe UI", 20, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_BG
        ).pack(pady=(0, 20))
        
        # Frame para las dos columnas
        columns_frame = tk.Frame(main, bg=COLOR_BG)
        columns_frame.pack(fill="both", expand=True)
        columns_frame.grid_columnconfigure(0, weight=1)
        columns_frame.grid_columnconfigure(1, weight=1)
        columns_frame.grid_rowconfigure(0, weight=1)
        
        # ==================== COLUMNA IZQUIERDA - LISTA DE USUARIOS ====================
        left_frame = tk.Frame(columns_frame, bg=COLOR_BG)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        tk.Label(
            left_frame,
            text="📋 USUARIOS REGISTRADOS",
            font=("Segoe UI", 14, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_BG
        ).pack(anchor="w", pady=(0, 10))
        
        # Contenedor de la tabla
        table_container = tk.Frame(left_frame, bg=COLOR_SURFACE)
        table_container.pack(fill="both", expand=True)
        
        # Treeview - SIN columna de PIN por seguridad
        self.tree = ttk.Treeview(table_container, style="Custom.Treeview")
        self.tree["columns"] = ("id", "nombre", "dni", "cargo", "pin", "estado")
        self.tree.column("#0", width=0, stretch=False)
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("nombre", width=150)
        self.tree.column("dni", width=100, anchor="center")
        self.tree.column("cargo", width=120)
        self.tree.column("pin", width=100, anchor="center")
        self.tree.column("estado", width=80, anchor="center")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="NOMBRE")
        self.tree.heading("dni", text="DNI")
        self.tree.heading("cargo", text="CARGO")
        self.tree.heading("pin", text="PIN")
        self.tree.heading("estado", text="ESTADO")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botones de acción debajo de la tabla
        left_buttons = tk.Frame(left_frame, bg=COLOR_BG)
        left_buttons.pack(fill="x", pady=10)
        left_buttons.grid_columnconfigure(0, weight=1)
        left_buttons.grid_columnconfigure(1, weight=1)
        
        tk.Button(
            left_buttons,
            text="✏️ EDITAR",
            font=("Segoe UI", 11, "bold"),
            bg=COLOR_PRIMARY,
            fg=COLOR_TEXT,
            height=1,
            command=self.editar_usuario
        ).grid(row=0, column=0, padx=5, sticky="ew")
        
        tk.Button(
            left_buttons,
            text="🗑️ ELIMINAR",
            font=("Segoe UI", 11, "bold"),
            bg=COLOR_DANGER,
            fg=COLOR_TEXT,
            height=1,
            command=self.eliminar_usuario
        ).grid(row=0, column=1, padx=5, sticky="ew")
        
        # ==================== COLUMNA DERECHA - FORMULARIO ====================
        right_frame = tk.Frame(columns_frame, bg=COLOR_SURFACE, relief="flat", bd=2)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Canvas con scroll para el formulario
        canvas = tk.Canvas(right_frame, bg=COLOR_SURFACE, highlightthickness=0)
        scrollbar_form = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLOR_SURFACE)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=right_frame.winfo_width())
        canvas.configure(yscrollcommand=scrollbar_form.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_form.pack(side="right", fill="y")
        
        # Actualizar el ancho del canvas cuando cambie el tamaño
        def configure_canvas(event):
            canvas.itemconfig(1, width=event.width)
        
        right_frame.bind("<Configure>", configure_canvas)
        
        # Título del formulario
        self.form_title = tk.Label(
            scrollable_frame,
            text="➕ NUEVO USUARIO",
            font=("Segoe UI", 16, "bold"),
            fg=COLOR_PRIMARY,
            bg=COLOR_SURFACE
        )
        self.form_title.pack(pady=(20, 20))
        
        # Frame para campos del formulario
        form_frame = tk.Frame(scrollable_frame, bg=COLOR_SURFACE)
        form_frame.pack(fill="both", expand=True, padx=30)
        
        # Campo Nombre
        tk.Label(
            form_frame,
            text="Nombre Completo:",
            font=("Segoe UI", 11, "bold"),
            fg=COLOR_PRIMARY,
            bg=COLOR_SURFACE
        ).pack(anchor="w", pady=(0, 5))
        
        self.nombre_entry = tk.Entry(
            form_frame,
            font=("Segoe UI", 11),
            relief="solid",
            bd=1
        )
        self.nombre_entry.pack(fill="x", pady=(0, 15), ipady=6)
        
        # Campo DNI
        tk.Label(
            form_frame,
            text="DNI:",
            font=("Segoe UI", 11, "bold"),
            fg=COLOR_PRIMARY,
            bg=COLOR_SURFACE
        ).pack(anchor="w", pady=(0, 5))
        
        self.dni_entry = tk.Entry(
            form_frame,
            font=("Segoe UI", 11),
            relief="solid",
            bd=1
        )
        self.dni_entry.pack(fill="x", pady=(0, 15), ipady=6)
        
        # Campo Cargo
        tk.Label(
            form_frame,
            text="Cargo:",
            font=("Segoe UI", 11, "bold"),
            fg=COLOR_PRIMARY,
            bg=COLOR_SURFACE
        ).pack(anchor="w", pady=(0, 5))
        
        self.cargo_entry = tk.Entry(
            form_frame,
            font=("Segoe UI", 11),
            relief="solid",
            bd=1
        )
        self.cargo_entry.pack(fill="x", pady=(0, 15), ipady=6)
        
        # Campo Tiempo
        tk.Label(
            form_frame,
            text="Tiempo de Contrato:",
            font=("Segoe UI", 11, "bold"),
            fg=COLOR_PRIMARY,
            bg=COLOR_SURFACE
        ).pack(anchor="w", pady=(0, 5))
        
        self.tiempo_var = tk.StringVar(value="COMPLETO")
        tiempo_options = ["COMPLETO", "MEDIO", "PARCIAL"]
        tiempo_menu = ttk.Combobox(form_frame, textvariable=self.tiempo_var, values=tiempo_options, state="readonly")
        tiempo_menu.pack(fill="x", pady=(0, 15))
        
        # Campo Estado
        tk.Label(
            form_frame,
            text="Estado:",
            font=("Segoe UI", 11, "bold"),
            fg=COLOR_PRIMARY,
            bg=COLOR_SURFACE
        ).pack(anchor="w", pady=(0, 5))
        
        self.estado_var = tk.StringVar(value="true")
        estado_frame = tk.Frame(form_frame, bg=COLOR_SURFACE)
        estado_frame.pack(fill="x", pady=(0, 15))
        
        tk.Radiobutton(
            estado_frame,
            text="ACTIVO",
            variable=self.estado_var,
            value="true",
            bg=COLOR_SURFACE,
            fg=COLOR_PRIMARY,
            selectcolor=COLOR_SURFACE,
            font=("Segoe UI", 10)
        ).pack(side="left", padx=(0, 20))
        
        tk.Radiobutton(
            estado_frame,
            text="INACTIVO",
            variable=self.estado_var,
            value="false",
            bg=COLOR_SURFACE,
            fg=COLOR_PRIMARY,
            selectcolor=COLOR_SURFACE,
            font=("Segoe UI", 10)
        ).pack(side="left")
        
        # Campo PIN - con show="•" para ocultar caracteres
        tk.Label(
            form_frame,
            text="PIN (4-6 dígitos):",
            font=("Segoe UI", 11, "bold"),
            fg=COLOR_PRIMARY,
            bg=COLOR_SURFACE
        ).pack(anchor="w", pady=(0, 5))
        
        self.pin_entry = tk.Entry(
            form_frame,
            font=("Segoe UI", 11),
            relief="solid",
            bd=1,
            show="•"  # Ocultar el PIN
        )
        self.pin_entry.pack(fill="x", pady=(0, 15), ipady=6)
        
        # Botón para capturar rostro
        self.btn_capturar = tk.Button(
            form_frame,
            text="📸 CAPTURAR ROSTRO",
            font=("Segoe UI", 12, "bold"),
            bg=COLOR_PRIMARY,
            fg=COLOR_TEXT,
            relief="flat",
            cursor="hand2",
            height=1,
            command=self.capturar_rostro
        )
        self.btn_capturar.pack(fill="x", pady=(0, 15))
        self.btn_capturar.bind("<Enter>", lambda e: self.btn_capturar.configure(bg="#004466"))
        self.btn_capturar.bind("<Leave>", lambda e: self.btn_capturar.configure(bg=COLOR_PRIMARY))
        
        # Labels para mostrar estado de la captura
        self.captura_label = tk.Label(
            form_frame,
            text="⚠️ No se ha capturado rostro",
            font=("Segoe UI", 9),
            fg=COLOR_DANGER,
            bg=COLOR_SURFACE
        )
        self.captura_label.pack(pady=(0, 15))
        
        # Variables para almacenar los embeddings y la imagen
        self.embeddings_capturados = []
        self.imagen_base64 = None
        
        # Frame para botones del formulario
        form_buttons = tk.Frame(form_frame, bg=COLOR_SURFACE)
        form_buttons.pack(fill="x", pady=(10, 20))
        form_buttons.grid_columnconfigure(0, weight=1)
        form_buttons.grid_columnconfigure(1, weight=1)
        
        # Botón GUARDAR
        self.btn_guardar = tk.Button(
            form_buttons,
            text="💾 GUARDAR",
            font=("Segoe UI", 12, "bold"),
            bg=COLOR_SUCCESS,
            fg="#003049",
            relief="flat",
            cursor="hand2",
            height=1,
            command=self.guardar_usuario
        )
        self.btn_guardar.grid(row=0, column=0, padx=5, sticky="ew")
        self.btn_guardar.bind("<Enter>", lambda e: self.btn_guardar.configure(bg="#B8FF88"))
        self.btn_guardar.bind("<Leave>", lambda e: self.btn_guardar.configure(bg=COLOR_SUCCESS))
        
        # Botón CANCELAR / LIMPIAR
        self.btn_cancelar = tk.Button(
            form_buttons,
            text="❌ LIMPIAR",
            font=("Segoe UI", 12, "bold"),
            bg=COLOR_DANGER,
            fg=COLOR_TEXT,
            relief="flat",
            cursor="hand2",
            height=1,
            command=self.limpiar_formulario
        )
        self.btn_cancelar.grid(row=0, column=1, padx=5, sticky="ew")
        self.btn_cancelar.bind("<Enter>", lambda e: self.btn_cancelar.configure(bg="#FF6666"))
        self.btn_cancelar.bind("<Leave>", lambda e: self.btn_cancelar.configure(bg=COLOR_DANGER))
        
        # Botón cerrar ventana
        tk.Button(
            main,
            text="CERRAR VENTANA",
            font=("Segoe UI", 12, "bold"),
            bg=COLOR_TITLE_BAR,
            fg=COLOR_TEXT,
            height=1,
            command=self.window.destroy
        ).pack(fill="x", pady=(20, 0))
        
        # Cargar usuarios y bindear selección
        self.cargar_usuarios()
        self.tree.bind("<<TreeviewSelect>>", self.on_select_usuario)
        
        # Bind para tecla Escape
        self.window.bind("<Escape>", lambda e: self.limpiar_formulario())
    
    def capturar_rostro(self):
        """Captura el rostro del usuario usando la cámara configurada"""
        # Recargar configuración por si cambió
        self.cargar_configuracion_camara()
        
        cap = cv2.VideoCapture(self.camara_index, cv2.CAP_DSHOW)
        
        if not cap.isOpened():
            messagebox.showerror("Error", f"No se pudo abrir la cámara en el índice {self.camara_index}\nVerifique la configuración")
            return
        
        embeddings = []
        count = 0
        frame_guardado = None
        
        # Crear ventana de captura con tkinter en lugar de OpenCV
        capture_window = tk.Toplevel(self.window)
        capture_window.title("Captura de Rostro")
        capture_window.geometry("660x540")
        capture_window.configure(bg=COLOR_BG)
        capture_window.transient(self.window)
        capture_window.grab_set()
        
        # Label para mostrar el video
        video_label = tk.Label(capture_window, bg=COLOR_BG)
        video_label.pack(pady=10)
        
        # Label para instrucciones
        info_label = tk.Label(
            capture_window,
            text="Mueva su rostro frente a la cámara...",
            font=("Segoe UI", 12),
            fg=COLOR_TEXT,
            bg=COLOR_BG
        )
        info_label.pack(pady=5)
        
        # Label para contador
        count_label = tk.Label(
            capture_window,
            text=f"Capturas: 0/15",
            font=("Segoe UI", 14, "bold"),
            fg=COLOR_SUCCESS,
            bg=COLOR_BG
        )
        count_label.pack(pady=5)
        
        # Botón para cancelar
        cancel_btn = tk.Button(
            capture_window,
            text="CANCELAR",
            font=("Segoe UI", 11, "bold"),
            bg=COLOR_DANGER,
            fg=COLOR_TEXT,
            command=lambda: cancelar_captura()
        )
        cancel_btn.pack(pady=10)
        
        def cancelar_captura():
            nonlocal capturando
            capturando = False
            capture_window.destroy()
        
        capturando = True
        
        def actualizar_frame():
            nonlocal count, frame_guardado, capturando
            
            if not capturando:
                return
            
            ret, frame = cap.read()
            if not ret:
                if capturando:
                    capture_window.after(10, actualizar_frame)
                return
            
            frame = cv2.resize(frame, (640, 480))
            frame_guardado = frame
            
            emb = self.engine.get_embedding(frame)
            
            if emb is not None and count < 15:
                embeddings.append(emb)
                count += 1
                count_label.config(text=f"Capturas: {count}/15")
                info_label.config(text=f"✅ Captura {count}/15 completada", fg=COLOR_SUCCESS)
                
                if count >= 15:
                    capturando = False
                    cap.release()
                    capture_window.destroy()
                    
                    if len(embeddings) > 0:
                        self.embeddings_capturados = embeddings
                        if frame_guardado is not None:
                            _, buffer = cv2.imencode('.jpg', frame_guardado)
                            self.imagen_base64 = base64.b64encode(buffer).decode('utf-8')
                        
                        self.captura_label.config(text="✅ Rostro capturado correctamente", fg=COLOR_SUCCESS)
                        messagebox.showinfo("Éxito", f"Rostro capturado con {len(embeddings)} muestras")
                    else:
                        self.captura_label.config(text="❌ Error en la captura", fg=COLOR_DANGER)
                        messagebox.showerror("Error", "No se pudo capturar el rostro")
                    return
            elif emb is None:
                info_label.config(text="⚠️ No se detecta rostro, ajuste su posición", fg=COLOR_DANGER)
            else:
                info_label.config(text="✅ Rostro detectado, mantenga la posición", fg=COLOR_SUCCESS)
            
            # Convertir frame de OpenCV a formato para tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = cv2.resize(frame_rgb, (640, 480))
            img_tk = tk.PhotoImage(data=cv2.imencode('.ppm', img)[1].tobytes())
            
            video_label.config(image=img_tk)
            video_label.image = img_tk
            
            if capturando and count < 15:
                capture_window.after(10, actualizar_frame)
        
        # Iniciar captura
        actualizar_frame()
        
        # Cuando se cierre la ventana
        def on_closing():
            nonlocal capturando
            capturando = False
            cap.release()
            capture_window.destroy()
        
        capture_window.protocol("WM_DELETE_WINDOW", on_closing)
    
    def cargar_usuarios(self):
        """Carga los usuarios en el Treeview (sin mostrar el PIN por seguridad)"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        conn = sqlite3.connect("personas.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, Nombre_Completo, Dni, Cargo, Pin, estado FROM personas ORDER BY id")
        data = cursor.fetchall()
        conn.close()
        
        for row in data:
            pin_visible = str(row[4])
            estado_texto = "🟢 ACTIVO" if row[5] == "true" else "🔴 INACTIVO"
            
            self.tree.insert(
                "", 
                "end", 
                values=(row[0], row[1], row[2], row[3], pin_visible, estado_texto)
            )
    
    def on_select_usuario(self, event):
        """Cuando se selecciona un usuario, cargar sus datos en el formulario (sin mostrar el PIN)"""
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        usuario = item['values']
        
        # Obtener datos completos del usuario (incluyendo PIN para edición)
        conn = sqlite3.connect("personas.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, Nombre_Completo, Dni, Cargo, Tiempo, estado, Pin 
            FROM personas WHERE id = ?
        """, (usuario[0],))
        data = cursor.fetchone()
        conn.close()
        
        if data:
            self.usuario_editando = {
                'id': data[0],
                'nombre': data[1],
                'dni': data[2],
                'cargo': data[3],
                'tiempo': data[4],
                'estado': data[5],
                'pin': data[6]
            }
            
            # Guardar el PIN original para no mostrarlo
            self.pin_original = data[6]
            
            # Cargar datos en el formulario
            self.nombre_entry.delete(0, tk.END)
            self.nombre_entry.insert(0, data[1])
            
            self.dni_entry.delete(0, tk.END)
            self.dni_entry.insert(0, data[2])
            
            self.cargo_entry.delete(0, tk.END)
            self.cargo_entry.insert(0, data[3])
            
            self.tiempo_var.set(data[4])
            self.estado_var.set(data[5])
            
            # NO mostrar el PIN real, mostrar puntos
            self.pin_entry.delete(0, tk.END)
            self.pin_entry.insert(0, "••••")  # Muestra puntos en lugar del PIN real
            
            # Cambiar título del formulario
            self.form_title.config(text=f"✏️ EDITANDO: {data[1]}")
            self.btn_guardar.config(text="💾 ACTUALIZAR")
            self.captura_label.config(text="ℹ️ Para cambiar el rostro, capture nuevamente", fg=COLOR_PRIMARY)
    
    def limpiar_formulario(self):
        """Limpia el formulario y resetea el estado"""
        self.nombre_entry.delete(0, tk.END)
        self.dni_entry.delete(0, tk.END)
        self.cargo_entry.delete(0, tk.END)
        self.tiempo_var.set("COMPLETO")
        self.estado_var.set("true")
        self.pin_entry.delete(0, tk.END)  # Limpiar completamente el campo PIN
        
        self.embeddings_capturados = []
        self.imagen_base64 = None
        self.usuario_editando = None
        self.pin_original = None  # Limpiar PIN original
        
        self.form_title.config(text="➕ NUEVO USUARIO")
        self.btn_guardar.config(text="💾 GUARDAR")
        self.captura_label.config(text="⚠️ Debe capturar el rostro", fg=COLOR_DANGER)
        
        # Quitar selección del treeview
        for item in self.tree.selection():
            self.tree.selection_remove(item)
        
        self.nombre_entry.focus()
    
    def guardar_usuario(self):
        """Guarda un nuevo usuario o actualiza uno existente"""
        nombre = self.nombre_entry.get().strip()
        dni = self.dni_entry.get().strip()
        cargo = self.cargo_entry.get().strip()
        tiempo = self.tiempo_var.get()
        estado = self.estado_var.get()

        # Obtener PIN
        pin_ingresado = self.pin_entry.get().strip()

        if self.usuario_editando and pin_ingresado == "••••":
            pin = self.pin_original
        else:
            pin = pin_ingresado

        # =========================
        # VALIDACIONES
        # =========================
        if not nombre or not dni or not cargo or not pin:
            messagebox.showwarning("Advertencia", "Complete todos los campos obligatorios")
            return

        if not pin.isdigit() or len(pin) < 4 or len(pin) > 6:
            messagebox.showwarning("Advertencia", "El PIN debe tener 4-6 dígitos numéricos")
            return

        if not self.usuario_editando and len(self.embeddings_capturados) == 0:
            messagebox.showwarning("Advertencia", "Debe capturar el rostro del usuario")
            return

        conn = sqlite3.connect("personas.db")
        cursor = conn.cursor()

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # =========================
        # ACTUALIZAR USUARIO
        # =========================
        if self.usuario_editando:

            if len(self.embeddings_capturados) > 0:
                # Normalizar embeddings antes de guardar
                embeddings_norm = []
                for emb in self.embeddings_capturados:
                    if isinstance(emb, np.ndarray):
                        embeddings_norm.append(emb / np.linalg.norm(emb))
                    else:
                        embeddings_norm.append(emb)
                
                emb_blob = pickle.dumps(embeddings_norm)
                imagen = self.imagen_base64

                cursor.execute("""
                    UPDATE personas 
                    SET Nombre_Completo = ?, Dni = ?, Cargo = ?, Tiempo = ?, 
                        estado = ?, Pin = ?, imagen = ?, descriptores = ?, updated_at = ?
                    WHERE id = ?
                """, (
                    nombre, dni, cargo, tiempo, estado,
                    pin, imagen, emb_blob, now,
                    self.usuario_editando['id']
                ))
            else:
                cursor.execute("""
                    UPDATE personas 
                    SET Nombre_Completo = ?, Dni = ?, Cargo = ?, Tiempo = ?, 
                        estado = ?, Pin = ?, updated_at = ?
                    WHERE id = ?
                """, (
                    nombre, dni, cargo, tiempo, estado,
                    pin, now,
                    self.usuario_editando['id']
                ))

            messagebox.showinfo("Éxito", "Usuario actualizado correctamente")

        # =========================
        # INSERTAR USUARIO
        # =========================
        else:

            cursor.execute("SELECT id FROM personas WHERE Pin = ?", (pin,))
            if cursor.fetchone():
                messagebox.showwarning("Advertencia", "El PIN ya está registrado por otro usuario")
                conn.close()
                return

            # Normalizar embeddings antes de guardar
            embeddings_norm = []
            for emb in self.embeddings_capturados:
                if isinstance(emb, np.ndarray):
                    embeddings_norm.append(emb / np.linalg.norm(emb))
                else:
                    embeddings_norm.append(emb)
            
            emb_blob = pickle.dumps(embeddings_norm)

            cursor.execute("""
                INSERT INTO personas (
                    Nombre_Completo, Dni, Cargo, Tiempo, estado, Pin,
                    imagen, descriptores, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                nombre, dni, cargo, tiempo, estado, pin,
                self.imagen_base64, emb_blob, now, now
            ))

            messagebox.showinfo("Éxito", "Usuario creado correctamente")

        conn.commit()
        conn.close()

        # =========================
        # REFRESH CORRECTO UI
        # =========================

        # Recargar tabla de usuarios
        self.cargar_usuarios()

        # IMPORTANTE: Ejecutar el callback para recargar usuarios en la ventana principal
        if self.refresh_callback:
            print("🔄 Ejecutando refresh_callback para recargar usuarios...")
            self.refresh_callback()

        # Limpiar formulario después de recargar
        self.limpiar_formulario()

        # Forzar refresco visual inmediato
        self.window.update_idletasks()

        # Limpiar selección del tree por seguridad
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def editar_usuario(self):
        """Editar usuario seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un usuario de la lista")
            return
        self.nombre_entry.focus()
    
    def eliminar_usuario(self):
        """Elimina el usuario seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un usuario para eliminar")
            return
        
        item = self.tree.item(selected[0])
        usuario = item['values']
        nombre = usuario[1]
        
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar al usuario '{nombre}'?\n¡Esta acción no se puede deshacer!"):
            usuario_id = usuario[0]
            
            conn = sqlite3.connect("personas.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM personas WHERE id = ?", (usuario_id,))
            conn.commit()
            conn.close()
            
            self.cargar_usuarios()
            
            # Ejecutar callback para actualizar ventana principal
            if self.refresh_callback:
                self.refresh_callback()
            
            # Si el usuario eliminado estaba siendo editado, limpiar formulario
            if self.usuario_editando and self.usuario_editando['id'] == usuario_id:
                self.limpiar_formulario()
            
            messagebox.showinfo("Éxito", "Usuario eliminado correctamente")