import cv2
import numpy as np
from ultralytics import YOLO
import threading
import time
import os
import csv
import logging
from app.services.storage_service import storage_service
from app.core.config import Config

logger = logging.getLogger(__name__)

class VisionService:
    def __init__(self):
        self.camera = None
        self.model = None
        self.lock = threading.Lock()
        self.latest_detections_display = ["Initializing..."]
        
        # State
        self.output_frame = None
        self.thread = None
        self.running = False
        
        # Logging State
        self.last_logged_time = {} 
        self.rolling_history = [] 
        self.frame_count = 0
        
        # CSV Logging
        self.log_file_csv = "logs/detections_log.csv"
        os.makedirs("logs", exist_ok=True)
        if not os.path.exists(self.log_file_csv):
            with open(self.log_file_csv, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Frame", "Timestamp", "Plant", "Disease", "Confidence", "Source"])

    def load_model(self):
        if self.model is None:
            path = Config.MODEL_PATH
            logger.info(f"Loading YOLO model from {path}...")
            try:
                self.model = YOLO(path)
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                self.model = None

    def start_processing(self):
        """Starts the background thread for camera processing if not running."""
        if self.thread is None or not self.thread.is_alive():
            self.running = True
            self.thread = threading.Thread(target=self._process_loop, daemon=True)
            self.thread.start()
            logger.info("Vision processing thread started.")

    def _process_loop(self):
        """Main loop that reads camera and runs inference."""
        self.get_camera() # Ensure camera is open
        if not self.camera or not self.camera.isOpened():
             logger.error("Camera could not be opened. Exiting loop.")
             return

        if self.model is None:
            self.load_model()

        while self.running:
            success, frame = self.camera.read()
            if not success:
                logger.warning("Camera read failed. Retrying...")
                # Simple retry logic
                self.camera.release()
                time.sleep(1)
                self.camera = cv2.VideoCapture(Config.CAMERA_INDEX)
                continue

            self.frame_count += 1
            
            # Run Inference
            annotated_frame, detections = self.detect_on_frame(frame, source="webcam")
            
            # Update Lock-protected State
            with self.lock:
                self.output_frame = annotated_frame.copy()
            
            # Update Detections Display
            current_probs = [f"Detected: {d['label']} ({d['confidence']:.2f})" for d in detections]
            if not current_probs:
                current_probs = ["Monitoring..."]
            self.latest_detections_display = current_probs
            
            # Sleep slightly to limit CPU usage if needed, or run full speed
            # time.sleep(0.01) 

    def get_camera(self):
        if self.camera is None or not self.camera.isOpened():
            logger.info("Opening Camera...")
            self.camera = cv2.VideoCapture(Config.CAMERA_INDEX)
            time.sleep(0.5)
        return self.camera

    def release_resources(self):
        self.running = False
        if self.thread:
            self.thread.join()
        if self.camera:
            self.camera.release()
            self.camera = None

    def should_log_db(self, label):
        """Debounce DB logging."""
        now = time.time()
        last = self.last_logged_time.get(label, 0)
        if last == 0 or (now - last) > Config.LOG_COOLDOWN:
            self.last_logged_time[label] = now
            return True
        return False

    def detect_on_frame(self, frame, source="webcam"):
        """Runs inference on a frame and returns annotated frame + detections list."""
        detections = []
        annotated_frame = frame
        
        if self.model:
            results = self.model.predict(frame, verbose=False, conf=Config.MODEL_CONFIDENCE)
            annotated_frame = results[0].plot()
            
            # Extract results
            found_items = []
            
            if hasattr(results[0], 'boxes') and results[0].boxes is not None:
                for box in results[0].boxes:
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    label = results[0].names[cls_id]
                    found_items.append((label, conf))
                    
            if hasattr(results[0], 'probs') and results[0].probs is not None:
                try:
                    top1_index = results[0].probs.top1
                    top1_conf = float(results[0].probs.top1conf)
                    if top1_conf > Config.MODEL_CONFIDENCE:
                        label = results[0].names[top1_index]
                        found_items.append((label, top1_conf))
                except Exception:
                    pass

            for label, conf in found_items:
                # Format Label
                parts = label.split('_', 1)
                if len(parts) > 1:
                    plant_name = parts[0]
                    disease_name = parts[1].replace('_', ' ')
                else:
                    plant_name = "Unknown"
                    disease_name = label
                
                display_label = f"{plant_name}: {disease_name}"
                detections.append({"label": display_label, "confidence": conf})
                
                # Log to CSV
                timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
                with open(self.log_file_csv, mode='a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([self.frame_count, timestamp, plant_name, disease_name, f"{conf:.4f}", source])
                
                # Log to DB (Debounced)
                if self.should_log_db(display_label):
                    storage_service.log_detection(display_label, conf, source)
                    
                    # Update rolling history (Thread safe copy?)
                    # Since this is in the loop, we can just append
                    self.rolling_history.append({
                        "label": display_label,
                        "confidence": conf,
                        "timestamp": time.strftime("%H:%M:%S")
                    })
                    if len(self.rolling_history) > 20:
                        self.rolling_history.pop(0)

        return annotated_frame, detections

    def generate_frames(self):
        """Generator for MJPEG stream."""
        # Ensure processing is running
        self.start_processing()
        
        while True:
            with self.lock:
                if self.output_frame is None:
                    continue
                # Encode the frame in Jpeg format
                (flag, encodedImage) = cv2.imencode(".jpg", self.output_frame)
            
            if not flag:
                continue
                
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
            
            # Simple throttle to control stream FPS
            time.sleep(0.05) 

    def predict_image_file(self, file_stream):
        """Process an uploaded image."""
        # Ensure model loaded
        if self.model is None:
            self.load_model()
            
        npimg = np.frombuffer(file_stream.read(), np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        
        valid_detections = []
        if frame is not None:
             _, valid_detections = self.detect_on_frame(frame, source="upload")
             
        return valid_detections

    def get_latest_status(self):
        return self.latest_detections_display

vision_service = VisionService()
