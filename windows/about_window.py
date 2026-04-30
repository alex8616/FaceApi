import tkinter as tk

# Colores
COLOR_BG = "#003049"
COLOR_TEXT = "#FFFFFF"
COLOR_SUCCESS = "#A1DD70"
COLOR_SURFACE = "#FFFFFF"

class AboutWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = None
        
    def show(self):
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
            
        self.window = tk.Toplevel(self.parent)
        self.window.title("Acerca de - Registro Biométrico")
        self.window.configure(bg=COLOR_BG)
        self.window.transient(self.parent)
        self.window.grab_set()
        
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        width = int(screen_width * 0.35)
        height = int(screen_height * 0.45)
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        self.window.minsize(400, 420)
        
        main = tk.Frame(self.window, bg=COLOR_BG, padx=30, pady=30)
        main.pack(fill="both", expand=True)
        
        tk.Label(
            main,
            text="👤 REGISTRO BIOMÉTRICO",
            font=("Segoe UI", 20, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_BG
        ).pack(pady=(0, 15))
        
        tk.Label(
            main,
            text="Versión 2.0",
            font=("Segoe UI", 13),
            fg=COLOR_SUCCESS,
            bg=COLOR_BG
        ).pack()
        
        tk.Label(
            main,
            text="Sistema de Control de Acceso Biométrico",
            font=("Segoe UI", 12),
            fg=COLOR_TEXT,
            bg=COLOR_BG
        ).pack(pady=(10, 20))
        
        tk.Frame(main, height=2, bg=COLOR_SURFACE).pack(fill="x", pady=10)
        
        tk.Label(
            main,
            text="Desarrollado con:",
            font=("Segoe UI", 12, "bold"),
            fg=COLOR_SUCCESS,
            bg=COLOR_BG
        ).pack()
        
        tk.Label(
            main,
            text="• Python 3.x + Tkinter\n• OpenCV + Face Recognition\n• SQLite Database",
            font=("Segoe UI", 11),
            fg=COLOR_TEXT,
            bg=COLOR_BG,
            justify="left"
        ).pack(pady=(10, 15))
        
        tk.Label(
            main,
            text="👨‍💻 Desarrollador: Alejandro Ventura Fuentes",
            font=("Segoe UI", 11, "bold"),
            fg=COLOR_SUCCESS,
            bg=COLOR_BG
        ).pack(pady=(5, 5))
        
        tk.Label(
            main,
            text="© 2024 - Todos los derechos reservados",
            font=("Segoe UI", 9),
            fg=COLOR_TEXT,
            bg=COLOR_BG
        ).pack(pady=(10, 0))
        
        tk.Button(
            main,
            text="CERRAR",
            font=("Segoe UI", 12, "bold"),
            bg=COLOR_SUCCESS,
            fg="#003049",
            height=2,
            command=self.window.destroy
        ).pack(fill="x", pady=(20, 0))