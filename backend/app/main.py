from fastapi import FastAPI

from .api import router as api_router

app = FastAPI(title="Number Recognition Service", version="0.1.0")

app.include_router(api_router, prefix="/api/v1")


@app.get("/ready")
def ready() -> dict[str, str]:
    return {"status": "ready"}


@app.get("/live")
def live() -> dict[str, str]:
    return {"status": "alive"}
