import os

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-key')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    PORT = int(os.environ.get('PORT', 5050))
    
    # Model Configuration
    MODEL_PATH = os.environ.get('MODEL_PATH', os.path.join(BASE_DIR, '..', 'models', 'best.pt'))
    MODEL_CONFIDENCE = float(os.environ.get('MODEL_CONFIDENCE', 0.5))
    
    # Database Configuration
    DB_PATH = os.environ.get('DB_PATH', os.path.join(BASE_DIR, '..', 'agri.db'))
    
    # Sensor Simulation Config
    SIMULATE_SENSORS = os.environ.get('SIMULATE_SENSORS', 'True') == 'True'
    
    # Vision Configuration
    CAMERA_INDEX = int(os.environ.get('CAMERA_INDEX', 0))
    LOG_COOLDOWN = float(os.environ.get('LOG_COOLDOWN', 1.0))
    
    # Weather API (Optional)
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', '')
    LOCATION_LAT = os.environ.get('LOCATION_LAT', '0')
    LOCATION_LON = os.environ.get('LOCATION_LON', '0')
