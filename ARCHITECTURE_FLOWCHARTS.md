# EcoGuard - Architecture & Flowcharts (Quick Reference)

## System Architecture Overview

```
                          ============ EcoGuard System ============
                                                  
    USER                                                            
      |
      |--- Takes Photo ---|                    |--- Opens App ---|
      |                   |                    |                 |
      V                   V                    V                 V
  
  [VISION MODEL]                          [MQ7 SENSOR]
  YOLOv8 Detection                        Real-time CO Monitor
  - Input: Image (any size)               - Input: Air (continuous)
  - Output: Object class                  - Output: CO ppm (0-1000)
  - Detection: 6 waste types              - Update: Every 1 second
  - Accuracy: 96.1%                       - Accuracy: ±5%
      |                                       |
      V                                       V
  
  [WEIGHT MODEL]                          [ALERT SYSTEM]
  Weight Estimator                        Safety & Tips
  - Input: Bbox + class                   - Input: CO levels
  - Output: Weight (grams)                - Output: Alerts + Tips
  - Formula: Rule-based                   - Status: Red/Yellow/Green
      |                                       |
      V                                       V
  
  [CARBON MODEL]                          [HISTORY TRACKER]
  CO2 Calculator                          24-Hour Data
  - Input: Weight + material              - Input: Sensor readings
  - Output: CO2 (kg)                      - Output: Trends + Changes
  - Emission factors: Per kg              - Display: Graphs + Reports
      |                                       |
      └──────────────────┬──────────────────┘
                         |
                         V
              [USER INTERFACE]
              Mobile App / Web
              
              Results Display:
              - Material: Plastic
              - Weight: 83.5g
              - CO2: 0.21 kg
              - Air Quality: 45 ppm (GOOD)
              - Recommendation: Recycle now!
              - Impact: Air will improve!
              
              Engagement Features:
              - Real-time alerts
              - 24-hour history
              - Weekly reports
              - Eco-badges
              - Friend comparisons

```

---

## Component Details Table

| Component | Input | Output | Technology | Speed | Data Source |
|-----------|-------|--------|-----------|-------|-------------|
| **Vision** | Photo | Object class, bbox, confidence | YOLOv8 | 6.6ms | RoboFlow (2,527 images) |
| **Weight** | Bbox + class | Weight in grams | Formula-based | <1ms | Real measurements |
| **Carbon** | Weight + material | CO2 in kg | Emission factors | Instant | LCA databases |
| **Lifestyle** | User data (20 features) | Carbon footprint | ML Regression | Instant | Kaggle (8K users) |
| **MQ7 Sensor** | Air | CO levels (ppm) | Electrochemical | 1 second | Real-time monitoring |

---

# FLOWCHART 1: Real-Time Image Analysis Pipeline

