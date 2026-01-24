from ultralytics import YOLO
import sys

try:
    model = YOLO("correct_model.pt")
    print(f"Model Task: {model.task}")
    print(f"Model Names: {model.names}")
except Exception as e:
    print(e)
