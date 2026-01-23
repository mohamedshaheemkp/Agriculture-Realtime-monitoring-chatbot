
from ultralytics import YOLO
import os
import torch
import sys

def train_unified_model():
    # 1. Setup Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATASET_YAML = os.path.join(BASE_DIR, "unified_dataset", "data.yaml")
    
    if not os.path.exists(DATASET_YAML):
        print(f"Error: Dataset not found at {DATASET_YAML}")
        print("Please run 'dataset_unifier.py' first.")
        sys.exit(1)

    # 2. Select Device
    device = '0' if torch.cuda.is_available() else 'cpu'
    print(f"Using Device: {device}")
    if device == 'cpu':
        print("WARNING: Training on CPU will be extremely slow. GPU recommended.")

    # 3. Initialize Model
    # 'yolov8n.pt' is Nano - fastest, good for RPi/Edge. 
    # 'yolov8s.pt' is Small - better accuracy, still fast.
    # We choose Small for a balance of professional accuracy and speed.
    model = YOLO('yolov8s.pt') 

    # 4. Train
    print("Starting Training...")
    results = model.train(
        data=DATASET_YAML,
        epochs=100,             # Professional standard for convergence
        imgsz=640,              # Standard YOLO resolution
        batch=16,               # Adjust based on GPU VRAM (16 is safe for 8GB)
        patience=15,            # Early stopping patience
        save=True,              # Save checkpoints
        device=device,
        workers=4,              # CPU dataloader workers
        project='agri_models',  # Output folder
        name='unified_v1',      # Run name
        exist_ok=True,          # Overwrite existing run
        pretrained=True,        # Transfer learning
        optimizer='auto',       # SGD or AdamW
        verbose=True,
        seed=42,                # Reproducibility
        
        # Augmentations (handled in unifier, but YOLO adds mosaic on the fly)
        # We keep some lightweight YOLO augs enabled for robustness
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=10.0,
        translate=0.1,
        scale=0.5,
        shear=0.0,
        perspective=0.0,
        flipud=0.0,
        fliplr=0.5,
        mosaic=1.0,  # Mosaic is excellent for small objects (insects/diseases)
        mixup=0.1,
    )

    # 5. Validation/Export
    print("Training Complete. Validating...")
    metrics = model.val()
    print(f"mAP@50-95: {metrics.box.map}")
    print(f"mAP@50: {metrics.box.map50}")

    # Export for deployment (ONNX for industry interoperability)
    print("Exporting model to ONNX...")
    model.export(format='onnx')

if __name__ == "__main__":
    train_unified_model()
