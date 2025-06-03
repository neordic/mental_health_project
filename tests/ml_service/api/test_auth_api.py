import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from ml_service.app.main import app
from ml_service.app.db.base import Base
from ml_service.app.db.session import get_db, SQLALCHEMY_DATABASE_URL
from ml_service.app.schemas.auth import UserCreate
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator


from ml_service.app.core.config import settings
DATABASE_URL = SQLALCHEMY_DATABASE_URL

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def db() -> Generator[Session, None, None]:

    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c


def test_register_and_login_and_me(client):
    
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpass123"
    }
    response = client.post("/auth/register", json=user_data)  
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]

    
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/auth/login", data=login_data)  
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)  
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]

