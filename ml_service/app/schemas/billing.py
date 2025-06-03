from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime


class BillingRecordCreate(BaseModel):
    type: Literal["freeze", "finalize", "unfreeze", "credit"]
    amount: int


class BillingRecordRead(BillingRecordCreate):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class BillingRecordPublic(BaseModel):
    timestamp: datetime
    type: Literal["freeze", "finalize", "unfreeze", "credit"]
    amount: int
    task_id: Optional[int]

    class Config:
        from_attributes = True        

class BillingHistoryItem(BaseModel):
    timestamp: datetime
    type: Literal["freeze", "finalize", "unfreeze", "credit"]
    amount: int
    model_type: Optional[str] = None
    explanation: Optional[str] = None

    class Config:
        from_attributes = True
