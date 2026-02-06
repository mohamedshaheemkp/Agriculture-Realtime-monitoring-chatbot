# Agriculture Monitoring System - Object Detection

This project unifies Weed, Pest, and Plant Disease datasets into a single YOLOv8 object detection model.

## Folder Structure
- `dataset_prep/`: Contains scripts for dataset conversion.
- `unified_dataset/`: The generated dataset (Images + Labels).
- `train.py`: Script to train the YOLOv8 model.
- `inference.py`: Script for real-time detection and logging.

## Instructions

### 1. Dataset Preparation
If you haven't already, run the preparation script to merge datasets:
```bash
python3 dataset_prep/prepare_dataset.py
```
This will create the `unified_dataset` folder with `data.yaml`.

### 2. Training the Model
Train the YOLOv8 model on the unified dataset. This requires a GPU or good CPU (M1/M2/M3 Mac is supported).
```bash
python3 train.py
```
Training logs and weights will be saved in `runs/detect/trainX/`. The best model is typically at `runs/detect/train/weights/best.pt`.

### 3. Real-time Inference (Webcam)
Run the inference script to start the webcam feed. Detections will be logged to `detection_log.csv`.
```bash
python3 inference.py --mode webcam
```
Press `q` to quit the webcam window.

### 4. Image Inference
To run detection on a specific image:
```bash
python3 inference.py --mode image --image path/to/your/image.jpg
```

## Logging
Detected objects (Weeds, Pests, Diseases) with confidence > 0.5 are logged to `detection_log.csv` with a timestamp. To prevent log spam, the same object class is only logged once every 2 seconds.
