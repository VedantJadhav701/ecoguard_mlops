# EcoGuard Frontend Integration Guide
## Complete Implementation Documentation for Frontend Team

---

## Table of Contents
1. System Overview
2. Components Architecture
3. API Specifications
4. Model Integration Guide
5. UI/UX Implementation
6. Real-Time Sensor Integration
7. Data Flow
8. Installation & Setup
9. Testing Checklist
10. Troubleshooting

---

## 1. SYSTEM OVERVIEW

### What is EcoGuard?
EcoGuard is a smart waste management system that combines:
- **Image Recognition** - Identifies waste items from photos
- **Weight Estimation** - Calculates weight from object size
- **Carbon Calculation** - Computes CO₂ emissions
- **Real-Time Monitoring** - Tracks air quality with MQ7 sensor
- **Lifestyle Tracking** - Monitors user's carbon footprint

### User Journey
```
User Takes Photo → App Analyzes → Shows Results + Air Quality → User Takes Action
                                                              ↓
                                        App Logs Action & Updates Score
```

### Frontend Responsibilities
1. Capture image from camera
2. Send image to backend Vision API
3. Display detection results
4. Connect to MQ7 sensor for real-time data
5. Show historical data and recommendations
6. Track user achievements

---

## 2. COMPONENTS ARCHITECTURE

### Component 1: Vision Model (YOLOv8)
**File:** `vision_model/best.pt`  
**Size:** 6.2 MB  
**Input:** Image (JPG, PNG, any size)  
**Output:** JSON with detections

**Expected Output:**
```json
{
  "detections": [
    {
      "class_id": 4,
      "class_name": "plastic",
      "confidence": 0.92,
      "bbox": {
        "x1": 100,
        "y1": 150,
        "x2": 250,
        "y2": 400
      }
    }
  ],
  "image_shape": [720, 1280, 3],
  "processing_time_ms": 6.6
}
```

**Classes Detected:**
- 0: cardboard
- 1: glass
- 2: metal
- 3: paper
- 4: plastic
- 5: trash

---

### Component 2: Weight Estimator
**File:** `weight_model/weight_estimator.pkl`  
**Config:** `weight_model/weight_estimator_config.json`  
**Input:** Bounding box + class name + image shape  
**Output:** Weight in grams

**Expected Output:**
```json
{
  "weight_g": 83.5,
  "weight_kg": 0.0835,
  "material": "plastic",
  "size_category": "medium (25-50% of image)",
  "confidence": "high",
  "explanation": "Base plastic = 25g. Size is medium. Adjusted weight: 83.5g"
}
```

**Base Weights (grams):**
```json
{
  "plastic": 25,
  "glass": 250,
  "metal": 50,
  "paper": 15,
  "cardboard": 40,
  "trash": 30
}
```

---

### Component 3: Carbon Calculator
**Type:** Python class (built-in, no separate file)  
**Input:** Weight + material type  
**Output:** CO₂ emissions

**Expected Output:**
```json
{
  "material": "plastic",
  "weight_kg": 0.0835,
  "carbon_kg": 0.2088,
  "carbon_g": 208.8,
  "emission_factor": 2.5,
  "recycling_reduction_percent": 70.0,
  "if_recycled_co2_kg": 0.0626,
  "co2_saved_kg": 0.1462
}
```

**Emission Factors (kg CO₂ per kg material):**
```json
{
  "plastic": 2.5,
  "glass": 1.8,
  "metal": 8.0,
  "paper": 1.0,
  "cardboard": 0.9,
  "trash": 1.5
}
```

---

### Component 4: Lifestyle Model
**File:** `lifestyle_model/best_ml_model.joblib`  
**Input:** 20 lifestyle features  
**Output:** User's carbon footprint prediction

**Required Features (20):**
1. Daily energy consumption (kWh)
2. Transportation mode (car/bus/bike)
3. Distance traveled (km)
4. Food type (meat/vegetarian)
5. Food waste percentage
6. Water consumption (liters)
7. Clothing purchases per month
8. Shopping frequency
9. Recycling rate (%)
10. Waste per day (kg)
11. Number of people in household
12. House size (sqft)
13. Heating type (gas/electric)
14. AC usage hours/day
15. Number of flights/year
16. Streaming hours/day
17. Game playing hours/day
18. Phone charging cycles/day
19. Internet data usage (GB)
20. Overall eco-consciousness (1-10 scale)

