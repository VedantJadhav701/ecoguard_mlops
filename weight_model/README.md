# Weight Estimator Model

## Overview
This is a **deterministic, rule-based weight estimator** (not ML-based) that predicts object weight from:
- Visual detection (bounding box size)
- Material classification (from YOLO)
- Base weight priors (dataset calibrated)

## Formula
```
weight_g = base_weight × (area_ratio / reference_ratio)
weight_g = max(min_weight, min(weight_g, max_weight))
```

## Files
- `weight_estimator.pkl` - Pickled estimator object (Python)
- `weight_estimator_config.json` - Configuration parameters
- `README.md` - This file

## Usage

### Python (with pickle)
```python
import pickle

with open('weight_estimator.pkl', 'rb') as f:
    estimator = pickle.load(f)

result = estimator.estimate_weight(
    bbox=(100, 100, 250, 350),
    image_shape=(720, 1280),
    material='plastic'
)

print(f"Weight: {result['weight_g']}g ({result['weight_kg']}kg)")
```

### Configuration (JSON)
```python
import json

with open('weight_estimator_config.json', 'r') as f:
    config = json.load(f)

base_weights = config['base_weights']
reference_ratio = config['reference_area_ratio']
```

## Material Base Weights (grams)
- plastic: 25g
- glass: 250g
- metal: 50g
- paper: 15g
- cardboard: 40g
- trash: 30g

## Parameters
- reference_area_ratio: 0.3 (30% of image = base weight)
- min_weight_g: 2g
- max_weight_g: 500g

## Integration
Use this estimator in the EcoGuard pipeline:
1. YOLOv8 detects objects → bbox + class
2. WeightEstimator predicts weight in grams
3. CarbonCalculator computes CO₂ emissions
4. Frontend displays: Material + Weight(g) + CO₂(kg)

## Performance
- Inference time: <1ms per object (no GPU needed)
- Stability: 100% deterministic
- Accuracy: Calibrated from real dataset
- Compatibility: Pure Python pickle format
