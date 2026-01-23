
import os
import shutil
import random
import yaml
import cv2
import numpy as np
import glob
from pathlib import Path
from tqdm import tqdm

# --- CONFIGURATION ---
TARGET_IMG_SIZE = 640
VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp'}

# Master Class List (Professional Agricultural Standard)
# Mapped to ID 0-24 based on the provided YAML
CLASS_NAMES = [
    "Apple_Scab", "Apple_Black_Rot", "Apple_Cedar_Rust", "Apple_Healthy",
    "Grape_Black_Rot", "Grape_Esca", "Grape_Leaf_Blight", "Grape_Healthy",
    "Corn_Common_Rust", "Corn_Gray_Leaf_Spot", "Corn_Healthy",
    "Potato_Early_Blight", "Potato_Late_Blight", "Potato_Healthy",
    "Tomato_Bacterial_Spot", "Tomato_Early_Blight", "Tomato_Late_Blight",
    "Tomato_Leaf_Mold", "Tomato_Septoria_Leaf_Spot", "Tomato_Spider_Mites",
    "Tomato_Target_Spot", "Tomato_Mosaic_Virus", "Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato_Healthy", "Pepper_Bacterial_Spot", "Pepper_Healthy"
]

CLASS_MAP = {name: i for i, name in enumerate(CLASS_NAMES)}

