from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token, verify_password
from app.api.deps import get_db, require_role
from app.db.models import User, UserRole
from app.events import alarm_relay_controller, event_manager, webhook_service
from app.monitoring import base_operational_snapshot, metrics_registry
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


@router.get("/monitoring/status", summary="Снимок метрик и состояния сервисов")
def monitoring_status(current_user: User = Depends(require_role(UserRole.viewer))) -> dict:
    metrics_registry.set_gauge("ingest_channels", len(ingest_manager.channels))
    metrics_registry.set_gauge("webhook_subscriptions", len(webhook_service.subscriptions))
    metrics_registry.set_gauge("relay_count", len(alarm_relay_controller.relays))
    return {
        "snapshot": base_operational_snapshot(),
        "metrics": metrics_registry.describe(),
    }


@router.get("/metrics", response_class=PlainTextResponse, include_in_schema=False)
def prometheus_metrics() -> str:
    return metrics_registry.export_prometheus()


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


@router.get(
    "/pipeline/status",
    summary="Конфигурация детектора, трекера, OCR и постобработки",
)
def pipeline_status(current_user: User = Depends(require_role(UserRole.viewer))) -> dict:
    return {
        **recognition_pipeline.describe(),
        "postprocess": postprocess_settings.describe(),
    }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str | None
    role: UserRole
    is_active: bool


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


class EventRequest(BaseModel):
    channel_id: str | None = Field(None, description="Канал, откуда пришло событие")
    track_id: str | None = Field(None, description="Track ID из трекера")
    plate: str | None = Field(None, description="Распознанный номер")
    confidence: float = Field(0.0, description="Уверенность распознавания")
    country: str | None = Field(None, description="Шаблон страны")
    bbox: list[float] | None = Field(None, description="Геометрия номера")
    direction: ChannelDirection | None = Field(None, description="Направление движения")
    image_url: str | None = Field(None, description="Ссылка на изображение/кадр")
    meta: dict | None = Field(None, description="Доп. метаданные события")


class WebhookSubscriptionRequest(BaseModel):
    name: str
    url: str
    secret: str | None = Field(None, description="Секрет для HMAC подписи")
    filters: dict | None = Field(None, description="Фильтры событий по спискам/каналам")


class AlarmRelayRequest(BaseModel):
    name: str
    channel_id: str | None = Field(None, description="Канал или камера")
    mode: str | None = Field(None, description="Режим реле")
    delay_ms: int | None = Field(None, description="Задержка между командами")
    debounce_ms: int | None = Field(None, description="Антидребезг")


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


@router.post(
    "/auth/token",
    response_model=TokenResponse,
    summary="Получить JWT токен (OAuth2 password flow)",
)
def issue_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user: User | None = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(subject=str(user.id), role=user.role.value)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 60 * get_settings().jwt_expires_minutes,
    }


@router.get(
    "/auth/me",
    response_model=UserResponse,
    summary="Текущий пользователь и его роль",
)
def auth_me(current_user: User = Depends(require_role(UserRole.viewer))) -> User:
    return current_user


@router.post("/ingest/channels", summary="Зарегистрировать канал для ingest")
def register_channel(
    request: ChannelRequest,
    current_user: User = Depends(require_role(UserRole.operator, UserRole.admin)),
    ) -> dict:
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
    metrics_registry.set_gauge("ingest_channels", len(ingest_manager.channels))
    return status.as_dict()


@router.get(
    "/ingest/channels",
    summary="Снимок состояния ingest по каналам",
)
def ingest_channels(current_user: User = Depends(require_role(UserRole.viewer))) -> list[dict]:
    return ingest_manager.snapshot()


@router.post(
    "/lists",
    summary="Создать список номеров",
)
def create_plate_list(
    request: PlateListRequest,
    current_user: User = Depends(require_role(UserRole.operator, UserRole.admin)),
) -> dict:
    payload = PlateListPayload(**request.model_dump())
    created = rules_engine.register_list(payload)
    metrics_registry.inc("lists_created", labels={"type": payload.type.value})
    return created.model_dump()


@router.post(
    "/lists/{list_id}/items",
    summary="Добавить элемент в список",
)
def add_plate_list_item(
    list_id: str,
    request: PlateListItemRequest,
    current_user: User = Depends(require_role(UserRole.operator, UserRole.admin)),
) -> dict:
    item = request.model_dump()
    updated = rules_engine.add_item(list_id, item)
    metrics_registry.inc("list_items", labels={"list_id": list_id})
    return updated.model_dump()


