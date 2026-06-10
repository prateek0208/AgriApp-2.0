import streamlit as st
from datetime import datetime

def show_weather_section(state_name, water_availability, top_crop):
    st.subheader("🌦️ Weather & Planting Ease Analysis")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Logic for Color/Label and SCORE (Added Score calculation)
    if water_availability > 80:
        suit_label, suit_color, suit_score = "EXCELLENT", "#00e676", 95
    elif water_availability > 50:
        suit_label, suit_color, suit_score = "STABLE", "#ffeb3b", 70
    else:
        suit_label, suit_color, suit_score = "RISKY", "#ff5252", 35

    st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.03); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <span style="color: #888; font-size: 0.8rem;">🕒 Analysis Timestamp</span><br>
                    <b style="color: white;">{current_time}</b>
                </div>
                <div style="background: {suit_color}; color: black; padding: 5px 15px; border-radius: 20px; font-weight: bold;">
                    🌱 {suit_label}: {suit_score}%
                </div>
            </div>
            <hr style="border-color: rgba(255,255,255,0.05); margin: 15px 0;">
            <div style="display: flex; flex-wrap: wrap; gap: 10px; justify-content: space-between;">
                <div style="flex: 1; min-width: 90px; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; text-align: center;">
                    <p style="margin:0; color: #a5d6a7; font-size: 0.75rem;">💧 Moisture</p>
                    <h4 style="margin:0;">{water_availability}%</h4>
                </div>
                <div style="flex: 1; min-width: 90px; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; text-align: center;">
                    <p style="margin:0; color: #a5d6a7; font-size: 0.75rem;">🌡️ Soil</p>
                    <h4 style="margin:0;">26°C</h4>
                </div>
                <div style="flex: 1; min-width: 90px; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; text-align: center;">
                    <p style="margin:0; color: #a5d6a7; font-size: 0.75rem;">☁️ Humid</p>
                    <h4 style="margin:0;">62%</h4>
                </div>
                <div style="flex: 1; min-width: 90px; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; text-align: center;">
                    <p style="margin:0; color: #a5d6a7; font-size: 0.75rem;">🌬️ Wind</p>
                    <h4 style="margin:0;">12 km/h</h4>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)