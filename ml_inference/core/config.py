from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    celery_broker_url: str
    model_dir: str

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
        "case_sensitive": False,
        "env_prefix": ""
    }

settings = Settings()
