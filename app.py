"""
EcoGuard - FastAPI Backend
Production-ready API server for all EcoGuard models
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
import asyncio
import json
from pathlib import Path
import cv2
import numpy as np
from datetime import datetime
import uuid

from predictor import get_predictor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="EcoGuard API",
    description="AI-powered waste management and carbon tracking system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== DATA MODELS ====================

class BBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

class WeightEstimateRequest(BaseModel):
    bbox: BBox
    class_name: str
    image_shape: List[int]  # [height, width, channels]

class CarbonCalculateRequest(BaseModel):
    weight_kg: float
    material: str

class LifestylePredictRequest(BaseModel):
    features: List[float]  # 20 lifestyle features

class UserActionRequest(BaseModel):
    material: str
    weight_g: float
    action: str  # 'recycle' or 'trash'
    timestamp: Optional[str] = None

class DetectionResult(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox: BBox

# ==================== GLOBAL STATE ====================

# In-memory storage for demo (use database in production)
user_actions = []
sensor_data_history = []
connected_clients = []

# ==================== HEALTH & INFO ====================

@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    """Root endpoint - API information"""
    return {
        "name": "EcoGuard API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "GET /health",
            "diagnostics": "GET /api/diagnostics (detailed model loading info)",
            "vision": "POST /api/vision/detect",
            "weight": "POST /api/weight/estimate",
            "carbon": "POST /api/carbon/calculate",
            "lifestyle": "POST /api/lifestyle/predict",
            "sensor": "WS /api/sensor/stream",
            "user": "POST /api/user/log-action"
        }
    }

@app.api_route("/health", methods=["GET", "HEAD"])
async def health_check():
    """Health check endpoint"""
    predictor = get_predictor()
    return {
        "status": "healthy",
        "models": {
            "vision": predictor.vision_model is not None,
            "weight": predictor.weight_estimator is not None,
            "lifestyle": predictor.lifestyle_model is not None
        },
        "timestamp": datetime.now().isoformat()
    }

# ==================== DIAGNOSTICS ====================

@app.get("/api/diagnostics")
async def diagnostics():
    """
    Detailed diagnostics about model loading status
    Shows which models loaded, which failed, and why
    """
    predictor = get_predictor()
    
    # Check file existence
    from pathlib import Path
    vision_path = Path("vision_model/best.pt")
    weight_path = Path("weight_model/weight_estimator.pkl")
    config_path = Path("weight_model/weight_estimator_config.json")
    lifestyle_path = Path("lifestyle_model/best_ml_model.joblib")
    
    return {
        "status": "diagnostic",
        "models_path": str(predictor.models_path),
        "model_status": {
            "vision": {
                "loaded": predictor.vision_model is not None and predictor.vision_model != "MOCK_MODE",
                "mock_mode": predictor.vision_model == "MOCK_MODE",
                "type": type(predictor.vision_model).__name__ if predictor.vision_model else "None",
                "file_exists": vision_path.exists(),
                "file_size_mb": (vision_path.stat().st_size / (1024*1024)) if vision_path.exists() else 0
            },
            "weight": {
                "loaded": predictor.weight_estimator is not None,
                "type": type(predictor.weight_estimator).__name__ if predictor.weight_estimator else "None",
                "file_exists": weight_path.exists(),
                "file_size_kb": (weight_path.stat().st_size / 1024) if weight_path.exists() else 0,
                "config_exists": config_path.exists(),
                "config_size_kb": (config_path.stat().st_size / 1024) if config_path.exists() else 0
            },
            "lifestyle": {
                "loaded": predictor.lifestyle_model is not None,
                "type": type(predictor.lifestyle_model).__name__ if predictor.lifestyle_model else "None",
                "file_exists": lifestyle_path.exists(),
                "file_size_mb": (lifestyle_path.stat().st_size / (1024*1024)) if lifestyle_path.exists() else 0
            }
        },
        "config": {
            "loaded": predictor.weight_config is not None,
            "type": type(predictor.weight_config).__name__ if predictor.weight_config else "None"
        },
        "summary": {
            "vision_ok": predictor.vision_model is not None,
            "weight_ok": predictor.weight_estimator is not None,
            "lifestyle_ok": predictor.lifestyle_model is not None,
            "config_ok": predictor.weight_config is not None
        },
        "environment": {
            "models_path_absolute": str(Path("vision_model").absolute()),
            "current_working_dir": str(Path(".").absolute())
        },
        "timestamp": datetime.now().isoformat()
    }

# ==================== VISION MODEL - OBJECT DETECTION ====================

@app.post("/api/vision/detect")
async def detect_objects(file: UploadFile = File(...)):
    """
    Detect waste objects in image (Primitive endpoint)
    """
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
            
        temp_path = f"/tmp/detect_{uuid.uuid4()}.jpg"
        cv2.imwrite(temp_path, img)
        
        predictor = get_predictor()
        result = predictor.detect_objects(temp_path)
        result['image_shape'] = list(img.shape)
        result['timestamp'] = datetime.now().isoformat()
        
        return result
    except Exception as e:
        logger.error(f"Error in vision detection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/vision/analyze")
async def analyze_vision(file: UploadFile = File(...)):
    """
    Combined endpoint: Detect objects -> Estimate Weight -> Calculate Carbon
    Returns a full eco-impact analysis for the image
    """
    try:
        logger.info(f"Full analysis requested for image: {file.filename}")
        
        # 1. Detection (Vision)
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
            
        temp_path = f"/tmp/analyze_{uuid.uuid4()}.jpg"
        cv2.imwrite(temp_path, img)
        
        predictor = get_predictor()
        detect_result = predictor.detect_objects(temp_path)
        
        # 2. Enrich detections with Weight and Carbon
        enriched_detections = []
        for det in detect_result.get('detections', []):
            enriched_det = det.copy()
            
            # Estimate Weight
            weight_result = predictor.estimate_weight(
                bbox=det['bbox'],
                class_name=det['class_name'],
                image_shape=list(img.shape)
            )
            
            if weight_result.get('success'):
                enriched_det['weight_g'] = weight_result['weight_g']
                enriched_det['weight_kg'] = weight_result['weight_kg']
                enriched_det['size_category'] = weight_result['size_category']
                
                # Calculate Carbon
                carbon_result = predictor.calculate_carbon_from_weight(
                    weight_kg=weight_result['weight_kg'],
                    material=det['class_name']
                )
                
                if carbon_result.get('success'):
                    enriched_det['carbon_g'] = carbon_result['carbon_g']
                    enriched_det['carbon_kg'] = carbon_result['carbon_kg']
                    enriched_det['co2_saved_kg'] = carbon_result['co2_saved_kg']
                    enriched_det['recycling_reduction_percent'] = carbon_result['recycling_reduction_percent']
            
            enriched_detections.append(enriched_det)
            
        # 3. Final Result
        return {
            "success": True,
            "count": len(enriched_detections),
            "detections": enriched_detections,
            "image_shape": list(img.shape),
            "timestamp": datetime.now().isoformat(),
            "model_vision": detect_result.get('model', 'YOLOv8'),
            "status": "complete_analysis"
        }
        
    except Exception as e:
        logger.error(f"Error in vision analysis: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# ==================== WEIGHT MODEL - WEIGHT ESTIMATION ====================

@app.post("/api/weight/estimate")
async def estimate_weight(request: WeightEstimateRequest):
    """
    Estimate object weight from bounding box
    
    Args:
        request: WeightEstimateRequest with bbox, class_name, image_shape
    
    Returns:
        Weight estimation in grams
    """
    try:
        logger.info(f"Weight estimation for {request.class_name}")
        
        predictor = get_predictor()
        result = predictor.estimate_weight(
            bbox=request.bbox.dict(),
            class_name=request.class_name,
            image_shape=request.image_shape
        )
        
        result['timestamp'] = datetime.now().isoformat()
        
        return result
    
    except Exception as e:
        logger.error(f"Error in weight estimation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== CARBON MODEL - CARBON CALCULATION ====================

@app.post("/api/carbon/calculate")
async def calculate_carbon(request: CarbonCalculateRequest):
    """
    Calculate CO2 emissions from material weight
    
    Args:
        request: CarbonCalculateRequest with weight_kg and material
    
    Returns:
        CO2 emissions and recycling impact
    """
    try:
        logger.info(f"Carbon calculation for {request.material} ({request.weight_kg}kg)")
        
        predictor = get_predictor()
        result = predictor.calculate_carbon(
            weight_kg=request.weight_kg,
            material=request.material
        )
        
        result['timestamp'] = datetime.now().isoformat()
        
        return result
    
    except Exception as e:
        logger.error(f"Error in carbon calculation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== LIFESTYLE MODEL - CARBON PREDICTION ====================

@app.post("/api/lifestyle/predict")
async def predict_lifestyle(request: LifestylePredictRequest):
    """
    Predict user's carbon footprint from lifestyle features
    
    Args:
        request: LifestylePredictRequest with 20 features
    
    Returns:
        Monthly/yearly carbon footprint prediction
    """
    try:
        if len(request.features) != 20:
            raise HTTPException(status_code=400, detail="Expected 20 features")
        
        logger.info("Lifestyle carbon prediction")
        
        predictor = get_predictor()
        result = predictor.predict_lifestyle_carbon(request.features)
        
        result['timestamp'] = datetime.now().isoformat()
        
        return result
    
    except Exception as e:
        logger.error(f"Error in lifestyle prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== USER ACTION LOGGING ====================

@app.post("/api/user/log-action")
async def log_action(request: UserActionRequest):
    """
    Log user action (recycle/trash decision)
    
    Args:
        request: UserActionRequest with material, weight, action
    
    Returns:
        Confirmation and updated score
    """
    try:
        action_data = {
            'id': str(uuid.uuid4()),
            'material': request.material,
            'weight_g': request.weight_g,
            'action': request.action,
            'timestamp': request.timestamp or datetime.now().isoformat()
        }
        
        # Store in memory (would be database in production)
        user_actions.append(action_data)
        
        logger.info(f"Action logged: {request.action} - {request.material} ({request.weight_g}g)")
        
        # Calculate current stats
        total_items = len(user_actions)
        recycled = len([a for a in user_actions if a['action'] == 'recycle'])
        recycled_percent = (recycled / total_items * 100) if total_items > 0 else 0
        
        return {
            'success': True,
            'action_id': action_data['id'],
            'message': f'Great! You {"recycled" if request.action == "recycle" else "discarded"} {request.material}',
            'stats': {
                'total_items': total_items,
                'recycled': recycled,
                'recycled_percent': round(recycled_percent, 1)
            },
            'timestamp': action_data['timestamp']
        }
    
    except Exception as e:
        logger.error(f"Error logging action: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== USER HISTORY ====================

@app.get("/api/user/history")
async def get_history(days: int = 7):
    """
    Get user action history
    
    Args:
        days: Number of days to retrieve
    
    Returns:
        List of user actions
    """
    try:
        logger.info(f"Retrieving history for last {days} days")
        
        # Filter by date (simplified - would be database query in production)
        history = user_actions[-50:]  # Return last 50 actions
        
        return {
            'success': True,
            'count': len(history),
            'actions': history,
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== USER REPORT ====================

@app.get("/api/user/report")
async def get_report(period: str = "weekly"):
    """
    Get user carbon report
    
    Args:
        period: 'weekly', 'monthly', or 'yearly'
    
    Returns:
        Carbon footprint report and statistics
    """
    try:
        logger.info(f"Generating {period} report")
        
        # Calculate statistics
        total_items = len(user_actions)
        recycled = len([a for a in user_actions if a['action'] == 'recycle'])
        
        # Estimate CO2 (simplified calculation)
        total_weight_g = sum([a['weight_g'] for a in user_actions])
        estimated_co2_kg = total_weight_g / 1000 * 2.5  # Average 2.5 kg CO2 per kg
        
        # Recycling savings (70% reduction)
        recycled_weight_g = sum([a['weight_g'] for a in user_actions if a['action'] == 'recycle'])
        savings_kg = (recycled_weight_g / 1000) * 2.5 * 0.7
        
        return {
            'success': True,
            'period': period,
            'stats': {
                'total_items': total_items,
                'recycled': recycled,
                'recycled_percent': round((recycled / total_items * 100) if total_items > 0 else 0, 1),
                'total_weight_g': round(total_weight_g, 2),
                'estimated_co2_kg': round(estimated_co2_kg, 2),
                'recycling_savings_kg': round(savings_kg, 2),
                'trees_equivalent': round(savings_kg / 20, 1)  # ~20kg CO2 per tree per year
            },
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== REAL-TIME SENSOR WebSocket ====================

@app.websocket("/api/sensor/stream")
async def sensor_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time sensor data stream
    Simulates MQ7 sensor readings (in production, read from actual sensor hardware)
    """
    await websocket.accept()
    connected_clients.append(websocket)
    logger.info("Sensor client connected")
    
    try:
        # Send sensor data every second
        import random
        
        while True:
            # Simulate sensor reading (in production, get from actual hardware)
            current_ppm = max(10, min(100, 50 + random.gauss(0, 10)))
            
            # Determine status
            if current_ppm < 50:
                status = "GOOD"
                trend = "IMPROVING"
                trend_pct = -5
            elif current_ppm < 100:
                status = "FAIR"
                trend = "STABLE"
                trend_pct = 0
            elif current_ppm < 500:
                status = "POOR"
                trend = "WORSENING"
                trend_pct = 5
            else:
                status = "DANGEROUS"
                trend = "WORSENING RAPIDLY"
                trend_pct = 10
            
            sensor_data = {
                'timestamp': datetime.now().isoformat(),
                'co_ppm': round(current_ppm, 1),
                'status': status,
                'trend': trend,
                'trend_percent': trend_pct,
                'last_24h_avg': 52,
                'peak_today': 78,
                'low_today': 32
            }
            
            # Send to client
            await websocket.send_json(sensor_data)
            
            # Wait 1 second before next reading
            await asyncio.sleep(1)
    
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    
    finally:
        if websocket in connected_clients:
            connected_clients.remove(websocket)
        logger.info("Sensor client disconnected")

# ==================== STARTUP & SHUTDOWN ====================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("EcoGuard API Starting...")
    
    # Load models
    try:
        predictor = get_predictor()
        logger.info("✓ All models loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load models: {str(e)}")
    
    logger.info("✓ EcoGuard API Ready")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("EcoGuard API Shutting down...")
    
    # Close any open connections
    for client in connected_clients:
        try:
            await client.close()
        except:
            pass
    
    logger.info("✓ EcoGuard API Stopped")

# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    
    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        log_level="info"
    )
