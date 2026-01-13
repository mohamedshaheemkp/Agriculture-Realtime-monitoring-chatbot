def analyze_state(sensor_data, detections):
    """
    Analyze current sensor data and recent detections to generate structured advice/alerts.
    """
    alerts = []
    advice = []
    
    # Structure for return
    result = {
        "status": "Normal",
        "alerts": [],
        "recommendations": []
    }

    # 1. Sensor Analysis
    if sensor_data:
        try:
            # Handle string inputs potentially having units
            temp_str = str(sensor_data.get('temperature', 0)).replace('°C', '')
            soil_str = str(sensor_data.get('soil_moisture', 0)).replace('%', '')
            
            # Remove any trailing non-numeric chars if necessary (simplified)
            temp = float(temp_str)
            soil = float(soil_str)

            # Rule: IF soil moisture < 20% → recommend irrigation
            if soil < 20:
                result["status"] = "Critical"
                result["alerts"].append(f"CRITICAL: Low Soil Moisture ({soil}%).")
                result["recommendations"].append({
                    "type": "irrigation",
                    "priority": "high",
                    "action": "Trigger irrigation system immediately to prevent crop stress."
                })
            
            if temp > 35:
                result["alerts"].append(f"High Temperature ({temp}°C).")
                result["recommendations"].append({
                    "type": "environment",
                    "priority": "medium",
                    "action": "Consider shading or misting to lower canopy temperature."
                })

        except ValueError:
            pass # Handle parsing errors gracefully

    # 2. Vision Analysis
    if detections:
        # Get most recent detection
        latest = detections[0]
        label = latest.get('label', '').lower()
        confidence = float(latest.get('confidence', 0))
        
        # Rule: IF disease confidence > 80% → recommend treatment
        if ("disease" in label or "rot" in label or "blight" in label) and confidence > 0.80:
            result["status"] = "Action Required"
            result["alerts"].append(f"Disease Detected: {latest['label']} ({confidence*100:.1f}%)")
            result["recommendations"].append({
                "type": "treatment",
                "priority": "high",
                "action": f"Apply treatment for {latest['label']}. Isolate affected plants.",
                "details": f"Confidence is high (>80%). Immediate intervention recommended."
            })
        elif "pest" in label and confidence > 0.70:
             result["alerts"].append(f"Pest Detected: {latest['label']}")
             result["recommendations"].append({
                "type": "pest_control",
                "priority": "medium",
                "action": "Monitor for infestation spread. Apply organic neem oil if population increases."
             })
             
    # Backwards compatibility for the chatbot
    result['advice'] = [r['action'] for r in result['recommendations']]
    
    return result
