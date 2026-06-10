import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

def show_regional_page():
    # --- 1. DATASET (Original Data Preserved) ---
    data = {
        'State': [
            'Andaman & Nicobar', 'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 
            'Chandigarh', 'Chhattisgarh', 'Dadra & Nagar Haveli', 'Delhi', 'Goa', 
            'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jammu & Kashmir', 'Jharkhand', 
            'Karnataka', 'Kerala', 'Ladakh', 'Lakshadweep', 'Madhya Pradesh', 
            'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 
            'Odisha', 'Puducherry', 'Punjab', 'Rajasthan', 'Sikkim', 
            'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal'
        ],
        'lat': [11.7401, 15.9129, 28.2180, 26.2006, 25.0961, 30.7333, 21.2787, 20.1809, 28.6139, 15.2993, 22.2587, 29.0588, 31.1048, 33.7782, 23.6102, 15.3173, 10.8505, 34.1526, 10.5667, 22.9734, 19.7515, 24.6637, 25.4670, 23.1645, 26.1584, 20.9517, 11.9416, 31.1471, 27.0238, 27.3314, 11.1271, 18.1124, 23.9408, 26.8467, 30.0668, 22.9868],
        'lon': [92.6586, 79.7400, 94.7278, 92.9376, 85.3131, 76.7794, 81.8661, 73.0169, 77.2090, 74.1240, 71.1924, 76.0856, 77.1734, 76.5762, 85.2799, 75.7139, 76.2711, 77.5771, 72.6417, 78.6569, 75.7139, 93.9063, 91.3662, 92.9376, 94.5624, 85.0985, 79.8083, 75.3412, 74.2179, 88.6138, 78.6569, 79.0193, 91.9882, 80.9462, 79.0193, 87.8550],
        'Top 3 Crops': [['Coconut', 'Rice', 'Arecanut'], ['Rice', 'Cotton', 'Chillies'], ['Oranges', 'Rice', 'Maize'], ['Tea', 'Rice', 'Jute'], ['Wheat', 'Rice', 'Maize'], ['Vegetables', 'Flowers', 'Fruit'], ['Rice', 'Pulses', 'Oilseeds'], ['Pulses', 'Rice', 'Wheat'], ['Mustard', 'Wheat', 'Vegetables'], ['Cashew', 'Rice', 'Coconut'], ['Cotton', 'Groundnut', 'Cumin'], ['Wheat', 'Rice', 'Mustard'], ['Apples', 'Maize', 'Potatoes'], ['Saffron', 'Apples', 'Walnuts'], ['Rice', 'Maize', 'Pulses'], ['Coffee', 'Rice', 'Maize'], ['Rubber', 'Coconut', 'Spices'], ['Apricots', 'Apples', 'Barley'], ['Coconut', 'Tuna', 'Rice'], ['Soybean', 'Wheat', 'Gram'], ['Sugarcane', 'Cotton', 'Soybean'], ['Rice', 'Pulses', 'Maize'], ['Turmeric', 'Rice', 'Maize'], ['Bamboo', 'Rice', 'Ginger'], ['Maize', 'Rice', 'Pulses'], ['Rice', 'Pulses', 'Oilseeds'], ['Rice', 'Sugarcane', 'Coconut'], ['Rice', 'Wheat', 'Cotton'], ['Maize', 'Bajra', 'Mustard'], ['Cardamom', 'Ginger', 'Oranges'], ['Cotton', 'Rice', 'Sugarcane'], ['Turmeric', 'Cotton', 'Rice'], ['Jute', 'Rice', 'Rubber'], ['Sugarcane', 'Wheat', 'Rice'], ['Apples', 'Rice', 'Wheat'], ['Rice', 'Jute', 'Tea']],
        'Water Availability %': [98, 70, 95, 92, 65, 85, 78, 70, 45, 94, 55, 88, 82, 75, 68, 60, 98, 20, 99, 58, 52, 90, 94, 88, 85, 82, 95, 95, 30, 90, 45, 55, 85, 75, 70, 85],
        'Avg Price (₹/kg)': [40, 48, 65, 250, 32, 25, 38, 55, 62, 140, 78, 25, 115, 250, 42, 210, 180, 150, 45, 52, 35, 46, 115, 22, 28, 44, 47, 45, 22, 450, 85, 120, 60, 35, 110, 48],
        'Market Trend': ['Stable', 'Rising', 'Stable', 'Stable', 'Rising', 'Stable', 'Stable', 'Stable', 'Rising', 'Stable', 'Rising', 'Stable', 'Rising', 'Stable', 'Stable', 'Rising', 'Rising', 'Stable', 'Stable', 'Rising', 'Rising', 'Stable', 'Stable', 'Stable', 'Stable', 'Stable', 'Stable', 'Stable', 'Rising', 'Stable', 'Falling', 'Stable', 'Rising', 'Rising', 'Stable', 'Rising'],
        'Fertilizer': ['Organic', 'Urea+DAP', 'NPK', 'Ammonium Sulfate', 'Urea', 'Compost', 'DAP', 'NPK', 'Urea', 'Potash', 'Zinc', 'Urea', 'Micros', 'Organic', 'DAP', 'Potash', 'MOP', 'Manure', 'Organic', 'NPK', 'Urea', 'DAP', 'Zinc', 'Organic', 'NPK', 'Urea', 'DAP', 'Urea+DAP', 'NPK', 'Organic', 'Potash', 'Zinc', 'SSP', 'Urea', 'Micros', 'DAP']
    }
    df = pd.DataFrame(data)

    # --- PROFESSIONAL UI INJECTION ---
    st.markdown("""
        <style>
        .main-header { font-size: 2.8rem; font-weight: 800; color: #00e676; margin-bottom: 0; }
        .sub-text { color: #888; font-size: 1.1rem; margin-bottom: 2rem; }
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        }
        </style>
    """, unsafe_allow_html=True)

    # SEO Header Block
    st.markdown('<h1 class="main-header">🗺️ Regional Intelligence & Planning</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-text">AI-Powered National Crop Distribution & Market Analytics</p>', unsafe_allow_html=True)

    # --- 1. SELECTOR & MAP ---
    selected_state = st.selectbox("📍 Select Focus Region:", df['State'].unique(), index=13)
    state_data = df[df['State'] == selected_state].iloc[0]

    st.subheader("🛰️ National Agricultural Map")
    fig_map = px.scatter_mapbox(
        df, 
        lat="lat", 
        lon="lon", 
        hover_name="State", 
        color="Water Availability %", 
        size="Avg Price (₹/kg)", 
        color_continuous_scale="GnBu", 
        zoom=3.8,
        mapbox_style="carto-darkmatter"
    )
    
    fig_map.update_layout(
        mapbox=dict(
            center=dict(lat=22.5937, lon=82.9629), # Locked on India Geographical Center
        ),
        margin={"r":0,"t":0,"l":0,"b":0}, 
        height=500, 
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_map, use_container_width=True)
    
    # --- 2. TOP 3 CROPS (Professional Cards) ---
    st.markdown(f"<h3>🌾 Recommended Crops for {selected_state}</h3>", unsafe_allow_html=True)
    c_cols = st.columns(3)
    for i in range(3):
        with c_cols[i]:
            st.markdown(f"""
                <div class="glass-card" style="text-align:center; border-top: 4px solid #00e676;">
                    <p style="margin:0; color:#a5d6a7; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;">Priority {i+1}</p>
                    <h2 style="margin:10px 0; color:white;">{state_data['Top 3 Crops'][i]}</h2>
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    # --- 3. WEATHER & SOIL DETAILS (Original Logic Preserved) ---
    st.subheader("🌦️ Real-Time Planting Ease Index")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if state_data['Water Availability %'] > 80:
        status_color, status_text, soil_moisture = "#00e676", "PERFECT: Sowing Highly Recommended", "High (Optimal)"
    elif state_data['Water Availability %'] > 50:
        status_color, status_text, soil_moisture = "#ffeb3b", "STABLE: Monitor Rain Forecast", "Medium (Stable)"
    else:
        status_color, status_text, soil_moisture = "#ff5252", "RISKY: High Irrigation Required", "Low (Dry)"

    st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #aaa;">🕒 Analysis: <b>{current_time}</b></span>
                <span style="background: {status_color}; color: black; padding: 6px 18px; border-radius: 20px; font-weight: bold;">{status_text}</span>
            </div>
            <hr style="border-color: rgba(255,255,255,0.1); margin: 15px 0;">
            <div style="display: flex; flex-wrap: wrap; gap: 40px;">
                <div><p style="margin:0; color: #a5d6a7;">💧 Soil Moisture</p><h3 style="margin:0;">{soil_moisture}</h3></div>
                <div><p style="margin:0; color: #a5d6a7;">🌡️ Avg Temp</p><h3 style="margin:0;">28°C</h3></div>
                <div><p style="margin:0; color: #a5d6a7;">🌬️ Wind Speed</p><h3 style="margin:0;">12 km/h</h3></div>
                <div><p style="margin:0; color: #a5d6a7;">🌧️ Rain Chance</p><h3 style="margin:0;">{100 - state_data['Water Availability %'] // 2}%</h3></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # --- 4. GAUGE & SMART GUIDE ---
    col_a, col_b = st.columns([1, 1.2])
    with col_a:
        fig_g = go.Figure(go.Indicator(
            mode = "gauge+number", value = 85 if state_data['Market Trend'] == 'Rising' else 60,
            title = {'text': "Farmer Profitability Index", 'font': {'size': 18}},
            gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#00e676"}, 'bgcolor': "rgba(0,0,0,0)"}
        ))
        fig_g.update_layout(height=280, margin=dict(t=50, b=0), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
        st.plotly_chart(fig_g, use_container_width=True)

    with col_b:
        st.markdown(f"""
            <div class="glass-card" style="border-left: 10px solid #00e676;">
                <h3 style="margin-top:0; color:#00e676;">💎 Farmer Strategy Guide</h3>
                <p><b>🛠️ Fertilizer:</b> Use <span style="color:#00e676">{state_data['Fertilizer']}</span> for {state_data['Top 3 Crops'][0]}.</p>
                <p><b>📈 Market:</b> {state_data['Market Trend']} trend makes this a safe investment.</p>
                <hr style="border-color: rgba(255,255,255,0.1)">
                <p style="color: #a5d6a7; font-style: italic;">Pro Tip: Based on the weather window above, prioritize {state_data['Top 3 Crops'][0]} planting this week.</p>
            </div>
        """, unsafe_allow_html=True)

    st.divider()
    
    # --- 5. NATIONAL HYDRATION ---
    st.subheader("📊 National Water Resource Comparison")
    colors = ['#1565c0'] * len(df)
    colors[df[df['State'] == selected_state].index[0]] = '#00e676' 
    fig_water = go.Figure(go.Bar(x=df['Water Availability %'], y=df['State'], orientation='h', marker_color=colors))
    fig_water.update_layout(template="plotly_dark", height=750, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_water, use_container_width=True)

if __name__ == "__main__":
    show_regional_page()
