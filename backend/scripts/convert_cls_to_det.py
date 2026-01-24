import os
import shutil
import random
import argparse
from pathlib import Path
from PIL import Image

def get_image_files(directory):
    return list(Path(directory).glob("*.[jJ][pP][gG]")) + list(Path(directory).glob("*.[pP][nN][gG]"))

def convert_to_yolo_detection(source_dir, output_dir, split_ratio=0.8):
    """
    Converts a classification dataset (folders of images) into a YOLO Detection dataset.
    It generates dummy bounding boxes covering the entire image (or center crop).
    """
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    
    images_train = output_path / 'images/train'
    images_val = output_path / 'images/val'
    labels_train = output_path / 'labels/train'
    labels_val = output_path / 'labels/val'
    
    for p in [images_train, images_val, labels_train, labels_val]:
        p.mkdir(parents=True, exist_ok=True)
        
    class_folders = [d for d in source_path.iterdir() if d.is_dir()]
    classes = sorted([d.name for d in class_folders])
    
    print(f"Found {len(classes)} classes: {classes}")
    
    # Save classes.txt
    with open(output_path / 'classes.txt', 'w') as f:
        for i, c in enumerate(classes):
            f.write(f"{i}: {c}\n")

    for class_id, class_dir in enumerate(class_folders):
        print(f"Processing {class_dir.name}...")
        images = get_image_files(class_dir)
        random.shuffle(images)
        
        split_idx = int(len(images) * split_ratio)
        train_imgs = images[:split_idx]
        val_imgs = images[split_idx:]
        
        # Helper to process file
        def process_files(file_list, img_dest, lbl_dest):
            for img_path in file_list:
                # Copy image
                shutil.copy(img_path, img_dest / img_path.name)
                
                # Create Label File (ClassID, CenterX, CenterY, Width, Height)
                # We assume the object covers the main part of the image
                # Box: Center at 0.5, 0.5, with width/height 0.9 (90% of image)
                label_file = lbl_dest / f"{img_path.stem}.txt"
                with open(label_file, 'w') as lf:
                    lf.write(f"{class_id} 0.5 0.5 0.9 0.9\n")

        process_files(train_imgs, images_train, labels_train)
        process_files(val_imgs, images_val, labels_val)

    print(f"Conversion Complete. Dataset ready at {output_dir}")
    print("Update your dlcpd_dataset.yaml 'names' section with the classes printed above.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Path to raw DLCPD-25 folders")
    parser.add_argument("--output", default="dataset/dlcpd_formatted", help="Output path")
    args = parser.parse_args()
    
    convert_to_yolo_detection(args.source, args.output)
