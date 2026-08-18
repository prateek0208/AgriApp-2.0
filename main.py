import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
from datetime import datetime, timedelta
from gtts import gTTS
import os
import random

# Internal Module Imports
from engines.regional_intelligence import show_regional_page
from engines.weather_intelligence import show_weather_section
from engines.weather_service import get_weather_data
from core.database import init_db, add_record, get_history
from engines.price_engine import get_predicted_price
from core.auth_manager import create_user, login_user, init_auth_db
from utils.report_generator import generate_soil_report
from engines.satellite_engine import show_satellite_tab
from engines.mandi_engine import show_mandi_tab
from core.language_pack import t, render_language_selector, get_tts_lang, translate_crop
from alerts.whatsapp_alerts import show_whatsapp_panel
from engines.disease_engine import show_plant_doctor_tab

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
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@300;400;600;700&display=swap');
    
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0b1519, #0f232a, #16323c);
        position: relative;
        overflow: hidden;
    }
    
    /* Option 1: Floating Glowing Background Orbs */
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: absolute;
        width: 450px;
        height: 450px;
        background: radial-gradient(circle, rgba(0, 230, 118, 0.1) 0%, rgba(0,0,0,0) 70%);
        top: -50px;
        left: -50px;
        filter: blur(80px);
        z-index: 0;
        pointer-events: none;
    }
    [data-testid="stAppViewContainer"]::after {
        content: "";
        position: absolute;
        width: 550px;
        height: 550px;
        background: radial-gradient(circle, rgba(46, 125, 50, 0.08) 0%, rgba(0,0,0,0) 70%);
        bottom: -100px;
        right: -100px;
        filter: blur(100px);
        z-index: 0;
        pointer-events: none;
    }

    h1 { font-family: 'Outfit', sans-serif; color: #00e676 !important; font-weight: 800 !important; }
    h2, h3 { font-family: 'Outfit', sans-serif; color: #a5d6a7 !important; font-weight: 600 !important; }

    /* Premium Custom Navigation Tabs Styling */
    div[data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 8px 12px !important;
        border-radius: 40px !important;
        gap: 8px !important;
        margin-bottom: 25px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
    }
    
    button[data-baseweb="tab"] {
        background: transparent !important;
        color: rgba(255, 255, 255, 0.6) !important;
        border: none !important;
        padding: 8px 24px !important;
        border-radius: 30px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    button[data-baseweb="tab"]:hover {
        color: #ffffff !important;
        background: rgba(255, 255, 255, 0.08) !important;
        transform: translateY(-1px) !important;
    }
    
    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(45deg, #2e7d32, #00e676) !important;
        color: white !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(0, 230, 118, 0.3) !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
    }

    /* Remove the default Streamlit bottom bar under active tab */
    div[data-baseweb="tab-highlight-spinner"] {
        display: none !important;
    }
    div[data-baseweb="tab-border-active"] {
        display: none !important;
    }
    div[data-baseweb="tab-border"] {
        display: none !important;
    }

    .metric-card {
        background: rgba(255, 255, 255, 0.04) !important;
        backdrop-filter: blur(15px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: rgba(0, 230, 118, 0.3) !important;
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(0, 230, 118, 0.1);
    }

    .rain-alert {
        background: rgba(255, 75, 75, 0.1) !important;
        border: 1px solid rgba(255, 75, 75, 0.3) !important;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.1);
    }

    .task-card {
        background: rgba(46, 125, 50, 0.1);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        border-left: 5px solid #00e676;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    div.stButton > button:first-child {
        background: linear-gradient(45deg, #2e7d32, #43a047);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 10px;
        font-family: 'Inter', sans-serif;
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
if 'lang' not in st.session_state:
    st.session_state.lang = "en"

# --- 1. AUTHENTICATION UI ---
if not st.session_state.logged_in:
    # Language selector on login screen too
    with st.sidebar:
        render_language_selector()

    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.markdown(f"<h1 style='text-align: center;'>{t('portal_title')}</h1>", unsafe_allow_html=True)
        auth_tab1, auth_tab2 = st.tabs([t('tab_login'), t('tab_register')])

        with auth_tab1:
            with st.form("login_form"):
                user = st.text_input(t('lbl_username'))
                pw   = st.text_input(t('lbl_password'), type="password")
                if st.form_submit_button(t('btn_login'), use_container_width=True):
                    auth_data = login_user(user, pw)
                    if auth_data:
                        st.session_state.logged_in = True
                        st.session_state.username  = auth_data['username']
                        st.rerun()
                    else:
                        st.error(t('msg_login_fail'))

        with auth_tab2:
            with st.form("register_form"):
                new_user = st.text_input(t('lbl_new_user'))
                new_pw   = st.text_input(t('lbl_new_pass'), type="password")
                if st.form_submit_button(t('btn_register'), use_container_width=True):
                    if create_user(new_user, new_pw):
                        st.success(t('msg_reg_success'))
                    else:
                        st.error(t('msg_reg_fail'))

# --- 2. MAIN APP CONTENT ---
else:
    def speak(text):
        """TTS in current session language (English or Hindi)."""
        try:
            tts_lang = get_tts_lang()  # 'en' or 'hi'
            tts = gTTS(text=text, lang=tts_lang)
            filename = "advice.mp3"
            tts.save(filename)
            with open(filename, 'rb') as f:
                audio_bytes = f.read()
            st.audio(audio_bytes, format='audio/mp3', autoplay=True)
        except Exception:
            pass

    @st.cache_resource
    def load_model():
        return joblib.load(os.path.join(os.path.dirname(__file__), 'models', 'my_crop_model.pkl'))

    model = load_model()

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown(f"<h3>{t('welcome')}, {st.session_state.username}</h3>", unsafe_allow_html=True)
        if st.button(t('btn_logout')):
            st.session_state.logged_in = False
            st.rerun()
        st.divider()

        # Language selector
        render_language_selector()
        st.divider()

        st.markdown("<h1>AgriTech <span style='color:white;'>AI</span></h1>", unsafe_allow_html=True)
        st.header(t('lbl_location_hdr'))
        state_input = st.text_input(t('lbl_location'), "Delhi")
        st.markdown(f"<h3>{t('sat_data')} <span class='live-indicator'>● LIVE</span></h3>", unsafe_allow_html=True)

        n         = st.slider(t('lbl_nitrogen'),   0, 250, 90)
        p         = st.slider(t('lbl_phosphorus'), 0, 250, 42)
        k         = st.slider(t('lbl_potassium'),  0, 250, 43)
        ph        = st.slider(t('lbl_ph'),         4.0, 9.0, 6.5)
        rain      = st.number_input(t('lbl_rainfall'),  0, 300, 20)
        farm_size = st.number_input(t('lbl_farm_size'), 1, 100, 5)

    # --- NAVIGATION TABS ---
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        t('tab_ai'),
        t('tab_weather'),
        t('tab_regional'),
        t('tab_history'),
        t('tab_satellite'),
        t('tab_mandi'),
        t('pd_title')
    ])

    weather = get_weather_data(state_input)

    with tab1:
        # Dynamic, Time-Based Welcome Greeting Banner (Option 3)
        current_hour = datetime.now().hour
        if current_hour < 12:
            greeting = f"☀️ Good Morning, {st.session_state.username}!"
            sub = "Ready to check soil diagnostics and optimize crop yields today?"
            banner_bg = "linear-gradient(135deg, rgba(255, 167, 38, 0.1) 0%, rgba(255, 224, 178, 0.02) 100%)"
            banner_border = "rgba(255, 167, 38, 0.15)"
        elif current_hour < 18:
            greeting = f"🌤️ Good Afternoon, {st.session_state.username}!"
            sub = "Monitor live weather metrics, prices, and satellite vegetative scans."
            banner_bg = "linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(187, 222, 251, 0.02) 100%)"
            banner_border = "rgba(33, 150, 243, 0.15)"
        else:
            greeting = f"🌙 Good Evening, {st.session_state.username}!"
            sub = "Review today's records and budget predictions for tomorrow."
            banner_bg = "linear-gradient(135deg, rgba(156, 39, 176, 0.1) 0%, rgba(225, 190, 231, 0.02) 100%)"
            banner_border = "rgba(156, 39, 176, 0.15)"
            
        st.markdown(f"""
            <div style="background: {banner_bg}; backdrop-filter: blur(15px); border-radius: 20px; border: 1px solid {banner_border}; padding: 25px; margin-bottom: 25px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.15);">
                <h1 style="margin: 0; font-size: 2.2rem; background: linear-gradient(to right, #ffffff, #a5d6a7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-family: 'Outfit', sans-serif;">{greeting}</h1>
                <p style="margin: 5px 0 0 0; color: #a5d6a7; font-size: 1.05rem; opacity: 0.9;">{sub}</p>
            </div>
        """, unsafe_allow_html=True)
        
        upcoming_rain = False
        
        if weather:
            st.subheader(f"{t('lbl_forecast')}: {state_input}")
            w_cols = st.columns(4)
            with w_cols[0]:
                st.metric(t('lbl_current_temp'), f"{weather['current_temp']}°C")
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
            st.subheader(t('sec_diagnostics'))
            if st.button(t('btn_run'), use_container_width=True):
                api_temp = weather['current_temp'] if weather else 25.0
                api_hum  = weather['current_hum']  if weather else 80.0
                input_data = pd.DataFrame(
                    [[n, p, k, api_temp, api_hum, ph, rain]],
                    columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
                )
                st.session_state.last_prediction = model.predict(input_data)[0].lower()
                current_price = get_predicted_price(
                    st.session_state.last_prediction, n, p, k, ph, rain, farm_size
                )
                add_record(state_input, n, p, k, ph, rain,
                           st.session_state.last_prediction, current_price)
                crop_translated = translate_crop(st.session_state.last_prediction)
                speak(f"{t('voice_recommended')} {crop_translated}.")
                st.rerun()

            # --- SaaS-STYLE RECOMMENDATION SHOWCASE CARD (Option 2) ---
            crop_emojis = {
                "rice": "🌾", "wheat": "🌾", "maize": "🌽", "corn": "🌽", "chickpea": "🌱", 
                "kidneybeans": "🫘", "pigeonpeas": "🌱", "mothbeans": "🌱", "mungbean": "🌱", 
                "blackgram": "🌱", "lentil": "🌱", "pomegranate": "🍎", "banana": "🍌", 
                "mango": "🥭", "grapes": "🍇", "watermelon": "🍉", "muskmelon": "🍈", 
                "apple": "🍎", "orange": "🍊", "papaya": "🥭", "coconut": "🥥", 
                "cotton": "☁️", "jute": "🌾", "coffee": "☕"
            }
            active_crop = st.session_state.last_prediction.lower()
            emoji = crop_emojis.get(active_crop, "🌱")
            crop_translated = translate_crop(active_crop)
            
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(0, 230, 118, 0.1) 0%, rgba(46, 125, 50, 0.03) 100%); border: 1px solid rgba(0, 230, 118, 0.25); border-radius: 16px; padding: 20px; text-align: center; margin-top: 15px; margin-bottom: 15px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);">
                    <span style="font-size: 2.8rem; display: block; margin-bottom: 5px;">{emoji}</span>
                    <p style="margin: 0; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 2px; color: #a5d6a7; font-weight: 700;">{t('recommended')}</p>
                    <h3 style="margin: 5px 0 0 0; color: #00e676; font-size: 1.6rem; font-family: 'Outfit', sans-serif; font-weight: 800; border: none !important;">{crop_translated.upper()}</h3>
                </div>
            """, unsafe_allow_html=True)

            # Model info expander — shows evaluation context
            with st.expander(t('model_info')):
                st.markdown("""
                    **Crop Recommendation Model**
                    - Algorithm: Random Forest / ML Classifier
                    - Input Features: N, P, K, Temperature, Humidity, pH, Rainfall (7 features)
                    - Trained on: Kaggle Crop Recommendation Dataset (~2200 samples, 22 crops)
                    - Typical Accuracy: ~98% on test split
                    - Output: 1 of 22 crop classes

                    **Price Prediction Model**
                    - Algorithm: Regression (ML-based)
                    - Input Features: N, P, K, pH, Rainfall, Farm Size (6 features)
                    - Output: Estimated investment in ₹
                """)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader(t('sec_soil'))

            # --- IMPROVED SOIL HEALTH SCORE ---
            # Uses N, P, K, pH, and Rainfall — not just pH alone
            ph_score     = max(0, 100 - (abs(6.5 - ph) * 15))          # Optimal pH = 6.5
            n_score      = min(100, (n / 250) * 100)                    # N: 0-250ppm → 0-100
            p_score      = min(100, (p / 250) * 100)                    # P: 0-250ppm → 0-100
            k_score      = min(100, (k / 250) * 100)                    # K: 0-250ppm → 0-100
            rain_score   = 100 if 50 <= rain <= 200 else max(0, 100 - abs(rain - 125) / 2)

            # Weighted average: pH 30%, N 20%, P 20%, K 20%, Rainfall 10%
            health_score = (
                ph_score   * 0.30 +
                n_score    * 0.20 +
                p_score    * 0.20 +
                k_score    * 0.20 +
                rain_score * 0.10
            )
            health_score = round(max(0, min(100, health_score)), 1)

            # Color: green > 70, yellow > 40, red otherwise
            bar_color = "#00e676" if health_score > 70 else ("#ffeb3b" if health_score > 40 else "#ff5252")

            fig_g = go.Figure(go.Indicator(
                mode  = "gauge+number",
                value = health_score,
                title = {'text': "Soil Health Score", 'font': {'color': 'white', 'size': 14}},
                gauge = {
                    'axis': {'range': [0, 100], 'tickcolor': 'white'},
                    'bar':  {'color': bar_color},
                    'steps': [
                        {'range': [0,  40], 'color': 'rgba(255,82,82,0.15)'},
                        {'range': [40, 70], 'color': 'rgba(255,235,59,0.10)'},
                        {'range': [70,100], 'color': 'rgba(0,230,118,0.10)'},
                    ]
                }
            ))
            fig_g.update_layout(
                height=300,
                margin=dict(t=40, b=0, l=10, r=10),
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': 'white'}
            )
            st.plotly_chart(fig_g, use_container_width=True)

            # Breakdown tooltip
            with st.expander(t('score_breakdown')):
                st.markdown(f"- 🧪 {t('ph_score')}: **{ph_score:.1f}** / 100")
                st.markdown(f"- 🌿 {t('n_score')}: **{n_score:.1f}** / 100")
                st.markdown(f"- 💜 {t('p_score')}: **{p_score:.1f}** / 100")
                st.markdown(f"- 🟡 {t('k_score')}: **{k_score:.1f}** / 100")
                st.markdown(f"- 🌧️ {t('rain_score')}: **{rain_score:.1f}** / 100")
            
            st.divider()

            # --- DYNAMIC NPK FERTILIZER PRESCRIPTION & VOICE ADVICE ---
            targets = {
                "rice":       {"n": 120, "p": 60, "k": 60},
                "wheat":      {"n": 100, "p": 50, "k": 50},
                "maize":      {"n": 110, "p": 55, "k": 55},
                "corn":       {"n": 110, "p": 55, "k": 55},
                "chickpea":   {"n": 30,  "p": 60, "k": 50},
                "lentil":     {"n": 30,  "p": 55, "k": 45},
                "cotton":     {"n": 90,  "p": 45, "k": 70},
                "jute":       {"n": 80,  "p": 40, "k": 60},
                "coffee":     {"n": 100, "p": 50, "k": 80},
                "default":    {"n": 90,  "p": 50, "k": 50}
            }
            target = targets.get(active_crop, targets["default"])
            
            def_n = max(0, target["n"] - n)
            def_p = max(0, target["p"] - p)
            def_k = max(0, target["k"] - k)
            
            # India agricultural standard 50kg bag calculations per acre
            urea_bags = round((def_n * 0.08) * farm_size, 1)
            ssp_bags = round((def_p * 0.25) * farm_size, 1)
            mop_bags = round((def_k * 0.06) * farm_size, 1)
            
            with st.expander("🧪 Dynamic NPK Fertilizer Prescription", expanded=False):
                st.markdown(f"**Target Requirements for {crop_translated.upper()}:**")
                st.markdown(f"`N: {target['n']} ppm` | `P: {target['p']} ppm` | `K: {target['k']} ppm` (per acre)")
                st.divider()
                
                if def_n == 0 and def_p == 0 and def_k == 0:
                    st.success("🟢 **Perfect Balance!** Your soil has optimal nutrients. No chemical fertilizers needed.")
                    advice_speech = f"Your soil has perfect nutrient balance for growing {crop_translated}. No chemical fertilizers are required."
                else:
                    speech_parts = []
                    
                    if def_n > 0:
                        st.markdown(f"🌿 **Nitrogen Deficit (-{def_n} ppm):**")
                        st.markdown(f"- Add **{urea_bags} Bags** of **Urea** (50kg each) for {farm_size} acres.")
                        st.caption("🍀 *Organic alternative:* Apply 1.8 tons of compost manure per acre.")
                        speech_parts.append(f"Add {urea_bags} bags of Urea for Nitrogen.")
                        
                    if def_p > 0:
                        st.markdown(f"💜 **Phosphorus Deficit (-{def_p} ppm):**")
                        st.markdown(f"- Add **{ssp_bags} Bags** of **Single Super Phosphate (SSP)** for {farm_size} acres.")
                        st.caption("🍀 *Organic alternative:* Mix rock phosphate or bone meal into the soil.")
                        speech_parts.append(f"Add {ssp_bags} bags of Single Super Phosphate for Phosphorus.")
                        
                    if def_k > 0:
                        st.markdown(f"🟡 **Potassium Deficit (-{def_k} ppm):**")
                        st.markdown(f"- Add **{mop_bags} Bags** of **Muriate of Potash (MOP)** for {farm_size} acres.")
                        st.caption("🍀 *Organic alternative:* Apply wood ash or compost rich in banana peels.")
                        speech_parts.append(f"Add {mop_bags} bags of Muriate of Potash for Potassium.")
                        
                    advice_speech = f"For growing {crop_translated} on your {farm_size} acre farm, we recommend: " + " ".join(speech_parts)
                    
                st.divider()
                if st.button("🔊 Listen to Fertilizer Advice", key="btn_speak_fertilizer", use_container_width=True):
                    speak(advice_speech)
            
            st.markdown('</div>', unsafe_allow_html=True)

        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader(t('sec_price'))
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
        st.markdown(f"<h1>{t('weather_title')}</h1>", unsafe_allow_html=True)
        if weather:
            # Pass the full weather object so real API values are displayed
            show_weather_section(
                state_name=state_input,
                water_availability=rain,
                top_crop=st.session_state.last_prediction.upper(),
                weather=weather
            )
        else:
            st.warning(t('weather_offline'))
            show_weather_section(
                state_name=state_input,
                water_availability=rain,
                top_crop=st.session_state.last_prediction.upper(),
                weather=None
            )

    with tab3:
        show_regional_page()

    with tab4:
        st.markdown(f"<h1>{t('history_title')}</h1>", unsafe_allow_html=True)
        history_df = get_history()
        
        if not history_df.empty:
            history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
            history_df = history_df.sort_values(by='timestamp', ascending=True)

            # Visualization
            st.subheader(t('trend_title'))
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=history_df['timestamp'], y=history_df['nitrogen'], mode='lines+markers', name='Nitrogen (N)', line=dict(color='#00e676', width=3)))
            fig_trend.add_trace(go.Scatter(x=history_df['timestamp'], y=history_df['rainfall'], mode='lines+markers', name='Rainfall (mm)', line=dict(color='#2196f3', width=3, dash='dot')))
            fig_trend.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # PDF Report
            st.divider()
            if st.button(t('btn_pdf'), use_container_width=True):
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
                    st.download_button(label=t('btn_download_pdf'), data=pdf_bytes, file_name="Health_Card.pdf", mime="application/pdf")
                except Exception as e: st.error(f"Error: {e}")

            # --- FRIENDLY FARM TIMELINE DIARY ---
            st.subheader("📜 Recent Diagnostic Diary")
            
            recent_logs = history_df.sort_values(by='timestamp', ascending=False)
            
            crop_emojis = {
                "rice": "🌾", "wheat": "🌾", "maize": "🌽", "corn": "🌽", "chickpea": "🌱", 
                "kidneybeans": "🫘", "pigeonpeas": "🌱", "mothbeans": "🌱", "mungbean": "🌱", 
                "blackgram": "🌱", "lentil": "🌱", "pomegranate": "🍎", "banana": "🍌", 
                "mango": "🥭", "grapes": "🍇", "watermelon": "🍉", "muskmelon": "🍈", 
                "apple": "🍎", "orange": "🍊", "papaya": "🥭", "coconut": "🥥", 
                "cotton": "☁️", "jute": "🌾", "coffee": "☕"
            }
            
            for index, row in recent_logs.head(5).iterrows():
                row_crop = str(row.get('crop', row.get('label', 'rice'))).lower()
                emoji = crop_emojis.get(row_crop, "🌱")
                time_str = row['timestamp'].strftime("%b %d, %Y — %I:%M %p")
                
                st.markdown(f"""
                    <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255,255,255,0.05); border-left: 5px solid #00e676; border-radius: 12px; padding: 15px; margin-bottom: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
                        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:5px;">
                            <span style="color:#888; font-size:0.8rem;">📅 {time_str}</span>
                            <span style="background:rgba(0, 230, 118, 0.1); color:#00e676; padding: 2px 10px; border-radius: 20px; font-size: 0.8rem; font-weight:bold;">
                                {emoji} {row_crop.upper()}
                            </span>
                        </div>
                        <p style="margin: 8px 0 0 0; color:#e0e0e0; font-size:0.95rem;">
                            Soil nutrients checked in <b>{row.get('location', state_input)}</b>: 
                            Nitrogen at {row.get('nitrogen', 0)}ppm, Phosphorus at {row.get('phosphorus', 0)}ppm, Potassium at {row.get('potassium', 0)}ppm, and pH is {row.get('ph', 7.0)}.
                        </p>
                        <p style="margin: 5px 0 0 0; color:#a5d6a7; font-size:0.85rem;">
                            💰 Estimated Investment: <b>₹{int(row.get('predicted_price', 0)):,}</b>
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
            with st.expander("📊 View Raw Database Table"):
                st.dataframe(recent_logs, use_container_width=True, hide_index=True)
        else:
            st.info(t('no_records'))

    with tab5:
        # --- CALL THE NEW SATELLITE ENGINE ---
        show_satellite_tab()

    with tab6:
        # --- MANDI PRICE INTELLIGENCE ---
        show_mandi_tab(
            predicted_crop=st.session_state.last_prediction,
            state_input=state_input
        )

        # --- WHATSAPP ALERT PANEL ---
        st.divider()
        show_whatsapp_panel(
            crop          = st.session_state.last_prediction,
            modal_price   = 2183,   # Replace with real mandi price when available
            weather       = weather,
            soil_score    = round(
                max(0, 100 - (abs(6.5 - ph) * 15)) * 0.30 +
                min(100, (n / 250) * 100) * 0.20 +
                min(100, (p / 250) * 100) * 0.20 +
                min(100, (k / 250) * 100) * 0.20 +
                (100 if 50 <= rain <= 200 else max(0, 100 - abs(rain - 125) / 2)) * 0.10,
                1
            ),
            location      = state_input,
            lang          = st.session_state.get('lang', 'en')
        )

    with tab7:
        # --- PLANT DOCTOR (AI CROP DISEASE VISION) ---
        show_plant_doctor_tab()