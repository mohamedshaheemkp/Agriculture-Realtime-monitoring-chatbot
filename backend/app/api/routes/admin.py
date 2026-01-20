from flask import Blueprint, jsonify
from app.services.storage_service import storage_service

bp = Blueprint('admin', __name__, url_prefix='/api/v1/admin')

@bp.route('/reset', methods=['POST'])
def reset_system():
    """Reset demo data."""
    try:
        storage_service.clear_logs()
        return jsonify({"success": True, "message": "System data cleared."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
