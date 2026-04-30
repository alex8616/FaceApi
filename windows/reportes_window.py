import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from collections import defaultdict
from windows.pdf_reportes import PDFReportes
from windows.planillas_window import generar_planilla_pdf  # Importar la función

# Colores
COLOR_BG = "#003049"
COLOR_SURFACE = "#FFFFFF"
COLOR_PRIMARY = "#003049"
COLOR_DANGER = "#FF5555"
COLOR_TEXT = "#FFFFFF"


class ReportesWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = None

        self.meses = [
            ("Enero", "01"), ("Febrero", "02"), ("Marzo", "03"),
            ("Abril", "04"), ("Mayo", "05"), ("Junio", "06"),
            ("Julio", "07"), ("Agosto", "08"), ("Septiembre", "09"),
            ("Octubre", "10"), ("Noviembre", "11"), ("Diciembre", "12")
        ]

    def show(self):
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = tk.Toplevel(self.parent)
        self.window.title("Reportes de Asistencia")
        self.window.configure(bg=COLOR_BG)
        self.window.geometry("1000x600")

        main = tk.Frame(self.window, bg=COLOR_BG, padx=20, pady=20)
        main.pack(fill="both", expand=True)

        tk.Label(
            main,
            text="📊 REPORTES DE ASISTENCIA",
            font=("Segoe UI", 18, "bold"),
            fg=COLOR_TEXT,
            bg=COLOR_BG
        ).pack(pady=(0, 15))

        # ================= TABLA =================
        table_frame = tk.Frame(main, bg=COLOR_SURFACE)
        table_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(table_frame)
        self.tree["columns"] = ("fecha", "nombre", "hora", "tipo")

        self.tree.column("fecha", width=120, anchor="center")
        self.tree.column("nombre", width=250)
        self.tree.column("hora", width=100, anchor="center")
        self.tree.column("tipo", width=100, anchor="center")

        self.tree.heading("fecha", text="FECHA")
        self.tree.heading("nombre", text="NOMBRE")
        self.tree.heading("hora", text="HORA")
        self.tree.heading("tipo", text="TIPO")

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # ================= FILTROS =================
        filter_frame = tk.Frame(main, bg=COLOR_BG)
        filter_frame.pack(fill="x", pady=10)

        self.tipo_var = tk.StringVar(value="DIARIO")

        self.tipo_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.tipo_var,
            values=["DIARIO", "MENSUAL"],
            width=12,
            state="readonly"
        )
        self.tipo_combo.grid(row=0, column=0, padx=5)

        self.day_var = tk.StringVar(value=str(datetime.now().day))
        self.day_spin = tk.Spinbox(filter_frame, from_=1, to=31, width=4, textvariable=self.day_var)
        self.day_spin.grid(row=0, column=1, padx=5)

        self.mes_var = tk.StringVar()
        self.mes_combo = ttk.Combobox(
            filter_frame,
            values=[m[0] for m in self.meses],
            width=12,
            state="readonly",
            textvariable=self.mes_var
        )
        self.mes_combo.current(datetime.now().month - 1)
        self.mes_combo.grid(row=0, column=2, padx=5)

        self.year_var = tk.StringVar(value=str(datetime.now().year))
        self.year_spin = tk.Spinbox(filter_frame, from_=2020, to=2100, width=6, textvariable=self.year_var)
        self.year_spin.grid(row=0, column=3, padx=5)

        # BOTÓN BUSCAR
        tk.Button(
            filter_frame,
            text="🔍 BUSCAR",
            bg=COLOR_PRIMARY,
            fg=COLOR_TEXT,
            command=self.cargar_reportes
        ).grid(row=0, column=4, padx=5)

        # BOTÓN EXPORTAR PDF (OCULTO INICIALMENTE)
        self.btn_pdf = tk.Button(
            filter_frame,
            text="📄 EXPORTAR PDF",
            bg="#1f7a1f",
            fg="white",
            command=self.exportar_pdf
        )
        self.btn_pdf.grid(row=0, column=5, padx=5)
        self.btn_pdf.grid_remove()  # oculto

        # BOTÓN PLANILLAS (OCULTO INICIALMENTE)
        self.btn_planillas = tk.Button(
            filter_frame,
            text="📋 PLANILLAS",
            bg="#D62828",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self.generar_planilla
        )
        self.btn_planillas.grid(row=0, column=6, padx=5)
        self.btn_planillas.grid_remove()

        self.tipo_var.trace("w", lambda *args: self.actualizar_ui())

        self.actualizar_ui()
        self.cargar_reportes()

    # ================= UI DINÁMICA =================
    def actualizar_ui(self):
        if self.tipo_var.get() == "DIARIO":
            self.day_spin.grid()
            self.btn_pdf.grid_remove()
            self.btn_planillas.grid_remove()
        else:
            self.day_spin.grid_remove()
            self.btn_pdf.grid()
            self.btn_planillas.grid()

    # ================= DATOS =================
    def obtener_datos(self):
        conn = sqlite3.connect("personas.db")
        cursor = conn.cursor()

        tipo = self.tipo_var.get()
        mes = next(m[1] for m in self.meses if m[0] == self.mes_var.get())

        query = """
            SELECT a.id, a.fecha, p.Nombre_Completo, a.hora, a.tipo
            FROM asistencias a
            JOIN personas p ON p.id = a.persona_id
        """

        params = []

        if tipo == "DIARIO":
            fecha = f"{self.year_var.get()}-{mes}-{int(self.day_var.get()):02d}"
            query += " WHERE DATE(a.fecha) = ?"
            params.append(fecha)
        else:
            query += " WHERE strftime('%Y-%m', a.fecha) = ?"
            params.append(f"{self.year_var.get()}-{mes}")

        query += " ORDER BY a.fecha ASC, a.hora ASC"

        cursor.execute(query, params)
        data = cursor.fetchall()
        conn.close()

        return data

    # ================= CARGAR TABLA =================
    def cargar_reportes(self):
        self.tree.delete(*self.tree.get_children())

        for row in self.obtener_datos():
            self.tree.insert("", "end", values=row[1:])

    # ================= EXPORTAR PDF =================
    def exportar_pdf(self):
        from windows.pdf_reportes import PDFReportes
        from tkinter import messagebox, filedialog

        try:
            mes = self.mes_var.get()
            anio = self.year_var.get()

            # Nombre sugerido
            file_name = f"ReporteAsistencia_{mes}_{anio}.pdf"

            # 🔥 Abrir diálogo para elegir dónde guardar
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("Archivo PDF", "*.pdf")],
                title="Guardar reporte de asistencia",
                initialfile=file_name
            )

            # Si el usuario cancela
            if not file_path:
                return

            pdf = PDFReportes()
            pdf.generar_pdf(
                file_path=file_path,
                mes=mes,
                anio=anio
            )

            messagebox.showinfo("Éxito", f"PDF generado:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ================= GENERAR PLANILLA =================
    def generar_planilla(self):
        """Genera directamente el PDF de planilla sin abrir ventana"""
        try:
            mes = self.mes_var.get()
            anio = self.year_var.get()
            
            # Preguntar dónde guardar el PDF
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf")],
                title=f"Guardar planilla - {mes} {anio}",
                initialfile=f"planilla_{mes}_{anio}.pdf"
            )
            
            if not file_path:
                return
            
            # Generar el PDF de planilla
            generar_planilla_pdf(file_path, mes, anio)
            
            messagebox.showinfo("Éxito", f"Planilla generada correctamente:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar planilla: {str(e)}")