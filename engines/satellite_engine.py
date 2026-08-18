import streamlit as st
import folium
from core.paths import get_path
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import pandas as pd
import sqlite3
import logging
from fpdf import FPDF
from engines.satellite_database import init_db, save_scan

logger = logging.getLogger(__name__)

# --- 1. PDF GENERATION ENGINE ---
def generate_pdf(dataframe: pd.DataFrame) -> bytes | None:
    """Generates a formatted PDF report from historical scan data."""
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
        widths  = [40, 50, 30, 30, 30]
        for header, width in zip(headers, widths):
            pdf.cell(width, 10, header, 1, 0, 'C', True)
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

    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        return None


# --- 2. IMPROVED NDVI CALCULATION ---
def calculate_ndvi(lat: float, lon: float, n: float = 90, p: float = 42,
                   k: float = 43, rainfall: float = 20) -> float:
    """
    Simulates NDVI using location + soil nutrient data.
    More scientifically valid than pure coordinate math:
      - High N/P/K → better vegetation health → higher NDVI
      - Higher rainfall → better growth (up to a limit)
      - Coordinate-based regional variance preserved
    """
    # Normalise nutrients to [0, 1] range (max realistic values: N=250, P=250, K=250)
    nutrient_score = min((n / 250 + p / 250 + k / 250) / 3, 1.0)

    # Rainfall contribution — optimal around 100-200mm, penalty beyond 250mm
    if rainfall <= 0:
        rain_score = 0.1
    elif rainfall <= 200:
        rain_score = rainfall / 200
    else:
        rain_score = max(0.5, 1.0 - (rainfall - 200) / 500)

    # Regional coordinate variance (keeps location uniqueness)
    coord_variance = (abs(lat) + abs(lon)) % 1

    # Weighted NDVI formula: nutrients 40%, rainfall 30%, location 30%
    ndvi = 0.30 + (nutrient_score * 0.35) + (rain_score * 0.25) + (coord_variance * 0.10)
    return round(min(ndvi, 0.95), 2)


