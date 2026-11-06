"""Run inside the open Blender instance through Blender MCP. Creates a new scene."""
import bpy, math, random, json
from pathlib import Path
from mathutils import Vector

BASE = Path('F:/UnityProjects/BowlingGame')
OUT = BASE / 'Blender/Exports/Lane'
OUT.mkdir(parents=True, exist_ok=True)
(BASE / 'Journey/screenshots').mkdir(parents=True, exist_ok=True)
if bpy.data.scenes.get('Lane_Asset'):
    raise RuntimeError('Lane_Asset already exists; inspect before rebuilding.')
scene = bpy.data.scenes.new('Lane_Asset')
bpy.context.window.scene = scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1
asset = bpy.data.collections.new('LANE | Export')
scene.collection.children.link(asset)
studio = bpy.data.collections.new('STUDIO | Do not export')
scene.collection.children.link(studio)
root = bpy.data.objects.new('BowlingLane', None)
asset.objects.link(root)
root['pivot'] = 'Foul line centre, playing surface height zero; lane extends +Y in Blender'
root['lane_width_m'] = 1.0668
root['head_pin_distance_m'] = 18.288

# Wide padded swatches: one tiny, portable texture and one material for all meshes.
hexes = ['CB934D','D49C54','DCA760','C58D49','D09A55','E0AC68','D7A15D','CC9450',
         '34343B','48464B','625C59','ACA297','C2B6A2','60452D','1D2229','AA493B']
