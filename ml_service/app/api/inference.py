from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ml_service.app.db.session import get_db
from ml_service.app.schemas.inference import InferenceTaskCreate, InferenceTaskRead, InferenceResult, InferenceHistoryPublic
from ml_service.app.services.inference_service import InferenceService
from ml_service.app.core.security import get_current_user
from ml_service.app.db.models.user import User
from typing import List
import json
from time import sleep
from ml_service.app.repositories.inference_repo import InferenceRepository
from ml_service.app.db.models.inference_task import InferenceTask
from sqlalchemy.orm import sessionmaker
from ml_service.app.db.session import engine

from ml_service.app.core.logger import get_logger

router = APIRouter()
logger = get_logger("api.inference")

@router.post("/submit", response_model=InferenceResult)
def submit_inference_task(
    task_data: InferenceTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        service = InferenceService(db)
        task = service.submit_task(current_user.id, task_data)

        if task.output_data:
            try:
                data = json.loads(task.output_data)
                explanation = data.get("explanation", "No explanation available")
                logger.info(f"[SUBMIT] user_id={current_user.id} task_id={task.id} → success")
                return InferenceResult(result=explanation)
            except Exception:
                logger.warning(f"[SUBMIT] user_id={current_user.id} task_id={task.id} → corrupted output")
                return InferenceResult(result="Corrupted output")
        logger.info(f"[SUBMIT] user_id={current_user.id} task_id={task.id} → timeout")            
        return InferenceResult(result="Timeout: task not completed")

    except Exception:
        logger.exception(f"[SUBMIT] Failed for user_id={current_user.id}")
        raise

@router.get("/history", response_model=List[InferenceHistoryPublic])
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = InferenceService(db)
    tasks = service.get_user_history(current_user.id)

    response = []
    for task in tasks:
        
        if isinstance(task, dict):
            input_data = task.get("input_data", {})
            output_data = {
                "score": task.get("score"),
                "explanation": task.get("result")
            }
            response.append({
                "model_type": task.get("model_type"),
                "input_data": input_data,
                "created_at": task.get("created_at"),
                "score": output_data["score"],
                "result": output_data["explanation"]
            })
        else:
            
            try:
                input_data = (
                    task.input_data if isinstance(task.input_data, dict)
                    else json.loads(task.input_data or "{}")
                )
            except json.JSONDecodeError:
                input_data = {}

            try:
                output_data = (
                    task.output_data if isinstance(task.output_data, dict)
                    else json.loads(task.output_data or "{}")
                )
            except json.JSONDecodeError:
                output_data = {}

            response.append({
                "model_type": task.model_type,
                "input_data": input_data,
                "created_at": task.created_at,
                "score": output_data.get("score"),
                "result": output_data.get("explanation")
            })

    return response
 



