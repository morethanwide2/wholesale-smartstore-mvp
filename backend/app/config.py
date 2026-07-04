from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/wholesale_mvp"

    default_margin_rate: float = 0.30
    default_channel_fee_rate: float = 0.08
    default_ad_cost_rate: float = 0.10
    default_price_round_unit: int = 100

    supplier_api_type: str = "mock"
    supplier_api_base_url: str = ""
    supplier_api_key: str = ""
    supplier_api_secret: str = ""

    smartstore_api_mode: str = "mock"
    smartstore_client_id: str = ""
    smartstore_client_secret: str = ""
    smartstore_seller_id: str = ""

    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
