"""
EcoGuard Streamlit Dashboard
Interactive UI for testing all ML models via the Render API
"""

import streamlit as st
import requests
import cv2
import numpy as np
from PIL import Image
import json
from io import BytesIO

# Configure page
st.set_page_config(
    page_title="EcoGuard Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App title
st.title("🌍 EcoGuard - AI Waste Management System")
st.markdown("Interactive dashboard for waste detection, carbon tracking, and environmental impact analysis")

# API Configuration
API_BASE_URL = "https://ecoguard-mlops.onrender.com"

# Sidebar config
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Status
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            st.success("✅ API Connected")
        else:
            st.error("❌ API Error")
    except:
        st.warning("⏳ API starting up... (first request may take 30-60s)")
    
    api_url = st.text_input("API URL", value=API_BASE_URL, disabled=True)
    
    st.divider()
    
    st.markdown("""
    **Quick Links:**
    - 📖 [API Docs](https://ecoguard-mlops.onrender.com/docs)
    - 🐙 [GitHub Repo](https://github.com/VedantJadhav701/ecoguard_mlops)
    - 📚 [README](https://github.com/VedantJadhav701/ecoguard_mlops/blob/main/README.md)
    """)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Vision Detection",
    "⚖️ Weight Estimation", 
    "🌱 Carbon Calculator",
    "📊 Lifestyle Tracker"
])

