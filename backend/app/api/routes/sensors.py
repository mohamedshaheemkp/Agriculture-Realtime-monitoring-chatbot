from flask import Blueprint, jsonify
from app.services.sensor_service import sensor_service

bp = Blueprint('sensors', __name__, url_prefix='/api/v1')

@bp.route('/sensors/telemetry')
def get_telemetry():
    """Get hardware telemetry."""
    data = sensor_service.get_data()
    return jsonify({
        "success": True,
        "data": data
    })