def show_satellite_tab():
    init_db()

    # --- SESSION STATE INITIALIZATION ---
    if 'analysis_done' not in st.session_state:
        st.session_state.analysis_done = False
    if 'current_data' not in st.session_state:
        st.session_state.current_data = {
            'ndvi': 0.0, 'moisture': 0, 'soil': "N/A",
            'soil_color': "#333333", 'yield': 0
        }

    st.markdown("<h1 style='text-align: center; color: #00e676;'>🛰️ Precision Field Scout</h1>",
                unsafe_allow_html=True)

    # --- SETTINGS BAR ---
    st.markdown("### 📍 Location & Soil Settings")
    col_a, col_b, col_c = st.columns(3)
    col_d, col_e, col_f = st.columns(3)

    with col_a:
        lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=20.5937, format="%.4f")
    with col_b:
        lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=78.9629, format="%.4f")
    with col_c:
        zoom = st.slider("Visual Detail", 10, 18, 15)
    with col_d:
        sat_n = st.number_input("N (ppm)", 0, 250, 90, help="Nitrogen level affects vegetation health")
    with col_e:
        sat_p = st.number_input("P (ppm)", 0, 250, 42, help="Phosphorus level")
    with col_f:
        sat_rain = st.number_input("Rainfall (mm)", 0, 300, 20, help="Current rainfall input")

    if st.button("🚀 RUN ANALYSIS", use_container_width=True):
        # Use improved NDVI formula
        ndvi_val = calculate_ndvi(lat, lon, n=sat_n, p=sat_p, rainfall=sat_rain)

        # Dynamic Moisture based on rainfall + location latitude
        moisture_val = int((sat_rain / 300 * 60) + (abs(lat) % 15) * 1.5)
        moisture_val = min(max(moisture_val, 20), 92)

        yield_val = int(ndvi_val * 85 + (moisture_val / 8))

        # Indian Regional Soil Classification
        if 8.0 <= lat <= 13.0:
            s_type, s_color = "Laterite / Alluvial", "#B22222"
        elif lat > 24.0 and (68.0 < lon < 76.0):
            s_type, s_color = "Sandy / Arid", "#C5BAAD"
            yield_val -= 10
        elif 15.0 <= lat <= 23.0 and (73.0 <= lon <= 80.0):
            s_type, s_color = "Black Soil (Regur)", "#373737"
        elif lat > 28.0:
            s_type, s_color = "Alluvial (Indo-Gangetic)", "#8B6914"
        else:
            s_type, s_color = "Red Loamy", "#8B5A2B"

        st.session_state.analysis_done = True
        st.session_state.current_data = {
            'lat': lat, 'lon': lon,
            'ndvi': ndvi_val,
            'moisture': moisture_val,
            'soil': s_type,
            'soil_color': s_color,
            'yield': min(yield_val, 98)
        }

    # --- MAP DISPLAY ---
    m = folium.Map(location=[lat, lon], zoom_start=zoom)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri'
    ).add_to(m)

    if st.session_state.analysis_done:
        v = st.session_state.current_data['ndvi']
        # Multi-zone heatmap for spatial health distribution
        heat_points = [
            [lat,          lon,          v],
            [lat + 0.0008, lon + 0.0008, v * 0.85],
            [lat - 0.0008, lon - 0.0008, v * 1.10],
            [lat + 0.0012, lon - 0.0005, v * 0.45],
            [lat - 0.0004, lon + 0.0011, v * 0.95],
        ]
        HeatMap(
            heat_points,
            radius=45,
            blur=25,
            gradient={0.2: 'red', 0.5: 'yellow', 0.8: '#00e676'}
        ).add_to(m)

    folium.Marker(
        [lat, lon],
        icon=folium.Icon(color='green', icon='leaf', prefix='fa')
    ).add_to(m)
    st_folium(m, width=1400, height=450, use_container_width=True, key="map")
    
    # --- VISUAL COLOR GUIDE LEGEND FOR FARMERS ---
    st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 12px; margin-top: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.15);">
            <h4 style="margin: 0 0 10px 0; color: #a5d6a7; font-size: 0.95rem; font-family: 'Outfit', sans-serif; font-weight:700;">🗺️ Satellite Color Guide (What do the colors mean?)</h4>
            <div style="display: flex; gap: 15px; flex-wrap: wrap;">
                <div style="flex: 1; min-width: 150px; display: flex; align-items: center; gap: 8px;">
                    <div style="width: 16px; height: 16px; background: #ff5252; border-radius: 4px; box-shadow: 0 0 8px rgba(255,82,82,0.5);"></div>
                    <span style="font-size: 0.85rem; color: #e0e0e0;"><b>🔴 Red Heatmap:</b> Bare soil / Very dry soil / Sparse crops (Needs Water)</span>
                </div>
                <div style="flex: 1; min-width: 150px; display: flex; align-items: center; gap: 8px;">
                    <div style="width: 16px; height: 16px; background: #ffeb3b; border-radius: 4px; box-shadow: 0 0 8px rgba(255,235,59,0.5);"></div>
                    <span style="font-size: 0.85rem; color: #e0e0e0;"><b>🟡 Yellow Heatmap:</b> Moderate health / Growth lag (Needs Fertilizer/Care)</span>
                </div>
                <div style="flex: 1; min-width: 150px; display: flex; align-items: center; gap: 8px;">
                    <div style="width: 16px; height: 16px; background: #00e676; border-radius: 4px; box-shadow: 0 0 8px rgba(0,230,118,0.5);"></div>
                    <span style="font-size: 0.85rem; color: #e0e0e0;"><b>🟢 Green Heatmap:</b> Excellent growth / Dense leaves (Flourishing Field! 🌿)</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- ANALYSIS RESULTS ---
    if st.session_state.analysis_done:
        data = st.session_state.current_data
        st.divider()
        st.subheader("📊 Zonal Analysis Results")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(
                f'<div style="background:rgba(255,255,255,0.05); padding:15px; border-radius:10px; '
                f'border-left:5px solid #00e676;">'
                f'<p style="margin:0; font-size:0.8rem; color:#888;">VEGETATION (NDVI)</p>'
                f'<h3 style="margin:0; color:#00e676;">{data["ndvi"]}</h3></div>',
                unsafe_allow_html=True
            )
        with c2:
            st.markdown(
                f'<div style="background:rgba(255,255,255,0.05); padding:15px; border-radius:10px; '
                f'border-left:5px solid #2196f3;">'
                f'<p style="margin:0; font-size:0.8rem; color:#888;">MOISTURE</p>'
                f'<h3 style="margin:0; color:#2196f3;">{data["moisture"]}%</h3></div>',
                unsafe_allow_html=True
            )
        with c3:
            st.markdown(
                f'<div style="background:{data["soil_color"]}; padding:15px; border-radius:10px; '
                f'border-left:5px solid #ffffff;">'
                f'<p style="margin:0; font-size:0.8rem; color:white;">SOIL TYPE</p>'
                f'<h3 style="margin:0; color:white;">{data["soil"]}</h3></div>',
                unsafe_allow_html=True
            )
        with c4:
            st.markdown(
                f'<div style="background:rgba(255,255,255,0.05); padding:15px; border-radius:10px; '
                f'border-left:5px solid #ff9800;">'
                f'<p style="margin:0; font-size:0.8rem; color:#888;">YIELD FORECAST</p>'
                f'<h3 style="margin:0; color:#ff9800;">{data["yield"]}%</h3></div>',
                unsafe_allow_html=True
            )

        # NDVI Interpretation with scientific labels
        st.write(" ")
        ndvi = data['ndvi']
        if ndvi < 0.30:
            st.error("🤖 **AI Crop Doctor:** Bare/Sparse vegetation (NDVI < 0.30). Urgent intervention — check for drought or soil degradation.")
        elif ndvi < 0.45:
            st.error("🤖 **AI Crop Doctor:** Critical Stress (NDVI 0.30–0.45). Red heatmap zones indicate urgent water/nutrient requirements.")
        elif ndvi < 0.60:
            st.warning("🤖 **AI Crop Doctor:** Moderate health (NDVI 0.45–0.60). Yellow 'caution' zones detected. Monitor soil moisture and apply fertilizer.")
        elif ndvi < 0.75:
            st.info("🤖 **AI Crop Doctor:** Good vegetation (NDVI 0.60–0.75). Field is healthy. Maintain current irrigation schedule.")
        else:
            st.success("🤖 **AI Crop Doctor:** Optimal health (NDVI > 0.75). Green heatmap confirms field-wide excellent growth! 🌿")

        if st.button("📁 SAVE FIELD SCAN", use_container_width=True):
            try:
                save_scan(data['lat'], data['lon'], data['ndvi'],
                          data['moisture'], data['soil'], data['yield'])
                st.success("✅ Record Saved to Database!")
                st.rerun()
            except Exception as e:
                logger.error(f"Failed to save field scan: {e}")
                st.error(f"Could not save record: {e}")

    # --- HISTORY ---
    st.write("---")
    st.subheader("📜 Historical Field Records")
    conn = sqlite3.connect(get_path('data', 'farm_records.db'))
    try:
        df_history = pd.read_sql_query("SELECT * FROM scans ORDER BY timestamp DESC", conn)
        if not df_history.empty:
            tab1, tab2 = st.tabs(["👁️ View History", "📥 Export Data"])
            with tab1:
                st.dataframe(df_history, use_container_width=True)
            with tab2:
                c_csv, c_pdf = st.columns(2)
                c_csv.download_button(
                    "📊 Export CSV",
                    df_history.to_csv(index=False).encode('utf-8'),
                    "history.csv",
                    use_container_width=True
                )
                pdf_b = generate_pdf(df_history)
                if pdf_b:
                    c_pdf.download_button(
                        "📄 Download PDF Report",
                        pdf_b,
                        "Field_Report.pdf",
                        use_container_width=True
                    )
        else:
            st.info("No records found yet. Run an analysis and save it.")

    except pd.errors.DatabaseError as e:
        logger.error(f"Database read error in satellite history: {e}")
        st.info("Initializing Data Engine...")
    except Exception as e:
        logger.error(f"Unexpected error reading satellite history: {e}")
        st.info("Initializing Data Engine...")
    finally:
        conn.close()