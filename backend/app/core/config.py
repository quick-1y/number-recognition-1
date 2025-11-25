from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = Field("development", validation_alias="APP_ENV")
    database_url: str = Field(..., validation_alias="DATABASE_URL")

    s3_endpoint: str = Field(..., validation_alias="S3_ENDPOINT")
    s3_region: str | None = Field(None, validation_alias="S3_REGION")
    s3_access_key: str = Field(..., validation_alias="S3_ACCESS_KEY")
    s3_secret_key: str = Field(..., validation_alias="S3_SECRET_KEY")
    s3_bucket: str = Field(..., validation_alias="S3_BUCKET")

    jwt_secret: str = Field(..., validation_alias="JWT_SECRET")
    jwt_expires_minutes: int = Field(60, validation_alias="JWT_EXPIRES_MINUTES")

    api_rate_limit: str | None = Field(None, validation_alias="API_RATE_LIMIT")
    log_level: str = Field("INFO", validation_alias="LOG_LEVEL")
    log_format: str = Field("json", validation_alias="LOG_FORMAT")
    sentry_dsn: str | None = Field(None, validation_alias="SENTRY_DSN")
    sentry_traces_sample_rate: float = Field(0.0, validation_alias="SENTRY_TRACES_SAMPLE_RATE")
    metrics_enabled: bool = Field(True, validation_alias="METRICS_ENABLED")
    metrics_namespace: str = Field("number_recognition", validation_alias="METRICS_NAMESPACE")

    ingest_default_target_fps: int = Field(12, validation_alias="INGEST_DEFAULT_TARGET_FPS")
    ingest_reconnect_seconds: int = Field(3, validation_alias="INGEST_RECONNECT_SECONDS")
    ingest_decoder_priority: list[str] = Field(
        default_factory=lambda: ["nvdec", "vaapi", "cpu"], validation_alias="INGEST_DECODER_PRIORITY"
    )

    detector_model: str = Field("yolov8", validation_alias="DETECTOR_MODEL")
    detector_device: str = Field("cuda", validation_alias="DETECTOR_DEVICE")
    detector_confidence_threshold: float = Field(0.25, validation_alias="DETECTOR_CONFIDENCE_THRESHOLD")
    detector_iou_threshold: float = Field(0.45, validation_alias="DETECTOR_IOU_THRESHOLD")
    detector_max_detections: int = Field(10, validation_alias="DETECTOR_MAX_DETECTIONS")
    detector_require_roi: bool = Field(False, validation_alias="DETECTOR_REQUIRE_ROI")

    tracker_type: str = Field("bytetrack", validation_alias="TRACKER_TYPE")
    tracker_max_age: int = Field(30, validation_alias="TRACKER_MAX_AGE")
    tracker_min_hits: int = Field(3, validation_alias="TRACKER_MIN_HITS")
    tracker_match_iou_threshold: float = Field(0.5, validation_alias="TRACKER_MATCH_IOU_THRESHOLD")

    ocr_engine: str = Field("easyocr", validation_alias="OCR_ENGINE")
    ocr_vote_frames: int = Field(3, validation_alias="OCR_VOTE_FRAMES")
    ocr_min_confidence: float = Field(0.6, validation_alias="OCR_MIN_CONFIDENCE")
    ocr_languages: list[str] = Field(default_factory=lambda: ["en", "ru"], validation_alias="OCR_LANGUAGES")

    postprocess_vote_by_char: bool = Field(True, validation_alias="POSTPROCESS_VOTE_BY_CHAR")
    postprocess_min_confidence: float = Field(0.55, validation_alias="POSTPROCESS_MIN_CONFIDENCE")
    postprocess_min_frames_for_event: int = Field(3, validation_alias="POSTPROCESS_MIN_FRAMES_FOR_EVENT")
    postprocess_anti_duplicate_seconds: int = Field(5, validation_alias="POSTPROCESS_ANTI_DUPLICATE_SECONDS")
    postprocess_country_templates: list[str] = Field(
        default_factory=lambda: ["ru", "by", "kz", "ua", "eu"], validation_alias="POSTPROCESS_COUNTRY_TEMPLATES"
    )

    events_s3_prefix: str = Field("events", validation_alias="EVENTS_S3_PREFIX")
    events_image_ttl_days: int = Field(90, validation_alias="EVENTS_IMAGE_TTL_DAYS")
    events_clip_before_seconds: int = Field(3, validation_alias="EVENTS_CLIP_BEFORE_SECONDS")
    events_clip_after_seconds: int = Field(3, validation_alias="EVENTS_CLIP_AFTER_SECONDS")

    webhook_max_attempts: int = Field(5, validation_alias="WEBHOOK_MAX_ATTEMPTS")
    webhook_backoff_seconds: int = Field(30, validation_alias="WEBHOOK_BACKOFF_SECONDS")
    webhook_signature_header: str = Field("X-Signature", validation_alias="WEBHOOK_SIGNATURE_HEADER")

    alarm_relay_default_mode: str = Field("toggle", validation_alias="ALARM_RELAY_DEFAULT_MODE")
    alarm_relay_debounce_ms: int = Field(200, validation_alias="ALARM_RELAY_DEBOUNCE_MS")

    rules_default_min_confidence: float = Field(0.6, validation_alias="RULES_DEFAULT_MIN_CONFIDENCE")
    rules_default_anti_flood_seconds: int = Field(10, validation_alias="RULES_DEFAULT_ANTI_FLOOD_SECONDS")
    rules_default_min_frames: int = Field(3, validation_alias="RULES_DEFAULT_MIN_FRAMES")
    rules_default_actions: list[str] = Field(
        default_factory=lambda: ["send_webhook", "annotate_ui"], validation_alias="RULES_DEFAULT_ACTIONS"
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

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


def get_settings() -> Settings:
    return Settings()
