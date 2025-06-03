from sqlalchemy.orm import Session
from ml_service.app.db.models.user_credits import UserCredits

from ml_service.app.core.logger import get_logger 

logger = get_logger("credits_repo")

class CreditsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int) -> UserCredits | None:
        credits = self.db.query(UserCredits).filter_by(user_id=user_id).first()
        if credits:
            logger.info(f"[GET] Found credits for user_id={user_id}: available={credits.available_credits}, frozen={credits.frozen_credits}")
        else:
            logger.info(f"[GET] No credits found for user_id={user_id}")
        return credits

    def get_or_create(self, user_id: int) -> UserCredits:
        credits = self.get_by_user_id(user_id)
        if not credits:
            credits = UserCredits(user_id=user_id, available_credits=0)
            self.db.add(credits)
            self.db.commit()
            self.db.refresh(credits)
            logger.info(f"[CREATE] Created new credits for user_id={user_id}")
        else:
            logger.info(f"[EXISTING] Returning existing credits for user_id={user_id}")
        return credits
