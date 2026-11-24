import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.suppliers import router as suppliers_router

app = FastAPI(title="HealthCore Supplier Directory API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(suppliers_router)

@app.get("/")
def root():
    return {"message": "API de Proveedores HealthCore funcionando"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
