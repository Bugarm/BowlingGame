"""Author the reference ball return through Blender MCP; no Unity mutations."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
BASE=Path('F:/UnityProjects/BowlingGame');OUT=BASE/'Blender/Exports/BallReturn';OUT.mkdir(parents=True,exist_ok=True)
if bpy.data.scenes.get('BallReturn_Asset'):raise RuntimeError('Return already exists; inspect first.')
if bpy.context.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
s=bpy.data.scenes.new('BallReturn_Asset');bpy.context.window.scene=s
s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
asset=bpy.data.collections.new('BALL RETURN | Export');s.collection.children.link(asset)
studio=bpy.data.collections.new('RETURN STUDIO | Do not export');s.collection.children.link(studio)
preview=bpy.data.collections.new('RETURN BALLS | Preview only');s.collection.children.link(preview)
root=bpy.data.objects.new('BowlingBallReturn',None);asset.objects.link(root)
root['pivot']='Ground centre of housing; tray extends Blender -Y'
root['capacity']=3;root['visual_asset_only']=True
palette=bpy.data.images.new('ReturnPalette',width=128,height=16,alpha=False)
hexes=['34343B','505057','8E8C8B','B3AAA0','BA3034','705044','805D4E','17191D']
def rgba(h):return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))+(1,)
palette.pixels=[v for y in range(16) for x in range(128) for v in rgba(hexes[x//16])]
palette.filepath_raw=str(OUT/'ReturnPalette.png');palette.file_format='PNG';palette.save()
mat=bpy.data.materials.new('Return_Palette');mat.use_nodes=True
bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Roughness'].default_value=.48
tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=palette;tex.interpolation='Closest'
mat.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color'])
def paint(ob,colors):
    ob.data.materials.append(mat);uv=ob.data.uv_layers.get('UVMap') or ob.data.uv_layers.new(name='UVMap')
    for p,c in zip(ob.data.polygons,colors):
        for li in p.loop_indices:uv.data[li].uv=((c+.5)/8,.5)
def mesh(name,verts,faces,colors):
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    ob=bpy.data.objects.new(name,data);asset.objects.link(ob);ob.parent=root;paint(ob,colors);return ob
def box(name,loc,size,color,bevel=0):
    bpy.ops.object.select_all(action='DESELECT');bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    ob=bpy.context.object;ob.name=name
    for col in list(ob.users_collection):col.objects.unlink(ob)
    asset.objects.link(ob);ob.parent=root;ob.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        m=ob.modifiers.new('Faceted chamfer','BEVEL');m.width=min(bevel,min(size)*.24);m.segments=1;bpy.ops.object.modifier_apply(modifier=m.name)
    paint(ob,[color]*len(ob.data.polygons));return ob

# Housing at y=0; front opening faces -Y. Hollow ring with actual inner walls.
outer=[(-.30,.07),(.30,.07),(.30,.44),(.27,.64),(.20,.73),(-.20,.73),(-.27,.64),(-.30,.44)]
inner=[(-.19,.25),(.19,.25),(.19,.44),(.17,.57),(.135,.625),(-.135,.625),(-.17,.57),(-.19,.44)]
verts=[(x,y,z) for y in (-.29,.29) for profile in (outer,inner) for x,z in profile]
faces=[];colors=[]
for i in range(8):
    j=(i+1)%8
    faces.extend([(i,j,8+j,8+i),(16+i,24+i,24+j,16+j),(i,16+i,16+j,j),(8+i,8+j,24+j,24+i)])
    colors.extend([1 if i in (2,3,4,5,6) else 0,0,1 if i in (3,4,5) else 0,7])
mesh('Return_Housing',verts,faces,colors)
# Rear cover, same faceted outline, shallow thickness.
verts=[(x,y,z) for y in (.29,.315) for x,z in outer]
faces=[tuple(reversed(range(8))),tuple(range(8,16))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
mesh('Return_Rear_Cover',verts,faces,[0]*len(faces))
box('Return_Housing_Plinth',(0,0,.035),(.66,.67,.07),0,.014)
box('Return_Rear_Service_Panel',(0,.333,.285),(.41,.022,.39),0,.007)
box('Return_Rear_Red_Badge',(0,.348,.515),(.25,.008,.032),4,.007)

# Tray: 0.80 m exposed usable length for three 0.217 m balls.
box('Return_Tray_Chassis',(0,-.66,.265),(.48,1.00,.085),0,.012)
box('Return_Tray_Wood',(0,-.64,.3075),(.375,.98,.015),5)
# Subtle alternating wooden strips: coplanar top faces, no collision grooves.
verts=[];faces=[]
for i in range(6):
    x0=-.1875+i*.0625;x1=x0+.0625;k=len(verts)
    verts.extend([(x0,-1.13,.3152),(x1,-1.13,.3152),(x1,-.15,.3152),(x0,-.15,.3152)])
    faces.append((k,k+1,k+2,k+3))
mesh('Return_Wood_Strips',verts,faces,[5,6,5,6,5,6])
for side,label in [(-1,'Left'),(1,'Right')]:
    box('Return_Rail_'+label,(side*.222,-.67,.348),(.055,1.02,.085),2,.008)
    box('Return_Rail_Dark_Top_'+label,(side*.222,-.67,.392),(.038,1.0,.014),7,.004)
    box('Return_Stop_Cap_'+label,(side*.222,-1.185,.325),(.09,.10,.145),2,.015)
    # Side slash on the vertical lower housing panel; tiny offset prevents z-fighting.
    x=side*.3006
    mesh('Return_Red_Slash_'+label,[(x,-.22,.15),(x,.20,.385),(x,.20,.435),(x,.10,.415)],[(0,1,2,3)] if side>0 else [(3,2,1,0)],[4])
box('Return_Front_Stop',(0,-1.19,.321),(.42,.075,.13),1,.007)
box('Return_Tray_Leg',(0,-.88,.135),(.22,.23,.20),0,.008)
box('Return_Tray_Foot',(0,-.88,.03),(.31,.32,.06),0,.008)
box('Return_Light_Recess',(0,-.298,.599),(.205,.022,.053),7,.008)
lamp=box('Return_Warm_Light',(0,-.314,.60),(.165,.012,.026),3,.006)
lampmat=bpy.data.materials.new('Return_Warm_Lamp');lampmat.use_nodes=True
ls=lampmat.node_tree.nodes.get('Principled BSDF');ls.inputs['Base Color'].default_value=(1,.72,.3,1)
ls.inputs['Emission Color'].default_value=(1,.62,.18,1);ls.inputs['Emission Strength'].default_value=2
lamp.data.materials.clear();lamp.data.materials.append(lampmat)
for idx,name in enumerate(['Red','Blue','Green']):
    source=bpy.data.objects['BowlingBall_'+name]
    ob=bpy.data.objects.new('Return_Preview_Ball_'+name,source.data);preview.objects.link(ob)
    ob.location=(0,-1.02+idx*.245,.3152+.1085)

def camera(name,pos,target,ortho):
    data=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,data);studio.objects.link(ob)
    ob.location=pos;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=ortho;return ob
s.camera=camera('Return_Perspective',(1.7,-2.7,1.6),(0,-.47,.34),1.9)
camera('Return_Side',(2,-.45,.4),(0,-.45,.4),1.8)
camera('Return_Front',(0,-3,1),(0,-.3,.34),1.55)
world=bpy.data.worlds.new('Return_Studio_World');world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.14,.18,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.55;s.world=world
for name,pos,power,size in [('Return_Key',(-1,-1.5,2.5),170,2),('Return_Fill',(2,-.5,1.5),100,1.5),('Return_Rim',(0,1.2,1.8),130,1.2)]:
    ld=bpy.data.lights.new(name,'AREA');ld.energy=power;ld.shape='DISK';ld.size=size
    ob=bpy.data.objects.new(name,ld);studio.objects.link(ob);ob.location=pos
    ob.rotation_euler=(Vector((0,-.3,.35))-ob.location).to_track_quat('-Z','Y').to_euler()
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.resolution_x=1400;s.render.resolution_y=1100;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.film_transparent=False;s.view_settings.view_transform='AgX'
s.render.filepath=str(BASE/'Journey/screenshots/005-ball-return.png')
bpy.ops.object.select_all(action='DESELECT')
for ob in asset.objects:ob.select_set(True)
bpy.context.view_layer.objects.active=root
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.shading.type='MATERIAL';area.spaces.active.overlay.show_overlays=False;area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.export_scene.fbx(filepath=str(OUT/'BowlingBallReturn.fbx'),use_selection=True,object_types={'MESH','EMPTY'},apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',use_triangles=True,bake_anim=False,path_mode='RELATIVE',use_custom_props=True)
stats=[]
for ob in asset.objects:
    if ob.type=='MESH':
        ob.data.calc_loop_triangles();stats.append({'name':ob.name,'triangles':len(ob.data.loop_triangles)})
result={'meshes':stats,'triangles':sum(r['triangles'] for r in stats),'materials':2,'texture':'128x16 ReturnPalette.png',
    'capacity':3,'preview_balls_exported':False,'nominal_size_m':[.66,1.587,.73],
    'ball_centres_y_m':[-1.02,-.775,-.53],'ball_diameter_m':.217,'unity_import_tested':False}
(OUT/'Return_validation.json').write_text(json.dumps(result,indent=2))
palette.pack();bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Blender/BowlingAssets.blend'))
