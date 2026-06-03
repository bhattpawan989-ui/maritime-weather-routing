from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Maritime Weather Routing API"
    api_prefix: str = "/api/v1"
    debug: bool = False
    database_url: str = (
        "postgresql+psycopg2://postgres:postgres@localhost:5432/maritime_routing"
    )
    cors_origins: list[str] = ["http://localhost:3000"]
    fuel_price_usd_per_mt: float = 650.0
    co2_kg_per_mt_fuel: float = 3114.0
    default_canal_cost_usd: float = 0.0
    ml_artifacts_dir: Path = REPO_ROOT / "ml_artifacts"
    ml_enabled: bool = True
    ml_fallback_to_heuristic: bool = True

    @field_validator("ml_artifacts_dir", mode="before")
    @classmethod
    def parse_artifacts_dir(cls, value: object) -> Path:
        if isinstance(value, str):
            return Path(value)
        return value  # type: ignore[return-value]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
