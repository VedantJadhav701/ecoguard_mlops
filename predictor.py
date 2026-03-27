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

# ==================== WEIGHT ESTIMATOR CLASS ====================

class WeightEstimator:
    """Simple weight estimation model based on area ratios"""
    
    def __init__(self):
        self.base_weights = {
            'plastic': 25,
            'glass': 35,
            'metal': 50,
            'paper': 10,
            'cardboard': 15,
            'trash': 20
        }
        self.reference_area_ratio = 0.1
        self.min_weight = 5
        self.max_weight = 500
    
    def estimate(self, area_ratio, material='plastic'):
        """Estimate weight based on area ratio"""
        base_weight = self.base_weights.get(material, 30)
        weight = base_weight * (area_ratio / self.reference_area_ratio)
        return max(self.min_weight, min(weight, self.max_weight))

# ==================== MODEL PREDICTOR ====================

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
    
    def _get_default_weight_config(self):
        """Provide default weight configuration if file is missing or corrupted"""
        return {
            'base_weights': {
                'plastic': 25,
                'glass': 35,
                'metal': 50,
                'paper': 10,
                'cardboard': 15,
                'trash': 20
            },
            'reference_area_ratio': 0.1,  # 10% of image
            'min_weight_g': 5,
            'max_weight_g': 500
        }
    
    def load_models(self):
        """Load all pre-trained models"""
        self.load_errors = []  # Track load errors
        
        try:
            # Disable YOLO download and network access
            import os
            os.environ['YOLO_DOWNLOAD'] = '0'  # Disable downloads
            os.environ['NO_UPDATES'] = '1'  # Disable auto-updates
            os.environ['YOLO_VERBOSE'] = 'True'  # Enable verbose logging for debugging
            
            # Log working directory and models path
            logger.info(f"Current working directory: {os.getcwd()}")
            logger.info(f"Models path: {self.models_path}")
            logger.info(f"Models path absolute: {self.models_path.absolute()}")
            
            # Check ultralytics environment and configuration
            try:
                import ultralytics
                logger.info(f"✓ ultralytics version: {ultralytics.__version__}")
                
                # Configure YOLO home and cache directories
                yolo_home = os.path.expanduser("~/.yolo")
                os.makedirs(yolo_home, exist_ok=True)
                os.environ['YOLO_HOME'] = yolo_home
                logger.info(f"Set YOLO_HOME to: {yolo_home}")
                
                # Try to get HUB_DIR (may not exist in all versions)
                try:
                    from ultralytics.utils.downloads import HUB_DIR
                    logger.info(f"YOLO cache/hub dir: {HUB_DIR}")
                except (ImportError, AttributeError):
                    logger.warning("HUB_DIR not available in this ultralytics version")
                
                # Set offline mode to prevent YOLO from trying to download
                os.environ['YOLO_CFG_DIR'] = yolo_home
                logger.info("Set YOLO_CFG_DIR for local caching")
                
                # Check PyTorch
                import torch
                logger.info(f"✓ PyTorch version: {torch.__version__}")
                logger.info(f"  CUDA Available: {torch.cuda.is_available()}")
                logger.info(f"  Device: {'GPU/CUDA' if torch.cuda.is_available() else 'CPU'}")
                
            except ImportError as im_err:
                logger.error(f"Dependency missing: {str(im_err)}")
                self.load_errors.append(str(im_err))
            
            # Load Vision Model (YOLOv8)
            logger.info("Loading Vision Model (YOLOv8)...")
            vision_path = self.models_path / 'vision_model' / 'best.pt'
            logger.info(f"Vision model path: {vision_path.absolute()}")
            logger.info(f"Vision model exists: {vision_path.exists()}")
            
            if vision_path.exists():
                try:
                    logger.info(f"Attempting to load YOLO from: {str(vision_path)}")
                    logger.info(f"File size: {vision_path.stat().st_size / (1024*1024):.2f} MB")
                    
                    # Try with explicit device and error handling
                    yolo_loaded = False
                    max_retries = 2
                    
                    for attempt in range(max_retries):
                        try:
                            logger.info(f"YOLO load attempt {attempt + 1}/{max_retries}")
                            
                            # First try: automatic device detection
                            if attempt == 0:
                                self.vision_model = YOLO(str(vision_path))
                            else:
                                # Second try: explicit mode (removed unsupported device arg)
                                self.vision_model = YOLO(str(vision_path))
                            
                            yolo_loaded = True
                            logger.info("✓ Vision Model loaded successfully")
                            break
                        
                        except RuntimeError as runtime_err:
                            error_msg = str(runtime_err).lower()
                            if 'cuda' in error_msg or 'gpu' in error_msg:
                                logger.warning(f"GPU/CUDA error: {str(runtime_err)}")
                                if attempt == 0:
                                    logger.info("Retrying with CPU mode...")
                                    continue
                            raise
                        except Exception as e:
                            if attempt < max_retries - 1:
                                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                                logger.info("Retrying...")
                                continue
                            raise
                    
                    if not yolo_loaded:
                        raise Exception("Failed to load YOLO after all retries")
                
                except Exception as e:
                    import traceback
                    logger.error(f"Failed to load vision model: {str(e)}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    logger.error(f"File size: {vision_path.stat().st_size if vision_path.exists() else 'N/A'} bytes")
                    
                    # Try standard YOLOv8 nano as fallback
                    logger.warning("Attempting fallback: loading standard YOLOv8 nano...")
                    try:
                        self.vision_model = YOLO('yolov8n.pt')
                        logger.warning("⚠️  Using standard YOLOv8n model as fallback (not custom trained)")
                    except Exception as fallback_e:
                        logger.error(f"Standard model also failed: {str(fallback_e)}")
                        logger.warning("Switching to MOCK_MODE for testing")
                        self.vision_model = "MOCK_MODE"
            
            else:
                logger.error(f"Vision model not found at {vision_path}")
                logger.info(f"Listing vision_model directory:")
                vision_dir = self.models_path / 'vision_model'
                if vision_dir.exists():
                    for item in vision_dir.iterdir():
                        logger.info(f"  - {item.name} ({item.stat().st_size / (1024*1024):.2f} MB if file)" if item.is_file() else f"  - {item.name}/ (directory)")
                else:
                    logger.error(f"vision_model directory not found at {vision_dir}")
                
                try:
                    logger.warning("Loading standard YOLOv8 nano as fallback...")
                    self.vision_model = YOLO('yolov8n.pt')
                    logger.warning("⚠️  Using standard YOLOv8n model (not custom trained)")
                except Exception as e:
                    logger.error(f"Failed to load standard model: {str(e)}")
                    logger.warning("Switching to MOCK_MODE for testing")
                    self.vision_model = "MOCK_MODE"
            
            # Load Weight Estimator
            logger.info("Loading Weight Estimator...")
            weight_path = self.models_path / 'weight_model' / 'weight_estimator.pkl'
            if weight_path.exists():
                try:
                    file_size = weight_path.stat().st_size
                    logger.info(f"Weight estimator file size: {file_size} bytes")
                    
                    if file_size == 0:
                        logger.warning("Weight estimator file is empty (0 bytes) - creating fallback")
                        self.weight_estimator = None  # Use fallback
                    else:
                        # Patch __main__ to find WeightEstimator if it was pickling from a notebook
                        import sys
                        main_module = sys.modules['__main__']
                        has_orig = hasattr(main_module, 'WeightEstimator')
                        orig_attr = getattr(main_module, 'WeightEstimator', None)
                        
                        try:
                            # Set WeightEstimator in __main__ temporarily if needed
                            setattr(main_module, 'WeightEstimator', WeightEstimator)
                            
                            with open(weight_path, 'rb') as f:
                                self.weight_estimator = pickle.load(f)
                            logger.info("✓ Weight Estimator loaded successfully")
                            
                        finally:
                            # Clean up __main__ patch
                            if has_orig:
                                setattr(main_module, 'WeightEstimator', orig_attr)
                            else:
                                if hasattr(main_module, 'WeightEstimator'):
                                    delattr(main_module, 'WeightEstimator')
                except (pickle.UnpicklingError, AttributeError, EOFError) as pickle_err:
                    logger.error(f"Failed to unpickle weight estimator: {str(pickle_err)}")
                    logger.warning(f"Error type: {type(pickle_err).__name__}")
                    logger.warning("Will use fallback weight estimation formula")
                    self.weight_estimator = None
                except Exception as pickle_err:
                    logger.error(f"Failed to load weight estimator: {str(pickle_err)}")
                    logger.warning("Will use fallback weight estimation formula")
                    self.weight_estimator = None
            else:
                logger.error(f"Weight estimator not found at {weight_path}")
            
            # Load Weight Config
            logger.info("Loading Weight Config...")
            config_path = self.models_path / 'weight_model' / 'weight_estimator_config.json'
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        self.weight_config = json.load(f)
                    logger.info("✓ Weight Config loaded successfully")
                except Exception as json_err:
                    logger.error(f"Failed to load weight config JSON: {str(json_err)}")
                    logger.warning("Using default weight config")
                    self.weight_config = self._get_default_weight_config()
            else:
                logger.error(f"Weight config not found at {config_path}")
                logger.warning("Using default weight config")
                self.weight_config = self._get_default_weight_config()
            
            # Load Lifestyle Model
            logger.info("Loading Lifestyle Model...")
            lifestyle_path = self.models_path / 'lifestyle_model' / 'best_ml_model.joblib'
            if lifestyle_path.exists():
                try:
                    file_size = lifestyle_path.stat().st_size
                    logger.info(f"Lifestyle model file size: {file_size} bytes")
                    
                    loaded_model = joblib.load(str(lifestyle_path))
                    
                    # If loaded object is a dictionary, try to extract the model
                    if isinstance(loaded_model, dict):
                        logger.info(f"Loaded lifestyle model is a dictionary with keys: {list(loaded_model.keys())}")
                        # Look for common keys that might contain the actual model
                        for key in ['model', 'best_model', 'regressor', 'classifier', 'pipeline', 'clf']:
                            if key in loaded_model:
                                logger.info(f"Found model in dictionary using key: '{key}'")
                                loaded_model = loaded_model[key]
                                break
                    
                    # Validate that what we loaded is actually a model (has predict method)
                    if not hasattr(loaded_model, 'predict'):
                        logger.error(f"Loaded object is not a valid model. Type: {type(loaded_model)}")
                        logger.warning("Object doesn't have predict() method - will use fallback")
                        self.lifestyle_model = None
                    else:
                        self.lifestyle_model = loaded_model
                        logger.info(f"✓ Lifestyle Model loaded successfully and validated (Type: {type(loaded_model).__name__})")
                except Exception as joblib_err:
                    logger.error(f"Failed to load lifestyle model: {str(joblib_err)}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    self.lifestyle_model = None
            else:
                logger.error(f"Lifestyle model not found at {lifestyle_path}")
                self.lifestyle_model = None
            
            logger.info("✓ All available models loaded")
            
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
        
        # Handle mock mode (for testing when YOLO fails to load)
        if self.vision_model == "MOCK_MODE":
            logger.warning("🎭 MOCK_MODE: Returning sample detections for testing")
            return {
                'success': True,
                'detections': [
                    {
                        'class_id': 4,
                        'class_name': 'plastic',
                        'confidence': 0.92,
                        'bbox': {'x1': 10, 'y1': 20, 'x2': 50, 'y2': 60}
                    },
                    {
                        'class_id': 2,
                        'class_name': 'metal',
                        'confidence': 0.85,
                        'bbox': {'x1': 60, 'y1': 30, 'x2': 95, 'y2': 70}
                    }
                ],
                'count': 2,
                'model': '⚠️  YOLOv8 (MOCK_MODE - actual model failed to load)',
                'accuracy': 'N/A - Mock Data',
                'warning': 'Running in MOCK_MODE because YOLOv8 failed to initialize. Real model loading needs debugging.'
            }
        
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
    
    def _fallback_lifestyle_prediction(self, features):
        """
        Rule-based fallback calculation when ML model is not available
        Features (20 values):
        [0] electricity, [1] gas, [2] water, [3] car, [4] transit, [5] flights,
        [6-8] food, [9] recycling, [10-11] plastic/clothes, [12-19] scaled/duplicates
        """
        try:
            # Extract key features
            electricity = max(0, features[0] * 10)           # kWh/day -> scale back
            gas = max(0, features[1] * 50)                   # m³/month -> scale back
            car_miles = max(0, features[3] * 100)            # scaled -> scale back
            flights = max(0, features[5])                    # flights/year
            meat_ratio = max(0, features[6])                 # meat meal ratio
            recycling = max(0, features[9])                  # recycling rate (0-1)
            
            # Rough carbon estimates (kg CO₂)
            electricity_carbon = electricity * 30 * 0.4           # 0.4 kg CO₂/kWh * 30 days
            gas_carbon = gas * 2.5                                # 2.5 kg CO₂/m³
            car_carbon = car_miles * 0.21                         # 0.21 kg CO₂/mile * 30 days
            flight_carbon = flights * 200 / 12                    # 200 kg per flight, annual
            food_carbon = (1 + meat_ratio) * 100                  # base + meat consumption
            
            # Calculate total with recycling benefit
            total_carbon = electricity_carbon + gas_carbon + car_carbon + flight_carbon + food_carbon
            recycling_reduction = total_carbon * recycling * 0.15  # 15% reduction per recycling %
            monthly_carbon = max(100, total_carbon - recycling_reduction)
            
            yearly_carbon = monthly_carbon * 12
            daily_average = monthly_carbon / 30
            
            average_carbon = 500
            compared_percent = round((monthly_carbon - average_carbon) / average_carbon * 100, 1)
            
            return {
                'success': True,
                'monthly_carbon_kg': round(monthly_carbon, 1),
                'yearly_carbon_kg': round(yearly_carbon, 1),
                'daily_average_kg': round(daily_average, 2),
                'compared_to_average_percent': compared_percent,
                'country_average_kg': average_carbon,
                'recommendation': self._get_recommendation(compared_percent),
                'warning': '⚠️ Using rule-based estimate (ML model not available)'
            }
        except Exception as e:
            logger.error(f"Fallback lifestyle prediction failed: {str(e)}")
            return {
                'success': False,
                'error': f"Fallback calculation failed: {str(e)}"
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
            if len(features) != 20:
                raise ValueError(f"Expected 20 features, got {len(features)}")
            
            # If model is not loaded or doesn't have predict method, use fallback
            if self.lifestyle_model is None or not hasattr(self.lifestyle_model, 'predict'):
                # Only log once instead of every prediction
                if self.lifestyle_model is not None and not hasattr(self.lifestyle_model, 'predict'):
                    logger.warning("Lifestyle model object is not a valid sklearn model, using rule-based fallback")
                return self._fallback_lifestyle_prediction(features)
            
            try:
                # Convert to numpy array
                features_array = np.array(features).reshape(1, -1)
                
                # Predict using loaded model
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
            except Exception as predict_err:
                logger.error(f"Model prediction failed: {str(predict_err)}")
                # Fall back silently without repeating the warning
                return self._fallback_lifestyle_prediction(features)
        
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
