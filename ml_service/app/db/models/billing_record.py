from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from ml_service.app.db.session import Base
from sqlalchemy.orm import relationship


class BillingRecord(Base):
    __tablename__ = "billing_records"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    task_id = Column(Integer, ForeignKey("inference_tasks.id"), nullable=True)
    amount = Column(Integer)
    type = Column(String)  
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="billing_records")
   