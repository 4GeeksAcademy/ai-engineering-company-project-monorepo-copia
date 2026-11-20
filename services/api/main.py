from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import router as auth_router
from routes.profiles import router as profiles_router
from routes.suppliers import router as suppliers_router
from routes.users import router as users_router
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
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(profiles_router)


@app.on_event("startup")
def initialize_database_on_startup():
    initialize_database()


@app.get("/")
def root():
    return {"message": "API de Proveedores HealthCore funcionando"}