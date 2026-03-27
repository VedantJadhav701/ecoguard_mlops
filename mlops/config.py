"""
MLOps Configuration & Constants
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict
import os

@dataclass
class MLOpsConfig:
    """MLOps configuration"""
    
    # Paths
    MODELS_PATH: Path = Path("/app/models")
    LOGS_PATH: Path = Path("/app/logs")
    DATA_PATH: Path = Path("/app/data")
    ARTIFACTS_PATH: Path = Path("/app/mlruns")
    
    # MLflow Configuration
    MLFLOW_TRACKING_URI: str = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
    MLFLOW_REGISTRY_URI: str = os.getenv("MLFLOW_REGISTRY_URI", "http://mlflow:5000")
    
    # Model Versioning
    MIN_MODEL_ACCURACY: float = 0.85
    REQUIRE_APPROVAL: bool = True
    AUTO_PROMOTE_TO_STAGING: bool = True
    AUTO_PROMOTE_TO_PROD: bool = False
    
    # Monitoring
    MONITORING_ENABLED: bool = True
    LOG_PREDICTIONS: bool = True
    DETECT_DRIFT: bool = True
    DRIFT_THRESHOLD: float = 0.1
    
    # Performance Thresholds
    LATENCY_THRESHOLD_MS: float = 100.0
    CONFIDENCE_THRESHOLD: float = 0.5
    ERROR_RATE_THRESHOLD: float = 0.05
    
    # Model Information
    MODEL_REGISTRY: Dict = None
    
    def __post_init__(self):
        """Create necessary directories"""
        for path in [self.MODELS_PATH, self.LOGS_PATH, self.DATA_PATH, self.ARTIFACTS_PATH]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Initialize model registry
        self.MODEL_REGISTRY = {
            'vision': {
                'name': 'yolov8_waste_detector',
                'type': 'yolo',
                'min_version': '1.0.0',
                'framework': 'pytorch'
            },
            'weight': {
                'name': 'weight_estimator',
                'type': 'regression',
                'min_version': '1.0.0',
                'framework': 'sklearn'
            },
            'lifestyle': {
                'name': 'lifestyle_carbon_calculator',
                'type': 'classifier',
                'min_version': '1.0.0',
                'framework': 'sklearn'
            }
        }

# Global config instance
mlops_config = MLOpsConfig()
