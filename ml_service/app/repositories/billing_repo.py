from sqlalchemy.orm import Session
from ml_service.app.db.models.billing_record import BillingRecord
from ml_service.app.schemas.billing import BillingRecordCreate

from ml_service.app.core.logger import get_logger

logger = get_logger("billing_repo")

class BillingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, data: BillingRecordCreate, task_id: int | None = None) -> BillingRecord:
        billing = BillingRecord(
            user_id=user_id,
            task_id=task_id,
            amount=data.amount,
            type=data.type
        )
        self.db.add(billing)
        self.db.commit()
        self.db.refresh(billing)

        logger.info(f"[CREATE] BillingRecord: user_id={user_id}, type={data.type}, amount={data.amount}, task_id={task_id}")

        return billing

    def get_by_user(self, user_id: int) -> list[BillingRecord]:
        logger.info(f"[GET] Billing records for user_id={user_id}")
        return (
            self.db.query(BillingRecord)
            .filter(BillingRecord.user_id == user_id)
            .order_by(BillingRecord.timestamp.desc())
            .all()
        )
