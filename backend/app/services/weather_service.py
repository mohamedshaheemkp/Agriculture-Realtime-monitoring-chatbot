import requests
import logging
from app.core.config import Config

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self):
        self.api_key = Config.WEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    def get_current_weather(self, lat=None, lon=None):
        """
        Fetches real-time weather data for the specified location.
        Falls back to simulation if API key is missing or request fails.
        """
        lat = lat or Config.LOCATION_LAT
        lon = lon or Config.LOCATION_LON
        
        # Fallback to simulation if no API key
        if not self.api_key or self.api_key == "your_api_key_here":
            logger.warning("No Weather API Key provided. Returning simulated data.")
            return self._get_simulated_weather()

        try:
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric"
            }
            response = requests.get(self.base_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            return self._parse_api_response(data)
            
        except requests.RequestException as e:
            logger.error(f"Weather API request failed: {e}")
            return self._get_simulated_weather()

    def _parse_api_response(self, data):
        """Parses OpenWeatherMap response into our standardized format."""
        main = data.get("main", {})
        weather = data.get("weather", [{}])[0]
        wind = data.get("wind", {})
        
        # Simple agricultural relevant alert logic
        condition = weather.get("main", "Clear")
        forecast_alert = None
        
        if "Rain" in condition or "Drizzle" in condition:
            forecast_alert = "Rain expected. Delay fertilizer application."
        elif main.get("temp", 25) > 35:
            forecast_alert = "High heat stress potential for crops."

        return {
            "location": data.get("name", "Unknown Location"),
            "condition": weather.get("description", "Clear"),
            "temp_c": main.get("temp", 0),
            "humidity_pct": main.get("humidity", 0),
            "wind_kph": round(wind.get("speed", 0) * 3.6, 1), # m/s to kph
            "forecast_alert": forecast_alert
        }

    def _get_simulated_weather(self):
        """Returns plausible dummy data for demos."""
        return {
            "location": "Simulated Farm",
            "condition": "Partly Cloudy",
            "temp_c": 28.5,
            "humidity_pct": 65,
            "wind_kph": 12.0,
            "forecast_alert": None
        }

weather_service = WeatherService()
