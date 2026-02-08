from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Tripy"
    app_description: str = "Enterprise-grade travel assistant API powered by FastAPI and LangGraph."
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False
    reload: bool = False

    host: str = "0.0.0.0"
    port: int = 8000
    api_v1_prefix: str = "/api/v1"

    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    log_level: str = "INFO"
    log_json: bool = False

    database_url: str = "sqlite:///./data/app.db"
    auto_create_tables: bool = True

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    default_passenger_id: str = "3442 587242"

    openai_api_key: str = "EMPTY"
    openai_api_base: str = "http://localhost:6006/v1"
    llm_model: str = "Qwen-7B"
    llm_temperature: float = 0.2

    tavily_api_key: str | None = None
    tavily_max_results: int = 2

    embeddings_api_key: str | None = None
    embeddings_api_base: str | None = None

    graph_enabled: bool = True
    default_user_role: str = "traveler"

    otel_enabled: bool = False
    otel_service_name: str = "tripy-api"
    otel_exporter_otlp_endpoint: str | None = None
    otel_exporter_otlp_headers: str | None = None
    otel_exporter_console: bool = True
    otel_log_correlation: bool = True

    bootstrap_admin_username: str = "admin"
    bootstrap_admin_password: str = "ChangeMe123!"
    bootstrap_admin_passenger_id: str = "3442 587242"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return []
            if stripped.startswith("["):
                import json

                parsed = json.loads(stripped)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            return [item.strip() for item in stripped.split(",") if item.strip()]
        return ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
