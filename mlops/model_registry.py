"""
MLflow Model Registry & Versioning
Handles model tracking, registration, and deployment
"""

import mlflow
import mlflow.sklearn
import mlflow.pytorch
from mlflow.models.signature import infer_signature
from datetime import datetime
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ModelRegistry:
    """
    Manages model versioning and registry with MLflow
    """
    
    def __init__(self, tracking_uri: str = "http://mlflow:5000"):
        """Initialize MLflow client"""
        mlflow.set_tracking_uri(tracking_uri)
        self.client = mlflow.tracking.MlflowClient(tracking_uri)
    
    def log_model_metadata(self, 
                          model_name: str,
                          model_type: str,
                          metrics: dict,
                          params: dict,
                          tags: dict = None) -> str:
        """Log model with metadata"""
        
        with mlflow.start_run():
            # Log parameters
            mlflow.log_params(params)
            
            # Log metrics
            mlflow.log_metrics(metrics)
            
            # Log tags
            if tags:
                mlflow.set_tags(tags)
            
            # Additional metadata
            mlflow.log_dict({
                'timestamp': datetime.now().isoformat(),
                'model_name': model_name,
                'model_type': model_type
            }, 'metadata.json')
            
            run_id = mlflow.active_run().info.run_id
            logger.info(f"Model logged with run_id: {run_id}")
            return run_id
    
    def register_model(self, 
                       run_id: str,
                       model_name: str,
                       model_path: str,
                       model_format: str = "sklearn") -> str:
        """Register model in MLflow registry"""
        
        try:
            # Log model
            if model_format == "sklearn":
                import joblib
                model = joblib.load(model_path)
                mlflow.sklearn.log_model(model, "model")
            elif model_format == "pytorch":
                mlflow.pytorch.log_model(model_path, "model")
            
            # Register in MLflow registry
            model_uri = f"runs:/{run_id}/model"
            
            result = mlflow.register_model(model_uri, model_name)
            
            logger.info(f"Model registered: {model_name} v{result.version}")
            return result.name
            
        except Exception as e:
            logger.error(f"Failed to register model: {e}")
            raise
    
    def promote_model(self, 
                     model_name: str,
                     version: int,
                     stage: str = "Production") -> None:
        """Promote model to stage (Staging/Production)"""
        
        self.client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage=stage
        )
        logger.info(f"Model {model_name} v{version} promoted to {stage}")
    
    def get_model_version(self, 
                         model_name: str,
                         stage: str = "Production"):
        """Get active model version for a stage"""
        
        try:
            latest_versions = self.client.get_latest_versions(model_name, stages=[stage])
            if latest_versions:
                version = latest_versions[0].version
                logger.info(f"Latest {stage} version of {model_name}: v{version}")
                return version
            return None
        except Exception as e:
            logger.error(f"Failed to get model version: {e}")
            return None
    
    def log_dataset(self, 
                   name: str,
                   dataset_path: str,
                   description: str):
        """Log dataset for reproducibility"""
        
        mlflow.log_artifact(
            dataset_path,
            artifact_path=f"datasets/{name}"
        )
        logger.info(f"Dataset logged: {name}")

# Example usage
if __name__ == "__main__":
    registry = ModelRegistry()
    
    # Log model metadata
    metrics = {
        "accuracy": 0.95,
        "precision": 0.93,
        "recall": 0.94,
        "f1_score": 0.935
    }
    params = {
        "learning_rate": 0.001,
        "batch_size": 32,
        "epochs": 100
    }
    tags = {
        "model_type": "classifier",
        "framework": "sklearn",
        "environment": "production"
    }
    
    run_id = registry.log_model_metadata(
        model_name="waste_classifier",
        model_type="sklearn_ensemble",
        metrics=metrics,
        params=params,
        tags=tags
    )
    
    print(f"Model logged successfully: {run_id}")
