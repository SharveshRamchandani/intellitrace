from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # ── App ──────────────────────────────────────────────────────────────────
    APP_NAME: str = "IntelliTrace SCF Sentinel"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # ── Database ─────────────────────────────────────────────────────────────
    POSTGRES_USER: str = "intellitrace"
    POSTGRES_PASSWORD: str = "intellitrace_secret"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "intellitrace"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def DATABASE_URL_SYNC(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # ── Redis / Celery ───────────────────────────────────────────────────────
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def CELERY_BROKER_URL(self) -> str:
        return self.REDIS_URL

    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return self.REDIS_URL

    # ── Fraud Engine ─────────────────────────────────────────────────────────
    REVENUE_RATIO_THRESHOLD: float = 2.0        # flag if total_financed / revenue > this
    CASCADE_DEPTH_THRESHOLD: int = 3             # flag if supply chain depth > this
    VELOCITY_WINDOW_DAYS: int = 30              # window for velocity anomaly detection
    VELOCITY_THRESHOLD: int = 20               # invoices per window before flagging
    HIGH_RISK_SCORE_THRESHOLD: float = 70.0    # score >= this → high risk alert

    # ── CORS ─────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",   # Vite dev
        "http://localhost:3000",
        "http://localhost:8080",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
