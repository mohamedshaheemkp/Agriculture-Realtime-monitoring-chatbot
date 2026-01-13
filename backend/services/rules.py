def analyze_state(sensor_data, detections):
    """
    Analyze current sensor data and recent detections to generate advice/alerts.
    """
    alerts = []
    advice = []

    # 1. Sensor Analysis
    if sensor_data:
        temp = float(sensor_data.get('temperature', 0))
        humidity = float(sensor_data.get('humidity', 0))
        soil = float(sensor_data.get('soil_moisture', 0))

        if temp > 35:
            alerts.append(f"CRITICAL: High Temperature ({temp}°C).")
            advice.append("Consider shading crops or increasing irrigation frequency.")
        elif temp < 10:
            alerts.append(f"WARNING: Low Temperature ({temp}°C).")
            advice.append("Protect sensitive crops from potential frost.")
            
        if soil < 20:
            alerts.append("CRITICAL: Low Soil Moisture.")
            advice.append("Irrigation system should be triggered immediately.")
        
        if humidity > 85:
            advice.append("High humidity detected. Watch out for fungal diseases.")

    # 2. Vision Analysis
    if detections:
        # Get most recent detection
        latest = detections[0]
        label = latest['label'].lower()
        
        if "healthy" in label:
            advice.append("Crops look healthy. Maintain current care schedule.")
        elif "disease" in label or "rot" in label or "blight" in label:
            alerts.append(f"DISEASE DETECTED: {latest['label']}")
            advice.append(f"Inspect plants immediately for {latest['label']}. Isolate affected plants.")
        elif "pest" in label:
            alerts.append(f"PEST DETECTED: {latest['label']}")
            advice.append("Check for infestation. Consider organic pesticides if threshold exceeded.")

    return {
        "alerts": alerts,
        "advice": advice,
        "summary": f"Found {len(alerts)} alerts."
    }