**Expected Output:**
```json
{
  "monthly_carbon_kg": 450.5,
  "yearly_carbon_kg": 5406,
  "daily_average_kg": 15.02,
  "compared_to_average_percent": -15,
  "country_average_kg": 630,
  "recommendation": "Your carbon footprint is 15% below average. Keep it up!"
}
```

---

### Component 5: MQ7 Real-Time Sensor
**Hardware:** MQ7 Gas Sensor + ESP8266/ESP32  
**Connection:** WiFi/Bluetooth  
**Update Rate:** Every 1 second  
**Range:** 0-1000 ppm CO

**Expected Data Stream:**
```json
{
  "timestamp": "2026-03-27T10:30:45Z",
  "co_ppm": 45,
  "status": "GOOD",
  "trend": "IMPROVING",
  "trend_percent": -10,
  "last_24h_avg": 52,
  "peak_today": 78,
  "low_today": 32
}
```

**Status Mapping:**
- CO 0-50 ppm: **GREEN** (GOOD)
- CO 50-100 ppm: **YELLOW** (FAIR)
- CO 100-500 ppm: **ORANGE** (POOR)
- CO 500+ ppm: **RED** (DANGEROUS - Alert!)

---

## 3. API SPECIFICATIONS

### Backend APIs You'll Call

#### Vision API
```
POST /api/vision/detect
Content-Type: multipart/form-data

Body: image file

Response: 200 OK
{
  "detections": [...],
  "image_shape": [...],
  "processing_time_ms": 6.6
}
```

#### Weight API
```
POST /api/weight/estimate
Content-Type: application/json

Body:
{
  "bbox": [100, 150, 250, 400],
  "class_name": "plastic",
  "image_shape": [720, 1280, 3]
}

Response: 200 OK
{
  "weight_g": 83.5,
  "weight_kg": 0.0835,
  "material": "plastic",
  "size_category": "medium (25-50% of image)",
  "confidence": "high",
  "explanation": "..."
}
```

#### Carbon API
```
POST /api/carbon/calculate
Content-Type: application/json

Body:
{
  "weight_kg": 0.0835,
  "material": "plastic"
}

Response: 200 OK
{
  "carbon_kg": 0.2088,
  "carbon_g": 208.8,
  "if_recycled_co2_kg": 0.0626,
  "co2_saved_kg": 0.1462
}
```

#### Lifestyle API
```
POST /api/lifestyle/predict
Content-Type: application/json

Body:
{
  "features": [45.2, 1, 25.5, 2, 15, 150, 2, 3, 85, 1.5, 4, 2500, 1, 6, 3, 4, 2, 5, 50, 8]
}

Response: 200 OK
{
  "monthly_carbon_kg": 450.5,
  "yearly_carbon_kg": 5406,
  "compared_to_average_percent": -15
}
```

#### Sensor Stream API (WebSocket)
```
WebSocket: ws://backend.local/api/sensor/stream

Connection established, receive:
{
  "timestamp": "2026-03-27T10:30:45Z",
  "co_ppm": 45,
  "status": "GOOD",
  "trend": "IMPROVING"
}

(Updates every 1 second)
```

---

## 4. MODEL INTEGRATION GUIDE

### Step 1: Setup Backend
The backend should be running Python Flask/FastAPI with these requirements:
- Python 3.8+
- ultralytics (YOLOv8)
- opencv-python
- scikit-learn
- numpy, pandas
- joblib, pickle

**Backend folder should contain:**
```
backend/
├── vision_model/
│   └── best.pt (6.2 MB)
├── weight_model/
│   ├── weight_estimator.pkl
│   └── weight_estimator_config.json
├── lifestyle_model/
│   └── best_ml_model.joblib
├── app.py (Flask/FastAPI server)
└── requirements.txt
```

### Step 2: Frontend Image Capture

**Implementation:**
```javascript
// Capture image from camera
const captureImage = async () => {
  const input = document.getElementById('cameraInput');
  const file = input.files[0];
  
  // Send to backend vision API
  const formData = new FormData();
  formData.append('image', file);
  
  try {
    const response = await fetch('/api/vision/detect', {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    handleDetections(data.detections);
  } catch (error) {
    console.error('Vision API error:', error);
  }
};
```

