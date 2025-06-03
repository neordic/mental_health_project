import pytest
from fastapi.testclient import TestClient
from ml_service.app.main import app
from ml_service.app.db.base import Base
from ml_service.app.db.session import SQLALCHEMY_DATABASE_URL, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator

from ml_service.app.core.security import create_access_token

DATABASE_URL = SQLALCHEMY_DATABASE_URL
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def db() -> Generator:
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


def register_user(client):
    user_data = {
        "username": "inferuser",
        "email": "inferuser@example.com",
        "password": "strongpass"
    }
    client.post("/auth/register", json=user_data)
    return user_data


def get_token(client, email, password):
    response = client.post("/auth/login", data={"username": email, "password": password})
    return response.json()["access_token"]


def test_submit_and_get_history(client):
    user_data = register_user(client)
    token = get_token(client, user_data["email"], user_data["password"])
    headers = {"Authorization": f"Bearer {token}"}

    task = {
        "model_type": "simple",
        "input_data": {
            "Age": 30,
            "Income": 40000,
            "Employment_Status": "Employed",
            "Education_Level": "Bachelor's Degree",
            "Marital_Status": "Single",
            "Number_of_Children": 0,
            "Family_History_of_Depression": "No",
            "History_of_Mental_Illness": "No",
            "Chronic_Medical_Conditions": "No",
            "Smoking_Status": "Never",
            "Alcohol_Consumption": "Moderate",
            "Physical_Activity_Level": "Moderate",
            "Dietary_Habits": "Healthy",
            "Sleep_Patterns": "Good"
        }
    }

    # Submit
    submit_response = client.post("/inference/submit", json=task, headers=headers)
    assert submit_response.status_code == 200
    assert "result" in submit_response.json()

    # History
    history_response = client.get("/inference/history", headers=headers)
    assert history_response.status_code == 200
    assert isinstance(history_response.json(), list)
    assert len(history_response.json()) >= 1
