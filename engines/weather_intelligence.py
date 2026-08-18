import streamlit as st
from datetime import datetime

def show_weather_section(state_name: str, water_availability: float, top_crop: str, weather: dict = None):
    """
    Displays detailed weather intelligence section.
    Now uses REAL weather data passed from the API instead of hardcoded values.

    Args:
        state_name: Name of the state/city
        water_availability: Rainfall mm (from sidebar slider)
        top_crop: Last predicted crop name
        weather: Full weather dict from get_weather_data() — used for real values
    """
    st.subheader("🌦️ Weather & Planting Ease Analysis")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --- Suitability logic based on rainfall input ---
    if water_availability > 80:
        suit_label, suit_color, suit_score = "EXCELLENT", "#00e676", 95
    elif water_availability > 50:
        suit_label, suit_color, suit_score = "STABLE", "#ffeb3b", 70
    else:
        suit_label, suit_color, suit_score = "RISKY", "#ff5252", 35

    # --- Pull REAL values from weather API if available ---
    if weather:
        display_temp   = f"{weather['current_temp']}°C"
        display_hum    = f"{weather['current_hum']}%"
        display_wind   = f"{weather['current_wind']} km/h"
        display_feels  = f"{weather['feels_like']}°C"
        display_desc   = weather['current_desc']
        data_source    = "🟢 Live API Data"
    else:
        # Graceful fallback — clearly shows it's not live
        display_temp   = "N/A"
        display_hum    = "N/A"
        display_wind   = "N/A"
        display_feels  = "N/A"
        display_desc   = "Unavailable"
        data_source    = "🔴 Offline (API unavailable)"

    st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.03); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <span style="color: #888; font-size: 0.8rem;">🕒 Analysis Timestamp</span><br>
                    <b style="color: white;">{current_time}</b><br>
                    <span style="color: #555; font-size: 0.75rem;">{data_source}</span>
                </div>
                <div style="background: {suit_color}; color: black; padding: 5px 15px; border-radius: 20px; font-weight: bold;">
                    🌱 {suit_label}: {suit_score}%
                </div>
            </div>
            <hr style="border-color: rgba(255,255,255,0.05); margin: 15px 0;">
            <p style="color: #888; margin: 0 0 10px 0; font-size: 0.8rem;">Current Conditions: <b style="color:white;">{display_desc}</b></p>
            <div style="display: flex; flex-wrap: wrap; gap: 10px; justify-content: space-between;">
                <div style="flex: 1; min-width: 90px; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; text-align: center;">
                    <p style="margin:0; color: #a5d6a7; font-size: 0.75rem;">🌡️ Temperature</p>
                    <h4 style="margin:0;">{display_temp}</h4>
                </div>
                <div style="flex: 1; min-width: 90px; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; text-align: center;">
                    <p style="margin:0; color: #a5d6a7; font-size: 0.75rem;">🌡️ Feels Like</p>
                    <h4 style="margin:0;">{display_feels}</h4>
                </div>
                <div style="flex: 1; min-width: 90px; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; text-align: center;">
                    <p style="margin:0; color: #a5d6a7; font-size: 0.75rem;">☁️ Humidity</p>
                    <h4 style="margin:0;">{display_hum}</h4>
                </div>
                <div style="flex: 1; min-width: 90px; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; text-align: center;">
                    <p style="margin:0; color: #a5d6a7; font-size: 0.75rem;">💧 Moisture Input</p>
                    <h4 style="margin:0;">{water_availability} mm</h4>
                </div>
                <div style="flex: 1; min-width: 90px; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; text-align: center;">
                    <p style="margin:0; color: #a5d6a7; font-size: 0.75rem;">🌬️ Wind Speed</p>
                    <h4 style="margin:0;">{display_wind}</h4>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- 3-Day Forecast Cards ---
    if weather and weather.get("forecast"):
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📅 3-Day Forecast")
        f_cols = st.columns(3)
        for i, day in enumerate(weather["forecast"]):
            rain_flag = "🌧️" if "rain" in day["desc"].lower() else "☀️"
            with f_cols[i]:
                st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 12px;
                                border: 1px solid rgba(255,255,255,0.08); text-align: center;">
                        <p style="margin:0; color:#888; font-size:0.8rem;">{day['date']}</p>
                        <h2 style="margin:5px 0;">{rain_flag}</h2>
                        <h3 style="margin:0; color:#00e676;">{day['temp']}°C</h3>
                        <p style="margin:5px 0 0; color:#aaa; font-size:0.8rem;">{day['desc']}</p>
                        <p style="margin:2px 0 0; color:#64b5f6; font-size:0.75rem;">💧 {day['hum']}% | 💨 {day['wind_speed']} km/h</p>
                    </div>
                """, unsafe_allow_html=True)

        # --- Actionable Farming Advice block ---
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 💡 Actionable Farming Advice")
        
        # Analyze current/forecast conditions to give custom tips
        is_rainy = False
        is_windy = False
        is_hot = False
        
        if weather:
            # Check current conditions
            is_rainy = "rain" in display_desc.lower() or "drizzle" in display_desc.lower()
            try:
                wind_val = float(weather.get('current_wind', 0))
                is_windy = wind_val > 15
            except ValueError:
                pass
            try:
                temp_val = float(weather.get('current_temp', 0))
                is_hot = temp_val > 30
            except ValueError:
                pass
            
            # Check forecast conditions
            for day in weather.get("forecast", []):
                if "rain" in day["desc"].lower():
                    is_rainy = True
                    
        # Construct the advice HTML card
        if is_rainy:
            card_title = "🌧️ Rainfall Advisory — Caution on Spraying"
            card_color = "#ff5252"
            card_body = f"Rain is expected or active. <b>Avoid applying liquid nitrogen (urea) or spraying liquid pesticides today</b>—the rain will wash it away, wasting effort and money. Ensure crop fields have proper drainage."
        elif is_windy:
            card_title = "🌬️ High Wind Speed Advisory — Spray Danger"
            card_color = "#ffeb3b"
            card_body = f"Wind speed is above 15 km/h. <b>Do not spray powder or mist pesticides today</b>. The high wind drift will blow the chemicals off-target and could harm neighboring crops."
        elif is_hot:
            card_title = "☀️ High Temperature Advisory — Evaporation Risk"
            card_color = "#ff9800"
            card_body = f"Temperatures are expected to exceed 30°C. <b>Water your fields only in the early morning (before 9 AM) or late evening (after 5 PM)</b>. Watering in mid-day causes water to evaporate before reaching crop roots."
        else:
            card_title = "🟢 Optimal Farming Conditions — Perfect Day"
            card_color = "#00e676"
            card_body = f"Weather is stable and moisture is balanced. This is a <b>perfect day for weeding, crop sowing, transplanting, and fertilizer application</b>. Ideal window for manual field labor."

        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.03); padding: 20px; border-radius: 15px; border-left: 5px solid {card_color}; box-shadow: 0 4px 15px rgba(0,0,0,0.15);">
                <h4 style="margin: 0 0 8px 0; color: {card_color}; font-family: 'Outfit', sans-serif; font-weight: 700;">{card_title}</h4>
                <p style="margin: 0; color: #e0e0e0; font-size: 0.95rem; line-height: 1.5;">{card_body}</p>
            </div>
        """, unsafe_allow_html=True)