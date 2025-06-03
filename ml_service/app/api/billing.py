from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ml_service.app.services.billing_service import BillingService
from ml_service.app.core.security import get_current_user
from ml_service.app.db.session import get_db
from ml_service.app.db.models.user import User
from ml_service.app.schemas.billing import BillingRecordPublic
from ml_service.app.services.cache_service import get_user_credits_cached, set_user_credits_cached
from ml_service.app.db.models.inference_task import InferenceTask
from ml_service.app.schemas.billing import BillingHistoryItem
from ml_service.app.repositories.billing_repo import BillingRepository
from ml_service.app.core.logger import get_logger
from ml_service.app.schemas.billing import BillingRecordPublic
from typing import List


router = APIRouter(prefix="/billing", tags=["Billing"])
logger = get_logger("api.billing")


@router.get("/balance")
def get_balance(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    try:
        
        cached = get_user_credits_cached(user.id)
        if cached:
            logger.info(f"[BALANCE] Cache HIT: user_id={user.id}")
            return {"balance": cached["available_credits"]}
        
        
        logger.info(f"[BALANCE] Cache MISS: user_id={user.id}")
        service = BillingService(db)
        balance = service.get_balance(user.id)

        set_user_credits_cached(user.id, {
            "available_credits": balance,
            "frozen_credits": 0  
        })
        return {"balance": balance}
    except Exception:
        logger.exception(f"[BALANCE] Failed to get balance for user_id={user.id}")
        raise
    

@router.get("/history", response_model=List[BillingRecordPublic])
def get_billing_history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    try:
        service = BillingService(db)
        records = service.billing_repo.get_by_user(user.id)
        logger.info(f"[HISTORY] {len(records)} records for user_id={user.id}")
        return records
    except Exception:
        logger.exception(f"[HISTORY] Failed to fetch billing records for user_id={user.id}")
        raise

@router.get("/history_detailed", response_model=List[BillingHistoryItem])
def get_billing_history_detailed(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    try:
        repo = BillingRepository(db)
        records = repo.get_by_user(user.id)

        task_map = {
            t.id: t.model_type
            for t in db.query(InferenceTask).filter(InferenceTask.user_id == user.id).all()
        }

        result = []

        for r in records:
            model_type = task_map.get(r.task_id)
            explanation = {
                "freeze": f"Funds frozen for model {model_type}" if model_type else "Funds frozen",
                "finalize": f"Final deduction for model {model_type}" if model_type else "Final deduction",
                "unfreeze": "Refund of frozen funds",
                "credit": "Credits added"
            }.get(r.type, "Transaction")

            result.append(BillingHistoryItem(
                timestamp=r.timestamp,
                type=r.type,
                amount=r.amount,
                model_type=model_type,
                explanation=explanation
            ))

        return result
    except Exception:
        logger.exception(f"[HISTORY_DETAILED] Failed for user_id={user.id}")
        raise




