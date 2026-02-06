from ultralytics import YOLO
import argparse
import os

# Define dataset path
dataset_yaml = "/Users/anusha/agri_monitoring_demo/unified_dataset/data.yaml"

def main():
    parser = argparse.ArgumentParser(description="Train YOLOv8 on the unified dataset")
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    args = parser.parse_args()

    # Load a model
    model = YOLO("yolov8n.pt")  # load a pretrained model

    print(f"Starting training for {args.epochs} epochs...")
    
    # Train the model
    try:
        # Use MPS (Metal Performance Shaders) for Mac acceleration if available
        # workers=0 is often safer for debugging on some systems to avoid multiprocessing issues
        model.train(
            data=dataset_yaml, 
            epochs=args.epochs, 
            imgsz=args.imgsz, 
            batch=args.batch,
            device="mps" 
        )
    except Exception as e:
        print(f"MPS Training failed: {e}")
        print("Falling back to CPU...")
        model.train(
            data=dataset_yaml, 
            epochs=args.epochs, 
            imgsz=args.imgsz, 
            batch=args.batch,
            device="cpu"
        )

    # Validate
    print("Validating model...")
    metrics = model.val()
    print(f"mAP50-95: {metrics.box.map}")

    # Export
    print("Exporting model to ONNX...")
    success = model.export(format="onnx")
    print(f"Model exported: {success}")

if __name__ == '__main__':
    main()
