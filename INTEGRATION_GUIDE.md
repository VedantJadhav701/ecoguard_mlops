# 🔗 EcoGuard Integration Guide - Vision + Weight + Carbon

## Architecture Overview

```
IMAGE INPUT
    ↓
[VISION MODEL] YOLOv8 - Detects objects
    ↓ Outputs: bbox (x1,y1,x2,y2) + class_name + confidence
    ↓
[WEIGHT MODEL] WeightEstimator - Predicts weight from bbox
    ↓ Outputs: weight_g, weight_kg + explanation
    ↓
[CARBON MODEL] CarbonCalculator - Computes CO₂ from weight
    ↓ Outputs: carbon_kg, carbon_g, recycling_impact
    ↓
[FRONTEND] Display results to user
```

## THREE COMPONENT PIPELINE (NO Different Models)

### ✅ Component 1: Vision Model (YOLOv8)
**File:** `vision_model/best.pt`  
**Purpose:** Detect waste objects in images  
**Input:** Image (any size)  
**Output:**
```python
{
    'class_name': 'plastic',      # cardboard, glass, metal, paper, plastic, trash
    'confidence': 0.92,            # Detection confidence
    'bbox': (x1, y1, x2, y2),      # Bounding box coordinates
}
```

### ✅ Component 2: Weight Model (WeightEstimator)
**File:** `weight_model/weight_estimator.pkl`  
**Purpose:** Estimate weight from bounding box size  
**Input:** bbox + class_name + image_shape  
**Output:**
```python
{
    'weight_g': 83.5,              # Weight in GRAMS ← Important!
    'weight_kg': 0.0835,
    'material': 'plastic',
    'size_category': 'medium (25-50% of image)',
    'explanation': 'Base plastic = 25g. Size is medium. Adjusted weight: 83.5g'
}
```

### ✅ Component 3: Carbon Calculator
**File:** Built-in Python class (no separate file)  
**Purpose:** Calculate CO₂ emissions from weight  
**Input:** weight_g + material_type  
**Output:**
```python
{
    'carbon_kg': 0.2088,           # CO₂ in kg
    'carbon_g': 208.8,
    'weight_kg': 0.0835,
    'emission_factor': 2.5,        # kg CO₂ per kg material
    'recycling_reduction_percent': 70.0
}
```

## Integration Flow (Step-by-Step)

```python
# Step 1: Load all models once (at startup)
import pickle
from pathlib import Path

# Load YOLOv8
from ultralytics import YOLO
vision_model = YOLO('vision_model/best.pt')

# Load WeightEstimator
with open('weight_model/weight_estimator.pkl', 'rb') as f:
    weight_estimator = pickle.load(f)

# Load Carbon Calculator (Python class - no file needed)
from carbon_calculator import CarbonEmissionCalculator
carbon_calculator = CarbonEmissionCalculator()

# Step 2: Process image
image_path = 'image.jpg'

# Step 2a: Vision - Detect objects
results = vision_model.predict(source=image_path, conf=0.25)
detections = [
    {
        'class_name': 'plastic',
        'bbox': (100, 100, 250, 350),
        'confidence': 0.92
    },
    # ... more detections
]

# Step 2b: Weight - Estimate for each detection
image = cv2.imread(image_path)
img_shape = image.shape  # (height, width, channels)

for detection in detections:
    weight_result = weight_estimator.estimate_weight(
        bbox=detection['bbox'],
        image_shape=img_shape,
        material=detection['class_name']
    )
    detection['weight_g'] = weight_result['weight_g']
    detection['weight_kg'] = weight_result['weight_kg']

# Step 2c: Carbon - Calculate emissions
for detection in detections:
    carbon_result = carbon_calculator.calculate_emission(
        weight_g=detection['weight_g'],
        material=detection['class_name']
    )
    detection['carbon_kg'] = carbon_result['carbon_kg']
    detection['carbon_g'] = carbon_result['carbon_g']

# Step 3: Return to frontend
final_result = {
    'detections': detections,
    'total_weight_g': sum(d['weight_g'] for d in detections),
    'total_carbon_kg': sum(d['carbon_kg'] for d in detections)
}
```

## Complete Integration Example (Simplified)

