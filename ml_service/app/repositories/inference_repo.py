from sqlalchemy.orm import Session
from ml_service.app.db.models.inference_task import InferenceTask
from typing import List
from typing import Optional
import json

from ml_service.app.core.logger import get_logger  
logger = get_logger("inference_repo")

class InferenceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, task_data: dict) -> InferenceTask:
        task = InferenceTask(**task_data)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        logger.info(f"[CREATE] New inference task created: id={task.id}, user_id={task.user_id}, model={task.model_type}")
        return task

    def get_all_by_user_id(self, user_id: int) -> List[InferenceTask]:
        tasks = self.db.query(InferenceTask).filter_by(user_id=user_id).all()
        logger.info(f"[GET ALL] Retrieved {len(tasks)} tasks for user_id={user_id}")
        return tasks
    
    def get_by_id_and_user(self, task_id: int, user_id: int) -> Optional[InferenceTask]:
        task = self.db.query(InferenceTask).filter_by(id=task_id, user_id=user_id).first()
        if task:
            logger.info(f"[GET ONE] Found task_id={task_id} for user_id={user_id}")
        else:
            logger.warning(f"[GET ONE] No task found with id={task_id} for user_id={user_id}")
        return task
    
    def update_output(self, task_id: int, output: dict | str):
        if isinstance(output, dict):
            output = json.dumps(output)
        task = self.db.query(InferenceTask).filter_by(id=task_id).first()
        if task:
            task.output_data = output
            task.status = "COMPLETED"
            self.db.commit()
            logger.info(f"[UPDATE] Task {task_id} marked as COMPLETED with output")
        else:
            logger.warning(f"[UPDATE] Attempt to update non-existent task_id={task_id}")

    


