from flask import Blueprint, jsonify, request
from app.services.weather_service import weather_service

bp = Blueprint('weather', __name__, url_prefix='/api/v1/weather')

@bp.route('/current', methods=['GET'])
def get_current_weather():
    """
    Get current weather for the farm.
    Query Params: lat (optional), lon (optional)
    """
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    
    data = weather_service.get_current_weather(lat, lon)
    
    return jsonify({
        "success": True,
        "data": data
    })