```python
def analyze_waste(image_path):
    """
    Complete analysis: Image → Detection → Weight → Carbon
    This is the ONLY function the frontend needs to call
    """
    
    # 1. VISION: Detect objects
    image = cv2.imread(image_path)
    results = vision_model.predict(source=image_path, conf=0.25)
    
    detections = []
    for box in results[0].boxes:
        detections.append({
            'class_name': CLASSES[int(box.cls[0])],
            'confidence': float(box.conf[0]),
            'bbox': tuple(box.xyxy[0].cpu().numpy().astype(int))
        })
    
    # 2. WEIGHT: Estimate for each detection
    img_shape = image.shape
    for det in detections:
        weight = weight_estimator.estimate_weight(
            bbox=det['bbox'],
            image_shape=img_shape,
            material=det['class_name']
        )
        det['weight_g'] = weight['weight_g']
    
    # 3. CARBON: Calculate emissions
    for det in detections:
        carbon = carbon_calculator.calculate_emission(
            weight_g=det['weight_g'],
            material=det['class_name']
        )
        det['carbon_kg'] = carbon['carbon_kg']
    
    # 4. AGGREGATE & RETURN
    return {
        'success': True,
        'detections': detections,
        'totals': {
            'items': len(detections),
            'weight_g': sum(d['weight_g'] for d in detections),
            'carbon_kg': sum(d['carbon_kg'] for d in detections)
        }
    }

# Frontend calls it like this:
result = analyze_waste('user_image.jpg')
print(f"Detected items: {result['totals']['items']}")
print(f"Total weight: {result['totals']['weight_g']}g")
print(f"Total CO₂: {result['totals']['carbon_kg']}kg")
```

## Model Files Location

```
C:\Users\HP\projects\Carbon Emission\
├── vision_model/
│   ├── best.pt              ← YOLOv8 model (225 MB)
│   └── README.md
│
└── weight_model/
    ├── weight_estimator.pkl ← WeightEstimator (45 KB)
    ├── weight_estimator_config.json
    └── README.md
```

## Loading Models (Python)

```python
# =============================================
# VISION MODEL (YOLOv8)
# =============================================
from ultralytics import YOLO

vision_model = YOLO('vision_model/best.pt')
# Inference: 50-100ms per image (CPU)

# =============================================
# WEIGHT MODEL (WeightEstimator)
# =============================================
import pickle

with open('weight_model/weight_estimator.pkl', 'rb') as f:
    weight_estimator = pickle.load(f)
# Inference: <1ms per object (CPU)

# =============================================
# CARBON CALCULATOR (Python Class)
# =============================================
# No loading - just define the class:
class CarbonEmissionCalculator:
    def calculate_emission(self, weight_g, material):
        factor = CARBON_FACTORS[material]
        return {'carbon_kg': (weight_g / 1000) * factor}

carbon_calc = CarbonEmissionCalculator()
# Inference: <1ms per calculation (CPU)
```

## Frontend Integration (What to Pass)

**Input to Backend:**
```json
{
  "image_file": "user_upload.jpg"  // Raw image file
}
```

**Output from Backend:**
```json
{
  "success": true,
  "detections": [
    {
      "material": "plastic",
      "weight_g": 83.5,
      "weight_kg": 0.0835,
      "carbon_kg": 0.2088,
      "confidence": 0.92
    }
  ],
  "totals": {
    "items": 1,
    "weight_g": 83.5,
    "carbon_kg": 0.2088,
    "recycling_saves_kg": 0.1462
  }
}
```

## Key Points - NO Different Models!

✅ **ONE Vision Model** - YOLOv8 (detects 6 classes)  
✅ **ONE Weight Model** - WeightEstimator (estimates weight)  
✅ **ONE Carbon Calculator** - Python class (computes CO₂)  

They work **sequentially as a pipeline**, not independently.

## Performance Benchmarks

| Component | Inference Time | GPU Required |
|-----------|---------------|--------------|
| Vision (YOLOv8) | 50-100ms | No (CPU OK) |
| Weight (Estimator) | <1ms × N objects | No (CPU only) |
| Carbon (Calculator) | <1ms × N objects | No (CPU only) |
| **Total** | **~100-150ms per image** | **No** |

## Integration Checklist for Frontend Dev

- [ ] Load `vision_model/best.pt` at startup
- [ ] Load `weight_model/weight_estimator.pkl` at startup  
- [ ] Create CarbonEmissionCalculator instance
- [ ] Implement single `analyze_waste(image_path)` function
- [ ] Call it with user-uploaded image
- [ ] Return JSON with detections + totals
- [ ] Display to user: Material + Weight(g) + CO₂(kg)

**Everything is already integrated and ready to use! 🚀**
