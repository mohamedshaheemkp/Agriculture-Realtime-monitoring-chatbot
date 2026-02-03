from flask import Blueprint, jsonify, request
from app.services.chatbot_service import chatbot_service

bp = Blueprint('chat', __name__, url_prefix='/api')

@bp.route('/chat', methods=['POST'])
def chat_message():
    """
    Send a message to the AI assistant.
    Input: { "message": "..." }
    Output: { "reply": "..." }
    """
    data = request.json or {}
    message = data.get('message', '')
    
    if not message:
        return jsonify({"reply": "I didn't receive a message. Please try again."}), 400
        
    response_text = chatbot_service.get_response(message)
    
    return jsonify({
        "reply": response_text
    })
