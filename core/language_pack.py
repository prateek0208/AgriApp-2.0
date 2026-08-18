"""
language_pack.py — AgriTech AI Translation Engine
Supports: English (en) | Hindi (hi)

Usage:
    from language_pack import t
    st.button(t('btn_run'))        # Returns in current session language
"""

import streamlit as st

# ─────────────────────────────────────────────────────────────
# FULL TRANSLATION DICTIONARY
# ─────────────────────────────────────────────────────────────
TRANSLATIONS = {

    # ── English ──────────────────────────────────────────────
    "en": {
        # App
        "app_title":        "AgriTech AI | Smart Farm & Precision Agriculture",
        "app_tagline":      "AI-Powered Precision Agriculture for Indian Farmers",

        # Auth
        "portal_title":     "🌱 Farmer Portal",
        "tab_login":        "🔐 Secure Login",
        "tab_register":     "📝 Create Account",
        "lbl_username":     "Username",
        "lbl_password":     "Password",
        "btn_login":        "Access System",
        "btn_register":     "Register Now",
        "lbl_new_user":     "Choose Username",
        "lbl_new_pass":     "Choose Password",
        "msg_login_fail":   "❌ Invalid Username or Password",
        "msg_reg_success":  "✅ Registration successful! Please login.",
        "msg_reg_fail":     "❌ Username already exists.",

        # Sidebar
        "welcome":          "👋 Welcome",
        "btn_logout":       "🚪 Logout System",
        "lbl_location":     "Enter State/City Name",
        "sidebar_title":    "AgriTech AI",
        "sat_data":         "🛰️ Satellite Data",
        "lbl_nitrogen":     "Nitrogen (N) - ppm",
        "lbl_phosphorus":   "Phosphorus (P) - ppm",
        "lbl_potassium":    "Potassium (K) - ppm",
        "lbl_ph":           "Soil pH",
        "lbl_rainfall":     "Current Rainfall (mm)",
        "lbl_farm_size":    "Farm Size (Acres)",
        "lbl_language":     "🌐 Language / भाषा",
        "lbl_location_hdr": "🌍 Farmer Location",

        # Navigation Tabs
        "tab_ai":           "🚀 AI Command Center",
        "tab_weather":      "🌦️ Weather Details",
        "tab_regional":     "🗺️ Regional Intelligence",
        "tab_history":      "📜 Farm History",
        "tab_satellite":    "🛰️ Satellite Health (NDVI)",
        "tab_mandi":        "💰 Mandi Prices",

        # AI Command Center
        "cmd_title":        "🚜 Agri-Intelligence Command Center",
        "lbl_forecast":     "🌤️ Live Forecast",
        "lbl_current_temp": "Current Temp",
        "sec_diagnostics":  "💡 AI Diagnostics",
        "btn_run":          "RUN SYSTEM ANALYSIS",
        "recommended":      "RECOMMENDED",
        "sec_soil":         "📊 Soil Health",
        "score_breakdown":  "🔍 Score Breakdown",
        "sec_price":        "💰 AI Price Prediction",
        "lbl_invest":       "ML Predicted Investment",
        "lbl_based_on":     "Based on",
        "lbl_acres":        "Acres & Soil Data",
        "model_info":       "🤖 Model Info",

        # History
        "history_title":    "📋 Farm Activity History & Analytics",
        "trend_title":      "📈 Soil Nutrient & Rainfall Trends",
        "btn_pdf":          "PREPARE PDF",
        "btn_download_pdf": "📥 DOWNLOAD PDF",
        "no_records":       "No records found.",

        # Weather
        "weather_title":    "🌦️ Detailed Weather Intelligence",
        "weather_offline":  "⚠️ Weather data unavailable — check your API key.",

        # Status labels
        "status_excellent": "EXCELLENT",
        "status_stable":    "STABLE",
        "status_risky":     "RISKY",

        # Soil score labels
        "ph_score":         "pH Score",
        "n_score":          "Nitrogen Score",
        "p_score":          "Phosphorus Score",
        "k_score":          "Potassium Score",
        "rain_score":       "Rainfall Score",

        # Crop names
        "rice":         "Rice",
        "wheat":        "Wheat",
        "maize":        "Maize",
        "cotton":       "Cotton",
        "sugarcane":    "Sugarcane",
        "soybean":      "Soybean",
        "groundnut":    "Groundnut",
        "mango":        "Mango",
        "banana":       "Banana",
        "grapes":       "Grapes",
        "tomato":       "Tomato",
        "onion":        "Onion",
        "potato":       "Potato",
        "chillies":     "Chillies",
        "turmeric":     "Turmeric",
        "ginger":       "Ginger",
        "mustard":      "Mustard",
        "jute":         "Jute",
        "coffee":       "Coffee",
        "coconut":      "Coconut",
        "papaya":       "Papaya",
        "orange":       "Orange",

        # Plant Doctor
        "pd_title":             "🩺 Plant Doctor: Crop Disease AI",
        "pd_upload_lbl":        "📸 Upload a photo of the sick leaf",
        "pd_analyzing":         "🔬 Analyzing leaf structure & pathogens...",
        "pd_detected":          "⚠️ Disease Detected:",
        "pd_confidence":        "🧠 AI Confidence:",
        "pd_organic":           "🌱 Organic Treatment",
        "pd_chemical":          "🧪 Chemical Treatment",
        "pd_no_image":          "Upload an image to get AI diagnosis.",

        # Voice advice
        "voice_recommended":    "The recommended crop is",
        "voice_soil_good":      "Your soil health is excellent. Keep it up.",
        "voice_soil_moderate":  "Your soil health is moderate. Consider adding fertilizers.",
        "voice_soil_poor":      "Your soil health needs improvement. Please consult an expert.",
    },

    # ── Hindi ─────────────────────────────────────────────────
    "hi": {
        # App
        "app_title":        "AgriTech AI | स्मार्ट खेती और सटीक कृषि",
        "app_tagline":      "भारतीय किसानों के लिए AI-संचालित सटीक कृषि",

        # Auth
        "portal_title":     "🌱 किसान पोर्टल",
        "tab_login":        "🔐 सुरक्षित लॉगिन",
        "tab_register":     "📝 खाता बनाएं",
        "lbl_username":     "उपयोगकर्ता नाम",
        "lbl_password":     "पासवर्ड",
        "btn_login":        "सिस्टम में प्रवेश करें",
        "btn_register":     "अभी पंजीकरण करें",
        "lbl_new_user":     "उपयोगकर्ता नाम चुनें",
        "lbl_new_pass":     "पासवर्ड चुनें",
        "msg_login_fail":   "❌ गलत उपयोगकर्ता नाम या पासवर्ड",
        "msg_reg_success":  "✅ पंजीकरण सफल! कृपया लॉगिन करें।",
        "msg_reg_fail":     "❌ उपयोगकर्ता नाम पहले से मौजूद है।",

        # Sidebar
        "welcome":          "👋 स्वागत है",
        "btn_logout":       "🚪 लॉगआउट करें",
        "lbl_location":     "राज्य / शहर का नाम दर्ज करें",
        "sidebar_title":    "AgriTech AI",
        "sat_data":         "🛰️ उपग्रह डेटा",
        "lbl_nitrogen":     "नाइट्रोजन (N) - ppm",
        "lbl_phosphorus":   "फास्फोरस (P) - ppm",
        "lbl_potassium":    "पोटेशियम (K) - ppm",
        "lbl_ph":           "मिट्टी का pH",
        "lbl_rainfall":     "वर्तमान वर्षा (mm)",
        "lbl_farm_size":    "खेत का आकार (एकड़)",
        "lbl_language":     "🌐 Language / भाषा",
        "lbl_location_hdr": "🌍 किसान का स्थान",

        # Navigation Tabs
        "tab_ai":           "🚀 AI कमांड सेंटर",
        "tab_weather":      "🌦️ मौसम विवरण",
        "tab_regional":     "🗺️ क्षेत्रीय जानकारी",
        "tab_history":      "📜 खेत का इतिहास",
        "tab_satellite":    "🛰️ उपग्रह स्वास्थ्य (NDVI)",
        "tab_mandi":        "💰 मंडी भाव",

        # AI Command Center
        "cmd_title":        "🚜 कृषि-बुद्धिमत्ता कमांड सेंटर",
        "lbl_forecast":     "🌤️ लाइव मौसम पूर्वानुमान",
        "lbl_current_temp": "वर्तमान तापमान",
        "sec_diagnostics":  "💡 AI विश्लेषण",
        "btn_run":          "सिस्टम विश्लेषण चलाएं",
        "recommended":      "अनुशंसित फसल",
        "sec_soil":         "📊 मिट्टी का स्वास्थ्य",
        "score_breakdown":  "🔍 स्कोर विवरण",
        "sec_price":        "💰 AI मूल्य भविष्यवाणी",
        "lbl_invest":       "ML अनुमानित निवेश",
        "lbl_based_on":     "आधार पर",
        "lbl_acres":        "एकड़ और मिट्टी डेटा",
        "model_info":       "🤖 मॉडल जानकारी",

        # History
        "history_title":    "📋 खेत गतिविधि इतिहास और विश्लेषण",
        "trend_title":      "📈 मिट्टी पोषक तत्व और वर्षा रुझान",
        "btn_pdf":          "PDF तैयार करें",
        "btn_download_pdf": "📥 PDF डाउनलोड करें",
        "no_records":       "कोई रिकॉर्ड नहीं मिला।",

        # Weather
        "weather_title":    "🌦️ विस्तृत मौसम जानकारी",
        "weather_offline":  "⚠️ मौसम डेटा उपलब्ध नहीं — API key जांचें।",

        # Status labels
        "status_excellent": "उत्तम",
        "status_stable":    "स्थिर",
        "status_risky":     "जोखिमपूर्ण",

        # Soil score labels
        "ph_score":         "pH स्कोर",
        "n_score":          "नाइट्रोजन स्कोर",
        "p_score":          "फास्फोरस स्कोर",
        "k_score":          "पोटेशियम स्कोर",
        "rain_score":       "वर्षा स्कोर",

        # Crop names in Hindi
        "rice":         "चावल",
        "wheat":        "गेहूं",
        "maize":        "मक्का",
        "cotton":       "कपास",
        "sugarcane":    "गन्ना",
        "soybean":      "सोयाबीन",
        "groundnut":    "मूंगफली",
        "mango":        "आम",
        "banana":       "केला",
        "grapes":       "अंगूर",
        "tomato":       "टमाटर",
        "onion":        "प्याज",
        "potato":       "आलू",
        "chillies":     "मिर्च",
        "turmeric":     "हल्दी",
        "ginger":       "अदरक",
        "mustard":      "सरसों",
        "jute":         "जूट",
        "coffee":       "कॉफी",
        "coconut":      "नारियल",
        "papaya":       "पपीता",
        "orange":       "संतरा",

        # Plant Doctor (Hindi)
        "pd_title":             "🩺 प्लांट डॉक्टर: फसल रोग AI",
        "pd_upload_lbl":        "📸 बीमार पत्ती की फोटो अपलोड करें",
        "pd_analyzing":         "🔬 पत्ती की संरचना और रोगजनकों का विश्लेषण कर रहा है...",
        "pd_detected":          "⚠️ रोग पाया गया:",
        "pd_confidence":        "🧠 AI विश्वास स्तर:",
        "pd_organic":           "🌱 जैविक उपचार",
        "pd_chemical":          "🧪 रासायनिक उपचार",
        "pd_no_image":          "AI निदान प्राप्त करने के लिए एक छवि अपलोड करें।",

        # Voice advice
        "voice_recommended":    "अनुशंसित फसल है",
        "voice_soil_good":      "आपकी मिट्टी का स्वास्थ्य उत्कृष्ट है। इसे बनाए रखें।",
        "voice_soil_moderate":  "आपकी मिट्टी का स्वास्थ्य मध्यम है। उर्वरक डालने पर विचार करें।",
        "voice_soil_poor":      "आपकी मिट्टी के स्वास्थ्य में सुधार की आवश्यकता है। किसी विशेषज्ञ से परामर्श लें।",
    },
}


