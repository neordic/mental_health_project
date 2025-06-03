from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ml_service.app.core.config import settings  # если config лежит в app/core/

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{settings.database_username}:{settings.database_password}"
    f"@{settings.database_hostname}:{settings.database_port}/{settings.database_name}?client_encoding=utf8"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency для FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
