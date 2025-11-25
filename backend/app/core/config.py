from pydantic import Field
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

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


def get_settings() -> Settings:
    return Settings()
