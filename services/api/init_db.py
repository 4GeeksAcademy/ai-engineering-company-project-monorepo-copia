from tinydb import TinyDB


def initialize_database():
    db = TinyDB("db.json")
    db.table("suppliers")
    db.close()
    print("Base de datos inicializada correctamente")


if __name__ == "__main__":
    initialize_database()
