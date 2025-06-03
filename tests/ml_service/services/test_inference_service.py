import pytest
from unittest.mock import MagicMock, patch
from ml_service.app.services.inference_service import InferenceService
from ml_service.app.schemas.inference import InferenceTaskCreate
from shared.schemas.inference import InferenceInput
from celery.exceptions import TimeoutError


@pytest.fixture
def db_mock():
    return MagicMock()

@pytest.fixture
def service(db_mock):
    service = InferenceService(db_mock)
    service.repo = MagicMock()
    service.billing = MagicMock()
    return service

@pytest.fixture
def task_data():
    return InferenceTaskCreate(
        model_type="simple",
        input_data=InferenceInput(
            Age=30,
            Income=50000,
            Employment_Status="Employed",
            Education_Level="Bachelor's Degree",
            Marital_Status="Single",
            Number_of_Children=0,
            Family_History_of_Depression="No",
            History_of_Mental_Illness="No",
            Chronic_Medical_Conditions="No",
            Smoking_Status="Never",
            Alcohol_Consumption="Moderate",
            Physical_Activity_Level="Active",
            Dietary_Habits="Healthy",
            Sleep_Patterns="Good"
        )
    )


def test_submit_task_success(service, task_data):
    mock_result = {"score": 0.75, "explanation": "text"}
    mock_async_result = MagicMock()
    mock_async_result.id = "task-uuid"
    mock_async_result.get.return_value = mock_result

    service.repo.create.return_value = MagicMock(id=1)
    service.repo.update_output = MagicMock()

    with patch("ml_service.app.services.inference_service.run_inference_task.apply_async", return_value=mock_async_result):
        task = service.submit_task(user_id=1, task_data=task_data)

    service.billing.freeze.assert_called_once_with(1, model_type="simple")
    service.repo.create.assert_called_once()
    service.repo.update_output.assert_called_once()
    assert task.id == 1

def test_submit_task_timeout(service, task_data):
    mock_async_result = MagicMock()
    mock_async_result.id = "uuid-timeout"
    mock_async_result.get.side_effect = TimeoutError()

    task_mock = MagicMock(id=10)
    service.repo.create.return_value = task_mock
    service.repo.update_output = MagicMock()

    with patch("ml_service.app.services.inference_service.run_inference_task.apply_async", return_value=mock_async_result):
        task = service.submit_task(user_id=99, task_data=task_data)

    assert task.id == 10
    service.repo.update_output.assert_not_called()


def test_get_user_history_cached(service):
    with patch("ml_service.app.services.inference_service.get_user_history_cached", return_value=[{"model_type": "simple"}]):
        result = service.get_user_history(user_id=1)
        assert isinstance(result, list)
        assert result[0]["model_type"] == "simple"

def test_get_user_history_fallback_to_db(service):
    task_mock = MagicMock()
    task_mock.id = 1
    task_mock.model_type = "simple"
    task_mock.input_data = '{"Age": 30}'
    task_mock.output_data = '{"score": 0.9, "explanation": "fine"}'
    task_mock.created_at.isoformat.return_value = "2024-01-01T00:00:00"

    service.repo.get_all_by_user_id.return_value = [task_mock]

    with patch("ml_service.app.services.inference_service.get_user_history_cached", return_value=None):
        with patch("ml_service.app.services.inference_service.set_user_history_cached") as cache_mock:
            result = service.get_user_history(user_id=2)

    assert isinstance(result, list)
    assert result[0].model_type == "simple"
    cache_mock.assert_called_once()
