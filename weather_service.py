import requests

# PASTE YOUR KEY HERE (No need for config.py anymore)
API_KEY = "6e6efa7cb17f763c893cd7598131403d" 

def get_weather_data(location_name):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={location_name},IN&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url).json()
        current = response['list'][0]
        
        # Get 3 days of forecast
        forecast_list = []
        for i in [8, 16, 24]:
            day_data = response['list'][i]
            forecast_list.append({
                "date": day_data['dt_txt'].split(" ")[0],
                "temp": day_data['main']['temp'],
                "hum": day_data['main']['humidity'],
                "desc": day_data['weather'][0]['description'].capitalize(),
                "icon": day_data['weather'][0]['icon']
            })
        return {
            "current_temp": current['main']['temp'],
            "current_hum": current['main']['humidity'],
            "current_desc": current['weather'][0]['description'].capitalize(),
            "current_icon": current['weather'][0]['icon'],
            "forecast": forecast_list
        }
    except:
        return None