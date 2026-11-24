from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import List, Optional, Literal
from datetime import datetime

VALID_CATEGORIES = [
    "medical_supplies", "laboratory_services", "pharmaceutical",
    "clinical_software", "it_infrastructure", "hr_and_payroll_software",
    "cleaning_and_facilities", "patient_communication",
    "billing_and_coding_software", "training_platforms"
]

class SupplierBase(BaseModel):
    name: str
    country: Literal["USA", "UK"]
    categories: List[str] = Field(..., min_length=1)
    monthly_rate: float = Field(..., gt=0)
    currency: Literal["USD", "GBP"]
    status: Literal["active", "suspended"]
    compliance_agreement: Optional[Literal["BAA", "DPA", "both"]] = None
    contract_renewal_date: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    notes: Optional[str] = None

    @field_validator('categories')
    def validate_categories(cls, v):
        for cat in v:
            if cat not in VALID_CATEGORIES:
                raise ValueError(f"Categoría no válida: {cat}")
        return v

    @model_validator(mode='after')
    def check_country_currency(self):
        if self.country == "USA" and self.currency != "USD":
            raise ValueError("Proveedores de USA deben tener currency = USD")
        if self.country == "UK" and self.currency != "GBP":
            raise ValueError("Proveedores de UK deben tener currency = GBP")
        return self

class SupplierCreate(SupplierBase):
    pass

class SupplierResponse(SupplierBase):
    id: int
    updated_at: datetime

class RateUpdate(BaseModel):
    monthly_rate: float = Field(..., gt=0)

class StatusUpdate(BaseModel):
    status: Literal["active", "suspended"]
