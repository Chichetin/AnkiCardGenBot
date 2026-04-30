from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    telegram_token: str
    gigachat_credentials: str
    anki_url: str = "http://localhost:8765"

    model_config = {"env_file": ".env"}


settings = Settings()
