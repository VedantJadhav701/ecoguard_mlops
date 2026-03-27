"""
Model Monitoring & Metrics Collection
Tracks model performance, data drift, and system health
"""

import time
from datetime import datetime
from typing import Dict, Any, List
import json
from pathlib import Path
from prometheus_client import Counter, Histogram, Gauge
import logging

logger = logging.getLogger(__name__)

# Prometheus metrics
prediction_counter = Counter(
    'predictions_total',
    'Total predictions made',
    ['model_type', 'status']
)

prediction_latency = Histogram(
    'prediction_latency_seconds',
    'Prediction latency in seconds',
    ['model_type']
)

model_accuracy = Gauge(
    'model_accuracy',
    'Current model accuracy',
    ['model_type', 'stage']
)

data_drift = Gauge(
    'data_drift_score',
    'Data drift detection score',
    ['feature']
)

class ModelMonitor:
    """Monitor model performance and data quality"""
    
    def __init__(self, log_path: str = "/app/logs"):
        self.log_path = Path(log_path)
        self.log_path.mkdir(parents=True, exist_ok=True)
        self.metrics_file = self.log_path / "model_metrics.jsonl"
        self.drift_file = self.log_path / "data_drift.jsonl"
    
    def log_prediction(self, 
                      model_type: str,
                      prediction: Any,
                      confidence: float,
                      execution_time: float,
                      input_features: Dict = None,
                      metadata: Dict = None) -> None:
        """Log prediction for monitoring"""
        
        # Update Prometheus metrics
        status = "success" if confidence > 0.5 else "low_confidence"
        prediction_counter.labels(model_type=model_type, status=status).inc()
        prediction_latency.labels(model_type=model_type).observe(execution_time)
        
        # Log to file
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "model_type": model_type,
            "prediction": str(prediction),
            "confidence": float(confidence),
            "execution_time_ms": execution_time * 1000,
            "input_features": input_features,
            "metadata": metadata
        }
        
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        logger.info(f"Prediction logged: {model_type} (confidence: {confidence:.2f})")
    
    def log_model_performance(self,
                             model_type: str,
                             accuracy: float,
                             precision: float,
                             recall: float,
                             f1_score: float,
                             stage: str = "production") -> None:
        """Log model performance metrics"""
        
        model_accuracy.labels(model_type=model_type, stage=stage).set(accuracy)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "model_type": model_type,
            "stage": stage,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score
        }
        
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        logger.info(f"Performance metrics logged: {model_type} (acc: {accuracy:.4f})")
    
    def detect_data_drift(self,
                        feature_name: str,
                        baseline_distribution: Dict,
                        current_distribution: Dict) -> float:
        """Detect data drift using KL divergence"""
        
        import numpy as np
        from scipy.spatial.distance import jensenshannon
        
        baseline = np.array(list(baseline_distribution.values()))
        current = np.array(list(current_distribution.values()))
        
        # Normalize distributions
        baseline = baseline / baseline.sum()
        current = current / current.sum()
        
        # Calculate JS divergence
        drift_score = jensenshannon(baseline, current)
        
        data_drift.labels(feature=feature_name).set(drift_score)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "feature": feature_name,
            "drift_score": float(drift_score),
            "drift_detected": drift_score > 0.1
        }
        
        with open(self.drift_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        logger.warning(f"Data drift detected for {feature_name}: {drift_score:.4f}")
        return drift_score
    
    def get_metrics_summary(self, hours: int = 24) -> Dict:
        """Get metrics summary for specified timeframe"""
        
        summary = {
            "prediction_count": 0,
            "avg_confidence": 0.0,
            "avg_latency_ms": 0.0,
            "errors": 0,
            "data_drifts": 0
        }
        
        # Parse metrics file
        if self.metrics_file.exists():
            entries = []
            with open(self.metrics_file, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        entries.append(entry)
                    except:
                        pass
            
            summary["prediction_count"] = len(entries)
            if entries:
                summary["avg_confidence"] = sum(
                    e.get("confidence", 0) for e in entries
                ) / len(entries)
                summary["avg_latency_ms"] = sum(
                    e.get("execution_time_ms", 0) for e in entries
                ) / len(entries)
        
        return summary
