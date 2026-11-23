"""
Generates a representative pilot dataset of image quality samples with real synthetic images
and feature labels for training the RetroMorph AI Image Readiness Classifier.
"""

import os
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import pandas as pd
from features import extract_image_features, FEATURE_NAMES


def create_sample_image(
    category: str,
    width: int,
    height: int,
    blur_radius: float = 0.0,
    brightness_factor: float = 1.0,
    contrast_factor: float = 1.0,
    noise_level: float = 0.0,
    subject_type: str = "humanoid",
    center_offset: float = 0.0
) -> Image.Image:
    """
    Creates an illustrative synthetic test image simulating camera conditions.
    """
    # Create background with gradient or texture
    img_arr = np.zeros((height, width, 3), dtype=np.float32)
    
    # Background gradient
    top_color = np.array([random.uniform(50, 200) for _ in range(3)])
    bottom_color = np.array([random.uniform(30, 180) for _ in range(3)])
    for y in range(height):
        alpha = y / max(height - 1, 1)
        img_arr[y, :, :] = (1 - alpha) * top_color + alpha * bottom_color
        
    img = Image.fromarray(np.clip(img_arr, 0, 255).astype(np.uint8))
    draw = ImageDraw.Draw(img)

    cx = width * (0.5 + center_offset)
    cy = height * 0.5
    
    # Draw character silhouette / features
    if subject_type == "humanoid":
        head_radius = min(width, height) * 0.12
        body_w = min(width, height) * 0.25
        body_h = min(width, height) * 0.4
        
        # Head
        skin_tones = [
            (240, 200, 180), (220, 175, 140), (180, 130, 90), 
            (140, 90, 60), (90, 55, 35)
        ]
        skin = random.choice(skin_tones)
        hair = (random.randint(20, 70), random.randint(20, 50), random.randint(10, 40))
        shirt = (random.randint(30, 220), random.randint(30, 220), random.randint(30, 220))
        
        # Body / torso
        draw.rectangle([cx - body_w/2, cy - body_h/4, cx + body_w/2, cy + body_h], fill=shirt)
        # Head
        draw.ellipse([cx - head_radius, cy - body_h/4 - head_radius*1.6, cx + head_radius, cy - body_h/4 + head_radius*0.4], fill=skin)
        # Hair
        draw.chord([cx - head_radius*1.1, cy - body_h/4 - head_radius*1.8, cx + head_radius*1.1, cy - body_h/4 - head_radius*0.5], 180, 360, fill=hair)
        # Eyes
        eye_y = cy - body_h/4 - head_radius*0.7
        draw.ellipse([cx - head_radius*0.4 - 3, eye_y - 3, cx - head_radius*0.4 + 3, eye_y + 3], fill=(30, 30, 30))
        draw.ellipse([cx + head_radius*0.4 - 3, eye_y - 3, cx + head_radius*0.4 + 3, eye_y + 3], fill=(30, 30, 30))
    elif subject_type == "blank":
        # No subject, just flat or noisy background
        pass

    # Post-processing simulation: Blur
    if blur_radius > 0:
        img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        
    arr = np.array(img, dtype=np.float32)
    
    # Brightness and contrast
    arr = (arr - 128.0) * contrast_factor + 128.0
    arr = arr * brightness_factor
    
    # Noise
    if noise_level > 0:
        noise = np.random.normal(0, noise_level * 255.0, arr.shape)
        arr = arr + noise
        
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def generate_dataset(output_dir: str = "ml/data", num_samples: int = 400):
    """
    Generates a balanced pilot dataset with labelled examples for 'ready' and 'retake'.
    """
    os.makedirs(output_dir, exist_ok=True)
    samples_dir = os.path.join(output_dir, "samples")
    os.makedirs(samples_dir, exist_ok=True)

    records = []
    random.seed(42)
    np.random.seed(42)

    print(f"Generating {num_samples} image quality samples...")

    for i in range(num_samples):
        # 50% ready, 50% retake
        is_ready = (i % 2 == 0)
        
        if is_ready:
            label = "ready"
            width = random.choice([512, 640, 768, 800, 1024])
            height = random.choice([512, 640, 768, 800, 1024, 1280])
            blur_radius = random.uniform(0.0, 1.1)
            brightness = random.uniform(0.75, 1.25)
            contrast = random.uniform(0.85, 1.35)
            noise = random.uniform(0.0, 0.03)
            subject = "humanoid"
            center_offset = random.uniform(-0.08, 0.08)
            reason = "Optimal clarity, balanced lighting, centered subject"
        else:
            label = "retake"
            issue_type = random.choice(["blurry", "too_dark", "too_bright", "low_res", "off_center", "low_contrast"])
            
            if issue_type == "blurry":
                width = random.choice([512, 640, 800])
                height = random.choice([512, 640, 800])
                blur_radius = random.uniform(3.5, 9.0)
                brightness = random.uniform(0.8, 1.1)
                contrast = random.uniform(0.8, 1.2)
                noise = random.uniform(0.0, 0.05)
                subject = "humanoid"
                center_offset = random.uniform(-0.1, 0.1)
                reason = "Excessive motion/lens blur"
            elif issue_type == "too_dark":
                width = random.choice([512, 768, 1024])
                height = random.choice([512, 768, 1024])
                blur_radius = random.uniform(0.0, 1.5)
                brightness = random.uniform(0.12, 0.32)
                contrast = random.uniform(0.4, 0.7)
                noise = random.uniform(0.01, 0.08)
                subject = "humanoid"
                center_offset = random.uniform(-0.1, 0.1)
                reason = "Severe underexposure; person silhouette barely visible"
            elif issue_type == "too_bright":
                width = random.choice([512, 768, 1024])
                height = random.choice([512, 768, 1024])
                blur_radius = random.uniform(0.0, 1.2)
                brightness = random.uniform(1.8, 2.5)
                contrast = random.uniform(0.5, 0.8)
                noise = random.uniform(0.0, 0.02)
                subject = "humanoid"
                center_offset = random.uniform(-0.1, 0.1)
                reason = "Severe overexposure; washed out highlights"
            elif issue_type == "low_res":
                width = random.choice([120, 160, 200, 240])
                height = random.choice([120, 160, 200, 240])
                blur_radius = random.uniform(0.0, 0.5)
                brightness = random.uniform(0.8, 1.2)
                contrast = random.uniform(0.8, 1.2)
                noise = random.uniform(0.0, 0.02)
                subject = "humanoid"
                center_offset = random.uniform(-0.05, 0.05)
                reason = "Sub-minimum resolution for 3D reconstruction"
            elif issue_type == "low_contrast":
                width = random.choice([512, 640, 800])
                height = random.choice([512, 640, 800])
                blur_radius = random.uniform(0.5, 1.5)
                brightness = random.uniform(0.9, 1.1)
                contrast = random.uniform(0.15, 0.35)
                noise = random.uniform(0.0, 0.02)
                subject = "humanoid"
                center_offset = random.uniform(-0.1, 0.1)
                reason = "Flat, low-contrast lighting"
            else:  # off_center / blank
                width = random.choice([512, 768])
                height = random.choice([512, 768])
                blur_radius = random.uniform(0.0, 1.0)
                brightness = random.uniform(0.8, 1.1)
                contrast = random.uniform(0.8, 1.1)
                noise = random.uniform(0.0, 0.02)
                subject = "blank"
                center_offset = 0.0
                reason = "Subject missing or poorly framed"

        # Generate image
        img = create_sample_image(
            category=label,
            width=width,
            height=height,
            blur_radius=blur_radius,
            brightness_factor=brightness,
            contrast_factor=contrast,
            noise_level=noise,
            subject_type=subject,
            center_offset=center_offset
        )

        # Save representative sample images to disk (first 20 of each)
        filename = f"sample_{i:04d}_{label}.jpg"
        img_path = os.path.join(samples_dir, filename)
        if i < 40:
            img.save(img_path, quality=85)

        # Extract features
        features = extract_image_features(img)
        features["label"] = label
        features["reason"] = reason
        features["filename"] = filename
        records.append(features)

    df = pd.DataFrame(records)
    csv_path = os.path.join(output_dir, "dataset.csv")
    df.to_csv(csv_path, index=False)
    print(f"Dataset saved to {csv_path} with {len(df)} records.")
    print("Class distribution:")
    print(df["label"].value_counts())
    return df


if __name__ == "__main__":
    generate_dataset()
