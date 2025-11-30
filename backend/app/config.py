from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    # Gemini API
    GEMINI_API_KEY: str = ""

    # Application
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # CORS - comma-separated list of allowed origins
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    # JWT Authentication
    SECRET_KEY: str = "change-this-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Registration
    REFERRAL_CODE: str = ""

    @property
    def database_url(self):
        url = f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@db:5432/{self.POSTGRES_DB}"
        print(f"\nURL: {url}\n\n")
        return url


settings = Settings()
