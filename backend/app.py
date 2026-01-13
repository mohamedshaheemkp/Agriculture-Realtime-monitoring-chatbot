from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from api.vision import gen_frames, get_latest_detections, predict_image_file
from api.sensors import get_sensor_data
from api.chatbot import get_chat_response

app = Flask(__name__)
CORS(app)  # enable CORS so React frontend can fetch data

@app.route('/video_feed')
def video_feed():
    # Stream for the live webcam
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/logs')
def logs():
    # Simple endpoint for simple logs
    return jsonify(get_latest_detections())

@app.route('/sensors')
def sensors():
    # Returns simulated sensor data and logs it to DB
    return jsonify(get_sensor_data())

@app.route('/chat', methods=['POST'])
def chat():
    # Context-aware chatbot
    data = request.json
    user_message = data.get('message', '')
    response = get_chat_response(user_message)
    return jsonify({"response": response})

@app.route('/predict-image', methods=['POST'])
def predict_image():
    # Endpoint for uploading an image file for analysis
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

if __name__ == '__main__':
    # Run on port 5050 to match frontend requests
    # debug=True allows hot-reload during development
    app.run(host='0.0.0.0', port=5050, debug=True)
