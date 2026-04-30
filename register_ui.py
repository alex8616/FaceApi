import tkinter as tk
from tkinter import messagebox
import cv2
import base64
import pickle
from datetime import datetime
import sqlite3

from face_engine import FaceEngine
from database import init_db

init_db()
engine = FaceEngine()

def guardar():
    nombre = entry_nombre.get()
    dni = entry_dni.get()
    cargo = entry_cargo.get()
    tiempo = var_tiempo.get()
    pin = entry_pin.get()

    cap = cv2.VideoCapture(2, cv2.CAP_DSHOW)

    embeddings = []
    count = 0

    print("📸 Capturando rostro (mueve la cara)...")

    while count < 15:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.resize(frame, (640, 480))

        emb = engine.get_embedding(frame)

        if emb is not None:
            embeddings.append(emb)
            count += 1
            print(f"✅ {count}/15")

        cv2.putText(frame, f"Captura {count}/15", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        cv2.imshow("Registro", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if len(embeddings) == 0:
        messagebox.showerror("Error", "No se detectó rostro")
        return

    _, buffer = cv2.imencode('.jpg', frame)
    img_base64 = base64.b64encode(buffer).decode('utf-8')

    emb_blob = pickle.dumps(embeddings)

    conn = sqlite3.connect("personas.db")
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO personas (
        Nombre_Completo, Dni, Cargo, Tiempo,
        estado, Pin, imagen, descriptores,
        created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        nombre, dni, cargo, tiempo,
        "true", pin, img_base64, emb_blob,
        now, now
    ))

    conn.commit()
    conn.close()

    messagebox.showinfo("OK", "Usuario registrado correctamente")

# UI
root = tk.Tk()
root.title("Registro Biométrico")
root.geometry("400x400")

tk.Label(root, text="Nombre").pack()
entry_nombre = tk.Entry(root)
entry_nombre.pack()

tk.Label(root, text="DNI").pack()
entry_dni = tk.Entry(root)
entry_dni.pack()

tk.Label(root, text="Cargo").pack()
entry_cargo = tk.Entry(root)
entry_cargo.pack()

tk.Label(root, text="Tiempo").pack()
var_tiempo = tk.StringVar(value="MEDIO")
tk.OptionMenu(root, var_tiempo, "COMPLETO", "MEDIO").pack()

tk.Label(root, text="PIN").pack()
entry_pin = tk.Entry(root, show="*")
entry_pin.pack()

tk.Button(root, text="Registrar", command=guardar).pack(pady=20)

root.mainloop()