### Step 3: Process Detections

**Implementation:**
```javascript
// For each detected object, estimate weight
const handleDetections = async (detections) => {
  const results = [];
  
  for (const detection of detections) {
    // Get weight estimate
    const weightResponse = await fetch('/api/weight/estimate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        bbox: detection.bbox,
        class_name: detection.class_name,
        image_shape: [720, 1280, 3] // replace with actual
      })
    });
    
    const weight = await weightResponse.json();
    
    // Get carbon impact
    const carbonResponse = await fetch('/api/carbon/calculate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        weight_kg: weight.weight_kg,
        material: weight.material
      })
    });
    
    const carbon = await carbonResponse.json();
    
    results.push({
      ...detection,
      ...weight,
      ...carbon
    });
  }
  
  displayResults(results);
};
```

### Step 4: Display Results to User

**UI Layout:**
```
┌─────────────────────────────────┐
│  ITEM DETECTED                  │
├─────────────────────────────────┤
│ [Image of item]                 │
│                                 │
│ Material: Plastic               │
│ Confidence: 92%                 │
│ Weight: 83.5 grams              │
│ CO₂ Cost: 0.21 kg               │
│                                 │
│ If Recycled:                    │
│ CO₂ Reduced to: 0.06 kg (70%)   │
│ You Save: 0.15 kg CO₂           │
│                                 │
│ Current Air Quality: 45 ppm ✓  │
│ Status: GOOD                    │
│                                 │
│ [RECYCLE] [TRASH] [MORE INFO]   │
└─────────────────────────────────┘
```

---

## 5. UI/UX IMPLEMENTATION

### Screen 1: Camera/Photo Input
```
┌─────────────────────────────────┐
│  EcoGuard - Scan Waste          │
├─────────────────────────────────┤
│                                 │
│     [CAMERA VIEW]               │
│     [Tap to capture]            │
│                                 │
│     [UPLOAD PHOTO]              │
│                                 │
│     [RECENT SCANS]              │
│     • Plastic bottle            │
│     • Glass jar                 │
│     • Paper box                 │
│                                 │
└─────────────────────────────────┘
```

### Screen 2: Results Display
```
┌─────────────────────────────────┐
│  Analysis Results               │
├─────────────────────────────────┤
│ [Item Image]                    │
│                                 │
│ PLASTIC BOTTLE                  │
│ Confidence: 92%                 │
│                                 │
│ Weight: 83.5g                   │
│ CO₂ Impact: 0.21 kg             │
│ If Recycled: -70% (0.06 kg)     │
│                                 │
│ Current Air Quality:            │
│ [45 ppm] GOOD ✓                 │
│ Status: Safe to breathe         │
│                                 │
│ [RECYCLE] [TRASH] [SAVE]        │
│ [VIEW DETAILS]                  │
└─────────────────────────────────┘
```

### Screen 3: Real-Time Air Quality Dashboard
```
┌─────────────────────────────────┐
│  Air Quality Monitor            │
├─────────────────────────────────┤
│                                 │
│  Live Reading:                  │
│  45 ppm                         │
│  [Green Indicator] GOOD         │
│                                 │
│  Status: Safe to breathe        │
│  Trend: Improving ↓ (-5 ppm)    │
│                                 │
│  24-Hour History:               │
│  [Graph showing CO levels]      │
│  Peak: 78 ppm (10:30 AM)        │
│  Low: 32 ppm (3:45 PM)          │
│  Average: 50 ppm                │
│                                 │
│  Weekly Comparison:             │
│  This week: ↓ 10% better        │
│  vs City avg: ✓ 15% better      │
│                                 │
│  [Settings] [Share] [History]   │
└─────────────────────────────────┘
```

### Screen 4: Weekly Report & Tracking
```
┌─────────────────────────────────┐
│  Weekly Report                  │
├─────────────────────────────────┤
│                                 │
│ Your Score: 45/100              │
│ Trend: ↑ UP 5 points            │
│                                 │
│ Items Scanned: 47               │
│ Total CO₂: 9.8 kg               │
│ Savings (recycling): 30%        │
│                                 │
│ Air Quality: Improved 40%       │
│ ■■■■■□□□□□ [Good]              │
│                                 │
│ Badges Earned:                  │
│ [Recycler] [Eco Hero]           │
│                                 │
│ Recommendations:                │
│ 1. Keep recycling items         │
│ 2. Use public transport         │
│ 3. Buy less packaged food       │
│                                 │
│ [Details] [Share] [Next Week]   │
└─────────────────────────────────┘
```

