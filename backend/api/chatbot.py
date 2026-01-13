from services.memory import get_latest_sensors, get_recent_detections
from services.rules import analyze_state

def get_chat_response(message):
    """
    Generates a response based on the user's message + current system context.
    """
    message = message.lower()
    
    # 1. Fetch Context
    sensors = get_latest_sensors()
    detections = get_recent_detections(limit=3)
    analysis = analyze_state(sensors, detections)
    
    response = ""
    
    # 2. Simple Intent Matching (Rule-based Chatbot)
    
    if "status" in message or "report" in message or "how is" in message:
        # User asks for general status
        if analysis['alerts']:
            response += "ATTENTION NEEDED: " + " ".join(analysis['alerts']) + "\n"
        else:
            response += "Everything looks stable. "
            
        if sensors:
            response += f"Current temperature is {sensors['temperature']}°C and humidity is {sensors['humidity']}%. "
            
        if detections:
            labels = [d['label'] for d in detections]
            response += f"Recently detected: {', '.join(set(labels))}."
        else:
            response += "No pests or diseases detected recently."
            
    elif "advice" in message or "what do" in message or "help" in message:
        # User looking for recommendations
        if analysis['advice']:
            response += "Recommendations: " + " ".join(analysis['advice'])
        else:
            response += "Conditions are optimal. Just ensure regular watering schedules."
            
    elif "temperature" in message:
        if sensors:
             response += f"Temperature is currently {sensors['temperature']}°C."
        else:
             response += "No sensor data available right now."
             
    elif "pest" in message or "disease" in message:
        if detections:
            latest = detections[0]
            response += f"I spotted a {latest['label']} recently ({int(latest['confidence']*100)}% confidence). "
            response += "Check the 'Advice' tab for treatment options."
        else:
            response += "I haven't seen any pests or diseases lately."
            
    else:
        # Fallback / Greeting
        response += "I am your Agri-Assistant. You can ask me for a 'status report', 'advice', or specific sensor readings like 'temperature'."

    return response
