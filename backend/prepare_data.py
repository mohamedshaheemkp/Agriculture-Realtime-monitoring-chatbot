import os
import shutil
import random
import glob

def prepare_dataset(source_dir, target_dir, split_ratio=0.8):
    """
    Splits a classification dataset into train and val folders.
    
    Structure expected in source_dir:
    class_a/
      img1.jpg
      ...
    class_b/
      ...
      
    Structure created in target_dir:
    train/
      class_a/
      class_b/
    val/
      class_a/
      class_b/
    """
    if not os.path.exists(source_dir):
        print(f"Source directory {source_dir} does not exist.")
        return

    if os.path.exists(target_dir):
        print(f"Target directory {target_dir} already exists. Deleting...")
        shutil.rmtree(target_dir)
    
    os.makedirs(target_dir, exist_ok=True)
    
    train_dir = os.path.join(target_dir, "train")
    val_dir = os.path.join(target_dir, "val")
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(val_dir, exist_ok=True)

    # Get all class directories
    classes = [d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))]
    print(f"Found classes: {classes}")

    for class_name in classes:
        class_source_path = os.path.join(source_dir, class_name)
        
        # Create class folders in train and val
        os.makedirs(os.path.join(train_dir, class_name), exist_ok=True)
        os.makedirs(os.path.join(val_dir, class_name), exist_ok=True)
        
        # Get all images
        images = []
        for ext in ["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"]:
            images.extend(glob.glob(os.path.join(class_source_path, ext)))
        
        random.shuffle(images)
        split_idx = int(len(images) * split_ratio)
        
        train_images = images[:split_idx]
        val_images = images[split_idx:]
        
        print(f"Processing {class_name}: {len(train_images)} train, {len(val_images)} val")
        
        for img in train_images:
            shutil.copy(img, os.path.join(train_dir, class_name, os.path.basename(img)))
            
        for img in val_images:
            shutil.copy(img, os.path.join(val_dir, class_name, os.path.basename(img)))

    print("Dataset preparation complete.")

if __name__ == "__main__":
    SOURCE = "/Users/anusha/Downloads/DLCPD-25"
    TARGET = os.path.join(os.path.dirname(__file__), "dataset")
    prepare_dataset(SOURCE, TARGET)
