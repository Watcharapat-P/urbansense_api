from fastapi import FastAPI
from app.database import engine
from app import models
from app.routers import router

# Create all tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="UrbanSense API",
    description="API for BTS station sensor data, weather, and MRT ridership.",
    version="0.1.0",
)

app.include_router(router, prefix="/api/v1")


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "docs": "/docs"}
