# services/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.suppliers import router as suppliers_router

app = FastAPI(
    title="HealthCore - Directorio de Proveedores API",
    description="API para la gestión centralizada de proveedores médicos de HealthCore",
    version="1.0.0"
)

# Configuración de CORS optimizada para Codespaces
app.add_middleware(
    CORSMiddleware,
    # Esto permite dinámicamente cualquier URL de github.dev
    allow_origin_regex="https://.*\.github\.dev", 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir las rutas de proveedores
app.include_router(suppliers_router)

@app.get("/")
def read_root() -> dict:
    return {"message": "Bienvenido a la API de HealthCore. Ve a /docs para ver la documentación."}