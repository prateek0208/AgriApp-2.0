import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap  # Required for the health overlay
import pandas as pd
import sqlite3
from fpdf import FPDF
from satellite_database import init_db, save_scan

# --- 1. PDF GENERATION ENGINE ---
def generate_pdf(dataframe):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.set_text_color(0, 100, 0)
        pdf.cell(200, 10, txt="Precision Field Scout - Harvest Report", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("Arial", 'B', 10)
        pdf.set_fill_color(200, 220, 255)
        headers = ["Date", "Soil Type", "NDVI", "Moisture", "Yield %"]
        widths = [40, 50, 30, 30, 30]
        for i in range(len(headers)):
            pdf.cell(widths[i], 10, headers[i], 1, 0, 'C', True)
        pdf.ln()

        pdf.set_font("Arial", size=10)
        for _, row in dataframe.iterrows():
            pdf.cell(40, 10, str(row['timestamp'])[:10], 1)
            pdf.cell(50, 10, str(row['soil_type']), 1)
            pdf.cell(30, 10, str(row['ndvi']), 1)
            pdf.cell(30, 10, f"{row['moisture']}%", 1)
            pdf.cell(30, 10, f"{row['yield_forecast']}%", 1)
            pdf.ln()
            
        return pdf.output(dest='S').encode('latin-1')
    except:
        return None

def show_satellite_tab():
    init_db()

    # --- SESSION STATE INITIALIZATION ---
    if 'analysis_done' not in st.session_state:
        st.session_state.analysis_done = False
    if 'current_data' not in st.session_state:
        st.session_state.current_data = {
            'ndvi': 0.0, 'moisture': 0, 'soil': "N/A", 'soil_color': "#333333", 'yield': 0
        }

    st.markdown("<h1 style='text-align: center; color: #00e676;'>🛰️ Precision Field Scout</h1>", unsafe_allow_html=True)
    
    # --- 2. SETTINGS BAR ---
    st.markdown("### 📍 Location Settings")
    col_a, col_b, col_c, col_d = st.columns([1, 1, 1, 1])
    
    with col_a:
        lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=20.5937, format="%.4f")
    with col_b:
        lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=78.9629, format="%.4f")
    with col_c:
        zoom = st.slider("Visual Detail", 10, 18, 15)
    with col_d:
        st.write(" ")
        st.write(" ")
        if st.button("🚀 RUN ANALYSIS", use_container_width=True):
            # Dynamic NDVI: Simulates different health based on location
            base_calc = (abs(lat) + abs(lon)) % 1 
            ndvi_val = round(0.35 + (base_calc * 0.55), 2)
            
            # Dynamic Moisture: Changes based on zoom levels
            moisture_val = int((abs(lat) % 15) * 2 + (zoom * 2.5))
            moisture_val = min(max(moisture_val, 20), 92)

            yield_val = int(ndvi_val * 100 + (moisture_val / 6))
            
            # Indian Regional Soil Logic
            if 8.0 <= lat <= 13.0: s_type, s_color = "Laterite / Alluvial", "#B22222"
            elif lat > 24.0 and (68.0 < lon < 76.0): s_type, s_color = "Sandy", "#C5BAAD"; yield_val -= 10
            elif 15.0 <= lat <= 23.0 and (73.0 <= lon <= 80.0): s_type, s_color = "Black Soil (Regur)", "#373737"
            else: s_type, s_color = "Red Loamy", "#8B5A2B"

            st.session_state.analysis_done = True
            st.session_state.current_data = {
                'lat': lat, 'lon': lon, 'ndvi': ndvi_val, 
                'moisture': moisture_val, 'soil': s_type, 'soil_color': s_color, 
                'yield': min(yield_val, 98)
            }

    # --- 3. MAP DISPLAY WITH ENHANCED HEATMAP ---
    m = folium.Map(location=[lat, lon], zoom_start=zoom)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', 
        attr='Esri'
    ).add_to(m)

    if st.session_state.analysis_done:
        v = st.session_state.current_data['ndvi']
        # MULTI-ZONE HEATMAP: Analyzes spatial health distribution
        heat_points = [
            [lat, lon, v],                          # Center Reading
            [lat + 0.0008, lon + 0.0008, v * 0.85], # Edge zone (Mild stress)
            [lat - 0.0008, lon - 0.0008, v * 1.10], # High health patch
            [lat + 0.0012, lon - 0.0005, v * 0.45], # Critical Drought Spot (Red)
            [lat - 0.0004, lon + 0.0011, v * 0.95]  # Normal patch
        ]
        
        # HeatMap Layer configuration
        HeatMap(
            heat_points, 
            radius=45, 
            blur=25, 
            gradient={0.2: 'red', 0.5: 'yellow', 0.8: '#00e676'}
        ).add_to(m)

    folium.Marker([lat, lon], icon=folium.Icon(color='green', icon='leaf', prefix='fa')).add_to(m)
    st_folium(m, width=1400, height=450, use_container_width=True, key="map")

    # --- 4. DISPLAY RESULTS ---
    if st.session_state.analysis_done:
        data = st.session_state.current_data
        st.divider()
        st.subheader("📊 Zonal Analysis Results")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div style="background:rgba(255,255,255,0.05); padding:15px; border-radius:10px; border-left:5px solid #00e676;"><p style="margin:0; font-size:0.8rem; color:#888;">VEGETATION</p><h3 style="margin:0; color:#00e676;">{data["ndvi"]} NDVI</h3></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div style="background:rgba(255,255,255,0.05); padding:15px; border-radius:10px; border-left:5px solid #2196f3;"><p style="margin:0; font-size:0.8rem; color:#888;">MOISTURE</p><h3 style="margin:0; color:#2196f3;">{data["moisture"]}%</h3></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div style="background:{data["soil_color"]}; padding:15px; border-radius:10px; border-left:5px solid #ffffff;"><p style="margin:0; font-size:0.8rem; color:white;">SOIL TYPE</p><h3 style="margin:0; color:white;">{data["soil"]}</h3></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div style="background:rgba(255,255,255,0.05); padding:15px; border-radius:10px; border-left:5px solid #ff9800;"><p style="margin:0; font-size:0.8rem; color:#888;">YIELD</p><h3 style="margin:0; color:#ff9800;">{data["yield"]}%</h3></div>', unsafe_allow_html=True)
        
        st.write(" ")
        # AI Crop Doctor Feedback
        if data['ndvi'] < 0.45:
            st.error(f"🤖 **AI Crop Doctor:** Critical Stress! Red heatmap zones indicate urgent water/nutrient requirements.")
        elif data['ndvi'] < 0.70:
            st.warning(f"🤖 **AI Crop Doctor:** Moderate health. Heatmap shows yellow 'caution' zones. Monitor soil moisture.")
        else:
            st.success(f"🤖 **AI Crop Doctor:** Optimal! Green heatmap overlay confirms field-wide healthy growth.")

        if st.button("📁 SAVE FIELD SCAN", use_container_width=True):
            save_scan(data['lat'], data['lon'], data['ndvi'], data['moisture'], data['soil'], data['yield'])
            st.success("✅ Record Saved to Database!")
            st.rerun()

    # --- 5. HISTORY ---
    st.write("---")
    st.subheader("📜 Historical Field Records")
    conn = sqlite3.connect('database/farm_records.db')
    try:
        df_history = pd.read_sql_query("SELECT * FROM scans ORDER BY timestamp DESC", conn)
        if not df_history.empty:
            tab1, tab2 = st.tabs(["👁️ View History", "📥 Export Data"])
            with tab1: st.dataframe(df_history, use_container_width=True)
            with tab2:
                c_csv, c_pdf = st.columns(2)
                c_csv.download_button("📊 Export CSV", df_history.to_csv(index=False).encode('utf-8'), "history.csv", use_container_width=True)
                pdf_b = generate_pdf(df_history)
                if pdf_b: c_pdf.download_button("📄 Download PDF Report", pdf_b, "Field_Report.pdf", use_container_width=True)
        else:
            st.info("No records found yet. Run an analysis and save it.")
    except:
        st.info("Initializing Data Engine...")
    finally:
        conn.close()