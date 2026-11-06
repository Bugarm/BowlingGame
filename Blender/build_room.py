"""Build the low-poly room and assemble existing assets through Blender MCP."""
import bpy,bmesh,math,json,random
from pathlib import Path
from mathutils import Vector

BASE=Path('F:/UnityProjects/BowlingGame');OUT=BASE/'Blender/Assembly';OUT.mkdir(parents=True,exist_ok=True)
if bpy.data.scenes.get('BowlingRoom_Complete'):raise RuntimeError('Room scene exists; inspect before rebuilding.')
if bpy.context.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
s=bpy.data.scenes.new('BowlingRoom_Complete');bpy.context.window.scene=s
s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
export=bpy.data.collections.new('ROOM | Complete asset assembly');s.collection.children.link(export)
def collection(name,parent=export):
    c=bpy.data.collections.new(name);parent.children.link(c);return c
shell=collection('ROOM | Floor and walls');ceiling=collection('ROOM | Ceiling')
decor=collection('ROOM | Trim and furniture');plants=collection('ROOM | Potted plants')
fixtures=collection('ROOM | Light fixture meshes');screen=collection('ROOM | Blank screen and pin surround')
lane_col=collection('ROOM | Lane');pins_col=collection('ROOM | Ten pins')
return_col=collection('ROOM | Ball return');balls_col=collection('ROOM | Three balls')
lighting=collection('ROOM | Blender lighting - do not export',s.collection)
cameras=collection('ROOM | Review cameras - do not export',s.collection)
markers=collection('ROOM | Layout markers - do not export',s.collection)
root=bpy.data.objects.new('BowlingRoom',None);export.objects.link(root)
root['dimensions']='Interior 5.6 m wide; Y -4.2 to 9.6; ceiling 3.3 m'
root['player_floor_z']=0.0
root['scope']='Assembled visual assets; no Unity gameplay or collision yet'

# Keep the existing source scenes intact, sharing geometry but copying object transforms.
def clone_collection(source,target,prefix,offset=(0,0,0)):
    mapping={}
    for old in bpy.data.collections[source].objects:
        ob=old.copy();ob.name=prefix+old.name;target.objects.link(ob);mapping[old]=ob
    for old,ob in mapping.items():
        if old.parent in mapping:ob.parent=mapping[old.parent]
        else:
            world=old.matrix_world.copy();ob.parent=root;ob.matrix_world=world
            ob.location+=Vector(offset)
    return mapping
clone_collection('LANE | Export',lane_col,'Room_')
clone_collection('PINS | Rack preview',pins_col,'Room_')
clone_collection('BALL RETURN | Export',return_col,'Room_',offset=(1.90,-1.5,0))
for name in ['Red','Blue','Green']:
    source=bpy.data.objects['Return_Preview_Ball_'+name]
    ob=source.copy();ob.name='Room_Ball_'+name;balls_col.objects.link(ob);ob.parent=root
    ob.location=source.location+Vector((1.90,-1.5,0))

hexes=['B9ADA0','D2C4B0','AC3C38','2C3038','49494E','655B55','89705E','715341',
       '293D26','426039','668248','839C4C','24262B','A79B86','735E4E','E1CBA9']