# ==================== TAB 1: VISION DETECTION ====================
with tab1:
    st.header("🎯 Waste Object Detection")
    st.markdown("Upload an image to detect waste objects using YOLOv8")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png", "bmp"])
        
        if uploaded_file is not None:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            # Button to detect
            if st.button("🔍 Detect Objects", key="detect_btn"):
                with st.spinner("Detecting objects..."):
                    try:
                        # Send request to API
                        files = {"file": uploaded_file.getvalue()}
                        response = requests.post(
                            f"{API_BASE_URL}/api/vision/detect",
                            files=files,
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            with col2:
                                st.success("✅ Detection Complete!")
                                
                                # Display results
                                detections = result.get("detections", [])
                                
                                st.metric("Objects Detected", len(detections))
                                
                                if detections:
                                    st.subheader("Detected Items:")
                                    for i, item in enumerate(detections, 1):
                                        with st.container(border=True):
                                            col_a, col_b = st.columns([2, 1])
                                            with col_a:
                                                st.write(f"**#{i}: {item['class_name'].upper()}**")
                                                st.caption(f"Confidence: {item['confidence']:.1%}")
                                            with col_b:
                                                if item['confidence'] > 0.8:
                                                    st.markdown("🟢 High")
                                                elif item['confidence'] > 0.5:
                                                    st.markdown("🟡 Med")
                                                else:
                                                    st.markdown("🔴 Low")
                        else:
                            st.error(f"API Error: {response.status_code}")
                            st.write(response.text)
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.info("Tip: First request may take 30-60s as the service wakes up from free tier")

# ==================== TAB 2: WEIGHT ESTIMATION ====================
with tab2:
    st.header("⚖️ Weight Estimation")
    st.markdown("Estimate weight of waste items based on material and size")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Material Properties")
        
        material = st.selectbox(
            "Material Type",
            ["plastic", "glass", "metal", "paper", "cardboard", "trash"]
        )
        
        size_percent = st.slider(
            "Item Size (% of image)",
            min_value=5,
            max_value=100,
            value=30,
            step=5
        )
        
        # Estimate weight
        if st.button("📏 Estimate Weight", key="weight_btn"):
            with st.spinner("Calculating weight..."):
                try:
                    payload = {
                        "material": material,
                        "size_percent": size_percent / 100.0
                    }
                    
                    response = requests.post(
                        f"{API_BASE_URL}/api/weight/estimate",
                        json=payload,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        with col2:
                            st.success("✅ Weight Estimated!")
                            
                            weight = result.get("weight_grams", 0)
                            st.metric("Estimated Weight", f"{weight:.1f}g")
                            
                            st.markdown("---")
                            
                            # Weight range info
                            col_min, col_max = st.columns(2)
                            with col_min:
                                st.caption(f"Min: {result.get('min_weight', 0):.1f}g")
                            with col_max:
                                st.caption(f"Max: {result.get('max_weight', 500):.1f}g")
                    else:
                        st.error(f"API Error: {response.status_code}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# ==================== TAB 3: CARBON CALCULATOR ====================
with tab3:
    st.header("🌱 Carbon Emission Calculator")
    st.markdown("Calculate CO₂ emissions for waste materials")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        material = st.selectbox(
            "Material",
            ["plastic", "glass", "metal", "paper", "cardboard", "trash"],
            key="carbon_material"
        )
    
    with col2:
        weight = st.number_input(
            "Weight (grams)",
            min_value=1,
            max_value=1000,
            value=100,
            step=10
        )
    
    with col3:
        recycled = st.checkbox("🔄 Recycled?", value=False)
    
    # Calculate
    if st.button("📊 Calculate Carbon", key="carbon_btn"):
        with st.spinner("Calculating emissions..."):
            try:
                payload = {
                    "material": material,
                    "weight_grams": weight,
                    "recycled": recycled
                }
                
                response = requests.post(
                    f"{API_BASE_URL}/api/carbon/calculate",
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display results in columns
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        emissions = result.get("carbon_kg", 0)
                        st.metric("CO₂ Emissions", f"{emissions:.3f} kg")
                    
                    with col_b:
                        if recycled:
                            recycled_emissions = result.get("recycled_carbon_kg", 0)
                            st.metric("If Recycled", f"{recycled_emissions:.3f} kg")
                    
                    with col_c:
                        if recycled:
                            saved = emissions - result.get("recycled_carbon_kg", 0)
                            st.metric("CO₂ Saved", f"{saved:.3f} kg", delta=f"-{saved*100/emissions:.0f}%")
                    
                    st.divider()
                    
                    # Environmental impact
                    st.subheader("🌍 Environmental Impact")
                    impact_col1, impact_col2 = st.columns(2)
                    
                    with impact_col1:
                        st.write("**Emission Factor:** " + result.get("emission_factor", "N/A"))
                    
                    with impact_col2:
                        recommendation = "♻️ Recycle this!" if not recycled else "✅ Great choice!"
                        st.write(f"**Recommendation:** {recommendation}")
                    
                else:
                    st.error(f"API Error: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# ==================== TAB 4: LIFESTYLE TRACKER ====================
with tab4:
    st.header("📊 Lifestyle Carbon Tracker")
    st.markdown("Track your carbon footprint based on lifestyle habits")
    
    # Get user inputs
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏠 Home Energy")
        daily_energy = st.slider("Daily Energy (kWh)", 0.0, 50.0, 15.0, 1.0)
        heating_type = st.selectbox("Heating", ["electric", "gas", "renewable"])
    
    with col2:
        st.subheader("🚗 Transportation")
        commute_miles = st.slider("Daily Commute (miles)", 0.0, 100.0, 20.0, 5.0)
        transport_mode = st.selectbox("Mode", ["car", "bus", "bike", "walk"])
    
    # Additional inputs
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("🍽️ Food & Shopping")
        meals_per_week = st.slider("Restaurant Meals/Week", 0, 14, 3)
        shopping_freq = st.selectbox("Shopping Frequency", ["weekly", "biweekly", "monthly"])
    
    with col4:
        st.subheader("♻️ Recycling")
        recycling_rate = st.slider("Recycling Rate (%)", 0, 100, 75, 10)
        waste_items_per_week = st.slider("Waste Items/Week", 0, 50, 10)
    
    # Calculate lifestyle carbon
    if st.button("📈 Calculate Footprint", key="lifestyle_btn"):
        with st.spinner("Analyzing your lifestyle..."):
            try:
                payload = {
                    "daily_energy_kwh": daily_energy,
                    "heating_type": heating_type,
                    "commute_miles": commute_miles,
                    "transport_mode": transport_mode,
                    "restaurant_meals_per_week": meals_per_week,
                    "shopping_frequency": shopping_freq,
                    "recycling_rate": recycling_rate / 100.0,
                    "waste_items_per_week": waste_items_per_week
                }
                
                response = requests.post(
                    f"{API_BASE_URL}/api/lifestyle/predict",
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    st.success("✅ Analysis Complete!")
                    
                    # Key metrics
                    metric_col1, metric_col2, metric_col3 = st.columns(3)
                    
                    with metric_col1:
                        yearly_carbon = result.get("yearly_carbon_kg", 0)
                        st.metric(
                            "Annual Carbon", 
                            f"{yearly_carbon:.0f} kg CO₂",
                            delta=f"{yearly_carbon/365:.1f} kg/day"
                        )
                    
                    with metric_col2:
                        avg_comparison = result.get("vs_average_percent", 0)
                        st.metric(
                            "vs. Average Person",
                            f"{abs(avg_comparison):.0f}%",
                            delta=f"{'Below' if avg_comparison < 0 else 'Above'}"
                        )
                    
                    with metric_col3:
                        ranking = result.get("percentile", 0)
                        st.metric(
                            "Environmental Score",
                            f"Top {100-ranking:.0f}%",
                            delta="Good job!" if ranking < 50 else "Room to improve"
                        )
                    
                    st.divider()
                    
                    # Recommendations
                    st.subheader("💡 Recommendations")
                    recommendations = result.get("recommendations", [])
                    if recommendations:
                        for i, rec in enumerate(recommendations, 1):
                            st.markdown(f"**{i}. {rec}**")
                    
                    # Breakdown
                    st.subheader("📊 Breakdown by Category")
                    breakdown = result.get("breakdown", {})
                    if breakdown:
                        breakdown_col1, breakdown_col2, breakdown_col3 = st.columns(3)
                        
                        with breakdown_col1:
                            st.metric("Energy", f"{breakdown.get('energy', 0):.0f} kg")
                        with breakdown_col2:
                            st.metric("Transport", f"{breakdown.get('transport', 0):.0f} kg")
                        with breakdown_col3:
                            st.metric("Food/Shopping", f"{breakdown.get('food_shopping', 0):.0f} kg")
                    
                else:
                    st.error(f"API Error: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# ==================== FOOTER ====================
st.divider()
st.markdown("""
### 🚀 About EcoGuard
EcoGuard is an AI-powered waste management system that helps track environmental impact.

**Technology Stack:**
- 🎯 YOLOv8 for object detection
- ⚖️ ML-based weight estimation
- 🌱 Carbon emission tracking
- 📊 Lifestyle analysis
- 🚀 Deployed on Render

**Live API:** https://ecoguard-mlops.onrender.com
""")
