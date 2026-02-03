from flask import Blueprint, jsonify, request
from app.services.chatbot_service import chatbot_service

bp = Blueprint('chat', __name__, url_prefix='/api')

@bp.route('/chat', methods=['POST'])
def chat_message():
    """
    Send a message to the AI assistant.
    
    Input JSON Schema:
    {
        "message": "string"  # Required, non-empty string
    }
    
    Unified Response Schema (200 OK):
    {
        "reply": "string",       # Primary response text (Backwards Compatible)
        "source": "string",      # "rule_based" | "gpt_fallback" | "system_error"
        "context": {             # Opportunistic context metadata
            "has_sensor_data": bool,
            "has_detections": bool
        },
        "warnings": ["string"]   # Active system alerts
    }
    
    Error Response (400 Bad Request):
    {
        "reply": "I didn't receive a message. Please try again."
    }
    """
    data = request.json or {}
    message = data.get('message', '')
    
    if not message:
        return jsonify({"reply": "I didn't receive a message. Please try again."}), 400
        
    response_data = chatbot_service.get_response(message)
    
    # Handle both legacy (string) and new (dict) response formats
    if isinstance(response_data, dict):
        return jsonify(response_data)
    else:
        # Legacy fallback
        return jsonify({"reply": str(response_data)})