def verify_label(label_path, img_width, img_height, fix=True):
    """
    Verifies and fixes YOLO label coordinates.
    Format: class x_center y_center width height (normalized)
    """
    valid_lines = []
    has_changes = False
    
    if not os.path.exists(label_path):
        return None

    with open(label_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        parts = line.strip().split()
        if len(parts) != 5:
            continue
            
        cls = int(parts[0])
        x, y, w, h = map(float, parts[1:])
        
        # Check normalization bounds
        if x > 1 or y > 1 or w > 1 or h > 1:
            # Attempt to normalize if raw pixels were used (simple heuristic)
            if x > 1: x /= img_width
            if y > 1: y /= img_height
            if w > 1: w /= img_width
            if h > 1: h /= img_height
            has_changes = True

        # Clip values to [0, 1]
        x = max(0, min(1, x))
        y = max(0, min(1, y))
        w = max(0, min(1, w))
        h = max(0, min(1, h))
        
        if w > 0 and h > 0:
            valid_lines.append(f"{cls} {x:.6f} {y:.6f} {w:.6f} {h:.6f}")
        else:
            has_changes = True # Dropped invalid box

    if has_changes and fix:
        with open(label_path, 'w') as f:
            f.write('\n'.join(valid_lines))
            
    return valid_lines

def augment_image(img, label_lines):
    """
    Applies random augmentations: Flip, Brightness, Noise.
    Returns: augmented_img, corrected_label_lines
    """
    aug_img = img.copy()
    aug_labels = []
    
    # 1. Horizontal Flip (50% chance)
    if random.random() > 0.5:
        aug_img = cv2.flip(aug_img, 1)
        for line in label_lines:
            parts = line.split()
            cls = parts[0]
            x = float(parts[1])
            # Flip x-coordinate: new_x = 1 - old_x
            new_x = 1.0 - x
            aug_labels.append(f"{cls} {new_x:.6f} {parts[2]} {parts[3]} {parts[4]}")
    else:
        aug_labels = label_lines

    # 2. Brightness/Contrast
    if random.random() > 0.5:
        alpha = random.uniform(0.8, 1.2) # Contrast
        beta = random.uniform(-30, 30)   # Brightness
        aug_img = cv2.convertScaleAbs(aug_img, alpha=alpha, beta=beta)
        
    return aug_img, aug_labels

def process_dataset(source_dirs, output_dir, train_ratio=0.8, val_ratio=0.1):
    """
    Main unification function.
    
    Args:
        source_dirs (list): List of paths to raw dataset folders.
                            Assumes structure: root/images, root/labels match by filename.
        output_dir (str): unified dataset path
    """
    # 1. Setup Directories
    print(f"Initializing Unified Dataset at {output_dir}...")
    
    splits = ['train', 'val', 'test']
    for split in splits:
        os.makedirs(os.path.join(output_dir, 'images', split), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'labels', split), exist_ok=True)

    all_samples = [] # Tuple (img_path, label_path)

    # 2. Scan Sources
    print("Scanning source datasets...")
    for source in source_dirs:
        # Recursive search for images
        img_files = []
        for ext in VALID_EXTENSIONS:
            img_files.extend(glob.glob(os.path.join(source, '**', f'*{ext}'), recursive=True))
            
        print(f"Found {len(img_files)} images in {source}")
        
        for img_path in img_files:
            # Infer label path (Assumes standard: /images/x.jpg corresponding to /labels/x.txt)
            # OR same directory.
            path_obj = Path(img_path)
            
            # Strategy A: Check same folder
            label_possibilities = [
                path_obj.with_suffix('.txt'),
                # Strategy B: Check parallel 'labels' folder
                Path(str(path_obj).replace('images', 'labels')).with_suffix('.txt')
            ]
            
            label_path = None
            for p in label_possibilities:
                if p.exists():
                    label_path = p
                    break
            
            if label_path:
                all_samples.append((str(img_path), str(label_path)))
            else:
                # print(f"Warning: No label found for {img_path}. Skipping.")
                pass

    print(f"Total valid samples found: {len(all_samples)}")
    
    # 3. Shuffle and Split
    random.seed(42)
    random.shuffle(all_samples)
    
    n_total = len(all_samples)
    n_train = int(n_total * train_ratio)
    n_val = int(n_total * val_ratio)
    
    splits_data = {
        'train': all_samples[:n_train],
        'val': all_samples[n_train:n_train+n_val],
        'test': all_samples[n_train+n_val:]
    }

    # 4. Process and Move
    class_counts = {name: 0 for name in CLASS_NAMES}

    for split, samples in splits_data.items():
        print(f"Processing {split} set ({len(samples)} images)...")
        
        for img_src, lbl_src in tqdm(samples):
            # Read Image
            img = cv2.imread(img_src)
            if img is None:
                continue
                
            h, w, _ = img.shape
            
            # Read and Verify Label
            valid_lines = verify_label(lbl_src, w, h)
            if not valid_lines:
                continue

            # Update Class Counts
            for line in valid_lines:
                cid = int(line.split()[0])
                if 0 <= cid < len(CLASS_NAMES):
                    class_counts[CLASS_NAMES[cid]] += 1

            # Destination Paths
            filename = os.path.basename(img_src)
            file_root = os.path.splitext(filename)[0]
            
            dst_img_path = os.path.join(output_dir, 'images', split, filename)
            dst_lbl_path = os.path.join(output_dir, 'labels', split, f"{file_root}.txt")
            
            # Save Original
            shutil.copy(img_src, dst_img_path)
            with open(dst_lbl_path, 'w') as f:
                f.write('\n'.join(valid_lines))

            # 5. AUGMENTATION (Train set only, if class is under-represented)
            # Simple logic: if in train set, add one augmented version
            if split == 'train':
                 aug_img, aug_lbls = augment_image(img, valid_lines)
                 
                 aug_filename = f"aug_{filename}"
                 aug_dst_img = os.path.join(output_dir, 'images', split, aug_filename)
                 aug_dst_lbl = os.path.join(output_dir, 'labels', split, f"aug_{file_root}.txt")
                 
                 cv2.imwrite(aug_dst_img, aug_img)
                 with open(aug_dst_lbl, 'w') as f:
                     f.write('\n'.join(aug_lbls))

    # 6. Generate data.yaml
    yaml_data = {
        'path': os.path.abspath(output_dir),
        'train': 'images/train',
        'val': 'images/val',
        'test': 'images/test',
        'names': {i: name for i, name in enumerate(CLASS_NAMES)}
    }
    
    with open(os.path.join(output_dir, 'data.yaml'), 'w') as f:
        yaml.dump(yaml_data, f, sort_keys=False)
        
    print("\nProcessing Complete.")
    print("Class Distribution:", class_counts)
    print(f"Data YAML saved to {os.path.join(output_dir, 'data.yaml')}")

if __name__ == "__main__":
    # Example usage:
    # 1. Place raw datasets in 'backend/raw_data'
    # 2. Run this script
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RAW_DATA_ROOT = os.path.join(BASE_DIR, "raw_data")
    OUTPUT_UNIFIED = os.path.join(BASE_DIR, "unified_dataset")
    
    # Auto-detect subfolders in raw_data
    if os.path.exists(RAW_DATA_ROOT):
        sources = [os.path.join(RAW_DATA_ROOT, d) for d in os.listdir(RAW_DATA_ROOT) if os.path.isdir(os.path.join(RAW_DATA_ROOT, d))]
        if sources:
            process_dataset(sources, OUTPUT_UNIFIED)
        else:
            print(f"No subdirectories found in {RAW_DATA_ROOT}. Please add datasets.")
    else:
        print(f"Please create '{RAW_DATA_ROOT}' and place your datasets there.")
        os.makedirs(RAW_DATA_ROOT, exist_ok=True)
