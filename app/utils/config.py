# app/utils/config.py
from functools import lru_cache
from typing import Optional, Sequence

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    host: str = Field(alias="DATABASE_HOST")
    port: int = Field(alias="DATABASE_PORT")
    user: str = Field(alias="POSTGRES_USER")
    password: str = Field(alias="POSTGRES_PASSWORD")
    name: str = Field(alias="POSTGRES_DB")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def url(self) -> str:
        return f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class SecuritySettings(BaseSettings):
    secret_key: str = Field(alias="SECRET_KEY")
    algorithm: str = Field("HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    api_key: Optional[str] = Field(None, alias="API_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class AppSettings(BaseSettings):
    # Project metadata
    project_name: str = "Versa-Forge API"
    description: str = "VersaForge – A modular platform for building custom GPT agents with multi-LLM support and RAG."
    version: str = "1.0.0"

    # Debugging flags
    run_main: bool = Field(False, alias="RUN_MAIN")
    debug_mode: bool = Field(False, alias="DEBUG_MODE")
    debug_port: int = Field(5678, alias="DEBUG_PORT")

    # CORS origins – covariant Sequence of AnyHttpUrl
    allowed_origins: Sequence[AnyHttpUrl] = Field(
        default_factory=lambda: [
            AnyHttpUrl("http://localhost"),
            AnyHttpUrl("https://yourdomain.com"),
        ],
        alias="ALLOWED_ORIGINS",
    )

    # Docker / environment flag
    running_in_docker: bool = Field(False, alias="RUNNING_IN_DOCKER")

    # Nested config classes, constructed immediately
    database: DatabaseSettings = Field(default=DatabaseSettings())  # type: ignore
    security: SecuritySettings = Field(default=SecuritySettings())  # type: ignore

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @classmethod
    def validate_allowed_origins(cls, v: Sequence[AnyHttpUrl]) -> Sequence[AnyHttpUrl]:
        if not v:
            raise ValueError("allowed_origins must contain at least one URL")
        return v


@lru_cache()
def get_settings() -> AppSettings:
    """
    Returns a cached AppSettings instance for FastAPI DI.
    """
    return AppSettings()  # type: ignore