```
                    USER CAPTURES PHOTO
                           |
                           V
                    ┌─────────────┐
                    │   Vision    │
                    │   Model     │
                    │  (YOLOv8)   │
                    │  6.6ms      │
                    └──────┬──────┘
                           |
                 ┌─────────┴──────────┐
                 | Detects object:    |
                 | - Class: plastic   |
                 | - Confidence: 94%  |
                 | - Bbox: (x1,y1,x2) |
                 └─────────┬──────────┘
                           |
                           V
                    ┌──────────────┐
                    │    Weight    │
                    │  Estimator   │
                    │   (Formula)  │
                    │   <1ms       │
                    └──────┬───────┘
                           |
                 ┌─────────┴─────────┐
                 | Calculates:       |
                 | - Weight: 83.5g   |
                 | - Confidence: High|
                 | - Category: Medium|
                 └─────────┬─────────┘
                           |
                           V
                    ┌──────────────┐
                    │   Carbon     │
                    │ Calculator   │
                    │  (Instant)   │
                    └──────┬───────┘
                           |
                 ┌─────────┴──────────────┐
                 | Computes:              |
                 | - CO2: 0.21 kg         |
                 | - Recycling: -70%      |
                 | - Savings: 0.15 kg     |
                 └─────────┬──────────────┘
                           |
                           V
                    ┌──────────────────┐
                    │  Get Real-Time   │
                    │  Air Quality     │
                    │ from MQ7 Sensor  │
                    │  (Parallel)      │
                    └──────┬───────────┘
                           |
                 ┌─────────┴──────────────┐
                 | Current Status:        |
                 | - CO: 45 ppm           |
                 | - Status: GOOD         |
                 | - Trend: Improving (↓) |
                 └─────────┬──────────────┘
                           |
                           V
            ┌────────────────────────────┐
            │    DISPLAY RESULTS TO USER │
            ├────────────────────────────┤
            │ [ITEM]                     │
            │ - Material: Plastic        │
            │ - Weight: 83.5g            │
            │ - CO2 Cost: 0.21 kg        │
            │ - Confidence: 94%          │
            │                            │
            │ [AIR QUALITY]              │
            │ - Level: 45 ppm            │
            │ - Status: GOOD (Safe)      │
            │ - Trend: Improving         │
            │                            │
            │ [RECOMMENDATION]           │
            │ - Action: Recycle now!     │
            │ - Impact: Air will improve │
            │ - Earn Badge: Eco Champion │
            └────────────────────────────┘
                           |
                           V
            ┌────────────────────────────┐
            │  USER DECIDES ACTION       │
            │                            │
            │ [RECYCLE] [TRASH] [SAVE]   │
            └────────────────┬───────────┘
                             |
                   ┌─────────┴─────────┐
                   |                   |
                   V                   V
            [Action Logged]    [Monitor Sensor]
            [Score Updated]    [Track Changes]
            [Badge Earned?]    [Show Trends]

```

---

# FLOWCHART 2: Long-Term Lifestyle Carbon Tracking

```
              ╔══════════════════════════════════════════╗
              ║  USER OPENS APP (Daily/Weekly/Monthly)   ║
              ║  Activities: Photos, Tips, Tracking      ║
              ╚════════════════┬═════════════════════════╝
                               |
                   ┌───────────┴────────────┐
                   |                        |
         ┌─────────V────────┐     ┌────────V─────────┐
         │ IMAGE ANALYSIS   │     │  SENSOR READING  │
         │ Current Actions: │     │ Air Quality:     │
         │ - Waste scanned  │     │ - CO: 45 ppm     │
         │ - Items detected │     │ - Status: Good   │
         │ - Weight calc    │     │ - Trend: Changes │
         │ - CO2 computed   │     │ - 24hr history   │
         └────────┬────────┘     └────────┬─────────┘
                  |                       |
                  └───────────┬───────────┘
                              |
                    ┌─────────V──────────┐
                    │  DATA COLLECTION   │
                    │  (Daily Updates)   │
                    ├────────────────────┤
                    │ • Items scanned    │
                    │ • Weight totals    │
                    │ • CO2 calculated   │
                    │ • Air quality data │
                    │ • User actions     │
                    │ • Recycling count  │
                    └────────┬───────────┘
                             |
                    ┌────────V──────────┐
                    │   LIFESTYLE       │
                    │   ML MODEL        │
                    │ (Scikit-learn)    │
                    ├────────────────────┤
                    │ Analyzes:          │
                    │ • Energy use       │
                    │ • Transport habits │
                    │ • Food waste       │
                    │ • Shopping pattern │
                    │ • Recycling freq   │
                    │ • 20+ Features     │
                    │ • 8000+ profiles   │
                    └────────┬───────────┘
                             |
              ┌──────────────┴──────────────┐
              |                             |
              V                             V
      ┌─────────────────┐         ┌────────────────┐
      │  WEEKLY         │         │  SENSOR        │
      │  REPORT         │         │  TREND DATA    │
      ├─────────────────┤         ├────────────────┤
      │ Score: 45/100   │         │ CO Trend:      │
      │ vs Last Week: ↑ │         │ 7-day graph    │
      │ vs Average: ↑   │         │ Peak: 78 ppm   │
      │ Items: 47       │         │ Low: 32 ppm    │
      │ CO2: 9.8 kg     │         │ Avg: 50 ppm    │
      │ Savings: 30%    │         │ Best day: 35   │
      └────────┬────────┘         └────────┬───────┘
               |                           |
               └───────────┬───────────────┘
                           |
                  ┌────────V──────────┐
                  │  PERSONALIZED     │
                  │  RECOMMENDATIONS  │
                  ├───────────────────┤
                  │ Based on trends:  │
                  │ • Recycle more    │
                  │ • Use public      │
                  │   transport       │
                  │ • Buy less        │
                  │   packaged food   │
                  │ • Reduce waste    │
                  │ • Improve air by: │
                  │   - Opening       │
                  │     windows       │
                  │   - Planting      │
                  │   - Recycling     │
                  └────────┬──────────┘
                           |
              ┌────────────┴─────────────┐
              |                          |
              V                          V
      ┌─────────────────┐      ┌────────────────┐
      │  ACHIEVEMENTS   │      │  COMPARISON    │
      ├─────────────────┤      ├────────────────┤
      │ Badges Earned:  │      │ Your Ranking:  │
      │ [RECYCLER]      │      │ Top 15%        │
      │ [ECO HERO]      │      │ Friends:       │
      │ [AIR GUARDIAN]  │      │ Beat 7 friends │
      │ [30 DAY STREAK] │      │ City Average:  │
      │                 │      │ You: -35% CO2  │
      │ Next Goal:      │      │ Country Avg:   │
      │ [EARTH FRIEND]  │      │ You: -22% CO2  │
      └─────────────────┘      └────────┬───────┘
                                        |
                              ┌─────────V──────────┐
                              │  MONTHLY/YEARLY    │
                              │  CARBON REPORT     │
                              ├────────────────────┤
                              │ Total Score:       │
                              │ 1,250 points       │
                              │                    │
                              │ Carbon Saved:      │
                              │ 125 kg CO2         │
                              │                    │
                              │ Air Quality:       │
                              │ Improved 40%       │
                              │                    │
                              │ Tree Equivalent:   │
                              │ = 18 trees         │
                              │                    │
                              │ Impact Shared:     │
                              │ 156 items logged   │
                              │ 8 friends joined   │
                              └────────────────────┘

```

