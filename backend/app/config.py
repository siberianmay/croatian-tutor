from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql+asyncpg://croatian:tutor_local@localhost:5432/croatian_tutor"

    # Gemini API
    gemini_api_key: str = ""

    # Application
    debug: bool = True
    api_v1_prefix: str = "/api/v1"


settings = Settings()
