import cv2
import csv
import time
import argparse
import os
from ultralytics import YOLO
from datetime import datetime

# Configuration
MODEL_PATH = "runs/detect/train/weights/best.pt" # Default path after training
LOG_FILE = "detection_log.csv"
CONF_THRESHOLD = 0.5
LOG_COOLDOWN = 2.0 # Seconds between logging the same class

class DetectionLogger:
    def __init__(self, log_file):
        self.log_file = log_file
        self.last_logged = {}
        
        # Initialize CSV if not exists
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Class", "Confidence"])

    def log(self, class_name, confidence):
        now = time.time()
        if class_name in self.last_logged:
            if now - self.last_logged[class_name] < LOG_COOLDOWN:
                return # Skip if recently logged

        self.last_logged[class_name] = now
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, class_name, f"{confidence:.2f}"])
        print(f"LOGGED: {class_name} ({confidence:.2f})")

def run_webcam(model, logger):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("Starting Webcam Inference... Press 'q' to exit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, verbose=False)
        annotated_frame = results[0].plot()

        # Logging logic
        for result in results:
            boxes = result.boxes
            for box in boxes:
                conf = float(box.conf[0])
                if conf < CONF_THRESHOLD:
                    continue
                
                cls_id = int(box.cls[0])
                class_name = model.names[cls_id]
                logger.log(class_name, conf)

        cv2.imshow("Real-time Detection", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def run_image(model, logger, image_path):
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        return

    results = model(image_path)
    
    # Process results
    for result in results:
        result.show() # Show image
        result.save(filename="output_detection.jpg") 
        print(f"Output saved to output_detection.jpg")
        
        for box in result.boxes:
            conf = float(box.conf[0])
            if conf < CONF_THRESHOLD:
                continue
            cls_id = int(box.cls[0])
            class_name = model.names[cls_id]
            logger.log(class_name, conf)

    print("Image processing complete. Press any key on the image window to exit (if open) or check output file.")
    # result.show() usually opens a window waiting for a key or just returns. 
    # Ultralytics .show() relies on platform view.

def main():
    parser = argparse.ArgumentParser(description="YOLOv8 Detection & Logging")
    parser.add_argument("--mode", type=str, default="webcam", choices=["webcam", "image"], help="Mode: webcam or image")
    parser.add_argument("--image", type=str, help="Path to image file (required for image mode)")
    parser.add_argument("--model", type=str, default=MODEL_PATH, help="Path to trained .pt model")
    
    args = parser.parse_args()

    # Load Model
    if not os.path.exists(args.model):
        print(f"Scanning for model at {args.model}...")
        # Fallback to pretrained if custom training isn't done yet, just for demo
        print("Warning: Custom model not found. Using yolov8n.pt (pretrained on COCO) for demonstration.")
        print("Please train your model first using train.py")
        model = YOLO("yolov8n.pt")
    else:
        model = YOLO(args.model)

    logger = DetectionLogger(LOG_FILE)

    if args.mode == "webcam":
        run_webcam(model, logger)
    elif args.mode == "image":
        if not args.image:
            print("Error: --image argument required for image mode.")
        else:
            run_image(model, logger, args.image)

if __name__ == "__main__":
    main()
