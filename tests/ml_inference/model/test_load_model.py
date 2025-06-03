import joblib
import tempfile
import shutil
from pathlib import Path
from ml_inference.model.load_model import load_model_and_scaler
from ml_inference.core.config import settings

def test_load_model_and_scaler(monkeypatch):
    
    temp_dir = tempfile.mkdtemp()

    try:
        model_path = Path(temp_dir) / "dummy_model.pkl"
        scaler_path = Path(temp_dir) / "scaler.joblib"
        joblib.dump({"model": "dummy"}, model_path)
        joblib.dump({"scaler": "dummy"}, scaler_path)

        
        monkeypatch.setattr(settings, "model_dir", temp_dir)

        
        model, scaler = load_model_and_scaler("dummy_model")

        assert model["model"] == "dummy"
        assert scaler["scaler"] == "dummy"

    finally:
        shutil.rmtree(temp_dir)  
