"""Author pin and linked rack in the open Blender instance via Blender MCP."""
import bpy, bmesh, math, json
from pathlib import Path
from mathutils import Vector

BASE=Path('F:/UnityProjects/BowlingGame')
OUT=BASE/'Blender/Exports/Pins'
OUT.mkdir(parents=True,exist_ok=True)
if bpy.data.objects.get('BowlingPin') or bpy.data.scenes.get('Pin_Asset'):
    raise RuntimeError('Pin asset already exists; inspect before modifying.')
if bpy.context.mode!='OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
scene=bpy.data.scenes.new('Pin_Asset')
bpy.context.window.scene=scene
scene.unit_settings.system='METRIC'
scene.unit_settings.scale_length=1
asset=bpy.data.collections.new('PIN | Export')
scene.collection.children.link(asset)
studio=bpy.data.collections.new('PIN STUDIO | Do not export')
scene.collection.children.link(studio)

# Pixel-space profile read from both references, bottom to top. Symmetrized
# around the axis; apparent top/bottom ellipse depth is not treated as body shape.
# Each entry is image Y and half-width. Height in reference: roughly 60..1478.
profile=[(1478,85),(1450,105),(1328,172),(1130,240),(995,248),
         (852,223),(605,113),(525,95),(475,95),(385,112),
         (250,152),(170,141),(75,60),(60,30)]
height=.38
scale=height/(1478-60)
sides=12
verts=[(r*scale*math.cos(j*math.tau/sides),r*scale*math.sin(j*math.tau/sides),(1478-y)*scale)
       for y,r in profile for j in range(sides)]
faces=[]
band_flags=[]
for row in range(len(profile)-1):
    # Two red rings share the body mesh; no floating sleeve geometry.
    red=row in (6,8)
    for j in range(sides):
        faces.append((row*sides+j,row*sides+(j+1)%sides,(row+1)*sides+(j+1)%sides,(row+1)*sides+j))
        band_flags.append(red)
faces += [tuple(reversed(range(sides))),tuple((len(profile)-1)*sides+j for j in range(sides))]
band_flags += [False,False]
data=bpy.data.meshes.new('BowlingPin_Mesh')
data.from_pydata(verts,[],faces)
data.update()
pin=bpy.data.objects.new('BowlingPin',data)
asset.objects.link(pin)
pin['height_m']=height
pin['source']='ConceptArt/BownlingPin.png + ConceptArt/BowlingPinSilhouette.png'
pin['pivot']='Base centre; Blender Z up'
pin['radial_sides']=sides

# Tiny portable colour atlas, with ample padding around the two sample points.
image=bpy.data.images.new('PinPalette',width=64,height=16,alpha=False)
cream=(.91,.865,.785,1)
red=(.72,.075,.055,1)
image.pixels=[v for y in range(16) for x in range(64) for v in (cream if x<32 else red)]
image.filepath_raw=str(OUT/'PinPalette.png'); image.file_format='PNG'; image.save()
material=bpy.data.materials.new('Pin_Palette'); material.use_nodes=True
bsdf=material.node_tree.nodes.get('Principled BSDF')
bsdf.inputs['Roughness'].default_value=.32
texture=material.node_tree.nodes.new('ShaderNodeTexImage'); texture.image=image; texture.interpolation='Closest'
material.node_tree.links.new(texture.outputs['Color'],bsdf.inputs['Base Color'])
data.materials.append(material)
uv=data.uv_layers.new(name='UVMap')
for poly,is_red in zip(data.polygons,band_flags):
    poly.use_smooth=False
    for li in poly.loop_indices: uv.data[li].uv=(.75 if is_red else .25,.5)

# Linked mesh copies on existing pin spots, confined to their own collection.
lane=bpy.data.scenes['Lane_Asset']
rack=bpy.data.collections.new('PINS | Rack preview')
lane.collection.children.link(rack)
rack_root=bpy.data.objects.new('BowlingPinRack',None); rack.objects.link(rack_root)
rack_root.location=(0,7,0)
number=1
for row in range(4):
    for col in range(row+1):
        ob=bpy.data.objects.new('Pin_%02d'%number,data)
        rack.objects.link(ob); ob.parent=rack_root
        ob.location=((col-row/2)*.3048,row*.264,0)
        number+=1