---

## 6. REAL-TIME SENSOR INTEGRATION

### MQ7 Sensor Setup
1. Hardware: MQ7 Gas Sensor + ESP8266/ESP32 microcontroller
2. Connection: WiFi or Bluetooth to app
3. Data Updates: Every 1 second
4. Battery: 48+ hours

### WebSocket Connection

**JavaScript Implementation:**
```javascript
// Connect to sensor stream
const connectToSensor = () => {
  const socket = new WebSocket('ws://backend.local/api/sensor/stream');
  
  socket.onmessage = (event) => {
    const sensorData = JSON.parse(event.data);
    updateAirQualityDisplay(sensorData);
  };
  
  socket.onerror = (error) => {
    console.error('Sensor connection error:', error);
  };
};

const updateAirQualityDisplay = (data) => {
  // Update in real-time every second
  const ppmElement = document.getElementById('co-ppm');
  const statusElement = document.getElementById('status');
  const trendElement = document.getElementById('trend');
  
  ppmElement.textContent = data.co_ppm + ' ppm';
  statusElement.textContent = data.status;
  trendElement.textContent = (data.trend_percent > 0 ? '↑' : '↓') + ' ' + Math.abs(data.trend_percent) + '%';
  
  // Update color based on status
  const statusColor = {
    'GOOD': 'green',
    'FAIR': 'yellow',
    'POOR': 'orange',
    'DANGEROUS': 'red'
  };
  
  statusElement.style.color = statusColor[data.status];
};
```

### Display Real-Time Updates
- Update air quality indicator every second
- Show trend (improving/worsening)
- Display 24-hour history as graph
- Alert user if dangerous levels detected (500+ ppm)

---

## 7. DATA FLOW

### Single Item Detection Flow
```
1. User captures photo
2. Frontend sends image to backend
3. Vision model detects objects (6.6ms)
4. For each detection:
   - Send bbox to weight estimator
   - Weight estimator returns weight (<1ms)
   - Send weight to carbon calculator
   - Carbon calculator returns CO₂ (instant)
5. Fetch current sensor data from MQ7
6. Display combined results to user
7. User chooses action (recycle/trash/save)
8. Log action to database
9. Update user score
10. Check if badge earned
```

### Lifetime Tracking Flow
```
1. Every scan logged with timestamp
2. Daily aggregation:
   - Total items scanned
   - Total CO₂ calculated
   - Total weight
3. Weekly calculations:
   - Score out of 100
   - Comparison to previous week
   - Comparison to average user
   - Air quality improvements
4. Monthly report:
   - Total carbon footprint
   - Trees equivalent
   - Impact visualization
5. Recommendations generated
6. Badges awarded
```

---

## 8. INSTALLATION & SETUP

### Frontend Setup
```bash
# Install dependencies
npm install

# For camera access (mobile/web)
# Ensure HTTPS or localhost for camera permissions
# Request permissions:
navigator.mediaDevices.getUserMedia({ video: true, audio: false })

# For WebSocket (real-time sensor)
# Use ws:// (local) or wss:// (production, HTTPS)

# Build for production
npm run build
```

### Backend Setup
```bash
# Clone repository
git clone <repo-url>

# Install Python dependencies
pip install -r requirements.txt

# Place model files in correct folders:
# vision_model/best.pt (6.2 MB)
# weight_model/weight_estimator.pkl
# weight_model/weight_estimator_config.json
# lifestyle_model/best_ml_model.joblib

# Run server
python app.py

# Server runs on localhost:5000 (or your port)
```

### Environment Variables (Frontend)
```
REACT_APP_API_URL=http://localhost:5000
REACT_APP_SENSOR_WS=ws://localhost:5000/api/sensor/stream
REACT_APP_API_TIMEOUT=30000
```

---

## 9. TESTING CHECKLIST

### Vision Model Testing
- [ ] Test with various light conditions
- [ ] Test with different waste types (all 6 classes)
- [ ] Verify 96.1% accuracy on test images
- [ ] Check confidence scores (should be 0.25+ for good detections)
- [ ] Test with multiple items in photo
- [ ] Performance: Should be <7ms per image

