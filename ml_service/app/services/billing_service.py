from sqlalchemy.orm import Session
from ml_service.app.repositories.billing_repo import BillingRepository
from ml_service.app.repositories.credits_repo import CreditsRepository
from ml_service.app.schemas.billing import BillingRecordCreate
from ml_service.app.db.models.user_credits import UserCredits
from ml_service.app.services.cache_service import (  
    get_user_credits_cached,
    set_user_credits_cached,
    invalidate_user_cache,
)
from ml_service.app.core.logger import get_logger

logger = get_logger("billing")

class BillingService:
    def __init__(self, db: Session):
        self.db = db
        self.billing_repo = BillingRepository(db)
        self.credits_repo = CreditsRepository(db)

    def credit_user(self, user_id: int, amount: int):
        """Начислить кредиты пользователю (например, при регистрации)"""
        credits = self.credits_repo.get_or_create(user_id)
        credits.available_credits += amount

        logger.info(f"[CREDIT] User {user_id}: +{amount} credits → available={credits.available_credits}")

        self.billing_repo.create(
            user_id=user_id,
            data=BillingRecordCreate(type="credit", amount=amount)
        )
        self.db.commit()

        set_user_credits_cached(user_id, {
            "available_credits": credits.available_credits,
            "frozen_credits": credits.frozen_credits
        }) #кэш

    def freeze(self, user_id: int, model_type: str, task_id: int | None = None):
        """Заморозить средства перед инференсом"""
        cost = self._get_model_cost(model_type)
        credits = self.credits_repo.get_by_user_id(user_id)

        if not credits or credits.available_credits < cost:
            raise ValueError("Insufficient funds")

        credits.available_credits -= cost

        logger.info(f"[FREEZE] User {user_id}: -{cost} credits for model={model_type}, task_id={task_id}")

        self.billing_repo.create(
            user_id=user_id,
            data=BillingRecordCreate(type="freeze", amount=-cost),
            task_id=task_id
        )
        self.db.commit()

        set_user_credits_cached(user_id, {
            "available_credits": credits.available_credits,
            "frozen_credits": credits.frozen_credits
        }) #кэш

    def finalize(self, user_id: int, task_id: int):
        """Подтвердить списание — оставляем всё как есть"""
        logger.info(f"[FINALIZE] User {user_id}: task_id={task_id} confirmed")

        self.billing_repo.create(
            user_id=user_id,
            data=BillingRecordCreate(type="finalize", amount=0),
            task_id=task_id
        )
        self.db.commit()
        invalidate_user_cache(user_id) #кэш

    def unfreeze(self, user_id: int, model_type: str, task_id: int):
        """Вернуть замороженные средства, если инференс не прошёл"""
        cost = self._get_model_cost(model_type)
        credits = self.credits_repo.get_by_user_id(user_id)
        credits.available_credits += cost

        logger.info(f"[UNFREEZE] User {user_id}: refund {cost} credits for task_id={task_id}, model={model_type}")

        self.billing_repo.create(
            user_id=user_id,
            data=BillingRecordCreate(type="unfreeze", amount=cost),
            task_id=task_id
        )
        self.db.commit()
        set_user_credits_cached(user_id, {
            "available_credits": credits.available_credits,
            "frozen_credits": credits.frozen_credits
        })

    def _get_model_cost(self, model_type: str) -> int:
        """Стоимость запуска модели по типу"""
        cost_map = {
            "simple": 1,
            "advanced": 3,
            "premium": 5,
        }
        return cost_map.get(model_type, 1) 
    def get_balance(self, user_id: int) -> int:
        credits = self.credits_repo.get_by_user_id(user_id)
        if credits:
            set_user_credits_cached(user_id, {
                "available_credits": credits.available_credits,
                "frozen_credits": credits.frozen_credits
            })
            return credits.available_credits
        logger.warning(f"[BALANCE] User {user_id}: no credits record found")
        return 0

