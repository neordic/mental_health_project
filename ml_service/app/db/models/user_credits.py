from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from ml_service.app.db.session import Base


class UserCredits(Base):
    __tablename__ = "user_credits"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    available_credits = Column(Integer, default=5)
    frozen_credits = Column(Integer, default=0)

    user = relationship("User", back_populates="credits")
