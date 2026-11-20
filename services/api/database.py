from pathlib import Path

from tinydb import TinyDB

DATABASE_PATH = Path(__file__).resolve().parent / "db.json"
db = TinyDB(DATABASE_PATH)
suppliers_table = db.table('suppliers')
users_table = db.table('users')
profiles_table = db.table('profiles')