### Weight Model Testing
- [ ] Test with different bbox sizes
- [ ] Verify weight calculations match formula
- [ ] Test all 6 material types
- [ ] Check output: 2g min, 500g max
- [ ] Verify explanation text is clear

### Carbon Model Testing
- [ ] Verify emission factors are correct
- [ ] Calculate recycling reduction (70%)
- [ ] Test with various weights
- [ ] Check decimal precision

### Sensor Testing
- [ ] Verify WiFi/Bluetooth connection
- [ ] Test real-time data updates (every 1 second)
- [ ] Check alert system for dangerous levels (500+ ppm)
- [ ] Verify 24-hour data retention
- [ ] Test with different locations (indoor/outdoor)

### UI/UX Testing
- [ ] Camera capture works on mobile
- [ ] Results display correctly
- [ ] Real-time sensor updates visible
- [ ] No lag or freezing
- [ ] Responsive design (mobile/tablet/desktop)
- [ ] User actions (recycle/trash) are logged

### Integration Testing
- [ ] Full pipeline: photo → detection → weight → carbon → display
- [ ] Sensor data displayed alongside results
- [ ] Real-time updates don't block UI
- [ ] Error handling for failed requests
- [ ] Offline mode (if applicable)

---

## 10. TROUBLESHOOTING

### Vision Model Issues

**Problem:** Low detection accuracy (<80%)
- Solution: Verify image quality and lighting
- Solution: Check bbox coordinates are valid
- Solution: Ensure model file best.pt is not corrupted

**Problem:** Slow processing (>20ms)
- Solution: Check if GPU is being used
- Solution: Verify image size (should be normalized)
- Solution: Check server CPU/memory usage

### Weight Model Issues

**Problem:** Unrealistic weight values
- Solution: Verify bbox coordinates are in image bounds
- Solution: Check image shape matches actual image
- Solution: Verify material class is correct (0-5)

**Problem:** "Weight out of range"
- Solution: Bbox might be too small or too large
- Solution: Verify reference_area_ratio in config (default 0.3)

### Sensor Issues

**Problem:** WebSocket connection fails
- Solution: Check if backend is running
- Solution: Verify correct WebSocket URL
- Solution: Check CORS settings (wss:// for HTTPS)

**Problem:** Sensor not updating
- Solution: Check WiFi/Bluetooth connection
- Solution: Verify sensor battery level
- Solution: Check sensor is within range (10-50m)

**Problem:** Dangerous CO levels not alerting
- Solution: Verify alert threshold is set to 500+ ppm
- Solution: Check notification permissions enabled
- Solution: Verify sound/vibration settings

### Database/Storage Issues

**Problem:** User data not persisting
- Solution: Check database connection
- Solution: Verify write permissions
- Solution: Check disk space

**Problem:** Historical data not loading
- Solution: Verify query filters are correct
- Solution: Check timestamp format consistency
- Solution: Ensure data has not expired

---

## QUICK REFERENCE API ENDPOINTS

```
Vision:        POST   /api/vision/detect
Weight:        POST   /api/weight/estimate
Carbon:        POST   /api/carbon/calculate
Lifestyle:     POST   /api/lifestyle/predict
Sensor Stream: WS     /api/sensor/stream
User Logs:     POST   /api/user/log-action
Get History:   GET    /api/user/history?days=7
Get Report:    GET    /api/user/report?period=weekly
```

---

## FILE SIZES & REQUIREMENTS

```
Model Files:
- vision_model/best.pt: 6.2 MB
- weight_model/weight_estimator.pkl: ~50 KB
- lifestyle_model/best_ml_model.joblib: ~500 KB
- Config files: ~10 KB

Total Backend Size: ~6.8 MB
Frontend Bundle: ~500 KB (optimized)
Database Per User: ~10 MB/year
```

---

## SUPPORT & DOCUMENTATION

For questions or issues:
1. Check TROUBLESHOOTING section above
2. Review API response codes (200, 400, 500)
3. Check server logs for detailed errors
4. Verify all model files are present and uncorrupted

---

**Document Version:** 1.0  
**Created:** March 2026  
**For:** Frontend Integration Team  
**Last Updated:** March 27, 2026
