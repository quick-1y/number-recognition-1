from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.pipeline import (
    ChannelConfig,
    ChannelDirection,
    DecoderPriority,
    ingest_manager,
    postprocess_settings,
    recognition_pipeline,
)

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


@router.get("/pipeline/status", summary="Конфигурация детектора, трекера, OCR и постобработки")
def pipeline_status() -> dict:
    return {
        **recognition_pipeline.describe(),
        "postprocess": postprocess_settings.describe(),
    }


class ChannelRequest(BaseModel):
    channel_id: str = Field(..., description="Уникальный идентификатор канала")
    name: str = Field(..., description="Человекочитаемое имя канала")
    source: str = Field(..., description="RTSP/ONVIF/файловый источник")
    protocol: str = Field("rtsp", description="Протокол источника (rtsp/onvif/file)")
    target_fps: int = Field(12, description="Целевой FPS обработки")
    reconnect_seconds: int = Field(3, description="Интервал авто-переподключения")
    decoder_priority: list[DecoderPriority] = Field(
        default_factory=lambda: [DecoderPriority.nvdec, DecoderPriority.vaapi, DecoderPriority.cpu]
    )
    direction: ChannelDirection = Field(ChannelDirection.any, description="Направление движения: up/down/any")
    roi: dict | None = Field(None, description="ROI/маска кадра в виде полигона")
    description: str | None = Field(None, description="Комментарий или место установки")


@router.post("/ingest/channels", summary="Зарегистрировать канал для ingest")
def register_channel(request: ChannelRequest) -> dict:
    channel = ChannelConfig(
        channel_id=request.channel_id,
        name=request.name,
        source=request.source,
        protocol=request.protocol,
        target_fps=request.target_fps,
        reconnect_seconds=request.reconnect_seconds,
        decoder_priority=list(request.decoder_priority),
        direction=request.direction,
        roi=request.roi,
        description=request.description,
    )
    status = ingest_manager.register_channel(channel)
    return status.as_dict()


@router.get("/ingest/channels", summary="Снимок состояния ingest по каналам")
def ingest_channels() -> list[dict]:
    return ingest_manager.snapshot()
