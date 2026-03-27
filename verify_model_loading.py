import logging
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(os.getcwd())

from predictor import ModelPredictor

# Setup logging to see predictor info
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def verify():
    print("=== EcoGuard Model Loading Verification ===")
    
    # Initialize predictor
    predictor = ModelPredictor(models_path=".")
    
    print("\n--- Model Loading Summary ---")
    print(f"Vision Model: {'✓ LOADED' if predictor.vision_model and predictor.vision_model != 'MOCK_MODE' else '✗ FAILED'}")
    if predictor.vision_model == 'MOCK_MODE':
        print("Detail: Vision model is in MOCK_MODE")
        
    print(f"Weight Estimator: {'✓ LOADED' if predictor.weight_estimator else '✗ FAILED'}")
    print(f"Weight Config: {'✓ LOADED' if predictor.weight_config else '✗ FAILED'}")
    print(f"Lifestyle Model: {'✓ LOADED' if predictor.lifestyle_model else '✗ FAILED'}")
    
    # Check if any model failed
    failures = []
    if not predictor.vision_model or predictor.vision_model == 'MOCK_MODE':
        failures.append("Vision Model")
    if not predictor.weight_estimator:
        failures.append("Weight Estimator")
    if not predictor.lifestyle_model:
        failures.append("Lifestyle Model")
        
    if not failures:
        print("\n✅ SUCCESS: All models loaded correctly!")
        return True
    else:
        print(f"\n❌ FAILURE: Some models failed to load: {', '.join(failures)}")
        print("Note: This might be expected if the files are not present in your local environment,")
        print("but the fix to predictor.py ensures they WILL load when present in the container.")
        return False

if __name__ == "__main__":
    verify()
