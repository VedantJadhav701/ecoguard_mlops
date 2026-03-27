"""
EcoGuard Streamlit Dashboard
Interactive UI for testing all ML models - LOCAL MODE
Loads models directly instead of calling API
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import json
import tempfile
import os
from pathlib import Path
import sys

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import local models
from predictor import get_predictor

# Configure page
st.set_page_config(
    page_title="EcoGuard Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App title
st.title("🌍 EcoGuard - AI Waste Management System")
st.markdown("**LOCAL MODE**: Testing all ML models directly (not via API)")

# Initialize predictor with caching
@st.cache_resource
def load_models():
    """Load all models once and cache them"""
    return get_predictor('.')

# Sidebar config
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Load models
    try:
        predictor = load_models()
        
        # Model Status
        st.subheader("📦 Model Status")
        
        vision_status = "✅ Loaded" if predictor.vision_model else "❌ Failed"
        st.write(f"Vision Model: {vision_status}")
        
        weight_status = "✅ Loaded" if predictor.weight_estimator else "❌ Failed"
        st.write(f"Weight Estimator: {weight_status}")
        
        lifestyle_status = "✅ Loaded" if predictor.lifestyle_model else "❌ Failed"
        st.write(f"Lifestyle Model: {lifestyle_status}")
        
        config_status = "✅ Loaded" if predictor.weight_config else "❌ Failed"
        st.write(f"Config: {config_status}")
        
        # Check if using mock mode
        if predictor.vision_model == "MOCK_MODE":
            st.warning("⚠️ Vision using MOCK_MODE (real model failed)")
        
    except Exception as e:
        st.error(f"❌ Failed to load models: {str(e)}")
        predictor = None
    
    st.divider()
    
    st.markdown("""
    **Quick Links:**
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
    
    if predictor is None:
        st.error("❌ Models not loaded. Check the sidebar for details.")
    else:
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
                            # Save temp file
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                                image.save(tmp.name)
                                temp_path = tmp.name
                            
                            # Run detection locally
                            result = predictor.detect_objects(temp_path)
                            
                            # Clean up
                            os.unlink(temp_path)
                            
                            with col2:
                                if result.get("success"):
                                    st.success("✅ Detection Complete!")
                                    
                                    # Display results
                                    detections = result.get("detections", [])
                                    
                                    st.metric("Objects Detected", len(detections))
                                    st.caption(f"Model: {result.get('model', 'Unknown')}")
                                    
                                    if 'warning' in result:
                                        st.warning(result['warning'])
                                    
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
                                    st.error(f"Detection failed: {result.get('error', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                            import traceback
                            st.code(traceback.format_exc())

# ==================== TAB 2: WEIGHT ESTIMATION ====================
with tab2:
    st.header("⚖️ Weight Estimation")
    st.markdown("Estimate weight of waste items based on material and size")
    
    if predictor is None:
        st.error("❌ Models not loaded. Check the sidebar for details.")
    else:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Material Properties")
            
            material = st.selectbox(
                "Material Type",
                ["plastic", "glass", "metal", "paper", "cardboard", "trash"]
            )
            
            # Get image shape info
            image_height = st.slider("Image Height (pixels)", 100, 2000, 480, step=100)
            image_width = st.slider("Image Width (pixels)", 100, 2000, 640, step=100)
            
            # Bounding box simulation
            bbox_width = st.slider("Object Width (pixels)", 20, image_width, image_width//4)
            bbox_height = st.slider("Object Height (pixels)", 20, image_height, image_height//4)
            
            # Estimate weight
            if st.button("📏 Estimate Weight", key="weight_btn"):
                with st.spinner("Calculating weight..."):
                    try:
                        bbox = {
                            'x1': 0,
                            'y1': 0,
                            'x2': bbox_width,
                            'y2': bbox_height
                        }
                        image_shape = [image_height, image_width, 3]
                        
                        result = predictor.estimate_weight(bbox, material, image_shape)
                        
                        with col2:
                            if result.get("success"):
                                st.success("✅ Weight Estimated!")
                                
                                st.metric("Weight (grams)", f"{result.get('weight_g', 0):.1f}")
                                st.metric("Weight (kg)", f"{result.get('weight_kg', 0):.4f}")
                                st.caption(f"Size: {result.get('size_category', 'Unknown')}")
                                
                                st.divider()
                                st.info(result.get('explanation', ''))
                            else:
                                st.error(f"Estimation failed: {result.get('error', 'Unknown error')}")
                    except Exception as e:
                        with col2:
                            st.error(f"❌ Error: {str(e)}")
                            import traceback
                            st.code(traceback.format_exc())

# ==================== TAB 3: CARBON CALCULATOR ====================
with tab3:
    st.header("🌱 Carbon Emission Calculator")
    st.markdown("Calculate CO₂ emissions for waste materials")
    
    if predictor is None:
        st.error("❌ Models not loaded. Check the sidebar for details.")
    else:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            material = st.selectbox(
                "Material",
                ["plastic", "glass", "metal", "paper", "cardboard", "trash"],
                key="carbon_material"
            )
        
        with col2:
            weight = st.number_input(
                "Weight (kg)",
                min_value=0.001,
                max_value=100.0,
                value=1.0,
                step=0.1,
                format="%.3f"
            )
        
        with col3:
            recycled = st.checkbox("🔄 Recycled?", value=False)
        
        # Calculate
        if st.button("📊 Calculate Carbon", key="carbon_btn"):
            with st.spinner("Calculating emissions..."):
                try:
                    result = predictor.calculate_carbon(weight, material)
                    
                    if result.get("success"):
                        # Display results in columns
                        col_a, col_b, col_c = st.columns(3)
                        
                        with col_a:
                            emissions = result.get("carbon_kg", 0)
                            st.metric("CO₂ Emissions", f"{emissions:.4f} kg", f"{emissions*1000:.1f}g")
                        
                        with col_b:
                            recycled_emissions = result.get("if_recycled_co2_kg", 0)
                            st.metric("If Recycled", f"{recycled_emissions:.4f} kg", f"{recycled_emissions*1000:.1f}g")
                        
                        with col_c:
                            saved = result.get("co2_saved_kg", 0)
                            pct = (saved / emissions * 100) if emissions > 0 else 0
                            st.metric("CO₂ Saved", f"{saved:.4f} kg", f"-{pct:.0f}%")
                        
                        st.divider()
                        
                        # Emission factor info
                        st.subheader("📋 Details")
                        info_col1, info_col2 = st.columns(2)
                        
                        with info_col1:
                            st.metric("Emission Factor", f"{result.get('emission_factor', 0):.1f} kg CO₂/kg")
                        with info_col2:
                            st.metric("Recycling Reduction", f"{result.get('recycling_reduction_percent', 0):.0f}%")
                    else:
                        st.error(f"Calculation failed: {result.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())

# ==================== TAB 4: LIFESTYLE TRACKER ====================
with tab4:
    st.header("📊 Lifestyle Carbon Tracker")
    st.markdown("Track your carbon footprint based on lifestyle habits")
    
    if predictor is None:
        st.error("❌ Models not loaded. Check the sidebar for details.")
    else:
        # Create a form for lifestyle inputs
        with st.form("lifestyle_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🏠 Home & Energy")
                daily_electricity = st.slider("Daily Electricity (kWh)", 0.0, 50.0, 15.0, 1.0, help="Average daily kilowatt-hours")
                natural_gas = st.slider("Monthly Gas (m³)", 0.0, 100.0, 30.0, 5.0, help="Average monthly cubic meters")
                water_usage = st.slider("Water Usage (liters/day)", 0, 500, 150, 50, help="Estimated daily water consumption")
            
            with col2:
                st.subheader("🚗 Transportation")
                car_miles = st.slider("Weekly Car Miles", 0, 500, 100, 25, help="Estimated weekly miles driven")
                public_transport = st.slider("Public Transport (miles/week)", 0, 200, 20, 10, help="Bus, train, or metro miles")
                flights_per_year = st.slider("Flights per Year", 0, 20, 2, help="Number of flight trips")
            
            col3, col4 = st.columns(2)
            
            with col3:
                st.subheader("🍽️ Food & Diet")
                meat_meals_week = st.slider("Meat Meals/Week", 0, 14, 5, help="Number of meals with meat")
                vegetarian_meals_week = st.slider("Vegetarian Meals/Week", 0, 14, 7, help="Purely vegetarian meals")
                dairy_servings_week = st.slider("Dairy Servings/Week", 0, 30, 10, help="Cheese, milk, yogurt, etc.")
            
            with col4:
                st.subheader("♻️ Waste & Recycling")
                recycling_percent = st.slider("Recycling Rate (%)", 0, 100, 70, 10, help="Percentage of waste recycled")
                plastic_bags_week = st.slider("Single-Use Plastics/Week", 0, 20, 5, help="Plastic bags, bottles, etc.")
                new_clothes_month = st.slider("New Clothing Items/Month", 0, 20, 3, help="New clothes purchased")
            
            st.divider()
            
            # Submit button
            submitted = st.form_submit_button("📈 Calculate My Footprint", use_container_width=True)
        
        if submitted:
            with st.spinner("Analyzing your lifestyle..."):
                try:
                    # Prepare 20-feature array for the lifestyle model
                    # Based on typical lifestyle carbon tracking models
                    features = [
                        daily_electricity / 10,           # 0: Daily electricity (scaled)
                        natural_gas / 50,                 # 1: Gas usage (scaled)
                        water_usage / 200,                # 2: Water (scaled)
                        car_miles / 100,                  # 3: Car miles (scaled)
                        public_transport / 100,           # 4: Public transport (scaled)
                        flights_per_year,                 # 5: Flights
                        meat_meals_week / 7,              # 6: Meat meal ratio
                        vegetarian_meals_week / 7,        # 7: Vegetarian meal ratio
                        dairy_servings_week / 20,         # 8: Dairy (scaled)
                        recycling_percent / 100,          # 9: Recycling rate
                        plastic_bags_week / 20,           # 10: Plastic usage (scaled)
                        new_clothes_month / 5,            # 11: Clothing (scaled)
                        (daily_electricity + natural_gas) / 30,  # 12: Total home energy
                        (car_miles + public_transport) / 100,    # 13: Total transport
                        meat_meals_week,                  # 14: Meat meals (count)
                        flights_per_year,                 # 15: Flights (count)
                        recycling_percent / 100,          # 16: Recycling (duplicate for padding)
                        plastic_bags_week / 20,           # 17: Plastic (duplicate)
                        daily_electricity / 20,           # 18: Electricity ratio
                        water_usage / 300                 # 19: Water ratio
                    ]
                    
                    result = predictor.predict_lifestyle_carbon(features)
                    
                    if result.get("success"):
                        st.success("✅ Analysis Complete!")
                        
                        # Key metrics
                        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                        
                        with metric_col1:
                            monthly = result.get("monthly_carbon_kg", 0)
                            st.metric("Monthly Carbon", f"{monthly:.1f} kg")
                        
                        with metric_col2:
                            yearly = result.get("yearly_carbon_kg", 0)
                            st.metric("Annual Carbon", f"{yearly:.0f} kg", f"{yearly/365:.1f} kg/day")
                        
                        with metric_col3:
                            daily = result.get("daily_average_kg", 0)
                            st.metric("Daily Average", f"{daily:.2f} kg")
                        
                        with metric_col4:
                            comparison = result.get("compared_to_average_percent", 0)
                            status = "🔴 Above" if comparison > 0 else "🟢 Below"
                            st.metric("vs. Average", f"{abs(comparison):.0f}%", status)
                        
                        st.divider()
                        
                        # Recommendation
                        st.subheader("💡 Recommendation")
                        recommendation = result.get("recommendation", "")
                        st.info(recommendation)
                        
                        # Environmental Impact Info
                        st.subheader("🌍 Context")
                        avg_carbon = result.get("country_average_kg", 500)
                        comparison_pct = result.get("compared_to_average_percent", 0)
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("Country Average", f"{avg_carbon:.0f} kg/month")
                        with col_b:
                            status_text = f"+{comparison_pct:.1f}% higher" if comparison_pct > 0 else f"{comparison_pct:.1f}% lower"
                            st.write(f"**Your footprint:** {status_text} than average")
                    
                    else:
                        st.error(f"Calculation failed: {result.get('error', 'Unknown error')}")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())

# ==================== FOOTER ====================
st.divider()
st.markdown("""
### 🚀 About EcoGuard
EcoGuard is an AI-powered waste management system that helps track environmental impact.

**🔬 Technology Stack:**
- 🎯 YOLOv8 for object detection
- ⚖️ ML-based weight estimation  
- 🌱 Carbon emission tracking
- 📊 Lifestyle analysis with scikit-learn
- 🚀 Deployed on Render

**📍 Status:** Running in LOCAL MODE (direct model testing)
""")
