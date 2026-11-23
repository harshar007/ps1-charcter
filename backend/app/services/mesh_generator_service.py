"""
3D Mesh Generation Service for RetroMorph AI.
Constructs authentic PS1-era low-poly humanoid geometry, generates retro UV texture maps,
and exports game-ready GLB assets using trimesh & pygltflib.
"""

import os
import cv2
import numpy as np
import trimesh
from PIL import Image, ImageDraw
from typing import Tuple, Dict, Any, Optional

from .ps1_concept_service import OUTFIT_PALETTES, extract_dominant_tones


def generate_retro_texture_atlas(
    source_img_path: str,
    output_texture_path: str,
    texture_size: int = 128,
    outfit: str = "casual",
    gender: str = "male"
) -> str:
    """
    Synthesizes a low-resolution retro UV texture atlas (64x64, 128x128, or 256x256)
    mapping facial features, skin, and clothing.
    """
    atlas = Image.new("RGB", (texture_size, texture_size), (30, 30, 35))
    draw = ImageDraw.Draw(atlas)

    src_cv = cv2.imread(source_img_path)
    if src_cv is not None:
        skin_rgb, hair_rgb = extract_dominant_tones(src_cv)
    else:
        skin_rgb, hair_rgb = (210, 175, 140), (45, 35, 30)

    palette = OUTFIT_PALETTES.get(outfit.lower(), OUTFIT_PALETTES["casual"])
    primary_col = palette["primary"]
    secondary_col = palette["secondary"]
    accent_col = palette["accent"]

    # Region 1: Face & Skin (Top Left quadrant: [0, 0] to [0.5, 0.5])
    face_w = texture_size // 2
    face_h = texture_size // 2
    draw.rectangle([0, 0, face_w, face_h], fill=skin_rgb)
    # Add subtle PS1 face details (eyes, nose shade, mouth)
    eye_y = int(face_h * 0.45)
    eye_lx = int(face_w * 0.3)
    eye_rx = int(face_w * 0.7)
    draw.rectangle([eye_lx - 2, eye_y - 1, eye_lx + 2, eye_y + 1], fill=(25, 25, 25))
    draw.rectangle([eye_rx - 2, eye_y - 1, eye_rx + 2, eye_y + 1], fill=(25, 25, 25))
    # Mouth
    mouth_y = int(face_h * 0.75)
    draw.rectangle([int(face_w * 0.35), mouth_y, int(face_w * 0.65), mouth_y + 1], fill=(120, 50, 50))

    # Region 2: Hair & Accessories (Top Right quadrant: [0.5, 0] to [1.0, 0.5])
    draw.rectangle([face_w, 0, texture_size, face_h], fill=hair_rgb)
    if outfit == "police":
        # Badge on police cap
        draw.rectangle([face_w + 10, 10, face_w + 30, 25], fill=(225, 200, 50))

    # Region 3: Torso & Outfit Fabric (Bottom Left quadrant: [0, 0.5] to [0.5, 1.0])
    draw.rectangle([0, face_h, face_w, texture_size], fill=primary_col)
    if outfit == "formal":
        # Tie & shirt stripes
        draw.rectangle([int(face_w * 0.4), face_h, int(face_w * 0.6), texture_size], fill=secondary_col)
        draw.rectangle([int(face_w * 0.46), face_h, int(face_w * 0.54), texture_size], fill=accent_col)
    elif outfit == "police":
        # Utility belt line & badge
        draw.rectangle([0, texture_size - int(face_h * 0.25), face_w, texture_size], fill=(20, 20, 25))
        draw.rectangle([int(face_w * 0.4), face_h + 10, int(face_w * 0.6), face_h + 25], fill=(220, 195, 60))
    elif outfit == "horror":
        # Blood splatter / distress stains
        draw.rectangle([int(face_w * 0.2), face_h + 10, int(face_w * 0.4), face_h + 30], fill=secondary_col)

    # Region 4: Pants & Boots (Bottom Right quadrant: [0.5, 0.5] to [1.0, 1.0])
    pant_col = (45, 65, 100) if outfit == "casual" else primary_col
    draw.rectangle([face_w, face_h, texture_size, texture_size], fill=pant_col)
    # Boot bottoms
    draw.rectangle([face_w, texture_size - int(face_h * 0.3), texture_size, texture_size], fill=(25, 25, 30))

    # Downsample to exact requested texture size (64, 128, 256)
    atlas = atlas.resize((texture_size, texture_size), Image.NEAREST)

    os.makedirs(os.path.dirname(os.path.abspath(output_texture_path)), exist_ok=True)
    atlas.save(output_texture_path, format="PNG")
    return output_texture_path


