from celery import Celery
from ml_inference.core.config import settings
from ml_inference.core.logger import get_logger

logger = get_logger("celery")

celery_app = Celery(
    "ml_inference",
    broker=settings.celery_broker_url,
    backend="redis://redis:6379/1"  
)

celery_app.autodiscover_tasks(["ml_inference.tasks"])

celery_app.conf.update(
    worker_send_task_events=True,
    task_send_sent_event=True,
)

logger.info("[CELERY] Celery app initialized")
logger.info(f"[CELERY] Broker: {settings.celery_broker_url}")
logger.info(f"[CELERY] Tasks autodiscovered from: ['ml_inference.tasks']")