def t(key: str) -> str:
    """
    Translate a key to the current session language.
    Falls back to English if key not found in selected language.

    Usage:
        st.subheader(t('sec_diagnostics'))
    """
    lang = st.session_state.get("lang", "en")
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    return lang_dict.get(key, TRANSLATIONS["en"].get(key, key))


def translate_crop(crop_name: str) -> str:
    """Translate a crop name to current language."""
    return t(crop_name.lower().strip())


def get_tts_lang() -> str:
    """Returns gTTS language code for current session language."""
    lang = st.session_state.get("lang", "en")
    return "hi" if lang == "hi" else "en"


def render_language_selector():
    """
    Renders the language toggle in the sidebar.
    Call this inside `with st.sidebar:` block.
    """
    lang_options = {"English 🇬🇧": "en", "हिंदी 🇮🇳": "hi"}
    current_lang = st.session_state.get("lang", "en")
    current_label = next(k for k, v in lang_options.items() if v == current_lang)

    selected_label = st.selectbox(
        t("lbl_language"),
        options=list(lang_options.keys()),
        index=list(lang_options.keys()).index(current_label),
        key="lang_selector"
    )
    selected_lang = lang_options[selected_label]

    if selected_lang != current_lang:
        st.session_state.lang = selected_lang
        st.rerun()
