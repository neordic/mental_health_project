from pydantic import BaseModel
from typing import Literal

class InferenceInput(BaseModel):
    Age: int
    Income: int
    Employment_Status: Literal["Unemployed", "Employed"]
    Education_Level: Literal["High School", "Bachelor's Degree", "Master's Degree", "PhD"]
    Marital_Status: Literal["Single", "Divorced", "Widowed", "Separated", "Married", "In a relationship"]
    Number_of_Children: int
    Family_History_of_Depression: Literal["Yes", "No"]
    History_of_Mental_Illness: Literal["Yes", "No"]
    Chronic_Medical_Conditions: Literal["Yes", "No"]
    Smoking_Status: Literal["Never", "Former", "Current"]
    Alcohol_Consumption: Literal["None", "Moderate", "High"]
    Physical_Activity_Level: Literal["Low", "Moderate", "Active"]
    Dietary_Habits: Literal["Poor", "Moderate", "Healthy"]
    Sleep_Patterns: Literal["Poor", "Fair", "Good"]
