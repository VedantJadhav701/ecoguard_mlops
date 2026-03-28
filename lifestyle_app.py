"""
EcoGuard - Lifestyle Regression API
Standalone service for calculating user carbon footprint from lifestyle data.
Uses best_ml_model.joblib (StackingRegressor).
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import joblib
import numpy as np
import logging
from pathlib import Path
import os
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lifestyle_app")

app = FastAPI(
    title="EcoGuard Lifestyle API",
    description="Regression service for lifestyle carbon footprint tracking",
    version="1.0.0"
)

# Data Model
class LifestylePredictRequest(BaseModel):
    features: List[float] # Expected 20 features

# Global model state
model_data = None

def load_lifestyle_model():
    global model_data
    model_path = Path("lifestyle_model/best_ml_model.joblib")
    
    if not model_path.exists():
        logger.error(f"Model not found at {model_path}")
        return None
        
    try:
        logger.info(f"Loading Lifestyle Model from {model_path}...")
        loaded = joblib.load(str(model_path))
        
        if isinstance(loaded, dict):
            logger.info(f"Loaded dictionary with keys: {list(loaded.keys())}")
            # The model is under the 'model' key as seen in logs
            model_data = loaded
        else:
            # Fallback if it's just the model object
            model_data = {'model': loaded}
            
        logger.info("✓ Lifestyle Model loaded successfully")
        return model_data
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        return None

@app.on_event("startup")
async def startup():
    load_lifestyle_model()

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": model_data is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/predict")
async def predict(request: LifestylePredictRequest):
    if model_data is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
        
    if len(request.features) < 18: # User said 18-20 features in prompt
        raise HTTPException(status_code=400, detail=f"Expected at least 18 features, got {len(request.features)}")
        
    try:
        # Simple prediction logic
        model = model_data['model']
        
        # Ensure we have the right number of features (truncate or pad to 20 if needed, 
        # but let's assume the request matches what the model expects)
        # In the original code it was using 20 features.
        features_array = np.array(request.features).reshape(1, -1)
        
        # If the model has a scaler, apply it (as seen in dictionary keys)
        if 'scaler' in model_data and model_data['scaler'] is not None:
            features_array = model_data['scaler'].transform(features_array)
            
        prediction = float(model.predict(features_array)[0])
        
        return {
            "success": True,
            "monthly_carbon_kg": round(prediction, 1),
            "yearly_carbon_kg": round(prediction * 12, 1),
            "status": "calculated",
            "model_type": type(model).__name__
        }
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
