from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FlyRank Capstone Widget Platform"
    app_env: str = "development"
    debug: bool = True

    database_url: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    cors_origins: str = "http://localhost:8000,http://localhost:5500"

    geo_provider_a_url: str = ""
    geo_provider_a_api_key: str = ""

    geo_provider_b_url: str = ""
    geo_provider_b_api_key: str = ""

    webhook_url: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()