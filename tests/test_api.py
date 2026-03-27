"""
Unit and Integration Tests for EcoGuard API
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
import json
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app
from predictor import ModelPredictor

client = TestClient(app)

class TestHealthEndpoints:
    """Test health and info endpoints"""
    
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "name" in response.json()
        assert response.json()["name"] == "EcoGuard API"
    
    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

class TestVisionEndpoints:
    """Test vision/object detection endpoints"""
    
    @patch('predictor.ModelPredictor.detect_waste')
    def test_detect_endpoint(self, mock_detect):
        """Test waste detection endpoint"""
        
        mock_detect.return_value = {
            'detections': [{
                'class_id': 1,
                'class_name': 'plastic',
                'confidence': 0.95,
                'bbox': {'x1': 10, 'y1': 20, 'x2': 100, 'y2': 150}
            }],
            'inference_time_ms': 45.2
        }
        
        # Create mock image
        with open('test_image.jpg', 'rb') as f:
            response = client.post(
                "/api/vision/detect",
                files={"file": f}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert 'detections' in data
        assert len(data['detections']) > 0

class TestWeightEstimation:
    """Test weight estimation endpoints"""
    
    @patch('predictor.ModelPredictor.estimate_weight')
    def test_weight_estimate(self, mock_estimate):
        """Test weight estimation"""
        
        mock_estimate.return_value = {
            'estimated_weight_kg': 0.5,
            'confidence': 0.88
        }
        
        payload = {
            "bbox": {"x1": 10, "y1": 20, "x2": 100, "y2": 150},
            "class_name": "plastic",
            "image_shape": [480, 640, 3]
        }
        
        response = client.post("/api/weight/estimate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "estimated_weight_kg" in data
        assert data["estimated_weight_kg"] > 0

class TestCarbonCalculation:
    """Test carbon emissions calculation"""
    
    @patch('predictor.ModelPredictor.calculate_carbon')
    def test_carbon_calculate(self, mock_carbon):
        """Test carbon calculation"""
        
        mock_carbon.return_value = {
            'carbon_emissions_kg': 1.25,
            'emissions_breakdown': {
                'production': 0.8,
                'transport': 0.3,
                'decomposition': 0.15
            }
        }
        
        payload = {
            "weight_kg": 0.5,
            "material": "plastic"
        }
        
        response = client.post("/api/carbon/calculate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "carbon_emissions_kg" in data
        assert data["carbon_emissions_kg"] > 0

class TestLifestylePrediction:
    """Test lifestyle-based predictions"""
    
    @patch('predictor.ModelPredictor.predict_lifestyle_emissions')
    def test_lifestyle_predict(self, mock_predict):
        """Test lifestyle emissions prediction"""
        
        mock_predict.return_value = {
            'annual_emissions_kg': 4500,
            'category': 'high',
            'recommendations': [
                'Reduce plastic usage',
                'Use public transportation'
            ]
        }
        
        payload = {
            "features": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                        1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        }
        
        response = client.post("/api/lifestyle/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "annual_emissions_kg" in data

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_request_format(self):
        """Test invalid request format"""
        
        response = client.post(
            "/api/carbon/calculate",
            json={"invalid": "data"}
        )
        assert response.status_code != 200
    
    def test_missing_required_fields(self):
        """Test missing required fields"""
        
        response = client.post(
            "/api/weight/estimate",
            json={"bbox": {"x1": 10}}  # Missing required fields
        )
        assert response.status_code != 200

class TestPerformance:
    """Test performance and latency"""
    
    @patch('predictor.ModelPredictor.detect_waste')
    def test_detection_latency(self, mock_detect):
        """Test that detection meets latency requirements"""
        
        import time
        
        mock_detect.return_value = {
            'detections': [],
            'inference_time_ms': 50
        }
        
        with open('test_image.jpg', 'rb') as f:
            start = time.time()
            response = client.post("/api/vision/detect", files={"file": f})
            elapsed = (time.time() - start) * 1000
        
        # Should respond within 2 seconds
        assert elapsed < 2000
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=.", "--cov-report=html"])
