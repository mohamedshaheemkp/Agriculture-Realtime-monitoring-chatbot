from flask import Blueprint, jsonify, request, Response
from app.services.vision_service import vision_service
from app.services.storage_service import storage_service

bp = Blueprint('vision', __name__, url_prefix='/api/v1/vision')

@bp.route('/analyze', methods=['POST'])
def analyze_image():
    """Upload and analyze an image."""
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "No file selected"}), 400
        
    try:
        result = vision_service.predict_image_file(file)
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@bp.route('/history')
def get_history():
    """Get recent detections."""
    limit = request.args.get('limit', 10)
    data = storage_service.get_recent_detections(limit=int(limit))
    return jsonify({
        "success": True,
        "data": data
    })

@bp.route('/summary')
def get_summary():
    """Get detection summary."""
    seconds = request.args.get('seconds', 60)
    data = storage_service.get_detections_summary(seconds=int(seconds))
    return jsonify({
        "success": True,
        "data": data
    })

# Note: video feed is often root relative or separate, but we can put it here or keep it simple
# The old frontend expects /video_feed at root, so we might need a legacy mapping or update frontend.
# For industry standard, we'll keep it under /api/v1/vision/feed if possible, 
# but strictly speaking stream URLs are often distinct. 
# We will add it here, but we might also support a legacy route in __init__ if needed.

@bp.route('/feed')
def video_feed():
    """MJPEG Video Feed."""
    return Response(vision_service.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@bp.route('/logs/current')
def current_logs():
    """Current frame status display (for overlay)."""
    return jsonify({
        "success": True,
        "data": vision_service.get_latest_status()
    })
