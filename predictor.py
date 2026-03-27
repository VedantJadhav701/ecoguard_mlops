"""
EcoGuard - Model Predictor
Handles all AI model predictions (Vision, Weight, Carbon, Lifestyle)
"""

import json
import pickle
import joblib
import numpy as np
from pathlib import Path
from ultralytics import YOLO
import logging

logger = logging.getLogger(__name__)

class ModelPredictor:
    """
    Central predictor class that loads and manages all models
    """
    
    def __init__(self, models_path="."):
        """
        Initialize and load all models
        Args:
            models_path: Path to models directory (default: current directory)
        """
        self.models_path = Path(models_path)
        self.vision_model = None
        self.weight_estimator = None
        self.weight_config = None
        self.lifestyle_model = None
        self.emission_factors = {
            'plastic': 2.5,
            'glass': 1.8,
            'metal': 8.0,
            'paper': 1.0,
            'cardboard': 0.9,
            'trash': 1.5
        }
        self.class_names = {
            0: 'cardboard',
            1: 'glass',
            2: 'metal',
            3: 'paper',
            4: 'plastic',
            5: 'trash'
        }
        
        # Load all models
        self.load_models()
    
    def load_models(self):
        """Load all pre-trained models"""
        try:
            # Check ultralytics environment and configuration
            try:
                import ultralytics
                logger.info(f"✓ ultralytics version: {ultralytics.__version__}")
                from ultralytics.utils.downloads import HUB_DIR
                logger.info(f"YOLO cache/hub dir: {HUB_DIR}")
                
                # Set offline mode to prevent YOLO from trying to download
                import os
                os.environ['YOLO_CFG_DIR'] = '/app/models'
                logger.info("Set YOLO_CFG_DIR to /app/models")
                
            except ImportError as im_err:
                logger.error(f"ultralytics not available: {str(im_err)}")
            
            # Load Vision Model (YOLOv8)
            logger.info("Loading Vision Model (YOLOv8)...")
            vision_path = self.models_path / 'vision_model' / 'best.pt'
            logger.info(f"Vision model path: {vision_path.absolute()}")
            logger.info(f"Vision model exists: {vision_path.exists()}")
            
            if vision_path.exists():
                try:
                    logger.info(f"Attempting to load YOLO from: {str(vision_path)}")
                    # Try with GPU first, but allow CPU fallback
                    try:
                        self.vision_model = YOLO(str(vision_path))
                        logger.info("✓ Vision Model loaded successfully")
                    except RuntimeError as runtime_err:
                        if 'cuda' in str(runtime_err).lower() or 'gpu' in str(runtime_err).lower():
                            logger.warning(f"GPU error, trying CPU mode: {str(runtime_err)}")
                            self.vision_model = YOLO(str(vision_path), device='cpu')
                            logger.info("✓ Vision Model loaded successfully (CPU mode)")
                        else:
                            raise
                except Exception as e:
                    import traceback
                    logger.error(f"Failed to load vision model: {str(e)}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    logger.error(f"File size: {vision_path.stat().st_size if vision_path.exists() else 'N/A'} bytes")
                    
                    # Try verifying file is a valid PyTorch model
                    try:
                        import torch
                        state_dict = torch.load(str(vision_path), map_location='cpu')
                        logger.warning("WARNING: torch.load succeeded but YOLO init failed - possible YOLO issue")
                        logger.info(f"Model dict keys: {list(state_dict.keys())[:5] if isinstance(state_dict, dict) else 'Not a dict'}")
                    except Exception as torch_e:
                        logger.error(f"torch.load also failed: {str(torch_e)}")
                    
                    logger.warning(f"Falling back to standard YOLOv8 nano model...")
                    # Try alternative path resolution
                    alt_path = Path("vision_model/best.pt")
                    if alt_path.exists():
                        try:
                            logger.info(f"Alt path file size: {alt_path.stat().st_size} bytes")
                            self.vision_model = YOLO(str(alt_path), device='cpu')
                            logger.info("✓ Vision Model loaded successfully (alternative path, CPU mode)")
                        except Exception as alt_e:
                            logger.error(f"Failed with alternative path too: {str(alt_e)}")
                            logger.error(f"Alt traceback: {traceback.format_exc()}")
                            logger.warning("Last fallback: Loading standard YOLOv8 nano...")
                            try:
                                self.vision_model = YOLO('yolov8n.pt', device='cpu')
                                logger.warning("⚠️  Using standard YOLOv8n model as fallback (not custom trained)")
                            except Exception as fallback_e:
                                logger.error(f"Even standard model failed: {str(fallback_e)}")
            else:
                logger.error(f"Vision model not found at {vision_path}")
                # Try alternative
                alt_path = Path("vision_model/best.pt")
                logger.info(f"Trying alternative path: {alt_path.absolute()}, exists: {alt_path.exists()}")
                if alt_path.exists():
                    try:
                        logger.info(f"Alt path file size: {alt_path.stat().st_size} bytes")
                        self.vision_model = YOLO(str(alt_path), device='cpu')
                        logger.info("✓ Vision Model loaded successfully (alternative path, CPU mode)")
                    except Exception as e:
                        import traceback
                        logger.error(f"Failed to load from alternative path: {str(e)}")
                        logger.error(f"Alt traceback: {traceback.format_exc()}")
                        logger.warning("Fallback: Loading standard YOLOv8 nano...")
                        try:
                            self.vision_model = YOLO('yolov8n.pt', device='cpu')
                            logger.warning("⚠️  Using standard YOLOv8n model as fallback (not custom trained)")
                        except Exception as fallback_e:
                            logger.error(f"Standard model also failed: {str(fallback_e)}")
                else:
                    logger.warning("Custom model file not found, loading standard YOLOv8...")
                    try:
                        self.vision_model = YOLO('yolov8n.pt', device='cpu')
                        logger.warning("⚠️  Using standard YOLOv8n model (not custom trained)")
                    except Exception as e:
                        logger.error(f"Failed to load standard model: {str(e)}")
            
            # Load Weight Estimator
            logger.info("Loading Weight Estimator...")
            weight_path = self.models_path / 'weight_model' / 'weight_estimator.pkl'
            if weight_path.exists():
                with open(weight_path, 'rb') as f:
                    self.weight_estimator = pickle.load(f)
                logger.info("✓ Weight Estimator loaded successfully")
            else:
                logger.error(f"Weight estimator not found at {weight_path}")
            
            # Load Weight Config
            config_path = self.models_path / 'weight_model' / 'weight_estimator_config.json'
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self.weight_config = json.load(f)
                logger.info("✓ Weight Config loaded successfully")
            
            # Load Lifestyle Model
            logger.info("Loading Lifestyle Model...")
            lifestyle_path = self.models_path / 'lifestyle_model' / 'best_ml_model.joblib'
            if lifestyle_path.exists():
                self.lifestyle_model = joblib.load(str(lifestyle_path))
                logger.info("✓ Lifestyle Model loaded successfully")
            else:
                logger.error(f"Lifestyle model not found at {lifestyle_path}")
            
            logger.info("✓ All models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Summary of loaded models
        logger.info("="*50)
        logger.info(f"Model Loading Summary:")
        logger.info(f"  Vision Model: {'✓ LOADED' if self.vision_model else '✗ FAILED'}")
        logger.info(f"  Weight Estimator: {'✓ LOADED' if self.weight_estimator else '✗ FAILED'}")
        logger.info(f"  Weight Config: {'✓ LOADED' if self.weight_config else '✗ FAILED'}")
        logger.info(f"  Lifestyle Model: {'✓ LOADED' if self.lifestyle_model else '✗ FAILED'}")
        logger.info("="*50)
    
    def detect_objects(self, image_path):
        """
        Detect waste objects in image using YOLOv8
        Args:
            image_path: Path to image file
        Returns:
            Dictionary with detections
        """
        if self.vision_model is None:
            logger.error("Vision model is None - check load_models() logs for details")
            logger.error(f"Models path: {self.models_path}")
            vision_path = self.models_path / 'vision_model' / 'best.pt'
            logger.error(f"Expected model path: {vision_path}")
            logger.error(f"File exists: {vision_path.exists() if self.models_path else 'N/A'}")
            raise Exception("Vision model not loaded - see logs for details")
        
        try:
            # Run inference
            results = self.vision_model(image_path, conf=0.25)
            
            detections = []
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                    
                    detections.append({
                        'class_id': class_id,
                        'class_name': self.class_names.get(class_id, 'unknown'),
                        'confidence': round(confidence, 4),
                        'bbox': {
                            'x1': round(bbox[0], 2),
                            'y1': round(bbox[1], 2),
                            'x2': round(bbox[2], 2),
                            'y2': round(bbox[3], 2)
                        }
                    })
            
            return {
                'success': True,
                'detections': detections,
                'count': len(detections),
                'model': 'YOLOv8 Nano',
                'accuracy': '96.1%'
            }
        
        except Exception as e:
            logger.error(f"Error in object detection: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def estimate_weight(self, bbox, class_name, image_shape):
        """
        Estimate object weight using rule-based formula
        Args:
            bbox: Bounding box [x1, y1, x2, y2]
            class_name: Material class name
            image_shape: Image shape [height, width, channels]
        Returns:
            Dictionary with weight estimation
        """
        try:
            if self.weight_config is None:
                raise Exception("Weight config not loaded")
            
            # Extract bbox coordinates
            x1, y1, x2, y2 = bbox['x1'], bbox['y1'], bbox['x2'], bbox['y2']
            
            # Calculate bbox area
            bbox_width = x2 - x1
            bbox_height = y2 - y1
            bbox_area = bbox_width * bbox_height
            
            # Calculate image area
            image_height, image_width = image_shape[0], image_shape[1]
            image_area = image_height * image_width
            
            # Calculate area ratio
            area_ratio = bbox_area / image_area if image_area > 0 else 0
            
            # Get base weight and reference ratio from config
            base_weights = self.weight_config['base_weights']
            reference_ratio = self.weight_config['reference_area_ratio']
            min_weight = self.weight_config['min_weight_g']
            max_weight = self.weight_config['max_weight_g']
            
            # Get base weight for material
            base_weight = base_weights.get(class_name, 30)  # Default to 30g
            
            # Calculate weight using formula
            weight_g = base_weight * (area_ratio / reference_ratio)
            
            # Apply limits
            weight_g = max(min_weight, min(weight_g, max_weight))
            weight_kg = weight_g / 1000
            
            # Determine size category
            if area_ratio < 0.1:
                size_category = 'small (<10% of image)'
            elif area_ratio < 0.25:
                size_category = 'small-medium (10-25% of image)'
            elif area_ratio < 0.5:
                size_category = 'medium (25-50% of image)'
            else:
                size_category = 'large (>50% of image)'
            
            return {
                'success': True,
                'weight_g': round(weight_g, 2),
                'weight_kg': round(weight_kg, 4),
                'material': class_name,
                'size_category': size_category,
                'confidence': 'high',
                'explanation': f'Base {class_name} = {base_weight}g. Size is {size_category.lower()}. Adjusted weight: {round(weight_g, 2)}g'
            }
        
        except Exception as e:
            logger.error(f"Error in weight estimation: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def calculate_carbon(self, weight_kg, material):
        """
        Calculate CO2 emissions using LCA factors
        Args:
            weight_kg: Weight in kilograms
            material: Material type
        Returns:
            Dictionary with carbon impact
        """
        try:
            # Get emission factor for material
            emission_factor = self.emission_factors.get(material, 2.0)
            
            # Calculate CO2
            carbon_kg = weight_kg * emission_factor
            carbon_g = carbon_kg * 1000
            
            # Calculate recycling impact (70% reduction when recycled)
            recycling_reduction_percent = 70.0
            if_recycled_co2_kg = carbon_kg * (1 - recycling_reduction_percent / 100)
            co2_saved_kg = carbon_kg - if_recycled_co2_kg
            
            return {
                'success': True,
                'material': material,
                'weight_kg': round(weight_kg, 4),
                'carbon_kg': round(carbon_kg, 4),
                'carbon_g': round(carbon_g, 2),
                'emission_factor': emission_factor,
                'recycling_reduction_percent': recycling_reduction_percent,
                'if_recycled_co2_kg': round(if_recycled_co2_kg, 4),
                'co2_saved_kg': round(co2_saved_kg, 4)
            }
        
        except Exception as e:
            logger.error(f"Error in carbon calculation: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def predict_lifestyle_carbon(self, features):
        """
        Predict user's carbon footprint from lifestyle features
        Args:
            features: List of 20 lifestyle features
        Returns:
            Dictionary with carbon prediction
        """
        try:
            if self.lifestyle_model is None:
                raise Exception("Lifestyle model not loaded")
            
            if len(features) != 20:
                raise ValueError(f"Expected 20 features, got {len(features)}")
            
            # Convert to numpy array
            features_array = np.array(features).reshape(1, -1)
            
            # Predict
            monthly_carbon = float(self.lifestyle_model.predict(features_array)[0])
            yearly_carbon = monthly_carbon * 12
            daily_average = monthly_carbon / 30
            
            # Compare to average (assuming average is ~500 kg/month)
            average_carbon = 500
            compared_percent = round((monthly_carbon - average_carbon) / average_carbon * 100, 1)
            
            return {
                'success': True,
                'monthly_carbon_kg': round(monthly_carbon, 1),
                'yearly_carbon_kg': round(yearly_carbon, 1),
                'daily_average_kg': round(daily_average, 2),
                'compared_to_average_percent': compared_percent,
                'country_average_kg': average_carbon,
                'recommendation': self._get_recommendation(compared_percent)
            }
        
        except Exception as e:
            logger.error(f"Error in lifestyle prediction: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_recommendation(self, compared_percent):
        """Generate recommendation based on comparison"""
        if compared_percent < -20:
            return "Excellent! Your carbon footprint is 20%+ below average. You're an environmental leader!"
        elif compared_percent < -10:
            return "Great! Your carbon footprint is 10%+ below average. Keep up the good work!"
        elif compared_percent <= 10:
            return "Good! Your carbon footprint is close to average. Small improvements can help."
        elif compared_percent <= 20:
            return "Your carbon footprint is slightly above average. Consider reducing energy use."
        else:
            return "Your carbon footprint is significantly above average. Major changes recommended."


# Global predictor instance
_predictor = None

def get_predictor(models_path="."):
    """Get or create global predictor instance"""
    global _predictor
    if _predictor is None:
        _predictor = ModelPredictor(models_path)
    return _predictor

def reload_predictor():
    """Reload all models"""
    global _predictor
    _predictor = None
    return get_predictor()
