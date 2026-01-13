import random
from services.memory import log_sensor_data

def get_sensor_data():
    # Simulate real-time sensor data with slight variations
    # In a real deployment, replace this with GPIO/MQTT reading logic
    
    # Generate realistic values
    temp = round(25 + random.uniform(-2, 5), 1)
    humidity = round(60 + random.uniform(-10, 10), 1)
    soil = round(40 + random.uniform(-10, 15), 1)
    
    data = {
        "temperature": f"{temp}",
        "humidity": f"{humidity}",
        "soil_moisture": f"{soil}"
    }
    
    # Store in DB for history/chatbot context
    log_sensor_data(data)
    
    # Add units for display
    display_data = {
        "temperature": f"{temp}°C",
        "humidity": f"{humidity}%",
        "soil_moisture": f"{soil}%"
    }
    
    return display_data
