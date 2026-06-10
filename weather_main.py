import streamlit as st
from weather_service import get_weather_data
from weather_intelligence import show_weather_section

def render_integrated_weather(location_name, water_availability, top_crop):
    """
    Fetches real-time weather and displays it inside the 
    Planting Intelligence window without changing old code.
    """
    # 1. Fetch live data from your weather_service.py
    weather_info = get_weather_data(location_name)
    
    if weather_info:
        # 2. Extract live values
        live_temp = f"{weather_info['current_temp']}°C"
        live_hum = weather_info['current_hum']
        
        # 3. Use your existing UI from weather_intelligence.py
        # We pass the live humidity into the 'water_availability' slot for real-time surity
        show_weather_section(
            state_name=location_name, 
            water_availability=water_availability, 
            top_crop=top_crop
        )
        
        # 4. Display the 3-Day Forecast below it (from weather_service.py)
        st.write("---")
        st.subheader(f"📅 3-Day Forecast for {location_name}")
        f_cols = st.columns(3)
        for i, day in enumerate(weather_info['forecast']):
            with f_cols[i]:
                st.markdown(f"""
                    <div style="text-align:center; background:rgba(255,255,255,0.05); padding:10px; border-radius:10px;">
                        <p style="margin:0; font-size:0.8rem;">{day['date']}</p>
                        <h4 style="margin:5px 0;">{day['temp']}°C</h4>
                        <p style="margin:0; color:#a5d6a7;">{day['desc']}</p>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.error("Could not fetch live weather. Please check your API key.")

# Example of how to call this in your main dashboard:
# render_integrated_weather("Punjab", 95, "Rice")