palette=bpy.data.images.new('RoomPalette',width=256,height=16,alpha=False)
def rgba(h):return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))+(1,)
palette.pixels=[v for y in range(16) for x in range(256) for v in rgba(hexes[x//16])]
palette.filepath_raw=str(OUT/'RoomPalette.png');palette.file_format='PNG';palette.save()
mat=bpy.data.materials.new('Room_Palette');mat.use_nodes=True
bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Roughness'].default_value=.72
tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=palette;tex.interpolation='Closest'
mat.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color'])
glow=bpy.data.materials.new('Room_Warm_Diffuser');glow.use_nodes=True
g=glow.node_tree.nodes.get('Principled BSDF');g.inputs['Base Color'].default_value=(1,.75,.38,1)
g.inputs['Emission Color'].default_value=(1,.64,.27,1);g.inputs['Emission Strength'].default_value=2.5
display=bpy.data.materials.new('Room_Blank_Screen');display.use_nodes=True
d=display.node_tree.nodes.get('Principled BSDF');d.inputs['Base Color'].default_value=(.008,.017,.029,1)
d.inputs['Roughness'].default_value=.38

def paint(ob,colours):
    ob.data.materials.clear();ob.data.materials.append(mat)
    uv=ob.data.uv_layers.get('UVMap') or ob.data.uv_layers.new(name='UVMap')
    for p,c in zip(ob.data.polygons,colours):
        for li in p.loop_indices:uv.data[li].uv=((c+.5)/16,.5)
def move_to(ob,col):
    for c in list(ob.users_collection):c.objects.unlink(ob)
    col.objects.link(ob);ob.parent=root
def box(name,loc,size,colour,col=decor,bevel=0):
    bpy.ops.object.select_all(action='DESELECT');bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    ob=bpy.context.object;ob.name=name;move_to(ob,col);ob.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        m=ob.modifiers.new('Single edge chamfer','BEVEL');m.width=min(bevel,min(size)*.22);m.segments=1
        bpy.ops.object.modifier_apply(modifier=m.name)
    paint(ob,[colour]*len(ob.data.polygons));return ob
def mesh(name,verts,faces,colours,col=decor):
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    ob=bpy.data.objects.new(name,data);col.objects.link(ob);ob.parent=root;paint(ob,colours);return ob
def cone(name,loc,r1,r2,depth,colour,col=decor,vertices=8):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=r1,radius2=r2,depth=depth,location=loc)
    ob=bpy.context.object;ob.name=name;move_to(ob,col);paint(ob,[colour]*len(ob.data.polygons));return ob
def rod(name,a,b,r,colour,col=decor):
    a,b=Vector(a),Vector(b);ob=cone(name,(a+b)/2,r,r*.7,(b-a).length,colour,col,6)
    ob.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return ob

# The structural slab is BELOW the gutters. Walking panels deliberately exclude
# the entire lane footprint, preventing the room floor from filling the channels.
box('Room_Subfloor',(0,2.7,-.43),(5.96,14.16,.14),3,shell)
box('Room_Front_Player_Floor',(0,-2.85,-.10),(5.6,2.7,.20),6,shell)
for side,label in [(-1,'Left'),(1,'Right')]:
    box('Room_'+label+'_Walkway',(side*1.8775,3.8,-.10),(1.845,10.6,.20),5,shell)
box('Room_Rear_Floor',(0,9.35,-.10),(5.6,.50,.20),5,shell)
# Subtle large floor blocks on side aisles, all at the same walking elevation.
for side in (-1,1):
    for i in range(10):
        x0,x1=(.958,2.8) if side==1 else (-2.8,-.958)
        y0=-1.5+i*1.06;y1=y0+1.06
        mesh('Room_Aisle_Tile_%s_%02d'%(side,i),[(x0,y0,.0004),(x1,y0,.0004),(x1,y1,.0004),(x0,y1,.0004)],[(0,1,2,3)],[5 if i%2 else 6],shell)
for side,label in [(-1,'Left'),(1,'Right')]:
    box('Room_'+label+'_Wall',(side*2.90,2.7,1.65),(.20,13.8,3.3),0,shell)
    box('Room_'+label+'_Skirting',(side*2.775,2.7,.20),(.05,13.8,.40),3,decor)
box('Room_Rear_Wall',(0,9.70,1.65),(6,.2,3.3),0,shell)
box('Room_Front_Wall',(0,-4.30,1.65),(6,.2,3.3),0,shell)
box('Room_Front_Skirting',(0,-4.175,.20),(5.6,.05,.40),3)
box('Room_Rear_Skirting',(0,9.575,.20),(5.6,.05,.40),3)

# Cream wall panels and bold red slashes from the concept; no typography.
for side,label in [(-1,'L'),(1,'R')]:
    for idx,y in enumerate([-1.8,2.3,6.4]):
        box('Room_Wall_Panel_'+label+str(idx),(side*2.786,y,1.62),(.022,3.55,2.26),1)
        x=side*2.770
        v=[(x,y-1.73,.51),(x,y-.88,.51),(x,y+1.73,2.20),(x,y+1.73,2.69)]
        f=(0,1,2,3) if side<0 else (3,2,1,0)
        mesh('Room_Red_Diagonal_'+label+str(idx),v,[f],[2])
    for idx,y in enumerate([-3.75,.25,4.35,8.80]):
        box('Room_Column_'+label+str(idx),(side*2.65,y,1.65),(.30,.32,3.3),3,decor,.025)
    box('Room_Upper_Red_Band_'+label,(side*2.765,2.7,3.05),(.045,13.8,.24),2)

# Ceiling stays in its own collection for convenient inspection; it is part of assembly.
box('Room_Ceiling',(0,2.7,3.37),(5.96,14.16,.14),5,ceiling)
for x in (-1.3,1.3):box('Room_Ceiling_Timber_'+str(x),(x,2.7,3.275),(.22,13.8,.05),7,ceiling)
for y in (-2.4,.8,4.0,7.2):
    ob=box('Room_Ceiling_Diffuser_'+str(y),(0,y,3.285),(.11,1.8,.018),15,ceiling)
    ob.data.materials.clear();ob.data.materials.append(glow)

# Blank screen and a dark pinsetting recess, matching the concept's focal point.
box('Room_Pin_Recess_Back',(0,9.30,.66),(2.28,.12,1.30),12,screen)
for side,label in [(-1,'Left'),(1,'Right')]:
    box('Room_Pin_Portal_'+label,(side*1.23,8.96,.72),(.20,.44,1.44),3,screen,.02)
    box('Room_Screen_Pillar_'+label,(side*1.50,9.02,1.65),(.26,.40,3.3),3,screen,.02)
box('Room_Pin_Portal_Header',(0,8.96,1.25),(2.58,.44,.18),4,screen,.015)
box('Room_Screen_Frame',(0,8.91,2.10),(2.82,.23,1.54),3,screen,.035)
panel=box('Room_Screen_Blank',(0,8.784,2.10),(2.56,.018,1.28),12,screen)
panel.data.materials.clear();panel.data.materials.append(display)
box('Room_Screen_Inner_Trim',(0,8.775,1.415),(2.64,.028,.045),13,screen)

# Two small benches along the outer walls, clear of the main throwing/pickup area.
for side,label in [(-1,'Left'),(1,'Right')]:
    box('Room_Bench_Seat_'+label,(side*2.32,5.70,.46),(.52,1.45,.10),7,decor,.02)
    box('Room_Bench_Back_'+label,(side*2.57,5.70,.66),(.075,1.45,.34),7,decor,.015)
    for y in (5.15,6.25):box('Room_Bench_Leg_'+label+str(y),(side*2.32,y,.21),(.39,.13,.42),3,decor,.012)

# Faceted planters: closed outer pot, inset soil, and solid angular leaves.
random.seed(41)
for idx,(px,py) in enumerate([(-2.30,-3.50),(2.35,-3.50),(-2.30,2.40),(2.30,2.40),(-2.17,8.30),(2.17,8.30)]):
    pot=cone('Room_Pot_%02d'%idx,(px,py,.23),.17,.235,.46,3,plants,6)
    cone('Room_Pot_Rim_%02d'%idx,(px,py,.447),.243,.243,.055,4,plants,6)
    cone('Room_Pot_Soil_%02d'%idx,(px,py,.477),.207,.207,.012,7,plants,6)
    for branch in range(3):
        ang=branch*math.tau/3+idx*.7
        tip=Vector((px+.10*math.cos(ang),py+.10*math.sin(ang),1.0+branch*.15))
        base=Vector((px,py,.48))
        rod('Room_Plant_Stem_%02d_%d'%(idx,branch),base,tip,.014,8,plants)
        for k in range(3):
            t=.38+k*.25;start=base.lerp(tip,t)
            a=ang+(k%2)*2.4
            direction=Vector((math.cos(a)*.28,math.sin(a)*.28,.29+random.random()*.14))
            end=start+direction
            cross=Vector((-math.sin(a),math.cos(a),0))*(.09+random.random()*.045)
            mid=start.lerp(end,.52);ridge=mid+Vector((0,0,.055));under=mid-Vector((0,0,.018))
            verts=[tuple(start),tuple(mid+cross),tuple(end),tuple(mid-cross),tuple(ridge),tuple(under)]
            faces=[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(1,0,5),(2,1,5),(3,2,5),(0,3,5)]
            mesh('Room_Plant_Leaf_%02d_%d_%d'%(idx,branch,k),verts,faces,[9,10,11,9,8,9,8,8],plants)

# Six hanging faceted metal shades; real Blender lights are a separate review layer.
for side,label in [(-1,'Left'),(1,'Right')]:
    for idx,y in enumerate([-1.50,3.0,7.35]):
        x=side*2.05
        cone('Room_Lamp_Ceiling_Rose_'+label+str(idx),(x,y,3.27),.085,.085,.06,3,fixtures)
        rod('Room_Lamp_Cord_'+label+str(idx),(x,y,3.24),(x,y,2.90),.012,3,fixtures)
        cone('Room_Lamp_Shade_'+label+str(idx),(x,y,2.77),.22,.085,.26,3,fixtures)
        diffuser=cone('Room_Lamp_Diffuser_'+label+str(idx),(x,y,2.634),.183,.183,.012,15,fixtures)
        diffuser.data.materials.clear();diffuser.data.materials.append(glow)
        ld=bpy.data.lights.new('Room_Pendant_Light_'+label+str(idx),'AREA');ld.energy=110;ld.color=(1,.77,.51);ld.shape='DISK';ld.size=.35
        lo=bpy.data.objects.new(ld.name,ld);lighting.objects.link(lo);lo.location=(x,y,2.60)

def area(name,loc,target,power,size,colour):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=colour
    ob=bpy.data.objects.new(name,data);lighting.objects.link(ob);ob.location=loc
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
area('Room_Approach_Fill',(0,-2,3.15),(0,-2,0),170,3,(1,.88,.72))
area('Room_Lane_Fill',(0,3.5,3.1),(0,3.5,0),220,3,(1,.87,.70))
area('Room_Pins_Fill',(0,7.7,2.85),(0,7.4,.2),100,1.6,(1,.83,.60))
world=bpy.data.worlds.new('Room_World');world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.16,.24,1);world.node_tree.nodes['Background'].inputs[1].default_value=.2;s.world=world

def camera(name,loc,target,lens=25,ortho=None):
    data=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,data);cameras.objects.link(ob)
    ob.location=loc;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens;data.clip_start=.03;data.clip_end=100
    if ortho:data.type='ORTHO';data.ortho_scale=ortho
    return ob
