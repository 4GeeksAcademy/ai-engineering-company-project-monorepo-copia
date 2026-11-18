from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.suppliers import router as suppliers_router
from init_db import initialize_database

app = FastAPI(title="HealthCore Supplier Directory API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(suppliers_router)


@app.on_event("startup")
def initialize_database_on_startup():
    initialize_database()


@app.get("/")
def root():
    return {"message": "API de Proveedores HealthCore funcionando"}
