import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
from datetime import datetime, timedelta
from gtts import gTTS 
import os
import random 

# Internal Module Imports
from regional_intelligence import show_regional_page
from weather_intelligence import show_weather_section
from weather_service import get_weather_data
from database import init_db, add_record, get_history 
from price_engine import get_predicted_price
from auth_manager import create_user, login_user, init_auth_db
from report_generator import generate_soil_report
from satellite_engine import show_satellite_tab

# --- SEO & PROFESSIONAL CONFIG ---
st.set_page_config(
    page_title="AgriTech AI | Smart Farm & Precision Agriculture",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize databases
init_db() 
init_auth_db()

# --- PROFESSIONAL GLASSMORPHISM CSS ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    }
    h1 { font-family: 'Inter', sans-serif; color: #00e676 !important; font-weight: 800 !important; }
    h2, h3 { font-family: 'Inter', sans-serif; color: #a5d6a7 !important; font-weight: 600 !important; }

    .metric-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(15px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 25px;
        margin-bottom: 20px;
    }

    .rain-alert {
        background: rgba(255, 75, 75, 0.15) !important;
        border: 2px solid #ff4b4b !important;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
    }

    .task-card {
        background: rgba(46, 125, 50, 0.15);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        border-left: 5px solid #00e676;
    }

    div.stButton > button:first-child {
        background: linear-gradient(45deg, #2e7d32, #43a047);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 10px;
        font-weight: bold;
        transition: 0.3s;
    }
    div.stButton > button:first-child:hover {
        box-shadow: 0 0 20px rgba(46, 125, 50, 0.8);
        transform: translateY(-2px);
    }

    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.7; } 100% { opacity: 1; } }
    .live-indicator { color: #ff4b4b; font-weight: bold; animation: pulse 1.5s infinite; }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE MANAGEMENT ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# --- 1. AUTHENTICATION UI ---
if not st.session_state.logged_in:
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.markdown("<h1 style='text-align: center;'>🌱 Farmer Portal</h1>", unsafe_allow_html=True)
        auth_tab1, auth_tab2 = st.tabs(["🔐 Secure Login", "📝 Create Account"])
        
        with auth_tab1:
            with st.form("login_form"):
                user = st.text_input("Username")
                pw = st.text_input("Password", type="password")
                if st.form_submit_button("Access System", use_container_width=True):
                    auth_data = login_user(user, pw)
                    if auth_data:
                        st.session_state.logged_in = True
                        st.session_state.username = auth_data['username']
                        st.rerun()
                    else:
                        st.error("Invalid Username or Password")
                    
        with auth_tab2:
            with st.form("register_form"):
                new_user = st.text_input("Choose Username")
                new_pw = st.text_input("Choose Password", type="password")
                if st.form_submit_button("Register Now", use_container_width=True):
                    if create_user(new_user, new_pw):
                        st.success("Registration successful! Please login.")
                    else:
                        st.error("Username already exists.")

# --- 2. MAIN APP CONTENT ---
else:
    def speak(text):
        try:
            tts = gTTS(text=text, lang='en')
            filename = "database/advice.mp3"
            tts.save(filename)
            with open(filename, 'rb') as f:
                audio_bytes = f.read()
            st.audio(audio_bytes, format='audio/mp3', autoplay=True)
        except Exception: pass

    @st.cache_resource
    def load_model():
        return joblib.load('models/my_crop_model.pkl')

    model = load_model()

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown(f"<h3>👋 Welcome, {st.session_state.username}</h3>", unsafe_allow_html=True)
        if st.button("🚪 Logout System"):
            st.session_state.logged_in = False
            st.rerun()
        st.divider()
        st.markdown("<h1>AgriTech <span style='color:white;'>AI</span></h1>", unsafe_allow_html=True)
        st.header("🌍 Farmer Location")
        state_input = st.text_input("Enter State/City Name", "Delhi")
        st.markdown("<h3>🛰️ Satellite Data <span class='live-indicator'>● LIVE</span></h3>", unsafe_allow_html=True)
        
        n = st.slider("Nitrogen (N) - ppm", 0, 250, 90)
        p = st.slider("Phosphorus (P) - ppm", 0, 250, 42)
        k = st.slider("Potassium (K) - ppm", 0, 250, 43)
        ph = st.slider("Soil pH", 4.0, 9.0, 6.5)
        rain = st.number_input("Current Rainfall (mm)", 0, 300, 20)
        farm_size = st.number_input("Farm Size (Acres)", 1, 100, 5)

    # --- NAVIGATION TABS ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🚀 AI Command Center", 
        "🌦️ Weather Details", 
        "🗺️ Regional Intelligence", 
        "📜 Farm History",
        "🛰️ Satellite Health (NDVI)"
    ])

    weather = get_weather_data(state_input)

    with tab1:
        st.markdown("<h1>🚜 Agri-Intelligence Command Center</h1>", unsafe_allow_html=True)
        upcoming_rain = False
        
        if weather:
            st.subheader(f"🌤️ Live Forecast: {state_input}")
            w_cols = st.columns(4) 
            with w_cols[0]:
                st.metric("Current Temp", f"{weather['current_temp']}°C")
                st.markdown("<h2 style='text-align:center;'>🌡️</h2>", unsafe_allow_html=True)

            for i, day in enumerate(weather['forecast']):
                with w_cols[i+1]:
                    st.metric(day['date'][5:], f"{day['temp']}°C")
                    st.caption(day['desc'])
                    if "rain" in day['desc'].lower(): 
                        upcoming_rain = True 
        
        st.divider()
        col1, col2, col3 = st.columns(3)

        if 'last_prediction' not in st.session_state:
            st.session_state.last_prediction = "rice"

        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("💡 AI Diagnostics")
            if st.button("RUN SYSTEM ANALYSIS", use_container_width=True):
                api_temp = weather['current_temp'] if weather else 25.0
                api_hum = weather['current_hum'] if weather else 80.0
                input_data = pd.DataFrame([[n, p, k, api_temp, api_hum, ph, rain]], 
                                         columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])
                st.session_state.last_prediction = model.predict(input_data)[0].lower()
                current_price = get_predicted_price(st.session_state.last_prediction, n, p, k, ph, rain, farm_size)
                add_record(state_input, n, p, k, ph, rain, st.session_state.last_prediction, current_price)
                st.success(f"### RECOMMENDED: {st.session_state.last_prediction.upper()}")
                speak(f"The recommended crop is {st.session_state.last_prediction}.") 
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("📊 Soil Health")
            health_score = max(0, min(100, 100 - (abs(6.5 - ph) * 15)))
            fig_g = go.Figure(go.Indicator(
                mode = "gauge+number", 
                value = health_score, 
                gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#00e676"}}
            ))
            fig_g.update_layout(height=300, margin=dict(t=0, b=0, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
            st.plotly_chart(fig_g, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("💰 AI Price Prediction")
            total_price = get_predicted_price(st.session_state.last_prediction, n, p, k, ph, rain, farm_size)
            st.markdown(f"""
                <div style="background: rgba(0, 230, 118, 0.1); padding: 15px; border-radius: 10px; border: 1px solid #00e676;">
                    <p style="margin:0; font-size: 0.9rem;">ML Predicted Investment</p>
                    <h2 style="margin:0; color: #00e676;">₹{total_price:,}</h2>
                    <small>Based on {farm_size} Acres & Soil Data</small>
                </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown("<h1>🌦️ Detailed Weather Intelligence</h1>", unsafe_allow_html=True)
        if weather:
            show_weather_section(state_name=state_input, water_availability=rain, top_crop=st.session_state.last_prediction.upper())
        else:
            st.error("Weather data unavailable.")

    with tab3:
        show_regional_page()

    with tab4:
        st.markdown("<h1>📋 Farm Activity History & Analytics</h1>", unsafe_allow_html=True)
        history_df = get_history()
        
        if not history_df.empty:
            history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
            history_df = history_df.sort_values(by='timestamp', ascending=True)

            # Visualization
            st.subheader("📈 Soil Nutrient & Rainfall Trends")
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=history_df['timestamp'], y=history_df['nitrogen'], mode='lines+markers', name='Nitrogen (N)', line=dict(color='#00e676', width=3)))
            fig_trend.add_trace(go.Scatter(x=history_df['timestamp'], y=history_df['rainfall'], mode='lines+markers', name='Rainfall (mm)', line=dict(color='#2196f3', width=3, dash='dot')))
            fig_trend.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # PDF Report
            st.divider()
            if st.button("PREPARE PDF", use_container_width=True):
                try:
                    latest = history_df.iloc[-1]
                    actual_crop = latest.get('crop', latest.get('label', "Unknown"))
                    report_data = {
                        "location": state_input, "n": latest.get('nitrogen', 0), "p": latest.get('phosphorus', 0),
                        "k": latest.get('potassium', 0), "ph": latest.get('ph', 7.0), "crop": str(actual_crop).upper(),
                        "weather_temp": weather['current_temp'] if weather else "N/A",
                        "weather_desc": weather['forecast'][0]['desc'] if weather else "N/A",
                        "advice": f"The soil conditions are optimal for {actual_crop}."
                    }
                    pdf_bytes = generate_soil_report(report_data)
                    st.balloons()
                    st.download_button(label="📥 DOWNLOAD PDF", data=pdf_bytes, file_name="Health_Card.pdf", mime="application/pdf")
                except Exception as e: st.error(f"Error: {e}")

            st.dataframe(history_df.sort_values(by='timestamp', ascending=False), use_container_width=True, hide_index=True)
        else:
            st.info("No records found.")

    with tab5:
        # --- CALL THE NEW SATELLITE ENGINE ---
        show_satellite_tab()