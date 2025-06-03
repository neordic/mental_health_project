import json
from sqlalchemy.orm import Session
from typing import List
from celery.exceptions import TimeoutError
from ml_service.app.monitoring.metrics import age_hist
from ml_service.app.repositories.inference_repo import InferenceRepository
from ml_service.app.db.models.inference_task import InferenceTask
from ml_service.app.services.billing_service import BillingService
from ml_service.app.schemas.inference import InferenceTaskCreate
from ml_service.app.services.cache_service import (
    get_user_history_cached,
    set_user_history_cached
)
from ml_inference.tasks.run_inference import run_inference_task
from ml_service.app.core.logger import get_logger

logger = get_logger("inference")


class InferenceService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = InferenceRepository(db)
        self.billing = BillingService(db)

    def submit_task(self, user_id: int, task_data: InferenceTaskCreate) -> InferenceTask:
        try:
            self.billing.freeze(user_id, model_type=task_data.model_type)
            input_dict = task_data.input_data.dict()
            if "Age" in input_dict and input_dict["Age"] is not None:
                age_hist.observe(input_dict["Age"])

            async_result = run_inference_task.apply_async(args=[
                task_data.model_type,
                input_dict,
                user_id
            ])

            task = self.repo.create({
                "user_id": user_id,
                "model_type": task_data.model_type,
                "input_data": json.dumps(input_dict),
                "output_data": None,
                "status": "PENDING",
                "task_uuid": async_result.id
            })

            try:
                result = async_result.get(timeout=5)
                self.repo.update_output(task.id, json.dumps(result))
                logger.info(f"[SUBMIT] Immediate result stored for task_id={task.id}")
            except TimeoutError:
                logger.warning(f"[SUBMIT] Timeout waiting for async task_id={task.id}")

            return task
        except Exception:
            logger.exception(f"[SUBMIT] Failed to submit task for user_id={user_id}")
            raise

    def get_user_history(self, user_id: int) -> List[InferenceTask]:
        cached = get_user_history_cached(user_id)
        if cached:
            return cached

        tasks = self.repo.get_all_by_user_id(user_id)

        for task in tasks:
            try:
                task.input_data = json.loads(task.input_data)
            except Exception as e:
                logger.warning(f"[HISTORY] input_data JSON error (task_id={task.id}): {e}")
                task.input_data = {}

            if task.output_data:
                try:
                    task.output_data = json.loads(task.output_data)
                except Exception as e:
                    logger.warning(f"[HISTORY] output_data JSON error (task_id={task.id}): {e}")
                    task.output_data = {}

        try:
            set_user_history_cached(user_id, [
                {
                    "model_type": t.model_type,
                    "input_data": t.input_data,
                    "created_at": t.created_at.isoformat(),
                    "score": t.output_data.get("score") if isinstance(t.output_data, dict) else None,
                    "result": t.output_data.get("explanation") if isinstance(t.output_data, dict) else None,
                }
                for t in tasks
            ])
        except Exception as e:
            logger.warning(f"[HISTORY] Failed to cache history for user_id={user_id}: {e}")

        return tasks            

        