@router.get(
    "/lists",
    summary="Получить все списки и элементы",
)
def get_plate_lists(current_user: User = Depends(require_role(UserRole.viewer))) -> list[dict]:
    return [item.model_dump() for item in rules_engine.lists.values()]


@router.post("/rules", summary="Зарегистрировать правило IF→THEN")
def create_rule(
    request: RuleRequest,
    current_user: User = Depends(require_role(UserRole.operator, UserRole.admin)),
) -> dict:
    rule = RuleDefinition(
        name=request.name,
        conditions=request.conditions,
        actions=request.actions or rules_engine.default_actions,
    )
    created = rules_engine.register_rule(rule)
    metrics_registry.inc("rules_registered")
    return created.model_dump()


@router.get("/rules/status", summary="Статус Rules Engine, условия и действия")
def rules_status(current_user: User = Depends(require_role(UserRole.viewer))) -> dict:
    return rules_engine.describe()


@router.post("/events", summary="Записать событие распознавания")
def record_event(
    request: EventRequest,
    current_user: User = Depends(require_role(UserRole.operator, UserRole.admin)),
) -> dict:
    event = event_manager.record_event(
        channel_id=request.channel_id,
        track_id=request.track_id,
        plate=request.plate,
        confidence=request.confidence,
        country=request.country,
        bbox=request.bbox,
        direction=request.direction.value if request.direction else None,
        image_url=request.image_url,
        meta=request.meta,
    )
    metrics_registry.inc(
        "events", labels={"channel": request.channel_id or "unknown", "country": request.country or "n/a"}
    )
    metrics_registry.observe("event_confidence", request.confidence)
    return event.as_dict()


@router.get("/events/status", summary="Статус Event Manager, Webhook Service и Alarm Relay")
def events_status(current_user: User = Depends(require_role(UserRole.viewer))) -> dict:
    return {
        "events": event_manager.describe(),
        "webhooks": webhook_service.describe(),
        "alarm_relays": alarm_relay_controller.describe(),
    }


@router.get("/events", summary="Последние события распознавания")
def list_events(
    channel_id: str | None = None,
    plate: str | None = None,
    limit: int = 50,
    current_user: User = Depends(require_role(UserRole.viewer)),
) -> list[dict]:
    query = list(reversed(event_manager.events))
    if channel_id:
        query = [event for event in query if event.channel_id == channel_id]
    if plate:
        query = [event for event in query if event.plate and plate.lower() in event.plate.lower()]
    return [event.as_dict() for event in query[:limit]]


@router.post(
    "/webhooks/subscriptions",
    summary="Зарегистрировать webhook подписку",
)
def create_webhook_subscription(
    request: WebhookSubscriptionRequest,
    current_user: User = Depends(require_role(UserRole.operator, UserRole.admin)),
) -> dict:
    subscription = webhook_service.register_subscription(
        name=request.name,
        url=request.url,
        secret=request.secret,
        filters=request.filters,
    )
    metrics_registry.set_gauge("webhook_subscriptions", len(webhook_service.subscriptions))
    return subscription.as_dict()


@router.get("/webhooks/subscriptions", summary="Получить активные подписки")
def list_webhook_subscriptions(
    current_user: User = Depends(require_role(UserRole.viewer)),
) -> list[dict]:
    return [item.as_dict() for item in webhook_service.subscriptions.values()]


@router.post("/alarms/relays", summary="Добавить реле камеры")
def register_alarm_relay(
    request: AlarmRelayRequest,
    current_user: User = Depends(require_role(UserRole.operator, UserRole.admin)),
) -> dict:
    relay = alarm_relay_controller.register_relay(
        name=request.name,
        channel_id=request.channel_id,
        mode=request.mode,
        delay_ms=request.delay_ms,
        debounce_ms=request.debounce_ms,
    )
    metrics_registry.set_gauge("relay_count", len(alarm_relay_controller.relays))
    return relay.as_dict()


@router.get("/alarms/relays", summary="Получить список реле")
def list_alarm_relays(
    current_user: User = Depends(require_role(UserRole.viewer)),
) -> list[dict]:
    return [relay.as_dict() for relay in alarm_relay_controller.relays.values()]


@router.post(
    "/alarms/relays/{relay_id}/trigger",
    summary="Сработать реле",
)
def trigger_alarm_relay(
    relay_id: str, current_user: User = Depends(require_role(UserRole.operator, UserRole.admin))
) -> dict:
    relay = alarm_relay_controller.trigger(relay_id)
    metrics_registry.inc("relay_triggers", labels={"relay_id": relay_id})
    return relay.as_dict()
