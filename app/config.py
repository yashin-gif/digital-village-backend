from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_SECRET_KEY = "change-this-secret-key"


class Settings(BaseSettings):
    app_name: str = "Digital Village API"
    app_version: str = "1.0.0"
    # প্রোডাকশনে DEBUG=false থাকবে (ডিফল্টও false)
    debug: bool = False

    database_url: str = "sqlite:///./digital_village.db"

    secret_key: str = DEFAULT_SECRET_KEY

    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30

    # ফ্রন্টএন্ডের যে ঠিকানাগুলো API ডাকতে পারবে
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
