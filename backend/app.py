from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from api.vision import gen_frames, get_latest_detections
from api.sensors import get_sensor_data
from api.chatbot import get_chat_response

app = Flask(__name__)
CORS(app)  # enable CORS so React frontend can fetch data

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/logs')
def logs():
    return jsonify(get_latest_detections())

@app.route('/sensors')
def sensors():
    return jsonify(get_sensor_data())

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    response = get_chat_response(user_message)
    return jsonify({"response": response})

if __name__ == '__main__':
    # Run on port 5050 to match frontend requests
    app.run(host='0.0.0.0', port=5050)
