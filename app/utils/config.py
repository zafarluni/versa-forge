from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Project Information (Static & Non-Sensitive)
    PROJECT_NAME: str = "Versa-Forge API"
    DESCRIPTION: str = "VersaForge – A modular platform for building custom GPT agents with multi-LLM support and RAG."
    VERSION: str = "1.0.0"

    # Debugging Settings
    RUN_MAIN: bool = False
    DEBUG_MODE: bool = False
    DEBUG_PORT: int = 5678

    # CORS Settings (Non-Sensitive)
    ALLOWED_ORIGINS: list[str] = ["http://localhost", "https://yourdomain.com"]

    # Database Settings (Sensitive - Must be set via `.env`)
    DATABASE_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_PORT: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    API_KEY: str

    # Docker Environment Indicator (Optional)
    RUNNING_IN_DOCKER: bool = False

    # postgresql+asyncpg://user:password@localhost/dbname
    @property
    def DATABASE_URL(self) -> str:  # pylint: disable=C0103:invalid-name
        """Constructs the database connection URL dynamically."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"
        extra = "ignore"  # Prevents unexpected environment variables from causing errors


# Instantiate settings from environment variables
settings = Settings()  # type: ignore
