from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from ml_service.app.db.session import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    credits = relationship("UserCredits", back_populates="user", uselist=False)
    tasks = relationship("InferenceTask", back_populates="user")
    billing_records = relationship("BillingRecord", back_populates="user")


