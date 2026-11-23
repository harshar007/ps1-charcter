"""
Blender Python Automation Script for RetroMorph AI.
Performs PS1-style low-poly mesh optimization, decimation, retro material setup,
and GLB export.

Can be run via Blender headless:
  blender.exe -b -P blender/optimize_and_export.py -- --input input.obj --output output.glb --poly-target medium --texture-size 128 --affine-jitter
"""

import sys
import os
import argparse

# Check if running inside Blender
try:
    import bpy
    IN_BLENDER = True
except ImportError:
    IN_BLENDER = False


def setup_blender_scene():
    """Clear default scene objects."""
    bpy.ops.wm.read_factory_settings(use_empty=True)


def import_model(filepath: str):
    """Import OBJ, FBX, or GLTF/GLB model into Blender."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".obj":
        bpy.ops.wm.obj_import(filepath=filepath)
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=filepath)
    elif ext in [".gltf", ".glb"]:
        bpy.ops.import_scene.gltf(filepath=filepath)
    else:
        raise ValueError(f"Unsupported format: {ext}")


def get_all_meshes():
    """Retrieve all mesh objects in current scene."""
    return [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']


def apply_decimation(obj, target_ratio: float):
    """Apply decimate modifier to reduce polygon count to target ratio."""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    initial_faces = len(obj.data.polygons)
    mod = obj.modifiers.new(name="Decimate_Retro", type='DECIMATE')
    mod.ratio = max(0.05, min(1.0, target_ratio))
    bpy.ops.object.modifier_apply(modifier=mod.name)
    final_faces = len(obj.data.polygons)
    print(f"[Blender] Decimated {obj.name}: {initial_faces} -> {final_faces} faces (ratio: {target_ratio})")


def apply_flat_shading_and_retro_normals(obj):
    """Set flat shading for classic PS1 polygonal aesthetic."""
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_flat()
    # Disable auto smooth for sharp facet edges
    if hasattr(obj.data, "use_auto_smooth"):
        obj.data.use_auto_smooth = False


def apply_ps1_vertex_snapping(obj, grid_size: float = 0.015):
    """
    Quantizes vertex coordinates to simulate PS1 fixed-point coordinate jitter.
    """
    mesh = obj.data
    for v in mesh.vertices:
        v.co.x = round(v.co.x / grid_size) * grid_size
        v.co.y = round(v.co.y / grid_size) * grid_size
        v.co.z = round(v.co.z / grid_size) * grid_size
    mesh.update()
    print(f"[Blender] Applied PS1 vertex snapping (grid: {grid_size})")


def configure_retro_materials(obj, texture_path: str = None, texture_size: int = 128):
    """
    Sets up retro unlit / diffuse material with closest (nearest-neighbor) texture filtering.
    """
    if not obj.data.materials:
        mat = bpy.data.materials.new(name="PS1_Retro_Material")
        obj.data.materials.append(mat)
    else:
        mat = obj.data.materials[0]

    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear existing nodes
    nodes.clear()

    # Output node
    output_node = nodes.new(type="ShaderNodeOutputMaterial")
    output_node.location = (400, 0)

    # Principled BSDF with low roughness
    bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf.location = (100, 0)
    bsdf.inputs['Roughness'].default_value = 0.9
    bsdf.inputs['Specular IOR Level'].default_value = 0.05
    links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])

    # Image Texture node with closest filtering
    if texture_path and os.path.exists(texture_path):
        tex_image = bpy.data.images.load(texture_path)
        img_node = nodes.new(type="ShaderNodeTexImage")
        img_node.image = tex_image
        img_node.interpolation = 'Closest'  # Nearest neighbor for PS1 pixel art!
        img_node.location = (-250, 0)
        links.new(img_node.outputs['Color'], bsdf.inputs['Base Color'])


def export_glb(output_path: str):
    """Export scene to standard GLB."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',
        export_apply=True,
        export_yup=True
    )
    print(f"[Blender] Successfully exported GLB to: {output_path}")


def optimize_mesh_pipeline(
    input_file: str,
    output_file: str,
    polygon_level: str = "medium",
    texture_path: str = None,
    texture_size: int = 128,
    enable_affine_jitter: bool = False
):
    """Orchestrates full Blender optimization pipeline."""
    setup_blender_scene()
    print(f"[Blender] Importing {input_file}...")
    import_model(input_file)

    meshes = get_all_meshes()
    if not meshes:
        print("[Blender Error] No meshes found in imported scene.")
        return False

    ratio_map = {
        "low": 0.25,      # ~800 - 1200 triangles
        "medium": 0.50,   # ~2000 - 3000 triangles
        "high": 0.85      # ~4500 - 6000 triangles
    }
    ratio = ratio_map.get(polygon_level.lower(), 0.5)

    for mesh_obj in meshes:
        apply_decimation(mesh_obj, ratio)
        apply_flat_shading_and_retro_normals(mesh_obj)
        if enable_affine_jitter:
            apply_ps1_vertex_snapping(mesh_obj)
        configure_retro_materials(mesh_obj, texture_path=texture_path, texture_size=texture_size)

    export_glb(output_file)
    return True


if __name__ == "__main__":
    if not IN_BLENDER:
        print("This script is meant to be executed inside Blender:")
        print("  blender -b -P blender/optimize_and_export.py -- --input <in> --output <out>")
        sys.exit(0)

    # Parse arguments passed after '--'
    argv = sys.argv
    if "--" in argv:
        args_to_parse = argv[argv.index("--") + 1:]
    else:
        args_to_parse = []

    parser = argparse.ArgumentParser(description="RetroMorph Blender Optimizer")
    parser.add_argument("--input", required=True, help="Input model path")
    parser.add_argument("--output", required=True, help="Output GLB path")
    parser.add_argument("--poly-target", default="medium", choices=["low", "medium", "high"], help="Polygon target")
    parser.add_argument("--texture", default=None, help="Texture image path")
    parser.add_argument("--texture-size", type=int, default=128, help="Texture resolution (64/128/256)")
    parser.add_argument("--affine-jitter", action="store_true", help="Apply PS1 fixed-point vertex snapping")

    args = parser.parse_args(args_to_parse)

    optimize_mesh_pipeline(
        input_file=args.input,
        output_file=args.output,
        polygon_level=args.poly_target,
        texture_path=args.texture,
        texture_size=args.texture_size,
        enable_affine_jitter=args.affine_jitter
    )
