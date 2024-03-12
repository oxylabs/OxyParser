from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    OXYLABS_SCRAPER_HOST: str = "https://realtime.oxylabs.io/v1/queries"
    OXYLABS_SCRAPER_USER: str = "default"
    OXYLABS_SCRAPER_PASSWORD: str = "default"
    OXYLABS_SCRAPER_TIMEOUT: int = 120

    LLM_API_KEY: str = "default"
    LLM_MODEL: str = "gpt-3.5-turbo"
    LLM_API_BASE_URL: str | None = None

    MAX_TOKEN_COUNT: int = 3500

    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
