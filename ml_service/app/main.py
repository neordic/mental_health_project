from fastapi import FastAPI
from ml_service.app.api import auth
from ml_service.app.api import billing
from ml_service.app.api import inference
import logging

from ml_service.app.core.logger import get_logger  
from prometheus_fastapi_instrumentator import Instrumentator

logger = get_logger("main")

app = FastAPI()

logger.info("FastAPI приложение инициализировано")

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(billing.router)
app.include_router(inference.router, prefix="/inference", tags=["Inference"])

Instrumentator().instrument(app).expose(app)



@app.get("/")
def read_root():
    logger.info("GET / — корневой эндпоинт вызван")
    return {"message": "Hello from FastAPI"}
