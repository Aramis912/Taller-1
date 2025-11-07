from sqlalchemy import create_engine, Column, Integer, String, Boolean 
from sqlalchemy.orm import declarative_base, sessionmaker 
from sqlalchemy.exc import OperationalError, SQLAlchemyError 
import os

# --- 1. Configuración de la Base de Datos MariaDB/MySQL ---
# NOTA: Asegúrate de que tu servidor MariaDB/MySQL esté en ejecución
# y reemplaza las credenciales con las tuyas.
DB_USER = 'usuario_bd'   # Cambia esto por tu usuario de MariaDB
DB_PASS = 'tu_contraseña'  # Cambia esto por tu contraseña
DB_HOST = 'localhost'
DB_PORT = 3306
DB_NAME = 'biblioteca_orm'

# URL de conexión para SQLAlchemy (usando PyMySQL como driver)
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- 2. Definición del ORM (Modelo de Datos) ---

# Base declarativa para nuestras clases de modelo
Base = declarative_base()

class Libro(Base):
    """Define la estructura de la tabla 'libros'."""
    __tablename__ = 'libros'

    id = Column(Integer, primary_key=True)
    titulo = Column(String(255), nullable=False)
    autor = Column(String(255), nullable=False)
    anio_publicacion = Column(Integer)
    genero = Column(String(100))
    leido = Column(Boolean, default=False) # SQLAlchemy maneja Boolean como 0/1

    def __repr__(self):
        """Representación legible del objeto."""
        return f"<Libro(id={self.id}, titulo='{self.titulo}', autor='{self.autor}')>"

# --- 3. Conexión y Sesión ---

# Creamos el motor de la base de datos
try:
    engine = create_engine(DATABASE_URL)
    # Crea las tablas definidas en el modelo (si no existen)
    Base.metadata.create_all(engine)
    
    # Creamos una clase Session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    print(f"✅ Conexión a MariaDB '{DB_NAME}' exitosa. Tablas verificadas/creadas.")

except OperationalError as e:
    print("\n❌ ERROR CRÍTICO DE CONEXIÓN A LA BASE DE DATOS ❌")
    print("---------------------------------------------------------------------")
    print(f"Asegúrate de que el servidor MariaDB/MySQL esté corriendo y que la base de datos '{DB_NAME}' exista.")
    print("Revisa tus credenciales (usuario/contraseña) y la configuración en el código.")
    print(f"Detalle: {e}")
    # Detenemos la ejecución si la conexión inicial falla
    exit(1)
except SQLAlchemyError as e:
    print(f"❌ Error general de SQLAlchemy: {e}")
    exit(1)


