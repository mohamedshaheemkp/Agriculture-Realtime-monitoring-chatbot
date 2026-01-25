from ultralytics import YOLO
from pathlib import Path

# Paths
MODEL_PATH = Path("../../models/best.pt")
DATA_YAML = Path("../../scripts/dlcpd_dataset.yaml")

# Load model
model = YOLO(str(MODEL_PATH))

# Run validation
metrics = model.val(
    data=str(DATA_YAML),
    split="val",
    project="../results",
    name="val",
    save_json=True
)

# Print key metrics (for terminal + viva)
print("\n=== VALIDATION METRICS ===")
print(f"mAP@0.5       : {metrics.box.map50:.4f}")
print(f"mAP@0.5:0.95  : {metrics.box.map:.4f}")
print(f"Precision     : {metrics.box.mp:.4f}")
print(f"Recall        : {metrics.box.mr:.4f}")
