import sqlite3
import os

# --- Configuración de la Base de Datos ---
DB_NAME = 'biblioteca_personal.db'

def get_db_connection():
    """Establece la conexión a la base de datos y la retorna."""
    try:
        conn = sqlite3.connect(DB_NAME)
        # Permite acceder a las columnas por nombre
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar con SQLite: {e}")
        # En caso de error crítico de conexión
        exit(1)

def crear_tabla():
    """Crea la tabla 'libros' si no existe."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS libros (
            id INTEGER PRIMARY KEY,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            anio_publicacion INTEGER,
            genero TEXT,
            leido INTEGER DEFAULT 0 -- 0=No leído, 1=Leído
        );
    """)
    conn.commit()
    conn.close()

# --- Funciones de la Biblioteca ---

def agregar_libro():
    """Permite al usuario ingresar los datos de un nuevo libro."""
    print("\n--- AGREGAR NUEVO LIBRO ---")
    titulo = input("Título: ").strip()
    autor = input("Autor: ").strip()
    
    if not titulo or not autor:
        print("❌ Error: El título y el autor no pueden estar vacíos.")
        return

    # Entrada opcional y manejo de errores
    try:
        anio = int(input("Año de Publicación (opcional, deja vacío y presiona Enter): ") or 0)
    except ValueError:
        print("⚠️ Advertencia: Año no válido. Se establecerá como 0.")
        anio = 0
        
    genero = input("Género: ").strip()
    
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO libros (titulo, autor, anio_publicacion, genero) VALUES (?, ?, ?, ?)",
            (titulo, autor, anio if anio > 0 else None, genero if genero else None)
        )
        conn.commit()
        print(f"\n✅ Libro '{titulo}' de {autor} agregado exitosamente.")
    except sqlite3.Error as e:
        print(f"❌ Error al insertar el libro: {e}")
    finally:
        conn.close()

def listar_libros():
    """Muestra todos los libros en la base de datos."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM libros ORDER BY id DESC")
    libros = cursor.fetchall()
    conn.close()
    
    if not libros:
        print("\n--- 📚 BIBLIOTECA VACÍA ---")
        print("Aún no tienes libros registrados. Usa la opción 1 para agregar uno.")
        return

    print("\n--- 📚 MI BIBLIOTECA PERSONAL ---")
    print(f"{'ID':<4} | {'Título':<40} | {'Autor':<25} | {'Año':<4} | {'Leído'}")
    print("-" * 80)
    
    for libro in libros:
        estado_leido = "Sí (✅)" if libro['leido'] == 1 else "No (❌)"
        print(f"{libro['id']:<4} | {libro['titulo'][:40]:<40} | {libro['autor'][:25]:<25} | {libro['anio_publicacion'] if libro['anio_publicacion'] else 'N/A':<4} | {estado_leido}")
    print("-" * 80)

def marcar_como_leido():
    """Marca un libro como leído usando su ID."""
    listar_libros()
    try:
        libro_id = int(input("\nIngresa el ID del libro para marcar como LEÍDO: "))
    except ValueError:
        print("❌ Error: Por favor, ingresa un número válido.")
        return

    conn = get_db_connection()
    try:
        cursor = conn.execute("UPDATE libros SET leido = 1 WHERE id = ?", (libro_id,))
        if cursor.rowcount == 0:
            print(f"⚠️ Advertencia: No se encontró ningún libro con el ID {libro_id}.")
        else:
            conn.commit()
            print(f"✅ Libro con ID {libro_id} marcado como LEÍDO.")
    except sqlite3.Error as e:
        print(f"❌ Error al actualizar el libro: {e}")
    finally:
        conn.close()

def eliminar_libro():
    """Elimina un libro de la base de datos usando su ID."""
    listar_libros()
    try:
        libro_id = int(input("\nIngresa el ID del libro para ELIMINAR: "))
    except ValueError:
        print("❌ Error: Por favor, ingresa un número válido.")
        return

    conn = get_db_connection()
    try:
        cursor = conn.execute("DELETE FROM libros WHERE id = ?", (libro_id,))
        if cursor.rowcount == 0:
            print(f"⚠️ Advertencia: No se encontró ningún libro con el ID {libro_id}.")
        else:
            conn.commit()
            print(f"✅ Libro con ID {libro_id} eliminado exitosamente.")
    except sqlite3.Error as e:
        print(f"❌ Error al eliminar el libro: {e}")
    finally:
        conn.close()

# --- Interfaz de Usuario (Menú) ---

def mostrar_menu():
    """Muestra el menú principal de la aplicación."""
    print("\n" + "="*30)
    print("  ADMINISTRADOR DE BIBLIOTECA")
    print("="*30)
    print("1. Agregar nuevo libro")
    print("2. Listar todos los libros")
    print("3. Marcar libro como leído")
    print("4. Eliminar libro por ID")
    print("5. Salir")
    print("-" * 30)

def main():
    """Función principal para correr la aplicación CLI."""
    # Asegura que la tabla exista al inicio de la aplicación
    crear_tabla() 
    
    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción (1-5): ").strip()
        
        if opcion == '1':
            agregar_libro()
        elif opcion == '2':
            listar_libros()
        elif opcion == '3':
            marcar_como_leido()
        elif opcion == '4':
            eliminar_libro()
        elif opcion == '5':
            print("👋 Gracias por usar la Biblioteca CLI. ¡Hasta pronto!")
            break
        else:
            print("❌ Opción no válida. Por favor, selecciona un número entre 1 y 5.")
        
        # Pausa para mejor visualización en la terminal
        input("\nPresiona Enter para continuar...")
        # Limpia la pantalla para un menú más limpio
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    main()