# Backend: Train and Configure YOLO model

This backend serves a webcam stream and runs a YOLO model to annotate frames. It also handles sensor simulation and the AI chatbot logic.

## ⚙️ Configuration

The backend reads the model file path from the environment variable `MODEL_PATH`. 
*   **Default**: `best.pt` inside the `models/` or current directory depending on setup.
*   **Custom**: `MODEL_PATH=/full/path/to/your_new_best.pt python3 app.py`

## 🏋️ How to Train with a New Dataset

### 1. Prepare Dataset
Ensure your dataset is in YOLOv8 format. 
*   **Option A (Recommended)**: Use a `dataset.yaml` file:
    ```yaml
    train: /full/path/to/dataset/images/train
    val: /full/path/to/dataset/images/val
    nc: 3
    names: ['class1','class2','class3']
    ```
*   **Option B**: Use the standard folder layout (`dataset/images`, `dataset/labels`).

### 2. Train Locally
You can use the provided helper script `train_yolo.py`.

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Run training
python3 train_yolo.py --data /path/to/dataset.yaml --epochs 50 --img 640 --name my_agri_model
```

After training, the weights will be saved in `runs/train/<name>/weights/best.pt`.

### 3. Use the New Model
Point the backend to your new model:

```bash
MODEL_PATH=runs/train/my_agri_model/weights/best.pt python3 app.py
```

## 📝 Notes
*   **GPU Training**: Training on CPU is slow. Ensure you have CUDA drivers installed and PyTorch with CUDA support if you have a compatible GPU.
*   **Dependencies**: All python requirements are listed in `requirements.txt`.

