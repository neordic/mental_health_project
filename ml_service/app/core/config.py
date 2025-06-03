from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_name: str
    database_username: str
    database_password: str
    redis_host: str
    redis_port: int

    model_dir: str = ""  
    celery_broker_url: str = ""

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "env_prefix": ""
    }

    

settings = Settings()