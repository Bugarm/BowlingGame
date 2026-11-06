"""Create three low-poly bowling balls inside Blender via MCP."""
import bpy, bmesh, math, json
from pathlib import Path
from mathutils import Vector

BASE=Path('F:/UnityProjects/BowlingGame')
OUT=BASE/'Blender/Exports/Balls'; OUT.mkdir(parents=True,exist_ok=True)
if bpy.data.scenes.get('Ball_Assets'): raise RuntimeError('Ball assets already exist; inspect first.')
if bpy.context.mode!='OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
scene=bpy.data.scenes.new('Ball_Assets'); bpy.context.window.scene=scene
scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1
asset=bpy.data.collections.new('BALLS | Export'); scene.collection.children.link(asset)
studio=bpy.data.collections.new('BALL STUDIO | Do not export'); scene.collection.children.link(studio)
radius=.1085
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3,radius=radius)
ball=bpy.context.object; ball.name='BowlingBall_Red'
for c in list(ball.users_collection): c.objects.unlink(ball)
asset.objects.link(ball)
body=bpy.data.materials.new('Ball_Working_Body')
interior=bpy.data.materials.new('Ball_Working_Interior')
ball.data.materials.append(body); ball.data.materials.append(interior)
holes=[(-.025,-.048,.094,.010),(.025,-.048,.094,.010),(0,-.086,.058,.013)]
for i,(x,y,z,r) in enumerate(holes):
    direction=Vector((x,y,z)).normalized()
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=.083,location=direction*.1025)
    cutter=bpy.context.object; cutter.name='Ball_Temporary_Drill_%d'%i
    cutter.rotation_euler=direction.to_track_quat('Z','Y').to_euler()
    cutter.data.materials.append(body); cutter.data.materials.append(interior)
    for p in cutter.data.polygons:p.material_index=1
    bpy.ops.object.select_all(action='DESELECT'); ball.select_set(True); bpy.context.view_layer.objects.active=ball
    mod=ball.modifiers.new('Recess_%d'%i,'BOOLEAN'); mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
ball.data.update()
interior_faces=[p.index for p in ball.data.polygons if p.material_index==1]
assert interior_faces,'Boolean interior material classification missing'

palette=bpy.data.images.new('BallPalette',width=128,height=16,alpha=False)
hexes=['A82E35','225C80','346346','111921','BC3C40','306E91','427752','222E38']
def rgba(h):return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))+(1,)
palette.pixels=[v for y in range(16) for x in range(128) for v in rgba(hexes[x//16])]
palette.filepath_raw=str(OUT/'BallPalette.png');palette.file_format='PNG';palette.save()
mat=bpy.data.materials.new('Ball_Palette');mat.use_nodes=True
shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Roughness'].default_value=.3
tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=palette;tex.interpolation='Closest'
mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color'])
ball.data.materials.clear();ball.data.materials.append(mat)
uv=ball.data.uv_layers.get('UVMap') or ball.data.uv_layers.new(name='UVMap')
balls=[]
for idx,name in enumerate(['Red','Blue','Green']):
    ob=ball if idx==0 else bpy.data.objects.new('BowlingBall_'+name,ball.data.copy())
    if idx:asset.objects.link(ob)
    ob.name='BowlingBall_'+name;ob.data.name=ob.name+'_Mesh'
    for p in ob.data.polygons:
        p.material_index=0;p.use_smooth=False
        colour=3 if p.index in interior_faces else idx
        for li in p.loop_indices:ob.data.uv_layers.active.data[li].uv=((colour+.5)/8,.5)
    ob['diameter_m']=radius*2;ob['pivot']='Sphere centre';ob['finger_holes']=3
    ob['collision_hint']='Use a SphereCollider radius 0.1085 m during Unity integration'
    balls.append(ob)

export_options=dict(use_selection=True,object_types={'MESH'},apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',use_triangles=True,
    bake_anim=False,path_mode='RELATIVE',use_custom_props=True)
reports=[]
for ob in balls:
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
    bpy.ops.export_scene.fbx(filepath=str(OUT/(ob.name+'.fbx')),**export_options)
    ob.data.calc_loop_triangles()
    bm=bmesh.new();bm.from_mesh(ob.data)
    report={'name':ob.name,'vertices':len(ob.data.vertices),'triangles':len(ob.data.loop_triangles),
       'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-10 for f in bm.faces),
       'volume_m3':bm.calc_volume(signed=True),'interior_faces':len(interior_faces)}
    bm.free()
    assert report['non_manifold_edges']==0 and report['zero_area_faces']==0 and report['volume_m3']>0
    reports.append(report)
# Move objects only for the source review scene; individual exports above stay centred.
for idx,ob in enumerate(balls):ob.location=((idx-1)*.285,0,radius)
scene['export_note']='Reset ball location to zero for individual re-export; build script exports before staging.'

def camera(name,pos,target,ortho):
    data=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,data);studio.objects.link(ob)
    ob.location=pos;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    data.type='ORTHO';data.ortho_scale=ortho;return ob
scene.camera=camera('Balls_Overview',(0,-1.4,1.0),(0,0,.1085),.96)
camera('Ball_Detail',(-.285,-.55,.48),(-.285,0,.1085),.30)
world=bpy.data.worlds.new('Ball_Studio_World');world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.09,.11,.15,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.5;scene.world=world
for name,pos,power,size in [('Ball_Key',(-.5,-.5,1),35,.7),('Ball_Fill',(.6,-.3,.5),12,.6),('Ball_Rim',(0,.5,.7),25,.5)]:
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
    ob=bpy.data.objects.new(name,data);studio.objects.link(ob);ob.location=pos
    ob.rotation_euler=(Vector((0,0,.1))-ob.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=1500;scene.render.resolution_y=700;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.render.filepath=str(BASE/'Journey/screenshots/004-bowling-balls.png');scene.view_settings.view_transform='AgX'
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.shading.type='MATERIAL';area.spaces.active.overlay.show_overlays=False
        area.spaces.active.region_3d.view_perspective='CAMERA'
palette.pack()
result={'balls':reports,'nominal_diameter_m':radius*2,'materials':1,'texture':'128x16 BallPalette.png',
        'hole_radii_m':[.01,.01,.013],'hole_bottom_radius_m':.061,'unity_import_tested':False}
(OUT/'Ball_validation.json').write_text(json.dumps(result,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Blender/BowlingAssets.blend'))
