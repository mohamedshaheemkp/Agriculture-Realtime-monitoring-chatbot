import cv2
import numpy as np
from ultralytics import YOLO
import os
from services.memory import log_detection

# Global variable to store latest detections for the video feed overlay
latest_detections = []

MODEL_PATH = os.environ.get("MODEL_PATH", "models/best.pt")
# Fallback logic
if not os.path.exists(MODEL_PATH) and os.path.exists("models/correct_model.pt"):
    MODEL_PATH = "models/correct_model.pt"

print(f"Loading model from: {MODEL_PATH}")
try:
    model = YOLO(MODEL_PATH)
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Open the default webcam
cap = cv2.VideoCapture(0)

def predict_on_frame(frame):
    """
    Run inference on a single frame (numpy array).
    Returns: annotated_frame, detection_list
    """
    detections = []
    annotated_frame = frame
    
    if model:
        results = model.predict(frame, verbose=False, conf=0.5)
        annotated_frame = results[0].plot()
        
        # Extract Results
        # 1. Object Detection (Boxes)
        if hasattr(results[0], 'boxes') and results[0].boxes is not None:
            for box in results[0].boxes:
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                class_name = results[0].names[cls_id]
                detections.append({"label": class_name, "confidence": conf})
                # Log to DB
                log_detection(class_name, conf)

        # 2. Classification (Probs)
        elif hasattr(results[0], 'probs') and results[0].probs is not None:
             top1_index = results[0].probs.top1
             top1_conf = float(results[0].probs.top1conf)
             if top1_conf > 0.5:
                 class_name = results[0].names[top1_index]
                 detections.append({"label": class_name, "confidence": top1_conf})
                 # Log to DB
                 log_detection(class_name, top1_conf)
    
    return annotated_frame, detections

def predict_image_file(file_stream):
    """
    Process an uploaded image file.
    """
    # Convert string data to numpy array
    npimg = np.frombuffer(file_stream.read(), np.uint8)
    # Convert numpy array to image
    frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    
    valid_detections = []
    if frame is not None:
        _, valid_detections = predict_on_frame(frame)
        
    return valid_detections

def gen_frames():
    global latest_detections
    while True:
        try:
            success, frame = cap.read()
            if not success:
                # If cam fails/is missing, create a black frame to keep stream alive
                # time.sleep(0.1)
                # continue
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, "No Camera", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            annotated_frame, detections = predict_on_frame(frame)
            
            # Update global state for /logs endpoint (if used directly)
            current_probs = []
            for d in detections:
                current_probs.append(f"Detected: {d['label']} ({d['confidence']:.2f})")
            
            if not current_probs:
                current_probs = ["Monitoring..."]
                
            latest_detections = current_probs

            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            print(f"Error in gen_frames: {e}")
            break

def get_latest_detections():
    return latest_detections
