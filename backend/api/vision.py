import cv2
import numpy as np
from ultralytics import YOLO
import os
import time
from services.memory import log_detection

# Global variable for web view
latest_detections = []

# Logging State
last_logged_time = {} # Key: label, Value: timestamp
LOG_COOLDOWN = 2.0 # Seconds
ROLLING_HISTORY = [] # Maintain rolling history of detections

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

def should_log(label):
    """
    Check if we should log this label (limit frequency).
    Log if it is new or after cooldown.
    """
    now = time.time()
    last = last_logged_time.get(label, 0)
    
    # Log if it's the first time seeing this label or if cooldown has passed
    if last == 0 or (now - last) > LOG_COOLDOWN:
        last_logged_time[label] = now
        return True
    return False

def update_rolling_history(label, conf):
    """
    Maintain rolling history of detections.
    Keep last 20 detections.
    """
    global ROLLING_HISTORY
    timestamp = time.strftime("%H:%M:%S", time.localtime())
    detection = {
        "label": label,
        "confidence": conf,
        "timestamp": timestamp
    }
    ROLLING_HISTORY.append(detection)
    if len(ROLLING_HISTORY) > 20:
        ROLLING_HISTORY.pop(0)

def predict_on_frame(frame, source="webcam"):
    """
    Run inference on a single frame (numpy array).
    Returns: annotated_frame, detection_list
    """
    detections = []
    annotated_frame = frame
    
    if model:
        results = model.predict(frame, verbose=False, conf=0.5)
        annotated_frame = results[0].plot()
        
        # Helper to process result item
        def process_det(label, conf):
            detections.append({"label": label, "confidence": conf})
            
            # Log Detection with Deduplication Logic
            if should_log(label):
                # print(f"Logging {label} from {source}")
                log_detection(label, conf, source)
                update_rolling_history(label, conf)

        # 1. Object Detection (Boxes)
        if hasattr(results[0], 'boxes') and results[0].boxes is not None:
            for box in results[0].boxes:
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                class_name = results[0].names[cls_id]
                process_det(class_name, conf)

        # 2. Classification (Probs)
        elif hasattr(results[0], 'probs') and results[0].probs is not None:
             top1_index = results[0].probs.top1
             top1_conf = float(results[0].probs.top1conf)
             if top1_conf > 0.5:
                 class_name = results[0].names[top1_index]
                 process_det(class_name, top1_conf)
    
    return annotated_frame, detections

def predict_image_file(file_stream):
    """
    Process an uploaded image file.
    """
    npimg = np.frombuffer(file_stream.read(), np.uint8)
    frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    
    valid_detections = []
    if frame is not None:
        # For uploads, we might want to force log (or use same debounce).
        # Let's say uploads always log because it's a deliberate user action.
        # But predict_on_frame handles logging. We can bypass debounce by
        # clearing cache or just passing source="upload" and handling it?
        # For simplicity, we stick to the same debounce or we can clear:
        # last_logged_time.clear() # Optional: clear debounce for uploads
        
        # Actually, for uploads, we probably want to log every single time.
        # Let's modify predict_on_frame slightly or just clear cache for specific items?
        # easier: just run it. The debounce is per-label. 
        # If user uploads same image twice in 2s, maybe satisfying to not log twice.
        _, valid_detections = predict_on_frame(frame, source="upload")
        
    return valid_detections

def gen_frames():
    global latest_detections
    while True:
        try:
            success, frame = cap.read()
            if not success:
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, "No Camera", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # This is the LIVE WEBCAM loop
            annotated_frame, detections = predict_on_frame(frame, source="webcam")
            
            # Update global state for /logs endpoint
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

def get_latest_detections_display():
    return latest_detections

def get_rolling_history():
    return ROLLING_HISTORY
