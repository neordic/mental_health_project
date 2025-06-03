import pytest
from unittest.mock import patch, MagicMock
from ml_inference.model import predict
from shared.schemas.inference import InferenceInput
import pandas as pd

def make_user_input():
    return InferenceInput(
        Age=30,
        Income=50000,
        Employment_Status="Employed",
        Education_Level="Bachelor's Degree",
        Marital_Status="Single",
        Number_of_Children=1,
        Family_History_of_Depression="No",
        History_of_Mental_Illness="No",
        Chronic_Medical_Conditions="No",
        Smoking_Status="Never",
        Alcohol_Consumption="Moderate",
        Physical_Activity_Level="Active",
        Dietary_Habits="Healthy",
        Sleep_Patterns="Good"
    )

def test_preprocess_input(monkeypatch):
    class DummyScaler:
        def transform(self, df):
            return df  

    user_input = make_user_input()
    scaler = DummyScaler()

    df = predict.preprocess_input(user_input, scaler)
    assert isinstance(df, pd.DataFrame)
    assert "Age" in df.columns
    assert df.shape[0] == 1

@patch("ml_inference.model.predict.load_model_and_scaler")
def test_run_inference_task(mock_load_model_and_scaler):
    dummy_model = MagicMock()
    dummy_model.predict.return_value = [4.5]
    dummy_scaler = MagicMock()
    dummy_scaler.transform.side_effect = lambda x: x

    mock_load_model_and_scaler.return_value = (dummy_model, dummy_scaler)

    user_input = make_user_input()
    result = predict.run_inference_task("simple", user_input)

    assert "score" in result
    assert "explanation" in result
    dummy_model.predict.assert_called_once()
    dummy_scaler.transform.assert_called_once()

def test_interpret_score():
    assert predict.interpret_score(5) == "⚠️ High risk of depression — please consult a specialist."
    assert predict.interpret_score(3) == "🟠 Moderate risk — consider self-assessment or preventive steps."
    assert predict.interpret_score(2) == "🟢 Low risk — no immediate concern detected."
