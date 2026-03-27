"""
Integration test for MLflow and model registry
"""

import pytest
import os
from mlops.model_registry import ModelRegistry
from mlops.config import mlops_config

@pytest.fixture
def registry():
    """Create registry instance for tests"""
    return ModelRegistry()

class TestModelRegistry:
    """Test model registry functionality"""
    
    def test_mlflow_connection(self, registry):
        """Test connection to MLflow"""
        assert registry.client is not None
    
    def test_log_metadata(self, registry):
        """Test logging model metadata"""
        
        metrics = {
            "accuracy": 0.95,
            "precision": 0.93
        }
        params = {
            "learning_rate": 0.001,
            "batch_size": 32
        }
        tags = {
            "framework": "sklearn",
            "environment": "test"
        }
        
        run_id = registry.log_model_metadata(
            model_name="test_classifier",
            model_type="sklearn",
            metrics=metrics,
            params=params,
            tags=tags
        )
        
        assert run_id is not None
        assert len(run_id) > 0
    
    def test_mlops_config(self):
        """Test MLOps configuration"""
        
        assert mlops_config.MINIMUM_MODEL_ACCURACY > 0
        assert mlops_config.MODELS_PATH.exists()
        assert mlops_config.LOGS_PATH.exists()
        assert len(mlops_config.MODEL_REGISTRY) > 0
