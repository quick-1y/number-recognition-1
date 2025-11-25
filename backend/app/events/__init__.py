"""Event pipeline primitives: event manager, webhook service and alarm relay controller."""

from __future__ import annotations

import hashlib
import hmac
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any

from app.core.config import get_settings


@dataclass
class EventStorageConfig:
    bucket: str
    prefix: str
    image_ttl_days: int
    clip_before_seconds: int
    clip_after_seconds: int

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RecognitionEvent:
    id: str
    channel_id: str | None
    track_id: str | None
    plate: str | None
    confidence: float
    country: str | None
    bbox: list[float] | None
    direction: str | None
    image_url: str | None
    meta: dict[str, Any]
    created_at: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EventManager:
    storage: EventStorageConfig
    events: list[RecognitionEvent] = field(default_factory=list)

    def record_event(
        self,
        *,
        channel_id: str | None,
        track_id: str | None,
        plate: str | None,
        confidence: float,
        country: str | None,
        bbox: list[float] | None,
        direction: str | None,
        image_url: str | None,
        meta: dict[str, Any] | None = None,
    ) -> RecognitionEvent:
        event = RecognitionEvent(
            id=str(uuid.uuid4()),
            channel_id=channel_id,
            track_id=track_id,
            plate=plate,
            confidence=confidence,
            country=country,
            bbox=bbox,
            direction=direction,
            image_url=image_url,
            meta=meta or {},
            created_at=time.time(),
        )
        self.events.append(event)
        return event

    def describe(self) -> dict[str, Any]:
        return {
            "storage": self.storage.as_dict(),
            "pending": len(self.events),
        }


@dataclass
class WebhookSubscription:
    id: str
    name: str
    url: str
    secret: str | None
    filters: dict[str, Any]
    is_active: bool
    created_at: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WebhookDelivery:
    id: str
    subscription_id: str
    event_id: str
    status: str
    attempts: int
    response_code: int | None
    response_body: str | None
    next_retry_at: float | None
    created_at: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WebhookService:
    max_attempts: int
    backoff_seconds: int
    signature_header: str
    subscriptions: dict[str, WebhookSubscription] = field(default_factory=dict)
    deliveries: list[WebhookDelivery] = field(default_factory=list)

    def register_subscription(
        self,
        name: str,
        url: str,
        secret: str | None,
        filters: dict[str, Any] | None = None,
    ) -> WebhookSubscription:
        subscription = WebhookSubscription(
            id=str(uuid.uuid4()),
            name=name,
            url=url,
            secret=secret,
            filters=filters or {},
            is_active=True,
            created_at=time.time(),
        )
        self.subscriptions[subscription.id] = subscription
        return subscription

    def sign_payload(self, payload: bytes, secret: str | None) -> str:
        if not secret:
            return ""
        return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

    def log_delivery(
        self,
        subscription_id: str,
        event_id: str,
        status: str,
        attempts: int,
        response_code: int | None = None,
        response_body: str | None = None,
        next_retry_at: float | None = None,
    ) -> WebhookDelivery:
        delivery = WebhookDelivery(
            id=str(uuid.uuid4()),
            subscription_id=subscription_id,
            event_id=event_id,
            status=status,
            attempts=attempts,
            response_code=response_code,
            response_body=response_body,
            next_retry_at=next_retry_at,
            created_at=time.time(),
        )
        self.deliveries.append(delivery)
        return delivery

    def describe(self) -> dict[str, Any]:
        return {
            "settings": {
                "max_attempts": self.max_attempts,
                "backoff_seconds": self.backoff_seconds,
                "signature_header": self.signature_header,
            },
            "subscriptions": [sub.as_dict() for sub in self.subscriptions.values()],
            "deliveries": [delivery.as_dict() for delivery in self.deliveries[-10:]],
        }


@dataclass
class AlarmRelay:
    id: str
    name: str
    channel_id: str | None
    mode: str
    delay_ms: int
    debounce_ms: int
    is_active: bool
    last_triggered_at: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AlarmRelayController:
    default_mode: str
    debounce_ms: int
    relays: dict[str, AlarmRelay] = field(default_factory=dict)

    def register_relay(
        self,
        *,
        name: str,
        channel_id: str | None,
        mode: str | None = None,
        delay_ms: int | None = None,
        debounce_ms: int | None = None,
    ) -> AlarmRelay:
        relay = AlarmRelay(
            id=str(uuid.uuid4()),
            name=name,
            channel_id=channel_id,
            mode=mode or self.default_mode,
            delay_ms=delay_ms or 0,
            debounce_ms=debounce_ms or self.debounce_ms,
            is_active=True,
        )
        self.relays[relay.id] = relay
        return relay

    def trigger(self, relay_id: str) -> AlarmRelay:
        if relay_id not in self.relays:
            raise KeyError(f"Relay {relay_id} not found")
        relay = self.relays[relay_id]
        relay.last_triggered_at = time.time()
        return relay

    def describe(self) -> dict[str, Any]:
        return {
            "defaults": {"mode": self.default_mode, "debounce_ms": self.debounce_ms},
            "relays": [relay.as_dict() for relay in self.relays.values()],
        }


_settings = get_settings()

event_storage = EventStorageConfig(
    bucket=_settings.s3_bucket,
    prefix=_settings.events_s3_prefix,
    image_ttl_days=_settings.events_image_ttl_days,
    clip_before_seconds=_settings.events_clip_before_seconds,
    clip_after_seconds=_settings.events_clip_after_seconds,
)

event_manager = EventManager(storage=event_storage)

webhook_service = WebhookService(
    max_attempts=_settings.webhook_max_attempts,
    backoff_seconds=_settings.webhook_backoff_seconds,
    signature_header=_settings.webhook_signature_header,
)

alarm_relay_controller = AlarmRelayController(
    default_mode=_settings.alarm_relay_default_mode,
    debounce_ms=_settings.alarm_relay_debounce_ms,
)

__all__ = [
    "EventManager",
    "RecognitionEvent",
    "event_manager",
    "WebhookSubscription",
    "WebhookDelivery",
    "WebhookService",
    "webhook_service",
    "AlarmRelay",
    "AlarmRelayController",
    "alarm_relay_controller",
    "EventStorageConfig",
    "event_storage",
]
