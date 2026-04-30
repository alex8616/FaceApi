import tkinter as tk
from tkinter import ttk
import sqlite3
from utils import calcular_horas

DB = "personas.db"


# =========================
# 📦 CARGAR DATOS
# =========================
def cargar_asistencias(nombre=None, fecha=None):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    query = "SELECT nombre, tipo, fecha, hora FROM asistencias WHERE 1=1"
    params = []

    if nombre:
        query += " AND nombre LIKE ?"
        params.append(f"%{nombre}%")

    if fecha:
        query += " AND fecha = ?"
        params.append(fecha)

    query += " ORDER BY datetime DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    conn.close()
    return rows


# =========================
# 🔄 ACTUALIZAR TABLA
# =========================
def actualizar():
    for row in tree.get_children():
        tree.delete(row)

    nombre = entry_nombre.get()
    fecha = entry_fecha.get()

    data = cargar_asistencias(nombre, fecha)

    for r in data:
        tree.insert("", "end", values=r)

    # 🔥 calcular horas si hay filtro por persona + fecha
    if nombre and fecha:
        h, m = calcular_horas(nombre, fecha)
        lbl_horas.config(text=f"⏱ Horas trabajadas: {h}h {m}m")
    else:
        lbl_horas.config(text="⏱ Horas trabajadas: --")


# =========================
# 🖥️ UI
# =========================
root = tk.Tk()
root.title("📊 Panel de Asistencias")
root.geometry("800x500")


# =========================
# 🔎 FILTROS
# =========================
frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Nombre:").grid(row=0, column=0)
entry_nombre = tk.Entry(frame, width=25)
entry_nombre.grid(row=0, column=1)

tk.Label(frame, text="Fecha (YYYY-MM-DD):").grid(row=0, column=2)
entry_fecha = tk.Entry(frame, width=15)
entry_fecha.grid(row=0, column=3)

tk.Button(frame, text="🔍 Buscar", command=actualizar).grid(row=0, column=4, padx=10)


# =========================
# 📊 TABLA
# =========================
columns = ("Nombre", "Tipo", "Fecha", "Hora")

tree = ttk.Treeview(root, columns=columns, show="headings")
tree.pack(fill="both", expand=True)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150)


# =========================
# ⏱ HORAS
# =========================
lbl_horas = tk.Label(root, text="⏱ Horas trabajadas: --", font=("Arial", 14))
lbl_horas.pack(pady=10)


# =========================
# 🔄 BOTÓN REFRESH
# =========================
tk.Button(root, text="🔄 Actualizar", command=actualizar).pack()


# carga inicial
actualizar()

root.mainloop()