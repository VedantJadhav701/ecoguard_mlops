# YOLOv8 Trash Detection Model

## Overview
This folder contains the trained YOLOv8 Nano object detection model for trash/waste classification. The model can detect and classify 6 types of waste materials in images and video streams.

## Files
- **best.pt** - Trained YOLOv8 Nano model (6.2 MB) - 96.1% mAP
- **config.yaml** - Model configuration and class definitions
- **README.md** - This file

## Model Specifications
- **Architecture**: YOLOv8 Nano
- **Input Size**: 640x640 pixels (auto-resizable)
- **Classes**: 6 (cardboard, glass, metal, paper, plastic, trash)
- **Parameters**: 3.01M
- **mAP50**: 96.1% (Excellent)
- **mAP50-95**: 96.1%
- **Inference Speed**: 6.6ms per image (~150 FPS)

## Supported Classes
1. **Cardboard** - mAP: 98.9%
2. **Glass** - mAP: 95.9%
3. **Metal** - mAP: 97.9%
4. **Paper** - mAP: 98.4%
5. **Plastic** - mAP: 93.9%
6. **Trash** - mAP: 91.8%

## Usage

### Python Integration
```python
from ultralytics import YOLO

# Load model
model = YOLO('best.pt')

# Predict on image
results = model.predict(source='image.jpg', conf=0.25)

# Get detections
for result in results:
    boxes = result.boxes
    for box in boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        class_name = result.names[class_id]
        print(f"{class_name}: {confidence*100:.1f}%")
```

### Command Line
```bash
yolo detect predict model=best.pt source=image.jpg conf=0.25
```

## Performance Metrics
- Training Time: 0.484 hours (50 epochs)
- Dataset: 2,527 images (2,021 train, 506 val)
- Precision: 92.8%
- Recall: 88.4%
- Real-time Capability: ✓ (22-25 FPS on RTX 3050)

## Requirements
- Python 3.8+
- torch 2.5.1+
- ultralytics 8.4.18+
- opencv-python
- numpy

## Installation
```bash
pip install ultralytics torch opencv-python numpy
```

## Notes
- Model is CUDA-optimized for GPU acceleration
- Works with CPU but slower inference (~40-50ms per image)
- Recommended confidence threshold: 0.25
- IOU threshold for NMS: 0.7

## Integration
See `../INTEGRATION_GUIDE.md` for combining this model with the weight estimator.

## Contact
For issues or questions, contact the Data Science team.
