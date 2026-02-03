from app.services.storage_service import storage_service
from app.services.rule_engine import analyze_state

LABEL_MAP = {
    "Tomato Early blight leaf": "Early Blight",
    "Tomato mold leaf": "Leaf Mold",
    "Tomato healthy leaf": "Healthy"
}

def call_gpt_api(context, message):
    """
    Simulates a call to an external LLM API (e.g., OpenAI).
    In a real deployment, this would use the `openai` library or `requests`.
    """
    # For now, return a placeholder or mock response.
    # We can log the prompt to see what would be sent.
    print(f"--- GPT PROMPT ---\nContext: {context}\nMessage: {message}\n--------------------")
    return "Analyzing data. Based on current readings, ensure soil moisture remains stable."

def gpt_fallback(message, sensor_data=None, detections=None):
    """
    Temporary GPT fallback placeholder.
    Replace body with real LLM call later.
    """
    return {
        "reply": f"(GPT FALLBACK PLACEHOLDER) User asked: {message}",
        "source": "gpt"
    }


def generate_status(sensors, analysis, summary):
    response = ""
    found_issues = False
    
    if analysis['alerts']:
        response += "ATTENTION: " + " ".join(analysis['alerts']) + "\n"
        found_issues = True
    
    if sensors:
        response += f"Temp: {sensors['temperature']}°C, Humidity: {sensors['humidity']}%. "
        
    if summary['most_frequent']:
         response += f"Frequent detection: {summary['most_frequent']} (seen {summary['count']} times in last 5m). "
    elif not found_issues:
         response += "Conditions look stable."
    return response

def generate_alerts(analysis):
    if analysis['alerts']:
        return "ATTENTION: " + " ".join(analysis['alerts'])
    return "No active alerts. Conditions seem normal."

def generate_recent_detections(recent_detections):
    if recent_detections:
        latest = recent_detections[0]
        response = f"Just detected {latest['label']} with {int(latest['confidence']*100)}% confidence."
        if latest['source'] == 'upload':
            response += " (from uploaded image)."
        return response
    return "No recent detections found."

def rule_based_response(message, sensors, detections, summary, analysis):
    msg = message.lower()

    if "status" in msg or "report" in msg or "how is" in msg:
        return generate_status(sensors, analysis, summary)

    if "alert" in msg:
        return generate_alerts(analysis)

    if "what did you see" in msg or "just now" in msg or "last" in msg or "what is this" in msg:
        return generate_recent_detections(detections)
        
    if "advice" in msg or "what should i do" in msg or "help" in msg:
        if analysis['advice']:
            return "Recommendations: " + " ".join(analysis['advice'])
        return "Everything looks fine. Keep monitoring soil moisture."

    if "how many" in msg or "count" in msg or "times" in msg:
         if summary['most_frequent']:
             response = f"In the last 5 minutes, I saw {summary['most_frequent']} {summary['count']} times."
             if summary['total_detections'] > summary['count']:
                 response += f" Total detections: {summary['total_detections']}."
             return response
         return "I haven't detected any diseases or pests in the last 5 minutes."

    if "temperature" in msg:
        if sensors:
             return f"Temperature is currently {sensors['temperature']}°C."
        return "No sensor data available right now."
    
    if "monitor" in msg:
        return "Monitoring live feed. Show a leaf to check for disease."

    return None

class ChatbotService:
    """
    Centralized chatbot logic.
    Separates the conversation capabilities from the direct sensor/detection handling 
    by leveraging the storage service and rule engine for context.
    """
    def get_response(self, message):
        """
        Generates a response based on the user's message + current system context.
        """
        message = message.lower()
        
        # 1. Fetch Context (Separated from logic: fetched via storage service)
        sensors = storage_service.get_latest_sensors()
        recent_detections = storage_service.get_recent_detections(limit=5)
        summary = storage_service.get_detections_summary(seconds=300) 
        
        # Normalize labels
        for d in recent_detections:
            d['label'] = LABEL_MAP.get(d['label'], d['label'])
            
        if summary.get('most_frequent'):
            summary['most_frequent'] = LABEL_MAP.get(summary['most_frequent'], summary['most_frequent']) 
        
        # 2. Analyze State (Rule Engine)
        analysis = analyze_state(sensors, recent_detections)
        
        # 3. Intent Matching & Response Generation
        # Try rule-based first
        rule_response = rule_based_response(message, sensors, recent_detections, summary, analysis)
        
        if rule_response:
             return rule_response

        # 4. Fallback to GPT
        return gpt_fallback(message, sensors, recent_detections)

chatbot_service = ChatbotService()
