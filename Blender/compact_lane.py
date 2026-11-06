"""Apply once through Blender MCP after build_lane.py; retain cross-section and pin spacing."""
import bpy, json
from pathlib import Path
from mathutils import Vector

BASE = Path('F:/UnityProjects/BowlingGame')
OUT = BASE / 'Blender/Exports/Lane'
scene = bpy.data.scenes['Lane_Asset']
bpy.context.window.scene = scene
asset = bpy.data.collections['LANE | Export']
root = bpy.data.objects['BowlingLane']
if root.get('proportion_revision'):
    raise RuntimeError('Compact proportions already applied; inspect rather than applying twice.')
assert abs(root['head_pin_distance_m']-18.288)<.001

def remap_y(name, function):
    ob=bpy.data.objects[name]
    old_origin=ob.location.y
    new_origin=function(old_origin)
    for v in ob.data.vertices:
        v.co.y=function(v.co.y+old_origin)-new_origin
    ob.location.y=new_origin
    ob.data.update()

head_pin=7.0
deck_end=19.55-(18.288-head_pin)
for name in ['Lane_Foundation','Lane_Wood_Edge','Lane_Surface']:
    remap_y(name,lambda y:y*deck_end/19.55)
for name in ['Approach_Foundation','Approach_Wood_Edge','Approach_Surface']:
    remap_y(name,lambda y:y/3)
for name in ['Gutter_Left','Gutter_Right','Edge_Rail_Left','Edge_Rail_Right']:
    remap_y(name,lambda y:y*(deck_end+.7)/20.25)
for name in ['Pin_Pit_Base','Pit_Backstop','Pin_Deck_Spots']:
    remap_y(name,lambda y:y-(18.288-head_pin))

# Move marks independently; preserve each triangle and circular dot's shape.
marks=bpy.data.objects['Lane_Aiming_Inlays']
for p in marks.data.polygons:
    ids=list(p.vertices)
    if len(ids)==3:
        x=sum(marks.data.vertices[i].co.x for i in ids)/3
        column=round(x/.1368)
        delta=(1.65-abs(column)*.22)-(4.57-abs(column)*.28)
    else:
        y=sum(marks.data.vertices[i].co.y for i in ids)/len(ids)
        old,new=min([(-3.65,-1.1),(-.9,-.3),(2.1,.55)],key=lambda pair:abs(pair[0]-y))
        delta=new-old
    for i in ids: marks.data.vertices[i].co.y+=delta
marks.data.update()
root['head_pin_distance_m']=head_pin
root['approach_length_m']=1.5
root['proportion_revision']='002 concept compact lane'
root['arrow_centres_y_m']='0.99 to 1.65'

def aim(name,pos,target):
    ob=bpy.data.objects[name]
    ob.location=pos
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
aim('Lane_Overview',(8,-9,11),(0,3.5,0))
bpy.data.objects['Lane_Overview'].data.ortho_scale=13
aim('Lane_Player_View',(0,-1.1,1.65),(0,4.0,0))
bpy.data.objects['Lane_Player_View'].data.lens=28
scene.camera=bpy.data.objects['Lane_Overview']
scene.render.resolution_x=1400
scene.render.resolution_y=1000
scene.render.filepath=str(BASE/'Journey/screenshots/002-compact-lane-overview.png')
bpy.ops.object.select_all(action='DESELECT')
for ob in asset.objects: ob.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.export_scene.fbx(filepath=str(OUT/'BowlingLane.fbx'),use_selection=True,object_types={'MESH','EMPTY'},
    apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',
    use_triangles=True,bake_anim=False,path_mode='RELATIVE',use_custom_props=True)
stats=[]
for ob in asset.objects:
    if ob.type=='MESH':
        ob.data.calc_loop_triangles()
        stats.append({'name':ob.name,'vertices':len(ob.data.vertices),'triangles':len(ob.data.loop_triangles)})
report={'revision':'002','meshes':stats,'triangles':sum(o['triangles'] for o in stats),'materials':1,
    'texture':'256x16 LanePalette.png','lane_width_m':1.0668,'head_pin_y_m':7,
    'deck_end_y_m':deck_end,'bounds_y_m':[-1.5,20.37-11.288],
    'arrow_centres_y_m':[.99,1.21,1.43,1.65,1.43,1.21,.99],
    'zero_area_faces':sum(p.area<1e-10 for o in asset.objects if o.type=='MESH' for p in o.data.polygons),
    'unity_import_tested':False}
(OUT/'Lane_validation.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Blender/BowlingAssets.blend'))
result=report
