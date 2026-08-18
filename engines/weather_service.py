import requests
import os
import logging
from dotenv import load_dotenv

# Load API key from .env file — never hardcode secrets!
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# Fallback: read from Streamlit secrets (for cloud deployment)
if not API_KEY:
    try:
        import streamlit as st
        API_KEY = st.secrets.get("OPENWEATHER_API_KEY", "")
    except Exception:
        pass

logger = logging.getLogger(__name__)

def get_weather_data(location_name: str) -> dict | None:
    """
    Fetches current weather and 3-day forecast from OpenWeatherMap API.
    Returns a structured dict or None on failure.
    """
    if not API_KEY:
        logger.error("OPENWEATHER_API_KEY is missing from .env file.")
        return None

    url = (
        f"http://api.openweathermap.org/data/2.5/forecast"
        f"?q={location_name},IN&appid={API_KEY}&units=metric"
    )
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "list" not in data or len(data["list"]) < 25:
            logger.warning("Unexpected API response structure.")
            return None

        current = data["list"][0]

        # Get 3 days of forecast (every 8th index = ~24hr gap)
        forecast_list = []
        for i in [8, 16, 24]:
            day_data = data["list"][i]
            forecast_list.append({
                "date": day_data["dt_txt"].split(" ")[0],
                "temp": round(day_data["main"]["temp"], 1),
                "hum": day_data["main"]["humidity"],
                "desc": day_data["weather"][0]["description"].capitalize(),
                "icon": day_data["weather"][0]["icon"],
                "wind_speed": round(day_data.get("wind", {}).get("speed", 0) * 3.6, 1),  # m/s → km/h
            })

        return {
            "current_temp": round(current["main"]["temp"], 1),
            "current_hum": current["main"]["humidity"],
            "current_desc": current["weather"][0]["description"].capitalize(),
            "current_icon": current["weather"][0]["icon"],
            "current_wind": round(current.get("wind", {}).get("speed", 0) * 3.6, 1),  # m/s → km/h
            "feels_like": round(current["main"].get("feels_like", current["main"]["temp"]), 1),
            "forecast": forecast_list,
        }

    except requests.exceptions.ConnectionError:
        logger.error("No internet connection. Could not reach OpenWeatherMap.")
        return None
    except requests.exceptions.Timeout:
        logger.error("OpenWeatherMap API request timed out.")
        return None
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error from weather API: {e}")
        return None
    except (KeyError, IndexError) as e:
        logger.error(f"Unexpected response format from weather API: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in get_weather_data: {e}")
        return None