def create_cube_mesh(
    center: Tuple[float, float, float],
    size: Tuple[float, float, float],
    uv_bounds: Tuple[float, float, float, float] = (0, 0, 1, 1)
) -> trimesh.Trimesh:
    """
    Creates a low-poly faceted 3D box (12 triangles) with explicit UV mapping.
    """
    cx, cy, cz = center
    sx, sy, sz = size[0] / 2.0, size[1] / 2.0, size[2] / 2.0

    vertices = np.array([
        [cx - sx, cy - sy, cz - sz],  # 0
        [cx + sx, cy - sy, cz - sz],  # 1
        [cx + sx, cy + sy, cz - sz],  # 2
        [cx - sx, cy + sy, cz - sz],  # 3
        [cx - sx, cy - sy, cz + sz],  # 4
        [cx + sx, cy - sy, cz + sz],  # 5
        [cx + sx, cy + sy, cz + sz],  # 6
        [cx - sx, cy + sy, cz + sz],  # 7
    ], dtype=np.float32)

    # 12 triangles (2 per cube face)
    faces = np.array([
        [0, 2, 1], [0, 3, 2],  # Back
        [4, 5, 6], [4, 6, 7],  # Front
        [0, 1, 5], [0, 5, 4],  # Bottom
        [3, 6, 2], [3, 7, 6],  # Top
        [0, 4, 7], [0, 7, 3],  # Left
        [1, 2, 6], [1, 6, 5],  # Right
    ], dtype=np.int32)

    # Simple planar UV mapping into uv_bounds: (u_min, v_min, u_max, v_max)
    u0, v0, u1, v1 = uv_bounds
    uvs = np.array([
        [u0, v0], [u1, v0], [u1, v1], [u0, v1],
        [u0, v0], [u1, v0], [u1, v1], [u0, v1]
    ], dtype=np.float32)

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    mesh.visual = trimesh.visual.TextureVisuals(uv=uvs)
    return mesh


