# services/api/models.py
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from typing import List

# 1. Enums (Valores permitidos)
class SupplierStatus(str, Enum):
    active = "active"
    suspended = "suspended"

class SupplierCategory(str, Enum):
    medical_equipment = "Medical Equipment"
    ppe = "PPE"
    pharmaceuticals = "Pharmaceuticals"
    lab_supplies = "Lab Supplies"

# 2. Modelo para crear un proveedor (POST)
class SupplierCreate(BaseModel):
    name: str = Field(..., min_length=2, description="Nombre del proveedor")
    country: str = Field(..., pattern="^(USA|UK)$", description="Debe ser USA o UK")
    product_categories: List[SupplierCategory] = Field(..., min_items=1)
    rate: float = Field(..., gt=0, description="La tarifa debe ser mayor a 0")
    status: SupplierStatus = Field(default=SupplierStatus.active)

# 3. Modelo completo (Lo que se guarda en TinyDB)
class Supplier(SupplierCreate):
    id: str
    updated_at: datetime

# 4. Modelos para actualizaciones parciales (PATCH)
class SupplierRateUpdate(BaseModel):
    rate: float = Field(..., gt=0, description="La tarifa debe ser mayor a 0")

class SupplierStatusUpdate(BaseModel):
    status: SupplierStatus