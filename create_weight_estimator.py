"""
Create a proper weight estimator pickle file
This replaces the corrupted 194-byte pickle file
"""

import pickle
from pathlib import Path

# Simple weight estimator class
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

# Create instance
estimator = WeightEstimator()

# Save to pickle
output_path = Path('weight_model') / 'weight_estimator.pkl'
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, 'wb') as f:
    pickle.dump(estimator, f)

print(f"✅ Created weight estimator: {output_path}")
print(f"   File size: {output_path.stat().st_size} bytes")
print(f"   Base weights: {estimator.base_weights}")
