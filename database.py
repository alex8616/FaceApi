import sqlite3
def init_db():
    conn = sqlite3.connect("personas.db")
    cursor = conn.cursor()

    # PERSONAS (ya la tienes)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS personas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Nombre_Completo TEXT,
        Dni TEXT,
        Cargo TEXT,
        Tiempo TEXT,
        estado TEXT,
        Pin TEXT,
        imagen TEXT,
        descriptores BLOB,
        created_at TEXT,
        updated_at TEXT
    )
    """)

    # 🔥 NUEVA TABLA ASISTENCIAS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS asistencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        persona_id INTEGER,
        nombre TEXT,
        tipo TEXT, -- INGRESO / SALIDA
        fecha TEXT,
        hora TEXT,
        datetime TEXT
    )
    """)

    conn.commit()
    conn.close()