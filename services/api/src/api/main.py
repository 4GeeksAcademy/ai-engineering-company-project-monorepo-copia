from fastapi import FastAPI

from api.incidents.router import router as incidents_router

app = FastAPI(title="API de HealthCore")
app.include_router(incidents_router)