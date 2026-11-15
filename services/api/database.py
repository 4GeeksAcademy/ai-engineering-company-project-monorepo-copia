# services/api/database.py
from tinydb import TinyDB
import os

# Obtener la ruta absoluta para que la BD se guarde en esta misma carpeta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "healthcore_db.json")

# Inicializar la base de datos TinyDB
db = TinyDB(DB_PATH)

# Definir la tabla de proveedores
suppliers_table = db.table("suppliers")