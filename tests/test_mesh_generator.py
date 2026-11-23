"""
Unit tests for 3D mesh building, texture atlas generation, and GLB export.
"""

import os
import tempfile
import pytest
from PIL import Image

import sys
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from backend.app.services.mesh_generator_service import (
    generate_retro_texture_atlas,
    build_ps1_humanoid_mesh,
    export_character_glb
)


def test_texture_atlas_generation():
    with tempfile.TemporaryDirectory() as tmpdir:
        src_path = os.path.join(tmpdir, "src.jpg")
        img = Image.new("RGB", (300, 300), color=(180, 140, 110))
        img.save(src_path)

        out_tex = os.path.join(tmpdir, "atlas.png")
        generate_retro_texture_atlas(
            source_img_path=src_path,
            output_texture_path=out_tex,
            texture_size=128,
            outfit="police",
            gender="male"
        )
        assert os.path.exists(out_tex)
        with Image.open(out_tex) as atlas_img:
            assert atlas_img.size == (128, 128)


def test_mesh_generation_and_export():
    with tempfile.TemporaryDirectory() as tmpdir:
        glb_path = os.path.join(tmpdir, "test_char.glb")
        mesh = build_ps1_humanoid_mesh(
            gender="female",
            outfit="formal",
            pose="standing"
        )
        assert mesh.vertices.shape[0] > 0
        assert mesh.faces.shape[0] > 0

        export_character_glb(mesh, glb_path)
        assert os.path.exists(glb_path)
        assert os.path.getsize(glb_path) > 1000  # Valid GLB is several KB
