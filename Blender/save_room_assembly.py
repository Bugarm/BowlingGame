"""Save the source and a single-scene .blend via Blender MCP after render review."""
import bpy,json
from pathlib import Path
BASE=Path('F:/UnityProjects/BowlingGame')
scene=bpy.data.scenes['BowlingRoom_Complete'];bpy.context.window.scene=scene
bpy.data.collections['ROOM | Ceiling'].hide_render=False
scene.camera=bpy.data.objects['Room_Player_View']
scene.render.resolution_x=1600;scene.render.resolution_y=1000
scene.render.filepath=str(BASE/'Journey/screenshots/007-room-player-view.png')
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        a.spaces.active.region_3d.view_perspective='CAMERA'
        a.spaces.active.shading.type='MATERIAL'
bpy.ops.object.select_all(action='DESELECT')
root=bpy.data.objects['BowlingRoom'];root.select_set(True);bpy.context.view_layer.objects.active=root
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Blender/BowlingAssets.blend'))
target=BASE/'Blender/Assembly/BowlingRoom.blend'
bpy.data.libraries.write(str(target),{scene},fake_user=True,compress=True)
with bpy.data.libraries.load(str(target),link=False) as (source,dest):
    names=list(source.scenes)
assert names==['BowlingRoom_Complete'],names
result={'source_saved':bpy.data.filepath,'standalone':str(target),'standalone_scenes':names,
        'standalone_bytes':target.stat().st_size,'ceiling_restored':True}
(BASE/'Blender/Assembly/Save_validation.json').write_text(json.dumps(result,indent=2))
