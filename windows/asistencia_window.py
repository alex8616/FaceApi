import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from calendar import monthrange

COLOR_PRIMARY = "#003049"
COLOR_SECONDARY = "#EAE2B7"
COLOR_ACCENT = "#D62828"
COLOR_SUCCESS = "#2A9D8F"
COLOR_TEXT = "#FFFFFF"
COLOR_BG = "#003049"
COLOR_SURFACE = "#FFFFFF"

MESES = {
    "Enero": "01", "Febrero": "02", "Marzo": "03", "Abril": "04",
    "Mayo": "05", "Junio": "06", "Julio": "07", "Agosto": "08",
    "Septiembre": "09", "Octubre": "10", "Noviembre": "11", "Diciembre": "12"
}

# Contraseña de acceso
CONTRASENA_ACCESO = "elextranjero"

class AsistenciaWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.selected_id = None
        self.current_filter = None
        self.acceso_autorizado = False
        
        # Asegurar que la columna detalles existe
        self.agregar_columna_detalles()

    def agregar_columna_detalles(self):
        """Agrega la columna detalles a la tabla asistencias si no existe"""
        try:
            conn = sqlite3.connect("personas.db")
            cursor = conn.cursor()
            cursor.execute("ALTER TABLE asistencias ADD COLUMN detalles TEXT")
            conn.commit()
            print("✅ Columna 'detalles' agregada a la tabla asistencias")
        except sqlite3.OperationalError:
            pass
        finally:
            conn.close()

    def show(self):
        """Muestra la ventana principal después de autenticar"""
        if self.acceso_autorizado and self.window and self.window.winfo_exists():
            self.window.lift()
            self.window.focus()
            return
        
        # Mostrar diálogo de contraseña
        self.mostrar_password_dialog()

    def mostrar_password_dialog(self):
        """Muestra el diálogo de autenticación"""
        # Crear ventana de diálogo
        dialog = tk.Toplevel(self.parent)
        dialog.title("🔐 Acceso Restringido - Sistema de Asistencia")
        dialog.configure(bg=COLOR_BG)
        dialog.transient(self.parent)
        dialog.grab_set()
        dialog.focus_force()
        
        # Centrar el diálogo
        dialog.update_idletasks()
        width = 420
        height = 320
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.resizable(False, False)
        
        # Frame principal
        main = tk.Frame(dialog, bg=COLOR_BG, padx=30, pady=30)
        main.pack(fill="both", expand=True)
        
        # Icono y título
        tk.Label(
            main,
            text="🔐",
            font=("Segoe UI", 56),
            fg=COLOR_SUCCESS,
            bg=COLOR_BG
        ).pack(pady=(0, 10))
        
        tk.Label(
            main,
            text="SISTEMA DE ASISTENCIA",
            font=("Segoe UI", 14, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_BG
        ).pack(pady=(0, 5))
        
        tk.Label(
            main,
            text="Acceso Restringido",
            font=("Segoe UI", 11),
            fg=COLOR_SECONDARY,
            bg=COLOR_BG
        ).pack(pady=(0, 20))
        
        tk.Label(
            main,
            text="Ingrese la contraseña de administrador:",
            font=("Segoe UI", 10),
            fg=COLOR_TEXT,
            bg=COLOR_BG
        ).pack(pady=(0, 10))
        
        # Campo de contraseña
        self.password_entry = tk.Entry(
            main,
            font=("Segoe UI", 14),
            show="•",
            justify="center",
            relief="solid",
            bd=2,
            width=20
        )
        self.password_entry.pack(pady=(0, 20), ipady=8)
        self.password_entry.focus()
        
        # Botones
        btn_frame = tk.Frame(main, bg=COLOR_BG)
        btn_frame.pack(fill="x")
        
        btn_aceptar = tk.Button(
            btn_frame,
            text="✅ ACCEDER",
            font=("Segoe UI", 11, "bold"),
            bg=COLOR_SUCCESS,
            fg=COLOR_PRIMARY,
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8,
            command=lambda: self.verificar_password(dialog)
        )
        btn_aceptar.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        btn_cancelar = tk.Button(
            btn_frame,
            text="❌ CANCELAR",
            font=("Segoe UI", 11, "bold"),
            bg=COLOR_ACCENT,
            fg=COLOR_TEXT,
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8,
            command=dialog.destroy
        )
        btn_cancelar.pack(side="right", expand=True, fill="x", padx=(5, 0))
        
        # Bind Enter para confirmar
        self.password_entry.bind("<Return>", lambda e: self.verificar_password(dialog))
        
        # Bind Escape para cancelar
        dialog.bind("<Escape>", lambda e: dialog.destroy())
        
        # Guardar referencia al diálogo
        self.password_dialog = dialog
        
        # Esperar a que se cierre el diálogo
        dialog.wait_window()

    def verificar_password(self, dialog):
        """Verifica la contraseña ingresada"""
        password = self.password_entry.get().strip()
        
        if password == CONTRASENA_ACCESO:
            self.acceso_autorizado = True
            dialog.destroy()
            self.mostrar_ventana_principal()
        else:
            messagebox.showerror("Acceso Denegado", "Contraseña incorrecta", parent=dialog)
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()

    def mostrar_ventana_principal(self):
        """Muestra la ventana principal del sistema de asistencia"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            self.window.focus()
            return

        self.window = tk.Toplevel(self.parent)
        self.window.title("Sistema de Asistencia - Control de Registros")
        self.window.configure(bg=COLOR_BG)
        self.window.geometry("1300x700")
        
        # Configurar cierre de ventana
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Centrar la ventana
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (1300 // 2)
        y = (self.window.winfo_screenheight() // 2) - (700 // 2)
        self.window.geometry(f"1300x700+{x}+{y}")

        # Crear UI
        self.create_widgets()
        
        # Cargar datos iniciales
        self.cargar_usuarios()
        self.cargar_todo()
        self.update_stats()

    def on_closing(self):
        """Maneja el cierre de la ventana"""
        if self.window:
            self.window.destroy()
            self.window = None
        # Opcional: resetear el flag para pedir contraseña nuevamente
        # self.acceso_autorizado = False

    def create_widgets(self):
        # Barra de título personalizada
        title_bar = tk.Frame(self.window, bg=COLOR_PRIMARY, height=40)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)
        
        title_label = tk.Label(title_bar, text="📋 SISTEMA DE ASISTENCIA", 
                               font=("Segoe UI", 14, "bold"), 
                               fg=COLOR_TEXT, bg=COLOR_PRIMARY)
        title_label.pack(side="left", padx=20, pady=8)
        
        # Botón de cerrar
        close_btn = tk.Button(title_bar, text="✖", command=self.on_closing,
                              font=("Segoe UI", 12), bg=COLOR_PRIMARY, 
                              fg=COLOR_TEXT, bd=0, cursor="hand2", 
                              activebackground="#1a2f3f", activeforeground="white")
        close_btn.pack(side="right", padx=20, pady=5)
        
        # Frame principal
        main = tk.Frame(self.window, bg=COLOR_BG)
        main.pack(fill="both", expand=True, padx=20, pady=20)

        main.grid_columnconfigure(0, weight=3)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(0, weight=1)

        # Panel izquierdo - Tabla de asistencia
        self.create_left_panel(main)
        
        # Panel derecho - Controles
        self.create_right_panel(main)

    def create_left_panel(self, parent):
        left_frame = tk.Frame(parent, bg=COLOR_SURFACE, relief="raised", bd=1)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Barra de búsqueda en tabla
        search_frame = tk.Frame(left_frame, bg=COLOR_SURFACE)
        search_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(search_frame, text="🔍 Buscar:", font=("Segoe UI", 10),
                bg=COLOR_SURFACE).pack(side="left", padx=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_table())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                                font=("Segoe UI", 10), width=30)
        search_entry.pack(side="left", fill="x", expand=True)
        
        # Treeview con scrollbar
        tree_frame = tk.Frame(left_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.tree = ttk.Treeview(tree_frame, yscrollcommand=scrollbar.set)
        self.tree["columns"] = ("id", "fecha", "hora", "nombre", "tipo", "detalles")
        
        self.tree.column("#0", width=0, stretch=False)
        self.tree.column("id", width=0, stretch=False)
        self.tree.column("fecha", width=120, anchor="center")
        self.tree.column("hora", width=100, anchor="center")
        self.tree.column("nombre", width=200)
        self.tree.column("tipo", width=100, anchor="center")
        self.tree.column("detalles", width=250)

        self.tree.heading("fecha", text="📅 FECHA")
        self.tree.heading("hora", text="⏰ HORA")
        self.tree.heading("nombre", text="👤 NOMBRE COMPLETO")
        self.tree.heading("tipo", text="🚪 TIPO")
        self.tree.heading("detalles", text="📝 DETALLES / HORAS EXTRA")

        self.tree.pack(fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Eventos
        self.tree.bind("<Double-1>", self.cargar_para_editar)
        self.tree.bind("<Delete>", lambda e: self.eliminar())
        
        # Etiqueta de total de registros
        self.total_label = tk.Label(left_frame, text="Total: 0 registros", 
                                   font=("Segoe UI", 9, "italic"),
                                   bg=COLOR_SURFACE, fg="gray")
        self.total_label.pack(pady=(0, 5))

    def create_right_panel(self, parent):
        right_frame = tk.Frame(parent, bg=COLOR_BG)
        right_frame.grid(row=0, column=1, sticky="nsew")
        
        # Estadísticas rápidas
        stats_frame = tk.Frame(right_frame, bg=COLOR_SECONDARY, relief="raised", bd=1)
        stats_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(stats_frame, text="📊 ESTADÍSTICAS HOY", 
                font=("Segoe UI", 10, "bold"), bg=COLOR_SECONDARY).pack(pady=5)
        
        self.stats_text = tk.Label(stats_frame, text="", font=("Segoe UI", 9),
                                   bg=COLOR_SECONDARY, fg=COLOR_PRIMARY)
        self.stats_text.pack(pady=5)
        
        # Filtros
        filter_frame = tk.LabelFrame(right_frame, text="🔎 FILTROS", 
                                     fg=COLOR_TEXT, bg=COLOR_BG,
                                     font=("Segoe UI", 11, "bold"))
        filter_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(filter_frame, text="Usuario:", fg=COLOR_TEXT, bg=COLOR_BG,
                font=("Segoe UI", 10)).pack(anchor="w", padx=10, pady=(10, 0))
        self.user_combo = ttk.Combobox(filter_frame, state="readonly", font=("Segoe UI", 10))
        self.user_combo.pack(fill="x", padx=10, pady=5)
        
        tk.Label(filter_frame, text="Mes:", fg=COLOR_TEXT, bg=COLOR_BG,
                font=("Segoe UI", 10)).pack(anchor="w", padx=10, pady=(5, 0))
        self.mes_combo = ttk.Combobox(filter_frame, state="readonly", font=("Segoe UI", 10))
        self.mes_combo["values"] = list(MESES.keys())
        mes_actual = datetime.now().strftime("%m")
        for k, v in MESES.items():
            if v == mes_actual:
                self.mes_combo.set(k)
                break
        self.mes_combo.pack(fill="x", padx=10, pady=5)
        
        tk.Label(filter_frame, text="Año:", fg=COLOR_TEXT, bg=COLOR_BG,
                font=("Segoe UI", 10)).pack(anchor="w", padx=10, pady=(5, 0))
        self.anio_combo = ttk.Combobox(filter_frame, state="readonly", font=("Segoe UI", 10))
        años = [str(a) for a in range(2020, datetime.now().year + 3)]
        self.anio_combo["values"] = años
        self.anio_combo.set(datetime.now().strftime("%Y"))
        self.anio_combo.pack(fill="x", padx=10, pady=5)
        
        # Botones de filtro
        btn_frame = tk.Frame(filter_frame, bg=COLOR_BG)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(btn_frame, text="🔍 APLICAR FILTRO", bg=COLOR_SUCCESS, 
                 fg="white", font=("Segoe UI", 10, "bold"), cursor="hand2",
                 command=self.filtrar).pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        tk.Button(btn_frame, text="🔄 LIMPIAR", bg="#FFA500", 
                 fg="white", font=("Segoe UI", 10, "bold"), cursor="hand2",
                 command=self.limpiar_filtros).pack(side="left", expand=True, fill="x", padx=(5, 0))
        
        # Botones de acción
        action_frame = tk.LabelFrame(right_frame, text="⚡ ACCIONES", 
                                     fg=COLOR_TEXT, bg=COLOR_BG,
                                     font=("Segoe UI", 11, "bold"))
        action_frame.pack(fill="x", pady=(0, 15))
        
        tk.Button(action_frame, text="➕ AGREGAR REGISTRO", bg=COLOR_PRIMARY, 
                 fg="white", font=("Segoe UI", 10, "bold"), cursor="hand2",
                 command=self.toggle_form).pack(fill="x", padx=10, pady=10)
        
        tk.Button(action_frame, text="🗑 ELIMINAR", bg=COLOR_ACCENT, 
                 fg="white", font=("Segoe UI", 10, "bold"), cursor="hand2",
                 command=self.eliminar).pack(fill="x", padx=10, pady=5)
        
        # Formulario de registro
        self.form_frame = tk.LabelFrame(right_frame, text="📝 FORMULARIO", 
                                        fg=COLOR_TEXT, bg=COLOR_BG,
                                        font=("Segoe UI", 11, "bold"))
        self.form_visible = False
        
        # Campos del formulario
        fields_frame = tk.Frame(self.form_frame, bg=COLOR_BG)
        fields_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tk.Label(fields_frame, text="PIN del Usuario:", fg=COLOR_TEXT, bg=COLOR_BG,
                font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 2))
        self.pin_entry = tk.Entry(fields_frame, font=("Segoe UI", 10), show="•")
        self.pin_entry.pack(fill="x", pady=(0, 10))
        
        tk.Label(fields_frame, text="Fecha (YYYY-MM-DD):", fg=COLOR_TEXT, bg=COLOR_BG,
                font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 2))
        self.fecha_entry = tk.Entry(fields_frame, font=("Segoe UI", 10))
        self.fecha_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.fecha_entry.pack(fill="x", pady=(0, 10))
        
        tk.Label(fields_frame, text="Hora (HH:MM:SS):", fg=COLOR_TEXT, bg=COLOR_BG,
                font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 2))
        self.hora_entry = tk.Entry(fields_frame, font=("Segoe UI", 10))
        self.hora_entry.insert(0, datetime.now().strftime("%H:%M:%S"))
        self.hora_entry.pack(fill="x", pady=(0, 10))
        
        tk.Label(fields_frame, text="Tipo:", fg=COLOR_TEXT, bg=COLOR_BG,
                font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 2))
        self.tipo_combo = ttk.Combobox(fields_frame, state="readonly", font=("Segoe UI", 10))
        self.tipo_combo["values"] = ["INGRESO", "SALIDA"]
        self.tipo_combo.set("INGRESO")
        self.tipo_combo.pack(fill="x", pady=(0, 10))
        
        # Campo de texto para detalles/horas extra
        tk.Label(fields_frame, text="Detalles / Horas Extra:", fg=COLOR_TEXT, bg=COLOR_BG,
                font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 2))
        
        # Frame para el text area con scrollbar
        text_frame = tk.Frame(fields_frame, bg=COLOR_BG)
        text_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.detalles_text = tk.Text(text_frame, font=("Segoe UI", 10), height=4, width=30)
        self.detalles_text.pack(side="left", fill="both", expand=True)
        
        text_scrollbar = tk.Scrollbar(text_frame, command=self.detalles_text.yview)
        text_scrollbar.pack(side="right", fill="y")
        self.detalles_text.config(yscrollcommand=text_scrollbar.set)
        
        # Botones del formulario
        form_btn_frame = tk.Frame(fields_frame, bg=COLOR_BG)
        form_btn_frame.pack(fill="x", pady=(0, 5))
        
        tk.Button(form_btn_frame, text="💾 GUARDAR", bg=COLOR_SUCCESS, 
                 fg="white", font=("Segoe UI", 10, "bold"), cursor="hand2",
                 command=self.guardar).pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        tk.Button(form_btn_frame, text="❌ CANCELAR", bg="#999999", 
                 fg="white", font=("Segoe UI", 10, "bold"), cursor="hand2",
                 command=self.cancelar_edicion).pack(side="left", expand=True, fill="x", padx=(5, 0))

    def filter_table(self):
        """Filtra la tabla en tiempo real según texto de búsqueda"""
        search_text = self.search_var.get().lower()
        if not search_text:
            self.cargar_todo()
            return
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        conn = sqlite3.connect("personas.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT a.id, a.fecha, a.hora, p.Nombre_Completo, a.tipo, IFNULL(a.detalles, '')
                FROM asistencias a
                JOIN personas p ON p.id = a.persona_id
                WHERE LOWER(p.Nombre_Completo) LIKE ? 
                   OR LOWER(a.tipo) LIKE ?
                   OR LOWER(IFNULL(a.detalles, '')) LIKE ?
                ORDER BY a.fecha DESC, a.hora DESC
            """, (f'%{search_text}%', f'%{search_text}%', f'%{search_text}%'))
            
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
        except sqlite3.OperationalError:
            cursor.execute("""
                SELECT a.id, a.fecha, a.hora, p.Nombre_Completo, a.tipo, '' as detalles
                FROM asistencias a
                JOIN personas p ON p.id = a.persona_id
                WHERE LOWER(p.Nombre_Completo) LIKE ? OR LOWER(a.tipo) LIKE ?
                ORDER BY a.fecha DESC, a.hora DESC
            """, (f'%{search_text}%', f'%{search_text}%'))
            
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
        
        conn.close()
        self.update_total_label()

    def update_stats(self):
        """Actualiza estadísticas del día actual"""
        hoy = datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect("personas.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*), 
                   SUM(CASE WHEN tipo='INGRESO' THEN 1 ELSE 0 END),
                   SUM(CASE WHEN tipo='SALIDA' THEN 1 ELSE 0 END)
            FROM asistencias WHERE fecha=?
        """, (hoy,))
        
        total, ingresos, salidas = cursor.fetchone()
        ingresos = ingresos or 0
        salidas = salidas or 0
        
        stats_text = f"Total: {total} | 🚪 Ingresos: {ingresos} | 🚶 Salidas: {salidas}"
        self.stats_text.config(text=stats_text)
        
        conn.close()

    def update_total_label(self):
        """Actualiza el contador de registros visibles"""
        total = len(self.tree.get_children())
        self.total_label.config(text=f"Total: {total} registros")

    def cargar_usuarios(self):
        conn = sqlite3.connect("personas.db")
        cursor = conn.cursor()
        cursor.execute("SELECT Nombre_Completo FROM personas ORDER BY Nombre_Completo")
        usuarios = [r[0] for r in cursor.fetchall()]
        self.user_combo["values"] = usuarios
        if usuarios:
            self.user_combo.set(usuarios[0])
        conn.close()

    def cargar_todo(self):
        self.tree.delete(*self.tree.get_children())

        conn = sqlite3.connect("personas.db")
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT a.id, a.fecha, a.hora, p.Nombre_Completo, a.tipo, IFNULL(a.detalles, '')
                FROM asistencias a
                JOIN personas p ON p.id = a.persona_id
                ORDER BY a.fecha DESC, a.hora DESC
            """)
        except sqlite3.OperationalError:
            cursor.execute("""
                SELECT a.id, a.fecha, a.hora, p.Nombre_Completo, a.tipo, '' as detalles
                FROM asistencias a
                JOIN personas p ON p.id = a.persona_id
                ORDER BY a.fecha DESC, a.hora DESC
            """)

        for row in cursor.fetchall():
            valores = list(row)
            if len(valores) < 6 or valores[5] is None:
                valores.append("")
            self.tree.insert("", "end", values=valores[:6])

        conn.close()
        self.update_total_label()
        self.update_stats()

    def filtrar(self):
        if not self.user_combo.get():
            messagebox.showwarning("Advertencia", "Seleccione un usuario")
            return
            
        user = self.user_combo.get()
        mes = MESES.get(self.mes_combo.get())
        anio = self.anio_combo.get()

        self.tree.delete(*self.tree.get_children())

        conn = sqlite3.connect("personas.db")
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT a.id, a.fecha, a.hora, p.Nombre_Completo, a.tipo, IFNULL(a.detalles, '')
                FROM asistencias a
                JOIN personas p ON p.id = a.persona_id
                WHERE p.Nombre_Completo = ?
                AND strftime('%m', a.fecha) = ?
                AND strftime('%Y', a.fecha) = ?
                ORDER BY a.fecha DESC, a.hora DESC
            """, (user, mes, anio))
        except sqlite3.OperationalError:
            cursor.execute("""
                SELECT a.id, a.fecha, a.hora, p.Nombre_Completo, a.tipo, '' as detalles
                FROM asistencias a
                JOIN personas p ON p.id = a.persona_id
                WHERE p.Nombre_Completo = ?
                AND strftime('%m', a.fecha) = ?
                AND strftime('%Y', a.fecha) = ?
                ORDER BY a.fecha DESC, a.hora DESC
            """, (user, mes, anio))

        results = cursor.fetchall()
        for row in results:
            valores = list(row)
            if len(valores) < 6 or valores[5] is None:
                valores.append("")
            self.tree.insert("", "end", values=valores[:6])

        conn.close()
        self.update_total_label()
        
        if not results:
            messagebox.showinfo("Información", "No se encontraron registros con esos filtros")

    def limpiar_filtros(self):
        """Limpia todos los filtros y muestra todos los registros"""
        if self.user_combo["values"]:
            self.user_combo.set(self.user_combo["values"][0])
        self.mes_combo.set("Enero")
        self.anio_combo.set(datetime.now().strftime("%Y"))
        self.search_var.set("")
        self.cargar_todo()
        messagebox.showinfo("Información", "Filtros limpiados")

    def toggle_form(self):
        if self.form_visible:
            self.form_frame.pack_forget()
        else:
            self.form_frame.pack(fill="both", expand=True, pady=(0, 15))
            self.pin_entry.focus()
        self.form_visible = not self.form_visible
        if not self.form_visible:
            self.cancelar_edicion()

    def guardar(self):
        pin = self.pin_entry.get().strip()
        fecha = self.fecha_entry.get().strip()
        hora = self.hora_entry.get().strip()
        tipo = self.tipo_combo.get()
        detalles = self.detalles_text.get("1.0", tk.END).strip()

        if not pin:
            messagebox.showerror("Error", "Ingrese el PIN del usuario")
            return
        
        if not fecha:
            messagebox.showerror("Error", "Ingrese la fecha")
            return
        
        if not hora:
            messagebox.showerror("Error", "Ingrese la hora")
            return

        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD")
            return

        try:
            datetime.strptime(hora, "%H:%M:%S")
        except ValueError:
            messagebox.showerror("Error", "Formato de hora inválido. Use HH:MM:SS")
            return

        conn = sqlite3.connect("personas.db")
        cursor = conn.cursor()

        try:
            cursor.execute("ALTER TABLE asistencias ADD COLUMN detalles TEXT")
            conn.commit()
        except sqlite3.OperationalError:
            pass

        cursor.execute("SELECT id, Nombre_Completo FROM personas WHERE Pin=?", (pin,))
        result = cursor.fetchone()

        if not result:
            messagebox.showerror("Error", "PIN no encontrado")
            conn.close()
            return

        persona_id, nombre = result

        if self.selected_id:
            cursor.execute("""
                UPDATE asistencias
                SET fecha=?, hora=?, tipo=?, detalles=?
                WHERE id=?
            """, (fecha, hora, tipo, detalles, self.selected_id))
            messagebox.showinfo("Éxito", f"Registro de {nombre} actualizado correctamente")
            self.selected_id = None
        else:
            cursor.execute("""
                INSERT INTO asistencias (persona_id, fecha, hora, tipo, detalles)
                VALUES (?, ?, ?, ?, ?)
            """, (persona_id, fecha, hora, tipo, detalles))
            messagebox.showinfo("Éxito", f"Registro de {nombre} guardado correctamente")

        conn.commit()
        conn.close()

        self.cargar_todo()
        
        if self.form_visible:
            self.cancelar_edicion()

    def cargar_para_editar(self, event):
        item = self.tree.selection()
        if not item:
            return

        values = self.tree.item(item, "values")
        if not values:
            return

        self.selected_id = values[0]
        self.fecha_entry.delete(0, tk.END)
        self.fecha_entry.insert(0, values[1])

        self.hora_entry.delete(0, tk.END)
        self.hora_entry.insert(0, values[2])

        self.tipo_combo.set(values[4])
        
        self.detalles_text.delete("1.0", tk.END)
        if len(values) > 5 and values[5]:
            self.detalles_text.insert("1.0", values[5])

        if not self.form_visible:
            self.toggle_form()
        
        self.pin_entry.delete(0, tk.END)
        self.pin_entry.focus()

    def cancelar_edicion(self):
        """Cancela la edición y limpia el formulario"""
        self.selected_id = None
        self.pin_entry.delete(0, tk.END)
        self.fecha_entry.delete(0, tk.END)
        self.fecha_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.hora_entry.delete(0, tk.END)
        self.hora_entry.insert(0, datetime.now().strftime("%H:%M:%S"))
        self.tipo_combo.set("INGRESO")
        self.detalles_text.delete("1.0", tk.END)

    def eliminar(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Aviso", "Seleccione un registro para eliminar")
            return

        values = self.tree.item(item, "values")
        if not values:
            return
            
        record_id = values[0]
        nombre = values[3]
        fecha = values[1]
        hora = values[2]

        confirm = messagebox.askyesno("Confirmar Eliminación", 
                                     f"¿Eliminar registro de {nombre}?\nFecha: {fecha} {hora}\n\nEsta acción no se puede deshacer.")
        if not confirm:
            return

        conn = sqlite3.connect("personas.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM asistencias WHERE id=?", (record_id,))
        conn.commit()
        conn.close()

        self.cargar_todo()
        messagebox.showinfo("Éxito", "Registro eliminado correctamente")