def rgb(h): return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
img = bpy.data.images.new('LanePalette', width=256, height=16, alpha=False)
img.pixels = [v for y in range(16) for x in range(256) for v in (*rgb(hexes[x//16]),1)]
img.filepath_raw = str(OUT / 'LanePalette.png')
img.file_format = 'PNG'
img.save()
mat = bpy.data.materials.new('Lane_Palette')
mat.use_nodes = True
shader = mat.node_tree.nodes.get('Principled BSDF')
shader.inputs['Roughness'].default_value = .36
tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
tex.image = img
tex.interpolation = 'Closest'
mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color'])

def paint(obj, indices):
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    uv = obj.data.uv_layers.get('UVMap') or obj.data.uv_layers.new(name='UVMap')
    for face, idx in zip(obj.data.polygons, indices):
        for li in face.loop_indices: uv.data[li].uv = ((idx+.5)/16,.5)

def mesh(name, verts, faces, colors):
    data = bpy.data.meshes.new(name)
    data.from_pydata(verts, [], faces)
    data.update()
    ob = bpy.data.objects.new(name, data)
    asset.objects.link(ob)
    ob.parent = root
    paint(ob,colors)
    return ob

def box(name, loc, size, color, bevel=0):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.object
    ob.name = name
    for col in list(ob.users_collection): col.objects.unlink(ob)
    asset.objects.link(ob)
    ob.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = ob.modifiers.new('Single segment edge chamfer','BEVEL')
        mod.width = bevel
        mod.segments = 1
        bpy.ops.object.modifier_apply(modifier=mod.name)
    ob.parent = root
    paint(ob, [color]*len(ob.data.polygons))
    return ob

random.seed(23)
def boards(name, width, start, end, count):
    verts, faces, colors = [], [], []
    for i in range(count):
        x0 = -width/2+width*i/count
        x1 = -width/2+width*(i+1)/count
        y = start
        while y < end-1e-6:
            next_y = min(end, y+random.uniform(1.1,2.5))
            k = len(verts)
            verts += [(x0,y,0),(x1,y,0),(x1,next_y,0),(x0,next_y,0)]
            faces.append((k,k+1,k+2,k+3))
            colors.append(random.randrange(8))
            y = next_y
    return mesh(name,verts,faces,colors)

width, deck_end, approach = 1.0668, 19.55, 4.5
box('Lane_Foundation',(0,9.775,-.27),(1.91,19.55,.18),8,.025)
box('Approach_Foundation',(0,-2.25,-.245),(1.91,4.5,.23),8,.025)
box('Lane_Wood_Edge',(0,9.775,-.065),(width,19.55,.12),3)
box('Approach_Wood_Edge',(0,-2.25,-.065),(1.91,4.5,.12),3)
boards('Lane_Surface',width,0,deck_end,39)
boards('Approach_Surface',1.91,-approach,0,69)

# Open-top, solid-bottom, faceted channels. Both ends are capped.
for side, label in [(-1,'Left'),(1,'Right')]:
    inner = width/2
    profile = [(inner,-.004),(inner+.028,-.063),(inner+.075,-.112),
               (inner+.13,-.14),(inner+.195,-.14),(inner+.25,-.105),
               (inner+.295,-.055),(inner+.315,-.004),
               (inner+.315,-.18),(inner,-.18)]
    verts = [(side*x,y,z) for y in (0,20.25) for x,z in profile]
    n = len(profile)
    faces = [(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
    faces += [tuple(reversed(range(n))),tuple(range(n,n*2))]
    if side < 0: faces = [tuple(reversed(f)) for f in faces]
    gutter = mesh('Gutter_'+label,verts,faces,[9]*7+[8]*5)
    # Correct outward normals for a closed cross-section extrusion.
    bpy.ops.object.select_all(action='DESELECT')
    gutter.select_set(True)
    bpy.context.view_layer.objects.active = gutter
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    box('Edge_Rail_'+label,(side*.902,10.125,-.012),(.105,20.25,.11),11,.018)

# Flat inlays sit 1 mm above the surface; exclude them from future collision meshes.
verts, faces, colors = [], [], []
for i in range(-3,4):
    x, y = i*.1368, 4.57-abs(i)*.28
    k = len(verts)
    verts += [(x-.025,y-.07,.001),(x+.025,y-.07,.001),(x,y+.09,.001)]
    faces.append((k,k+1,k+2)); colors.append(13)
for y in (-3.65,-.9,2.1):
    for i in range(-3,4):
        k = len(verts)
        radius = .011 if i else .016
        verts += [(i*.1368+radius*math.cos(a*math.tau/8),y+radius*math.sin(a*math.tau/8),.001) for a in range(8)]
        faces.append(tuple(range(k,k+8))); colors.append(13)
mesh('Lane_Aiming_Inlays',verts,faces,colors)
mesh('Foul_Line',[(-.5334,-.018,.001),(.5334,-.018,.001),(.5334,.018,.001),(-.5334,.018,.001)],[(0,1,2,3)],[14])
box('Pin_Pit_Base',(0,19.94,-.22),(1.91,.78,.18),14,.02)
box('Pit_Backstop',(0,20.31,-.01),(1.91,.12,.6),8,.025)

# Small pin placement dots are part of the lane, not pin assets.
verts, faces = [], []
for row in range(4):
    for col in range(row+1):
        x,y = (col-row/2)*.3048,18.288+row*.264
        k = len(verts)
        verts += [(x+.012*math.cos(a*math.tau/8),y+.012*math.sin(a*math.tau/8),.001) for a in range(8)]
        faces.append(tuple(range(k,k+8)))
mesh('Pin_Deck_Spots',verts,faces,[13]*len(faces))

def camera(name, pos, target, ortho=None):
    data = bpy.data.cameras.new(name)
    ob = bpy.data.objects.new(name,data); studio.objects.link(ob)
    ob.location = pos
    ob.rotation_euler = (Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    if ortho: data.type='ORTHO'; data.ortho_scale=ortho
    else: data.lens=28
    return ob
scene.camera = camera('Lane_Overview',(12,-13,19),(0,7.5,0),28)
camera('Lane_Player_View',(0,-3.5,1.65),(0,9.5,0))
world = bpy.data.worlds.new('Lane_Studio_World'); world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.22,.22,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.8
scene.world=world
for name,pos,power,size in [('Key',(-5,5,12),2500,12),('Fill',(6,12,8),1700,10)]:
    data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size
    ob=bpy.data.objects.new(name,data); studio.objects.link(ob); ob.location=pos
    ob.rotation_euler=(Vector((0,8,0))-ob.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES'
scene.cycles.samples=32
scene.cycles.use_denoising=True
scene.render.resolution_x=1400; scene.render.resolution_y=1000; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=True
scene.view_settings.view_transform='AgX'
bpy.ops.object.select_all(action='DESELECT')
for ob in asset.objects: ob.select_set(True)
bpy.context.view_layer.objects.active=root
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.shading.type='MATERIAL'
        area.spaces.active.overlay.show_overlays=False
        area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.export_scene.fbx(filepath=str(OUT/'BowlingLane.fbx'),use_selection=True,object_types={'MESH','EMPTY'},
    apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',
    use_triangles=True,bake_anim=False,path_mode='RELATIVE',use_custom_props=True)
stats=[]
for ob in asset.objects:
    if ob.type=='MESH':
        ob.data.calc_loop_triangles()
        stats.append({'name':ob.name,'vertices':len(ob.data.vertices),'triangles':len(ob.data.loop_triangles)})
report={'meshes':stats,'triangles':sum(s['triangles'] for s in stats),'materials':1,
        'texture':'256x16 LanePalette.png','lane_width_m':width,'head_pin_y_m':18.288,
        'bounds_y_m':[-4.5,20.37],'unity_import_tested':False}
(OUT/'Lane_validation.json').write_text(json.dumps(report,indent=2))
img.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Blender/BowlingAssets.blend'))
result=report
