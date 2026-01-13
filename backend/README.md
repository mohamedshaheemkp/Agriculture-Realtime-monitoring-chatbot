# Backend: Train and Configure YOLO model

This backend serves a webcam stream and runs a YOLO model to annotate frames.

What I changed
- Backend now reads the model file path from the environment variable `MODEL_PATH`. Default is `best.pt`.
  - Example: `MODEL_PATH=/full/path/to/your_new_best.pt python3 app.py`
- Added `train_yolo.py` — a helper script that wraps `ultralytics.YOLO.train()` to train on a new dataset.
- Added a `requirements.txt` listing the core Python dependencies.

How to replace/train with your new dataset

1) Prepare dataset in YOLOv8 format

- Option A: Use a dataset YAML file (recommended). Minimal example (`dataset.yaml`):

```yaml
train: /full/path/to/dataset/images/train
val: /full/path/to/dataset/images/val
nc: 3
names: ['class1','class2','class3']
```

- Option B: Use the images/labels folder layout under a `dataset/` folder. See Ultralytics docs for details.

2) Train a model locally

Install dependencies (use a virtualenv):

```bash
cd /path/to/agri_monitoring_demo/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# ultralytics may install additional packages and optionally GPU drivers are needed for CUDA
```

Train using the helper script:

```bash
python3 train_yolo.py --data /path/to/dataset.yaml --epochs 50 --img 640 --name my_agri_model
```

After training you'll find weights in `runs/train/<name>/weights/` (e.g., `best.pt`).

3) Use the new model with the backend

- Either move the produced `best.pt` into the `backend/` folder and run the server normally:

```bash
# example: copy best.pt to backend/
cp runs/train/my_agri_model/weights/best.pt backend/my_new_best.pt
MODEL_PATH=backend/my_new_best.pt python3 app.py
```

- Or point `MODEL_PATH` to the full path of your trained model:

```bash
MODEL_PATH=/full/path/to/runs/train/my_agri_model/weights/best.pt python3 app.py
```

Notes and caveats
- Training on CPU is slow. For practical training use a GPU and ensure CUDA drivers and PyTorch with CUDA are installed.
- The `ultralytics` package's API may change; the helper script is minimal and intended for common setups.
- If you only want to test the frontend connectivity without running the heavy model, you can temporarily bypass model inference in `app.py` (stream raw frames) — contact me and I'll add a debug endpoint.

If you'd like, I can:
- Add a script to convert common annotation formats to YOLO format.
- Add a debug-only endpoint that streams raw camera frames (no model) so you can test the UI quickly.
- Patch the frontend to let you upload a model or change `MODEL_PATH` from configuration.

Tell me which next step you want and I will implement it.
