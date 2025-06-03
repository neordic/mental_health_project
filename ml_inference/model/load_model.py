from pathlib import Path
import joblib
from functools import lru_cache
from ml_inference.core.config import settings

from ml_inference.core.logger import get_logger
logger = get_logger("model_loader")

@lru_cache(maxsize=3)
def load_model_and_scaler(model_name: str):
    model_path = Path(settings.model_dir) / f"{model_name}.pkl"
    scaler_path = Path(settings.model_dir) / "scaler.joblib"

    try:
        model = joblib.load(model_path)
        logger.info(f"[LOAD] Model loaded: {model_path}")
    except Exception as e:
        logger.exception(f"[ERROR] Failed to load model {model_name} at {model_path}")
        raise

    try:
        scaler = joblib.load(scaler_path)
        logger.info(f"[LOAD] Scaler loaded: {scaler_path}")
    except Exception as e:
        logger.exception(f"[ERROR] Failed to load scaler at {scaler_path}")
        raise
         
    return model, scaler


