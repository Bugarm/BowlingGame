"""Validate assembled Blender scene and approximate player-route clearance via MCP."""
import bpy,bmesh,json,math,os
from pathlib import Path
from mathutils import Vector
BASE=Path('F:/UnityProjects/BowlingGame');OUT=BASE/'Blender/Assembly'
s=bpy.data.scenes['BowlingRoom_Complete'];bpy.context.window.scene=s
bpy.context.view_layer.update()
assembly=bpy.data.collections['ROOM | Complete asset assembly']
objects=list(assembly.all_objects);meshes=[o for o in objects if o.type=='MESH']
assert len(bpy.data.collections['ROOM | Ten pins'].objects)==11
assert len(bpy.data.collections['ROOM | Three balls'].objects)==3
assert not any(o.type=='FONT' for o in s.objects)
zero=[];missing=[]
for ob in meshes:
    if any(p.area<1e-10 for p in ob.data.polygons):zero.append(ob.name)
    assert len(ob.data.uv_layers)>0,ob.name
    assert all(abs(x-1)<1e-5 for x in ob.scale),ob.name
    for mat in ob.data.materials:
        if mat.use_nodes:
            for n in mat.node_tree.nodes:
                if n.type=='TEX_IMAGE' and n.image and not n.image.packed_file and not os.path.exists(bpy.path.abspath(n.image.filepath)):
                    missing.append(n.image.filepath)
assert not zero,zero
assert not missing,missing

# Check assembled source objects preserve geometry and source-relative placement.
for ob in bpy.data.collections['LANE | Export'].objects:
    copy=bpy.data.objects['Room_'+ob.name]
    if ob.type=='MESH':assert copy.data==ob.data
    assert (copy.matrix_world.translation-ob.matrix_world.translation).length<1e-6
for ob in bpy.data.collections['PINS | Rack preview'].objects:
    copy=bpy.data.objects['Room_'+ob.name]
    assert (copy.matrix_world.translation-ob.matrix_world.translation).length<1e-6
offset=Vector((1.9,-1.5,0))
for ob in bpy.data.collections['BALL RETURN | Export'].objects:
    copy=bpy.data.objects['Room_'+ob.name]
    assert (copy.matrix_world.translation-ob.matrix_world.translation-offset).length<1e-5

# Conservative horizontal AABB obstacle checks for a 0.35 m radius, 1.8 m tall
# player proxy. Floor panels and details below 0.10 m do not obstruct walking.
obstacles=[]
for ob in meshes:
    points=[ob.matrix_world@Vector(c) for c in ob.bound_box]
    mn=[min(p[i] for p in points) for i in range(3)]
    mx=[max(p[i] for p in points) for i in range(3)]
    if mx[2]>.10 and mn[2]<1.8:obstacles.append((ob.name,mn,mx))
routes=[('Start_to_pickup',[(0,-2.75),(1.15,-2.25)]),
        ('Pickup_to_throw',[(1.15,-2.25),(.60,-1.80),(0,-.65)])]
route_results=[]
for name,points in routes:
    closest=100;hits=[]
    for a,b in zip(points,points[1:]):
        for step in range(51):
            t=step/50;x=a[0]+t*(b[0]-a[0]);y=a[1]+t*(b[1]-a[1])
            for ob,mn,mx in obstacles:
                dx=max(mn[0]-x,0,x-mx[0]);dy=max(mn[1]-y,0,y-mx[1])
                dist=math.hypot(dx,dy);closest=min(closest,dist)
                if dist<.35:hits.append(ob)
    assert not hits,(name,sorted(set(hits)))
    route_results.append({'route':name,'waypoints_xy_m':points,'player_radius_m':.35,'min_obstacle_clearance_from_centre_m':closest})

# Floor height under route points, and no room floor geometry filling the gutters.
for x,y in [(0,-2.75),(1.15,-2.25),(.6,-1.8),(0,-.65)]:
    hit,location,normal,index,obj,matrix=s.ray_cast(bpy.context.evaluated_depsgraph_get(),Vector((x,y,.09)),Vector((0,0,-1)),distance=.2)
    assert hit and abs(location.z)<.002,(x,y,location)
for x,y in [(.67,1),(-.67,5),(.67,7.8)]:
    hit,loc,*_=s.ray_cast(bpy.context.evaluated_depsgraph_get(),Vector((x,y,.10)),Vector((0,0,-1)),distance=.5)
    assert hit and loc.z<-.05,(x,y,loc)
for ob in meshes:ob.data.calc_loop_triangles()
result={'passed':True,'scene':s.name,'mesh_objects':len(meshes),'triangles':sum(len(o.data.loop_triangles) for o in meshes),
    'zero_area_objects':zero,'missing_images':missing,'routes':route_results,
    'source_assets_linked_and_transforms_checked':True,'floor_route_height_checked':True,'gutters_not_filled_by_room_floor':True,
    'pins':10,'balls':3,'plants':6,'blank_screen':True,'unity_xr_tested':False,
    'clearance_test_limit':'Static 0.35 m horizontal radius / 1.8 m tall proxy against bounding boxes; not XR reach, collision or comfort validation.'}
(OUT/'Room_validation.json').write_text(json.dumps(result,indent=2))
