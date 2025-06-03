import pytest
from unittest.mock import patch, MagicMock
from ml_inference.tasks import run_inference

@pytest.fixture
def user_input_dict():
    return {
        "Age": 30,
        "Income": 50000,
        "Employment_Status": "Employed",
        "Education_Level": "Bachelor's Degree",
        "Marital_Status": "Single",
        "Number_of_Children": 1,
        "Family_History_of_Depression": "No",
        "History_of_Mental_Illness": "No",
        "Chronic_Medical_Conditions": "No",
        "Smoking_Status": "Never",
        "Alcohol_Consumption": "Moderate",
        "Physical_Activity_Level": "Active",
        "Dietary_Habits": "Healthy",
        "Sleep_Patterns": "Good"
    }

@patch("ml_inference.tasks.run_inference.sync_task")
@patch("ml_inference.tasks.run_inference.SessionLocal")
@patch("ml_inference.tasks.run_inference.InferenceRepository")
@patch("ml_inference.tasks.run_inference.BillingService")
@patch("ml_inference.tasks.run_inference.logger")
def test_run_inference_task(
    mock_logger,
    mock_billing_service,
    mock_repo_class,
    mock_session_local,
    mock_sync_task,
    user_input_dict
):
    mock_sync_task.return_value = {"score": 0.8, "explanation": "some explanation"}

    mock_db = MagicMock()
    mock_session_local.return_value = mock_db

    mock_repo = MagicMock()
    mock_repo.create.return_value = MagicMock(id=123)
    mock_repo_class.return_value = mock_repo

    mock_billing = MagicMock()
    mock_billing_service.return_value = mock_billing

    result = run_inference.run_inference_task("simple", user_input_dict, user_id=1)

    
    mock_sync_task.assert_called_once()
    
    
    mock_session_local.assert_called_once()
    mock_db.close.assert_called_once()

    
    mock_repo.create.assert_called_once()
    
    
    mock_billing.finalize.assert_called_once_with(user_id=1, task_id=123)

    assert result == {"score": 0.8, "explanation": "some explanation"}

    
    assert mock_logger.info.call_count > 0
