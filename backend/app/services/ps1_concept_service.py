"""
PS1 2D Concept Generation Service for RetroMorph AI.
Transforms an uploaded photo into a PlayStation 1-era low-poly character concept.
Supports both native CV/pixel-art polygonal rendering and external generative AI endpoints.
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from typing import Optional, Dict, Any, Tuple


# PS1 Retro Color Palettes
OUTFIT_PALETTES = {
    "casual": {
        "primary": (52, 98, 145),      # Faded denim blue
        "secondary": (220, 215, 205),  # Vintage off-white t-shirt
        "accent": (160, 80, 50),       # Brown leather sneakers/belt
        "style_desc": "Street Casual (Faded Denim & Vintage Tee)",
    },
    "formal": {
        "primary": (30, 32, 42),       # Dark charcoal suit
        "secondary": (245, 245, 250),  # Crisp dress shirt
        "accent": (150, 25, 35),       # Crimson tie
        "style_desc": "Corporate / Noir Formal Suit",
    },
    "police": {
        "primary": (28, 45, 80),       # Metro RPD Navy
        "secondary": (210, 195, 110),  # Brass badge & buckle
        "accent": (20, 20, 25),        # Tactical gear / utility belt
        "style_desc": "R.P.D. Tactical Patrol Officer",
    },
    "horror": {
        "primary": (65, 55, 45),       # Weathered trench coat
        "secondary": (115, 30, 30),    # Dried rust / bloodstains
        "accent": (175, 165, 150),     # Bandaged tattered wrap
        "style_desc": "Survival Horror Distressed Survivor",
    },
    "traditional": {
        "primary": (170, 35, 45),      # Crimson silk
        "secondary": (230, 200, 100),  # Gold thread embroidery
        "accent": (35, 35, 40),        # Obsidian sash
        "style_desc": "Ceremonial Martial Robes",
    },
    "custom": {
        "primary": (80, 70, 120),      # Custom violet-slate
        "secondary": (200, 210, 220),  # Custom highlight
        "accent": (230, 150, 40),      # Custom accent
        "style_desc": "Custom Spec Outfit",
    }
}


def apply_ordered_dither(img: Image.Image, palette_colors: int = 16) -> Image.Image:
    """
    Applies classic PS1/retro 4x4 Bayer matrix ordered dithering.
    """
    bayer_matrix = np.array([
        [ 0,  8,  2, 10],
        [12,  4, 14,  6],
        [ 3, 11,  1,  9],
        [15,  7, 13,  5]
    ], dtype=np.float32) / 16.0 - 0.5

    arr = np.array(img, dtype=np.float32)
    h, w, c = arr.shape
    tiled_bayer = np.tile(bayer_matrix, (int(np.ceil(h / 4)), int(np.ceil(w / 4))))[:h, :w]
    tiled_bayer = np.repeat(tiled_bayer[:, :, np.newaxis], c, axis=2)

    # Add dither noise before quantization
    step = 256.0 / palette_colors
    arr = arr + (tiled_bayer * step * 0.8)
    arr = np.clip(np.round(arr / step) * step, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def extract_dominant_tones(img_bgr: np.ndarray) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
    """
    Estimates dominant skin tone and hair/accent color from facial region.
    """
    h, w = img_bgr.shape[:2]
    # Sample center-upper quadrant (face area)
    face_sample = img_bgr[int(h * 0.2):int(h * 0.5), int(w * 0.3):int(w * 0.7)]
    if face_sample.size == 0:
        return (215, 175, 145), (45, 35, 30)

    # Average skin tone
    avg_bgr = np.median(face_sample, axis=(0, 1))
    skin_rgb = (int(avg_bgr[2]), int(avg_bgr[1]), int(avg_bgr[0]))

    # Top of head for hair
    hair_sample = img_bgr[int(h * 0.1):int(h * 0.25), int(w * 0.35):int(w * 0.65)]
    if hair_sample.size > 0:
        hair_bgr = np.percentile(hair_sample, 25, axis=(0, 1))
        hair_rgb = (int(hair_bgr[2]), int(hair_bgr[1]), int(hair_bgr[0]))
    else:
        hair_rgb = (40, 30, 25)

    return skin_rgb, hair_rgb


def render_ps1_polygonal_character(
    source_image: Image.Image,
    gender: str = "male",
    outfit: str = "casual",
    custom_outfit: Optional[str] = None
) -> Image.Image:
    """
    Renders an authentic PS1-style low-poly character concept with flat-shaded facets,
    limited color depth, and retro HUD overlay.
    """
    canvas_w, canvas_h = 480, 640
    canvas = Image.new("RGB", (canvas_w, canvas_h), (18, 16, 24))
    draw = ImageDraw.Draw(canvas)

    # Background: PS1-era low-poly gradient & retro grid
    for y in range(0, canvas_h, 8):
        v = int(25 + (y / canvas_h) * 20)
        draw.rectangle([0, y, canvas_w, y + 8], fill=(v - 5, v - 3, v + 8))

    # Perspective floor grid
    horizon_y = int(canvas_h * 0.65)
    for x in range(-200, canvas_w + 300, 60):
        draw.line([(canvas_w // 2, horizon_y), (x, canvas_h)], fill=(45, 45, 65), width=2)
    for y in range(horizon_y, canvas_h, 25):
        draw.line([(0, y), (canvas_w, y)], fill=(40, 42, 60), width=1)

    # Extract source photo tones
    src_cv = cv2.cvtColor(np.array(source_image), cv2.COLOR_RGB2BGR)
    skin_rgb, hair_rgb = extract_dominant_tones(src_cv)

    palette = OUTFIT_PALETTES.get(outfit.lower(), OUTFIT_PALETTES["casual"])
    primary_col = palette["primary"]
    secondary_col = palette["secondary"]
    accent_col = palette["accent"]

    # Proportions based on gender
    cx = canvas_w // 2
    if gender.lower() == "female":
        shoulder_w = 110
        hip_w = 95
        head_w = 46
        head_h = 60
    elif gender.lower() == "male":
        shoulder_w = 140
        hip_w = 85
        head_w = 52
        head_h = 64
    else:
        shoulder_w = 125
        hip_w = 90
        head_w = 50
        head_h = 62

    # Draw Low-Poly Character Mesh Facets (Triangles & Quads for PS1 look)
    neck_y = 190
    chest_y = 260
    waist_y = 330
    crotch_y = 390
    knee_y = 490
    feet_y = 570

    def draw_poly(points, fill_rgb, wireframe=(40, 40, 40)):
        draw.polygon(points, fill=fill_rgb, outline=wireframe)

    def shade(rgb, factor):
        return tuple(int(np.clip(c * factor, 0, 255)) for c in rgb)

    # 1. Legs / Pants (Low Poly Quads)
    left_hip = (cx - hip_w // 2, waist_y)
    right_hip = (cx + hip_w // 2, waist_y)
    crotch = (cx, crotch_y)
    left_knee = (cx - hip_w // 2 - 5, knee_y)
    right_knee = (cx + hip_w // 2 + 5, knee_y)
    left_foot = (cx - hip_w // 2 - 10, feet_y)
    right_foot = (cx + hip_w // 2 + 10, feet_y)

    pant_col = primary_col if outfit != "casual" else (40, 60, 95)
    # Left Leg facets
    draw_poly([left_hip, (cx - 5, crotch_y - 20), left_knee], shade(pant_col, 0.75))
    draw_poly([left_knee, (cx - 5, crotch_y - 20), (cx - 15, knee_y + 10)], shade(pant_col, 0.65))
    draw_poly([left_knee, left_foot, (cx - 8, feet_y), (cx - 15, knee_y + 10)], shade(pant_col, 0.7))

    # Right Leg facets
    draw_poly([right_hip, (cx + 5, crotch_y - 20), right_knee], shade(pant_col, 0.95))
    draw_poly([right_knee, (cx + 5, crotch_y - 20), (cx + 15, knee_y + 10)], shade(pant_col, 0.85))
    draw_poly([right_knee, right_foot, (cx + 8, feet_y), (cx + 15, knee_y + 10)], shade(pant_col, 0.9))

    # Shoes (Retro Chunky Boots)
    boot_col = (25, 25, 30) if outfit != "casual" else accent_col
    draw_poly([left_foot, (left_foot[0] - 15, feet_y + 15), (left_foot[0] + 15, feet_y + 15), (cx - 8, feet_y)], shade(boot_col, 0.7))
    draw_poly([right_foot, (right_foot[0] - 15, feet_y + 15), (right_foot[0] + 15, feet_y + 15), (cx + 8, feet_y)], shade(boot_col, 0.9))

    # 2. Torso & Outfit Facets
    left_shoulder = (cx - shoulder_w // 2, neck_y + 15)
    right_shoulder = (cx + shoulder_w // 2, neck_y + 15)
    neck_base = (cx, neck_y)

    # Chest front plates
    draw_poly([neck_base, left_shoulder, (cx - 20, chest_y), (cx, chest_y)], shade(primary_col, 0.8))
    draw_poly([neck_base, right_shoulder, (cx + 20, chest_y), (cx, chest_y)], shade(primary_col, 1.05))
    draw_poly([(cx - 20, chest_y), (cx, chest_y), (cx, waist_y), left_hip], shade(secondary_col if outfit == "formal" else primary_col, 0.75))
    draw_poly([(cx + 20, chest_y), (cx, chest_y), (cx, waist_y), right_hip], shade(secondary_col if outfit == "formal" else primary_col, 0.95))

    # Outfit specifics (tie / badge / details)
    if outfit == "formal":
        # Crimson tie
        draw_poly([neck_base, (cx - 6, neck_y + 15), (cx, waist_y - 20), (cx + 6, neck_y + 15)], accent_col)
    elif outfit == "police":
        # Badge
        draw_poly([(cx + 25, neck_y + 35), (cx + 38, neck_y + 30), (cx + 42, neck_y + 45), (cx + 28, neck_y + 48)], (225, 200, 60))
        # RPD shoulder patches
        draw_poly([(left_shoulder[0] + 5, left_shoulder[1] + 10), (left_shoulder[0] + 20, left_shoulder[1] + 15), (left_shoulder[0] + 15, left_shoulder[1] + 30)], (200, 50, 50))
    elif outfit == "horror":
        # Bandage / tear marks
        draw_line_coords = [(cx - 15, chest_y - 20), (cx + 25, chest_y + 10)]
        draw.line(draw_line_coords, fill=accent_col, width=4)

    # 3. Arms (Low Poly faceted segments)
    left_elbow = (cx - shoulder_w // 2 - 25, chest_y + 30)
    left_hand = (cx - shoulder_w // 2 - 15, waist_y + 40)
    right_elbow = (cx + shoulder_w // 2 + 25, chest_y + 30)
    right_hand = (cx + shoulder_w // 2 + 15, waist_y + 40)

    draw_poly([left_shoulder, (left_shoulder[0] - 10, neck_y + 30), left_elbow], shade(primary_col, 0.7))
    draw_poly([left_elbow, (left_elbow[0] + 12, left_elbow[1] + 10), left_hand], shade(skin_rgb if outfit == "casual" else primary_col, 0.75))
    draw_poly([right_shoulder, (right_shoulder[0] + 10, neck_y + 30), right_elbow], shade(primary_col, 1.0))
    draw_poly([right_elbow, (right_elbow[0] - 12, right_elbow[1] + 10), right_hand], shade(skin_rgb if outfit == "casual" else primary_col, 0.95))

    # Hands
    draw_poly([left_hand, (left_hand[0] - 8, left_hand[1] + 15), (left_hand[0] + 8, left_hand[1] + 15)], skin_rgb)
    draw_poly([right_hand, (right_hand[0] - 8, right_hand[1] + 15), (right_hand[0] + 8, right_hand[1] + 15)], skin_rgb)

    # 4. Neck & Head (Faceted Geometry)
    draw_poly([(cx - 14, neck_y), (cx + 14, neck_y), (cx + 10, neck_y - 25), (cx - 10, neck_y - 25)], shade(skin_rgb, 0.8))

    # Head facets
    chin = (cx, neck_y - 22)
    left_jaw = (cx - head_w // 2, neck_y - 45)
    right_jaw = (cx + head_w // 2, neck_y - 45)
    left_temple = (cx - head_w // 2 + 3, neck_y - 85)
    right_temple = (cx + head_w // 2 - 3, neck_y - 85)
    forehead = (cx, neck_y - 95)
    nose = (cx, neck_y - 52)

    # Lower face
    draw_poly([chin, left_jaw, nose], shade(skin_rgb, 0.8))
    draw_poly([chin, right_jaw, nose], shade(skin_rgb, 1.05))
    # Mid face
    draw_poly([nose, left_jaw, left_temple], shade(skin_rgb, 0.85))
    draw_poly([nose, right_jaw, right_temple], shade(skin_rgb, 1.0))
    # Forehead
    draw_poly([nose, left_temple, forehead], shade(skin_rgb, 0.9))
    draw_poly([nose, right_temple, forehead], shade(skin_rgb, 1.1))

    # Hair (Retro faceted crown)
    hair_top = (cx, neck_y - 110)
    draw_poly([forehead, (cx - head_w // 2 - 6, neck_y - 88), (cx - head_w // 2 - 2, neck_y - 108), hair_top], shade(hair_rgb, 0.8))
    draw_poly([forehead, (cx + head_w // 2 + 6, neck_y - 88), (cx + head_w // 2 + 2, neck_y - 108), hair_top], shade(hair_rgb, 1.1))

    # Police peaked cap if outfit is police
    if outfit == "police":
        cap_visor = (cx, neck_y - 80)
        draw_poly([forehead, (cx - head_w // 2 - 8, neck_y - 86), cap_visor, (cx + head_w // 2 + 8, neck_y - 86)], (15, 15, 20))
        draw_poly([(cx - head_w // 2 - 5, neck_y - 92), (cx + head_w // 2 + 5, neck_y - 92), (cx + 28, neck_y - 118), (cx - 28, neck_y - 118)], (25, 40, 75))
        # Cap badge
        draw_poly([(cx - 6, neck_y - 98), (cx + 6, neck_y - 98), (cx, neck_y - 108)], (230, 205, 50))

    # Apply authentic downsampling and retro dithering
    # Downsample to 240x320 PS1 VRAM resolution, then dither, then scale up
    low_res = canvas.resize((240, 320), Image.BILINEAR)
    dithered = apply_ordered_dither(low_res, palette_colors=24)
    final_canvas = dithered.resize((canvas_w, canvas_h), Image.NEAREST)

    # Add PS1 HUD Overlay & Metadata Frame
    hud_draw = ImageDraw.Draw(final_canvas)
    
    # CRT Scanline effect (subtle)
    for y in range(0, canvas_h, 3):
        hud_draw.line([(0, y), (canvas_w, y)], fill=(0, 0, 0, 45))

    # Bottom status card
    hud_draw.rectangle([15, canvas_h - 65, canvas_w - 15, canvas_h - 15], fill=(12, 14, 20), outline=(80, 100, 140), width=2)
    hud_draw.text((25, canvas_h - 58), f"RETROMORPH PS1 ASSET // {gender.upper()}", fill=(100, 210, 255))
    hud_draw.text((25, canvas_h - 40), f"STYLE: {palette['style_desc']}", fill=(200, 210, 220))
    hud_draw.text((canvas_w - 115, canvas_h - 50), "32-BIT VRAM", fill=(140, 160, 180))

    # Inset source photo thumbnail in top right corner
    try:
        thumb = source_image.copy()
        thumb.thumbnail((70, 70), Image.LANCZOS)
        thumb_low = thumb.resize((48, 48), Image.BILINEAR).resize((64, 64), Image.NEAREST)
        final_canvas.paste(thumb_low, (canvas_w - 82, 18))
        hud_draw.rectangle([canvas_w - 84, 16, canvas_w - 16, 84], outline=(80, 120, 160), width=2)
        hud_draw.text((canvas_w - 82, 88), "INPUT REF", fill=(130, 150, 170))
    except Exception:
        pass

    return final_canvas


def generate_ps1_concept_art(
    image_path: str,
    output_path: str,
    gender: str = "male",
    outfit: str = "casual",
    custom_outfit: Optional[str] = None
) -> str:
    """
    Main entry point for generating PS1 2D concept image.
    """
    source_img = Image.open(image_path).convert("RGB")
    concept_img = render_ps1_polygonal_character(
        source_image=source_img,
        gender=gender,
        outfit=outfit,
        custom_outfit=custom_outfit
    )

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    concept_img.save(output_path, format="PNG")
    return output_path
