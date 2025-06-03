import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from ml_service.app.services.auth_service import AuthService
from ml_service.app.schemas.auth import UserCreate
from ml_service.app.db.models.user import User

@pytest.fixture
def db_session_mock():
    return MagicMock()

@pytest.fixture
def auth_service(db_session_mock):
    return AuthService(db_session_mock)

@pytest.fixture
def user_data():
    return UserCreate(
        username="testuser",
        email="test@example.com",
        password="securepassword"
    )

def test_register_user_success(auth_service, user_data):
    
    user_mock = MagicMock(spec=User)
    user_mock.id = 1
    user_mock.email = user_data.email
    user_mock.username = user_data.username

    auth_service.repo.get_by_email = MagicMock(return_value=None)
    auth_service.repo.create = MagicMock(return_value=user_mock)
    auth_service.billing.credit_user = MagicMock()
    
    with patch("ml_service.app.services.auth_service.set_user_profile_cached") as cache_mock:
        result = auth_service.register_user(user_data)

    assert result.email == user_data.email
    auth_service.repo.create.assert_called_once()
    auth_service.billing.credit_user.assert_called_once_with(1, amount=10)
    cache_mock.assert_called_once()

def test_register_user_existing_email(auth_service, user_data):
    auth_service.repo.get_by_email = MagicMock(return_value=MagicMock())

    with pytest.raises(HTTPException) as exc_info:
        auth_service.register_user(user_data)

    assert exc_info.value.status_code == 400
    assert "already exists" in exc_info.value.detail

def test_authenticate_user_success(auth_service):
    user_mock = MagicMock(spec=User)
    user_mock.password_hash = "$2b$12$123456789012345678901u5MB.VLYnp.ZnC1DQUoDClmUeRW3MP3a"  # bcrypt hash for 'password'
    user_mock.email = "test@example.com"
    user_mock.id = 1

    auth_service.repo.get_by_email = MagicMock(return_value=user_mock)

    with patch("ml_service.app.services.auth_service.pwd_context.verify", return_value=True):
        result = auth_service.authenticate_user("test@example.com", "password")

    assert result.email == "test@example.com"

def test_authenticate_user_wrong_password(auth_service):
    user_mock = MagicMock(spec=User)
    user_mock.password_hash = "invalid_hash"

    auth_service.repo.get_by_email = MagicMock(return_value=user_mock)

    with patch("ml_service.app.services.auth_service.pwd_context.verify", return_value=False):
        with pytest.raises(HTTPException) as exc_info:
            auth_service.authenticate_user("test@example.com", "wrongpass")

    assert exc_info.value.status_code == 401
