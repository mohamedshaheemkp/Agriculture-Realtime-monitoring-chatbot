import os
import argparse
from ultralytics import YOLO
import torch

def freeze_layer(trainer):
    """
    Freeze specific layers during training.
    """
    model = trainer.model
    num_freeze = 10  # Freeze the first 10 layers (backbone features)
    print(f"Freezing first {num_freeze} layers")
    freeze = [f'model.{x}.' for x in range(num_freeze)]  # layers to freeze 
    for k, v in model.named_parameters(): 
        v.requires_grad = True  # train all layers 
        if any(x in k for x in freeze): 
            print(f'freezing {k}') 
            v.requires_grad = False 

def main():
    parser = argparse.ArgumentParser(description="Advanced YOLO Training Script for Agri-Disease Detection")
    parser.add_argument("--data", default="dlcpd_dataset.yaml", help="Path to dataset yaml")
    parser.add_argument("--epochs", type=int, default=50, help="Number of epochs")
    parser.add_argument("--img", type=int, default=640, help="Image size")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--pretrained", default="yolov8n.pt", help="Pretrained model path (e.g. yolov8n.pt or best.pt)")
    parser.add_argument("--freeze", action="store_true", help="Freeze backbone layers for transfer learning")
    
    args = parser.parse_args()

    print(f"Starting training with:")
    print(f"  Data: {args.data}")
    print(f"  Epochs: {args.epochs}")
    print(f"  Pretrained: {args.pretrained}")
    print(f"  Device: {'GPU' if torch.cuda.is_available() else 'CPU'}")

    # Load Model
    model = YOLO(args.pretrained)

    # Add Freeze Callback if requested
    if args.freeze:
        model.add_callback("on_train_start", freeze_layer)

    # Train
    # We use built-in augmentation (scale, fliplr, mosaic) by default in YOLOv8
    results = model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.img,
        batch=args.batch,
        name="agri_multicrop_model",
        patience=10,        # Early stopping
        save=True,
        device=0 if torch.cuda.is_available() else "cpu",
        half=True if torch.cuda.is_available() else False, # Mixed precision
        fliplr=0.5,         # Augmentation: 50% flip left-right
        degrees=10.0,       # Augmentation: +/- 10 degrees rotation
        mosaic=1.0,         # Augmentation: Mosaic enabled
    )

    print("Training Complete. Best model saved in runs/detect/agri_multicrop_model/weights/best.pt")

if __name__ == "__main__":
    main()
