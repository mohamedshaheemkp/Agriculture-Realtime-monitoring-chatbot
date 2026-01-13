import cv2
from ultralytics import YOLO
import os

# Global variable to store latest detections
latest_detections = []

# Load YOLO model
# Set MODEL_PATH via env or default to models/best.pt
MODEL_PATH = os.environ.get("MODEL_PATH", "models/best.pt")
# Ensure the path is absolute or relative to the backend root correctly
if not os.path.exists(MODEL_PATH):
    # fallback to correct_model if best.pt missing, or check relative paths
    if os.path.exists("models/correct_model.pt"):
        MODEL_PATH = "models/correct_model.pt"
    else:
        print(f"Warning: Model not found at {MODEL_PATH}")

try:
    model = YOLO(MODEL_PATH)
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Open the default webcam
cap = cv2.VideoCapture(0)

def gen_frames():
    global latest_detections
    while True:
        try:
            success, frame = cap.read()
            if not success:
                # print("Error: Failed to read frame from webcam.")
                # break 
                # For robustness in headless/server environments without cam, we might yield a placeholder or sleep
                continue 
            
            if model:
                results = model.predict(frame, verbose=False, conf=0.5)
                
                # Update latest detections
                current_detections = []
                
                # Check for Object Detection results (boxes)
                if hasattr(results[0], 'boxes') and results[0].boxes is not None:
                    for box in results[0].boxes:
                        conf = float(box.conf[0])
                        cls_id = int(box.cls[0])
                        class_name = results[0].names[cls_id]
                        current_detections.append(f"Detected: {class_name} ({conf:.2f})")

                # Check for Classification results (probs)
                elif hasattr(results[0], 'probs') and results[0].probs is not None:
                     top1_index = results[0].probs.top1
                     top1_conf = results[0].probs.top1conf
                     if top1_conf > 0.5:
                         class_name = results[0].names[top1_index]
                         current_detections.append(f"Detected: {class_name} ({top1_conf:.2f})")
                
                if not current_detections:
                     current_detections = ["Monitoring... No significant detections"]

                latest_detections = current_detections
                annotated_frame = results[0].plot()
            else:
                annotated_frame = frame
                latest_detections = ["Model not loaded"]

            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            print(f"Error in gen_frames: {e}")
            break

def get_latest_detections():
    return latest_detections
