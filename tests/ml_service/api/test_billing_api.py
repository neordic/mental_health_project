import pytest
from fastapi.testclient import TestClient
from ml_service.app.main import app
from ml_service.app.db.session import get_db, SQLALCHEMY_DATABASE_URL
from ml_service.app.db.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator
from sqlalchemy.orm import Session

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

@pytest.fixture(scope="module")
def auth_token(client):
    user_data = {
        "username": "billuser",
        "email": "billuser@example.com",
        "password": "secret123"
    }
    # Register
    client.post("/auth/register", json=user_data)
    # Login
    response = client.post("/auth/login", data={
        "username": user_data["email"],
        "password": user_data["password"]
    })
    return response.json()["access_token"]

def test_get_balance(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/billing/balance", headers=headers)
    assert response.status_code == 200
    assert "balance" in response.json()
    assert response.json()["balance"] == 10  # При регистрации начисляется 10

def test_get_billing_history(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/billing/history", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["type"] == "credit"
    assert data[0]["amount"] == 10

def test_get_billing_history_detailed(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/billing/history_detailed", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert "explanation" in data[0]
    assert "Credits added" in data[0]["explanation"]
