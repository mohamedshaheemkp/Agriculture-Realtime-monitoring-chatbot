import random

def get_sensor_data():
    # Simulate real-time sensor data
    # In a real app, this would read from serial/GPIO/MQTT
    temp = 25 + random.uniform(-2, 5)
    humidity = 60 + random.uniform(-10, 10)
    soil = 40 + random.uniform(-5, 15)
    
    return {
        "temperature": f"{temp:.1f}°C",
        "humidity": f"{humidity:.1f}%",
        "soil_moisture": f"{soil:.1f}%"
    }
