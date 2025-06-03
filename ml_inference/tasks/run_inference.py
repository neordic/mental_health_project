from ml_inference.core.celery_app import celery_app
from ml_service.app.core.config import settings
from shared.schemas.inference import InferenceInput


from ml_inference.model.predict import run_inference_task as sync_task


from ml_service.app.db.session import SessionLocal
from ml_service.app.repositories.inference_repo import InferenceRepository
from datetime import datetime
from ml_service.app.services.billing_service import BillingService 
import json

from ml_inference.core.logger import get_logger

from ml_inference.monitoring.metrics import inference_duration_hist
import time  



logger = get_logger("ml_inference_task")


@celery_app.task(name="run_inference_task")
def run_inference_task(model_type: str, user_input: dict, user_id: int):
    logger.info(f"[START] Inference task started | model_type={model_type} | user_id={user_id}")
    
    input_obj = InferenceInput(**user_input)  
    start_time = time.time()
    result = sync_task(model_type, input_obj)
    duration = time.time() - start_time

    logger.info(f"[METRIC] Duration = {duration:.4f} sec — sending to Prometheus")
    logger.info(f"[METRIC DEBUG] Actual inference time = {duration:.6f} seconds")

    inference_duration_hist.observe(duration)

    logger.info(f"[INFERENCE] Inference result received | model_type={model_type} | result_type={type(result)}")
   

    db = SessionLocal()
    repo = InferenceRepository(db)
    billing = BillingService(db)

    try:

        task = repo.create({
            "user_id": user_id,
            "model_type": model_type,
            "input_data": json.dumps(user_input),  
            "output_data": json.dumps(result), 
            "status": "completed",
            "finished_at": datetime.utcnow()
        })
        logger.info(f"[DB] Inference task created in DB | task_id={task.id}")

        billing.finalize(user_id=user_id, task_id=task.id)
        logger.info(f"[BILLING] Finalized billing for user_id={user_id}, task_id={task.id}")
    except Exception as e:
        logger.exception(f"[ERROR] Failed to save task or finalize billing | user_id={user_id} | error={e}")
    finally:
        db.close()
    logger.info(f"[FINISH] Inference task completed | task_id={task.id}")
    return result

