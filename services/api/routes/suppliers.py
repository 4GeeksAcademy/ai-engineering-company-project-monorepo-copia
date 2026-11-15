# services/api/routes/suppliers.py
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from datetime import datetime
import uuid

from models import Supplier, SupplierCreate, SupplierRateUpdate, SupplierStatusUpdate
from database import suppliers_table

router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"]
)

# 1. POST /suppliers - Registrar un proveedor nuevo
@router.post("/", response_model=Supplier, status_code=status.HTTP_201_CREATED)
def create_supplier(supplier: SupplierCreate):
    # mode="json" convierte los Enums a strings para que TinyDB no falle
    supplier_dict = supplier.model_dump(mode="json")
    
    # Generamos ID y fecha
    supplier_dict["id"] = str(uuid.uuid4())
    supplier_dict["updated_at"] = datetime.now().isoformat()
    
    # Guardamos en TinyDB
    suppliers_table.insert(supplier_dict)
    
    return supplier_dict

# 2. GET /suppliers - Listar todos (con filtros opcionales)
@router.get("/", response_model=List[Supplier])
def get_suppliers(country: Optional[str] = None, category: Optional[str] = None):
    all_suppliers = suppliers_table.all()
    
    # Filtrado
    filtered = all_suppliers
    if country:
        filtered = [s for s in filtered if s.get("country") == country]
    if category:
        filtered = [s for s in filtered if category in s.get("product_categories", [])]
        
    return filtered

# 3. GET /suppliers/{id} - Detalle de un proveedor
@router.get("/{supplier_id}", response_model=Supplier)
def get_supplier(supplier_id: str):
    # TinyDB busca por el campo 'id'
    supplier = suppliers_table.get(lambda s: s["id"] == supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return supplier

# 4. PATCH /suppliers/{id}/rate - Actualizar tarifa
@router.patch("/{supplier_id}/rate", response_model=Supplier)
def update_supplier_rate(supplier_id: str, rate_update: SupplierRateUpdate):
    supplier = suppliers_table.get(lambda s: s["id"] == supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    # Actualizamos la tarifa y el timestamp
    suppliers_table.update(
        {"rate": rate_update.rate, "updated_at": datetime.now().isoformat()},
        lambda s: s["id"] == supplier_id
    )
    
    # Obtenemos el actualizado
    updated_supplier = suppliers_table.get(lambda s: s["id"] == supplier_id)
    return updated_supplier

# 5. PATCH /suppliers/{id}/status - Activar o suspender
@router.patch("/{supplier_id}/status", response_model=Supplier)
def update_supplier_status(supplier_id: str, status_update: SupplierStatusUpdate):
    supplier = suppliers_table.get(lambda s: s["id"] == supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    # status_update.status.value extrae el string ("active" o "suspended")
    suppliers_table.update(
        {"status": status_update.status.value, "updated_at": datetime.now().isoformat()},
        lambda s: s["id"] == supplier_id
    )
    
    updated_supplier = suppliers_table.get(lambda s: s["id"] == supplier_id)
    return updated_supplier

# 6. DELETE /suppliers/{id} - Eliminar proveedor
@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_supplier(supplier_id: str):
    supplier = suppliers_table.get(lambda s: s["id"] == supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    suppliers_table.remove(lambda s: s["id"] == supplier_id)
    return None