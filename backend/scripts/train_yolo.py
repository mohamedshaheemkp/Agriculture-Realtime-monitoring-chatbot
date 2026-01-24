"""
Simple helper to train a YOLO model with the ultralytics package.

Usage:
  - Prepare your dataset in YOLOv8 format (images/labels or a dataset YAML file)
  - Example dataset layout:
      dataset/
        images/
          train/
          val/
        labels/
          train/
          val/

  - Or provide a dataset YAML (see ultralytics docs) and set DATASET_YAML to its path.

Run:
  python3 train_yolo.py --data path/to/dataset.yaml --epochs 50 --img 640 --name my_new_model

This script will call ultralytics.YOLO('yolov8n.pt').train(...)
It is minimal and intended for local training/test. Training requires GPU or will be slow on CPU.
"""

import argparse
import os
from ultralytics import YOLO


def main():
    parser = argparse.ArgumentParser(description="Train YOLO model on your dataset")
    parser.add_argument("--data", required=False, default="dataset", help="Path to dataset directory (for classification)")
    parser.add_argument("--epochs", type=int, default=5, help="Number of epochs")
    parser.add_argument("--img", type=int, default=224, help="Image size (224 for classification)")
    parser.add_argument("--name", default="runs/classify/exp")
    parser.add_argument("--pretrained", default="yolov8n-cls.pt", help="Pretrained weights to start from (default: yolov8n-cls.pt)")
    args = parser.parse_args()

    print(f"Training with data={args.data}, epochs={args.epochs}, img={args.img}, name={args.name}")

    # Ensure ultralytics can download checkpoints if needed and that the path exists
    model = YOLO(args.pretrained)

    # Call train; for classification, 'data' should typically be the folder path containing train/val
    model.train(data=args.data, epochs=args.epochs, imgsz=args.img, name=args.name)

    print("Training finished. Check the runs/classify/<name> directory for weights.")


if __name__ == '__main__':
    main()
