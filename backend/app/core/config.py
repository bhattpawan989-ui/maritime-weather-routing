from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


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


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
