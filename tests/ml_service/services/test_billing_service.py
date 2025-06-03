import pytest
from unittest.mock import MagicMock, patch
from ml_service.app.services.billing_service import BillingService
from ml_service.app.schemas.billing import BillingRecordCreate

@pytest.fixture
def db_mock():
    return MagicMock()

@pytest.fixture
def billing_service(db_mock):
    service = BillingService(db_mock)
    service.credits_repo = MagicMock()
    service.billing_repo = MagicMock()
    return service

def test_credit_user_success(billing_service):
    user_id = 1
    amount = 10
    credits_mock = MagicMock()
    credits_mock.available_credits = 5
    credits_mock.frozen_credits = 0

    billing_service.credits_repo.get_or_create.return_value = credits_mock

    with patch("ml_service.app.services.billing_service.set_user_credits_cached") as cache_mock:
        billing_service.credit_user(user_id, amount)

    assert credits_mock.available_credits == 15
    billing_service.billing_repo.create.assert_called_once_with(
        user_id=user_id,
        data=BillingRecordCreate(type="credit", amount=amount)
    )
    billing_service.db.commit.assert_called_once()
    cache_mock.assert_called_once()

def test_freeze_success(billing_service):
    user_id = 1
    model_type = "advanced"
    task_id = 42
    credits_mock = MagicMock()
    credits_mock.available_credits = 10
    credits_mock.frozen_credits = 0

    billing_service.credits_repo.get_by_user_id.return_value = credits_mock

    with patch("ml_service.app.services.billing_service.set_user_credits_cached") as cache_mock:
        billing_service.freeze(user_id, model_type, task_id)

    assert credits_mock.available_credits == 7
    billing_service.billing_repo.create.assert_called_once()
    billing_service.db.commit.assert_called_once()
    cache_mock.assert_called_once()

def test_freeze_insufficient_funds(billing_service):
    user_id = 1
    model_type = "premium"
    billing_service.credits_repo.get_by_user_id.return_value = MagicMock(available_credits=3)

    with pytest.raises(ValueError, match="Insufficient funds"):
        billing_service.freeze(user_id, model_type, task_id=99)

def test_unfreeze_success(billing_service):
    user_id = 1
    model_type = "premium"
    task_id = 101
    credits_mock = MagicMock()
    credits_mock.available_credits = 2
    credits_mock.frozen_credits = 0

    billing_service.credits_repo.get_by_user_id.return_value = credits_mock

    with patch("ml_service.app.services.billing_service.set_user_credits_cached") as cache_mock:
        billing_service.unfreeze(user_id, model_type, task_id)

    assert credits_mock.available_credits == 7
    billing_service.billing_repo.create.assert_called_once()
    billing_service.db.commit.assert_called_once()
    cache_mock.assert_called_once()

def test_finalize_calls_create_and_commit(billing_service):
    user_id = 2
    task_id = 99

    with patch("ml_service.app.services.billing_service.invalidate_user_cache") as invalidate_mock:
        billing_service.finalize(user_id, task_id)

    billing_service.billing_repo.create.assert_called_once_with(
        user_id=user_id,
        data=BillingRecordCreate(type="finalize", amount=0),
        task_id=task_id
    )
    billing_service.db.commit.assert_called_once()
    invalidate_mock.assert_called_once_with(user_id)

def test_get_balance_existing_user(billing_service):
    user_id = 3
    credits_mock = MagicMock(available_credits=8, frozen_credits=1)
    billing_service.credits_repo.get_by_user_id.return_value = credits_mock

    with patch("ml_service.app.services.billing_service.set_user_credits_cached") as cache_mock:
        balance = billing_service.get_balance(user_id)

    assert balance == 8
    cache_mock.assert_called_once()

def test_get_balance_no_user(billing_service):
    user_id = 999
    billing_service.credits_repo.get_by_user_id.return_value = None

    balance = billing_service.get_balance(user_id)

    assert balance == 0
