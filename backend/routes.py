from flask import Blueprint, Response, jsonify, request
from api.vision import gen_frames, get_latest_detections, predict_image_file
from api.sensors import get_sensor_data
from api.chatbot import get_chat_response

# Create a Blueprint for the API routes
api_bp = Blueprint('api', __name__)

@api_bp.route('/video_feed')
def video_feed():
    """Stream for the live webcam."""
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@api_bp.route('/logs')
def logs():
    """Endpoint for latest detection logs."""
    return jsonify(get_latest_detections())

@api_bp.route('/sensors')
def sensors():
    """Returns sensor data and logs it to DB."""
    return jsonify(get_sensor_data())

@api_bp.route('/chat', methods=['POST'])
def chat():
    """Context-aware chatbot endpoint."""
    data = request.json or {}
    user_message = data.get('message', '')
    response = get_chat_response(user_message)
    return jsonify({"response": response})

@api_bp.route('/predict-image', methods=['POST'])
def predict_image():
    """Endpoint for uploading an image file for analysis."""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    try:
        detections = predict_image_file(file)
        return jsonify(detections)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
