from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging import configure_logging

from .api import router as api_router

settings = get_settings()
configure_logging(
    level=settings.log_level,
    json_format=settings.log_format == "json",
    sentry_dsn=settings.sentry_dsn,
    sentry_traces_sample_rate=settings.sentry_traces_sample_rate,
    environment=settings.app_env,
)

app = FastAPI(title="Number Recognition Service", version="0.1.0")

app.include_router(api_router, prefix="/api/v1")


@app.get("/ready")
def ready() -> dict[str, str]:
    return {"status": "ready"}


@app.get("/live")
def live() -> dict[str, str]:
    return {"status": "alive"}
