
from flask import Blueprint, jsonify, request
from app.services.vision_service import vision_service
from app.services.weather_service import weather_service
from app.services.remedy_service import remedy_service
import logging

bp = Blueprint('remedy', __name__, url_prefix='/api/v1/remedy')
logger = logging.getLogger(__name__)

@bp.route('/analyze', methods=['POST'])
def analyze_and_recommend():
    """
    Unified Endpoint: Upload Image -> Get Detections -> Check Weather -> Get Remedy
    
    Accepts: multipart/form-data with 'file'
    Returns: JSON with detailed analysis and context-aware recommendations.
    """
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded", "code": "MISSING_FILE"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "No file selected", "code": "EMPTY_FILENAME"}), 400
        
    try:
        # 1. Vision Analysis
        # Returns list of dicts: [{'label': 'Potato_Early_Blight', 'confidence': 0.95}, ...]
        detections = vision_service.predict_image_file(file)
        
        # 2. Weather Context
        # Fetches real-time or simulated weather
        weather = weather_service.get_current_weather()
        
        # 3. Intelligent Remedy Resolution
        results = []
        
        if not detections:
            # Handle case with no detections (Healthy or Unknown)
            results.append({
                "detection": "None",
                "confidence": 0,
                "recommendation": {
                     "remedy": "Continue routine monitoring.",
                     "reasoning": "No threats detected in the uploaded image.",
                     "alert_level": "Low"
                }
            })
        else:
            for d in detections:
                label = d['label']
                conf = d['confidence']
                
                # Filter low confidence only if strictly needed, but vision service usually handles generic thresholds.
                # Here we trust the vision service's output.
                
                recommendation = remedy_service.recommend(label, weather)
                
                results.append({
                    "detection": label,
                    "confidence": float(conf),
                    "recommendation": recommendation
                })

        # 4. Construct Final Response
        response = {
            "success": True,
            "weather_context": {
                "condition": weather.get('condition'),
                "temp_c": weather.get('temp_c'),
                "wind_kph": weather.get('wind_kph'),
                "humidity_pct": weather.get('humidity_pct')
            },
            "analysis": results
        }
        
        return jsonify(response)

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        return jsonify({
            "success": False, 
            "error": "Internal Processing Error", 
            "details": str(e)
        }), 500
