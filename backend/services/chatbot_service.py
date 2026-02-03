from app.services.storage_service import storage_service
from app.services.rule_engine import analyze_state

from app.services.label_normalizer import normalize_label

def call_gpt_api(system_prompt, user_prompt):
    """
    Simulates a call to an external LLM API (e.g., OpenAI).
    In a real deployment, this would use the `openai` library or `requests`.
    """
    # For now, return a placeholder or mock response.
    # We can log the prompt to see what would be sent.
    print(f"--- GPT PROMPT ---\nSystem: {system_prompt}\nUser: {user_prompt}\n--------------------")
    return "Analyzing data. Based on current readings, ensure soil moisture remains stable."

def gpt_fallback(message, sensor_data=None, detections=None):
    """
    Temporary GPT fallback placeholder.
    Replace body with real LLM call later.
    """
    sensor_data = sensor_data or {}
    detections = detections or []
    normalized_detections = [
        f"{d.get('label', 'unknown')} ({int(d.get('confidence', 0) * 100)}% confidence)"
        for d in detections
    ]
    detections_text = "\n".join(normalized_detections) if normalized_detections else "None"

    system_prompt = (
        "You are an expert agricultural advisor helping farmers interpret sensor data "
        "and crop disease detections. Provide concise, practical, and safe guidance. "
        "If data is missing, say so explicitly and avoid speculation."
    )
    user_prompt = (
        f"User question: {message}\n\n"
        "Sensor readings:\n"
        f"- Temperature: {sensor_data.get('temperature', 'N/A')}°C\n"
        f"- Humidity: {sensor_data.get('humidity', 'N/A')}%\n"
        f"- Soil moisture: {sensor_data.get('soil_moisture', 'N/A')}%\n\n"
        "Recent YOLO detections (normalized):\n"
        f"{detections_text}\n\n"
        "Respond with actionable agricultural advice in plain language."
    )
    try:
        return call_gpt_api(system_prompt, user_prompt)
    except Exception:
        return "I'm unable to reach the AI service right now. Please try again later."


def generate_status(sensors, analysis, summary):
    response = ""
    found_issues = False
    
    alerts = analysis.get('alerts', [])
    if alerts:
        response += "ATTENTION: " + " ".join(alerts) + "\n"
        found_issues = True
    
    if sensors:
        temperature = sensors.get('temperature', 'N/A')
        humidity = sensors.get('humidity', 'N/A')
        response += f"Temp: {temperature}°C, Humidity: {humidity}%. "
    else:
        response += "Sensor data unavailable. "
        
    if summary.get('most_frequent'):
         response += f"Frequent detection: {summary['most_frequent']} (seen {summary.get('count', 0)} times in last 5m). "
    elif not found_issues:
         response += "Conditions look stable."
    return response

def generate_alerts(analysis):
    alerts = analysis.get('alerts', [])
    if alerts:
        return "ATTENTION: " + " ".join(alerts)
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
        advice = analysis.get('advice', [])
        if advice:
            return "Recommendations: " + " ".join(advice)
        return "Everything looks fine. Keep monitoring soil moisture."

    if "how many" in msg or "count" in msg or "times" in msg:
         if summary.get('most_frequent'):
             response = f"In the last 5 minutes, I saw {summary['most_frequent']} {summary.get('count', 0)} times."
             if summary.get('total_detections', 0) > summary.get('count', 0):
                 response += f" Total detections: {summary.get('total_detections', 0)}."
             return response
         return "I haven't detected any diseases or pests in the last 5 minutes."

    if "temperature" in msg:
        if sensors:
             temperature = sensors.get('temperature', 'N/A')
             return f"Temperature is currently {temperature}°C."
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
        message = str(message or "").lower()
        
        # 1. Fetch Context (Separated from logic: fetched via storage service)
        try:
            sensors = storage_service.get_latest_sensors()
            recent_detections = storage_service.get_recent_detections(limit=5) or []
            summary = storage_service.get_detections_summary(seconds=300) or {}
        except Exception:
            return "I'm having trouble accessing sensor data right now. Please try again shortly."
        
        # Normalize labels
        for d in recent_detections:
            try:
                d['label'] = normalize_label(d.get('label', 'unknown'))
            except Exception:
                d['label'] = d.get('label', 'unknown')
            
        if summary.get('most_frequent'):
            try:
                summary['most_frequent'] = normalize_label(summary['most_frequent'])
            except Exception:
                summary['most_frequent'] = summary['most_frequent']
        
        # 2. Analyze State (Rule Engine)
        try:
            analysis = analyze_state(sensors, recent_detections) or {}
        except Exception:
            analysis = {}
        
        # 3. Intent Matching & Response Generation
        # Try rule-based first
        rule_response = rule_based_response(message, sensors, recent_detections, summary, analysis)
        
        if rule_response:
             return rule_response

        # 4. Fallback to GPT
        return gpt_fallback(message, sensors, recent_detections)

chatbot_service = ChatbotService()
