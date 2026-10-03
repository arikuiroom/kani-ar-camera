import bpy
import os
from mathutils import Vector

ROOT = os.environ.get("GITHUB_WORKSPACE", os.getcwd())
SRC = os.path.join(ROOT, "build_src")
OUT = os.path.join(ROOT, "assets", "kani-guitar-red.usdz")
OUT_IDLE = os.path.join(ROOT, "assets", "kani-guitar-red-idle-test.usdz")
FBX = os.path.join(SRC, "CrabGuitarKA23_High.fbx")
ALBEDO = os.path.join(SRC, "KA23_Red_Albedo.png")
METALLIC = os.path.join(SRC, "KA23_Solid_Metallic.png")
ROUGHNESS = os.path.join(SRC, "KA23_Solid_Roughness.png")

TARGET_MAX_METERS = 0.80

bpy.ops.wm.read_factory_settings(use_empty=True)

# Import the same KA-23 mesh used by kani-camera.
bpy.ops.import_scene.fbx(filepath=FBX)

mesh_objects = [o for o in bpy.context.scene.objects if o.type == "MESH"]
if not mesh_objects:
    raise RuntimeError("No mesh objects were imported from FBX")

# One predictable PBR material, matching the web camera app's material policy.
mat = bpy.data.materials.new("KaniGuitar_PBR")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
for n in list(nodes):
    nodes.remove(n)

out = nodes.new("ShaderNodeOutputMaterial")
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

def image_node(path, non_color=False):
    node = nodes.new("ShaderNodeTexImage")
    node.image = bpy.data.images.load(path, check_existing=True)
    if non_color:
        node.image.colorspace_settings.name = "Non-Color"
    return node

albedo = image_node(ALBEDO, False)
metal = image_node(METALLIC, True)
rough = image_node(ROUGHNESS, True)

links.new(albedo.outputs["Color"], bsdf.inputs["Base Color"])
links.new(metal.outputs["Color"], bsdf.inputs["Metallic"])
links.new(rough.outputs["Color"], bsdf.inputs["Roughness"])

# Keep the metallic response slightly below 1, like the existing camera app.
bsdf.inputs["Metallic"].default_value = 0.92
bsdf.inputs["Roughness"].default_value = 1.0

for obj in mesh_objects:
    obj.data.materials.clear()
    obj.data.materials.append(mat)

# Parent imported top-level objects to one root so we can normalize size and floor contact.
root = bpy.data.objects.new("KaniGuitarRoot", None)
bpy.context.collection.objects.link(root)
top_level = [o for o in bpy.context.scene.objects if o != root and o.parent is None]
for obj in top_level:
    world = obj.matrix_world.copy()
    obj.parent = root
    obj.matrix_world = world

bpy.context.view_layer.update()

def world_bounds(objects):
    pts = []
    for obj in objects:
        for corner in obj.bound_box:
            pts.append(obj.matrix_world @ Vector(corner))
    mins = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    maxs = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mins, maxs

mins, maxs = world_bounds(mesh_objects)
size = maxs - mins
max_dim = max(size)
if max_dim <= 0:
    raise RuntimeError("Invalid imported model bounds")

scale = TARGET_MAX_METERS / max_dim
root.scale = (scale, scale, scale)
bpy.context.view_layer.update()

mins, maxs = world_bounds(mesh_objects)
center = (mins + maxs) * 0.5

# Center in X/Y and make the lowest point touch Blender's Z=0 floor.
root.location.x -= center.x
root.location.y -= center.y
root.location.z -= mins.z
bpy.context.view_layer.update()

mins2, maxs2 = world_bounds(mesh_objects)
print("Final bounds meters:", tuple(mins2), tuple(maxs2), "size:", tuple(maxs2 - mins2))

os.makedirs(os.path.dirname(OUT), exist_ok=True)

# Blender packages dependencies when the output extension is .usdz.
# Keep arguments conservative for Blender 4.0 compatibility.
result = bpy.ops.wm.usd_export(
    filepath=OUT,
    export_materials=True,
    export_uvmaps=True,
    export_normals=True,
    relative_paths=True,
)
print("USDZ export result:", result)
print("Wrote:", OUT, os.path.getsize(OUT), "bytes")

# ---------------------------------------------------------------------------
# Animation capability test
# Add a subtle 3-second root motion to the same Kani Guitar.
# This is NOT the final character motion. It only verifies that AR Quick Look
# preserves and plays animation exported from Blender/USDZ.
# ---------------------------------------------------------------------------
scene = bpy.context.scene
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 91

base_location = root.location.copy()
base_rotation = root.rotation_euler.copy()

poses = [
    (1,  0.000,  0.0,  0.0),
    (23, 0.010,  1.8, -1.2),
    (46, 0.020, -1.6,  1.4),
    (68, 0.010,  1.2,  0.8),
    (91, 0.000,  0.0,  0.0),
]

for frame, dz, rx_deg, ry_deg in poses:
    scene.frame_set(frame)
    root.location = base_location.copy()
    root.location.z += dz
    root.rotation_euler = base_rotation.copy()
    root.rotation_euler.x += rx_deg * 3.141592653589793 / 180.0
    root.rotation_euler.y += ry_deg * 3.141592653589793 / 180.0
    root.keyframe_insert(data_path="location", frame=frame)
    root.keyframe_insert(data_path="rotation_euler", frame=frame)

# Smooth the test motion.
if root.animation_data and root.animation_data.action:
    for fcurve in root.animation_data.action.fcurves:
        for key in fcurve.keyframe_points:
            key.interpolation = "BEZIER"

scene.frame_set(1)

result_idle = bpy.ops.wm.usd_export(
    filepath=OUT_IDLE,
    export_materials=True,
    export_uvmaps=True,
    export_normals=True,
    relative_paths=True,
    export_animation=True,
)
print("Animated USDZ export result:", result_idle)
print("Wrote:", OUT_IDLE, os.path.getsize(OUT_IDLE), "bytes")