def get_db_session():
    """Genera una nueva sesión de base de datos para cada operación."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 4. Funciones de la Biblioteca (Usando ORM) ---

def agregar_libro():
    """Agrega un nuevo libro a la base de datos usando el ORM."""
    print("\n--- AGREGAR NUEVO LIBRO ---")
    titulo = input("Título: ").strip()
    autor = input("Autor: ").strip()
    
    if not titulo or not autor:
        print("❌ Error: El título y el autor no pueden estar vacíos.")
        return

    try:
        anio = input("Año de Publicación (opcional): ")
        anio = int(anio) if anio.isdigit() else None
    except ValueError:
        print("⚠️ Advertencia: Año no válido. Se ignorará.")
        anio = None
        
    genero = input("Género: ").strip()
    genero = genero if genero else None

    # Creamos un objeto Libro
    nuevo_libro = Libro(
        titulo=titulo,
        autor=autor,
        anio_publicacion=anio,
        genero=genero,
        leido=False
    )
    
    # Abrimos sesión, agregamos y confirmamos (commit)
    session = next(get_db_session())
    try:
        session.add(nuevo_libro)
        session.commit()
        print(f"\n✅ Libro '{titulo}' de {autor} agregado exitosamente (ID: {nuevo_libro.id}).")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"❌ Error al insertar el libro: {e}")
    finally:
        session.close()

def listar_libros():
    """Muestra todos los libros consultados a través del ORM."""
    session = next(get_db_session())
    libros = session.query(Libro).order_by(Libro.id.desc()).all()
    session.close()
    
    if not libros:
        print("\n--- 📚 BIBLIOTECA VACÍA ---")
        print("Aún no tienes libros registrados. Usa la opción 1 para agregar uno.")
        return

    print("\n--- 📚 MI BIBLIOTECA PERSONAL ---")
    print(f"{'ID':<4} | {'Título':<40} | {'Autor':<25} | {'Año':<4} | {'Leído'}")
    print("-" * 80)
    
    for libro in libros:
        estado_leido = "Sí (✅)" if libro.leido else "No (❌)"
        print(f"{libro.id:<4} | {libro.titulo[:40]:<40} | {libro.autor[:25]:<25} | {libro.anio_publicacion if libro.anio_publicacion else 'N/A':<4} | {estado_leido}")
    print("-" * 80)

def marcar_como_leido():
    """Marca un libro como leído usando su ID (ORM Update)."""
    listar_libros()
    try:
        libro_id = int(input("\nIngresa el ID del libro para marcar como LEÍDO: "))
    except ValueError:
        print("❌ Error: Por favor, ingresa un número válido.")
        return

    session = next(get_db_session())
    try:
        # Busca el objeto Libro por ID
        libro = session.query(Libro).filter(Libro.id == libro_id).first()
        
        if libro:
            if libro.leido:
                print(f"⚠️ Advertencia: El libro con ID {libro_id} ya estaba marcado como leído.")
                return
            
            libro.leido = True  # Modificamos el atributo del objeto
            session.commit()    # Guardamos el cambio en la BD
            print(f"✅ Libro con ID {libro_id} ('{libro.titulo}') marcado como LEÍDO.")
        else:
            print(f"⚠️ Advertencia: No se encontró ningún libro con el ID {libro_id}.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"❌ Error al actualizar el libro: {e}")
    finally:
        session.close()

def eliminar_libro():
    """Elimina un libro de la base de datos usando su ID (ORM Delete)."""
    listar_libros()
    try:
        libro_id = int(input("\nIngresa el ID del libro para ELIMINAR: "))
    except ValueError:
        print("❌ Error: Por favor, ingresa un número válido.")
        return

    session = next(get_db_session())
    try:
        libro = session.query(Libro).filter(Libro.id == libro_id).first()
        
        if libro:
            session.delete(libro) # Eliminamos el objeto
            session.commit()
            print(f"✅ Libro con ID {libro_id} ('{libro.titulo}') eliminado exitosamente.")
        else:
            print(f"⚠️ Advertencia: No se encontró ningún libro con el ID {libro_id}.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"❌ Error al eliminar el libro: {e}")
    finally:
        session.close()

# --- 5. Interfaz de Usuario (Menú) ---

def mostrar_menu():
    """Muestra el menú principal de la aplicación."""
    print("\n" + "="*35)
    print("  ADMINISTRADOR DE BIBLIOTECA (MariaDB)")
    print("="*35)
    print("1. Agregar nuevo libro")
    print("2. Listar todos los libros")
    print("3. Marcar libro como leído")
    print("4. Eliminar libro por ID")
    print("5. Salir")
    print("-" * 35)

def main():
    """Función principal para correr la aplicación CLI."""
    # Base.metadata.create_all(engine) ya fue llamado en la sección de conexión
    
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
            print("👋 Gracias por usar la Biblioteca CLI con MariaDB/SQLAlchemy.")
            break
        else:
            print("❌ Opción no válida. Por favor, selecciona un número entre 1 y 5.")
        
        # Pausa y limpieza de pantalla
        input("\nPresiona Enter para continuar...")
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    main()