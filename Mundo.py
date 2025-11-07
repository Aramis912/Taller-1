import sqlite3

# Nombre del archivo de la base de datos
DB_NAME = 'mundo_aventuras.db'

def crear_conexion():
    """Crea y devuelve una conexión a la base de datos."""
    try:
        conn = sqlite3.connect(DB_NAME)
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def crear_tablas(conn):
    """Crea las tablas Misiones, Heroes, Monstruos, Participacion y Encuentros."""
    cursor = conn.cursor()
    
    # Comandos SQL para crear las tablas
    sql_commands = [
        """
        -- Tabla MISIONES
        CREATE TABLE IF NOT EXISTS Misiones (
            id_mision INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            recompensa_oro INTEGER DEFAULT 0,
            nivel_dificultad TEXT CHECK (nivel_dificultad IN ('Fácil', 'Medio', 'Difícil', 'Épico')) NOT NULL,
            fecha_inicio DATE,
            estado TEXT CHECK (estado IN ('Pendiente', 'En Progreso', 'Completada', 'Fallida')) NOT NULL DEFAULT 'Pendiente'
        );
        """,
        """
        -- Tabla HEROES
        CREATE TABLE IF NOT EXISTS Heroes (
            id_heroe INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            clase TEXT,
            nivel INTEGER DEFAULT 1 CHECK (nivel >= 1),
            raza TEXT
        );
        """,
        """
        -- Tabla MONSTRUOS
        CREATE TABLE IF NOT EXISTS Monstruos (
            id_monstruo INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            tipo TEXT,
            puntos_salud INTEGER,
            peligrosidad TEXT CHECK (peligrosidad IN ('Baja', 'Media', 'Alta', 'Jefe'))
        );
        """,
        """
        -- Tabla de Relación: PARTICIPACION (Héroes en Misiones)
        CREATE TABLE IF NOT EXISTS Participacion (
            id_mision INTEGER,
            id_heroe INTEGER,
            rol_en_mision TEXT,
            estado_heroe TEXT CHECK (estado_heroe IN ('Activo', 'Herido', 'Caído')),
            
            PRIMARY KEY (id_mision, id_heroe),
            FOREIGN KEY (id_mision) REFERENCES Misiones(id_mision) ON DELETE CASCADE,
            FOREIGN KEY (id_heroe) REFERENCES Heroes(id_heroe) ON DELETE CASCADE
        );
        """,
        """
        -- Tabla de Relación: ENCUENTROS (Monstruos en Misiones)
        CREATE TABLE IF NOT EXISTS Encuentros (
            id_mision INTEGER,
            id_monstruo INTEGER,
            cantidad INTEGER DEFAULT 1 CHECK (cantidad >= 1),
            
            PRIMARY KEY (id_mision, id_monstruo),
            FOREIGN KEY (id_mision) REFERENCES Misiones(id_mision) ON DELETE CASCADE,
            FOREIGN KEY (id_monstruo) REFERENCES Monstruos(id_monstruo) ON DELETE CASCADE
        );
        """
    ]
    
    for command in sql_commands:
        cursor.execute(command)
    
    conn.commit()
    print("✅ Tablas creadas exitosamente.")

