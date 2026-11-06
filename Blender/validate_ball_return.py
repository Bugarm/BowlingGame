"""Run through Blender MCP: source fit checks and exported geometry verification."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
OUT=Path('F:/UnityProjects/BowlingGame/Blender/Exports/BallReturn')
source=bpy.data.collections['BALL RETURN | Export']
points=[o.matrix_world@Vector(c) for o in source.objects if o.type=='MESH' for c in o.bound_box]
bounds=[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]
zero_area=0
solid_errors=[]
decorative={'Return_Wood_Strips','Return_Red_Slash_Left','Return_Red_Slash_Right'}
for ob in source.objects:
    if ob.type!='MESH':continue
    bm=bmesh.new();bm.from_mesh(ob.data)
    zero_area+=sum(f.calc_area()<1e-10 for f in bm.faces)
    if ob.name not in decorative and any(not e.is_manifold for e in bm.edges):solid_errors.append(ob.name)
    bm.free()
assert zero_area==0 and not solid_errors
balls=[bpy.data.objects['Return_Preview_Ball_'+c] for c in ['Red','Blue','Green']]
for ob in balls:
    assert abs(ob.location.z-.1085-.3152)<1e-6
    assert abs(ob.location.x)+.1085 < .1945
for a,b in zip(balls,balls[1:]):assert (a.location-b.location).length>.217
assert balls[0].location.y-.1085 > -1.1525
original=bpy.context.scene
qa=bpy.data.scenes.new('Return_Export_QA');bpy.context.window.scene=qa
try:
    bpy.ops.import_scene.fbx(filepath=str(OUT/'BowlingBallReturn.fbx'))
    meshes=[o for o in qa.objects if o.type=='MESH']
    for ob in meshes:ob.data.calc_loop_triangles()
    tris=sum(len(o.data.loop_triangles) for o in meshes)
    assert len(meshes)==21 and tris==780
    assert all(len(o.data.uv_layers)>0 for o in meshes)
    assert not any('Preview_Ball' in o.name for o in meshes)
    pts=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
    export_bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
    assert all(abs(a-b)<.00001 for row1,row2 in zip(bounds,export_bounds) for a,b in zip(row1,row2))
    result={'passed':True,'meshes':len(meshes),'triangles':tris,'bounds_m':bounds,
        'dimensions_m':[hi-lo for lo,hi in bounds],'zero_area_faces':zero_area,
        'non_manifold_solid_objects':solid_errors,'intentional_open_decorative_meshes':sorted(decorative),
        'three_ball_static_fit':True,'preview_balls_exported':False,'unity_import_tested':False}
finally:
    for ob in list(qa.objects):bpy.data.objects.remove(ob,do_unlink=True)
    bpy.context.window.scene=original;bpy.data.scenes.remove(qa)
(OUT/'FBX_roundtrip_validation.json').write_text(json.dumps(result,indent=2))
report=json.loads((OUT/'Return_validation.json').read_text());report['nominal_size_m']=result['dimensions_m']
(OUT/'Return_validation.json').write_text(json.dumps(report,indent=2))
