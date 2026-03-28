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
tab1, tab2, tab3 = st.tabs(["🔍 Object Impact Analyst", "🌍 Lifestyle Carbon Tracker", "🛠️ Advanced Tools"])

# ==================== TAB 1: OBJECT IMPACT ANALYST ====================
with tab1:
    st.header("Object Impact Analyst")
    st.write("Upload an image of a waste object to automatically detect it, estimate its weight, and calculate its carbon footprint.")
    
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
                with st.spinner("Analyzing image (Vision + Weight + Carbon)..."):
                    response = requests.post(
                        f"{API_BASE_URL}/api/vision/analyze",
                        files=files,
                        timeout=30
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    st.success("✅ Analysis successful!")
                    
                    # Display detections count
                    count = result.get('count', 0)
                    st.metric("Objects Detected", count)
                    
                    # Display detections
                    detections = result.get('detections', [])
                    if detections:
                        st.write("**Detected Objects & Eco-Impact:**")
                        for i, detection in enumerate(detections, 1):
                            with st.expander(f"Object {i}: {detection['class_name'].upper()} (Confidence: {detection['confidence']:.2f})", expanded=True):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Class:** {detection['class_name']}")
                                    st.write(f"**Confidence:** {detection['confidence']*100:.1f}%")
                                    st.write("**Bounding Box:**")
                                    st.json(detection['bbox'])
                                
                                with col2:
                                    st.write("⚖️ **Weight Estimation**")
                                    if 'weight_g' in detection:
                                        st.write(f"Weight: **{detection['weight_g']:.1f}g**")
                                        st.write(f"Category: {detection.get('size_category', 'N/A')}")
                                    else:
                                        st.warning("Weight estimation N/A")
                                        
                                st.markdown("---")
                                st.write("💨 **Carbon Footprint Analysis**")
                                
                                if 'carbon_g' in detection:
                                    c_col1, c_col2, c_col3 = st.columns(3)
                                    with c_col1:
                                        st.metric("CO₂ Emitted", f"{detection['carbon_g']:.1f}g")
                                    with c_col2:
                                        st.metric("CO₂ Saved (Recycled)", f"{detection.get('co2_saved_kg', 0)*1000:.1f}g")
                                    with c_col3:
                                        st.metric("Reduction %", f"{detection.get('recycling_reduction_percent', 0)}%")
                                    
                                    st.info(f"💡 **Tip:** Proper disposal of {detection['class_name']} significantly reduces environmental impact.")
                                else:
                                    st.warning("Carbon footprint data N/A")
                    
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

# ==================== TAB 2: LIFESTYLE CARBON TRACKER ====================
with tab2:
    st.header("Lifestyle Carbon Prediction")
    st.write("Predict your personal carbon footprint based on your daily habits and lifestyle.")
    
    st.info("Fill in the following categories to estimate your monthly and yearly carbon footprint.")
    
    features = []
    
    # Home Energy
    st.subheader("🏠 Home Energy")
    col1, col2 = st.columns(2)
    with col1:
        electricity = st.slider(
            "Daily Electricity (kWh)",
            0.0, 50.0, 10.0, step=0.5,
            help="Average household uses ~10 kWh/day",
            key="lifestyle_elec"
        )
        features.append(electricity / 10)
    with col2:
        gas = st.slider(
            "Monthly Gas (m³)",
            0.0, 500.0, 100.0, step=10.0,
            help="Average household uses ~100 m³/month",
            key="lifestyle_gas"
        )
        features.append(gas / 50)
    
    water = st.slider(
        "Daily Water (liters)",
        0.0, 500.0, 100.0, step=10.0,
        help="Average household uses ~100 liters/day",
        key="lifestyle_water"
    )
    features.append(water / 100)
    
    # Transportation
    st.subheader("🚗 Transportation")
    col1, col2 = st.columns(2)
    with col1:
        car_miles = st.slider(
            "Weekly Car Miles",
            0.0, 500.0, 100.0, step=10.0,
            help="Average commute is ~100 miles/week",
            key="lifestyle_car"
        )
        features.append(car_miles / 100)
    with col2:
        transit = st.slider(
            "Weekly Transit (miles)",
            0.0, 500.0, 50.0, step=10.0,
            help="Public transport usage",
            key="lifestyle_transit"
        )
        features.append(transit / 100)
    
    flights = st.slider(
        "Annual Flights",
        0, 20, 2, step=1,
        help="Number of flights per year",
        key="lifestyle_flights"
    )
    features.append(float(flights))
    
    # Food
    st.subheader("🍽️ Food & Diet")
    col1, col2, col3 = st.columns(3)
    with col1:
        meat_meals = st.slider(
            "Meat Meals/Week",
            0, 21, 7, step=1,
            help="Number of meals with meat per week",
            key="lifestyle_meat"
        )
        features.append(meat_meals / 21)
    with col2:
        vegetarian_meals = st.slider(
            "Vegetarian Meals/Week",
            0, 21, 5, step=1,
            help="Number of vegetarian meals per week",
            key="lifestyle_veg"
        )
        features.append(vegetarian_meals / 21)
    with col3:
        local_food = st.slider(
            "Local Food %",
            0.0, 100.0, 50.0, step=10.0,
            help="Percentage of locally sourced food",
            key="lifestyle_local"
        )
        features.append(local_food / 100)
    
    # Waste & Recycling
    st.subheader("♻️ Waste & Recycling")
    col1, col2 = st.columns(2)
    with col1:
        recycling_rate = st.slider(
            "Recycling Rate (%)",
            0.0, 100.0, 50.0, step=5.0,
            help="Percentage of waste recycled",
            key="lifestyle_recycling"
        )
        features.append(recycling_rate / 100)
    with col2:
        plastic_bags = st.slider(
            "Plastic Bags/Week",
            0, 20, 5, step=1,
            help="Single-use plastic bags per week",
            key="lifestyle_plastic"
        )
        features.append(plastic_bags / 20)
    
    clothing = st.slider(
        "New Clothes/Year",
        0, 100, 20, step=5,
        help="Number of new clothing items purchased per year",
        key="lifestyle_clothing"
    )
    features.append(clothing / 100)
    
    # Padding features to 20
    while len(features) < 20:
        features.append(0.5)
    
    debug_lifestyle = st.checkbox("Debug Info", value=False, key="debug_lifestyle")
    
    if st.button("🌍 Calculate Carbon Footprint", key="lifestyle_btn"):
        try:
            st.info("📡 Sending request to API...")
            payload = {"features": [float(f) for f in features]}
            
            with st.spinner("Predicting lifestyle footprint..."):
                response = requests.post(f"{API_BASE_URL}/api/lifestyle/predict", json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    st.success("✅ Prediction successful!")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Monthly Carbon", f"{result.get('monthly_carbon_kg', 0):.1f} kg")
                    c2.metric("Yearly Carbon", f"{result.get('yearly_carbon_kg', 0):.1f} kg")
                    c3.metric("Daily Average", f"{result.get('daily_average_kg', 0):.2f} kg")
                    
                    compared = result.get('compared_to_average_percent', 0)
                    if compared < 0:
                        st.success(f"✅ You are **{abs(compared):.1f}%** below average!")
                    else:
                        st.warning(f"⚠️ You are **{compared:.1f}%** above average")
                    
                    st.info(f"💡 **Recommendation:** {result.get('recommendation', 'N/A')}")
                else:
                    st.error(f"API Error: {result.get('error')}")
            else:
                st.error(f"API Error: {response.status_code}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# ==================== TAB 3: ADVANCED TOOLS ====================
with tab3:
    st.header("Manual Estimation Tools")
    st.write("Use these tools for deep-dive testing of individual model components.")
    
    with st.expander("⚖️ Manual Weight Estimator"):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Image Dimensions")
            h = st.slider("Image Height", 100, 2000, 640, key="manual_h")
            w = st.slider("Image Width", 100, 2000, 480, key="manual_w")
        with col2:
            st.subheader("BBox")
            x1 = st.slider("X1", 0, w, 50, key="manual_x1")
            y1 = st.slider("Y1", 0, h, 50, key="manual_y1")
            x2 = st.slider("X2", 0, w, 200, key="manual_x2")
            y2 = st.slider("Y2", 0, h, 200, key="manual_y2")
        
        mat = st.selectbox("Material", ["plastic", "glass", "metal", "paper", "cardboard", "trash"], key="manual_mat")
        
        if st.button("⚖️ Estimate Weight", key="manual_w_btn"):
            payload = {"bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2}, "class_name": mat, "image_shape": [h, w, 3]}
            resp = requests.post(f"{API_BASE_URL}/api/weight/estimate", json=payload)
            if resp.status_code == 200:
                st.json(resp.json())
            else:
                st.error(f"Error: {resp.status_code}")

    with st.expander("💨 Manual Carbon Calculator"):
        c_mat = st.selectbox("Material", ["plastic", "glass", "metal", "paper", "cardboard", "trash"], key="manual_c_mat")
        c_weight = st.number_input("Weight (kg)", 0.0, 100.0, 1.0, key="manual_c_weight")
        
        if st.button("💨 Calculate Carbon", key="manual_c_btn"):
            payload = {"weight_kg": c_weight, "material": c_mat}
            resp = requests.post(f"{API_BASE_URL}/api/carbon/calculate", json=payload)
            if resp.status_code == 200:
                st.json(resp.json())
            else:
                st.error(f"Error: {resp.status_code}")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown(f"""
### About This Dashboard
- **Production API:** `{API_BASE_URL}`
- **Dual Focus Architecture:**
  1. **Object Impact Analyst**: Integrated Vision, Weight, and Carbon analysis.
  2. **Lifestyle Carbon Tracker**: Personal habit-based yearly footprint prediction.
""")
