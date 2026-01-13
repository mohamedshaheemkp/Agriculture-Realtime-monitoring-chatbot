from flask import Flask
from flask_cors import CORS
from routes import api_bp

# Initialize Flask App
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Register Blueprints
app.register_blueprint(api_bp)

if __name__ == '__main__':
    # Run on port 5050 to match frontend requests
    # debug=True allows hot-reload during development
    print("🚀 Starting Agri-Monitoring Backend on port 5050...")
    app.run(host='0.0.0.0', port=5050, debug=True)
