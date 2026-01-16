# 🚜 Comprehensive Guide: Upgrading to Multi-Crop Disease Detection

This guide explains how to upgrade your system to detect multiple crops using the DLCPD-25 dataset.

## 1. 📂 Dataset Preparation

Since DLCPD-25 is typically a **Classification** dataset (folders of images), but you want **Detection** (bounding boxes), we use a strategy where we treat the entire image as the "detected object".

### Step A: Download Dataset
Ensure you have the DLCPD-25 dataset downloaded. It should look like this:
```
raw_dlcpd/
  Tomato_Bacterial_Spot/
  Tomato_Healthy/
  Potato_Early_Blight/
  ...
```

### Step B: Convert and Format
Use the provided script to convert this structure into YOLOv8 Detection format.

```bash
cd backend
python3 convert_cls_to_det.py --source /path/to/raw_dlcpd --output dataset/dlcpd_formatted
```
This will create `dataset/dlcpd_formatted/images` and `dataset/dlcpd_formatted/labels`.

### Step C: Update Configuration
1.  Open `backend/dlcpd_dataset.yaml`.
2.  Update `path` to `dataset/dlcpd_formatted`.
3.  **Critical**: Update the `names` list in the YAML file to match exact output from Step B.

---

## 2. 🧠 Training the Model

We use `train_advanced.py` to perform Transfer Learning.

### Strategy Stats
*   **Base Model**: `yolov8n.pt` (Small, Fast) or your previous `best.pt`.
*   **Freezing**: We freeze the first 10 layers ("backbone") to retain low-level features and speed up training.
*   **Augmentation**: Creating copies of data is not needed; YOLOv8 applies real-time augmentation (Flip, Mosaic, Rotation) during training.

### Run Training
```bash
python3 train_advanced.py --data dlcpd_dataset.yaml --epochs 50 --freeze --batch 16
```

**Note**: If you have a GPU, this happens automatically. If on CPU, it will be slow.

---

## 3. 📝 Logging & Inference

The backend `api/vision.py` has been updated.

### features
1.  **CSV Logging**: All detections are saved to `backend/detections_log.csv`.
    *   Columns: `Frame, Timestamp, Plant, Disease, Confidence, Source`
2.  **Smart Labeling**: It parses labels like `Tomato_Bacterial_Spot` into:
    *   **Plant**: Tomato
    *   **Disease**: Bacterial Spot
3.  **Frame Counter**: Tracks frame numbers for video analysis.

---

## 4. 🚀 Running the Upgraded System

1.  **Set the Model Path**:
    Point to your newly trained model.
    ```bash
    export MODEL_PATH=runs/detect/agri_multicrop_model/weights/best.pt
    ```

2.  **Start the Backend**:
    ```bash
    python3 app.py
    ```

3.  **Start the Frontend**:
    ```bash
    cd ../frontend
    npm start
    ```

Your system is now a Real-Time Multi-Crop Disease Assistant! 🌿
