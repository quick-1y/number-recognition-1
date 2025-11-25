from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="Service health-check")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/modules", summary="List core modules and responsibilities")
def modules() -> dict[str, list[str]]:
    return {
        "pipeline": [
            "ingest",
            "decoder",
            "motion_trigger",
            "detector",
            "tracker",
            "cropper",
            "ocr_engine",
            "postprocessor",
            "rules_engine",
            "event_manager",
            "webhook_service",
            "alarm_relay_controller",
        ],
        "interfaces": ["api", "ui", "monitoring"],
    }
