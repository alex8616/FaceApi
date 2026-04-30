import sqlite3
from datetime import datetime

DB_NAME = "personas.db"


def registrar_asistencia(nombre, tipo):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM personas WHERE Nombre_Completo = ?", (nombre,))
    persona = cursor.fetchone()

    if not persona:
        conn.close()
        return False, "Persona no encontrada"

    persona_id = persona[0]

    cursor.execute("""
        SELECT tipo FROM asistencias
        WHERE persona_id = ?
        ORDER BY datetime DESC LIMIT 1
    """, (persona_id,))

    ultimo = cursor.fetchone()

    # 🔴 REGLAS
    if tipo == "INGRESO" and ultimo and ultimo[0] == "INGRESO":
        conn.close()
        return False, "⚠️ Ya tiene un ingreso activo"

    if tipo == "SALIDA" and (not ultimo or ultimo[0] == "SALIDA"):
        conn.close()
        return False, "⚠️ No puede registrar salida sin ingreso previo"

    now = datetime.now()
    fecha = now.strftime("%Y-%m-%d")
    hora = now.strftime("%H:%M:%S")
    dt = now.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO asistencias (persona_id, nombre, tipo, fecha, hora, datetime)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (persona_id, nombre, tipo, fecha, hora, dt))

    conn.commit()
    conn.close()

    return True, f"✔ {nombre} registró {tipo}"