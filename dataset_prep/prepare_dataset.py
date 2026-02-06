import os
import shutil
import pandas as pd
import random
import yaml
from glob import glob
from tqdm import tqdm

# Paths
WEED_PATH = "/Users/anusha/Downloads/main project/archive"
PEST_PATH = "/Users/anusha/Downloads/main project/archive-2"
DISEASE_PATH = "/Users/anusha/Downloads/main project/PlantVillage"
OUTPUT_PATH = "/Users/anusha/agri_monitoring_demo/unified_dataset"

# Ensure output directories exist - using 'valid' to match standard YOLO conventions often used, though 'val' is also common.
# Creating both to be safe or just sticking to one. YOLOv8 uses 'val'.
os.makedirs(f"{OUTPUT_PATH}/images/train", exist_ok=True)
os.makedirs(f"{OUTPUT_PATH}/images/val", exist_ok=True)
os.makedirs(f"{OUTPUT_PATH}/labels/train", exist_ok=True)
os.makedirs(f"{OUTPUT_PATH}/labels/val", exist_ok=True)

final_classes = []

def get_weed_classes():
    df = pd.read_csv(os.path.join(WEED_PATH, "labels", "labels.csv"))
    return sorted(df['Species'].unique().tolist())

def get_pest_classes():
    with open(os.path.join(PEST_PATH, "classes.txt"), 'r') as f:
        # Assuming format "ID Name" or just "Name" or "ID: Name"
        # Content saw earlier: "1: 1 rice leaf roller" (from view_file)
        # Actual content probably "1 rice leaf roller"
        lines = f.readlines()
    classes = []
    for line in lines:
        parts = line.strip().split(maxsplit=1) # split on first space
        if len(parts) > 1:
            # Check if first part is digit
            if parts[0].isdigit():
                classes.append(parts[1].strip())
            else:
               classes.append(line.strip())
    return classes

def get_disease_classes():
    # List directories in PlantVillage
    # There is a nested PlantVillage folder 'PlantVillage/PlantVillage' usually, or just 'PlantVillage'.
    # From previous ls: 'PlantVillage/Potato___Early_blight' etc. so it's direct.
    # But wait, there was also a 'PlantVillage' folder INSIDE 'PlantVillage'.
    # output: "PlantVillage": isDir true
    # I should check if the images are inside the subfolders of the root or the nested one.
    # I'll check both or assume root ones are valid classes.
    # The ls showed 'Potato___Early_blight' AND 'PlantVillage'.
    # I will ignore 'PlantVillage' folder if it is a folder.
    
    dirs = [d for d in os.listdir(DISEASE_PATH) if os.path.isdir(os.path.join(DISEASE_PATH, d))]
    classes = [d for d in dirs if d != "PlantVillage"]
    return sorted(classes)

print("Gathering classes...")
weed_classes = get_weed_classes()
pest_classes = get_pest_classes()
disease_classes = get_disease_classes()

# Unified list
# Note: 'Invasive' might be a good prefix for proper distinction?
# Or just keep them as is.
final_classes = sorted(list(set(weed_classes + pest_classes + disease_classes)))
print(f"Total Combined Classes: {len(final_classes)}")

# Create helper to process copy
def process_file(src_path, class_name, split):
    try:
        class_id = final_classes.index(class_name)
    except ValueError:
        print(f"Warning: Class {class_name} not found in final list for {src_path}")
        return

    basename = os.path.basename(src_path)
    # Avoid duplicate filenames by adding prefix if needed, but shutil.copy overwrites.
    # Optimally: prefix with dataset type to be safe.
    
    if "archive" in src_path and "archive-2" not in src_path:
        prefix = "weed_"
    elif "archive-2" in src_path:
        prefix = "pest_"
    else:
        prefix = "plant_"
        
    new_filename = f"{prefix}{basename}"
    dst_img_path = os.path.join(OUTPUT_PATH, "images", split, new_filename)
    dst_label_path = os.path.join(OUTPUT_PATH, "labels", split, new_filename.replace(os.path.splitext(new_filename)[1], ".txt"))
    
    # Copy Image
    shutil.copy2(src_path, dst_img_path)
    
    # Create Label (YOLO format: class x_center y_center width height)
    with open(dst_label_path, 'w') as f:
        f.write(f"{class_id} 0.5 0.5 1.0 1.0\n")

# --- PROCESS WEEDS ---
print("Processing Weeds...")
df = pd.read_csv(os.path.join(WEED_PATH, "labels", "labels.csv"))
# Group by species to split stratify? simple random is easier.
# Iterate rows
files = df.to_dict('records') # [{'Filename': '...', 'Species': '...'}, ...]
random.shuffle(files)
split_idx = int(len(files) * 0.8)
train_files = files[:split_idx]
val_files = files[split_idx:]

for item in tqdm(train_files):
    src = os.path.join(WEED_PATH, "images", item['Filename'])
    if os.path.exists(src):
        process_file(src, item['Species'], "train")

for item in tqdm(val_files):
    src = os.path.join(WEED_PATH, "images", item['Filename'])
    if os.path.exists(src):
        process_file(src, item['Species'], "val")

# --- PROCESS PESTS ---
print("Processing Pests...")
# Structure: archive-2/classification/train/{id}/*.jpg
# We need to map {id} to class_name using pest_classes list index.
# Assumption: folder '0' is pest_classes[0]
for split in ['train', 'val']:
    src_dir = os.path.join(PEST_PATH, "classification", split)
    if not os.path.exists(src_dir):
        continue
        
    for folder_id in os.listdir(src_dir):
        if not folder_id.isdigit(): continue
        
        folder_path = os.path.join(src_dir, folder_id)
        if not os.path.isdir(folder_path): continue
        
        idx = int(folder_id)
        if idx >= len(pest_classes):
            print(f"Warning: Folder ID {idx} out of range for pest classes.")
            continue
            
        class_name = pest_classes[idx]
        
        for img_file in os.listdir(folder_path):
            if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                src = os.path.join(folder_path, img_file)
                process_file(src, class_name, split)

# --- PROCESS DISEASES ---
print("Processing Diseases...")
all_disease_images = []
for cls in disease_classes:
    folder_path = os.path.join(DISEASE_PATH, cls)
    images = glob(os.path.join(folder_path, "*"))
    for img in images:
        if img.lower().endswith(('.jpg', '.jpeg', '.png', '.JPG')):
            all_disease_images.append((img, cls))

random.shuffle(all_disease_images)
split_idx = int(len(all_disease_images) * 0.8)
train_imgs = all_disease_images[:split_idx]
val_imgs = all_disease_images[split_idx:]

for img, cls in tqdm(train_imgs):
    process_file(img, cls, "train")
    
for img, cls in tqdm(val_imgs):
    process_file(img, cls, "val")

# --- CREATE DATA.YAML ---
yaml_content = {
    'train': os.path.join(OUTPUT_PATH, "images", "train"),
    'val': os.path.join(OUTPUT_PATH, "images", "val"),
    'nc': len(final_classes),
    'names': final_classes
}

with open(os.path.join(OUTPUT_PATH, "data.yaml"), 'w') as f:
    yaml.dump(yaml_content, f)

print("Dataset creation complete!")
print(f"Data.yaml created at {os.path.join(OUTPUT_PATH, 'data.yaml')}")
