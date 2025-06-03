from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ml_service.app.db.session import Base
from uuid import uuid4

from .user import User

class InferenceTask(Base):
    __tablename__ = "inference_tasks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    model_type = Column(String, nullable=False) 
    input_data = Column(String, nullable=False)
    output_data = Column(Text, nullable=True)
    status = Column(String, default="PENDING")
    
    task_uuid = Column(String, unique=True, default=lambda: str(uuid4()), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="tasks")
