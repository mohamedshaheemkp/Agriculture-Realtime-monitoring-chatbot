import random
from app.services.storage_service import storage_service
from app.core.config import Config

class SensorService:
    def get_data(self):
        """
        Get sensor data. In production, this would read from hardware.
        Currently returns simulated data.
        """
        # Simulation Logic
        if Config.SIMULATE_SENSORS:
             temp = round(25 + random.uniform(-2, 5), 1)
             humidity = round(60 + random.uniform(-10, 10), 1)
             soil = round(40 + random.uniform(-10, 15), 1)
        else:
            # Placeholder for real hardware reading
            temp, humidity, soil = 0, 0, 0
            
        data = {
            "temperature": f"{temp}",
            "humidity": f"{humidity}",
            "soil_moisture": f"{soil}"
        }
        
        # Log to DB
        storage_service.log_sensor_data(data)
        
        # Format for Display
        display_data = {
            "temperature": f"{temp}°C",
            "humidity": f"{humidity}%",
            "soil_moisture": f"{soil}%"
        }
        return display_data

sensor_service = SensorService()
