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

    ingest_default_target_fps: int = Field(12, validation_alias="INGEST_DEFAULT_TARGET_FPS")
    ingest_reconnect_seconds: int = Field(3, validation_alias="INGEST_RECONNECT_SECONDS")
    ingest_decoder_priority: list[str] = Field(
        default_factory=lambda: ["nvdec", "vaapi", "cpu"], validation_alias="INGEST_DECODER_PRIORITY"
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


def get_settings() -> Settings:
    return Settings()
