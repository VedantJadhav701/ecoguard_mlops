"""
EcoGuard - API Testing Dashboard
Tests the deployed Render API endpoints
"""

import streamlit as st
import requests
import json
from pathlib import Path
import numpy as np
from datetime import datetime

# Configuration
API_BASE_URL = "https://ecoguard-mlops.onrender.com"
# For local testing, use: API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="EcoGuard - API Testing",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== SIDEBAR - API STATUS ====================

st.sidebar.title("🔌 API Status & Info")

# Health check
try:
    response = requests.get(f"{API_BASE_URL}/health", timeout=5)
    health_data = response.json()
    
    st.sidebar.success("✅ API is healthy!")
    st.sidebar.write(f"**Status:** {health_data.get('status', 'unknown')}")
    
    models = health_data.get('models', {})
    st.sidebar.write("**Models:**")
    st.sidebar.write(f"  - Vision: {'✅' if models.get('vision') else '❌'}")
    st.sidebar.write(f"  - Weight: {'✅' if models.get('weight') else '❌'}")
    st.sidebar.write(f"  - Lifestyle: {'✅' if models.get('lifestyle') else '❌'}")
    
    # Add diagnostics button
    if st.sidebar.button("🔧 Show Diagnostics", key="diag_btn"):
        try:
            diag_response = requests.get(f"{API_BASE_URL}/api/diagnostics", timeout=5)
            if diag_response.status_code == 200:
                diag_data = diag_response.json()
                st.sidebar.info("**📊 Diagnostics:**")
                with st.sidebar.expander("Vision Model Details", expanded=models.get('vision') is False):
                    st.json(diag_data['model_status']['vision'])
                with st.sidebar.expander("Weight Model Details", expanded=models.get('weight') is False):
                    st.json(diag_data['model_status']['weight'])
                with st.sidebar.expander("Lifestyle Model Details", expanded=models.get('lifestyle') is False):
                    st.json(diag_data['model_status']['lifestyle'])
                with st.sidebar.expander("Environment Info"):
                    st.json(diag_data['environment'])
        except Exception as e:
            st.sidebar.error(f"Diagnostics failed: {str(e)}")
    
except Exception as e:
    st.sidebar.error(f"❌ API Error: {str(e)}")
    st.sidebar.write(f"**URL:** {API_BASE_URL}")
    st.sidebar.write("**Troubleshooting:**")
    st.sidebar.write("- If using localhost, start API with: `uvicorn app:app`")
    st.sidebar.write("- If using Render, check deployment status")
    st.sidebar.write("- Click 'Show Diagnostics' to see detailed model info")

st.sidebar.markdown("---")
st.sidebar.write(f"**API Base URL:** `{API_BASE_URL}`")
st.sidebar.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ==================== MAIN TITLE ====================

st.title("♻️ EcoGuard API Testing Dashboard")
st.markdown("Test all API endpoints for the deployed EcoGuard system")

# ==================== TABS ====================

tab1, tab2, tab3, tab4 = st.tabs(["🎯 Vision Detection", "⚖️ Weight Estimation", "💨 Carbon Calculator", "🌍 Lifestyle Tracker"])

# ==================== TAB 1: VISION DETECTION ====================

