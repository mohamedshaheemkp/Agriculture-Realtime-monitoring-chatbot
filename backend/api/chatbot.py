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
    # Get summary for broader "what's happening" context (last 5 mins)
    summary = get_detections_summary(seconds=300) 
    
    analysis = analyze_state(sensors, recent_detections)
    
    response = ""
    
    # 2. Intent Matching
    
    # A. "Status" or "Report"
    if "status" in message or "report" in message or "how is" in message:
        found_issues = False
        if analysis['alerts']:
            response += "ATTENTION: " + " ".join(analysis['alerts']) + "\n"
            found_issues = True
        
        if sensors:
            response += f"Temp: {sensors['temperature']}, Humidity: {sensors['humidity']}. "
            
        if summary['most_frequent']:
             response += f"Frequent detection: {summary['most_frequent']} (seen {summary['count']} times in last 5m). "
        elif not found_issues:
             response += "Conditions look stable."

    # B. "Advice" or "Help"
    elif "advice" in message or "what should i do" in message or "help" in message:
        if analysis['advice']:
            response += "Recommendations: " + " ".join(analysis['advice'])
        else:
            response += "Everything looks fine. Keep monitoring soil moisture."
            
    # C. "What did I just show?" (Latest detection)
    elif "just now" in message or "last" in message or "what did i show" in message or "what is this" in message:
        if recent_detections:
            latest = recent_detections[0]
            # Convert timestamp (optional, or just say 'Just now')
            response += f"I just detected **{latest['label']}** with {int(latest['confidence']*100)}% confidence."
            if latest['source'] == 'upload':
                response += " (from uploaded image)."
        else:
            response += "I haven't detected anything recently."

    # D. "How many times?" (Frequency / Summary)
    elif "how many" in message or "count" in message or "times" in message:
         if summary['most_frequent']:
             response += f"In the last 5 minutes, I saw {summary['most_frequent']} {summary['count']} times."
             if summary['total_detections'] > summary['count']:
                 response += f" Total detections: {summary['total_detections']}."
         else:
             response += "I haven't detected any diseases or pests in the last 5 minutes."

    # E. Specific queries
    elif "temperature" in message:
        if sensors:
             response += f"Temperature is currently {sensors['temperature']}."
        else:
             response += "No sensor data available right now."
             
    elif "monitor" in message:
        response += "I am monitoring the live feed. Show me a leaf and I will tell you if it's healthy."

    else:
        # Fallback / Greeting
        response += "I'm your Agri-Assistant. Ask me 'What did you see just now?', 'Status report', or 'Any alerts?'."

    return response
