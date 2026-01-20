from app.services.storage_service import storage_service
from app.services.rule_engine import analyze_state

class ChatbotService:
    def get_response(self, message):
        """
        Generates a response based on the user's message + current system context.
        """
        message = message.lower()
        
        # 1. Fetch Context
        sensors = storage_service.get_latest_sensors()
        recent_detections = storage_service.get_recent_detections(limit=5)
        summary = storage_service.get_detections_summary(seconds=300) 
        
        analysis = analyze_state(sensors, recent_detections)
        
        response = ""
        
        # 2. Intent Matching
        if "status" in message or "report" in message or "how is" in message:
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

        elif "advice" in message or "what should i do" in message or "help" in message:
            if analysis['advice']:
                response += "Recommendations: " + " ".join(analysis['advice'])
            else:
                response += "Everything looks fine. Keep monitoring soil moisture."
                
        elif "just now" in message or "last" in message or "what did i show" in message or "what is this" in message:
            if recent_detections:
                latest = recent_detections[0]
                response += f"I just detected **{latest['label']}** with {int(latest['confidence']*100)}% confidence."
                if latest['source'] == 'upload':
                    response += " (from uploaded image)."
            else:
                response += "I haven't detected anything recently."

        elif "how many" in message or "count" in message or "times" in message:
             if summary['most_frequent']:
                 response += f"In the last 5 minutes, I saw {summary['most_frequent']} {summary['count']} times."
                 if summary['total_detections'] > summary['count']:
                     response += f" Total detections: {summary['total_detections']}."
             else:
                 response += "I haven't detected any diseases or pests in the last 5 minutes."

        elif "temperature" in message:
            if sensors:
                 response += f"Temperature is currently {sensors['temperature']}°C."
            else:
                 response += "No sensor data available right now."
        
        elif "monitor" in message:
            response += "I am monitoring the live feed. Show me a leaf and I will tell you if it's healthy."

        else:
            response += "I'm your Agri-Assistant. Ask me 'What did you see just now?', 'Status report', or 'Any alerts?'."

        return response

chatbot_service = ChatbotService()