with tab1:
    st.header("Vision Detection API")
    st.write("Upload an image to detect waste objects using the Vision API")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload image (JPG, PNG, BMP)",
            type=["jpg", "jpeg", "png", "bmp"],
            key="vision_upload"
        )
    
    with col2:
        st.write("")  # Spacing
        debug_vision = st.checkbox("Debug Info", value=False, key="debug_vision")
    
    if uploaded_file is not None:
        # Display uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        
        if st.button("🔍 Detect Objects", key="detect_btn"):
            try:
                st.info("📡 Sending request to API...")
                
                # Prepare file for API
                files = {'file': (uploaded_file.name, uploaded_file, 'image/jpeg')}
                
                # Call API
                with st.spinner("Detecting objects..."):
                    response = requests.post(
                        f"{API_BASE_URL}/api/vision/detect",
                        files=files,
                        timeout=30
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    st.success("✅ Detection successful!")
                    
                    # Display detections count
                    count = result.get('count', 0)
                    st.metric("Objects Detected", count)
                    
                    # Display detections
                    detections = result.get('detections', [])
                    if detections:
                        st.write("**Detected Objects:**")
                        for i, detection in enumerate(detections, 1):
                            with st.expander(f"Object {i}: {detection['class_name'].upper()} (Confidence: {detection['confidence']})"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Class:** {detection['class_name']}")
                                    st.write(f"**Class ID:** {detection['class_id']}")
                                with col2:
                                    st.write(f"**Confidence:** {detection['confidence']:.4f}")
                                    st.write(f"**Confidence %:** {detection['confidence']*100:.2f}%")
                                
                                st.write("**Bounding Box:**")
                                bbox = detection['bbox']
                                st.json(bbox)
                    
                    # API metadata
                    with st.expander("📊 API Response Details"):
                        st.write(f"**Model:** {result.get('model', 'N/A')}")
                        st.write(f"**Accuracy:** {result.get('accuracy', 'N/A')}")
                        st.write(f"**Image Shape:** {result.get('image_shape', 'N/A')}")
                        if 'timestamp' in result:
                            st.write(f"**Timestamp:** {result['timestamp']}")
                    
                    if debug_vision:
                        st.write("**Full Response:**")
                        st.json(result)
                
                else:
                    st.error(f"❌ API Error: {response.status_code}")
                    st.write(f"**Message:** {response.text}")
            
            except requests.exceptions.Timeout:
                st.error("❌ Request timeout - API took too long to respond")
            except requests.exceptions.ConnectionError:
                st.error("❌ Connection error - Cannot reach API")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# ==================== TAB 2: WEIGHT ESTIMATION ====================

with tab2:
    st.header("Weight Estimation API")
    st.write("Estimate object weight from bounding box dimensions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Image Dimensions")
        image_height = st.slider("Image Height (pixels)", 100, 2000, 640, step=10)
        image_width = st.slider("Image Width (pixels)", 100, 2000, 480, step=10)
    
    with col2:
        st.subheader("Object BBox")
        bbox_x1 = st.slider("X1 (left)", 0, image_width, 50)
        bbox_y1 = st.slider("Y1 (top)", 0, image_height, 50)
        bbox_x2 = st.slider("X2 (right)", 0, image_width, 200)
        bbox_y2 = st.slider("Y2 (bottom)", 0, image_height, 200)
    
    material = st.selectbox(
        "Material Type",
        ["plastic", "glass", "metal", "paper", "cardboard", "trash"]
    )
    
    debug_weight = st.checkbox("Debug Info", value=False, key="debug_weight")
    
    if st.button("⚖️ Estimate Weight", key="weight_btn"):
        try:
            st.info("📡 Sending request to API...")
            
            # Prepare request payload
            payload = {
                "bbox": {
                    "x1": float(bbox_x1),
                    "y1": float(bbox_y1),
                    "x2": float(bbox_x2),
                    "y2": float(bbox_y2)
                },
                "class_name": material,
                "image_shape": [image_height, image_width, 3]
            }
            
            # Call API
            with st.spinner("Estimating weight..."):
                response = requests.post(
                    f"{API_BASE_URL}/api/weight/estimate",
                    json=payload,
                    timeout=10
                )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success', False):
                    st.success("✅ Weight estimation successful!")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Weight (grams)", f"{result.get('weight_g', 0):.2f}")
                    with col2:
                        st.metric("Weight (kg)", f"{result.get('weight_kg', 0):.4f}")
                    with col3:
                        st.metric("Material", result.get('material', 'N/A'))
                    
                    st.write(f"**Size Category:** {result.get('size_category', 'N/A')}")
                    st.write(f"**Confidence:** {result.get('confidence', 'N/A')}")
                    st.info(f"**Explanation:** {result.get('explanation', 'N/A')}")
                    
                    if debug_weight:
                        st.write("**Full Response:**")
                        st.json(result)
                else:
                    st.error(f"API returned error: {result.get('error', 'Unknown error')}")
            
            else:
                st.error(f"❌ API Error: {response.status_code}")
                st.write(f"**Message:** {response.text}")
        
        except requests.exceptions.Timeout:
            st.error("❌ Request timeout - API took too long to respond")
        except requests.exceptions.ConnectionError:
            st.error("❌ Connection error - Cannot reach API")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# ==================== TAB 3: CARBON CALCULATOR ====================

with tab3:
    st.header("Carbon Calculator API")
    st.write("Calculate CO₂ emissions from material weight")
    
    col1, col2 = st.columns(2)
    
    with col1:
        material_carbon = st.selectbox(
            "Material Type",
            ["plastic", "glass", "metal", "paper", "cardboard", "trash"],
            key="carbon_material"
        )
    
    with col2:
        weight_kg = st.number_input(
            "Weight (kg)",
            min_value=0.001,
            max_value=100.0,
            value=1.0,
            step=0.1
        )
    
    debug_carbon = st.checkbox("Debug Info", value=False, key="debug_carbon")
    
    if st.button("💨 Calculate Carbon", key="carbon_btn"):
        try:
            st.info("📡 Sending request to API...")
            
            # Prepare request payload
            payload = {
                "weight_kg": float(weight_kg),
                "material": material_carbon
            }
            
            # Call API
            with st.spinner("Calculating emissions..."):
                response = requests.post(
                    f"{API_BASE_URL}/api/carbon/calculate",
                    json=payload,
                    timeout=10
                )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success', False):
                    st.success("✅ Carbon calculation successful!")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("CO₂ (kg)", f"{result.get('carbon_kg', 0):.4f}")
                    with col2:
                        st.metric("CO₂ (grams)", f"{result.get('carbon_g', 0):.2f}")
                    with col3:
                        st.metric("Emission Factor", f"{result.get('emission_factor', 0):.2f}")
                    
                    st.write(f"**Material:** {result.get('material', 'N/A')}")
                    st.write(f"**Weight:** {result.get('weight_kg', 0):.4f} kg")
                    
                    # Recycling impact
                    st.subheader("♻️ Recycling Impact")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric(
                            "Recycling Reduction",
                            f"{result.get('recycling_reduction_percent', 0)}%"
                        )
                    
                    with col2:
                        st.metric(
                            "CO₂ if Recycled",
                            f"{result.get('if_recycled_co2_kg', 0):.4f} kg"
                        )
                    
                    st.info(f"**CO₂ Saved if Recycled:** {result.get('co2_saved_kg', 0):.4f} kg")
                    
                    if debug_carbon:
                        st.write("**Full Response:**")
                        st.json(result)
                else:
                    st.error(f"API returned error: {result.get('error', 'Unknown error')}")
            
            else:
                st.error(f"❌ API Error: {response.status_code}")
                st.write(f"**Message:** {response.text}")
        
        except requests.exceptions.Timeout:
            st.error("❌ Request timeout - API took too long to respond")
        except requests.exceptions.ConnectionError:
            st.error("❌ Connection error - Cannot reach API")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# ==================== TAB 4: LIFESTYLE TRACKER ====================

with tab4:
    st.header("Lifestyle Carbon Prediction API")
    st.write("Predict user's carbon footprint from lifestyle features")
    
    st.info("Fill in the following categories to estimate your carbon footprint")
    
    features = []
    
    # Home Energy
    st.subheader("🏠 Home Energy")
    col1, col2 = st.columns(2)
    with col1:
        electricity = st.slider(
            "Daily Electricity (kWh)",
            0.0, 50.0, 10.0, step=0.5,
            help="Average household uses ~10 kWh/day"
        )
        features.append(electricity / 10)  # Normalize
    with col2:
        gas = st.slider(
            "Monthly Gas (m³)",
            0.0, 500.0, 100.0, step=10.0,
            help="Average household uses ~100 m³/month"
        )
        features.append(gas / 50)  # Normalize
    
    water = st.slider(
        "Daily Water (liters)",
        0.0, 500.0, 100.0, step=10.0,
        help="Average household uses ~100 liters/day"
    )
    features.append(water / 100)  # Normalize
    
    # Transportation
    st.subheader("🚗 Transportation")
    col1, col2 = st.columns(2)
    with col1:
        car_miles = st.slider(
            "Weekly Car Miles",
            0.0, 500.0, 100.0, step=10.0,
            help="Average commute is ~100 miles/week"
        )
        features.append(car_miles / 100)  # Normalize
    with col2:
        transit = st.slider(
            "Weekly Transit (miles)",
            0.0, 500.0, 50.0, step=10.0,
            help="Public transport usage"
        )
        features.append(transit / 100)  # Normalize
    
    flights = st.slider(
        "Annual Flights",
        0, 20, 2, step=1,
        help="Number of flights per year"
    )
    features.append(float(flights))
    
    # Food
    st.subheader("🍽️ Food & Diet")
    col1, col2, col3 = st.columns(3)
    with col1:
        meat_meals = st.slider(
            "Meat Meals/Week",
            0, 21, 7, step=1,
            help="Number of meals with meat per week"
        )
        features.append(meat_meals / 21)  # Normalize (0-1)
    with col2:
        vegetarian_meals = st.slider(
            "Vegetarian Meals/Week",
            0, 21, 5, step=1,
            help="Number of vegetarian meals per week"
        )
        features.append(vegetarian_meals / 21)  # Normalize (0-1)
    with col3:
        local_food = st.slider(
            "Local Food %",
            0.0, 100.0, 50.0, step=10.0,
            help="Percentage of locally sourced food"
        )
        features.append(local_food / 100)  # Normalize (0-1)
    
    # Waste & Recycling
    st.subheader("♻️ Waste & Recycling")
    col1, col2 = st.columns(2)
    with col1:
        recycling_rate = st.slider(
            "Recycling Rate (%)",
            0.0, 100.0, 50.0, step=5.0,
            help="Percentage of waste recycled"
        )
        features.append(recycling_rate / 100)  # Normalize (0-1)
    with col2:
        plastic_bags = st.slider(
            "Plastic Bags/Week",
            0, 20, 5, step=1,
            help="Single-use plastic bags per week"
        )
        features.append(plastic_bags / 20)  # Normalize (0-1)
    
    clothing = st.slider(
        "New Clothes/Year",
        0, 100, 20, step=5,
        help="Number of new clothing items purchased per year"
    )
    features.append(clothing / 100)  # Normalize (0-1)
    
    # Additional features (padding to 20)
    features.append(0.5)  # placeholder
    features.append(0.5)  # placeholder
    features.append(0.5)  # placeholder
    features.append(0.5)  # placeholder
    
    debug_lifestyle = st.checkbox("Debug Info", value=False, key="debug_lifestyle")
    
    if st.button("🌍 Calculate Carbon Footprint", key="lifestyle_btn"):
        try:
            st.info("📡 Sending request to API...")
            
            # Ensure we have 20 features
            while len(features) < 20:
                features.append(0.5)
            features = features[:20]
            
            # Prepare request payload
            payload = {"features": [float(f) for f in features]}
            
            # Call API
            with st.spinner("Calculating lifestyle carbon footprint..."):
                response = requests.post(
                    f"{API_BASE_URL}/api/lifestyle/predict",
                    json=payload,
                    timeout=10
                )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success', False):
                    st.success("✅ Lifestyle prediction successful!")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "Monthly Carbon",
                            f"{result.get('monthly_carbon_kg', 0):.1f} kg"
                        )
                    with col2:
                        st.metric(
                            "Yearly Carbon",
                            f"{result.get('yearly_carbon_kg', 0):.1f} kg"
                        )
                    with col3:
                        st.metric(
                            "Daily Average",
                            f"{result.get('daily_average_kg', 0):.2f} kg"
                        )
                    
                    # Comparison to average
                    compared = result.get('compared_to_average_percent', 0)
                    average = result.get('country_average_kg', 500)
                    
                    st.write(f"**Country Average:** {average} kg/month")
                    
                    if compared < 0:
                        st.success(f"✅ You are **{abs(compared):.1f}%** below average!")
                    elif compared > 0:
                        st.warning(f"⚠️ You are **{compared:.1f}%** above average")
                    else:
                        st.info("You are at the average level")
                    
                    # Recommendation
                    st.info(f"**💡 Recommendation:** {result.get('recommendation', 'N/A')}")
                    
                    if debug_lifestyle:
                        st.write("**Full Response:**")
                        st.json(result)
                else:
                    st.error(f"API returned error: {result.get('error', 'Unknown error')}")
            
            else:
                st.error(f"❌ API Error: {response.status_code}")
                st.write(f"**Message:** {response.text}")
        
        except requests.exceptions.Timeout:
            st.error("❌ Request timeout - API took too long to respond")
        except requests.exceptions.ConnectionError:
            st.error("❌ Connection error - Cannot reach API")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# ==================== FOOTER ====================

st.markdown("---")
st.markdown("""
### About This Dashboard
- **Purpose:** Test deployed EcoGuard API endpoints
- **API URL:** `{}`
- **Endpoints Tested:**
  - `POST /api/vision/detect` - Waste object detection
  - `POST /api/weight/estimate` - Object weight estimation
  - `POST /api/carbon/calculate` - CO₂ emissions calculation
  - `POST /api/lifestyle/predict` - Carbon footprint prediction
  - `GET /health` - API health check

### How to Switch API Endpoints
Edit line 14 in this file:
- **Production (Render):** `https://ecoguard-mlops.onrender.com`
- **Local (Development):** `http://localhost:8000`

### Documentation
- **API Docs:** Visit `/docs` on the API server for Swagger UI
- **GitHub:** https://github.com/VedantJadhav701/ecoguard_mlops
""".format(API_BASE_URL))
