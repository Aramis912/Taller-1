import pymongo
# Se usa ConnectionFailure ya que ConnectionError causa el ImportError
from pymongo.errors import ConnectionFailure, OperationFailure 
import os
import sys 

# --- 1. Configuración de la Base de Datos MongoDB ---
# Usaremos una variable de entorno para la URI, si no está configurada, usa la local por defecto
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/') 
DB_NAME = 'biblioteca_nosql'
COLLECTION_NAME = 'libros'

# --- 2. Conexión y Cliente ---
def get_mongo_collection():
    """Establece la conexión a MongoDB y retorna la colección 'libros'."""
    try:
        # 1. Crear el cliente
        # Ajuste: El serverSelectionTimeoutMS previene que la aplicación se congele indefinidamente si falla la conexión.
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000) 
        
        # 2. Verificar la conexión inmediatamente
        client.admin.command('ping') 
        
        # 3. Seleccionar la base de datos y la colección
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        print(f"✅ Conexión a MongoDB exitosa. Usando colección '{COLLECTION_NAME}'.")
        return collection
    
    # Capturamos el error de fallo de conexión con la clase correcta
    except ConnectionFailure as e: 
        print("\n❌ ERROR CRÍTICO DE CONEXIÓN A MONGODB ❌")
        print("---------------------------------------------------------------------")
        print(f"Asegúrate de que el servidor MongoDB esté corriendo o que la URI ({MONGO_URI}) sea correcta.")
        print("El programa se cerrará.")
        sys.exit(1) # Finaliza el programa si la conexión inicial falla
    except OperationFailure as e:
        print(f"❌ Error de operación de MongoDB: {e}")
        sys.exit(1)


libros_collection = get_mongo_collection()


# --- 3. Funciones de la Biblioteca (CRUD y Validaciones) ---

def agregar_libro():
    """Agrega un nuevo libro como un documento a la colección con validación de entradas."""
    print("\n--- AGREGAR NUEVO LIBRO ---")
    titulo = input("Título: ").strip()
    autor = input("Autor: ").strip()
    
    # Validación 1: Campos requeridos
    if not titulo or not autor:
        print("❌ Error: El título y el autor no pueden estar vacíos (Documento mal estructurado).")
        return

    try:
        anio = input("Año de Publicación (opcional): ")
        # Validación 2: Tipo de dato (garantiza que sea None o int)
        anio = int(anio) if anio.isdigit() else None
    except ValueError:
        print("⚠️ Advertencia: Año no válido. Se ignorará.")
        anio = None
        
    genero = input("Género: ").strip()
    
    nuevo_libro = {
        "titulo": titulo,
        "autor": autor,
        "anio_publicacion": anio,
        "genero": genero if genero else None,
        "leido": False 
    }
    
    try:
        resultado = libros_collection.insert_one(nuevo_libro)
        print(f"\n✅ Libro '{titulo}' de {autor} agregado exitosamente (ID: {resultado.inserted_id}).")
    except OperationFailure as e:
        print(f"❌ Error al insertar el libro: {e}")

def listar_libros():
    """Muestra todos los documentos (libros) en la colección."""
    
    libros_cursor = libros_collection.find().sort("_id", pymongo.DESCENDING)
    libros = list(libros_cursor) 
    
    # Validación 3: Búsquedas sin resultados
    if not libros:
        print("\n--- 📚 BIBLIOTECA VACÍA ---")
        print("Aún no tienes libros registrados. Usa la opción 1 para agregar uno.")
        return

    print("\n--- 📚 MI BIBLIOTECA PERSONAL (MongoDB) ---")
    print(f"{'ID (5 chars)':<7} | {'Título':<35} | {'Autor':<25} | {'Año':<4} | {'Leído'}")
    print("-" * 85)
    
    for libro in libros:
        estado_leido = "Sí (✅)" if libro.get('leido', False) else "No (❌)"
        id_display = str(libro['_id'])[-5:]
        
        print(f"{id_display:<7} | {libro['titulo'][:35]:<35} | {libro['autor'][:25]:<25} | {libro['anio_publicacion'] if libro['anio_publicacion'] else 'N/A':<4} | {estado_leido}")
    print("-" * 85)

# (Las funciones marcar_como_leido y eliminar_libro se mantienen con el mismo manejo de errores)

# ... (El resto del código del menú y main se mantiene igual)

def marcar_como_leido():
    listar_libros()
    id_str = input("\nIngresa los ÚLTIMOS 5 dígitos del ID para marcar como LEÍDO: ").strip()
    
    if not id_str:
        print("❌ Error: El ID no puede estar vacío.")
        return

    try:
        libro = libros_collection.find_one({"_id": {"$regex": f".*{id_str}$"}})
        
        if not libro:
            print(f"⚠️ Advertencia: No se encontró un libro cuyo ID termine en {id_str}.")
            return
            
        resultado = libros_collection.update_one(
            {"_id": libro["_id"]},
            {"$set": {"leido": True}}
        )
        
        if resultado.modified_count > 0:
            print(f"✅ Libro con ID final {id_str} ('{libro['titulo']}') marcado como LEÍDO.")
        else:
             print(f"⚠️ Advertencia: El libro ya estaba marcado como leído o no se pudo actualizar.")
             
    except OperationFailure as e:
        print(f"❌ Error al actualizar el libro: {e}")
        
def eliminar_libro():
    listar_libros()
    id_str = input("\nIngresa los ÚLTIMOS 5 dígitos del ID para ELIMINAR: ").strip()
    
    if not id_str:
        print("❌ Error: El ID no puede estar vacío.")
        return

    try:
        libro = libros_collection.find_one({"_id": {"$regex": f".*{id_str}$"}})

        if not libro:
            print(f"⚠️ Advertencia: No se encontró un libro cuyo ID termine en {id_str}.")
            return
            
        resultado = libros_collection.delete_one({"_id": libro["_id"]})
        
        if resultado.deleted_count > 0:
            print(f"✅ Libro con ID final {id_str} ('{libro['titulo']}') eliminado exitosamente.")
        else:
            print(f"⚠️ Advertencia: No se pudo eliminar el libro.")

    except OperationFailure as e:
        print(f"❌ Error al eliminar el libro: {e}")

def mostrar_menu():
    print("\n" + "="*38)
    print("  ADMINISTRADOR DE BIBLIOTECA (MongoDB)")
    print("="*38)
    print("1. Agregar nuevo libro")
    print("2. Listar todos los libros")
    print("3. Marcar libro como leído")
    print("4. Eliminar libro por ID (últimos 5 dígitos)")
    print("5. Salir")
    print("-" * 38)

def main():
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
            print("👋 Gracias por usar la Biblioteca CLI con MongoDB.")
            break
        else:
            print("❌ Opción no válida. Por favor, selecciona un número entre 1 y 5.")
        
        input("\nPresiona Enter para continuar...")
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    if libros_collection: # Asegura que la aplicación solo corra si la conexión fue exitosa
        main()   