# 🌾 AgriTech AI — Precision Agriculture Intelligence System

<p align="center">
  <img src="https://img.shields.io/badge/Built%20With-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit" />
  <img src="https://img.shields.io/badge/ML-scikit--learn-F7931E?style=for-the-badge&logo=scikitlearn" />
  <img src="https://img.shields.io/badge/Maps-Folium-77B829?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Weather-OpenWeatherMap-EB6E4B?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Security-bcrypt-003087?style=for-the-badge" />
</p>

A full-stack **AI-powered agricultural intelligence web application** that helps Indian farmers make data-driven decisions using machine learning, real-time weather data, satellite field analysis, and regional crop intelligence.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **AI Crop Recommendation** | ML model predicts the optimal crop based on soil N, P, K, pH, rainfall, temperature & humidity |
| 💰 **Price Prediction** | Regression model estimates expected investment cost per crop per farm size |
| 🌦️ **Live Weather Intelligence** | Real-time 3-day forecast via OpenWeatherMap API with planting suitability scoring |
| 🛰️ **Satellite Field Scout (NDVI)** | Interactive Folium map with heatmap overlay showing vegetation health by GPS coordinates |
| 🗺️ **Regional Intelligence** | National crop distribution map across all 36 Indian states/UTs with water availability data |
| 📊 **Soil Health Dashboard** | Multi-parameter soil scoring (pH, N, P, K, Rainfall) with Plotly gauge visualization |
| 📋 **Farm History & Analytics** | SQLite-backed record keeping with trend charts and PDF/CSV export |
| 🔐 **Secure Authentication** | bcrypt-hashed password storage with farmer registration/login portal |
| 🔊 **Voice Advice (TTS)** | gTTS-powered audio playback of crop recommendations |

---

## 🚀 Quick Start

### 1. Clone / Download the project
```bash
git clone <your-repo-url>
cd AgriAPP
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up your API key
```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your OpenWeatherMap API key
# Get a free key at: https://openweathermap.org/api
```
Your `.env` file should look like:
```
OPENWEATHER_API_KEY=your_actual_key_here
```

### 4. Run the app
```bash
streamlit run main.py
```

---

## 📁 Project Structure

```
AgriAPP/
│
├── main.py                  # Main Streamlit application & navigation
├── auth_manager.py          # Farmer authentication (bcrypt hashing)
├── database.py              # Farm history SQLite database
├── weather_service.py       # OpenWeatherMap API integration
├── weather_intelligence.py  # Weather display component
├── regional_intelligence.py # National crop & map intelligence
├── satellite_engine.py      # NDVI field scout with Folium maps
├── satellite_database.py    # Satellite scan history database
├── price_engine.py          # ML price prediction engine
├── report_generator.py      # PDF report generator (fpdf2)
│
├── my_crop_model.pkl        # Trained crop recommendation model
├── price_model.pkl          # Trained price prediction model
│
├── .env                     # 🔐 Your API keys (DO NOT commit)
├── .env.example             # Template — safe to commit
├── .gitignore               # Excludes .env, .db, .pkl from git
├── requirements.txt         # All Python dependencies
│
└── tests/
    └── test_basic.py        # Unit tests for core modules
```

---

## 🧠 ML Models

### Crop Recommendation Model (`my_crop_model.pkl`)
- **Algorithm**: Random Forest Classifier
- **Input Features**: N, P, K, Temperature, Humidity, pH, Rainfall
- **Dataset**: Kaggle Crop Recommendation Dataset (~2,200 samples)
- **Output**: One of 22 crop classes (Rice, Wheat, Cotton, etc.)
- **Typical Accuracy**: ~98% on held-out test set

### Price Prediction Model (`price_model.pkl`)
- **Algorithm**: Regression (ML-based)
- **Input Features**: N, P, K, pH, Rainfall, Farm Size (Acres)
- **Output**: Estimated investment cost in ₹

---

## 🔐 Security

- Passwords are hashed using **bcrypt** with automatic salt generation
- API keys are stored in **`.env`** (never hardcoded in source)
- `.env` is listed in `.gitignore` to prevent accidental commits

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit + Custom CSS (Glassmorphism) |
| ML Engine | scikit-learn + joblib |
| Visualisation | Plotly, Folium (interactive maps) |
| Database | SQLite (via Python sqlite3) |
| Weather API | OpenWeatherMap (REST API) |
| Authentication | bcrypt |
| PDF Reports | fpdf2 |
| TTS | Google Text-to-Speech (gTTS) |

---

## 📸 Screenshots

> Run the app and explore the 5 tabs:
> 1. 🚀 AI Command Center
> 2. 🌦️ Weather Intelligence
> 3. 🗺️ Regional Intelligence
> 4. 📜 Farm History
> 5. 🛰️ Satellite NDVI Scout

---

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

---

## 📄 License

MIT License — free to use and modify for academic and personal projects.

---

## 👤 Author

Built as a 4th Year AI/ML Engineering capstone project.  
Focused on real-world application of machine learning in Indian precision agriculture.
