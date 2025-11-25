from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.pipeline import (
    ChannelConfig,
    ChannelDirection,
    DecoderPriority,
    PlateListPayload,
    PlateListType,
    RuleAction,
    RuleCondition,
    RuleDefinition,
    build_rules_engine,
    ingest_manager,
    postprocess_settings,
    recognition_pipeline,
)

router = APIRouter()

settings = get_settings()

rules_engine = build_rules_engine(
    min_confidence=settings.rules_default_min_confidence,
    anti_flood_seconds=settings.rules_default_anti_flood_seconds,
    min_frames=settings.rules_default_min_frames,
    default_actions={
        "trigger_relay": "trigger_relay" in settings.rules_default_actions,
        "send_webhook": "send_webhook" in settings.rules_default_actions,
        "record_clip": "record_clip" in settings.rules_default_actions,
        "annotate_ui": "annotate_ui" in settings.rules_default_actions,
    },
)


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


class PlateListRequest(BaseModel):
    name: str = Field(..., description="Название списка")
    type: PlateListType = Field(..., description="Тип списка: white/black/info")
    priority: int = Field(100, description="Приоритет обработки")
    ttl_seconds: int | None = Field(None, description="TTL элементов списка")
    schedule: dict | None = Field(None, description="Расписание активности списка")
    description: str | None = Field(None, description="Описание")


class PlateListItemRequest(BaseModel):
    pattern: str = Field(..., description="Номер или шаблон")
    comment: str | None = Field(None, description="Комментарий")
    ttl_seconds: int | None = Field(None, description="TTL для элемента")
    expires_at: str | None = Field(None, description="Дата истечения в ISO")


class RuleRequest(BaseModel):
    name: str
    conditions: RuleCondition
    actions: RuleAction | None = None


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


@router.post("/lists", summary="Создать список номеров")
def create_plate_list(request: PlateListRequest) -> dict:
    payload = PlateListPayload(**request.model_dump())
    created = rules_engine.register_list(payload)
    return created.model_dump()


@router.post("/lists/{list_id}/items", summary="Добавить элемент в список")
def add_plate_list_item(list_id: str, request: PlateListItemRequest) -> dict:
    item = request.model_dump()
    updated = rules_engine.add_item(list_id, item)
    return updated.model_dump()


@router.get("/lists", summary="Получить все списки и элементы")
def get_plate_lists() -> list[dict]:
    return [item.model_dump() for item in rules_engine.lists.values()]


@router.post("/rules", summary="Зарегистрировать правило IF→THEN")
def create_rule(request: RuleRequest) -> dict:
    rule = RuleDefinition(
        name=request.name,
        conditions=request.conditions,
        actions=request.actions or rules_engine.default_actions,
    )
    created = rules_engine.register_rule(rule)
    return created.model_dump()


@router.get("/rules/status", summary="Статус Rules Engine, условия и действия")
def rules_status() -> dict:
    return rules_engine.describe()
