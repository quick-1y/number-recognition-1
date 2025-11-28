"""Application settings loaded from environment variables.

The previous implementation relied on ``pydantic_settings.BaseSettings`` which
is not always available in user environments. This module now uses
``pydantic.BaseModel`` together with manual environment loading via
``python-dotenv`` so the application starts without optional extras while
preserving the existing validation logic.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


_ENV_FILES = (
    Path(__file__).resolve().parent.parent / ".env",
    Path(__file__).resolve().parent.parent.parent / ".env",
)


def _load_env_files() -> None:
    """Load environment variables from the known ``.env`` locations."""

    for env_path in _ENV_FILES:
        load_dotenv(env_path, override=False)


class Settings(BaseModel):
    """Pydantic model describing application configuration."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    app_env: str = Field("development", alias="APP_ENV")
    database_url: str = Field("sqlite:///./data/number_recognition.db", alias="DATABASE_URL")

    s3_endpoint: str = Field(..., alias="S3_ENDPOINT")
    s3_region: str | None = Field(None, alias="S3_REGION")
    s3_access_key: str = Field(..., alias="S3_ACCESS_KEY")
    s3_secret_key: str = Field(..., alias="S3_SECRET_KEY")
    s3_bucket: str = Field(..., alias="S3_BUCKET")

    jwt_secret: str = Field(..., alias="JWT_SECRET")
    jwt_expires_minutes: int = Field(60, alias="JWT_EXPIRES_MINUTES")

    api_rate_limit: str | None = Field(None, alias="API_RATE_LIMIT")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    log_format: str = Field("json", alias="LOG_FORMAT")
    sentry_dsn: str | None = Field(None, alias="SENTRY_DSN")
    sentry_traces_sample_rate: float = Field(0.0, alias="SENTRY_TRACES_SAMPLE_RATE")
    metrics_enabled: bool = Field(True, alias="METRICS_ENABLED")
    metrics_namespace: str = Field("number_recognition", alias="METRICS_NAMESPACE")

    ingest_default_target_fps: int = Field(12, alias="INGEST_DEFAULT_TARGET_FPS")
    ingest_reconnect_seconds: int = Field(3, alias="INGEST_RECONNECT_SECONDS")
    ingest_decoder_priority: list[str] | str = Field(
        default_factory=lambda: ["nvdec", "vaapi", "cpu"], alias="INGEST_DECODER_PRIORITY"
    )

    detector_model: str = Field("yolov8", alias="DETECTOR_MODEL")
    detector_device: str = Field("cuda", alias="DETECTOR_DEVICE")
    detector_confidence_threshold: float = Field(0.25, alias="DETECTOR_CONFIDENCE_THRESHOLD")
    detector_iou_threshold: float = Field(0.45, alias="DETECTOR_IOU_THRESHOLD")
    detector_max_detections: int = Field(10, alias="DETECTOR_MAX_DETECTIONS")
    detector_require_roi: bool = Field(False, alias="DETECTOR_REQUIRE_ROI")

    tracker_type: str = Field("bytetrack", alias="TRACKER_TYPE")
    tracker_max_age: int = Field(30, alias="TRACKER_MAX_AGE")
    tracker_min_hits: int = Field(3, alias="TRACKER_MIN_HITS")
    tracker_match_iou_threshold: float = Field(0.5, alias="TRACKER_MATCH_IOU_THRESHOLD")

    ocr_engine: str = Field("easyocr", alias="OCR_ENGINE")
    ocr_vote_frames: int = Field(3, alias="OCR_VOTE_FRAMES")
    ocr_min_confidence: float = Field(0.6, alias="OCR_MIN_CONFIDENCE")
    ocr_languages: list[str] | str = Field(default_factory=lambda: ["en", "ru"], alias="OCR_LANGUAGES")

    postprocess_vote_by_char: bool = Field(True, alias="POSTPROCESS_VOTE_BY_CHAR")
    postprocess_min_confidence: float = Field(0.55, alias="POSTPROCESS_MIN_CONFIDENCE")
    postprocess_min_frames_for_event: int = Field(3, alias="POSTPROCESS_MIN_FRAMES_FOR_EVENT")
    postprocess_anti_duplicate_seconds: int = Field(5, alias="POSTPROCESS_ANTI_DUPLICATE_SECONDS")
    postprocess_country_templates: list[str] | str = Field(
        default_factory=lambda: ["ru", "by", "kz", "ua", "eu"], alias="POSTPROCESS_COUNTRY_TEMPLATES"
    )

    events_s3_prefix: str = Field("events", alias="EVENTS_S3_PREFIX")
    events_image_ttl_days: int = Field(90, alias="EVENTS_IMAGE_TTL_DAYS")
    events_clip_before_seconds: int = Field(3, alias="EVENTS_CLIP_BEFORE_SECONDS")
    events_clip_after_seconds: int = Field(3, alias="EVENTS_CLIP_AFTER_SECONDS")

    webhook_max_attempts: int = Field(5, alias="WEBHOOK_MAX_ATTEMPTS")
    webhook_backoff_seconds: int = Field(30, alias="WEBHOOK_BACKOFF_SECONDS")
    webhook_signature_header: str = Field("X-Signature", alias="WEBHOOK_SIGNATURE_HEADER")

    alarm_relay_default_mode: str = Field("toggle", alias="ALARM_RELAY_DEFAULT_MODE")
    alarm_relay_debounce_ms: int = Field(200, alias="ALARM_RELAY_DEBOUNCE_MS")

    rules_default_min_confidence: float = Field(0.6, alias="RULES_DEFAULT_MIN_CONFIDENCE")
    rules_default_anti_flood_seconds: int = Field(10, alias="RULES_DEFAULT_ANTI_FLOOD_SECONDS")
    rules_default_min_frames: int = Field(3, alias="RULES_DEFAULT_MIN_FRAMES")
    rules_default_actions: list[str] | str = Field(
        default_factory=lambda: ["send_webhook", "annotate_ui"], alias="RULES_DEFAULT_ACTIONS"
    )

    @field_validator("ingest_decoder_priority", mode="before")
    @classmethod
    def parse_decoder_priority(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator(
        "log_format",
        "detector_model",
        "detector_device",
        "tracker_type",
        "ocr_engine",
        mode="before",
    )
    @classmethod
    def lowercase_strings(cls, value: str) -> str:
        return value.lower() if isinstance(value, str) else value

    @field_validator("ocr_languages", mode="before")
    @classmethod
    def parse_ocr_languages(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("postprocess_country_templates", mode="before")
    @classmethod
    def parse_country_templates(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip().lower() for item in value.split(",") if item.strip()]
        return [item.lower() for item in value]

    @field_validator("rules_default_actions", mode="before")
    @classmethod
    def parse_rule_actions(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("alarm_relay_default_mode", mode="before")
    @classmethod
    def normalize_alarm_mode(cls, value: str) -> str:
        return value.lower() if isinstance(value, str) else value


def _collect_env_values() -> dict[str, Any]:
    """Build a dictionary of values gathered from environment variables.

    Field aliases (e.g. ``APP_ENV``) are checked first. If a variable is not
    provided under its alias, the uppercase field name is used as a fallback so
    existing deployments keep working.
    """

    values: dict[str, Any] = {}
    for field_name, field in Settings.model_fields.items():
        for env_key in (field.alias, field_name.upper()):
            if env_key and env_key in os.environ:
                values[field_name] = os.environ[env_key]
                break
    return values


def get_settings() -> Settings:
    """Return validated application settings."""

    _load_env_files()
    try:
        return Settings.model_validate(_collect_env_values())
    except ValidationError as exc:  # pragma: no cover - raised during startup
        # Re-raise with the same message to avoid obscuring validation details
        raise exc

