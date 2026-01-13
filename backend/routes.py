from flask import Blueprint, Response, jsonify, request
from api.vision import gen_frames, get_latest_detections_display, predict_image_file
from api.sensors import get_sensor_data
from api.chatbot import get_chat_response
from services.memory import get_recent_detections, get_detections_summary

# Create a Blueprint for the API routes
api_bp = Blueprint('api', __name__)

@api_bp.route('/video_feed')
def video_feed():
    """Stream for the live webcam."""
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@api_bp.route('/logs')
def logs():
    """Endpoint for realtime display logs (current frame)."""
    return jsonify(get_latest_detections_display())

@api_bp.route('/detections/latest')
def logs_latest():
    """Get the most recent logged detections from DB."""
    limit = request.args.get('limit', 5)
    return jsonify(get_recent_detections(limit=int(limit)))

@api_bp.route('/detections/history')
def logs_history():
    """Alias for history."""
    return jsonify(get_recent_detections(limit=20))

@api_bp.route('/detections/summary')
def logs_summary():
    """Get summary of recent activity."""
    seconds = request.args.get('seconds', 60)
    return jsonify(get_detections_summary(seconds=int(seconds)))

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