s.camera=camera('Room_Player_View',(0,-3.65,1.65),(0,5.0,1.28),23)
camera('Room_Pickup_View',(.60,-3.25,1.65),(1.65,-2.05,.55),30)
camera('Room_Overview',(11,-12,14),(0,2.2,0),ortho=18)
for name,loc in [('Player_Start',(0,-2.75,0)),('Ball_Pickup_Stance',(1.15,-2.25,0)),('Throw_Stance',(0,-.65,0))]:
    ob=bpy.data.objects.new(name,None);markers.objects.link(ob);ob.location=loc;ob.empty_display_type='CIRCLE';ob.empty_display_size=.30
    ob['note']='Layout reference only; validate with XR Interaction Simulator during later Unity integration.'
s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True
s.render.resolution_x=1600;s.render.resolution_y=1000;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.film_transparent=False;s.view_settings.view_transform='AgX'
s.render.filepath=str(BASE/'Journey/screenshots/007-room-player-view.png')
for a in bpy.context.screen.areas:
    if a.type=='VIEW_3D':
        a.spaces.active.shading.type='MATERIAL';a.spaces.active.overlay.show_overlays=False;a.spaces.active.region_3d.view_perspective='CAMERA'
bpy.context.view_layer.update()
stats=[]
for c in [shell,ceiling,decor,plants,fixtures,screen,lane_col,pins_col,return_col,balls_col]:
    tris=0
    for ob in c.objects:
        if ob.type=='MESH':ob.data.calc_loop_triangles();tris+=len(ob.data.loop_triangles)
    stats.append({'collection':c.name,'mesh_objects':sum(o.type=='MESH' for o in c.objects),'triangles':tris})
result={'scene':s.name,'collections':stats,'triangles':sum(r['triangles'] for r in stats),
    'interior_dimensions_m':[5.6,13.8,3.3],'lane_head_pin_y_m':7,
    'ball_return_root':[1.9,-1.5,0],'player_start':[0,-2.75,0],
    'pickup_stance':[1.15,-2.25,0],'throw_stance':[0,-.65,0],
    'pins':10,'balls':3,'plants':6,'pendants':6,'unity_import_tested':False,'export_deferred':True}
(OUT/'Room_manifest.json').write_text(json.dumps(result,indent=2))
palette.pack();bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'Blender/BowlingAssets.blend'))