def insertar_datos_ejemplo(conn):
    """Inserta datos de prueba en todas las tablas."""
    cursor = conn.cursor()

    try:
        # Limpiar datos existentes para evitar duplicados en la ejecución de prueba
        cursor.execute("DELETE FROM Participacion;")
        cursor.execute("DELETE FROM Encuentros;")
        cursor.execute("DELETE FROM Misiones;")
        cursor.execute("DELETE FROM Heroes;")
        cursor.execute("DELETE FROM Monstruos;")
        conn.commit()
        print("Datos anteriores limpiados (si existían).")

        # 1. Héroes
        heroes = [
            (1, 'Aura', 'Paladín', 10, 'Humano'),
            (2, 'Gimli', 'Guerrero', 8, 'Enano'),
            (3, 'Lyra', 'Maga', 9, 'Elfo')
        ]
        cursor.executemany("INSERT INTO Heroes VALUES (?, ?, ?, ?, ?)", heroes)

        # 2. Monstruos
        monstruos = [
            (101, 'Gran Trasgo', 'Goblin', 50, 'Media'),
            (102, 'Sombra Alada', 'Espectral', 80, 'Alta'),
            (103, 'Rey Esqueleto', 'No-muerto', 300, 'Jefe')
        ]
        cursor.executemany("INSERT INTO Monstruos VALUES (?, ?, ?, ?, ?)", monstruos)

        # 3. Misiones
        misiones = [
            (501, 'Rescate del Amuleto', 'Recuperar un amuleto robado por goblins.', 500, 'Fácil', '2025-11-01', 'Completada'),
            (502, 'Cacería del Dragón', 'Exterminar un dragón en las montañas.', 5000, 'Épico', '2025-11-05', 'En Progreso')
        ]
        cursor.executemany("INSERT INTO Misiones VALUES (?, ?, ?, ?, ?, ?, ?)", misiones)

        # 4. Participación (Aura y Gimli en Rescate)
        participacion = [
            (501, 1, 'Líder', 'Activo'),  # Aura en Misión 501
            (501, 2, 'Defensa', 'Activo'), # Gimli en Misión 501
            (502, 1, 'Líder', 'Activo'),  # Aura en Misión 502
            (502, 3, 'Apoyo Mágico', 'Activo') # Lyra en Misión 502
        ]
        cursor.executemany("INSERT INTO Participacion VALUES (?, ?, ?, ?)", participacion)

        # 5. Encuentros (Monstruos en Misiones)
        encuentros = [
            (501, 101, 5),  # 5 Gran Trasgo en Misión 501
            (502, 102, 10), # 10 Sombra Alada en Misión 502
            (502, 103, 1)   # 1 Rey Esqueleto (Jefe) en Misión 502
        ]
        cursor.executemany("INSERT INTO Encuentros VALUES (?, ?, ?)", encuentros)

        conn.commit()
        print("✅ Datos de ejemplo insertados exitosamente.")

    except sqlite3.Error as e:
        print(f"Error al insertar datos: {e}")
        conn.rollback()


def consultar_misiones_completas(conn):
    """
    Realiza una consulta con JOIN para obtener los detalles completos de las misiones,
    incluyendo héroes y monstruos.
    """
    print("\n--- 🔍 Reporte de Misiones, Héroes y Monstruos ---")
    
    query = """
    SELECT
        M.nombre AS Mision,
        H.nombre AS Heroe,
        P.rol_en_mision AS Rol,
        MO.nombre AS Monstruo_Enfrentado,
        E.cantidad AS Cantidad_Monstruo
    FROM
        Misiones M
    JOIN
        Participacion P ON M.id_mision = P.id_mision
    JOIN
        Heroes H ON P.id_heroe = H.id_heroe
    JOIN
        Encuentros E ON M.id_mision = E.id_mision
    JOIN
        Monstruos MO ON E.id_monstruo = MO.id_monstruo
    ORDER BY
        M.nombre, H.nombre, MO.nombre;
    """
    
    cursor = conn.cursor()
    cursor.execute(query)
    
    resultados = cursor.fetchall()
    
    if resultados:
        # Imprimir encabezado de la tabla
        print(f"{'Misión':<20} | {'Héroe':<10} | {'Rol':<15} | {'Monstruo Enfrentado':<20} | {'Cant.'}")
        print("-" * 75)
        # Imprimir resultados
        for row in resultados:
            print(f"{row[0]:<20} | {row[1]:<10} | {row[2]:<15} | {row[3]:<20} | {row[4]:<5}")
    else:
        print("No se encontraron datos en la consulta.")


# --- Función Principal ---
def main():
    conn = crear_conexion()
    
    if conn:
        crear_tablas(conn)
        insertar_datos_ejemplo(conn)
        consultar_misiones_completas(conn)
        conn.close()

if __name__ == "__main__":
    main()