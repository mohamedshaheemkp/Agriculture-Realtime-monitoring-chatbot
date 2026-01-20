from flask import Flask, Response
from flask_cors import CORS
from app.core.config import Config
from app.core.database import db
from app.core.logging import configure_logger

def create_app(config_class=Config):
    # Initialize Core
    configure_logger()
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Extensions
    CORS(app)
    
    # Initialize DB
    with app.app_context():
        try:
            db.init_db()
        except Exception as e:
            print(f"DB Init Failed: {e}")

    # Register Blueprints
    from app.api.routes import vision, chat, sensors, admin, weather
    app.register_blueprint(vision.bp)
    app.register_blueprint(chat.bp)
    app.register_blueprint(sensors.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(weather.bp)

    # Legacy / Compatibility Routes (to match old frontend for now if needed, 
    # but strictly we should update frontend. We will provide redirects or direct mapping)
    
    # Map old /video_feed to new service for backward compatibility during transition
    from app.services.vision_service import vision_service
    @app.route('/video_feed')
    def legacy_video_feed():
        return Response(vision_service.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
        
    return app
