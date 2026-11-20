from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from database import suppliers_table
from models import SupplierCreate, SupplierResponse, RateUpdate, StatusUpdate
from security import get_current_user
from datetime import datetime

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

@router.post("", response_model=SupplierResponse, status_code=201)
def create_supplier(supplier: SupplierCreate, current_user: dict = Depends(get_current_user)):
    doc = supplier.model_dump()
    doc["updated_at"] = datetime.now().isoformat()
    doc_id = suppliers_table.insert(doc)
    doc["id"] = doc_id
    return doc

@router.get("", response_model=List[SupplierResponse])
def get_suppliers(country: Optional[str] = None, category: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    result = []
    # TinyDB devuelve Document al iterar la tabla; cada documento expone
    # públicamente doc_id además de los campos almacenados.
    for document in suppliers_table:
        doc = dict(document)
        if country and doc.get("country") != country:
            continue
        if category and category not in doc.get("categories", []):
            continue
        doc["id"] = document.doc_id
        result.append(doc)
    return result

@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(supplier_id: int, current_user: dict = Depends(get_current_user)):
    supplier = suppliers_table.get(doc_id=supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    supplier["id"] = supplier_id
    return supplier

@router.patch("/{supplier_id}/rate", response_model=SupplierResponse)
def update_rate(supplier_id: int, rate_data: RateUpdate, current_user: dict = Depends(get_current_user)):
    supplier = suppliers_table.get(doc_id=supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    supplier["monthly_rate"] = rate_data.monthly_rate
    supplier["updated_at"] = datetime.now().isoformat()
    suppliers_table.update(supplier, doc_ids=[supplier_id])
    supplier["id"] = supplier_id
    return supplier

@router.patch("/{supplier_id}/status", response_model=SupplierResponse)
def update_status(supplier_id: int, status_data: StatusUpdate, current_user: dict = Depends(get_current_user)):
    supplier = suppliers_table.get(doc_id=supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    supplier["status"] = status_data.status
    suppliers_table.update(supplier, doc_ids=[supplier_id])
    supplier["id"] = supplier_id
    return supplier

@router.delete("/{supplier_id}")
def delete_supplier(supplier_id: int, current_user: dict = Depends(get_current_user)):
    if not suppliers_table.contains(doc_id=supplier_id):
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    suppliers_table.remove(doc_ids=[supplier_id])
    return {"message": "Proveedor eliminado"}