from services.memory import get_latest_sensors, get_recent_detections, get_detections_summary
from services.rules import analyze_state

def get_chat_response(message):
    """
    Generates a response based on the user's message + current system context.
    """
    message = message.lower()
    
    # 1. Fetch Context
    sensors = get_latest_sensors()
    # Get last 5 detections for immediate context
    recent_detections = get_recent_detections(limit=5)
    # Get summary for broader "what's happening" context
    summary = get_detections_summary(seconds=120) 
    
    analysis = analyze_state(sensors, recent_detections)
    
    response = ""
    
    # 2. Simple Intent Matching (Rule-based Chatbot)
    
    if "status" in message or "report" in message or "how is" in message:
        # User asks for general status
        found_issues = False
        if analysis['alerts']:
            response += "ATTENTION: " + " ".join(analysis['alerts']) + "\n"
            found_issues = True
        
        if sensors:
            response += f"Temp: {sensors['temperature']}, Humidity: {sensors['humidity']}. "
            
        if summary['most_frequent']:
             response += f"I have frequently detected {summary['most_frequent']} ({summary['count']} times) in the last 2 minutes. "
        elif not found_issues:
             response += "Conditions look stable."

    elif "advice" in message or "what should i do" in message or "help" in message:
        # User looking for recommendations
        if analysis['advice']:
            response += "Recommendations: " + " ".join(analysis['advice'])
        else:
            response += "Everything looks fine. Keep monitoring soil moisture."
            
    elif "last" in message and ("detect" in message or "seen" in message or "disease" in message):
        # "What did I just show?" or "Last detected disease?"
        if recent_detections:
            latest = recent_detections[0]
            # Convert timestamp to something readable or just say "Most recently"
            response += f"The last thing I detected was **{latest['label']}** ({int(latest['confidence']*100)}% confidence)."
        else:
            response += "I haven't detected anything recently."

    elif "history" in message or "summary" in message:
         if summary['most_frequent']:
             response += f"In the last few minutes, the most common detection was {summary['most_frequent']} (seen {summary['count']} times)."
         else:
             response += "No significant detections in history log."

    elif "temperature" in message:
        if sensors:
             response += f"Temperature is currently {sensors['temperature']}."
        else:
             response += "No sensor data available right now."
             
    elif "monitor" in message:
        response += "I am monitoring the live feed. Show me a leaf and I will tell you if it's healthy."

    else:
        # Fallback / Greeting
        response += "I'm your Agri-Assistant. Ask me 'What did you see?' or 'Status report'."

    return response
