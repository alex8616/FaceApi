import tkinter as tk
from tkinter import ttk
import sqlite3
import base64
import cv2
import numpy as np
from PIL import Image, ImageTk
import io

# =========================
# 📦 CARGAR USUARIOS
# =========================
def cargar_usuarios():
    conn = sqlite3.connect("personas.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, Nombre_Completo, Dni, Cargo, Tiempo, imagen
        FROM personas
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


# =========================
# 🖼️ MOSTRAR IMAGEN
# =========================
def mostrar_imagen(event):
    selected = tree.focus()

    if not selected:
        return

    data = tree.item(selected)["values"]

    if len(data) < 6:
        return

    img_base64 = data[5]

    if not img_base64:
        return

    try:
        img_bytes = base64.b64decode(img_base64)
        img_np = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

        img = cv2.resize(img, (200, 200))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        img_pil = Image.fromarray(img)
        img_tk = ImageTk.PhotoImage(img_pil)

        label_img.config(image=img_tk)
        label_img.image = img_tk

    except Exception as e:
        print("Error imagen:", e)


# =========================
# 🗑️ ELIMINAR USUARIO
# =========================
def eliminar_usuario():
    selected = tree.focus()

    if not selected:
        return

    data = tree.item(selected)["values"]
    user_id = data[0]

    conn = sqlite3.connect("personas.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM personas WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    cargar_tabla()


# =========================
# 🔄 RECARGAR TABLA
# =========================
def cargar_tabla():
    for row in tree.get_children():
        tree.delete(row)

    usuarios = cargar_usuarios()

    for u in usuarios:
        tree.insert("", tk.END, values=u)


# =========================
# 🎨 UI
# =========================
root = tk.Tk()
root.title("Panel de Usuarios Biométrico")
root.geometry("800x500")

# TABLA
columns = ("ID", "Nombre", "DNI", "Cargo", "Tiempo", "Imagen")

tree = ttk.Treeview(root, columns=columns, show="headings")

for col in columns[:-1]:
    tree.heading(col, text=col)
    tree.column(col, anchor="center")

tree.heading("Imagen", text="Imagen (oculta)")
tree.column("Imagen", width=0, stretch=False)

tree.pack(fill=tk.BOTH, expand=True)

tree.bind("<<TreeviewSelect>>", mostrar_imagen)

# IMAGEN
label_img = tk.Label(root)
label_img.pack(pady=10)

# BOTONES
frame_btn = tk.Frame(root)
frame_btn.pack()

tk.Button(frame_btn, text="🔄 Recargar", command=cargar_tabla).pack(side=tk.LEFT, padx=10)
tk.Button(frame_btn, text="🗑️ Eliminar", command=eliminar_usuario).pack(side=tk.LEFT, padx=10)

# CARGAR DATOS
cargar_tabla()

root.mainloop()