def camera(name,pos,target,ortho):
    cam_data=bpy.data.cameras.new(name)
    ob=bpy.data.objects.new(name,cam_data); studio.objects.link(ob)
    ob.location=pos; ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    cam_data.type='ORTHO'; cam_data.ortho_scale=ortho
    return ob
scene.camera=camera('Pin_Portrait',(0,-1,.19),(0,0,.19),.47)
camera('Pin_Three_Quarter',(.5,-1,.4),(0,0,.19),.48)
closeup_data=bpy.data.cameras.new('Pin_Rack_Closeup')
closeup=bpy.data.objects.new('Pin_Rack_Closeup',closeup_data)
bpy.data.collections['STUDIO | Do not export'].objects.link(closeup)
closeup.location=(1.15,5.1,1.05)
closeup.rotation_euler=(Vector((0,7.4,.16))-closeup.location).to_track_quat('-Z','Y').to_euler()
closeup_data.lens=55
world=bpy.data.worlds.new('Pin_Studio_World'); world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.11,.13,.17,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.5
scene.world=world
for name,pos,power,size in [('Pin_Key',(-.45,-.6,.8),22,.55),('Pin_Fill',(.5,-.2,.4),8,.4),('Pin_Rim',(.1,.5,.65),18,.4)]:
    ld=bpy.data.lights.new(name,'AREA'); ld.energy=power; ld.shape='DISK'; ld.size=size
    ob=bpy.data.objects.new(name,ld); studio.objects.link(ob); ob.location=pos
    ob.rotation_euler=(Vector((0,0,.2))-ob.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES'; scene.cycles.samples=32; scene.cycles.use_denoising=True
scene.render.resolution_x=800; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.render.filepath=str(BASE/'Journey/screenshots/003-pin-portrait.png')
scene.view_settings.view_transform='AgX'
bpy.ops.object.select_all(action='DESELECT'); pin.select_set(True); bpy.context.view_layer.objects.active=pin
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.shading.type='MATERIAL'
        area.spaces.active.overlay.show_overlays=False
        area.spaces.active.region_3d.view_perspective='CAMERA'
export_options=dict(use_selection=True,object_types={'MESH','EMPTY'},apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',use_triangles=True,
    bake_anim=False,path_mode='RELATIVE',use_custom_props=True)
bpy.ops.export_scene.fbx(filepath=str(OUT/'BowlingPin.fbx'),**export_options)
bpy.context.window.scene=lane
bpy.ops.object.select_all(action='DESELECT')
for ob in rack.objects: ob.select_set(True)
bpy.context.view_layer.objects.active=rack_root
bpy.ops.export_scene.fbx(filepath=str(OUT/'BowlingPinRack.fbx'),**export_options)
bpy.context.window.scene=scene

data.calc_loop_triangles()
bm=bmesh.new(); bm.from_mesh(data)
report={'height_m':height,'width_m':2*248*scale,'vertices':len(data.vertices),
    'triangles_per_pin':len(data.loop_triangles),'rack_triangles':10*len(data.loop_triangles),
    'radial_sides':sides,'profile_rings':len(profile),'materials':1,'texture':'64x16 PinPalette.png',
    'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),
    'zero_area_faces':sum(f.calc_area()<1e-10 for f in bm.faces),
    'volume_m3':bm.calc_volume(signed=True),'red_face_count':sum(band_flags),
    'reference_profile_pixels':profile,'unity_import_tested':False}
bm.free()
assert report['non_manifold_edges']==0 and report['zero_area_faces']==0 and report['volume_m3']>0
(OUT/'Pin_validation.json').write_text(json.dumps(report,indent=2))
image.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Blender/BowlingAssets.blend'))
result=report