---

## Key Metrics Summary

### Vision Model
- Trained On: 2,021 real trash images
- Tested On: 506 validation images
- Accuracy: 96.1% mAP
- Classes: 6 waste types
- Speed: 6.6ms per image

### Weight Model
- Method: Deterministic formula
- Accuracy: Calibrated on real samples
- Speed: <1ms per object
- Range: 2g to 500g
- GPU: Not required

### Carbon Model
- Data: Global LCA databases
- Coverage: 6 material types
- Accuracy: High (verified factors)
- Update: Real-time calculations

### Lifestyle Model
- Training Data: 8,000 profiles
- Test Data: 2,000 profiles
- Features: 20 factors
- Accuracy: Varies with data quality

### MQ7 Sensor
- Range: 0-1000 ppm CO
- Accuracy: ±5%
- Update Rate: 1 second
- Battery: 48+ hours
- History: 24-hour tracking

---

## Data Flow Summary

```
IMAGE INPUT ──> VISION ──> WEIGHT ──> CARBON ──┐
                                                 |
REAL-TIME SENSOR ──> MONITOR ──> ALERTS ────────┤
                                                 |
LIFESTYLE DATA ──> ML MODEL ──> PREDICTIONS ────┤
                                                 |
                    ┌─────────────────────────────┘
                    |
                    V
         COMBINED USER FEEDBACK
         
         [WHAT IT IS] [HOW HEAVY] [CO2 COST]
         [AIR QUALITY] [SAFETY] [RECOMMENDATIONS]
```

---

## Integration Points

```
EcoGuard System connects to:

Frontend Layer:
├─ Mobile App (iOS/Android)
├─ Web App (React/Vue)
└─ Desktop App

Backend Layer:
├─ Python REST API
├─ Database (tracking)
└─ Cloud Sync (optional)

Hardware Layer:
├─ Camera (image capture)
├─ MQ7 Sensor (WiFi/Bluetooth)
└─ Device Storage (local)

External Systems:
├─ LCA Databases
├─ Weather APIs
└─ Social Sharing
```

---

**Document Version:** 1.0  
**Last Updated:** March 2026  
**Purpose:** Quick Reference - Architecture & System Flow

