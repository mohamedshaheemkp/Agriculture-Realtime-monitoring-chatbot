from flask import Blueprint, jsonify, request
from app.services.chatbot_service import chatbot_service

bp = Blueprint('chat', __name__, url_prefix='/api/v1/chat')

@bp.route('/message', methods=['POST'])
def chat_message():
    """
    Send a message to the AI assistant.
    Input: { "message": "..." }
    Output: { "success": true, "data": { "reply": "..." } }
    """
    data = request.json or {}
    message = data.get('message', '')
    
    if not message:
        return jsonify({"success": False, "error": "Message is required"}), 400
        
    response_text = chatbot_service.get_response(message)
    
    return jsonify({
        "success": True,
        "data": {
            "reply": response_text
        }
    })
