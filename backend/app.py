from flask import Flask, Response, jsonify
from flask_cors import CORS
import cv2
from ultralytics import YOLO
import os

app = Flask(__name__)
CORS(app)  # allow React to fetch data

# Load YOLO model - allow overriding via environment variable MODEL_PATH
# Set MODEL_PATH=/path/to/your/new/best.pt to use your trained model.
MODEL_PATH = os.environ.get("MODEL_PATH", "correct_model.pt")
model = YOLO(MODEL_PATH)

# Open the default webcam
cap = cv2.VideoCapture(0)  # Mac webcam

# Global variable to store latest detections
latest_detections = []

def gen_frames():
    global latest_detections
    while True:
        try:
            success, frame = cap.read()
            if not success:
                print("Error: Failed to read frame from webcam.")
                break # Or continue, but usually break prevents infinite loop of errors
            
            results = model.predict(frame, verbose=False, conf=0.5)
            
            # Update latest detections
            current_detections = []
            
            # Check for Object Detection results (boxes)
            if hasattr(results[0], 'boxes') and results[0].boxes is not None:
                for box in results[0].boxes:
                    # conf=0.5 in predict should filter, but we can access values here
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    class_name = results[0].names[cls_id]
                    current_detections.append(f"Detected: {class_name} ({conf:.2f})")

            # Check for Classification results (probs) - as fallback or alternative
            elif hasattr(results[0], 'probs') and results[0].probs is not None:
                 # Classification model returns probs
                 top1_index = results[0].probs.top1
                 top1_conf = results[0].probs.top1conf
                 if top1_conf > 0.5: # specific confidence threshold
                     class_name = results[0].names[top1_index]
                     current_detections.append(f"Detected: {class_name} ({top1_conf:.2f})")
            
            if not current_detections:
                 current_detections = ["Monitoring... No significant detections"]

            latest_detections = current_detections

            annotated_frame = results[0].plot()
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            print(f"Error in gen_frames: {e}")
            break

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/logs')
def logs():
    return jsonify(latest_detections)

@app.route('/sensors')
def sensors():
    return jsonify({"temperature": "28°C", "humidity": "70%"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)

