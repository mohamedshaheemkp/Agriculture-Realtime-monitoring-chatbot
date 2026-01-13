from flask import Flask, Response, jsonify
from flask_cors import CORS
import cv2
from ultralytics import YOLO
import os

app = Flask(__name__)
CORS(app)  # enable CORS so React frontend can fetch data

# Load YOLO model - configurable via MODEL_PATH env var
# Example: MODEL_PATH=/full/path/to/best.pt python3 backend/app.py
MODEL_PATH = os.environ.get("MODEL_PATH", "best.pt")
model = YOLO(MODEL_PATH)

# Open the default webcam (0)
cap = cv2.VideoCapture(0)

def gen_frames():
    # Stream frames from the webcam, annotate with model, and yield as multipart JPEG
    while True:
        success, frame = cap.read()
        if not success:
            # If frame read fails, break the generator. The client should handle reconnect.
            break
        results = model.predict(frame, conf=0.5, verbose=False)
        annotated_frame = results[0].plot()
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/logs')
def logs():
    # Dummy detection logs
    return jsonify(["Detected Tomato Leaf Disease", "No pests detected"])

@app.route('/sensors')
def sensors():
    # Dummy sensor data
    return jsonify({"temperature": "28°C", "humidity": "70%"})

if __name__ == '__main__':
    # Run on port 5050 to match frontend VideoFeed.js (http://localhost:5050/video_feed)
    app.run(host='0.0.0.0', port=5050)
