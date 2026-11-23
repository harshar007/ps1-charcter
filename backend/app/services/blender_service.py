"""
Blender Integration Service for RetroMorph AI.
Manages headless execution of Blender optimization pipelines.
"""

import os
import subprocess
import shutil
from typing import Optional


DEFAULT_BLENDER_PATHS = [
    r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
    r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
]


def find_blender_binary() -> Optional[str]:
    """Finds path to blender.exe on the host system."""
    which_blender = shutil.which("blender")
    if which_blender:
        return which_blender

    for path in DEFAULT_BLENDER_PATHS:
        if os.path.exists(path):
            return path

    return None


def run_blender_optimization(
    input_model_path: str,
    output_glb_path: str,
    polygon_level: str = "medium",
    texture_path: Optional[str] = None,
    texture_size: int = 128,
    enable_affine_jitter: bool = False
) -> bool:
    """
    Executes blender/optimize_and_export.py via Blender CLI.
    """
    blender_bin = find_blender_binary()
    if not blender_bin:
        print("[Blender Service] Blender executable not found. Falling back to native trimesh pipeline.")
        return False

    script_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "blender", "optimize_and_export.py"
    ))

    if not os.path.exists(script_path):
        print(f"[Blender Service] Script not found: {script_path}")
        return False

    cmd = [
        blender_bin,
        "-b",  # background / headless
        "-P", script_path,
        "--",
        "--input", os.path.abspath(input_model_path),
        "--output", os.path.abspath(output_glb_path),
        "--poly-target", polygon_level.lower(),
        "--texture-size", str(texture_size),
    ]

    if texture_path and os.path.exists(texture_path):
        cmd.extend(["--texture", os.path.abspath(texture_path)])

    if enable_affine_jitter:
        cmd.append("--affine-jitter")

    print(f"[Blender Service] Running command: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=120
        )
        if result.returncode == 0 and os.path.exists(output_glb_path):
            print(f"[Blender Service] Blender optimization succeeded! Output: {output_glb_path}")
            return True
        else:
            print(f"[Blender Service] Blender process exited with code {result.returncode}")
            print(f"[Blender Service] STDERR: {result.stderr[-500:]}")
            return False
    except Exception as e:
        print(f"[Blender Service] Execution failed: {e}")
        return False
