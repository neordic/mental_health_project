import pandas as pd
from .load_model import load_model_and_scaler
from shared.schemas.inference import InferenceInput

from ml_inference.core.logger import get_logger

logger = get_logger("predict")

def preprocess_input(user_input: InferenceInput, scaler):
    try:
        employment_map = {"Unemployed": 0, "Employed": 1}
        marital_map = {
            'Single': 0, 'Divorced': 0, 'Widowed': 0, 'Separated': 0,
            'Married': 1, 'In a relationship': 1
        }

        df = pd.DataFrame([{
            "Age": user_input.Age,
            "Employment Status": employment_map[user_input.Employment_Status],
            "Income": user_input.Income,
            "Education Level_Bachelor's Degree": user_input.Education_Level == "Bachelor's Degree",
            "Education Level_High School": user_input.Education_Level == "High School",
            "Education Level_Master's Degree": user_input.Education_Level == "Master's Degree",
            "Education Level_PhD": user_input.Education_Level == "PhD",
            "Social_Support": marital_map[user_input.Marital_Status] + user_input.Number_of_Children,
            "family_personal_health": (
                int(user_input.Family_History_of_Depression == "Yes") +
                int(user_input.History_of_Mental_Illness == "Yes") +
                int(user_input.Chronic_Medical_Conditions == "Yes")
            ),
            "personal_burden": (
                int(user_input.Smoking_Status == "Current") +
                int(user_input.Alcohol_Consumption == "High") -
                int(user_input.Physical_Activity_Level == "Active") -
                int(user_input.Dietary_Habits == "Healthy") -
                int(user_input.Sleep_Patterns == "Good")
            )
        }])

        df[["Age", "Income"]] = scaler.transform(df[["Age", "Income"]])
        logger.info("[PREPROCESS] Input transformed for inference")
        return df
    except Exception:
        logger.exception("[PREPROCESS][ERROR] Failed to preprocess user input")
        raise



def interpret_score(score: float) -> str:
    if score >= 5:
        return "⚠️ High risk of depression — please consult a specialist."
    elif score >= 3:
        return "🟠 Moderate risk — consider self-assessment or preventive steps."
    else:
        return "🟢 Low risk — no immediate concern detected."
    
def run_inference_task(model_type: str, user_input: dict) -> dict:
    try:    
        model, scaler = load_model_and_scaler(model_type)
        logger.info(f"[INFERENCE] Model and scaler loaded for: {model_type}")
        
        df = preprocess_input(user_input, scaler)
        prediction = model.predict(df)[0]
        logger.info(f"[INFERENCE] Prediction made: {prediction}")

        explanation = interpret_score(prediction)
        logger.info(f"[INFERENCE] Interpretation: {explanation}")

        return {
            "score": float(prediction),
            "explanation": explanation
        }
    except Exception:
        logger.exception("[INFERENCE][ERROR] Failed to run inference")
        raise    