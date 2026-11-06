"""Export the assembled bowling room for Unity.

Writes FBX + palettes under Blender/Exports/Room using the same metre-aware
FBX settings as the earlier asset exports. Pins and balls stay in the room
hierarchy so layout is preserved; they remain separately named for later
dynamics. Blender lights, cameras and layout markers are not exported.
"""
import bpy
import json
from pathlib import Path

BASE = Path(r"F:/UnityProjects/BowlingGame/BowlingGame")
OUT = BASE / "Blender" / "Exports" / "Room"
OUT.mkdir(parents=True, exist_ok=True)

scene = bpy.data.scenes["BowlingRoom_Complete"]
bpy.context.window.scene = scene
bpy.ops.object.mode_set(mode="OBJECT")

# Restore visibility in case a review hid the ceiling.
if "ROOM | Ceiling" in bpy.data.collections:
    bpy.data.collections["ROOM | Ceiling"].hide_viewport = False
    bpy.data.collections["ROOM | Ceiling"].hide_render = False

root = bpy.data.objects["BowlingRoom"]


def is_under(ob, ancestor):
    p = ob
    while p:
        if p == ancestor:
            return True
        p = p.parent
    return False


def select_hierarchy(ob):
    ob.hide_set(False)
    ob.hide_viewport = False
    ob.hide_select = False
    ob.select_set(True)
    for ch in ob.children:
        select_hierarchy(ch)


# Save packed palettes beside the FBX so Unity can find them.
palette_files = []
for img_name in ["RoomPalette", "LanePalette", "PinPalette", "BallPalette", "ReturnPalette"]:
    img = bpy.data.images[img_name]
    dest = OUT / f"{img_name}.png"
    img.filepath_raw = str(dest)
    img.file_format = "PNG"
    img.save()
    palette_files.append({"name": img_name, "path": str(dest), "size": list(img.size)})

bpy.ops.object.select_all(action="DESELECT")
select_hierarchy(root)
bpy.context.view_layer.objects.active = root

selected = [ob for ob in bpy.context.selected_objects]
mesh_count = sum(1 for ob in selected if ob.type == "MESH")
empty_count = sum(1 for ob in selected if ob.type == "EMPTY")
tris = 0
for ob in selected:
    if ob.type == "MESH":
        ob.data.calc_loop_triangles()
        tris += len(ob.data.loop_triangles)

fbx_path = OUT / "BowlingRoom.fbx"
bpy.ops.export_scene.fbx(
    filepath=str(fbx_path),
    use_selection=True,
    object_types={"MESH", "EMPTY"},
    apply_unit_scale=True,
    apply_scale_options="FBX_SCALE_UNITS",
    axis_forward="-Z",
    axis_up="Y",
    use_triangles=True,
    bake_anim=False,
    path_mode="COPY",
    embed_textures=False,
    use_custom_props=True,
)

# Unity coordinate mapping used by this export: Blender (x, y, z) -> Unity (x, z, y)
# with Blender +Y (toward pins) becoming Unity +Z.
def to_unity(v):
    return [float(v[0]), float(v[2]), float(v[1])]


markers = {}
for name in ["Player_Start", "Ball_Pickup_Stance", "Throw_Stance"]:
    ob = bpy.data.objects[name]
    markers[name] = {
        "blender": list(ob.matrix_world.translation),
        "unity": to_unity(ob.matrix_world.translation),
    }

cam = bpy.data.objects["Room_Player_View"]
camera = {
    "blender": list(cam.matrix_world.translation),
    "unity": to_unity(cam.matrix_world.translation),
    "lens": float(cam.data.lens),
}

pins = []
balls = []
for ob in selected:
    if ob.name.startswith("Room_Pin_") and ob.type == "MESH" and ob.name[9:].isdigit():
        pins.append({"name": ob.name, "unity": to_unity(ob.matrix_world.translation)})
    if ob.name.startswith("Room_Ball_"):
        balls.append({"name": ob.name, "unity": to_unity(ob.matrix_world.translation)})

report = {
    "fbx": str(fbx_path),
    "fbx_bytes": fbx_path.stat().st_size,
    "selected": len(selected),
    "meshes": mesh_count,
    "empties": empty_count,
    "triangles": tris,
    "palettes": palette_files,
    "markers": markers,
    "camera": camera,
    "pins": sorted(pins, key=lambda p: p["name"]),
    "balls": balls,
    "axis_forward": "-Z",
    "axis_up": "Y",
    "unity_mapping": "blender (x,y,z) -> unity (x,z,y); blender +Y toward pins becomes unity +Z",
    "excluded": [
        "ROOM | Blender lighting - do not export",
        "ROOM | Review cameras - do not export",
        "ROOM | Layout markers - do not export",
    ],
}
(OUT / "Room_export.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
result = report
