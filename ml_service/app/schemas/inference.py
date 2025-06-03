from pydantic import BaseModel
from datetime import datetime
from typing import Literal, Dict, Any, Optional
from shared.schemas.inference import InferenceInput

# 🟢 Запрос от пользователя
class InferenceTaskCreate(BaseModel):
    model_type: Literal["simple", "advanced", "premium"]
    input_data: InferenceInput
    


class InferenceTaskRead(InferenceTaskCreate):
    id: int
    model_type: str
    input_data: Dict[str, Any]
    status: str
    task_uuid: str
    created_at: datetime
    finished_at: Optional[datetime]

    class Config:
        from_attributes = True  

class InferenceResult(BaseModel):
    result: str
        


class InferenceHistoryPublic(BaseModel):
    model_type: str
    created_at: datetime
    input_data: Dict[str, Any]
    result: Optional[str]
    score: Optional[float]
