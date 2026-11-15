# services/api/seed.py
import uuid
from datetime import datetime
from database import suppliers_table

def seed_database():
    # Datos iniciales (basados en el contexto de HealthCore)
    initial_suppliers = [
        {
            "name": "Austin Medical Supplies",
            "country": "USA",
            "product_categories": ["Medical Equipment", "PPE"],
            "rate": 1500.50,
            "status": "active"
        },
        {
            "name": "London Pharma Logistics",
            "country": "UK",
            "product_categories": ["Pharmaceuticals"],
            "rate": 3200.00,
            "status": "active"
        },
        {
            "name": "Global Lab Gear",
            "country": "USA",
            "product_categories": ["Lab Supplies"],
            "rate": 850.00,
            "status": "suspended"
        },
        {
            "name": "UK MediTech",
            "country": "UK",
            "product_categories": ["Medical Equipment"],
            "rate": 2100.75,
            "status": "active"
        }
    ]

    inserted_count = 0

    for supplier in initial_suppliers:
        # Lógica de idempotencia: Verificar si el proveedor ya existe por nombre
        existing = suppliers_table.search(lambda s: s['name'] == supplier['name'])
        
        if not existing:
            # Generar ID y timestamp automáticamente
            supplier['id'] = str(uuid.uuid4())
            supplier['updated_at'] = datetime.now().isoformat()
            
            # Insertar en la base de datos
            suppliers_table.insert(supplier)
            inserted_count += 1

    print(f"✅ Seeder completado. {inserted_count} proveedores insertados en el directorio de HealthCore.")

def main():
    seed_database()

if __name__ == "__main__":
    main()