def build_ps1_humanoid_mesh(
    gender: str = "male",
    outfit: str = "casual",
    pose: str = "standing",
    texture_path: str = None
) -> trimesh.Trimesh:
    """
    Constructs an authentic PS1 segmented low-poly character mesh (similar to FF7 / Resident Evil 1 / MGS1).
    """
    # Proportions
    if gender.lower() == "female":
        shoulder_w = 0.42
        hip_w = 0.34
        torso_w = 0.32
        head_sz = (0.24, 0.28, 0.24)
        arm_spread = 0.35 if pose == "t_pose" else 0.08
    else:  # male / default
        shoulder_w = 0.52
        hip_w = 0.32
        torso_w = 0.38
        head_sz = (0.26, 0.30, 0.26)
        arm_spread = 0.40 if pose == "t_pose" else 0.10

    parts = []

    # UV Atlas quadrants:
    # Face:  (0.0, 0.5, 0.5, 1.0)
    # Hair:  (0.5, 0.5, 1.0, 1.0)
    # Torso: (0.0, 0.0, 0.5, 0.5)
    # Pants: (0.5, 0.0, 1.0, 0.5)

    # 1. Head
    head_y = 1.62
    head = create_cube_mesh(
        center=(0.0, head_y, 0.0),
        size=head_sz,
        uv_bounds=(0.0, 0.5, 0.5, 1.0)
    )
    parts.append(head)

    # Hair / Cap topper
    hair = create_cube_mesh(
        center=(0.0, head_y + 0.14, 0.0),
        size=(head_sz[0] * 1.08, 0.10, head_sz[2] * 1.08),
        uv_bounds=(0.5, 0.5, 1.0, 1.0)
    )
    parts.append(hair)

    # 2. Neck
    neck = create_cube_mesh(
        center=(0.0, 1.45, 0.0),
        size=(0.14, 0.10, 0.14),
        uv_bounds=(0.0, 0.5, 0.2, 0.7)
    )
    parts.append(neck)

    # 3. Torso (Chest + Abdomen)
    chest_y = 1.28
    chest = create_cube_mesh(
        center=(0.0, chest_y, 0.0),
        size=(shoulder_w, 0.26, 0.24),
        uv_bounds=(0.0, 0.0, 0.5, 0.5)
    )
    parts.append(chest)

    abdomen = create_cube_mesh(
        center=(0.0, 1.06, 0.0),
        size=(torso_w, 0.20, 0.22),
        uv_bounds=(0.0, 0.0, 0.5, 0.5)
    )
    parts.append(abdomen)

    # 4. Pelvis / Hips
    pelvis_y = 0.90
    pelvis = create_cube_mesh(
        center=(0.0, pelvis_y, 0.0),
        size=(hip_w, 0.16, 0.22),
        uv_bounds=(0.5, 0.0, 1.0, 0.5)
    )
    parts.append(pelvis)

    # 5. Legs & Feet
    leg_x = hip_w * 0.28
    upper_leg_len = 0.38
    lower_leg_len = 0.40

    for side in [-1, 1]:
        # Upper Leg (Thigh)
        thigh_y = pelvis_y - 0.22
        thigh = create_cube_mesh(
            center=(side * leg_x, thigh_y, 0.0),
            size=(0.15, upper_leg_len, 0.16),
            uv_bounds=(0.5, 0.0, 1.0, 0.5)
        )
        parts.append(thigh)

        # Lower Leg (Calf)
        calf_y = thigh_y - upper_leg_len
        calf = create_cube_mesh(
            center=(side * leg_x, calf_y, 0.0),
            size=(0.14, lower_leg_len, 0.15),
            uv_bounds=(0.5, 0.0, 1.0, 0.5)
        )
        parts.append(calf)

        # Foot (Boot)
        boot_y = calf_y - lower_leg_len / 2.0 - 0.05
        boot = create_cube_mesh(
            center=(side * leg_x, boot_y, 0.05),
            size=(0.15, 0.10, 0.26),
            uv_bounds=(0.5, 0.0, 0.9, 0.3)
        )
        parts.append(boot)

    # 6. Arms & Hands
    arm_x = shoulder_w / 2.0 + 0.09
    upper_arm_len = 0.30
    lower_arm_len = 0.28

    if pose == "t_pose":
        # T-Pose (horizontal arms along X)
        for side in [-1, 1]:
            # Upper Arm
            u_arm = create_cube_mesh(
                center=(side * (shoulder_w / 2.0 + upper_arm_len / 2.0), chest_y + 0.05, 0.0),
                size=(upper_arm_len, 0.14, 0.14),
                uv_bounds=(0.0, 0.0, 0.5, 0.5)
            )
            parts.append(u_arm)
            # Forearm
            f_arm = create_cube_mesh(
                center=(side * (shoulder_w / 2.0 + upper_arm_len + lower_arm_len / 2.0), chest_y + 0.05, 0.0),
                size=(lower_arm_len, 0.12, 0.12),
                uv_bounds=(0.0, 0.5, 0.3, 0.8)
            )
            parts.append(f_arm)
            # Hand
            hand = create_cube_mesh(
                center=(side * (shoulder_w / 2.0 + upper_arm_len + lower_arm_len + 0.06), chest_y + 0.05, 0.0),
                size=(0.10, 0.10, 0.10),
                uv_bounds=(0.0, 0.5, 0.2, 0.7)
            )
            parts.append(hand)
    else:
        # Standing Pose (arms relaxed at sides)
        for side in [-1, 1]:
            u_arm_y = chest_y - 0.10
            u_arm = create_cube_mesh(
                center=(side * arm_x, u_arm_y, 0.0),
                size=(0.13, upper_arm_len, 0.13),
                uv_bounds=(0.0, 0.0, 0.5, 0.5)
            )
            parts.append(u_arm)

            f_arm_y = u_arm_y - upper_arm_len
            f_arm = create_cube_mesh(
                center=(side * arm_x, f_arm_y, 0.02),
                size=(0.12, lower_arm_len, 0.12),
                uv_bounds=(0.0, 0.5, 0.3, 0.8)
            )
            parts.append(f_arm)

            hand_y = f_arm_y - lower_arm_len / 2.0 - 0.05
            hand = create_cube_mesh(
                center=(side * arm_x, hand_y, 0.03),
                size=(0.10, 0.10, 0.10),
                uv_bounds=(0.0, 0.5, 0.2, 0.7)
            )
            parts.append(hand)

    # Merge parts into single combined mesh
    combined = trimesh.util.concatenate(parts)

    # Attach texture visual
    if texture_path and os.path.exists(texture_path):
        tex_pil = Image.open(texture_path).convert("RGB")
        material = trimesh.visual.material.PBRMaterial(
            baseColorTexture=tex_pil,
            roughnessFactor=0.9,
            metallicFactor=0.0
        )
        combined.visual.material = material

    return combined


def export_character_glb(
    mesh: trimesh.Trimesh,
    output_path: str,
    texture_path: Optional[str] = None
) -> str:
    """
    Exports the combined trimesh to standard GLB format.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Export scene
    scene = trimesh.Scene(mesh)
    glb_data = scene.export(file_type="glb")
    
    with open(output_path, "wb") as f:
        f.write(glb_data)
        
    print(f"Exported character GLB to: {output_path} (size: {len(glb_data)} bytes)")
    return output_path
